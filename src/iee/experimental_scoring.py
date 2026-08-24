"""Motor reproducible de diagnóstico experimental; no calcula un IEE oficial."""

from __future__ import annotations

import csv
import io
import json
import math
import re
import tomllib
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex
from .scoring import bounded_scores, weighted_geometric_mean, weighted_mean


class ExperimentalScoringError(RuntimeError):
    """Error de contrato, entrada o publicación del diagnóstico experimental."""


@dataclass(frozen=True)
class IndicatorRule:
    indicator_id: str
    dimension: str
    role: str
    selection: str
    direction: str
    transform: str
    lower_bound: Decimal
    upper_bound: Decimal
    bound_status: str
    bound_reference: str
    flags: tuple[str, ...]
    year: int | None = None
    start_year: int | None = None
    end_year: int | None = None


@dataclass(frozen=True)
class DimensionRule:
    id: str
    label: str
    weight: Decimal
    input_indicator_id: str
    input_selection: str
    input_compatible: bool
    input_reason: str
    input_start_year: int | None = None
    input_end_year: int | None = None


@dataclass(frozen=True)
class SensitivityRule:
    id: str
    description: str
    aggregation: str
    result_weight_multiplier: Decimal
    override_indicator_id: str | None = None
    override_selection: str | None = None
    override_year: int | None = None
    override_start_year: int | None = None
    override_end_year: int | None = None
    override_transform: str | None = None
    override_upper_bound: Decimal | None = None
    exclude_observation_statuses: tuple[str, ...] = ()
    add_flags: tuple[str, ...] = ()
    remove_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class CatalogSeriesIdentity:
    indicator_id: str
    direction: str
    unit: str
    source_id: str
    source_status: str
    series_code: str


@dataclass(frozen=True)
class ExperimentConfig:
    version: str
    schema_version: str
    ingestion_schema_version: str
    status: str
    reference_cutoff_year: int
    countries: tuple[str, ...]
    input_sha256: str
    catalog_path: Path
    methodology_path: Path
    aggregation: str
    minimum_role_coverage: Decimal
    minimum_dimension_coverage: Decimal
    frontier_min_countries: int
    official_roles: tuple[str, ...]
    role_weights: Mapping[str, Decimal]
    dimensions: tuple[DimensionRule, ...]
    indicators: tuple[IndicatorRule, ...]
    sensitivity: tuple[SensitivityRule, ...]
    catalog_series: Mapping[str, CatalogSeriesIdentity]
    config_sha256: str
    catalog_sha256: str
    methodology_sha256: str


@dataclass(frozen=True)
class SourceObservation:
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
class IndicatorDiagnostic:
    entity: str
    dimension: str
    indicator_id: str
    role: str
    period_start: int
    period_end: int
    periods: tuple[int, ...]
    raw_value: Decimal
    transformed_value: float
    score: float
    direction: str
    transform: str
    lower_bound: Decimal
    upper_bound: Decimal
    bound_status: str
    bound_reference: str
    unit: str
    source_id: str
    observation_statuses: tuple[str, ...]
    flags: tuple[str, ...]


@dataclass(frozen=True)
class DiagnosticRow:
    entity: str
    level: str
    component_id: str
    label: str
    diagnostic_score: float
    official_iee_score: None
    coverage: Decimal
    available_roles: tuple[str, ...]
    missing_roles: tuple[str, ...]
    input_compatible: bool
    frontier_eligible: bool
    publication_eligible: bool
    flags: tuple[str, ...]


@dataclass(frozen=True)
class ContextRow:
    entity: str
    dimension: str
    indicator_id: str
    period_start: int | None
    period_end: int | None
    value: Decimal | None
    unit: str
    source_status: str
    observation_statuses: tuple[str, ...]
    input_compatible: bool
    reason: str
    flags: tuple[str, ...]


@dataclass(frozen=True)
class SensitivityRow:
    scenario_id: str
    description: str
    entity: str
    level: str
    component_id: str
    diagnostic_score: float
    base_score: float
    delta_from_base: float
    flags: tuple[str, ...]


@dataclass(frozen=True)
class ExperimentResult:
    indicator_count: int
    diagnostic_count: int
    sensitivity_count: int
    context_count: int
    diagnostic_composite: Mapping[str, float]
    official_iee_score: None
    publication_eligible: bool
    indicator_path: Path
    diagnostic_path: Path
    sensitivity_path: Path
    context_path: Path
    provenance_path: Path
    output_sha256: Mapping[str, str]


_AGGREGATIONS = {"weighted-geometric-mean", "weighted-mean"}
_DIRECTIONS = {"higher", "lower"}
_SELECTIONS = {"point", "mean"}
_TRANSFORMS = {"linear", "log1p"}
_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load_experiment_config(path: str | Path) -> ExperimentConfig:
    """Carga y cruza la configuración experimental con catálogo y metodología."""

    config_path = Path(path)
    config_bytes, raw = _load_toml(config_path, "configuración experimental")
    try:
        catalog_path = config_path.parent / str(raw["catalog"])
        methodology_path = config_path.parent / str(raw["methodology"])
        catalog_bytes, catalog = _load_toml(catalog_path, "catálogo")
        methodology_bytes, methodology = _load_toml(methodology_path, "metodología")
        countries = tuple(str(value) for value in raw["countries"])
        official_roles = tuple(str(value) for value in raw["official_roles"])
        role_weights = {
            str(role): _decimal(value, f"peso de rol {role}")
            for role, value in raw["role_weights"].items()
        }
        dimensions = tuple(_parse_dimension(item) for item in raw["dimensions"])
        indicators = tuple(_parse_indicator(item) for item in raw["indicators"])
        sensitivity = tuple(_parse_sensitivity(item) for item in raw.get("sensitivity", []))
        catalog_series = {
            str(item["indicator_id"]): _parse_catalog_identity(item)
            for item in catalog["series"]
        }
        config = ExperimentConfig(
            version=str(raw["version"]),
            schema_version=str(raw["schema_version"]),
            ingestion_schema_version=str(raw["ingestion_schema_version"]),
            status=str(raw["status"]),
            reference_cutoff_year=int(raw["reference_cutoff_year"]),
            countries=countries,
            input_sha256=str(raw["input_sha256"]),
            catalog_path=catalog_path,
            methodology_path=methodology_path,
            aggregation=str(raw["aggregation"]),
            minimum_role_coverage=_decimal(
                raw["minimum_role_coverage"], "minimum_role_coverage"
            ),
            minimum_dimension_coverage=_decimal(
                raw["minimum_dimension_coverage"], "minimum_dimension_coverage"
            ),
            frontier_min_countries=int(raw["frontier_min_countries"]),
            official_roles=official_roles,
            role_weights=role_weights,
            dimensions=dimensions,
            indicators=indicators,
            sensitivity=sensitivity,
            catalog_series=catalog_series,
            config_sha256=sha256_hex(config_bytes),
            catalog_sha256=sha256_hex(catalog_bytes),
            methodology_sha256=sha256_hex(methodology_bytes),
        )
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise ExperimentalScoringError(
            f"estructura incompleta en {config_path}: {error}"
        ) from error

    _validate_config(config, catalog, methodology)
    return config


def _load_toml(path: Path, label: str) -> tuple[bytes, Mapping[str, Any]]:
    try:
        content = path.read_bytes()
        document = tomllib.load(io.BytesIO(content))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ExperimentalScoringError(f"no se pudo leer {label} {path}: {error}") from error
    return content, document


def _parse_dimension(raw: Mapping[str, Any]) -> DimensionRule:
    return DimensionRule(
        id=str(raw["id"]),
        label=str(raw["label"]),
        weight=_decimal(raw["weight"], "peso de dimensión"),
        input_indicator_id=str(raw["input_indicator_id"]),
        input_selection=str(raw["input_selection"]),
        input_compatible=raw["input_compatible"],
        input_reason=str(raw["input_reason"]),
        input_start_year=_optional_int(raw, "input_start_year"),
        input_end_year=_optional_int(raw, "input_end_year"),
    )


def _parse_indicator(raw: Mapping[str, Any]) -> IndicatorRule:
    return IndicatorRule(
        indicator_id=str(raw["indicator_id"]),
        dimension=str(raw["dimension"]),
        role=str(raw["role"]),
        selection=str(raw["selection"]),
        direction=str(raw["direction"]),
        transform=str(raw["transform"]),
        lower_bound=_decimal(raw["lower_bound"], "límite inferior"),
        upper_bound=_decimal(raw["upper_bound"], "límite superior"),
        bound_status=str(raw["bound_status"]),
        bound_reference=str(raw["bound_reference"]),
        flags=tuple(str(value) for value in raw.get("flags", [])),
        year=_optional_int(raw, "year"),
        start_year=_optional_int(raw, "start_year"),
        end_year=_optional_int(raw, "end_year"),
    )


def _parse_sensitivity(raw: Mapping[str, Any]) -> SensitivityRule:
    return SensitivityRule(
        id=str(raw["id"]),
        description=str(raw["description"]),
        aggregation=str(raw["aggregation"]),
        result_weight_multiplier=_decimal(
            raw["result_weight_multiplier"], "multiplicador de resultado"
        ),
        override_indicator_id=_optional_text(raw, "override_indicator_id"),
        override_selection=_optional_text(raw, "override_selection"),
        override_year=_optional_int(raw, "override_year"),
        override_start_year=_optional_int(raw, "override_start_year"),
        override_end_year=_optional_int(raw, "override_end_year"),
        override_transform=_optional_text(raw, "override_transform"),
        override_upper_bound=(
            _decimal(raw["override_upper_bound"], "límite alternativo")
            if "override_upper_bound" in raw
            else None
        ),
        exclude_observation_statuses=tuple(
            str(value) for value in raw.get("exclude_observation_statuses", [])
        ),
        add_flags=tuple(str(value) for value in raw.get("add_flags", [])),
        remove_flags=tuple(str(value) for value in raw.get("remove_flags", [])),
    )


def _parse_catalog_identity(raw: Mapping[str, Any]) -> CatalogSeriesIdentity:
    return CatalogSeriesIdentity(
        indicator_id=str(raw["indicator_id"]),
        direction=str(raw["direction"]),
        unit=str(raw["unit"]),
        source_id=str(raw["source_id"]),
        source_status=str(raw["status"]),
        series_code=str(raw["official_code"]),
    )


def _optional_text(raw: Mapping[str, Any], key: str) -> str | None:
    value = raw.get(key)
    return None if value is None else str(value)


def _optional_int(raw: Mapping[str, Any], key: str) -> int | None:
    value = raw.get(key)
    return None if value is None else int(value)


def _decimal(value: Any, context: str) -> Decimal:
    if isinstance(value, bool) or value in (None, ""):
        raise ExperimentalScoringError(f"valor numérico inválido en {context}")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ExperimentalScoringError(f"valor no numérico en {context}: {value!r}") from error
    if not number.is_finite():
        raise ExperimentalScoringError(f"valor no finito en {context}: {value!r}")
    return number


def _validate_config(
    config: ExperimentConfig,
    catalog: Mapping[str, Any],
    methodology: Mapping[str, Any],
) -> None:
    if config.status != "experimental-not-for-publication":
        raise ExperimentalScoringError("la configuración debe bloquear publicación")
    if not config.ingestion_schema_version:
        raise ExperimentalScoringError("ingestion_schema_version no puede estar vacío")
    if not config.countries or len(config.countries) != len(set(config.countries)):
        raise ExperimentalScoringError("countries debe contener códigos únicos")
    if not _HEX_SHA256.fullmatch(config.input_sha256):
        raise ExperimentalScoringError("input_sha256 inválido")
    if config.aggregation not in _AGGREGATIONS:
        raise ExperimentalScoringError("agregación no permitida")
    if not config.official_roles or len(config.official_roles) != len(set(config.official_roles)):
        raise ExperimentalScoringError("official_roles debe contener roles únicos")
    if set(config.role_weights) != set(config.official_roles):
        raise ExperimentalScoringError("los pesos deben cubrir todos los roles oficiales")
    if any(weight <= 0 for weight in config.role_weights.values()):
        raise ExperimentalScoringError("los pesos de roles deben ser positivos")
    if sum(config.role_weights.values()) != Decimal("1"):
        raise ExperimentalScoringError("los pesos de roles deben sumar 1")
    if not Decimal("0") < config.minimum_role_coverage <= Decimal("1"):
        raise ExperimentalScoringError("minimum_role_coverage inválido")
    if not Decimal("0") < config.minimum_dimension_coverage <= Decimal("1"):
        raise ExperimentalScoringError("minimum_dimension_coverage inválido")
    if config.frontier_min_countries < 3:
        raise ExperimentalScoringError("frontier_min_countries debe ser al menos 3")

    dimension_ids = [dimension.id for dimension in config.dimensions]
    if len(dimension_ids) != len(set(dimension_ids)) or not dimension_ids:
        raise ExperimentalScoringError("las dimensiones deben ser únicas")
    if sum(dimension.weight for dimension in config.dimensions) != Decimal("1"):
        raise ExperimentalScoringError("los pesos de dimensiones deben sumar 1")
    for dimension in config.dimensions:
        if dimension.weight <= 0:
            raise ExperimentalScoringError(f"peso inválido en {dimension.id}")
        if dimension.input_selection not in {"latest", "mean"}:
            raise ExperimentalScoringError(f"selección de insumo inválida en {dimension.id}")
        if not isinstance(dimension.input_compatible, bool):
            raise ExperimentalScoringError(f"input_compatible inválido en {dimension.id}")
        if dimension.input_selection == "mean":
            if (
                dimension.input_start_year is None
                or dimension.input_end_year is None
                or dimension.input_end_year < dimension.input_start_year
            ):
                raise ExperimentalScoringError(f"ventana de insumo inválida en {dimension.id}")
            if dimension.input_end_year > config.reference_cutoff_year:
                raise ExperimentalScoringError(
                    f"ventana de insumo posterior al corte en {dimension.id}"
                )

    indicator_ids = [rule.indicator_id for rule in config.indicators]
    if len(indicator_ids) != len(set(indicator_ids)) or not indicator_ids:
        raise ExperimentalScoringError("los indicadores experimentales deben ser únicos")
    for rule in config.indicators:
        if rule.dimension not in dimension_ids:
            raise ExperimentalScoringError(f"dimensión desconocida en {rule.indicator_id}")
        if rule.role not in config.official_roles:
            raise ExperimentalScoringError(f"rol desconocido en {rule.indicator_id}")
        if rule.selection not in _SELECTIONS:
            raise ExperimentalScoringError(f"selección inválida en {rule.indicator_id}")
        if rule.direction not in _DIRECTIONS:
            raise ExperimentalScoringError(f"dirección inválida en {rule.indicator_id}")
        if rule.transform not in _TRANSFORMS:
            raise ExperimentalScoringError(f"transformación inválida en {rule.indicator_id}")
        if not rule.bound_status or not rule.bound_reference:
            raise ExperimentalScoringError(f"metadatos de límites vacíos en {rule.indicator_id}")
        if rule.upper_bound <= rule.lower_bound:
            raise ExperimentalScoringError(f"límites inválidos en {rule.indicator_id}")
        if rule.transform == "log1p" and rule.lower_bound <= -1:
            raise ExperimentalScoringError(f"log1p inválido en {rule.indicator_id}")
        if rule.selection == "point" and rule.year is None:
            raise ExperimentalScoringError(f"falta año puntual en {rule.indicator_id}")
        if rule.selection == "mean" and (
            rule.start_year is None
            or rule.end_year is None
            or rule.end_year < rule.start_year
        ):
            raise ExperimentalScoringError(f"ventana inválida en {rule.indicator_id}")
        years = [year for year in (rule.year, rule.start_year, rule.end_year) if year is not None]
        if any(year > config.reference_cutoff_year for year in years):
            raise ExperimentalScoringError(f"año posterior al corte en {rule.indicator_id}")

    catalog_entries = {
        str(entry["indicator_id"]): entry for entry in catalog.get("series", [])
    }
    for rule in config.indicators:
        entry = catalog_entries.get(rule.indicator_id)
        if entry is None:
            raise ExperimentalScoringError(f"{rule.indicator_id} no existe en el catálogo")
        expected = {
            "dimension": rule.dimension,
            "role": rule.role,
            "direction": rule.direction,
            "status": "validated",
        }
        for field, actual in expected.items():
            if entry.get(field) != actual:
                raise ExperimentalScoringError(
                    f"{rule.indicator_id}: {field} difiere del catálogo"
                )
    for dimension in config.dimensions:
        entry = catalog_entries.get(dimension.input_indicator_id)
        if entry is None or entry.get("dimension") != dimension.id or entry.get("role") != "insumo":
            raise ExperimentalScoringError(f"insumo incoherente en {dimension.id}")

    method_dimensions = {
        str(item["id"]): _decimal(item["weight"], "peso metodológico")
        for item in methodology.get("dimensions", [])
    }
    if method_dimensions != {dimension.id: dimension.weight for dimension in config.dimensions}:
        raise ExperimentalScoringError("los pesos de dimensiones difieren de la metodología")
    if str(methodology.get("aggregation")) != config.aggregation:
        raise ExperimentalScoringError("la agregación difiere de la metodología")
    if _decimal(
        methodology.get("minimum_indicator_coverage"), "cobertura metodológica"
    ) != config.minimum_role_coverage:
        raise ExperimentalScoringError("la cobertura de roles difiere de la metodología")
    if _decimal(
        methodology.get("minimum_dimension_coverage"), "cobertura metodológica"
    ) != config.minimum_dimension_coverage:
        raise ExperimentalScoringError("la cobertura de dimensiones difiere de la metodología")

    sensitivity_ids = [scenario.id for scenario in config.sensitivity]
    if len(sensitivity_ids) != len(set(sensitivity_ids)):
        raise ExperimentalScoringError("los escenarios de sensibilidad deben ser únicos")
    indicator_rules = {rule.indicator_id: rule for rule in config.indicators}
    for scenario in config.sensitivity:
        if scenario.aggregation not in _AGGREGATIONS:
            raise ExperimentalScoringError(f"agregación inválida en {scenario.id}")
        if scenario.result_weight_multiplier <= 0:
            raise ExperimentalScoringError(f"multiplicador inválido en {scenario.id}")
        if scenario.override_indicator_id not in (None, *indicator_ids):
            raise ExperimentalScoringError(f"indicador alternativo inválido en {scenario.id}")
        if scenario.override_selection not in (None, *_SELECTIONS):
            raise ExperimentalScoringError(f"selección alternativa inválida en {scenario.id}")
        if scenario.override_transform not in (None, *_TRANSFORMS):
            raise ExperimentalScoringError(
                f"transformación alternativa inválida en {scenario.id}"
            )
        if set(scenario.add_flags) & set(scenario.remove_flags):
            raise ExperimentalScoringError(f"flags alternativos contradictorios en {scenario.id}")
        indicator_overrides = (
            scenario.override_selection,
            scenario.override_year,
            scenario.override_start_year,
            scenario.override_end_year,
            scenario.override_transform,
            scenario.override_upper_bound,
        )
        if scenario.override_indicator_id is None and (
            any(value is not None for value in indicator_overrides)
            or scenario.add_flags
            or scenario.remove_flags
        ):
            raise ExperimentalScoringError(
                f"override sin indicador objetivo en {scenario.id}"
            )
        if scenario.override_indicator_id is not None:
            base_rule = indicator_rules[scenario.override_indicator_id]
            effective_rule = _effective_indicator_rule(base_rule, scenario)
            if effective_rule.upper_bound <= effective_rule.lower_bound:
                raise ExperimentalScoringError(f"límite alternativo inválido en {scenario.id}")
            if effective_rule.transform == "log1p" and effective_rule.lower_bound <= -1:
                raise ExperimentalScoringError(f"log1p alternativo inválido en {scenario.id}")
            if effective_rule.selection == "mean" and (
                effective_rule.start_year is None
                or effective_rule.end_year is None
                or effective_rule.end_year < effective_rule.start_year
            ):
                raise ExperimentalScoringError(f"ventana alternativa inválida en {scenario.id}")
            if effective_rule.selection == "point" and effective_rule.year is None:
                raise ExperimentalScoringError(f"falta año puntual alternativo en {scenario.id}")
            if effective_rule.selection == "point" and (
                scenario.override_start_year is not None
                or scenario.override_end_year is not None
            ):
                raise ExperimentalScoringError(
                    f"ventana mean incompatible con selección point en {scenario.id}"
                )
            if effective_rule.selection == "mean" and scenario.override_year is not None:
                raise ExperimentalScoringError(
                    f"año point incompatible con selección mean en {scenario.id}"
                )
            years = [
                year
                for year in (
                    effective_rule.year,
                    effective_rule.start_year,
                    effective_rule.end_year,
                )
                if year is not None
            ]
            if any(year > config.reference_cutoff_year for year in years):
                raise ExperimentalScoringError(
                    f"año alternativo posterior al corte en {scenario.id}"
                )


def _effective_indicator_rule(
    rule: IndicatorRule,
    scenario: SensitivityRule | None,
) -> IndicatorRule:
    if scenario is None or scenario.override_indicator_id != rule.indicator_id:
        return rule
    return replace(
        rule,
        selection=scenario.override_selection or rule.selection,
        year=scenario.override_year if scenario.override_year is not None else rule.year,
        start_year=(
            scenario.override_start_year
            if scenario.override_start_year is not None
            else rule.start_year
        ),
        end_year=(
            scenario.override_end_year
            if scenario.override_end_year is not None
            else rule.end_year
        ),
        upper_bound=(
            scenario.override_upper_bound
            if scenario.override_upper_bound is not None
            else rule.upper_bound
        ),
        transform=scenario.override_transform or rule.transform,
        flags=tuple(
            sorted(
                (set(rule.flags) - set(scenario.remove_flags))
                | set(scenario.add_flags)
            )
        ),
    )


def read_normalized_observations(payload: bytes) -> list[SourceObservation]:
    """Lee el CSV normalizado y conserva solo tipos explícitos y claves únicas."""

    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ExperimentalScoringError(f"CSV normalizado no está en UTF-8: {error}") from error
    reader = csv.DictReader(io.StringIO(text))
    required = {
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
    }
    if not reader.fieldnames or not required <= set(reader.fieldnames):
        missing = sorted(required - set(reader.fieldnames or []))
        raise ExperimentalScoringError(f"faltan columnas normalizadas: {missing}")

    observations: list[SourceObservation] = []
    keys: set[tuple[str, int, str]] = set()
    for row in reader:
        try:
            period = int(row["period"])
        except ValueError as error:
            raise ExperimentalScoringError(f"año inválido: {row['period']!r}") from error
        score_text = row["score_eligible"].strip().lower()
        if score_text not in {"true", "false"}:
            raise ExperimentalScoringError("score_eligible no es booleano")
        observation = SourceObservation(
            entity=row["entity"],
            period=period,
            indicator_id=row["indicator_id"],
            value=_decimal(row["value"], "observación normalizada"),
            direction=row["direction"],
            unit=row["unit"],
            source_id=row["source_id"],
            series_code=row["series_code"],
            source_status=row["source_status"],
            score_eligible=score_text == "true",
            observation_status=row["observation_status"],
            observation_kind=row["observation_kind"],
            resource_id=row["resource_id"],
        )
        if not observation.entity or not observation.indicator_id:
            raise ExperimentalScoringError("entity e indicator_id no pueden estar vacíos")
        if not observation.observation_status or not observation.resource_id:
            raise ExperimentalScoringError("estado y resource_id no pueden estar vacíos")
        if observation.observation_kind not in {"reported", "derived", "manual_control"}:
            raise ExperimentalScoringError(
                f"observation_kind inválido: {observation.observation_kind!r}"
            )
        key = (observation.entity, observation.period, observation.indicator_id)
        if key in keys:
            raise ExperimentalScoringError(f"clave duplicada en CSV: {key}")
        keys.add(key)
        observations.append(observation)
    if not observations:
        raise ExperimentalScoringError("el CSV normalizado está vacío")
    return observations


def _validate_observation_contract(
    config: ExperimentConfig,
    observations: Sequence[SourceObservation],
) -> None:
    scored_ids = {rule.indicator_id for rule in config.indicators}
    context_ids = {dimension.input_indicator_id for dimension in config.dimensions}
    allowed_ids = scored_ids | context_ids
    for row in observations:
        if row.indicator_id not in allowed_ids:
            eligibility = "elegible" if row.score_eligible else "no configurada"
            raise ExperimentalScoringError(
                f"serie {eligibility} fuera del experimento: {row.indicator_id}"
            )
        identity = config.catalog_series.get(row.indicator_id)
        if identity is None:
            raise ExperimentalScoringError(f"serie fuera del catálogo: {row.indicator_id}")
        expected = {
            "direction": identity.direction,
            "unit": identity.unit,
            "source_id": identity.source_id,
            "source_status": identity.source_status,
            "series_code": identity.series_code,
        }
        for field, value in expected.items():
            if getattr(row, field) != value:
                raise ExperimentalScoringError(
                    f"{row.indicator_id}/{row.entity}: {field} difiere del catálogo"
                )
        expected_eligibility = row.indicator_id in scored_ids
        if row.score_eligible != expected_eligibility:
            raise ExperimentalScoringError(
                f"elegibilidad inconsistente en {row.indicator_id}/{row.entity}"
            )


def _select_indicator(
    rule: IndicatorRule,
    observations: Sequence[SourceObservation],
    entity: str,
    *,
    cutoff_year: int,
    scenario: SensitivityRule | None = None,
) -> IndicatorDiagnostic | None:
    effective_rule = _effective_indicator_rule(rule, scenario)
    excluded_statuses: set[str] = set()
    if scenario is not None:
        excluded_statuses = set(scenario.exclude_observation_statuses)

    candidates = [
        row
        for row in observations
        if row.entity == entity
        and row.indicator_id == rule.indicator_id
        and row.period <= cutoff_year
        and row.observation_status not in excluded_statuses
    ]
    if effective_rule.selection == "point":
        assert effective_rule.year is not None
        selected = [row for row in candidates if row.period == effective_rule.year]
        expected_periods = (effective_rule.year,)
    else:
        assert effective_rule.start_year is not None and effective_rule.end_year is not None
        expected_periods = tuple(
            range(effective_rule.start_year, effective_rule.end_year + 1)
        )
        selected = [row for row in candidates if row.period in expected_periods]

    if not selected and excluded_statuses:
        return None
    if tuple(sorted(row.period for row in selected)) != expected_periods:
        raise ExperimentalScoringError(
            f"ventana incompleta en {rule.indicator_id}/{entity}: "
            f"{sorted(row.period for row in selected)} != {list(expected_periods)}"
        )
    for row in selected:
        if not row.score_eligible or row.source_status != "validated":
            raise ExperimentalScoringError(
                f"observación no elegible: {rule.indicator_id}/{entity}"
            )
        if row.direction != rule.direction:
            raise ExperimentalScoringError(
                f"dirección inconsistente: {rule.indicator_id}/{entity}"
            )
    if len({row.unit for row in selected}) != 1 or len({row.source_id for row in selected}) != 1:
        raise ExperimentalScoringError(f"metadatos variables: {rule.indicator_id}/{entity}")

    raw_value = sum((row.value for row in selected), Decimal()) / Decimal(len(selected))
    score, transformed_value, clipping_flags = _normalize(raw_value, effective_rule)
    statuses = tuple(sorted({row.observation_status for row in selected}))
    flags = set(effective_rule.flags) | set(clipping_flags)
    if "source:sampling_caution" in statuses:
        flags.add("source_sampling_caution")
    if any(row.observation_kind == "manual_control" for row in selected):
        flags.add("manual_control")
    return IndicatorDiagnostic(
        entity=entity,
        dimension=rule.dimension,
        indicator_id=rule.indicator_id,
        role=rule.role,
        period_start=min(expected_periods),
        period_end=max(expected_periods),
        periods=expected_periods,
        raw_value=raw_value,
        transformed_value=transformed_value,
        score=score,
        direction=rule.direction,
        transform=rule.transform,
        lower_bound=effective_rule.lower_bound,
        upper_bound=effective_rule.upper_bound,
        bound_status=effective_rule.bound_status,
        bound_reference=effective_rule.bound_reference,
        unit=selected[0].unit,
        source_id=selected[0].source_id,
        observation_statuses=statuses,
        flags=tuple(sorted(flags)),
    )


def _normalize(value: Decimal, rule: IndicatorRule) -> tuple[float, float, tuple[str, ...]]:
    raw = float(value)
    lower = float(rule.lower_bound)
    upper = float(rule.upper_bound)
    flags: list[str] = []
    if raw < lower:
        flags.append("clipped_lower")
    if raw > upper:
        flags.append("clipped_upper")
    if rule.transform == "log1p":
        if raw <= -1 or lower <= -1 or upper <= -1:
            raise ExperimentalScoringError(f"log1p fuera de dominio en {rule.indicator_id}")
        transformed = math.log1p(raw)
        transformed_lower = math.log1p(lower)
        transformed_upper = math.log1p(upper)
    else:
        transformed = raw
        transformed_lower = lower
        transformed_upper = upper
    score = bounded_scores(
        [transformed],
        lower_bound=transformed_lower,
        upper_bound=transformed_upper,
        higher_is_better=rule.direction == "higher",
    )[0]
    return score, transformed, tuple(flags)


def _aggregate(
    scores: Mapping[str, float],
    weights: Mapping[str, float],
    method: str,
) -> float:
    if method == "weighted-geometric-mean":
        return weighted_geometric_mean(scores, weights)
    if method == "weighted-mean":
        return weighted_mean(scores, weights)
    raise ExperimentalScoringError(f"agregación no implementada: {method}")


def _build_diagnostics(
    config: ExperimentConfig,
    selected: Sequence[IndicatorDiagnostic],
    *,
    aggregation: str,
    result_weight_multiplier: Decimal,
) -> list[DiagnosticRow]:
    by_entity_dimension: dict[tuple[str, str], list[IndicatorDiagnostic]] = defaultdict(list)
    for row in selected:
        by_entity_dimension[(row.entity, row.dimension)].append(row)

    dimension_rows: list[DiagnosticRow] = []
    sample_size_eligible = len(config.countries) >= config.frontier_min_countries
    for entity in config.countries:
        for dimension in config.dimensions:
            rows = by_entity_dimension[(entity, dimension.id)]
            by_role: dict[str, list[IndicatorDiagnostic]] = defaultdict(list)
            for row in rows:
                by_role[row.role].append(row)
            role_scores: dict[str, float] = {}
            for role, role_rows in by_role.items():
                role_scores[role] = weighted_geometric_mean(
                    {row.indicator_id: row.score for row in role_rows},
                    {row.indicator_id: 1.0 for row in role_rows},
                )
            available_roles = tuple(role for role in config.official_roles if role in role_scores)
            missing_roles = tuple(role for role in config.official_roles if role not in role_scores)
            if not available_roles:
                raise ExperimentalScoringError(f"sin diagnóstico para {dimension.id}/{entity}")
            coverage = sum(config.role_weights[role] for role in available_roles)
            weights = {
                role: float(
                    config.role_weights[role]
                    * (result_weight_multiplier if role == "resultado" else Decimal("1"))
                )
                for role in available_roles
            }
            diagnostic_score = _aggregate(role_scores, weights, aggregation)
            frontier_eligible = (
                sample_size_eligible
                and dimension.input_compatible
                and not missing_roles
                and coverage >= config.minimum_role_coverage
            )
            flags = {
                "experimental_only",
                "not_efficiency_score",
                "publication_blocked",
                "official_iee_null",
                "no_valid_input",
            }
            if missing_roles:
                flags.add("partial_dimension")
                flags.add("partial_roles_reweighted_for_diagnostic")
                flags.update(f"missing_required_role:{role}" for role in missing_roles)
            if coverage < config.minimum_role_coverage:
                flags.add("coverage_below_075")
            if len(rows) == 1:
                flags.add("single_indicator_proxy")
            if not frontier_eligible:
                flags.add(f"frontier_not_estimable_n_lt_{config.frontier_min_countries}")
            for row in rows:
                flags.update(row.flags)
            if len({(row.period_start, row.period_end) for row in rows}) > 1:
                flags.add("mixed_vintage")
            dimension_rows.append(
                DiagnosticRow(
                    entity=entity,
                    level="dimension",
                    component_id=dimension.id,
                    label=dimension.label,
                    diagnostic_score=diagnostic_score,
                    official_iee_score=None,
                    coverage=coverage,
                    available_roles=available_roles,
                    missing_roles=missing_roles,
                    input_compatible=dimension.input_compatible,
                    frontier_eligible=frontier_eligible,
                    publication_eligible=False,
                    flags=tuple(sorted(flags)),
                )
            )

    by_entity = defaultdict(list)
    for row in dimension_rows:
        by_entity[row.entity].append(row)
    composite_rows: list[DiagnosticRow] = []
    for entity in config.countries:
        rows = by_entity[entity]
        scores = {row.component_id: row.diagnostic_score for row in rows}
        weights = {
            dimension.id: float(dimension.weight) for dimension in config.dimensions
        }
        diagnostic_score = _aggregate(scores, weights, aggregation)
        coverage = sum(
            dimension.weight
            for dimension in config.dimensions
            if next(row for row in rows if row.component_id == dimension.id).coverage
            >= config.minimum_role_coverage
        )
        flags = {
            "experimental_only",
            "not_efficiency_score",
            "publication_blocked",
            "ranking_blocked",
            "official_iee_null",
            "mixed_vintage",
            f"frontier_not_estimable_n_lt_{config.frontier_min_countries}",
            "no_valid_input",
        }
        if coverage < config.minimum_dimension_coverage:
            flags.add("dimension_coverage_below_075")
        if any("pandemic_sensitive" in row.flags for row in rows):
            flags.add("pandemic_sensitive")
        if any("pandemic_window_excluded" in row.flags for row in rows):
            flags.add("pandemic_window_excluded")
        if any("source_sampling_caution" in row.flags for row in rows):
            flags.add("source_sampling_caution")
        if any("bounds_provisional" in row.flags for row in rows):
            flags.add("bounds_provisional")
        frontier_eligible = all(row.frontier_eligible for row in rows)
        composite_rows.append(
            DiagnosticRow(
                entity=entity,
                level="composite",
                component_id="diagnostic_outcome_composite",
                label="Compuesto diagnóstico de resultados",
                diagnostic_score=diagnostic_score,
                official_iee_score=None,
                coverage=coverage,
                available_roles=(),
                missing_roles=(),
                input_compatible=False,
                frontier_eligible=frontier_eligible,
                publication_eligible=False,
                flags=tuple(sorted(flags)),
            )
        )
    return dimension_rows + composite_rows


def _select_all(
    config: ExperimentConfig,
    observations: Sequence[SourceObservation],
    scenario: SensitivityRule | None = None,
) -> list[IndicatorDiagnostic]:
    selected: list[IndicatorDiagnostic] = []
    globally_excluded = _globally_excluded_indicators(config, observations, scenario)
    for entity in config.countries:
        for rule in config.indicators:
            if rule.indicator_id in globally_excluded:
                continue
            row = _select_indicator(
                rule,
                observations,
                entity,
                cutoff_year=config.reference_cutoff_year,
                scenario=scenario,
            )
            if row is not None:
                selected.append(row)
    return selected


def _globally_excluded_indicators(
    config: ExperimentConfig,
    observations: Sequence[SourceObservation],
    scenario: SensitivityRule | None,
) -> set[str]:
    """Excluye una serie para todos los países si una cautela afecta a cualquiera."""

    if scenario is None or not scenario.exclude_observation_statuses:
        return set()
    excluded_statuses = set(scenario.exclude_observation_statuses)
    excluded_indicators: set[str] = set()
    for rule in config.indicators:
        effective_rule = _effective_indicator_rule(rule, scenario)
        if effective_rule.selection == "point":
            assert effective_rule.year is not None
            periods = {effective_rule.year}
        else:
            assert effective_rule.start_year is not None
            assert effective_rule.end_year is not None
            periods = set(range(effective_rule.start_year, effective_rule.end_year + 1))
        if any(
            row.entity in config.countries
            and row.indicator_id == rule.indicator_id
            and row.period in periods
            and row.observation_status in excluded_statuses
            for row in observations
        ):
            excluded_indicators.add(rule.indicator_id)
    return excluded_indicators


def _build_context(
    config: ExperimentConfig,
    observations: Sequence[SourceObservation],
) -> list[ContextRow]:
    rows: list[ContextRow] = []
    for entity in config.countries:
        for dimension in config.dimensions:
            candidates = sorted(
                (
                    row
                    for row in observations
                    if row.entity == entity
                    and row.indicator_id == dimension.input_indicator_id
                    and row.period <= config.reference_cutoff_year
                ),
                key=lambda row: row.period,
            )
            selected: list[SourceObservation] = []
            flags = {"context_only", "not_scored", "no_valid_input"}
            if dimension.input_selection == "latest" and candidates:
                selected = [candidates[-1]]
            elif dimension.input_selection == "mean":
                assert dimension.input_start_year is not None
                assert dimension.input_end_year is not None
                expected = tuple(
                    range(dimension.input_start_year, dimension.input_end_year + 1)
                )
                selected = [row for row in candidates if row.period in expected]
                if tuple(row.period for row in selected) != expected:
                    selected = []
                    flags.add("input_window_incomplete")
            if not selected:
                flags.add("input_not_materialized")
                rows.append(
                    ContextRow(
                        entity=entity,
                        dimension=dimension.id,
                        indicator_id=dimension.input_indicator_id,
                        period_start=None,
                        period_end=None,
                        value=None,
                        unit="",
                        source_status="",
                        observation_statuses=(),
                        input_compatible=dimension.input_compatible,
                        reason=dimension.input_reason,
                        flags=tuple(sorted(flags)),
                    )
                )
                continue
            value = sum((row.value for row in selected), Decimal()) / Decimal(len(selected))
            statuses = tuple(sorted({row.observation_status for row in selected}))
            if "provisional" in statuses:
                flags.add("provisional")
            rows.append(
                ContextRow(
                    entity=entity,
                    dimension=dimension.id,
                    indicator_id=dimension.input_indicator_id,
                    period_start=selected[0].period,
                    period_end=selected[-1].period,
                    value=value,
                    unit=selected[0].unit,
                    source_status=selected[0].source_status,
                    observation_statuses=statuses,
                    input_compatible=dimension.input_compatible,
                    reason=dimension.input_reason,
                    flags=tuple(sorted(flags)),
                )
            )
    periods_by_dimension: dict[str, set[int]] = defaultdict(set)
    for row in rows:
        if row.period_end is not None:
            periods_by_dimension[row.dimension].add(row.period_end)
    return [
        replace(
            row,
            flags=tuple(sorted((*row.flags, "non_harmonized_vintage"))),
        )
        if len(periods_by_dimension[row.dimension]) > 1
        else row
        for row in rows
    ]


def _build_sensitivity(
    config: ExperimentConfig,
    observations: Sequence[SourceObservation],
    base_rows: Sequence[DiagnosticRow],
) -> list[SensitivityRow]:
    base = {(row.entity, row.level, row.component_id): row for row in base_rows}
    results = [
        SensitivityRow(
            scenario_id="base",
            description="Configuración experimental base.",
            entity=row.entity,
            level=row.level,
            component_id=row.component_id,
            diagnostic_score=row.diagnostic_score,
            base_score=row.diagnostic_score,
            delta_from_base=0.0,
            flags=row.flags,
        )
        for row in base_rows
    ]
    for scenario in config.sensitivity:
        globally_excluded = _globally_excluded_indicators(config, observations, scenario)
        selected = _select_all(config, observations, scenario)
        scenario_rows = _build_diagnostics(
            config,
            selected,
            aggregation=scenario.aggregation,
            result_weight_multiplier=scenario.result_weight_multiplier,
        )
        for row in scenario_rows:
            base_row = base[(row.entity, row.level, row.component_id)]
            scenario_flags = set(row.flags)
            affected_dimensions = {
                rule.dimension
                for rule in config.indicators
                if rule.indicator_id in globally_excluded
            }
            if row.level == "composite" or row.component_id in affected_dimensions:
                scenario_flags.update(
                    f"globally_excluded_indicator:{indicator_id}"
                    for indicator_id in globally_excluded
                )
            results.append(
                SensitivityRow(
                    scenario_id=scenario.id,
                    description=scenario.description,
                    entity=row.entity,
                    level=row.level,
                    component_id=row.component_id,
                    diagnostic_score=row.diagnostic_score,
                    base_score=base_row.diagnostic_score,
                    delta_from_base=row.diagnostic_score - base_row.diagnostic_score,
                    flags=tuple(sorted(scenario_flags)),
                )
            )
    return results


def _validate_publication_paths(
    config: ExperimentConfig,
    config_path: str | Path,
    observations_path: str | Path,
    ingestion_provenance_path: str | Path,
    outputs: Sequence[str | Path],
) -> None:
    input_paths = {
        Path(config_path).resolve(),
        config.catalog_path.resolve(),
        config.methodology_path.resolve(),
        Path(observations_path).resolve(),
        Path(ingestion_provenance_path).resolve(),
    }
    output_paths = [Path(path).resolve() for path in outputs]
    if len(output_paths) != len(set(output_paths)):
        raise ExperimentalScoringError("las rutas de salida deben ser únicas")
    collisions = sorted(path.as_posix() for path in set(output_paths) & input_paths)
    if collisions:
        raise ExperimentalScoringError(
            f"una salida no puede sobrescribir una entrada: {', '.join(collisions)}"
        )


def run_experiment(
    config_path: str | Path,
    *,
    observations_path: str | Path,
    ingestion_provenance_path: str | Path,
    indicator_path: str | Path,
    diagnostic_path: str | Path,
    sensitivity_path: str | Path,
    context_path: str | Path,
    provenance_path: str | Path,
    calculated_at: str | None = None,
) -> ExperimentResult:
    """Calcula diagnósticos, aplica gates y publica todas las salidas juntas."""

    config = load_experiment_config(config_path)
    _validate_publication_paths(
        config,
        config_path,
        observations_path,
        ingestion_provenance_path,
        (
            indicator_path,
            diagnostic_path,
            sensitivity_path,
            context_path,
            provenance_path,
        ),
    )
    source_path = Path(observations_path)
    receipt_path = Path(ingestion_provenance_path)
    try:
        source_bytes = source_path.read_bytes()
        receipt_bytes = receipt_path.read_bytes()
        receipt = json.loads(receipt_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ExperimentalScoringError(f"no se pudieron leer las entradas: {error}") from error
    source_hash = sha256_hex(source_bytes)
    if source_hash != config.input_sha256:
        raise ExperimentalScoringError(
            f"el snapshot normalizado difiere de la configuración: {source_hash}"
        )
    try:
        receipt_hash = str(receipt["processed"]["sha256"])
        receipt_records = int(receipt["processed"]["records"])
        receipt_schema = str(receipt["schema_version"])
        receipt_catalog_hash = str(receipt["catalog"]["sha256"])
        receipt_countries = tuple(str(country) for country in receipt["countries"])
    except (KeyError, TypeError, ValueError) as error:
        raise ExperimentalScoringError("recibo de ingestión incompleto") from error
    if receipt_hash != source_hash:
        raise ExperimentalScoringError("el hash del CSV no coincide con el recibo")
    if receipt_schema != config.ingestion_schema_version:
        raise ExperimentalScoringError("el esquema del recibo no coincide con la configuración")
    if receipt_catalog_hash != config.catalog_sha256:
        raise ExperimentalScoringError("el catálogo del recibo no coincide con la configuración")
    if receipt_countries != config.countries:
        raise ExperimentalScoringError("los países del recibo difieren de la configuración")

    observations = read_normalized_observations(source_bytes)
    if len(observations) != receipt_records:
        raise ExperimentalScoringError("el conteo del CSV no coincide con el recibo")
    if {row.entity for row in observations} != set(config.countries):
        raise ExperimentalScoringError("los países del CSV difieren de la configuración")
    _validate_observation_contract(config, observations)

    selected = _select_all(config, observations)
    diagnostics = _build_diagnostics(
        config,
        selected,
        aggregation=config.aggregation,
        result_weight_multiplier=Decimal("1"),
    )
    context = _build_context(config, observations)
    sensitivity = _build_sensitivity(config, observations, diagnostics)

    indicator_bytes = _indicator_csv(selected)
    diagnostic_bytes = _diagnostic_csv(diagnostics)
    sensitivity_bytes = _sensitivity_csv(sensitivity)
    context_bytes = _context_csv(context)
    output_hashes = {
        "indicators": sha256_hex(indicator_bytes),
        "diagnostics": sha256_hex(diagnostic_bytes),
        "sensitivity": sha256_hex(sensitivity_bytes),
        "context": sha256_hex(context_bytes),
    }
    timestamp = calculated_at or datetime.now(UTC).replace(microsecond=0).isoformat()
    composites = {
        row.entity: row.diagnostic_score
        for row in diagnostics
        if row.level == "composite"
    }
    provenance = {
        "schema_version": config.schema_version,
        "experiment_version": config.version,
        "status": config.status,
        "calculated_at": timestamp,
        "input": {
            "path": source_path.as_posix(),
            "sha256": source_hash,
            "records": len(observations),
            "ingestion_provenance_path": receipt_path.as_posix(),
            "ingestion_provenance_sha256": sha256_hex(receipt_bytes),
            "retrieved_at": receipt.get("retrieved_at"),
        },
        "configuration": {
            "path": Path(config_path).as_posix(),
            "sha256": config.config_sha256,
            "catalog_path": config.catalog_path.as_posix(),
            "catalog_sha256": config.catalog_sha256,
            "methodology_path": config.methodology_path.as_posix(),
            "methodology_sha256": config.methodology_sha256,
            "ingestion_schema_version": config.ingestion_schema_version,
        },
        "countries": list(config.countries),
        "selected_indicators": [
            {
                "entity": row.entity,
                "indicator_id": row.indicator_id,
                "period_start": row.period_start,
                "period_end": row.period_end,
                "raw_value": _decimal_text(row.raw_value),
                "diagnostic_score": _float_text(row.score),
                "bound_status": row.bound_status,
                "bound_reference": row.bound_reference,
                "flags": list(row.flags),
            }
            for row in selected
        ],
        "diagnostic_outcome_composite": {
            entity: _float_text(score) for entity, score in composites.items()
        },
        "publication_gate": {
            "official_iee_score": None,
            "publication_eligible": False,
            "ranking_eligible": False,
            "reasons": [
                "ninguna dimensión tiene un insumo compatible habilitado",
                "faltan roles obligatorios en las cuatro dimensiones",
                (
                    f"la frontera requiere al menos {config.frontier_min_countries} "
                    f"países y hay {len(config.countries)}"
                ),
                "existen límites provisionales y sensibilidad material a ventanas",
            ],
        },
        "outputs": {
            "indicators": {
                "path": Path(indicator_path).as_posix(),
                "records": len(selected),
                "sha256": output_hashes["indicators"],
            },
            "diagnostics": {
                "path": Path(diagnostic_path).as_posix(),
                "records": len(diagnostics),
                "sha256": output_hashes["diagnostics"],
            },
            "sensitivity": {
                "path": Path(sensitivity_path).as_posix(),
                "records": len(sensitivity),
                "sha256": output_hashes["sensitivity"],
            },
            "context": {
                "path": Path(context_path).as_posix(),
                "records": len(context),
                "sha256": output_hashes["context"],
            },
        },
    }
    provenance_bytes = (
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    try:
        _atomic_write_publication(
            (
                (Path(indicator_path), indicator_bytes),
                (Path(diagnostic_path), diagnostic_bytes),
                (Path(sensitivity_path), sensitivity_bytes),
                (Path(context_path), context_bytes),
                (Path(provenance_path), provenance_bytes),
            )
        )
    except IngestionError as error:
        raise ExperimentalScoringError(f"no se pudo publicar el diagnóstico: {error}") from error
    return ExperimentResult(
        indicator_count=len(selected),
        diagnostic_count=len(diagnostics),
        sensitivity_count=len(sensitivity),
        context_count=len(context),
        diagnostic_composite=composites,
        official_iee_score=None,
        publication_eligible=False,
        indicator_path=Path(indicator_path),
        diagnostic_path=Path(diagnostic_path),
        sensitivity_path=Path(sensitivity_path),
        context_path=Path(context_path),
        provenance_path=Path(provenance_path),
        output_sha256=output_hashes,
    )


def _indicator_csv(rows: Sequence[IndicatorDiagnostic]) -> bytes:
    fieldnames = [
        "entity",
        "dimension",
        "indicator_id",
        "role",
        "period_start",
        "period_end",
        "periods",
        "raw_value",
        "transformed_value",
        "diagnostic_score",
        "direction",
        "transform",
        "lower_bound",
        "upper_bound",
        "bound_status",
        "bound_reference",
        "unit",
        "source_id",
        "observation_statuses",
        "flags",
    ]
    records = [
        {
            "entity": row.entity,
            "dimension": row.dimension,
            "indicator_id": row.indicator_id,
            "role": row.role,
            "period_start": row.period_start,
            "period_end": row.period_end,
            "periods": ";".join(str(period) for period in row.periods),
            "raw_value": _decimal_text(row.raw_value),
            "transformed_value": _float_text(row.transformed_value),
            "diagnostic_score": _float_text(row.score),
            "direction": row.direction,
            "transform": row.transform,
            "lower_bound": _decimal_text(row.lower_bound),
            "upper_bound": _decimal_text(row.upper_bound),
            "bound_status": row.bound_status,
            "bound_reference": row.bound_reference,
            "unit": row.unit,
            "source_id": row.source_id,
            "observation_statuses": ";".join(row.observation_statuses),
            "flags": ";".join(row.flags),
        }
        for row in sorted(rows, key=lambda item: (item.entity, item.dimension, item.indicator_id))
    ]
    return _csv_bytes(fieldnames, records)


def _diagnostic_csv(rows: Sequence[DiagnosticRow]) -> bytes:
    fieldnames = [
        "entity",
        "level",
        "component_id",
        "label",
        "diagnostic_score",
        "official_iee_score",
        "coverage",
        "available_roles",
        "missing_roles",
        "input_compatible",
        "frontier_eligible",
        "publication_eligible",
        "flags",
    ]
    records = [
        {
            "entity": row.entity,
            "level": row.level,
            "component_id": row.component_id,
            "label": row.label,
            "diagnostic_score": _float_text(row.diagnostic_score),
            "official_iee_score": "",
            "coverage": _decimal_text(row.coverage),
            "available_roles": ";".join(row.available_roles),
            "missing_roles": ";".join(row.missing_roles),
            "input_compatible": str(row.input_compatible).lower(),
            "frontier_eligible": str(row.frontier_eligible).lower(),
            "publication_eligible": str(row.publication_eligible).lower(),
            "flags": ";".join(row.flags),
        }
        for row in sorted(rows, key=lambda item: (item.entity, item.level, item.component_id))
    ]
    return _csv_bytes(fieldnames, records)


def _sensitivity_csv(rows: Sequence[SensitivityRow]) -> bytes:
    fieldnames = [
        "scenario_id",
        "description",
        "entity",
        "level",
        "component_id",
        "diagnostic_score",
        "base_score",
        "delta_from_base",
        "flags",
    ]
    records = [
        {
            "scenario_id": row.scenario_id,
            "description": row.description,
            "entity": row.entity,
            "level": row.level,
            "component_id": row.component_id,
            "diagnostic_score": _float_text(row.diagnostic_score),
            "base_score": _float_text(row.base_score),
            "delta_from_base": _float_text(row.delta_from_base),
            "flags": ";".join(row.flags),
        }
        for row in rows
    ]
    return _csv_bytes(fieldnames, records)


def _context_csv(rows: Sequence[ContextRow]) -> bytes:
    fieldnames = [
        "entity",
        "dimension",
        "indicator_id",
        "period_start",
        "period_end",
        "value",
        "unit",
        "source_status",
        "observation_statuses",
        "input_compatible",
        "reason",
        "flags",
    ]
    records = [
        {
            "entity": row.entity,
            "dimension": row.dimension,
            "indicator_id": row.indicator_id,
            "period_start": "" if row.period_start is None else row.period_start,
            "period_end": "" if row.period_end is None else row.period_end,
            "value": "" if row.value is None else _decimal_text(row.value),
            "unit": row.unit,
            "source_status": row.source_status,
            "observation_statuses": ";".join(row.observation_statuses),
            "input_compatible": str(row.input_compatible).lower(),
            "reason": row.reason,
            "flags": ";".join(row.flags),
        }
        for row in sorted(rows, key=lambda item: (item.entity, item.dimension))
    ]
    return _csv_bytes(fieldnames, records)


def _csv_bytes(fieldnames: Sequence[str], records: Sequence[Mapping[str, Any]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue().encode("utf-8")


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _float_text(value: float) -> str:
    if not math.isfinite(value):
        raise ExperimentalScoringError(f"resultado no finito: {value}")
    return format(value, ".10f").rstrip("0").rstrip(".")
