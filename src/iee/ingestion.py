"""Descarga y normalización reproducible de las fuentes oficiales del piloto."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import tempfile
import tomllib
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class IngestionError(RuntimeError):
    """Error controlado de descarga, parseo o validación."""


@dataclass(frozen=True)
class DownloadSpec:
    resource_id: str
    indicator_id: str
    source_id: str
    source_status: str
    score_eligible: bool
    adapter: str
    series_code: str
    url: str
    direction: str
    unit: str
    expected_entities: tuple[str, ...]
    expected_latest_year: Mapping[str, int]
    expected_latest_value: Mapping[str, Decimal]
    latest_value_tolerance: Decimal
    minimum_observations_per_entity: int
    denominator_url: str | None = None
    ppp_url: str | None = None
    population_url: str | None = None
    category_column: str | None = None
    expected_categories: tuple[str, ...] = ()
    scale: Decimal = Decimal("1")


@dataclass(frozen=True)
class DownloadManifest:
    version: str
    schema_version: str
    countries: tuple[str, ...]
    catalog_path: Path
    manual_control_ids: tuple[str, ...]
    deferred_ids: tuple[str, ...]
    series: tuple[DownloadSpec, ...]


@dataclass(frozen=True)
class Observation:
    entity: str
    period: int
    indicator_id: str
    value: Decimal
    direction: str
    unit: str
    source_id: str
    series_code: str
    source_status: str
    score_eligible: bool
    observation_status: str
    observation_kind: str
    resource_id: str


@dataclass(frozen=True)
class FetchedPayload:
    requested_url: str
    final_url: str
    content: bytes
    content_type: str = ""
    etag: str = ""
    last_modified: str = ""


@dataclass(frozen=True)
class PipelineResult:
    observation_count: int
    series_count: int
    raw_resource_count: int
    processed_path: Path
    provenance_path: Path
    processed_sha256: str


Fetcher = Callable[..., FetchedPayload]
_RESOURCE_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_ADAPTERS = {
    "world_bank_json",
    "oecd_sdmx_csv",
    "oecd_ratio_csv",
    "oecd_ppp_per_capita",
}
_STATUSES = {"validated", "conditional", "reserve"}
_DIRECTIONS = {"higher", "lower", "input"}
_CSV_ACCEPT = "application/vnd.sdmx.data+csv;version=1.0.0"
_JSON_ACCEPT = "application/json"


def load_download_manifest(path: str | Path) -> DownloadManifest:
    """Carga el manifiesto y lo contrasta con el catálogo metodológico."""

    manifest_path = Path(path)
    try:
        with manifest_path.open("rb") as manifest_file:
            raw = tomllib.load(manifest_file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise IngestionError(f"no se pudo leer el manifiesto {manifest_path}: {error}") from error

    try:
        version = str(raw["version"])
        schema_version = str(raw["schema_version"])
        countries = tuple(str(value) for value in raw["countries"])
        catalog_path = manifest_path.parent / str(raw["catalog"])
        manual_ids = tuple(str(value) for value in raw.get("manual_control_ids", []))
        deferred_ids = tuple(str(value) for value in raw.get("deferred_ids", []))
        raw_series = raw["series"]
    except (KeyError, TypeError) as error:
        raise IngestionError(f"estructura incompleta en {manifest_path}: {error}") from error

    if not countries or len(set(countries)) != len(countries):
        raise IngestionError("countries debe contener códigos únicos")
    if not isinstance(raw_series, list) or not raw_series:
        raise IngestionError("el manifiesto debe incluir al menos una serie automática")

    specs = tuple(_parse_download_spec(item, countries) for item in raw_series)
    resource_ids = [spec.resource_id for spec in specs]
    indicator_ids = [spec.indicator_id for spec in specs]
    if len(resource_ids) != len(set(resource_ids)):
        raise IngestionError("resource_id debe ser único")
    if len(indicator_ids) != len(set(indicator_ids)):
        raise IngestionError("cada indicador solo puede tener una adquisición automática")

    acquisition_ids = set(indicator_ids)
    manual_set = set(manual_ids)
    deferred_set = set(deferred_ids)
    if acquisition_ids & manual_set or acquisition_ids & deferred_set or manual_set & deferred_set:
        raise IngestionError("las rutas automática, manual y diferida deben ser disjuntas")

    manifest = DownloadManifest(
        version=version,
        schema_version=schema_version,
        countries=countries,
        catalog_path=catalog_path,
        manual_control_ids=manual_ids,
        deferred_ids=deferred_ids,
        series=specs,
    )
    _validate_against_catalog(manifest)
    return manifest


def _parse_download_spec(raw: Mapping[str, Any], countries: tuple[str, ...]) -> DownloadSpec:
    try:
        adapter = str(raw["adapter"])
        expected_entities = tuple(str(value) for value in raw["expected_entities"])
        latest_year = {
            str(entity): int(year) for entity, year in raw["expected_latest_year"].items()
        }
        latest_value = {
            str(entity): _parse_decimal(value, f"latest value {entity}")
            for entity, value in raw["expected_latest_value"].items()
        }
        spec = DownloadSpec(
            resource_id=str(raw["resource_id"]),
            indicator_id=str(raw["indicator_id"]),
            source_id=str(raw["source_id"]),
            source_status=str(raw["source_status"]),
            score_eligible=raw["score_eligible"],
            adapter=adapter,
            series_code=str(raw["series_code"]),
            url=str(raw["url"]),
            direction=str(raw["direction"]),
            unit=str(raw["unit"]),
            expected_entities=expected_entities,
            expected_latest_year=latest_year,
            expected_latest_value=latest_value,
            latest_value_tolerance=_parse_decimal(
                raw["latest_value_tolerance"], "latest_value_tolerance"
            ),
            minimum_observations_per_entity=int(raw["minimum_observations_per_entity"]),
            denominator_url=_optional_text(raw, "denominator_url"),
            ppp_url=_optional_text(raw, "ppp_url"),
            population_url=_optional_text(raw, "population_url"),
            category_column=_optional_text(raw, "category_column"),
            expected_categories=tuple(str(value) for value in raw.get("expected_categories", [])),
            scale=_parse_decimal(raw.get("scale", 1), "scale"),
        )
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise IngestionError(f"serie de descarga incompleta: {error}") from error

    if not _RESOURCE_ID.fullmatch(spec.resource_id):
        raise IngestionError(f"resource_id inválido: {spec.resource_id}")
    if adapter not in _ADAPTERS:
        raise IngestionError(f"adaptador no permitido para {spec.indicator_id}: {adapter}")
    if spec.source_status not in _STATUSES:
        raise IngestionError(f"estado no permitido para {spec.indicator_id}")
    if not isinstance(spec.score_eligible, bool):
        raise IngestionError(f"score_eligible debe ser booleano para {spec.indicator_id}")
    if spec.score_eligible and spec.source_status != "validated":
        raise IngestionError(f"solo una fuente validada puede puntuar: {spec.indicator_id}")
    if spec.direction not in _DIRECTIONS:
        raise IngestionError(f"dirección no permitida para {spec.indicator_id}")
    if spec.direction == "input" and spec.score_eligible:
        raise IngestionError(f"un insumo no puede puntuarse directamente: {spec.indicator_id}")
    if set(expected_entities) != set(countries):
        raise IngestionError(f"{spec.indicator_id} debe exigir exactamente {countries}")
    if set(latest_year) != set(expected_entities):
        raise IngestionError(f"faltan años esperados por país en {spec.indicator_id}")
    if set(latest_value) != set(expected_entities):
        raise IngestionError(f"faltan valores esperados por país en {spec.indicator_id}")
    if spec.latest_value_tolerance < 0:
        raise IngestionError(f"tolerancia negativa en {spec.indicator_id}")
    if spec.minimum_observations_per_entity < 1:
        raise IngestionError(f"mínimo de observaciones inválido en {spec.indicator_id}")
    _validate_https(spec.url, spec.indicator_id)

    if adapter == "oecd_ratio_csv":
        if not spec.denominator_url or not spec.category_column or not spec.expected_categories:
            raise IngestionError(f"faltan parámetros de razón en {spec.indicator_id}")
        _validate_https(spec.denominator_url, spec.indicator_id)
    if adapter == "oecd_ppp_per_capita":
        if not spec.ppp_url or not spec.population_url:
            raise IngestionError(f"faltan dependencias PPA/población en {spec.indicator_id}")
        _validate_https(spec.ppp_url, spec.indicator_id)
        _validate_https(spec.population_url, spec.indicator_id)
    return spec


def _optional_text(raw: Mapping[str, Any], key: str) -> str | None:
    value = raw.get(key)
    return None if value is None else str(value)


def _validate_https(url: str, indicator_id: str) -> None:
    if not url.startswith("https://"):
        raise IngestionError(f"URL no segura en {indicator_id}: {url}")


def _validate_against_catalog(manifest: DownloadManifest) -> None:
    try:
        with manifest.catalog_path.open("rb") as catalog_file:
            catalog = tomllib.load(catalog_file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise IngestionError(
            f"no se pudo leer el catálogo {manifest.catalog_path}: {error}"
        ) from error

    catalog_entries = {entry["indicator_id"]: entry for entry in catalog.get("series", [])}
    acquisition_ids = {spec.indicator_id for spec in manifest.series}
    covered_ids = acquisition_ids | set(manifest.manual_control_ids) | set(manifest.deferred_ids)
    if covered_ids != set(catalog_entries):
        missing = sorted(set(catalog_entries) - covered_ids)
        unexpected = sorted(covered_ids - set(catalog_entries))
        raise IngestionError(
            f"el manifiesto no cubre el catálogo; faltan={missing}, inesperados={unexpected}"
        )

    for spec in manifest.series:
        catalog_entry = catalog_entries[spec.indicator_id]
        comparisons = {
            "source_id": spec.source_id,
            "status": spec.source_status,
            "unit": spec.unit,
        }
        for field, actual in comparisons.items():
            expected = catalog_entry[field]
            if actual != expected:
                raise IngestionError(
                    f"{spec.indicator_id}: {field} difiere del catálogo "
                    f"({actual!r} != {expected!r})"
                )
        try:
            expected_catalog_values = {
                "COL": _parse_decimal(
                    catalog_entry["latest_col_value"], "latest_col_value"
                ),
                "USA": _parse_decimal(
                    catalog_entry["latest_usa_value"], "latest_usa_value"
                ),
            }
        except KeyError as error:
            raise IngestionError(
                f"{spec.indicator_id}: falta un valor de control en el catálogo"
            ) from error
        if dict(spec.expected_latest_value) != expected_catalog_values:
            raise IngestionError(
                f"{spec.indicator_id}: los valores de control difieren del catálogo"
            )


def download_url(
    url: str,
    *,
    accept: str,
    timeout: float = 30.0,
    max_bytes: int = 100_000_000,
    opener: Callable[..., Any] = urlopen,
) -> FetchedPayload:
    """Descarga una URL con límite de tamaño y metadatos de procedencia."""

    request = Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": "iee/0.1 (+https://github.com/rickHard29/indice-eficiencia-del-estado)",
        },
    )
    try:
        with opener(request, timeout=timeout) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > max_bytes:
                raise IngestionError(f"respuesta demasiado grande para {url}")
            content = response.read(max_bytes + 1)
            if len(content) > max_bytes:
                raise IngestionError(f"respuesta demasiado grande para {url}")
            final_url = response.geturl() if hasattr(response, "geturl") else url
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip()
            etag = response.headers.get("ETag", "")
            last_modified = response.headers.get("Last-Modified", "")
    except HTTPError as error:
        raise IngestionError(f"HTTP {error.code} al descargar {url}") from error
    except (URLError, TimeoutError, OSError) as error:
        raise IngestionError(f"falló la descarga de {url}: {error}") from error
    except ValueError as error:
        raise IngestionError(f"cabecera HTTP inválida al descargar {url}: {error}") from error

    if not content:
        raise IngestionError(f"respuesta vacía para {url}")
    return FetchedPayload(
        requested_url=url,
        final_url=final_url,
        content=bytes(content),
        content_type=content_type,
        etag=etag,
        last_modified=last_modified,
    )


def sha256_hex(payload: bytes) -> str:
    """Calcula SHA-256 sobre los bytes originales, sin normalizarlos."""

    return hashlib.sha256(payload).hexdigest()


def parse_world_bank_json(payload: bytes, spec: DownloadSpec) -> list[Observation]:
    """Convierte la envoltura JSON de World Bank API en observaciones IEE."""

    records = _world_bank_value_map(payload, spec.expected_entities)
    observations = [
        _make_observation(
            spec,
            entity=entity,
            period=period,
            value=value,
            status=status,
            kind="reported",
        )
        for (entity, period), (value, status) in records.items()
    ]
    return validate_observations(observations, spec)


def parse_oecd_sdmx_csv(payload: bytes, spec: DownloadSpec) -> list[Observation]:
    """Convierte una respuesta SDMX-CSV directa en observaciones IEE."""

    rows = _read_oecd_rows(payload, spec.expected_entities)
    observations = [
        _make_observation(
            spec,
            entity=row["REF_AREA"],
            period=_parse_year(row["TIME_PERIOD"]),
            value=_scaled_oecd_value(row),
            status=_quality_status([row.get("OBS_STATUS", "")]),
            kind="reported",
        )
        for row in rows
    ]
    return validate_observations(observations, spec)


def parse_oecd_ratio_csv(
    numerator_payload: bytes,
    denominator_payload: bytes,
    spec: DownloadSpec,
) -> list[Observation]:
    """Calcula una razón OECD exigiendo todos los componentes por país-año."""

    if not spec.category_column or not spec.expected_categories:
        raise IngestionError(f"configuración de razón incompleta para {spec.indicator_id}")
    numerator_rows = _read_oecd_rows(
        numerator_payload,
        spec.expected_entities,
        additional_columns=(spec.category_column,),
    )
    denominator_rows = _read_oecd_rows(denominator_payload, spec.expected_entities)

    grouped: dict[tuple[str, int], dict[str, Mapping[str, str]]] = defaultdict(dict)
    for row in numerator_rows:
        key = (row["REF_AREA"], _parse_year(row["TIME_PERIOD"]))
        category = row[spec.category_column]
        if category not in spec.expected_categories:
            raise IngestionError(f"categoría inesperada {category} en {spec.indicator_id}")
        if category in grouped[key]:
            raise IngestionError(f"componente duplicado {category} para {key}")
        grouped[key][category] = row

    denominators = _unique_oecd_rows(denominator_rows)
    if set(grouped) != set(denominators):
        raise IngestionError(f"numerador y denominador no coinciden en {spec.indicator_id}")

    observations: list[Observation] = []
    for key, components in grouped.items():
        if set(components) != set(spec.expected_categories):
            missing = sorted(set(spec.expected_categories) - set(components))
            raise IngestionError(f"faltan componentes {missing} para {key}")
        denominator_row = denominators[key]
        _validate_same_currency([*components.values(), denominator_row], key)
        numerator = sum((_scaled_oecd_value(row) for row in components.values()), Decimal())
        denominator = _scaled_oecd_value(denominator_row)
        if denominator == 0:
            raise IngestionError(f"denominador cero para {key}")
        statuses = [row.get("OBS_STATUS", "") for row in components.values()]
        statuses.append(denominator_row.get("OBS_STATUS", ""))
        observations.append(
            _make_observation(
                spec,
                entity=key[0],
                period=key[1],
                value=numerator / denominator * spec.scale,
                status=_quality_status(statuses),
                kind="derived",
            )
        )
    return validate_observations(observations, spec)


def parse_oecd_ppp_per_capita(
    expenditure_payload: bytes,
    ppp_payload: bytes,
    population_payload: bytes,
    spec: DownloadSpec,
) -> list[Observation]:
    """Deriva gasto COFOG por habitante en PPA sin mezclar país-año."""

    expenditure_rows = _unique_oecd_rows(
        _read_oecd_rows(expenditure_payload, spec.expected_entities)
    )
    ppp = _world_bank_value_map(ppp_payload, spec.expected_entities)
    population = _world_bank_value_map(population_payload, spec.expected_entities)
    common_keys = set(expenditure_rows) & set(ppp) & set(population)
    if common_keys != set(expenditure_rows):
        missing = sorted(set(expenditure_rows) - common_keys)
        raise IngestionError(f"faltan PPA o población para {missing}")

    observations: list[Observation] = []
    for key, row in expenditure_rows.items():
        ppp_value, ppp_status = ppp[key]
        population_value, population_status = population[key]
        if ppp_value <= 0 or population_value <= 0:
            raise IngestionError(f"PPA o población no positiva para {key}")
        value = _scaled_oecd_value(row) / ppp_value / population_value
        observations.append(
            _make_observation(
                spec,
                entity=key[0],
                period=key[1],
                value=value,
                status=_quality_status(
                    [row.get("OBS_STATUS", ""), ppp_status, population_status]
                ),
                kind="derived",
            )
        )
    return validate_observations(observations, spec)


def _world_bank_value_map(
    payload: bytes,
    expected_entities: Sequence[str],
) -> dict[tuple[str, int], tuple[Decimal, str]]:
    try:
        document = json.loads(payload.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise IngestionError(f"JSON World Bank inválido: {error}") from error
    if not isinstance(document, list) or len(document) != 2:
        raise IngestionError("envoltura World Bank inválida")
    metadata, raw_records = document
    if not isinstance(metadata, dict) or not isinstance(raw_records, list):
        raise IngestionError("metadatos o registros World Bank inválidos")
    try:
        if int(metadata.get("page", 1)) < int(metadata.get("pages", 1)):
            raise IngestionError("la respuesta World Bank está paginada e incompleta")
    except (TypeError, ValueError) as error:
        raise IngestionError("paginación World Bank inválida") from error

    allowed = set(expected_entities)
    result: dict[tuple[str, int], tuple[Decimal, str]] = {}
    for raw_record in raw_records:
        if not isinstance(raw_record, dict):
            raise IngestionError("registro World Bank inválido")
        entity = str(raw_record.get("countryiso3code", ""))
        if entity not in allowed:
            raise IngestionError(f"país inesperado en World Bank: {entity}")
        raw_value = raw_record.get("value")
        if raw_value is None:
            continue
        period = _parse_year(raw_record.get("date"))
        key = (entity, period)
        if key in result:
            raise IngestionError(f"observación World Bank duplicada: {key}")
        result[key] = (
            _parse_decimal(raw_value, f"World Bank {key}"),
            _quality_status([str(raw_record.get("obs_status", ""))]),
        )
    if not result:
        raise IngestionError("World Bank no devolvió valores observados")
    return result


def _read_oecd_rows(
    payload: bytes,
    expected_entities: Sequence[str],
    *,
    additional_columns: Sequence[str] = (),
) -> list[dict[str, str]]:
    if payload.lstrip().startswith((b"<?xml", b"<message:")):
        raise IngestionError("OECD devolvió XML; la consulta debe solicitar format=csvfile")
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise IngestionError(f"SDMX-CSV no está en UTF-8: {error}") from error
    reader = csv.DictReader(io.StringIO(text))
    required = {"REF_AREA", "TIME_PERIOD", "OBS_VALUE", *additional_columns}
    if not reader.fieldnames or not required <= set(reader.fieldnames):
        missing = sorted(required - set(reader.fieldnames or []))
        raise IngestionError(f"faltan columnas SDMX-CSV: {missing}")

    allowed = set(expected_entities)
    rows: list[dict[str, str]] = []
    for row in reader:
        entity = row.get("REF_AREA", "")
        if entity not in allowed:
            raise IngestionError(f"país inesperado en OECD: {entity}")
        _parse_year(row.get("TIME_PERIOD"))
        _parse_decimal(row.get("OBS_VALUE"), f"OECD {entity}")
        rows.append(row)
    if not rows:
        raise IngestionError("OECD no devolvió observaciones")
    return rows


def _unique_oecd_rows(
    rows: Iterable[Mapping[str, str]],
) -> dict[tuple[str, int], Mapping[str, str]]:
    result: dict[tuple[str, int], Mapping[str, str]] = {}
    for row in rows:
        key = (row["REF_AREA"], _parse_year(row["TIME_PERIOD"]))
        if key in result:
            raise IngestionError(f"observación OECD duplicada: {key}")
        result[key] = row
    return result


def _validate_same_currency(rows: Sequence[Mapping[str, str]], key: tuple[str, int]) -> None:
    currencies = {row.get("CURRENCY", "") for row in rows if row.get("CURRENCY", "")}
    if len(currencies) > 1:
        raise IngestionError(f"monedas incompatibles para {key}: {sorted(currencies)}")


def _scaled_oecd_value(row: Mapping[str, str]) -> Decimal:
    value = _parse_decimal(row.get("OBS_VALUE"), "OBS_VALUE")
    raw_multiplier = row.get("UNIT_MULT", "")
    try:
        multiplier = 0 if raw_multiplier in (None, "") else int(raw_multiplier)
    except ValueError as error:
        raise IngestionError(f"UNIT_MULT inválido: {raw_multiplier}") from error
    return value * (Decimal(10) ** multiplier)


def _parse_decimal(value: Any, context: str) -> Decimal:
    if isinstance(value, bool) or value in (None, ""):
        raise IngestionError(f"valor numérico ausente o inválido en {context}")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise IngestionError(f"valor no numérico en {context}: {value!r}") from error
    if not number.is_finite():
        raise IngestionError(f"valor no finito en {context}: {value!r}")
    return number


def _parse_year(value: Any) -> int:
    text = str(value)
    if not re.fullmatch(r"\d{4}", text):
        raise IngestionError(f"año inválido: {value!r}")
    return int(text)


def _quality_status(statuses: Iterable[str]) -> str:
    normalized = {status.strip() for status in statuses if status and status.strip()}
    if "P" in normalized or "provisional" in normalized:
        return "provisional"
    meaningful = sorted(normalized - {"A", "observed"})
    return "observed" if not meaningful else "source:" + "+".join(meaningful)


def _make_observation(
    spec: DownloadSpec,
    *,
    entity: str,
    period: int,
    value: Decimal,
    status: str,
    kind: str,
) -> Observation:
    return Observation(
        entity=entity,
        period=period,
        indicator_id=spec.indicator_id,
        value=value,
        direction=spec.direction,
        unit=spec.unit,
        source_id=spec.source_id,
        series_code=spec.series_code,
        source_status=spec.source_status,
        score_eligible=spec.score_eligible,
        observation_status=status,
        observation_kind=kind,
        resource_id=spec.resource_id,
    )


def validate_observations(
    observations: Sequence[Observation],
    spec: DownloadSpec,
) -> list[Observation]:
    """Valida cobertura sin exigir un panel balanceado ni el mismo último año."""

    if not observations:
        raise IngestionError(f"{spec.indicator_id} no tiene observaciones")
    keys: set[tuple[str, int]] = set()
    counts: Counter[str] = Counter()
    latest: dict[str, int] = {}
    by_key: dict[tuple[str, int], Observation] = {}
    allowed = set(spec.expected_entities)
    for observation in observations:
        if observation.entity not in allowed:
            raise IngestionError(f"entidad inesperada en {spec.indicator_id}")
        key = (observation.entity, observation.period)
        if key in keys:
            raise IngestionError(f"clave duplicada en {spec.indicator_id}: {key}")
        keys.add(key)
        by_key[key] = observation
        counts[observation.entity] += 1
        latest[observation.entity] = max(latest.get(observation.entity, 0), observation.period)
        if not observation.value.is_finite():
            raise IngestionError(f"valor no finito en {spec.indicator_id}: {key}")

    for entity in spec.expected_entities:
        if counts[entity] < spec.minimum_observations_per_entity:
            raise IngestionError(
                f"cobertura insuficiente en {spec.indicator_id}/{entity}: {counts[entity]}"
            )
        expected_latest = spec.expected_latest_year[entity]
        if latest.get(entity) != expected_latest:
            raise IngestionError(
                f"último año inesperado en {spec.indicator_id}/{entity}: "
                f"{latest.get(entity)} != {expected_latest}"
            )
        latest_observation = by_key[(entity, expected_latest)]
        expected_value = spec.expected_latest_value[entity]
        difference = abs(latest_observation.value - expected_value)
        if difference > spec.latest_value_tolerance:
            raise IngestionError(
                f"último valor revisado en {spec.indicator_id}/{entity}: "
                f"{latest_observation.value} != {expected_value} "
                f"(tolerancia {spec.latest_value_tolerance})"
            )
    return sorted(observations, key=lambda row: (row.entity, row.period, row.indicator_id))


def run_pipeline(
    manifest_path: str | Path,
    *,
    raw_dir: str | Path,
    processed_path: str | Path,
    provenance_path: str | Path,
    timeout: float = 30.0,
    max_bytes: int = 100_000_000,
    fetcher: Fetcher = download_url,
    retrieved_at: str | None = None,
) -> PipelineResult:
    """Descarga todas las fuentes, valida y publica salidas solo si todo es coherente."""

    manifest_file = Path(manifest_path)
    manifest = load_download_manifest(manifest_file)
    observations: list[Observation] = []
    payloads: list[tuple[str, str, FetchedPayload]] = []
    series_summaries: list[dict[str, Any]] = []

    for spec in manifest.series:
        series_observations, series_payloads = _acquire_series(
            spec,
            timeout=timeout,
            max_bytes=max_bytes,
            fetcher=fetcher,
        )
        observations.extend(series_observations)
        payloads.extend(series_payloads)
        latest_rows = {
            entity: max(
                (row for row in series_observations if row.entity == entity),
                key=lambda row: row.period,
            )
            for entity in spec.expected_entities
        }
        series_summaries.append(
            {
                "indicator_id": spec.indicator_id,
                "resource_id": spec.resource_id,
                "records": len(series_observations),
                "latest_year": {
                    entity: row.period for entity, row in latest_rows.items()
                },
                "latest_value": {
                    entity: _decimal_text(row.value) for entity, row in latest_rows.items()
                },
                "score_eligible": spec.score_eligible,
                "source_status": spec.source_status,
            }
        )

    observations = _validate_dataset(observations)
    processed_bytes = observations_to_csv(observations)
    processed_hash = sha256_hex(processed_bytes)

    raw_root = Path(raw_dir)
    raw_entries: list[dict[str, Any]] = []
    raw_writes: dict[Path, bytes] = {}
    for resource_id, role, fetched in payloads:
        digest = sha256_hex(fetched.content)
        extension = "json" if "json" in fetched.content_type else "csv"
        raw_path = raw_root / f"{digest}.{extension}"
        raw_writes[raw_path] = fetched.content
        raw_entries.append(
            {
                "resource_id": resource_id,
                "role": role,
                "requested_url": fetched.requested_url,
                "final_url": fetched.final_url,
                "content_type": fetched.content_type,
                "bytes": len(fetched.content),
                "sha256": digest,
                "raw_path": raw_path.as_posix(),
                "etag": fetched.etag,
                "last_modified": fetched.last_modified,
            }
        )

    timestamp = retrieved_at or datetime.now(UTC).replace(microsecond=0).isoformat()
    manifest_bytes = manifest_file.read_bytes()
    catalog_bytes = manifest.catalog_path.read_bytes()
    provenance = {
        "schema_version": manifest.schema_version,
        "manifest_version": manifest.version,
        "retrieved_at": timestamp,
        "manifest": {
            "path": manifest_file.as_posix(),
            "sha256": sha256_hex(manifest_bytes),
        },
        "catalog": {
            "path": manifest.catalog_path.as_posix(),
            "sha256": sha256_hex(catalog_bytes),
        },
        "countries": list(manifest.countries),
        "resources": raw_entries,
        "series": series_summaries,
        "manual_control_ids": list(manifest.manual_control_ids),
        "deferred_ids": list(manifest.deferred_ids),
        "processed": {
            "path": Path(processed_path).as_posix(),
            "records": len(observations),
            "sha256": processed_hash,
        },
    }
    provenance_bytes = (
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    for path, content in raw_writes.items():
        _atomic_write_bytes(path, content)
    _atomic_write_bytes(Path(processed_path), processed_bytes)
    _atomic_write_bytes(Path(provenance_path), provenance_bytes)

    return PipelineResult(
        observation_count=len(observations),
        series_count=len(manifest.series),
        raw_resource_count=len(raw_entries),
        processed_path=Path(processed_path),
        provenance_path=Path(provenance_path),
        processed_sha256=processed_hash,
    )


def _acquire_series(
    spec: DownloadSpec,
    *,
    timeout: float,
    max_bytes: int,
    fetcher: Fetcher,
) -> tuple[list[Observation], list[tuple[str, str, FetchedPayload]]]:
    primary_accept = _JSON_ACCEPT if spec.adapter == "world_bank_json" else _CSV_ACCEPT
    primary = fetcher(spec.url, accept=primary_accept, timeout=timeout, max_bytes=max_bytes)
    _validate_content_type(primary, "json" if spec.adapter == "world_bank_json" else "csv")
    payloads = [(spec.resource_id, "primary", primary)]

    if spec.adapter == "world_bank_json":
        return parse_world_bank_json(primary.content, spec), payloads
    if spec.adapter == "oecd_sdmx_csv":
        return parse_oecd_sdmx_csv(primary.content, spec), payloads
    if spec.adapter == "oecd_ratio_csv":
        assert spec.denominator_url is not None
        denominator = fetcher(
            spec.denominator_url,
            accept=_CSV_ACCEPT,
            timeout=timeout,
            max_bytes=max_bytes,
        )
        _validate_content_type(denominator, "csv")
        payloads.append((spec.resource_id, "denominator", denominator))
        return parse_oecd_ratio_csv(primary.content, denominator.content, spec), payloads
    if spec.adapter == "oecd_ppp_per_capita":
        assert spec.ppp_url is not None and spec.population_url is not None
        ppp = fetcher(spec.ppp_url, accept=_JSON_ACCEPT, timeout=timeout, max_bytes=max_bytes)
        population = fetcher(
            spec.population_url,
            accept=_JSON_ACCEPT,
            timeout=timeout,
            max_bytes=max_bytes,
        )
        _validate_content_type(ppp, "json")
        _validate_content_type(population, "json")
        payloads.extend(
            [
                (spec.resource_id, "ppp", ppp),
                (spec.resource_id, "population", population),
            ]
        )
        return (
            parse_oecd_ppp_per_capita(
                primary.content,
                ppp.content,
                population.content,
                spec,
            ),
            payloads,
        )
    raise IngestionError(f"adaptador no implementado: {spec.adapter}")


def _validate_content_type(payload: FetchedPayload, expected: str) -> None:
    content_type = payload.content_type.lower()
    if expected == "json":
        valid = "json" in content_type or payload.content.lstrip().startswith((b"[", b"{"))
    else:
        valid = "csv" in content_type and not payload.content.lstrip().startswith(b"<")
    if not valid:
        raise IngestionError(
            f"tipo de contenido inesperado para {payload.requested_url}: "
            f"{payload.content_type or 'desconocido'}"
        )


def _validate_dataset(observations: Sequence[Observation]) -> list[Observation]:
    keys: set[tuple[str, int, str]] = set()
    for row in observations:
        key = (row.entity, row.period, row.indicator_id)
        if key in keys:
            raise IngestionError(f"clave duplicada en el dataset: {key}")
        keys.add(key)
    return sorted(observations, key=lambda row: (row.entity, row.period, row.indicator_id))


def observations_to_csv(observations: Sequence[Observation]) -> bytes:
    """Serializa observaciones con orden y representación decimal estables."""

    output = io.StringIO(newline="")
    fieldnames = [
        "entity",
        "period",
        "indicator_id",
        "value",
        "direction",
        "unit",
        "source_id",
        "series_code",
        "source_status",
        "score_eligible",
        "observation_status",
        "observation_kind",
        "resource_id",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in sorted(observations, key=lambda item: (item.entity, item.period, item.indicator_id)):
        writer.writerow(
            {
                "entity": row.entity,
                "period": row.period,
                "indicator_id": row.indicator_id,
                "value": _decimal_text(row.value),
                "direction": row.direction,
                "unit": row.unit,
                "source_id": row.source_id,
                "series_code": row.series_code,
                "source_status": row.source_status,
                "score_eligible": str(row.score_eligible).lower(),
                "observation_status": row.observation_status,
                "observation_kind": row.observation_kind,
                "resource_id": row.resource_id,
            }
        )
    return output.getvalue().encode("utf-8")


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
    except OSError as error:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()
        raise IngestionError(f"no se pudo escribir {path}: {error}") from error
