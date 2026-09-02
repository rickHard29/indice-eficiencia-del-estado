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
import zipfile
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree


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
    comparison_url: str | None = None
    category_column: str | None = None
    expected_categories: tuple[str, ...] = ()
    scale: Decimal = Decimal("1")
    level_url: str | None = None
    dimension_filters: Mapping[str, str] | None = None
    reference_year: int | None = None
    worksheet: str | None = None
    entity_column: str | None = None
    value_column: str | None = None
    entity_aliases: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class UniverseMask:
    indicator_id: str
    included_countries: tuple[str, ...]
    excluded_countries: tuple[str, ...]


@dataclass(frozen=True)
class CountryUniverse:
    path: Path
    sha256: str
    version: str
    snapshot_date: str
    frame: str
    official_source: str
    countries: tuple[str, ...]
    membership_count: int
    estimation_sample: str
    frontier_min_countries: int
    require_complete_indicator_window: bool
    allow_imputation_for_eligibility: bool
    retain_flagged_observations: bool
    input_masks: tuple[UniverseMask, ...]


@dataclass(frozen=True)
class ManualControlValue:
    entity: str
    period: int
    value: Decimal
    observation_status: str


@dataclass(frozen=True)
class ManualControlSpec:
    resource_id: str
    indicator_id: str
    source_id: str
    source_status: str
    score_eligible: bool
    series_code: str
    source_url: str
    release: str
    locator: str
    direction: str
    unit: str
    observations: tuple[ManualControlValue, ...]


@dataclass(frozen=True)
class DownloadManifest:
    version: str
    schema_version: str
    countries: tuple[str, ...]
    catalog_path: Path
    manifest_sha256: str
    catalog_sha256: str
    manual_controls_path: Path | None
    manual_controls_version: str | None
    manual_controls_validation_date: str | None
    manual_controls_sha256: str | None
    manual_controls: tuple[ManualControlSpec, ...]
    deferred_ids: tuple[str, ...]
    series: tuple[DownloadSpec, ...]
    country_universe: CountryUniverse | None

    @property
    def manual_control_ids(self) -> tuple[str, ...]:
        return tuple(spec.indicator_id for spec in self.manual_controls)


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
    "world_bank_absolute_gap",
    "world_bank_percent_times_level",
    "oecd_sdmx_csv",
    "oecd_percent_times_level",
    "oecd_ratio_csv",
    "oecd_ratio_times_level",
    "oecd_ppp_per_capita",
    "oecd_regional_weighted_interdecile_gap",
    "oecd_pisa_xlsx",
}
_STATUSES = {"validated", "conditional", "reserve"}
_DIRECTIONS = {"higher", "lower", "input"}
_MANUAL_OBSERVATION_STATUSES = {"observed", "source:sampling_caution"}
_CSV_ACCEPT = "application/vnd.sdmx.data+csv;version=1.0.0"
_JSON_ACCEPT = "application/json"


def load_download_manifest(path: str | Path) -> DownloadManifest:
    """Carga el manifiesto y lo contrasta con el catálogo metodológico."""

    manifest_path = Path(path)
    try:
        manifest_bytes = manifest_path.read_bytes()
        raw = tomllib.load(io.BytesIO(manifest_bytes))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise IngestionError(f"no se pudo leer el manifiesto {manifest_path}: {error}") from error

    try:
        version = str(raw["version"])
        schema_version = str(raw["schema_version"])
        countries = tuple(str(value) for value in raw["countries"])
        catalog_path = manifest_path.parent / str(raw["catalog"])
        universe_filename = raw.get("country_universe")
        universe_path = (
            manifest_path.parent / str(universe_filename)
            if universe_filename is not None
            else None
        )
        manual_filename = raw.get("manual_controls")
        manual_path = (
            manifest_path.parent / str(manual_filename)
            if manual_filename is not None
            else None
        )
        deferred_ids = tuple(str(value) for value in raw.get("deferred_ids", []))
        raw_series = raw["series"]
    except (KeyError, TypeError) as error:
        raise IngestionError(f"estructura incompleta en {manifest_path}: {error}") from error

    if not countries or len(set(countries)) != len(countries):
        raise IngestionError("countries debe contener códigos únicos")
    if not isinstance(raw_series, list):
        raise IngestionError("series debe ser una lista")

    entity_aliases = {
        str(label): str(entity) for label, entity in raw.get("entity_aliases", {}).items()
    }
    if any(not label or entity not in countries for label, entity in entity_aliases.items()):
        raise IngestionError("entity_aliases contiene una etiqueta o país inválido")

    specs = tuple(
        _parse_download_spec(item, countries, entity_aliases=entity_aliases)
        for item in raw_series
    )
    country_universe = _load_country_universe(universe_path, version, countries, specs)
    try:
        catalog_bytes = catalog_path.read_bytes()
    except OSError as error:
        raise IngestionError(f"no se pudo leer el catálogo {catalog_path}: {error}") from error
    (
        manual_version,
        manual_validation_date,
        manual_sha256,
        manual_specs,
    ) = _load_manual_controls(manual_path, countries)
    if not specs and not manual_specs:
        raise IngestionError(
            "el manifiesto debe incluir al menos una serie automática o un control manual"
        )
    resource_ids = [spec.resource_id for spec in (*specs, *manual_specs)]
    indicator_ids = [spec.indicator_id for spec in specs]
    manual_ids = [spec.indicator_id for spec in manual_specs]
    if len(resource_ids) != len(set(resource_ids)):
        raise IngestionError("resource_id debe ser único")
    if len(indicator_ids) != len(set(indicator_ids)):
        raise IngestionError("cada indicador solo puede tener una adquisición automática")
    if len(manual_ids) != len(set(manual_ids)):
        raise IngestionError("cada control manual debe tener un indicador único")

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
        manifest_sha256=sha256_hex(manifest_bytes),
        catalog_sha256=sha256_hex(catalog_bytes),
        manual_controls_path=manual_path,
        manual_controls_version=manual_version,
        manual_controls_validation_date=manual_validation_date,
        manual_controls_sha256=manual_sha256,
        manual_controls=manual_specs,
        deferred_ids=deferred_ids,
        series=specs,
        country_universe=country_universe,
    )
    _validate_against_catalog(manifest, catalog_bytes)
    return manifest


def _load_country_universe(
    path: Path | None,
    manifest_version: str,
    manifest_countries: tuple[str, ...],
    specs: tuple[DownloadSpec, ...],
) -> CountryUniverse | None:
    if path is None:
        return None
    try:
        universe_bytes = path.read_bytes()
        raw = tomllib.load(io.BytesIO(universe_bytes))
        version = str(raw["version"])
        snapshot_date = str(raw["snapshot_date"])
        frame = str(raw["frame"])
        official_source = str(raw["official_source"])
        countries = tuple(str(value) for value in raw["countries"])
        membership_count = int(raw["membership_count"])
        estimation_sample = str(raw["estimation_sample"])
        frontier_min_countries = int(raw["frontier_min_countries"])
        require_complete = raw["require_complete_indicator_window"]
        allow_imputation = raw["allow_imputation_for_eligibility"]
        retain_flagged = raw["retain_flagged_observations"]
        raw_masks = raw["input_masks"]
    except (OSError, KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as error:
        raise IngestionError(f"no se pudo leer el universo {path}: {error}") from error

    if version != manifest_version:
        raise IngestionError(
            f"la versión del universo difiere del manifiesto ({version} != {manifest_version})"
        )
    try:
        datetime.strptime(snapshot_date, "%Y-%m-%d")
    except ValueError as error:
        raise IngestionError("snapshot_date inválida en el universo") from error
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", snapshot_date):
        raise IngestionError("snapshot_date inválida en el universo")
    if not frame or not estimation_sample:
        raise IngestionError("el universo debe declarar frame y estimation_sample")
    _validate_https(official_source, "country_universe")
    if countries != manifest_countries:
        raise IngestionError("los países del universo difieren del manifiesto")
    if not countries or len(countries) != len(set(countries)):
        raise IngestionError("el universo debe contener países únicos")
    if membership_count != len(countries):
        raise IngestionError("membership_count difiere del número de países")
    if not 1 <= frontier_min_countries <= membership_count:
        raise IngestionError("frontier_min_countries es inválido")
    for field, value in {
        "require_complete_indicator_window": require_complete,
        "allow_imputation_for_eligibility": allow_imputation,
        "retain_flagged_observations": retain_flagged,
    }.items():
        if not isinstance(value, bool):
            raise IngestionError(f"{field} debe ser booleano en el universo")
    if not isinstance(raw_masks, list) or not raw_masks:
        raise IngestionError("el universo debe declarar input_masks")

    masks: list[UniverseMask] = []
    try:
        for raw_mask in raw_masks:
            masks.append(
                UniverseMask(
                    indicator_id=str(raw_mask["indicator_id"]),
                    included_countries=tuple(
                        str(value) for value in raw_mask["included_countries"]
                    ),
                    excluded_countries=tuple(
                        str(value) for value in raw_mask["excluded_countries"]
                    ),
                )
            )
    except (KeyError, TypeError) as error:
        raise IngestionError(f"máscara de insumo incompleta: {error}") from error

    mask_ids = [mask.indicator_id for mask in masks]
    spec_ids = [spec.indicator_id for spec in specs]
    if len(mask_ids) != len(set(mask_ids)):
        raise IngestionError("input_masks contiene indicator_id duplicados")
    if set(mask_ids) != set(spec_ids):
        raise IngestionError("input_masks no coincide con las series automáticas")
    universe_set = set(countries)
    specs_by_id = {spec.indicator_id: spec for spec in specs}
    for mask in masks:
        included = set(mask.included_countries)
        excluded = set(mask.excluded_countries)
        if (
            len(included) != len(mask.included_countries)
            or len(excluded) != len(mask.excluded_countries)
            or included & excluded
            or included | excluded != universe_set
        ):
            raise IngestionError(f"máscara de países inválida para {mask.indicator_id}")
        if tuple(mask.included_countries) != specs_by_id[mask.indicator_id].expected_entities:
            raise IngestionError(
                f"la máscara de {mask.indicator_id} difiere de expected_entities"
            )
        if len(included) < frontier_min_countries:
            raise IngestionError(
                f"la máscara de {mask.indicator_id} no alcanza el mínimo de frontera"
            )

    return CountryUniverse(
        path=path,
        sha256=sha256_hex(universe_bytes),
        version=version,
        snapshot_date=snapshot_date,
        frame=frame,
        official_source=official_source,
        countries=countries,
        membership_count=membership_count,
        estimation_sample=estimation_sample,
        frontier_min_countries=frontier_min_countries,
        require_complete_indicator_window=require_complete,
        allow_imputation_for_eligibility=allow_imputation,
        retain_flagged_observations=retain_flagged,
        input_masks=tuple(masks),
    )


def _load_manual_controls(
    path: Path | None,
    countries: tuple[str, ...],
) -> tuple[str | None, str | None, str | None, tuple[ManualControlSpec, ...]]:
    if path is None:
        return None, None, None, ()
    try:
        controls_bytes = path.read_bytes()
        raw = tomllib.load(io.BytesIO(controls_bytes))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise IngestionError(f"no se pudieron leer los controles manuales {path}: {error}") from error

    try:
        version = str(raw["version"])
        validation_date = str(raw["validation_date"])
        control_countries = tuple(str(value) for value in raw["countries"])
        raw_series = raw["series"]
    except (KeyError, TypeError) as error:
        raise IngestionError(f"estructura incompleta en {path}: {error}") from error
    if set(control_countries) != set(countries) or len(control_countries) != len(countries):
        raise IngestionError("los países de controles manuales difieren del manifiesto")
    if not isinstance(raw_series, list) or not raw_series:
        raise IngestionError("el archivo de controles manuales debe incluir series")
    try:
        datetime.strptime(validation_date, "%Y-%m-%d")
    except ValueError as error:
        raise IngestionError("validation_date inválida en controles manuales") from error
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", validation_date):
        raise IngestionError("validation_date inválida en controles manuales")
    return (
        version,
        validation_date,
        sha256_hex(controls_bytes),
        tuple(_parse_manual_control_spec(item, countries) for item in raw_series),
    )


def _parse_manual_control_spec(
    raw: Mapping[str, Any],
    countries: tuple[str, ...],
) -> ManualControlSpec:
    try:
        raw_observations = raw["observations"]
        if not isinstance(raw_observations, list):
            raise TypeError("observations debe ser una lista")
        values = tuple(
            ManualControlValue(
                entity=str(item["entity"]),
                period=_parse_year(item["period"]),
                value=_parse_decimal(item["value"], "control manual"),
                observation_status=str(item["observation_status"]),
            )
            for item in raw_observations
        )
        spec = ManualControlSpec(
            resource_id=str(raw["resource_id"]),
            indicator_id=str(raw["indicator_id"]),
            source_id=str(raw["source_id"]),
            source_status=str(raw["source_status"]),
            score_eligible=raw["score_eligible"],
            series_code=str(raw["series_code"]),
            source_url=str(raw["source_url"]),
            release=str(raw["release"]),
            locator=str(raw["locator"]),
            direction=str(raw["direction"]),
            unit=str(raw["unit"]),
            observations=values,
        )
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise IngestionError(f"control manual incompleto: {error}") from error

    if not _RESOURCE_ID.fullmatch(spec.resource_id):
        raise IngestionError(f"resource_id inválido: {spec.resource_id}")
    if spec.source_status not in _STATUSES:
        raise IngestionError(f"estado no permitido para {spec.indicator_id}")
    if not isinstance(spec.score_eligible, bool):
        raise IngestionError(f"score_eligible debe ser booleano para {spec.indicator_id}")
    if spec.score_eligible and spec.source_status != "validated":
        raise IngestionError(f"solo una fuente validada puede puntuar: {spec.indicator_id}")
    if spec.direction not in _DIRECTIONS or spec.direction == "input":
        raise IngestionError(f"dirección no permitida para {spec.indicator_id}")
    if not spec.series_code or not spec.release or not spec.locator:
        raise IngestionError(f"falta procedencia documental en {spec.indicator_id}")
    _validate_https(spec.source_url, spec.indicator_id)
    if not spec.observations:
        raise IngestionError(f"{spec.indicator_id} no tiene controles manuales")

    keys: set[tuple[str, int]] = set()
    represented_entities: set[str] = set()
    for value in spec.observations:
        if value.entity not in countries:
            raise IngestionError(f"entidad inesperada en {spec.indicator_id}: {value.entity}")
        key = (value.entity, value.period)
        if key in keys:
            raise IngestionError(f"control manual duplicado en {spec.indicator_id}: {key}")
        if value.observation_status not in _MANUAL_OBSERVATION_STATUSES:
            raise IngestionError(
                f"estado de observación no permitido en {spec.indicator_id}: "
                f"{value.observation_status!r}"
            )
        keys.add(key)
        represented_entities.add(value.entity)
    if represented_entities != set(countries):
        raise IngestionError(f"{spec.indicator_id} debe cubrir exactamente {countries}")
    return spec


def _parse_download_spec(
    raw: Mapping[str, Any],
    countries: tuple[str, ...],
    *,
    entity_aliases: Mapping[str, str] | None = None,
) -> DownloadSpec:
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
            comparison_url=_optional_text(raw, "comparison_url"),
            category_column=_optional_text(raw, "category_column"),
            expected_categories=tuple(str(value) for value in raw.get("expected_categories", [])),
            scale=_parse_decimal(raw.get("scale", 1), "scale"),
            level_url=_optional_text(raw, "level_url"),
            dimension_filters={
                str(key): str(value)
                for key, value in raw.get("dimension_filters", {}).items()
            },
            reference_year=(
                int(raw["reference_year"])
                if raw.get("reference_year") is not None
                else None
            ),
            worksheet=_optional_text(raw, "worksheet"),
            entity_column=_optional_text(raw, "entity_column"),
            value_column=_optional_text(raw, "value_column"),
            entity_aliases=dict(entity_aliases or {}),
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
    if not expected_entities or len(expected_entities) != len(set(expected_entities)):
        raise IngestionError(f"entidades esperadas inválidas en {spec.indicator_id}")
    if not set(expected_entities) <= set(countries):
        raise IngestionError(f"{spec.indicator_id} contiene países fuera del universo")
    if not latest_year or set(latest_year) != set(latest_value):
        raise IngestionError(f"checkpoints incompletos en {spec.indicator_id}")
    if not set(latest_year) <= set(expected_entities):
        raise IngestionError(f"checkpoint fuera de las entidades de {spec.indicator_id}")
    if spec.latest_value_tolerance < 0:
        raise IngestionError(f"tolerancia negativa en {spec.indicator_id}")
    if spec.minimum_observations_per_entity < 1:
        raise IngestionError(f"mínimo de observaciones inválido en {spec.indicator_id}")
    if spec.reference_year is not None:
        if spec.reference_year < 0:
            raise IngestionError(f"reference_year inválido en {spec.indicator_id}")
        if any(year > spec.reference_year for year in latest_year.values()):
            raise IngestionError(
                f"un checkpoint supera reference_year en {spec.indicator_id}"
            )
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
    if adapter in {
        "world_bank_percent_times_level",
        "oecd_percent_times_level",
        "oecd_ratio_times_level",
    }:
        if not spec.level_url:
            raise IngestionError(f"falta la serie de nivel en {spec.indicator_id}")
        _validate_https(spec.level_url, spec.indicator_id)
    if adapter == "world_bank_absolute_gap":
        if not spec.comparison_url:
            raise IngestionError(f"falta la serie de comparación en {spec.indicator_id}")
        _validate_https(spec.comparison_url, spec.indicator_id)
    if adapter == "oecd_regional_weighted_interdecile_gap":
        if not spec.level_url:
            raise IngestionError(f"falta la población regional en {spec.indicator_id}")
        _validate_https(spec.level_url, spec.indicator_id)
        if spec.reference_year is None:
            raise IngestionError(f"falta reference_year en {spec.indicator_id}")
    if adapter == "oecd_ratio_times_level":
        if not spec.denominator_url or not spec.category_column or not spec.expected_categories:
            raise IngestionError(f"faltan parámetros de razón en {spec.indicator_id}")
        _validate_https(spec.denominator_url, spec.indicator_id)
    if adapter == "oecd_pisa_xlsx":
        if (
            not spec.worksheet
            or not spec.entity_column
            or not spec.value_column
            or not spec.entity_aliases
        ):
            raise IngestionError(f"faltan parámetros XLSX PISA en {spec.indicator_id}")
        if not re.fullmatch(r"[A-Z]+", spec.entity_column) or not re.fullmatch(
            r"[A-Z]+", spec.value_column
        ):
            raise IngestionError(f"columnas XLSX inválidas en {spec.indicator_id}")
        if not set(spec.expected_entities) <= set(spec.entity_aliases.values()):
            raise IngestionError(f"aliases insuficientes para {spec.indicator_id}")
    if spec.dimension_filters is not None:
        if any(not key or not value for key, value in spec.dimension_filters.items()):
            raise IngestionError(f"filtros OECD inválidos en {spec.indicator_id}")
    return spec


def _optional_text(raw: Mapping[str, Any], key: str) -> str | None:
    value = raw.get(key)
    return None if value is None else str(value)


def _validate_https(url: str, indicator_id: str) -> None:
    if not url.startswith("https://"):
        raise IngestionError(f"URL no segura en {indicator_id}: {url}")


def _validate_against_catalog(
    manifest: DownloadManifest,
    catalog_bytes: bytes,
) -> None:
    try:
        catalog = tomllib.load(io.BytesIO(catalog_bytes))
    except tomllib.TOMLDecodeError as error:
        raise IngestionError(
            f"no se pudo leer el catálogo {manifest.catalog_path}: {error}"
        ) from error

    raw_catalog_entries = catalog.get("series", [])
    catalog_entries = {entry["indicator_id"]: entry for entry in raw_catalog_entries}
    if len(catalog_entries) != len(raw_catalog_entries):
        raise IngestionError("el catálogo contiene indicator_id duplicados")
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
        _validate_catalog_identity(spec, catalog_entry)
        if spec.url != catalog_entry.get("exact_url"):
            raise IngestionError(
                f"{spec.indicator_id}: la URL automática difiere del catálogo"
            )
        raw_dependency_urls = catalog_entry.get("dependency_urls", [])
        if not isinstance(raw_dependency_urls, list):
            raise IngestionError(
                f"{spec.indicator_id}: dependency_urls debe ser una lista"
            )
        catalog_dependency_urls = tuple(str(value) for value in raw_dependency_urls)
        if _dependency_urls(spec) != catalog_dependency_urls:
            raise IngestionError(
                f"{spec.indicator_id}: las dependencias difieren del catálogo"
            )
        catalog_reference_year = catalog_entry.get("reference_year")
        expected_reference_year = (
            int(catalog_reference_year) if catalog_reference_year is not None else None
        )
        if spec.reference_year != expected_reference_year:
            raise IngestionError(
                f"{spec.indicator_id}: reference_year difiere del catálogo"
            )
        expected_catalog_years, expected_catalog_values = _catalog_checkpoints(
            spec.indicator_id, catalog_entry
        )
        if dict(spec.expected_latest_year) != expected_catalog_years:
            raise IngestionError(
                f"{spec.indicator_id}: los años de control difieren del catálogo"
            )
        if dict(spec.expected_latest_value) != expected_catalog_values:
            raise IngestionError(
                f"{spec.indicator_id}: los valores de control difieren del catálogo"
            )

    for spec in manifest.manual_controls:
        catalog_entry = catalog_entries[spec.indicator_id]
        _validate_catalog_identity(spec, catalog_entry)
        if spec.source_url != catalog_entry.get("exact_url"):
            raise IngestionError(
                f"{spec.indicator_id}: la URL del control manual difiere del catálogo"
            )
        expected_years, expected_values = _catalog_checkpoints(
            spec.indicator_id, catalog_entry
        )
        latest = {
            entity: max(
                (value for value in spec.observations if value.entity == entity),
                key=lambda value: value.period,
            )
            for entity in manifest.countries
        }
        # El catálogo congela puntos de control para COL y USA. Un control
        # manual puede cubrir un universo mayor, cuyos países adicionales no
        # deben invalidar esos checkpoints canónicos.
        actual_years = {entity: latest[entity].period for entity in expected_years}
        actual_values = {entity: latest[entity].value for entity in expected_values}
        try:
            expected_statuses = {
                "COL": str(catalog_entry["latest_col_status"]),
                "USA": str(catalog_entry["latest_usa_status"]),
            }
        except KeyError as error:
            raise IngestionError(
                f"{spec.indicator_id}: faltan estados manuales en el catálogo"
            ) from error
        actual_statuses = {
            entity: latest[entity].observation_status for entity in expected_statuses
        }
        if actual_years != expected_years:
            raise IngestionError(
                f"{spec.indicator_id}: los años manuales difieren del catálogo"
            )
        if actual_values != expected_values:
            raise IngestionError(
                f"{spec.indicator_id}: los valores manuales difieren del catálogo"
            )
        if actual_statuses != expected_statuses:
            raise IngestionError(
                f"{spec.indicator_id}: los estados manuales difieren del catálogo"
            )


def _validate_catalog_identity(
    spec: DownloadSpec | ManualControlSpec,
    catalog_entry: Mapping[str, Any],
) -> None:
    comparisons = {
        "source_id": spec.source_id,
        "status": spec.source_status,
        "unit": spec.unit,
        "direction": spec.direction,
        "official_code": spec.series_code,
    }
    for field, actual in comparisons.items():
        expected = catalog_entry.get(field)
        if actual != expected:
            raise IngestionError(
                f"{spec.indicator_id}: {field} difiere del catálogo "
                f"({actual!r} != {expected!r})"
            )


def _dependency_urls(spec: DownloadSpec) -> tuple[str, ...]:
    if spec.adapter == "oecd_ppp_per_capita":
        assert spec.ppp_url is not None and spec.population_url is not None
        return (spec.ppp_url, spec.population_url)
    if spec.adapter in {"oecd_ratio_csv"}:
        assert spec.denominator_url is not None
        return (spec.denominator_url,)
    if spec.adapter in {"world_bank_percent_times_level", "oecd_percent_times_level"}:
        assert spec.level_url is not None
        return (spec.level_url,)
    if spec.adapter == "world_bank_absolute_gap":
        assert spec.comparison_url is not None
        return (spec.comparison_url,)
    if spec.adapter == "oecd_regional_weighted_interdecile_gap":
        assert spec.level_url is not None
        return (spec.level_url,)
    if spec.adapter == "oecd_ratio_times_level":
        assert spec.denominator_url is not None and spec.level_url is not None
        return (spec.denominator_url, spec.level_url)
    return ()


def _catalog_checkpoints(
    indicator_id: str,
    catalog_entry: Mapping[str, Any],
) -> tuple[dict[str, int], dict[str, Decimal]]:
    try:
        years = {
            "COL": int(catalog_entry["latest_col_year"]),
            "USA": int(catalog_entry["latest_usa_year"]),
        }
        values = {
            "COL": _parse_decimal(catalog_entry["latest_col_value"], "latest_col_value"),
            "USA": _parse_decimal(catalog_entry["latest_usa_value"], "latest_usa_value"),
        }
    except (KeyError, TypeError, ValueError) as error:
        raise IngestionError(
            f"{indicator_id}: falta un punto de control en el catálogo"
        ) from error
    return years, values


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


def parse_world_bank_percent_times_level(
    percent_payload: bytes,
    level_payload: bytes,
    spec: DownloadSpec,
) -> list[Observation]:
    """Convierte una participación del PIB en PPA constante por habitante."""

    percentages = _world_bank_value_map(percent_payload, spec.expected_entities)
    levels = _world_bank_value_map(level_payload, spec.expected_entities)
    missing_levels = sorted(set(percentages) - set(levels))
    if missing_levels:
        raise IngestionError(f"faltan niveles PPA para {missing_levels}")

    observations: list[Observation] = []
    for key, (percentage, percentage_status) in percentages.items():
        level, level_status = levels[key]
        if percentage < 0 or level <= 0:
            raise IngestionError(f"porcentaje o nivel inválido para {key}")
        observations.append(
            _make_observation(
                spec,
                entity=key[0],
                period=key[1],
                value=percentage / Decimal("100") * level,
                status=_quality_status([percentage_status, level_status]),
                kind="derived",
            )
        )
    return validate_observations(observations, spec)


def parse_world_bank_absolute_gap(
    primary_payload: bytes,
    comparison_payload: bytes,
    spec: DownloadSpec,
) -> list[Observation]:
    """Calcula una brecha absoluta entre dos series World Bank por país y año."""

    primary = _world_bank_value_map(primary_payload, spec.expected_entities)
    comparison = _world_bank_value_map(comparison_payload, spec.expected_entities)
    if set(primary) != set(comparison):
        missing_primary = sorted(set(comparison) - set(primary))
        missing_comparison = sorted(set(primary) - set(comparison))
        raise IngestionError(
            f"series incompletas para brecha absoluta en {spec.indicator_id}; "
            f"faltan_primaria={missing_primary}, faltan_comparación={missing_comparison}"
        )

    observations: list[Observation] = []
    for (entity, period), (primary_value, primary_status) in primary.items():
        comparison_value, comparison_status = comparison[(entity, period)]
        observations.append(
            _make_observation(
                spec,
                entity=entity,
                period=period,
                value=abs(primary_value - comparison_value),
                status=_quality_status([primary_status, comparison_status]),
                kind="derived",
            )
        )
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


def parse_oecd_regional_weighted_interdecile_gap(
    homicide_payload: bytes,
    population_payload: bytes,
    spec: DownloadSpec,
) -> list[Observation]:
    """Calcula P90-P10 de homicidios TL2 ponderado por población.

    El cuantil ponderado es la primera tasa cuya población acumulada, ordenada de
    menor a mayor tasa, alcanza el porcentaje solicitado. Así las regiones muy
    pequeñas no pesan igual que las zonas mucho más pobladas.
    """

    if spec.reference_year is None:
        raise IngestionError(f"falta reference_year en {spec.indicator_id}")

    homicides = _regional_oecd_map(
        homicide_payload, spec, measure="HOMIC", unit="CS_10P5PS"
    )
    populations = _regional_oecd_map(
        population_payload, spec, measure="POP", unit="PS"
    )
    # Algunas extracciones TL2 incluyen territorios técnicos con población cero
    # (por ejemplo, códigos residuales). No pueden ponderar una tasa y se omiten;
    # una región con homicidios pero sin población positiva sigue siendo un error.
    populations = {
        key: value for key, value in populations.items() if value[0] > 0
    }
    missing_populations = sorted(set(homicides) - set(populations))
    if missing_populations:
        raise IngestionError(
            f"poblaciones regionales faltantes para {spec.indicator_id}: "
            f"{missing_populations}"
        )
    populations = {key: populations[key] for key in homicides}

    by_country: dict[str, list[tuple[Decimal, Decimal, str, str, str]]] = defaultdict(list)
    for (country, region), (rate, rate_status) in homicides.items():
        population, population_status = populations[(country, region)]
        if rate < 0 or population <= 0:
            raise IngestionError(f"tasa o población regional inválida para {country}/{region}")
        by_country[country].append((rate, population, region, rate_status, population_status))

    observations: list[Observation] = []
    for country in spec.expected_entities:
        regions = by_country.get(country, [])
        if len(regions) < 3:
            raise IngestionError(
                f"{country} necesita al menos tres regiones TL2 en {spec.indicator_id}"
            )
        p10 = _weighted_regional_quantile(regions, Decimal("0.10"))
        p90 = _weighted_regional_quantile(regions, Decimal("0.90"))
        statuses = [status for _rate, _population, _region, *pair in regions for status in pair]
        observations.append(
            _make_observation(
                spec,
                entity=country,
                period=spec.reference_year,
                value=p90 - p10,
                status=_quality_status(statuses),
                kind="derived",
            )
        )
    return validate_observations(observations, spec)


def _regional_oecd_map(
    payload: bytes,
    spec: DownloadSpec,
    *,
    measure: str,
    unit: str,
) -> dict[tuple[str, str], tuple[Decimal, str]]:
    """Lee una serie TL2 de la OCDE y conserva solo el universo congelado."""

    try:
        rows = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    except UnicodeDecodeError as error:
        raise IngestionError(f"CSV regional inválido en {spec.indicator_id}: {error}") from error
    required = {
        "TERRITORIAL_LEVEL",
        "REF_AREA",
        "MEASURE",
        "AGE",
        "SEX",
        "UNIT_MEASURE",
        "TIME_PERIOD",
        "OBS_VALUE",
        "COUNTRY",
    }
    if rows.fieldnames is None or not required <= set(rows.fieldnames):
        raise IngestionError(f"columnas regionales incompletas en {spec.indicator_id}")

    expected = set(spec.expected_entities)
    values: dict[tuple[str, str], tuple[Decimal, str]] = {}
    for row in rows:
        country = row.get("COUNTRY", "")
        if country not in expected:
            continue
        if (
            row.get("TERRITORIAL_LEVEL") != "TL2"
            or row.get("MEASURE") != measure
            or row.get("AGE") != "_T"
            or row.get("SEX") != "_T"
            or row.get("UNIT_MEASURE") != unit
            or _parse_year(row.get("TIME_PERIOD")) != spec.reference_year
        ):
            raise IngestionError(f"fila regional incompatible en {spec.indicator_id}: {country}")
        region = row.get("REF_AREA", "")
        if not region:
            raise IngestionError(f"región TL2 ausente en {spec.indicator_id}")
        key = (country, region)
        if key in values:
            raise IngestionError(f"región TL2 duplicada en {spec.indicator_id}: {key}")
        values[key] = (_scaled_oecd_value(row), row.get("OBS_STATUS", ""))
    if not values:
        raise IngestionError(f"sin regiones TL2 utilizables en {spec.indicator_id}")
    return values


def _weighted_regional_quantile(
    regions: Sequence[tuple[Decimal, Decimal, str, str, str]],
    quantile: Decimal,
) -> Decimal:
    total_population = sum((population for _rate, population, *_rest in regions), Decimal("0"))
    if total_population <= 0:
        raise IngestionError("población regional total inválida")
    threshold = total_population * quantile
    accumulated = Decimal("0")
    for rate, population, region, _rate_status, _population_status in sorted(
        regions, key=lambda item: (item[0], item[2])
    ):
        accumulated += population
        if accumulated >= threshold:
            return rate
    raise IngestionError(f"no se alcanzó el cuantil regional para {region}")


def parse_oecd_pisa_xlsx(payload: bytes, spec: DownloadSpec) -> list[Observation]:
    """Extrae una columna de una tabla oficial PISA distribuida como XLSX.

    El libro de PISA 2022 no requiere una dependencia de ejecución: XLSX es un
    contenedor ZIP de XML. La configuración congela hoja, columnas y el mapeo de
    nombres OCDE a ISO3; los asteriscos publicados se preservan como cautelas de
    muestreo, en vez de descartarse silenciosamente.
    """

    if not spec.worksheet or not spec.entity_column or not spec.value_column:
        raise IngestionError(f"configuración XLSX incompleta para {spec.indicator_id}")
    if spec.reference_year is None:
        raise IngestionError(f"XLSX PISA exige reference_year en {spec.indicator_id}")

    cells = _xlsx_sheet_cells(payload, spec.worksheet)
    observations: list[Observation] = []
    for row_number, row in sorted(cells.items()):
        raw_label = row.get(spec.entity_column)
        raw_value = row.get(spec.value_column)
        if raw_label is None or raw_value is None:
            continue
        label = str(raw_label).strip()
        sampling_caution = label.endswith("*")
        canonical_label = label.rstrip("*").strip()
        entity = spec.entity_aliases.get(canonical_label)
        if entity is None or entity not in spec.expected_entities:
            continue
        if str(raw_value).strip().lower() in {"", "m"}:
            continue
        observations.append(
            _make_observation(
                spec,
                entity=entity,
                period=spec.reference_year,
                value=_parse_decimal(raw_value, f"PISA {spec.indicator_id} fila {row_number}"),
                status="source:sampling_caution" if sampling_caution else "observed",
                kind="reported",
            )
        )
    return validate_observations(observations, spec)


def _xlsx_sheet_cells(payload: bytes, worksheet_name: str) -> dict[int, dict[str, str]]:
    """Lee las celdas con valor de una hoja XLSX usando únicamente la biblioteca estándar."""

    spreadsheet_ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    office_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    package_ns = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
            relationship_id = next(
                (
                    sheet.attrib.get(f"{office_ns}id")
                    for sheet in workbook.findall(f"{spreadsheet_ns}sheets/{spreadsheet_ns}sheet")
                    if sheet.attrib.get("name") == worksheet_name
                ),
                None,
            )
            if relationship_id is None:
                raise IngestionError(f"hoja XLSX no encontrada: {worksheet_name}")
            relationships = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
            target = next(
                (
                    relation.attrib.get("Target")
                    for relation in relationships.findall(f"{package_ns}Relationship")
                    if relation.attrib.get("Id") == relationship_id
                ),
                None,
            )
            if not target:
                raise IngestionError(f"relación XLSX no encontrada: {worksheet_name}")
            target_path = target.lstrip("/")
            if not target_path.startswith("xl/"):
                target_path = f"xl/{target_path}"
            shared_strings = _xlsx_shared_strings(archive, spreadsheet_ns)
            sheet = ElementTree.fromstring(archive.read(target_path))
    except (KeyError, OSError, ValueError, zipfile.BadZipFile, ElementTree.ParseError) as error:
        raise IngestionError(f"XLSX PISA inválido: {error}") from error

    rows: dict[int, dict[str, str]] = {}
    for row in sheet.findall(f".//{spreadsheet_ns}row"):
        try:
            row_number = int(row.attrib["r"])
        except (KeyError, ValueError) as error:
            raise IngestionError("fila XLSX sin referencia válida") from error
        values: dict[str, str] = {}
        for cell in row.findall(f"{spreadsheet_ns}c"):
            reference = cell.attrib.get("r", "")
            match = re.fullmatch(r"([A-Z]+)[1-9][0-9]*", reference)
            if not match:
                continue
            value = _xlsx_cell_value(cell, spreadsheet_ns, shared_strings)
            if value is not None:
                values[match.group(1)] = value
        if values:
            rows[row_number] = values
    return rows


def _xlsx_shared_strings(
    archive: zipfile.ZipFile,
    spreadsheet_ns: str,
) -> list[str]:
    try:
        root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return [
        "".join(node.text or "" for node in item.iter(f"{spreadsheet_ns}t"))
        for item in root.findall(f"{spreadsheet_ns}si")
    ]


def _xlsx_cell_value(
    cell: ElementTree.Element,
    spreadsheet_ns: str,
    shared_strings: Sequence[str],
) -> str | None:
    value_node = cell.find(f"{spreadsheet_ns}v")
    if value_node is None or value_node.text is None:
        return None
    value = value_node.text
    if cell.attrib.get("t") != "s":
        return value
    try:
        return shared_strings[int(value)]
    except (IndexError, ValueError) as error:
        raise IngestionError("índice de cadena compartida XLSX inválido") from error


def parse_oecd_percent_times_level(
    percent_payload: bytes,
    level_payload: bytes,
    spec: DownloadSpec,
) -> list[Observation]:
    """Convierte una participación OECD del PIB en PPA constante por habitante."""

    percentage_rows = _unique_oecd_rows(
        _read_oecd_rows(
            percent_payload,
            spec.expected_entities,
            dimension_filters=spec.dimension_filters,
        )
    )
    levels = _world_bank_value_map(level_payload, spec.expected_entities)
    missing_levels = sorted(set(percentage_rows) - set(levels))
    if missing_levels:
        raise IngestionError(f"faltan niveles PPA para {missing_levels}")

    observations: list[Observation] = []
    for key, row in percentage_rows.items():
        percentage = _scaled_oecd_value(row)
        level, level_status = levels[key]
        if percentage < 0 or level <= 0:
            raise IngestionError(f"porcentaje o nivel inválido para {key}")
        observations.append(
            _make_observation(
                spec,
                entity=key[0],
                period=key[1],
                value=percentage / Decimal("100") * level,
                status=_quality_status([row.get("OBS_STATUS", ""), level_status]),
                kind="derived",
            )
        )
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


def parse_oecd_ratio_times_level(
    numerator_payload: bytes,
    denominator_payload: bytes,
    level_payload: bytes,
    spec: DownloadSpec,
) -> list[Observation]:
    """Multiplica una razón OECD por un nivel PPA constante de WDI."""

    if not spec.category_column or not spec.expected_categories:
        raise IngestionError(f"configuración de razón incompleta para {spec.indicator_id}")
    numerator_rows = _read_oecd_rows(
        numerator_payload,
        spec.expected_entities,
        additional_columns=(spec.category_column,),
        dimension_filters=spec.dimension_filters,
    )
    denominator_rows = _read_oecd_rows(denominator_payload, spec.expected_entities)
    levels = _world_bank_value_map(level_payload, spec.expected_entities)

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
    missing_denominators = sorted(set(grouped) - set(denominators))
    missing_levels = sorted(set(grouped) - set(levels))
    if missing_denominators:
        raise IngestionError(f"faltan denominadores para {missing_denominators}")
    if missing_levels:
        raise IngestionError(f"faltan niveles PPA para {missing_levels}")

    observations: list[Observation] = []
    for key, components in grouped.items():
        if set(components) != set(spec.expected_categories):
            continue
        denominator_row = denominators[key]
        _validate_same_currency([*components.values(), denominator_row], key)
        numerator = sum((_scaled_oecd_value(row) for row in components.values()), Decimal())
        denominator = _scaled_oecd_value(denominator_row)
        level, level_status = levels[key]
        if denominator == 0 or level <= 0:
            raise IngestionError(f"denominador o nivel inválido para {key}")
        statuses = [row.get("OBS_STATUS", "") for row in components.values()]
        statuses.extend([denominator_row.get("OBS_STATUS", ""), level_status])
        observations.append(
            _make_observation(
                spec,
                entity=key[0],
                period=key[1],
                value=numerator / denominator * level * spec.scale,
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
    dimension_filters: Mapping[str, str] | None = None,
) -> list[dict[str, str]]:
    if payload.lstrip().startswith((b"<?xml", b"<message:")):
        raise IngestionError("OECD devolvió XML; la consulta debe solicitar format=csvfile")
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise IngestionError(f"SDMX-CSV no está en UTF-8: {error}") from error
    reader = csv.DictReader(io.StringIO(text))
    filters = dimension_filters or {}
    required = {
        "REF_AREA",
        "TIME_PERIOD",
        "OBS_VALUE",
        *additional_columns,
        *filters,
    }
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
        for column, expected in filters.items():
            if row.get(column) != expected:
                raise IngestionError(
                    f"dimensión OECD inesperada en {column}: "
                    f"{row.get(column)!r} != {expected!r}"
                )
        if row.get("OBS_VALUE") in (None, ""):
            continue
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


def manual_control_observations(spec: ManualControlSpec) -> list[Observation]:
    """Materializa puntos oficiales transcritos sin presentarlos como una descarga."""

    return sorted(
        [
            Observation(
                entity=value.entity,
                period=value.period,
                indicator_id=spec.indicator_id,
                value=value.value,
                direction=spec.direction,
                unit=spec.unit,
                source_id=spec.source_id,
                series_code=spec.series_code,
                source_status=spec.source_status,
                score_eligible=spec.score_eligible,
                observation_status=value.observation_status,
                observation_kind="manual_control",
                resource_id=spec.resource_id,
            )
            for value in spec.observations
        ],
        key=lambda row: (row.entity, row.period, row.indicator_id),
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

    for entity, expected_latest in spec.expected_latest_year.items():
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


def _manifest_input_paths(manifest_file: Path, manifest: DownloadManifest) -> set[Path]:
    paths = {manifest_file.resolve(), manifest.catalog_path.resolve()}
    if manifest.manual_controls_path is not None:
        paths.add(manifest.manual_controls_path.resolve())
    if manifest.country_universe is not None:
        paths.add(manifest.country_universe.path.resolve())
    return paths


def _validate_pipeline_paths(
    manifest_file: Path,
    manifest: DownloadManifest,
    raw_root: Path,
    processed_file: Path,
    provenance_file: Path,
) -> None:
    inputs = _manifest_input_paths(manifest_file, manifest)
    outputs = [processed_file.resolve(), provenance_file.resolve()]
    if len(outputs) != len(set(outputs)):
        raise IngestionError("las rutas de salida deben ser únicas")
    collisions = sorted(path.as_posix() for path in set(outputs) & inputs)
    if collisions:
        raise IngestionError(
            f"una salida no puede sobrescribir una entrada: {', '.join(collisions)}"
        )
    raw_resolved = raw_root.resolve()
    if raw_resolved in inputs or raw_resolved in outputs:
        raise IngestionError("raw_dir no puede ser una ruta de entrada o salida")


def _validate_raw_targets(
    manifest_file: Path,
    manifest: DownloadManifest,
    raw_targets: Sequence[Path],
    output_targets: Sequence[Path],
) -> None:
    inputs = _manifest_input_paths(manifest_file, manifest)
    outputs = {path.resolve() for path in output_targets}
    raw = {path.resolve() for path in raw_targets}
    collisions = sorted(path.as_posix() for path in raw & (inputs | outputs))
    if collisions:
        raise IngestionError(
            f"un recurso crudo no puede sobrescribir una entrada o salida: "
            f"{', '.join(collisions)}"
        )


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
    raw_root = Path(raw_dir)
    processed_file = Path(processed_path)
    provenance_file = Path(provenance_path)
    _validate_pipeline_paths(
        manifest_file,
        manifest,
        raw_root,
        processed_file,
        provenance_file,
    )
    observations: list[Observation] = []
    payloads: list[tuple[str, str, FetchedPayload]] = []
    series_summaries: list[dict[str, Any]] = []
    universe_masks = (
        {
            mask.indicator_id: mask
            for mask in manifest.country_universe.input_masks
        }
        if manifest.country_universe is not None
        else {}
    )

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
        record_counts = Counter(row.entity for row in series_observations)
        summary: dict[str, Any] = {
            "indicator_id": spec.indicator_id,
            "resource_id": spec.resource_id,
            "acquisition_mode": "automatic",
            "records": len(series_observations),
            "records_by_entity": {
                entity: record_counts[entity] for entity in spec.expected_entities
            },
            "latest_year": {
                entity: row.period for entity, row in latest_rows.items()
            },
            "latest_value": {
                entity: _decimal_text(row.value) for entity, row in latest_rows.items()
            },
            "reference_year": spec.reference_year,
            "vintage_age": (
                {
                    entity: spec.reference_year - row.period
                    for entity, row in latest_rows.items()
                }
                if spec.reference_year is not None
                else None
            ),
            "dimension_filters": dict(spec.dimension_filters or {}),
            "score_eligible": spec.score_eligible,
            "source_status": spec.source_status,
        }
        mask = universe_masks.get(spec.indicator_id)
        if mask is not None:
            assert manifest.country_universe is not None
            summary["country_mask"] = {
                "frame": manifest.country_universe.frame,
                "included_countries": list(mask.included_countries),
                "included_count": len(mask.included_countries),
                "excluded_countries": list(mask.excluded_countries),
                "excluded_count": len(mask.excluded_countries),
                "frontier_min_countries": (
                    manifest.country_universe.frontier_min_countries
                ),
                "frontier_min_met": (
                    len(mask.included_countries)
                    >= manifest.country_universe.frontier_min_countries
                ),
            }
        series_summaries.append(summary)

    for spec in manifest.manual_controls:
        series_observations = manual_control_observations(spec)
        observations.extend(series_observations)
        latest_rows = {
            entity: max(
                (row for row in series_observations if row.entity == entity),
                key=lambda row: row.period,
            )
            for entity in manifest.countries
        }
        series_summaries.append(
            {
                "indicator_id": spec.indicator_id,
                "resource_id": spec.resource_id,
                "acquisition_mode": "manual_control",
                "source_url": spec.source_url,
                "release": spec.release,
                "locator": spec.locator,
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

    _validate_raw_targets(
        manifest_file,
        manifest,
        tuple(raw_writes),
        (processed_file, provenance_file),
    )

    timestamp = retrieved_at or datetime.now(UTC).replace(microsecond=0).isoformat()
    manual_controls_metadata = None
    if manifest.manual_controls_path is not None:
        manual_controls_metadata = {
            "path": manifest.manual_controls_path.as_posix(),
            "sha256": manifest.manual_controls_sha256,
            "version": manifest.manual_controls_version,
            "validation_date": manifest.manual_controls_validation_date,
            "indicator_ids": list(manifest.manual_control_ids),
        }
    country_universe_metadata = None
    if manifest.country_universe is not None:
        universe = manifest.country_universe
        country_universe_metadata = {
            "path": universe.path.as_posix(),
            "sha256": universe.sha256,
            "version": universe.version,
            "snapshot_date": universe.snapshot_date,
            "frame": universe.frame,
            "official_source": universe.official_source,
            "countries": list(universe.countries),
            "membership_count": universe.membership_count,
            "estimation_sample": universe.estimation_sample,
            "frontier_min_countries": universe.frontier_min_countries,
            "require_complete_indicator_window": (
                universe.require_complete_indicator_window
            ),
            "allow_imputation_for_eligibility": (
                universe.allow_imputation_for_eligibility
            ),
            "retain_flagged_observations": universe.retain_flagged_observations,
            "input_masks": [
                {
                    "indicator_id": mask.indicator_id,
                    "included_countries": list(mask.included_countries),
                    "excluded_countries": list(mask.excluded_countries),
                    "included_count": len(mask.included_countries),
                    "frontier_min_met": (
                        len(mask.included_countries) >= universe.frontier_min_countries
                    ),
                }
                for mask in universe.input_masks
            ],
        }
    provenance = {
        "schema_version": manifest.schema_version,
        "manifest_version": manifest.version,
        "retrieved_at": timestamp,
        "manifest": {
            "path": manifest_file.as_posix(),
            "sha256": manifest.manifest_sha256,
        },
        "catalog": {
            "path": manifest.catalog_path.as_posix(),
            "sha256": manifest.catalog_sha256,
        },
        "manual_controls": manual_controls_metadata,
        "country_universe": country_universe_metadata,
        "countries": list(manifest.countries),
        "resources": raw_entries,
        "series": series_summaries,
        "series_counts": {
            "automatic": len(manifest.series),
            "manual_control": len(manifest.manual_controls),
            "materialized": len(manifest.series) + len(manifest.manual_controls),
        },
        "manual_control_ids": list(manifest.manual_control_ids),
        "deferred_ids": list(manifest.deferred_ids),
        "processed": {
            "path": processed_file.as_posix(),
            "records": len(observations),
            "sha256": processed_hash,
        },
    }
    provenance_bytes = (
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    for path, content in raw_writes.items():
        _atomic_write_bytes(path, content)
    _atomic_write_publication(
        (
            (processed_file, processed_bytes),
            (provenance_file, provenance_bytes),
        )
    )

    return PipelineResult(
        observation_count=len(observations),
        series_count=len(manifest.series) + len(manifest.manual_controls),
        raw_resource_count=len(raw_entries),
        processed_path=processed_file,
        provenance_path=provenance_file,
        processed_sha256=processed_hash,
    )


def _acquire_series(
    spec: DownloadSpec,
    *,
    timeout: float,
    max_bytes: int,
    fetcher: Fetcher,
) -> tuple[list[Observation], list[tuple[str, str, FetchedPayload]]]:
    primary_accept = (
        _JSON_ACCEPT
        if spec.adapter
        in {"world_bank_json", "world_bank_absolute_gap", "world_bank_percent_times_level"}
        else (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if spec.adapter == "oecd_pisa_xlsx"
            else _CSV_ACCEPT
        )
    )
    primary = fetcher(spec.url, accept=primary_accept, timeout=timeout, max_bytes=max_bytes)
    _validate_content_type(
        primary,
        (
            "json"
            if spec.adapter
            in {"world_bank_json", "world_bank_absolute_gap", "world_bank_percent_times_level"}
            else "xlsx"
            if spec.adapter == "oecd_pisa_xlsx"
            else "csv"
        ),
    )
    payloads = [(spec.resource_id, "primary", primary)]

    if spec.adapter == "world_bank_json":
        return parse_world_bank_json(primary.content, spec), payloads
    if spec.adapter == "world_bank_absolute_gap":
        assert spec.comparison_url is not None
        comparison = fetcher(
            spec.comparison_url,
            accept=_JSON_ACCEPT,
            timeout=timeout,
            max_bytes=max_bytes,
        )
        _validate_content_type(comparison, "json")
        payloads.append((spec.resource_id, "comparison", comparison))
        return parse_world_bank_absolute_gap(primary.content, comparison.content, spec), payloads
    if spec.adapter == "world_bank_percent_times_level":
        assert spec.level_url is not None
        level = fetcher(
            spec.level_url,
            accept=_JSON_ACCEPT,
            timeout=timeout,
            max_bytes=max_bytes,
        )
        _validate_content_type(level, "json")
        payloads.append((spec.resource_id, "level", level))
        return parse_world_bank_percent_times_level(primary.content, level.content, spec), payloads
    if spec.adapter == "oecd_sdmx_csv":
        return parse_oecd_sdmx_csv(primary.content, spec), payloads
    if spec.adapter == "oecd_regional_weighted_interdecile_gap":
        assert spec.level_url is not None
        population = fetcher(
            spec.level_url,
            accept=_CSV_ACCEPT,
            timeout=timeout,
            max_bytes=max_bytes,
        )
        _validate_content_type(population, "csv")
        payloads.append((spec.resource_id, "population", population))
        return (
            parse_oecd_regional_weighted_interdecile_gap(
                primary.content,
                population.content,
                spec,
            ),
            payloads,
        )
    if spec.adapter == "oecd_pisa_xlsx":
        return parse_oecd_pisa_xlsx(primary.content, spec), payloads
    if spec.adapter == "oecd_percent_times_level":
        assert spec.level_url is not None
        level = fetcher(
            spec.level_url,
            accept=_JSON_ACCEPT,
            timeout=timeout,
            max_bytes=max_bytes,
        )
        _validate_content_type(level, "json")
        payloads.append((spec.resource_id, "level", level))
        return parse_oecd_percent_times_level(primary.content, level.content, spec), payloads
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
    if spec.adapter == "oecd_ratio_times_level":
        assert spec.denominator_url is not None and spec.level_url is not None
        denominator = fetcher(
            spec.denominator_url,
            accept=_CSV_ACCEPT,
            timeout=timeout,
            max_bytes=max_bytes,
        )
        level = fetcher(
            spec.level_url,
            accept=_JSON_ACCEPT,
            timeout=timeout,
            max_bytes=max_bytes,
        )
        _validate_content_type(denominator, "csv")
        _validate_content_type(level, "json")
        payloads.extend(
            [
                (spec.resource_id, "denominator", denominator),
                (spec.resource_id, "level", level),
            ]
        )
        return (
            parse_oecd_ratio_times_level(
                primary.content,
                denominator.content,
                level.content,
                spec,
            ),
            payloads,
        )
    raise IngestionError(f"adaptador no implementado: {spec.adapter}")


def _validate_content_type(payload: FetchedPayload, expected: str) -> None:
    content_type = payload.content_type.lower()
    if expected == "json":
        valid = "json" in content_type or payload.content.lstrip().startswith((b"[", b"{"))
    elif expected == "csv":
        valid = "csv" in content_type and not payload.content.lstrip().startswith(b"<")
    else:
        valid = "spreadsheetml" in content_type and payload.content.startswith(b"PK")
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
    temporary_path = _stage_bytes(path, content)
    try:
        os.replace(temporary_path, path)
    except OSError as error:
        if temporary_path.exists():
            temporary_path.unlink()
        raise IngestionError(f"no se pudo escribir {path}: {error}") from error


def _atomic_write_publication(outputs: Sequence[tuple[Path, bytes]]) -> None:
    """Publica salidas relacionadas y restaura la versión anterior ante un fallo."""

    targets = [path for path, _content in outputs]
    resolved_targets = [path.resolve() for path in targets]
    if not targets or len(resolved_targets) != len(set(resolved_targets)):
        raise IngestionError("la publicación debe incluir rutas únicas")

    staged: dict[Path, Path] = {}
    backups: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for path, content in outputs:
            staged[path] = _stage_bytes(path, content)
            if path.exists():
                backups[path] = _stage_bytes(path, path.read_bytes())

        try:
            for path in targets:
                os.replace(staged[path], path)
                replaced.append(path)
        except OSError as error:
            rollback_errors: list[str] = []
            for path in reversed(replaced):
                try:
                    backup = backups.get(path)
                    if backup is None:
                        path.unlink(missing_ok=True)
                    else:
                        os.replace(backup, path)
                except OSError as rollback_error:
                    rollback_errors.append(f"{path}: {rollback_error}")
            detail = (
                f"; rollback incompleto: {'; '.join(rollback_errors)}"
                if rollback_errors
                else ""
            )
            raise IngestionError(f"falló la publicación conjunta{detail}") from error
    finally:
        for temporary_path in (*staged.values(), *backups.values()):
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass


def _stage_bytes(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
    except OSError as error:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise IngestionError(f"no se pudo preparar {path}: {error}") from error
    assert temporary_path is not None
    return temporary_path
