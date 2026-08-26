"""Frontera cuantílica experimental v0.3; nunca publica un IEE oficial."""

from __future__ import annotations

import csv
import io
import json
import math
import random
import re
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class ExperimentalFrontierError(RuntimeError):
    """Error controlado de configuración, estimación o publicación."""


@dataclass(frozen=True)
class FrontierRule:
    id: str
    outcome_indicator_id: str
    direction: str
    transform: str
    lower_bound: Decimal
    upper_bound: Decimal
    bound_status: str
    bound_reference: str


@dataclass(frozen=True)
class EstimatorConfig:
    path: Path
    sha256: str
    version: str
    schema_version: str
    status: str
    countries: tuple[str, ...]
    panel_config_path: Path
    panel_config_sha256: str
    diagnostic_config_path: Path
    diagnostic_config_sha256: str
    panel_sha256: str
    gates_sha256: str
    panel_provenance_sha256: str
    frontier_min_countries: int
    result_snapshot_sha256: str
    input_snapshot_sha256: str
    frontier_quantile: float
    sensitivity_quantiles: tuple[float, ...]
    input_transform: str
    require_non_decreasing_frontier: bool
    bootstrap_replications: int
    confidence_level: float
    random_seed: int
    panel_input_indicators: Mapping[str, str]
    dependency_paths: tuple[Path, ...]
    rules: tuple[FrontierRule, ...]


@dataclass(frozen=True)
class PanelObservation:
    entity: str
    dimension: str
    outcome_indicator_id: str
    outcome_value: Decimal | None
    outcome_unit: str
    input_indicator_id: str
    input_value: Decimal | None
    input_unit: str
    sample_member: bool
    flags: tuple[str, ...]


@dataclass(frozen=True)
class PanelGate:
    dimension: str
    complete_pairs: int
    frontier_min_countries: int
    experimental_sample_eligible: bool
    official_frontier_eligible: bool


@dataclass(frozen=True)
class QuantileFit:
    quantile: float
    intercept: float
    slope: float
    pinball_loss: float


@dataclass(frozen=True)
class FrontierEstimate:
    entity: str
    dimension: str
    sample_member: bool
    outcome_value: Decimal | None
    outcome_unit: str
    outcome_score: float | None
    input_value: Decimal | None
    input_unit: str
    transformed_input: float | None
    frontier_score: float | None
    outcome_gap_points: float | None
    experimental_efficiency_score: float | None
    efficiency_ci_lower: float | None
    efficiency_ci_upper: float | None
    official_iee_score: None
    flags: tuple[str, ...]


@dataclass(frozen=True)
class ModelSummary:
    dimension: str
    sample_size: int
    quantile: float
    intercept: float | None
    slope: float | None
    pinball_loss: float | None
    experimental_sample_eligible: bool
    official_frontier_eligible: bool
    official_iee_score: None
    flags: tuple[str, ...]


@dataclass(frozen=True)
class SensitivityEstimate:
    entity: str
    dimension: str
    quantile: float
    frontier_score: float
    experimental_efficiency_score: float
    base_efficiency_score: float
    delta_from_base: float


@dataclass(frozen=True)
class ExperimentalFrontierResult:
    estimate_count: int
    model_count: int
    sensitivity_count: int
    estimates_path: Path
    models_path: Path
    sensitivity_path: Path
    provenance_path: Path
    output_sha256: Mapping[str, str]


_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load_estimator_config(path: str | Path) -> EstimatorConfig:
    """Carga y cruza el estimador con el contrato del panel v0.3."""

    config_path = Path(path)
    config_bytes, raw = _load_toml(config_path, "configuración de frontera")
    try:
        panel_config_path = config_path.parent / str(raw["panel_config"])
        panel_config_bytes, panel_config = _load_toml(panel_config_path, "configuración del panel")
        universe_path = panel_config_path.parent / str(panel_config["country_universe"])
        _, universe = _load_toml(universe_path, "universo de países")
        diagnostic_config_path = config_path.parent / str(raw["diagnostic_config"])
        diagnostic_bytes, diagnostic_config = _load_toml(
            diagnostic_config_path, "configuración diagnóstica"
        )
        result_catalog_path = panel_config_path.parent / str(panel_config["result_catalog"])
        input_catalog_path = panel_config_path.parent / str(panel_config["input_catalog"])
        rules = tuple(_parse_rule(item) for item in raw["dimensions"])
        panel_input_indicators = {
            str(item["id"]): str(item["input_indicator_id"])
            for item in panel_config["dimensions"]
        }
        config = EstimatorConfig(
            path=config_path,
            sha256=sha256_hex(config_bytes),
            version=str(raw["version"]),
            schema_version=str(raw["schema_version"]),
            status=str(raw["status"]),
            countries=tuple(str(value) for value in universe["countries"]),
            panel_config_path=panel_config_path,
            panel_config_sha256=str(raw["panel_config_sha256"]),
            diagnostic_config_path=diagnostic_config_path,
            diagnostic_config_sha256=str(raw["diagnostic_config_sha256"]),
            panel_sha256=str(raw["panel_sha256"]),
            gates_sha256=str(raw["gates_sha256"]),
            panel_provenance_sha256=str(raw["panel_provenance_sha256"]),
            frontier_min_countries=int(panel_config["frontier_min_countries"]),
            result_snapshot_sha256=str(panel_config["result_snapshot_sha256"]),
            input_snapshot_sha256=str(panel_config["input_snapshot_sha256"]),
            frontier_quantile=float(raw["frontier_quantile"]),
            sensitivity_quantiles=tuple(float(value) for value in raw["sensitivity_quantiles"]),
            input_transform=str(raw["input_transform"]),
            require_non_decreasing_frontier=raw["require_non_decreasing_frontier"],
            bootstrap_replications=int(raw["bootstrap_replications"]),
            confidence_level=float(raw["confidence_level"]),
            random_seed=int(raw["random_seed"]),
            panel_input_indicators=panel_input_indicators,
            dependency_paths=(
                panel_config_path,
                diagnostic_config_path,
                universe_path,
                result_catalog_path,
                input_catalog_path,
            ),
            rules=rules,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ExperimentalFrontierError(f"configuración incompleta: {error}") from error
    if sha256_hex(panel_config_bytes) != config.panel_config_sha256:
        raise ExperimentalFrontierError("el hash de la configuración del panel cambió")
    if sha256_hex(diagnostic_bytes) != config.diagnostic_config_sha256:
        raise ExperimentalFrontierError("el hash de la configuración diagnóstica cambió")
    _validate_config(config, panel_config, diagnostic_config)
    return config


def _load_toml(path: Path, label: str) -> tuple[bytes, Mapping[str, Any]]:
    try:
        payload = path.read_bytes()
        return payload, tomllib.load(io.BytesIO(payload))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ExperimentalFrontierError(f"no se pudo leer {label} {path}: {error}") from error


def _parse_rule(raw: Mapping[str, Any]) -> FrontierRule:
    try:
        return FrontierRule(
            id=str(raw["id"]),
            outcome_indicator_id=str(raw["outcome_indicator_id"]),
            direction=str(raw["direction"]),
            transform=str(raw["transform"]),
            lower_bound=_decimal(raw["lower_bound"], "lower_bound"),
            upper_bound=_decimal(raw["upper_bound"], "upper_bound"),
            bound_status=str(raw["bound_status"]),
            bound_reference=str(raw["bound_reference"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ExperimentalFrontierError(f"regla de dimensión incompleta: {error}") from error


def _decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, bool) or value in (None, ""):
        raise ExperimentalFrontierError(f"{label} inválido")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ExperimentalFrontierError(f"{label} inválido") from error
    if not result.is_finite():
        raise ExperimentalFrontierError(f"{label} no finito")
    return result


def _validate_config(
    config: EstimatorConfig,
    panel_config: Mapping[str, Any],
    diagnostic_config: Mapping[str, Any],
) -> None:
    if (
        config.version not in {"0.3", "0.8"}
        or config.schema_version != "iee-experimental-frontier-v1"
        or config.status != "experimental-not-for-publication"
    ):
        raise ExperimentalFrontierError("la frontera debe declarar una versión experimental compatible")
    if not config.countries or len(config.countries) != len(set(config.countries)):
        raise ExperimentalFrontierError("el universo debe contener países únicos")
    for digest in (
        config.panel_config_sha256,
        config.diagnostic_config_sha256,
        config.panel_sha256,
        config.gates_sha256,
        config.panel_provenance_sha256,
        config.result_snapshot_sha256,
        config.input_snapshot_sha256,
    ):
        if not _HEX_SHA256.fullmatch(digest):
            raise ExperimentalFrontierError("hash inválido en la configuración")
    quantiles = (config.frontier_quantile, *config.sensitivity_quantiles)
    if len(set(quantiles)) != len(quantiles) or any(not 0.5 < value < 1.0 for value in quantiles):
        raise ExperimentalFrontierError("cuantiles de frontera inválidos")
    if config.input_transform != "log1p":
        raise ExperimentalFrontierError("v0.3 exige transformación log1p del insumo")
    if not isinstance(config.require_non_decreasing_frontier, bool):
        raise ExperimentalFrontierError("la restricción monotónica debe ser booleana")
    if not config.require_non_decreasing_frontier:
        raise ExperimentalFrontierError("v0.3 exige una frontera no decreciente")
    if not 50 <= config.bootstrap_replications <= 5000:
        raise ExperimentalFrontierError("número de réplicas bootstrap inválido")
    if not 0.5 < config.confidence_level < 1.0:
        raise ExperimentalFrontierError("nivel de confianza inválido")
    rule_ids = [rule.id for rule in config.rules]
    if not rule_ids or len(rule_ids) != len(set(rule_ids)):
        raise ExperimentalFrontierError("las reglas de dimensión deben ser únicas")
    panel_dimensions = {
        str(item["id"]): str(item["outcome_indicator_id"])
        for item in panel_config.get("dimensions", [])
    }
    if set(panel_dimensions) != set(rule_ids):
        raise ExperimentalFrontierError("las dimensiones difieren del panel")
    if set(config.panel_input_indicators) != set(rule_ids):
        raise ExperimentalFrontierError("los insumos difieren del panel")
    canonical_rules = {
        str(item["indicator_id"]): item
        for item in diagnostic_config.get("indicators", [])
    }
    for rule in config.rules:
        if panel_dimensions[rule.id] != rule.outcome_indicator_id:
            raise ExperimentalFrontierError(f"resultado incoherente en {rule.id}")
        if rule.direction not in {"higher", "lower"}:
            raise ExperimentalFrontierError(f"dirección inválida en {rule.id}")
        if rule.transform not in {"linear", "log1p"}:
            raise ExperimentalFrontierError(f"transformación inválida en {rule.id}")
        if rule.upper_bound <= rule.lower_bound:
            raise ExperimentalFrontierError(f"límites inválidos en {rule.id}")
        if not rule.bound_status or not rule.bound_reference:
            raise ExperimentalFrontierError(f"procedencia de límites vacía en {rule.id}")
        canonical = canonical_rules.get(rule.outcome_indicator_id)
        if canonical is None:
            raise ExperimentalFrontierError(f"resultado sin regla diagnóstica en {rule.id}")
        expected = (
            str(canonical["direction"]),
            str(canonical["transform"]),
            _decimal(canonical["lower_bound"], "lower_bound canónico"),
            _decimal(canonical["upper_bound"], "upper_bound canónico"),
            str(canonical["bound_status"]),
            str(canonical["bound_reference"]),
        )
        actual = (
            rule.direction,
            rule.transform,
            rule.lower_bound,
            rule.upper_bound,
            rule.bound_status,
            rule.bound_reference,
        )
        if actual != expected:
            raise ExperimentalFrontierError(f"límites difieren del diagnóstico en {rule.id}")


def fit_monotone_quantile(
    x: Sequence[float], y: Sequence[float], quantile: float
) -> QuantileFit:
    """Resuelve exactamente una regresión cuantílica lineal con pendiente >= 0.

    Con dos parámetros, el óptimo de la pérdida pinball está en una recta que pasa
    por dos observaciones o en la frontera pendiente=0. Enumerar esos vértices evita
    dependencias numéricas y conserva una regla de desempate determinista.
    """

    if len(x) != len(y) or len(x) < 3:
        raise ExperimentalFrontierError("la regresión cuantílica requiere al menos 3 pares")
    if not 0.0 < quantile < 1.0:
        raise ExperimentalFrontierError("cuantil fuera de rango")
    if not all(math.isfinite(value) for value in (*x, *y)):
        raise ExperimentalFrontierError("datos no finitos en la frontera")
    candidates: set[tuple[float, float]] = {(value, 0.0) for value in y}
    for left in range(len(x)):
        for right in range(left + 1, len(x)):
            delta_x = x[right] - x[left]
            if delta_x == 0.0:
                continue
            slope = (y[right] - y[left]) / delta_x
            if slope < 0.0:
                continue
            intercept = y[left] - slope * x[left]
            if math.isfinite(intercept) and math.isfinite(slope):
                candidates.add((intercept, slope))
    if not candidates:
        raise ExperimentalFrontierError("no se pudo construir candidatos de frontera")

    def objective(candidate: tuple[float, float]) -> tuple[float, float, float]:
        intercept, slope = candidate
        residuals = (observed - (intercept + slope * resource) for resource, observed in zip(x, y))
        loss = math.fsum(
            quantile * residual if residual >= 0.0 else (quantile - 1.0) * residual
            for residual in residuals
        )
        return loss, slope, intercept

    intercept, slope = min(candidates, key=objective)
    loss = objective((intercept, slope))[0]
    return QuantileFit(quantile=quantile, intercept=intercept, slope=slope, pinball_loss=loss)


def run_experimental_frontier(
    config_path: str | Path,
    *,
    panel_path: str | Path,
    gates_path: str | Path,
    panel_provenance_path: str | Path,
    estimates_path: str | Path,
    models_path: str | Path,
    sensitivity_path: str | Path,
    provenance_path: str | Path,
    calculated_at: str | None = None,
) -> ExperimentalFrontierResult:
    """Estima fronteras por dimensión y publica resultados experimentales juntos."""

    config = load_estimator_config(config_path)
    _validate_paths(
        config,
        config_path,
        panel_path,
        gates_path,
        panel_provenance_path,
        estimates_path,
        models_path,
        sensitivity_path,
        provenance_path,
    )
    panel_bytes, gates_bytes, receipt_bytes, receipt = _read_inputs(
        config, panel_path, gates_path, panel_provenance_path
    )
    panel = _read_panel(panel_bytes)
    gates = _read_gates(gates_bytes, config.frontier_min_countries)
    if set(gates) != {rule.id for rule in config.rules}:
        raise ExperimentalFrontierError("los gates no cubren las dimensiones configuradas")

    rules = {rule.id: rule for rule in config.rules}
    expected_keys = {
        (entity, dimension) for entity in config.countries for dimension in rules
    }
    actual_keys = {(row.entity, row.dimension) for row in panel}
    if actual_keys != expected_keys:
        raise ExperimentalFrontierError("el panel no contiene exactamente universo × dimensión")
    for row in panel:
        rule = rules[row.dimension]
        if row.outcome_indicator_id != rule.outcome_indicator_id:
            raise ExperimentalFrontierError(f"resultado inesperado en {row.dimension}/{row.entity}")
        if row.input_indicator_id != config.panel_input_indicators[row.dimension]:
            raise ExperimentalFrontierError(f"insumo inesperado en {row.dimension}/{row.entity}")
    estimates: list[FrontierEstimate] = []
    models: list[ModelSummary] = []
    sensitivities: list[SensitivityEstimate] = []
    for dimension in sorted(rules):
        rule = rules[dimension]
        gate = gates[dimension]
        dimension_rows = sorted(
            (row for row in panel if row.dimension == dimension), key=lambda row: row.entity
        )
        sample = [row for row in dimension_rows if row.sample_member]
        if len(sample) != gate.complete_pairs:
            raise ExperimentalFrontierError(f"conteo del gate difiere del panel en {dimension}")
        if not gate.experimental_sample_eligible:
            estimates.extend(_blocked_estimates(dimension_rows, rule, gate))
            models.append(_blocked_model(rule, gate, config.frontier_quantile))
            continue
        x, y = _model_vectors(sample, rule)
        fit = fit_monotone_quantile(x, y, config.frontier_quantile)
        intervals = _bootstrap_intervals(config, dimension, x, y, fit)
        estimates.extend(_estimated_rows(dimension_rows, rule, fit, intervals))
        models.append(
            ModelSummary(
                dimension=dimension,
                sample_size=len(sample),
                quantile=fit.quantile,
                intercept=fit.intercept,
                slope=fit.slope,
                pinball_loss=fit.pinball_loss,
                experimental_sample_eligible=True,
                official_frontier_eligible=False,
                official_iee_score=None,
                flags=tuple(sorted(_fit_flags(rule, fit))),
            )
        )
        sensitivities.extend(_sensitivity_rows(config, dimension, sample, rule, fit))

    estimate_bytes = _estimates_csv(estimates)
    model_bytes = _models_csv(models)
    sensitivity_bytes = _sensitivity_csv(sensitivities)
    output_hashes = {
        "estimates": sha256_hex(estimate_bytes),
        "models": sha256_hex(model_bytes),
        "sensitivity": sha256_hex(sensitivity_bytes),
    }
    timestamp = calculated_at or datetime.now(UTC).replace(microsecond=0).isoformat()
    provenance = {
        "schema_version": config.schema_version,
        "version": config.version,
        "status": config.status,
        "calculated_at": timestamp,
        "inputs": {
            "panel": {"path": Path(panel_path).as_posix(), "sha256": sha256_hex(panel_bytes)},
            "gates": {"path": Path(gates_path).as_posix(), "sha256": sha256_hex(gates_bytes)},
            "panel_provenance": {
                "path": Path(panel_provenance_path).as_posix(),
                "sha256": sha256_hex(receipt_bytes),
            },
        },
        "configuration": {
            "path": Path(config_path).as_posix(),
            "sha256": config.sha256,
            "panel_config_path": config.panel_config_path.as_posix(),
            "panel_config_sha256": config.panel_config_sha256,
            "diagnostic_config_path": config.diagnostic_config_path.as_posix(),
            "diagnostic_config_sha256": config.diagnostic_config_sha256,
            "frontier_min_countries": config.frontier_min_countries,
        },
        "method": {
            "family": "monotone-linear-quantile-regression",
            "input_transform": config.input_transform,
            "frontier_quantile": config.frontier_quantile,
            "sensitivity_quantiles": list(config.sensitivity_quantiles),
            "bootstrap_replications": config.bootstrap_replications,
            "confidence_level": config.confidence_level,
            "random_seed": config.random_seed,
            "quantile_noncrossing": "anchored-to-base-quantile",
        },
        "dimension_models": [
            {
                "dimension": row.dimension,
                "sample_size": row.sample_size,
                "experimental_sample_eligible": row.experimental_sample_eligible,
                "official_frontier_eligible": False,
                "intercept": _optional_float(row.intercept),
                "slope": _optional_float(row.slope),
                "flags": list(row.flags),
            }
            for row in models
        ],
        "publication_gate": {
            "official_iee_score": None,
            "publication_eligible": False,
            "ranking_eligible": False,
            "reasons": [
                "los insumos permanecen conditional",
                "el modelo aún no incorpora controles estructurales",
                "faltan roles obligatorios e incertidumbre metodológica externa",
                "seguridad y administración no alcanzan una muestra estimable",
            ],
        },
        "outputs": {
            "estimates": {
                "path": Path(estimates_path).as_posix(),
                "records": len(estimates),
                "sha256": output_hashes["estimates"],
            },
            "models": {
                "path": Path(models_path).as_posix(),
                "records": len(models),
                "sha256": output_hashes["models"],
            },
            "sensitivity": {
                "path": Path(sensitivity_path).as_posix(),
                "records": len(sensitivities),
                "sha256": output_hashes["sensitivity"],
            },
        },
        "upstream_status": receipt.get("status"),
    }
    provenance_bytes = (
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    try:
        _atomic_write_publication(
            (
                (Path(estimates_path), estimate_bytes),
                (Path(models_path), model_bytes),
                (Path(sensitivity_path), sensitivity_bytes),
                (Path(provenance_path), provenance_bytes),
            )
        )
    except IngestionError as error:
        raise ExperimentalFrontierError(f"no se pudo publicar la frontera: {error}") from error
    return ExperimentalFrontierResult(
        estimate_count=len(estimates),
        model_count=len(models),
        sensitivity_count=len(sensitivities),
        estimates_path=Path(estimates_path),
        models_path=Path(models_path),
        sensitivity_path=Path(sensitivity_path),
        provenance_path=Path(provenance_path),
        output_sha256=output_hashes,
    )


def _read_inputs(
    config: EstimatorConfig,
    panel_path: str | Path,
    gates_path: str | Path,
    provenance_path: str | Path,
) -> tuple[bytes, bytes, bytes, Mapping[str, Any]]:
    try:
        panel = Path(panel_path).read_bytes()
        gates = Path(gates_path).read_bytes()
        receipt_bytes = Path(provenance_path).read_bytes()
        receipt = json.loads(receipt_bytes.decode("utf-8"))
        if sha256_hex(panel) != config.panel_sha256:
            raise ExperimentalFrontierError("el panel difiere de la configuración")
        if sha256_hex(gates) != config.gates_sha256:
            raise ExperimentalFrontierError("los gates difieren de la configuración")
        if sha256_hex(receipt_bytes) != config.panel_provenance_sha256:
            raise ExperimentalFrontierError("la procedencia del panel difiere de la configuración")
        if receipt["schema_version"] != "iee-frontier-panel-v1":
            raise ExperimentalFrontierError("esquema del panel no compatible")
        if receipt["version"] != config.version:
            raise ExperimentalFrontierError("versión de procedencia del panel no compatible")
        if receipt["status"] != "experimental-not-for-publication":
            raise ExperimentalFrontierError("estado de procedencia del panel no compatible")
        if receipt["outputs"]["panel"]["sha256"] != config.panel_sha256:
            raise ExperimentalFrontierError("hash del panel difiere de su recibo")
        if receipt["outputs"]["gates"]["sha256"] != config.gates_sha256:
            raise ExperimentalFrontierError("hash de gates difiere de su recibo")
        if receipt["configuration"]["sha256"] != config.panel_config_sha256:
            raise ExperimentalFrontierError("configuración del panel difiere de su recibo")
        if (
            receipt["configuration"]["frontier_min_countries"]
            != config.frontier_min_countries
        ):
            raise ExperimentalFrontierError("mínimo muestral difiere de la configuración")
        if (
            receipt["inputs"]["results"]["observations_sha256"]
            != config.result_snapshot_sha256
        ):
            raise ExperimentalFrontierError("snapshot de resultados difiere de su recibo")
        if (
            receipt["inputs"]["inputs"]["observations_sha256"]
            != config.input_snapshot_sha256
        ):
            raise ExperimentalFrontierError("snapshot de insumos difiere de su recibo")
        publication = receipt["publication_gate"]
        if (
            publication["official_iee_score"] is not None
            or publication["publication_eligible"] is not False
            or publication["ranking_eligible"] is not False
        ):
            raise ExperimentalFrontierError("el panel upstream abrió un gate de publicación")
        if tuple(receipt["countries"]) != config.countries:
            raise ExperimentalFrontierError("universo del panel difiere de la configuración")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise ExperimentalFrontierError(f"no se pudieron validar las entradas: {error}") from error
    return panel, gates, receipt_bytes, receipt


def _read_panel(payload: bytes) -> list[PanelObservation]:
    required = {
        "entity", "dimension", "outcome_indicator_id", "outcome_value", "outcome_unit",
        "input_indicator_id", "input_value", "input_unit", "sample_member", "flags",
    }
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    if not reader.fieldnames or not required <= set(reader.fieldnames):
        raise ExperimentalFrontierError("esquema del panel incompleto")
    rows: list[PanelObservation] = []
    keys: set[tuple[str, str]] = set()
    for raw in reader:
        key = (raw["entity"], raw["dimension"])
        if key in keys:
            raise ExperimentalFrontierError(f"fila duplicada en el panel: {key}")
        keys.add(key)
        member = _boolean(raw["sample_member"], "sample_member")
        outcome = _optional_decimal(raw["outcome_value"], "outcome_value")
        resource = _optional_decimal(raw["input_value"], "input_value")
        if member and (outcome is None or resource is None):
            raise ExperimentalFrontierError(f"miembro sin par completo: {key}")
        rows.append(
            PanelObservation(
                entity=raw["entity"], dimension=raw["dimension"],
                outcome_indicator_id=raw["outcome_indicator_id"], outcome_value=outcome,
                outcome_unit=raw["outcome_unit"], input_indicator_id=raw["input_indicator_id"],
                input_value=resource, input_unit=raw["input_unit"], sample_member=member,
                flags=tuple(filter(None, raw["flags"].split(";"))),
            )
        )
    if not rows:
        raise ExperimentalFrontierError("panel vacío")
    return rows


def _read_gates(payload: bytes, expected_minimum: int) -> Mapping[str, PanelGate]:
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    required = {
        "dimension", "complete_pairs", "frontier_min_countries",
        "experimental_sample_eligible", "official_frontier_eligible",
    }
    if not reader.fieldnames or not required <= set(reader.fieldnames):
        raise ExperimentalFrontierError("esquema de gates incompleto")
    gates: dict[str, PanelGate] = {}
    for raw in reader:
        dimension = raw["dimension"]
        if dimension in gates:
            raise ExperimentalFrontierError(f"gate duplicado: {dimension}")
        gate = PanelGate(
            dimension=dimension,
            complete_pairs=int(raw["complete_pairs"]),
            frontier_min_countries=int(raw["frontier_min_countries"]),
            experimental_sample_eligible=_boolean(raw["experimental_sample_eligible"], "gate"),
            official_frontier_eligible=_boolean(raw["official_frontier_eligible"], "gate oficial"),
        )
        if gate.official_frontier_eligible:
            raise ExperimentalFrontierError("un gate oficial no puede estar abierto en v0.3")
        if gate.frontier_min_countries != expected_minimum:
            raise ExperimentalFrontierError(f"mínimo muestral inesperado: {dimension}")
        if gate.experimental_sample_eligible != (
            gate.complete_pairs >= gate.frontier_min_countries
        ):
            raise ExperimentalFrontierError(f"gate inconsistente: {dimension}")
        gates[dimension] = gate
    return gates


def _boolean(value: str, label: str) -> bool:
    if value not in {"true", "false"}:
        raise ExperimentalFrontierError(f"{label} debe ser booleano")
    return value == "true"


def _optional_decimal(value: str, label: str) -> Decimal | None:
    return None if value == "" else _decimal(value, label)


def _normalize(value: Decimal, rule: FrontierRule) -> tuple[float, tuple[str, ...]]:
    clipped = min(max(value, rule.lower_bound), rule.upper_bound)
    raw = float(value)
    lower = float(rule.lower_bound)
    upper = float(rule.upper_bound)
    normalized_value = float(clipped)
    if rule.transform == "log1p":
        if rule.lower_bound <= -1 or value <= -1:
            raise ExperimentalFrontierError(f"log1p fuera de dominio en {rule.id}")
        normalized_value = math.log1p(normalized_value)
        lower = math.log1p(lower)
        upper = math.log1p(upper)
    if not all(math.isfinite(item) for item in (raw, normalized_value, lower, upper)):
        raise ExperimentalFrontierError(f"normalización no finita en {rule.id}")
    score = 100.0 * (normalized_value - lower) / (upper - lower)
    if rule.direction == "lower":
        score = 100.0 - score
    flags: set[str] = set()
    if value < rule.lower_bound:
        flags.add("outcome_clipped_lower")
    if value > rule.upper_bound:
        flags.add("outcome_clipped_upper")
    return score, tuple(sorted(flags))


def _model_vectors(
    sample: Sequence[PanelObservation], rule: FrontierRule
) -> tuple[list[float], list[float]]:
    x: list[float] = []
    y: list[float] = []
    for row in sample:
        assert row.input_value is not None and row.outcome_value is not None
        resource = float(row.input_value)
        if resource < 0.0:
            raise ExperimentalFrontierError(f"insumo negativo en {rule.id}/{row.entity}")
        x.append(math.log1p(resource))
        y.append(_normalize(row.outcome_value, rule)[0])
    return x, y


def _predict(fit: QuantileFit, x: float) -> float:
    return min(100.0, max(0.0, fit.intercept + fit.slope * x))


def _efficiency(observed: float, frontier: float) -> tuple[float, float]:
    gap = max(0.0, frontier - observed)
    if frontier <= 0.0:
        return (100.0 if observed >= frontier else 0.0), gap
    return min(100.0, max(0.0, 100.0 * observed / frontier)), gap


def _bootstrap_intervals(
    config: EstimatorConfig,
    dimension: str,
    x: Sequence[float],
    y: Sequence[float],
    base_fit: QuantileFit,
) -> list[tuple[float, float]]:
    seed = config.random_seed + sum((index + 1) * ord(char) for index, char in enumerate(dimension))
    generator = random.Random(seed)
    values: list[list[float]] = [[] for _ in x]
    indices = tuple(range(len(x)))
    for _ in range(config.bootstrap_replications):
        sample_indices = generator.choices(indices, k=len(indices))
        fit = fit_monotone_quantile(
            [x[index] for index in sample_indices],
            [y[index] for index in sample_indices],
            base_fit.quantile,
        )
        for position, resource in enumerate(x):
            values[position].append(_efficiency(y[position], _predict(fit, resource))[0])
    tail = (1.0 - config.confidence_level) / 2.0
    return [(_percentile(row, tail), _percentile(row, 1.0 - tail)) for row in values]


def _percentile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _estimated_rows(
    rows: Sequence[PanelObservation],
    rule: FrontierRule,
    fit: QuantileFit,
    intervals: Sequence[tuple[float, float]],
) -> list[FrontierEstimate]:
    interval_by_entity = {
        row.entity: interval
        for row, interval in zip((item for item in rows if item.sample_member), intervals)
    }
    results: list[FrontierEstimate] = []
    for row in rows:
        outcome_score = None
        transformed = None
        frontier = None
        efficiency = None
        gap = None
        lower_ci = None
        upper_ci = None
        flags = set(row.flags) | _fit_flags(rule, fit)
        if row.outcome_value is not None:
            outcome_score, clipping = _normalize(row.outcome_value, rule)
            flags.update(clipping)
        if row.sample_member:
            assert row.input_value is not None and outcome_score is not None
            transformed = math.log1p(float(row.input_value))
            frontier = _predict(fit, transformed)
            efficiency, gap = _efficiency(outcome_score, frontier)
            lower_ci, upper_ci = interval_by_entity[row.entity]
            if outcome_score > frontier:
                flags.add("observed_above_q90_frontier")
        else:
            flags.add("not_in_estimation_sample")
        results.append(
            FrontierEstimate(
                entity=row.entity, dimension=row.dimension, sample_member=row.sample_member,
                outcome_value=row.outcome_value, outcome_unit=row.outcome_unit,
                outcome_score=outcome_score, input_value=row.input_value, input_unit=row.input_unit,
                transformed_input=transformed, frontier_score=frontier, outcome_gap_points=gap,
                experimental_efficiency_score=efficiency, efficiency_ci_lower=lower_ci,
                efficiency_ci_upper=upper_ci, official_iee_score=None, flags=tuple(sorted(flags)),
            )
        )
    return results


def _blocked_estimates(
    rows: Sequence[PanelObservation], rule: FrontierRule, gate: PanelGate
) -> list[FrontierEstimate]:
    results: list[FrontierEstimate] = []
    for row in rows:
        outcome_score = None
        flags = set(row.flags) | _model_flags(rule) | {
            "frontier_not_estimated", f"sample_below_frontier_min:{gate.frontier_min_countries}"
        }
        if row.outcome_value is not None:
            outcome_score, clipping = _normalize(row.outcome_value, rule)
            flags.update(clipping)
        results.append(
            FrontierEstimate(
                entity=row.entity, dimension=row.dimension, sample_member=row.sample_member,
                outcome_value=row.outcome_value, outcome_unit=row.outcome_unit,
                outcome_score=outcome_score, input_value=row.input_value, input_unit=row.input_unit,
                transformed_input=None, frontier_score=None, outcome_gap_points=None,
                experimental_efficiency_score=None, efficiency_ci_lower=None,
                efficiency_ci_upper=None, official_iee_score=None, flags=tuple(sorted(flags)),
            )
        )
    return results


def _blocked_model(
    rule: FrontierRule, gate: PanelGate, quantile: float
) -> ModelSummary:
    return ModelSummary(
        dimension=rule.id, sample_size=gate.complete_pairs, quantile=quantile,
        intercept=None, slope=None, pinball_loss=None, experimental_sample_eligible=False,
        official_frontier_eligible=False, official_iee_score=None,
        flags=tuple(sorted(_model_flags(rule) | {"frontier_not_estimated"})),
    )


def _model_flags(rule: FrontierRule) -> set[str]:
    flags = {
        "experimental_only", "not_official_iee", "resource_only_frontier",
        "input_conditional", "ranking_blocked", "official_iee_null",
    }
    if rule.bound_status == "provisional":
        flags.add("bounds_provisional")
    return flags


def _fit_flags(rule: FrontierRule, fit: QuantileFit) -> set[str]:
    flags = _model_flags(rule)
    if abs(fit.slope) <= 1e-12:
        flags.add("flat_frontier")
    return flags


def _sensitivity_rows(
    config: EstimatorConfig,
    dimension: str,
    sample: Sequence[PanelObservation],
    rule: FrontierRule,
    base_fit: QuantileFit,
) -> list[SensitivityEstimate]:
    x, y = _model_vectors(sample, rule)
    base = {
        row.entity: _efficiency(observed, _predict(base_fit, resource))[0]
        for row, resource, observed in zip(sample, x, y)
    }
    quantiles = (config.frontier_quantile, *config.sensitivity_quantiles)
    fits = {
        quantile: (
            base_fit
            if quantile == config.frontier_quantile
            else fit_monotone_quantile(x, y, quantile)
        )
        for quantile in quantiles
    }
    results: list[SensitivityEstimate] = []
    for row, resource, observed in zip(sample, x, y):
        raw_frontiers = {
            quantile: _predict(fit, resource) for quantile, fit in fits.items()
        }
        frontiers = _anchor_noncrossing(
            raw_frontiers, base_quantile=config.frontier_quantile
        )
        for quantile in quantiles:
            frontier = frontiers[quantile]
            efficiency = _efficiency(observed, frontier)[0]
            results.append(
                SensitivityEstimate(
                    entity=row.entity, dimension=dimension, quantile=quantile,
                    frontier_score=frontier, experimental_efficiency_score=efficiency,
                    base_efficiency_score=base[row.entity],
                    delta_from_base=efficiency - base[row.entity],
                )
            )
    return results


def _anchor_noncrossing(
    frontiers: Mapping[float, float], *, base_quantile: float
) -> Mapping[float, float]:
    """Ordena sensibilidades por cuantíl sin modificar la frontera base."""

    if base_quantile not in frontiers:
        raise ExperimentalFrontierError("falta el cuantíl base para anclar sensibilidades")
    adjusted = {base_quantile: frontiers[base_quantile]}
    ceiling = frontiers[base_quantile]
    for quantile in sorted((value for value in frontiers if value < base_quantile), reverse=True):
        ceiling = min(frontiers[quantile], ceiling)
        adjusted[quantile] = ceiling
    floor = frontiers[base_quantile]
    for quantile in sorted(value for value in frontiers if value > base_quantile):
        floor = max(frontiers[quantile], floor)
        adjusted[quantile] = floor
    return adjusted


def _validate_paths(config: EstimatorConfig, *paths: str | Path) -> None:
    config_path, panel, gates, receipt, *outputs = paths
    inputs = {
        Path(config_path).resolve(),
        *(path.resolve() for path in config.dependency_paths),
        Path(panel).resolve(), Path(gates).resolve(), Path(receipt).resolve(),
    }
    resolved_outputs = [Path(path).resolve() for path in outputs]
    if len(resolved_outputs) != len(set(resolved_outputs)):
        raise ExperimentalFrontierError("las rutas de salida deben ser únicas")
    if set(resolved_outputs) & inputs:
        raise ExperimentalFrontierError("una salida no puede sobrescribir una entrada")


def _optional_float(value: float | None) -> str | None:
    return None if value is None else format(value, ".12g")


def _csv_text(value: float | None) -> str:
    return "" if value is None else format(value, ".12g")


def _estimates_csv(rows: Sequence[FrontierEstimate]) -> bytes:
    fields = [
        "entity", "dimension", "sample_member", "outcome_value", "outcome_unit", "outcome_score",
        "input_value", "input_unit", "transformed_input", "frontier_score", "outcome_gap_points",
        "experimental_efficiency_score", "efficiency_ci_lower", "efficiency_ci_upper",
        "official_iee_score", "flags",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in sorted(rows, key=lambda item: (item.dimension, item.entity)):
        writer.writerow({
            "entity": row.entity,
            "dimension": row.dimension,
            "sample_member": str(row.sample_member).lower(),
            "outcome_value": "" if row.outcome_value is None else str(row.outcome_value),
            "outcome_unit": row.outcome_unit,
            "outcome_score": _csv_text(row.outcome_score),
            "input_value": "" if row.input_value is None else str(row.input_value),
            "input_unit": row.input_unit,
            "transformed_input": _csv_text(row.transformed_input),
            "frontier_score": _csv_text(row.frontier_score),
            "outcome_gap_points": _csv_text(row.outcome_gap_points),
            "experimental_efficiency_score": _csv_text(row.experimental_efficiency_score),
            "efficiency_ci_lower": _csv_text(row.efficiency_ci_lower),
            "efficiency_ci_upper": _csv_text(row.efficiency_ci_upper),
            "official_iee_score": "",
            "flags": ";".join(row.flags),
        })
    return output.getvalue().encode("utf-8")


def _models_csv(rows: Sequence[ModelSummary]) -> bytes:
    fields = [
        "dimension", "sample_size", "quantile", "intercept", "slope", "pinball_loss",
        "experimental_sample_eligible", "official_frontier_eligible", "official_iee_score", "flags",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in sorted(rows, key=lambda item: item.dimension):
        writer.writerow({
            "dimension": row.dimension,
            "sample_size": row.sample_size,
            "quantile": _csv_text(row.quantile),
            "intercept": _csv_text(row.intercept),
            "slope": _csv_text(row.slope),
            "pinball_loss": _csv_text(row.pinball_loss),
            "experimental_sample_eligible": str(row.experimental_sample_eligible).lower(),
            "official_frontier_eligible": "false",
            "official_iee_score": "",
            "flags": ";".join(row.flags),
        })
    return output.getvalue().encode("utf-8")


def _sensitivity_csv(rows: Sequence[SensitivityEstimate]) -> bytes:
    fields = [
        "entity", "dimension", "quantile", "frontier_score", "experimental_efficiency_score",
        "base_efficiency_score", "delta_from_base",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in sorted(rows, key=lambda item: (item.dimension, item.quantile, item.entity)):
        writer.writerow({
            "entity": row.entity, "dimension": row.dimension, "quantile": _csv_text(row.quantile),
            "frontier_score": _csv_text(row.frontier_score),
            "experimental_efficiency_score": _csv_text(row.experimental_efficiency_score),
            "base_efficiency_score": _csv_text(row.base_efficiency_score),
            "delta_from_base": _csv_text(row.delta_from_base),
        })
    return output.getvalue().encode("utf-8")
