"""Sensibilidades de contexto para la frontera experimental; nunca publican un IEE."""

from __future__ import annotations

import csv
import io
import json
import math
import re
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .experimental_frontier import (
    EstimatorConfig,
    ExperimentalFrontierError,
    PanelObservation,
    _efficiency,
    _model_vectors,
    _predict,
    _read_gates,
    _read_inputs,
    _read_panel,
    fit_monotone_quantile,
    load_estimator_config,
)
from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class ContextSensitivityError(RuntimeError):
    """Error controlado de contrato, ajuste o publicación de sensibilidad."""


@dataclass(frozen=True)
class ContextControl:
    indicator_id: str
    transform: str
    source_id: str
    series_code: str
    unit: str


@dataclass(frozen=True)
class ContextSensitivityConfig:
    path: Path
    sha256: str
    version: str
    schema_version: str
    status: str
    frontier_config_path: Path
    frontier_config_sha256: str
    context_catalog_path: Path
    context_catalog_sha256: str
    context_manifest_path: Path
    context_manifest_sha256: str
    context_observations_sha256: str
    context_provenance_sha256: str
    context_start_year: int
    context_end_year: int
    frontier_quantile: float
    minimum_sample: int
    uncertainty: str
    controls: tuple[ContextControl, ...]
    dimensions: tuple[str, ...]


@dataclass(frozen=True)
class ConditionalQuantileFit:
    quantile: float
    intercept: float
    resource_slope: float
    context_slope: float
    pinball_loss: float


@dataclass(frozen=True)
class ContextSensitivityRow:
    entity: str
    dimension: str
    control_indicator_id: str
    control_value: Decimal
    control_unit: str
    control_transform: str
    transformed_control: float
    sample_size: int
    baseline_frontier_score: float
    conditional_frontier_score: float
    base_efficiency_score: float
    conditional_efficiency_score: float
    delta_from_base: float
    official_iee_score: None
    flags: tuple[str, ...]


@dataclass(frozen=True)
class ContextModelRow:
    dimension: str
    control_indicator_id: str
    sample_size: int
    quantile: float
    intercept: float
    resource_slope: float
    context_slope: float
    pinball_loss: float
    official_iee_score: None
    flags: tuple[str, ...]


@dataclass(frozen=True)
class ContextSensitivityResult:
    row_count: int
    model_count: int
    rows_path: Path
    models_path: Path
    provenance_path: Path
    output_sha256: Mapping[str, str]


_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load_context_sensitivity_config(path: str | Path) -> ContextSensitivityConfig:
    """Carga el contrato v0.4 y lo contrasta con sus catálogos congelados."""

    config_path = Path(path)
    config_bytes, raw = _load_toml(config_path, "configuración de sensibilidad")
    try:
        frontier_path = config_path.parent / str(raw["frontier_config"])
        catalog_path = config_path.parent / str(raw["context_catalog"])
        manifest_path = config_path.parent / str(raw["context_manifest"])
        frontier_bytes = frontier_path.read_bytes()
        catalog_bytes, catalog = _load_toml(catalog_path, "catálogo de contexto")
        manifest_bytes, manifest = _load_toml(manifest_path, "manifiesto de contexto")
        controls = tuple(_parse_control(item, catalog) for item in raw["controls"])
        config = ContextSensitivityConfig(
            path=config_path,
            sha256=sha256_hex(config_bytes),
            version=str(raw["version"]),
            schema_version=str(raw["schema_version"]),
            status=str(raw["status"]),
            frontier_config_path=frontier_path,
            frontier_config_sha256=str(raw["frontier_config_sha256"]),
            context_catalog_path=catalog_path,
            context_catalog_sha256=str(raw["context_catalog_sha256"]),
            context_manifest_path=manifest_path,
            context_manifest_sha256=str(raw["context_manifest_sha256"]),
            context_observations_sha256=str(raw["context_observations_sha256"]),
            context_provenance_sha256=str(raw["context_provenance_sha256"]),
            context_start_year=int(raw["context_start_year"]),
            context_end_year=int(raw["context_end_year"]),
            frontier_quantile=float(raw["frontier_quantile"]),
            minimum_sample=int(raw["minimum_sample"]),
            uncertainty=str(raw["uncertainty"]),
            controls=controls,
            dimensions=tuple(str(item["id"]) for item in raw["dimensions"]),
        )
    except (KeyError, OSError, TypeError, ValueError) as error:
        raise ContextSensitivityError(
            f"configuración de sensibilidad incompleta: {error}"
        ) from error
    if sha256_hex(frontier_bytes) != config.frontier_config_sha256:
        raise ContextSensitivityError("el hash de configuración de frontera cambió")
    if sha256_hex(catalog_bytes) != config.context_catalog_sha256:
        raise ContextSensitivityError("el hash del catálogo de contexto cambió")
    if sha256_hex(manifest_bytes) != config.context_manifest_sha256:
        raise ContextSensitivityError("el hash del manifiesto de contexto cambió")
    _validate_config(config, catalog, manifest)
    return config


def _load_toml(path: Path, label: str) -> tuple[bytes, Mapping[str, Any]]:
    try:
        payload = path.read_bytes()
        return payload, tomllib.load(io.BytesIO(payload))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ContextSensitivityError(f"no se pudo leer {label} {path}: {error}") from error


def _parse_control(raw: Mapping[str, Any], catalog: Mapping[str, Any]) -> ContextControl:
    try:
        indicator_id = str(raw["indicator_id"])
        transform = str(raw["transform"])
        entries = {str(item["indicator_id"]): item for item in catalog["series"]}
        entry = entries[indicator_id]
        return ContextControl(
            indicator_id=indicator_id,
            transform=transform,
            source_id=str(entry["source_id"]),
            series_code=str(entry["official_code"]),
            unit=str(entry["unit"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ContextSensitivityError(f"control de contexto incompleto: {error}") from error


def _validate_config(
    config: ContextSensitivityConfig,
    catalog: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> None:
    if (
        config.version != "0.4"
        or config.schema_version != "iee-experimental-context-sensitivity-v1"
        or config.status != "experimental-not-for-publication"
    ):
        raise ContextSensitivityError("la sensibilidad de contexto debe ser v0.4 experimental")
    for digest in (
        config.frontier_config_sha256,
        config.context_catalog_sha256,
        config.context_manifest_sha256,
        config.context_observations_sha256,
        config.context_provenance_sha256,
    ):
        if not _HEX_SHA256.fullmatch(digest):
            raise ContextSensitivityError("hash inválido en la configuración de contexto")
    if config.context_end_year < config.context_start_year:
        raise ContextSensitivityError("ventana de contexto inválida")
    if not 0.5 < config.frontier_quantile < 1.0:
        raise ContextSensitivityError("cuantil de contexto inválido")
    if config.minimum_sample < 3:
        raise ContextSensitivityError("muestra mínima de contexto inválida")
    if config.uncertainty != "not-estimated-for-context-sensitivity":
        raise ContextSensitivityError("la incertidumbre de contexto debe permanecer explícita")
    control_ids = [control.indicator_id for control in config.controls]
    if not control_ids or len(control_ids) != len(set(control_ids)):
        raise ContextSensitivityError("los controles de contexto deben ser únicos")
    dimensions = list(config.dimensions)
    if not dimensions or len(dimensions) != len(set(dimensions)):
        raise ContextSensitivityError("las dimensiones de contexto deben ser únicas")
    catalog_entries = {
        str(item["indicator_id"]): item for item in catalog.get("series", [])
    }
    if set(catalog_entries) != set(control_ids):
        raise ContextSensitivityError(
            "el contrato debe cubrir exactamente el catálogo de contexto"
        )
    manifest_entries = {
        str(item["indicator_id"]): item for item in manifest.get("series", [])
    }
    if set(manifest_entries) != set(control_ids):
        raise ContextSensitivityError(
            "el manifiesto debe cubrir exactamente el catálogo de contexto"
        )
    if str(manifest.get("version")) != config.version:
        raise ContextSensitivityError("la versión del manifiesto de contexto difiere")
    for control in config.controls:
        entry = catalog_entries[control.indicator_id]
        spec = manifest_entries[control.indicator_id]
        if entry.get("role") != "contexto" or entry.get("direction") != "input":
            raise ContextSensitivityError(f"rol inválido para {control.indicator_id}")
        if entry.get("status") != "validated" or spec.get("source_status") != "validated":
            raise ContextSensitivityError(f"estado inválido para {control.indicator_id}")
        if entry.get("transform") != control.transform:
            raise ContextSensitivityError(
                f"transformación canónica distinta en {control.indicator_id}"
            )
        if control.transform not in {"linear", "log1p"}:
            raise ContextSensitivityError(f"transformación no permitida en {control.indicator_id}")
        if spec.get("score_eligible") is not False or spec.get("direction") != "input":
            raise ContextSensitivityError(f"el contexto no puede puntuar: {control.indicator_id}")
        if spec.get("url") != entry.get("exact_url"):
            raise ContextSensitivityError(f"URL de contexto distinta en {control.indicator_id}")


def fit_conditional_monotone_quantile(
    resources: Sequence[float],
    contexts: Sequence[float],
    outcomes: Sequence[float],
    quantile: float,
) -> ConditionalQuantileFit:
    """Ajusta p90 con un control y pendiente de recursos no negativa.

    La pérdida pinball es lineal por tramos. Para tres parámetros se enumeran los
    vértices definidos por tres residuos nulos y los de la frontera de pendiente
    cero definidos por dos residuos nulos. El algoritmo no requiere dependencias
    estadísticas externas y usa desempate determinista.
    """

    if len(resources) != len(contexts) or len(resources) != len(outcomes) or len(resources) < 4:
        raise ContextSensitivityError("la frontera condicionada requiere al menos 4 pares")
    if not 0.0 < quantile < 1.0:
        raise ContextSensitivityError("cuantil condicionado fuera de rango")
    if not all(math.isfinite(value) for value in (*resources, *contexts, *outcomes)):
        raise ContextSensitivityError("datos no finitos en la frontera condicionada")

    candidates: set[tuple[float, float, float]] = set()
    has_full_rank = False
    for first in range(len(resources)):
        for second in range(first + 1, len(resources)):
            for third in range(second + 1, len(resources)):
                candidate = _solve_three_equations(
                    (resources[first], contexts[first], outcomes[first]),
                    (resources[second], contexts[second], outcomes[second]),
                    (resources[third], contexts[third], outcomes[third]),
                )
                if candidate is not None:
                    has_full_rank = True
                if candidate is not None and candidate[1] >= -1e-10:
                    intercept, resource_slope, context_slope = candidate
                    candidates.add((intercept, max(0.0, resource_slope), context_slope))
    for first in range(len(resources)):
        for second in range(first + 1, len(resources)):
            delta_context = contexts[second] - contexts[first]
            if delta_context == 0.0:
                continue
            context_slope = (outcomes[second] - outcomes[first]) / delta_context
            intercept = outcomes[first] - context_slope * contexts[first]
            if math.isfinite(intercept) and math.isfinite(context_slope):
                candidates.add((intercept, 0.0, context_slope))
    if not has_full_rank:
        raise ContextSensitivityError("recursos y contexto son colineales")
    if not candidates:
        raise ContextSensitivityError("recursos y contexto no permiten una frontera identificable")

    def objective(candidate: tuple[float, float, float]) -> tuple[float, float, float, float]:
        intercept, resource_slope, context_slope = candidate
        residuals = (
            observed - (intercept + resource_slope * resource + context_slope * context)
            for resource, context, observed in zip(resources, contexts, outcomes)
        )
        loss = math.fsum(
            quantile * residual if residual >= 0.0 else (quantile - 1.0) * residual
            for residual in residuals
        )
        return loss, resource_slope, context_slope, intercept

    intercept, resource_slope, context_slope = min(candidates, key=objective)
    loss = objective((intercept, resource_slope, context_slope))[0]
    return ConditionalQuantileFit(
        quantile=quantile,
        intercept=intercept,
        resource_slope=resource_slope,
        context_slope=context_slope,
        pinball_loss=loss,
    )


def _solve_three_equations(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
    third: tuple[float, float, float],
) -> tuple[float, float, float] | None:
    matrix = [
        [1.0, first[0], first[1], first[2]],
        [1.0, second[0], second[1], second[2]],
        [1.0, third[0], third[1], third[2]],
    ]
    for column in range(3):
        pivot = max(range(column, 3), key=lambda row: abs(matrix[row][column]))
        if abs(matrix[pivot][column]) <= 1e-12:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        divisor = matrix[column][column]
        matrix[column] = [value / divisor for value in matrix[column]]
        for row in range(3):
            if row == column:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[column])
            ]
    solution = tuple(matrix[row][3] for row in range(3))
    return solution if all(math.isfinite(value) for value in solution) else None


def run_context_sensitivity(
    config_path: str | Path,
    *,
    panel_path: str | Path,
    gates_path: str | Path,
    panel_provenance_path: str | Path,
    context_path: str | Path,
    context_provenance_path: str | Path,
    rows_path: str | Path,
    models_path: str | Path,
    provenance_path: str | Path,
    calculated_at: str | None = None,
) -> ContextSensitivityResult:
    """Compara la frontera base con una sensibilidad por control estructural."""

    config = load_context_sensitivity_config(config_path)
    frontier_config = load_estimator_config(config.frontier_config_path)
    if config.minimum_sample != frontier_config.frontier_min_countries:
        raise ContextSensitivityError("mínimo de contexto distinto de la frontera base")
    if config.frontier_quantile != frontier_config.frontier_quantile:
        raise ContextSensitivityError("cuantil de contexto distinto de la frontera base")
    _validate_paths(
        config,
        frontier_config,
        config_path,
        panel_path,
        gates_path,
        panel_provenance_path,
        context_path,
        context_provenance_path,
        rows_path,
        models_path,
        provenance_path,
    )
    panel_bytes, gates_bytes, panel_receipt_bytes, panel_receipt = _read_frontier_inputs(
        frontier_config, panel_path, gates_path, panel_provenance_path
    )
    context_bytes, context_receipt_bytes, context_receipt = _read_context_inputs(
        config, frontier_config, context_path, context_provenance_path
    )
    panel = _read_panel(panel_bytes)
    gates = _read_gates(gates_bytes, frontier_config.frontier_min_countries)
    controls = _context_means(config, frontier_config, context_bytes)
    rules = {rule.id: rule for rule in frontier_config.rules}
    if not set(config.dimensions) <= set(rules):
        raise ContextSensitivityError(
            "la sensibilidad contiene una dimensión fuera de la frontera"
        )

    rows: list[ContextSensitivityRow] = []
    models: list[ContextModelRow] = []
    for dimension in config.dimensions:
        gate = gates.get(dimension)
        if gate is None or not gate.experimental_sample_eligible:
            raise ContextSensitivityError(
                f"la dimensión no está habilitada para sensibilidad: {dimension}"
            )
        if gate.complete_pairs < config.minimum_sample:
            raise ContextSensitivityError(f"muestra insuficiente para contexto: {dimension}")
        sample = sorted(
            (row for row in panel if row.dimension == dimension and row.sample_member),
            key=lambda row: row.entity,
        )
        if len(sample) != gate.complete_pairs:
            raise ContextSensitivityError(f"conteo de muestra inconsistente: {dimension}")
        rule = rules[dimension]
        resources, outcomes = _model_vectors(sample, rule)
        base_fit = fit_monotone_quantile(resources, outcomes, config.frontier_quantile)
        for control in config.controls:
            control_values = [controls[(row.entity, control.indicator_id)] for row in sample]
            transformed = [_transform_context(value, control) for value in control_values]
            fit = fit_conditional_monotone_quantile(
                resources, transformed, outcomes, config.frontier_quantile
            )
            models.append(_model_row(dimension, control, len(sample), fit))
            for row, resource, outcome, value, transformed_value in zip(
                sample, resources, outcomes, control_values, transformed
            ):
                baseline_frontier = _predict(base_fit, resource)
                conditional_frontier = _predict_conditional(fit, resource, transformed_value)
                base_efficiency = _efficiency(outcome, baseline_frontier)[0]
                conditional_efficiency = _efficiency(outcome, conditional_frontier)[0]
                rows.append(
                    ContextSensitivityRow(
                        entity=row.entity,
                        dimension=dimension,
                        control_indicator_id=control.indicator_id,
                        control_value=value,
                        control_unit=control.unit,
                        control_transform=control.transform,
                        transformed_control=transformed_value,
                        sample_size=len(sample),
                        baseline_frontier_score=baseline_frontier,
                        conditional_frontier_score=conditional_frontier,
                        base_efficiency_score=base_efficiency,
                        conditional_efficiency_score=conditional_efficiency,
                        delta_from_base=conditional_efficiency - base_efficiency,
                        official_iee_score=None,
                        flags=tuple(sorted(_row_flags(fit))),
                    )
                )

    rows_bytes = _rows_csv(rows)
    models_bytes = _models_csv(models)
    output_hashes = {"rows": sha256_hex(rows_bytes), "models": sha256_hex(models_bytes)}
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
                "sha256": sha256_hex(panel_receipt_bytes),
                "status": panel_receipt["status"],
            },
            "context": {"path": Path(context_path).as_posix(), "sha256": sha256_hex(context_bytes)},
            "context_provenance": {
                "path": Path(context_provenance_path).as_posix(),
                "sha256": sha256_hex(context_receipt_bytes),
                "manifest_version": context_receipt["manifest_version"],
            },
        },
        "configuration": {
            "path": Path(config_path).as_posix(),
            "sha256": config.sha256,
            "frontier_config_sha256": config.frontier_config_sha256,
            "context_catalog_sha256": config.context_catalog_sha256,
            "context_manifest_sha256": config.context_manifest_sha256,
        },
        "method": {
            "family": "monotone-linear-conditional-quantile-regression",
            "frontier_quantile": config.frontier_quantile,
            "resource_transform": frontier_config.input_transform,
            "context_window": [config.context_start_year, config.context_end_year],
            "separate_controls": [control.indicator_id for control in config.controls],
            "uncertainty": config.uncertainty,
        },
        "publication_gate": {
            "official_iee_score": None,
            "publication_eligible": False,
            "ranking_eligible": False,
            "reasons": [
                "sensibilidades de contexto exploratorias sin incertidumbre estimada",
                "los insumos de frontera permanecen conditional",
                "faltan roles obligatorios por dimensión",
            ],
        },
        "outputs": {
            "rows": {
                "path": Path(rows_path).as_posix(),
                "records": len(rows),
                "sha256": output_hashes["rows"],
            },
            "models": {
                "path": Path(models_path).as_posix(),
                "records": len(models),
                "sha256": output_hashes["models"],
            },
        },
    }
    provenance_bytes = (
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    try:
        _atomic_write_publication(
            (
                (Path(rows_path), rows_bytes),
                (Path(models_path), models_bytes),
                (Path(provenance_path), provenance_bytes),
            )
        )
    except IngestionError as error:
        raise ContextSensitivityError(
            f"no se pudo publicar sensibilidad de contexto: {error}"
        ) from error
    return ContextSensitivityResult(
        row_count=len(rows),
        model_count=len(models),
        rows_path=Path(rows_path),
        models_path=Path(models_path),
        provenance_path=Path(provenance_path),
        output_sha256=output_hashes,
    )


def _read_frontier_inputs(
    frontier_config: EstimatorConfig,
    panel_path: str | Path,
    gates_path: str | Path,
    provenance_path: str | Path,
) -> tuple[bytes, bytes, bytes, Mapping[str, Any]]:
    try:
        return _read_inputs(frontier_config, panel_path, gates_path, provenance_path)
    except ExperimentalFrontierError as error:
        raise ContextSensitivityError(f"frontera base inválida: {error}") from error


def _read_context_inputs(
    config: ContextSensitivityConfig,
    frontier_config: EstimatorConfig,
    context_path: str | Path,
    provenance_path: str | Path,
) -> tuple[bytes, bytes, Mapping[str, Any]]:
    try:
        payload = Path(context_path).read_bytes()
        receipt_bytes = Path(provenance_path).read_bytes()
        receipt = json.loads(receipt_bytes.decode("utf-8"))
        if sha256_hex(payload) != config.context_observations_sha256:
            raise ContextSensitivityError("las observaciones de contexto difieren del contrato")
        if sha256_hex(receipt_bytes) != config.context_provenance_sha256:
            raise ContextSensitivityError("la procedencia de contexto difiere del contrato")
        if (
            receipt["schema_version"] != "iee-observations-v1"
            or receipt["manifest_version"] != "0.4"
        ):
            raise ContextSensitivityError("recibo de contexto no compatible")
        if receipt["catalog"]["sha256"] != config.context_catalog_sha256:
            raise ContextSensitivityError("catálogo de contexto distinto en recibo")
        if receipt["manifest"]["sha256"] != config.context_manifest_sha256:
            raise ContextSensitivityError("manifiesto de contexto distinto en recibo")
        if receipt["processed"]["sha256"] != config.context_observations_sha256:
            raise ContextSensitivityError("hash de contexto distinto en recibo")
        if tuple(receipt["countries"]) != frontier_config.countries:
            raise ContextSensitivityError("universo de contexto distinto de frontera")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise ContextSensitivityError(f"no se pudo validar el contexto: {error}") from error
    return payload, receipt_bytes, receipt


def _context_means(
    config: ContextSensitivityConfig,
    frontier_config: EstimatorConfig,
    payload: bytes,
) -> Mapping[tuple[str, str], Decimal]:
    required = {
        "entity", "period", "indicator_id", "value", "direction", "unit", "source_id",
        "series_code", "source_status", "score_eligible", "observation_kind",
    }
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    if not reader.fieldnames or not required <= set(reader.fieldnames):
        raise ContextSensitivityError("esquema de contexto incompleto")
    expected_controls = {control.indicator_id: control for control in config.controls}
    values: dict[tuple[str, str], dict[int, Decimal]] = {}
    for raw in reader:
        indicator_id = raw["indicator_id"]
        if indicator_id not in expected_controls:
            raise ContextSensitivityError(f"indicador de contexto inesperado: {indicator_id}")
        entity = raw["entity"]
        if entity not in frontier_config.countries:
            raise ContextSensitivityError(f"entidad de contexto inesperada: {entity}")
        control = expected_controls[indicator_id]
        if (
            raw["direction"] != "input"
            or raw["score_eligible"] != "false"
            or raw["source_status"] != "validated"
            or raw["source_id"] != control.source_id
            or raw["series_code"] != control.series_code
            or raw["unit"] != control.unit
            or raw["observation_kind"] != "reported"
        ):
            raise ContextSensitivityError(f"identidad de contexto distinta: {indicator_id}")
        try:
            period = int(raw["period"])
        except ValueError as error:
            raise ContextSensitivityError(
                f"año de contexto inválido: {indicator_id}/{entity}"
            ) from error
        value = _decimal(raw["value"], f"contexto {indicator_id}/{entity}")
        key = (entity, indicator_id)
        by_year = values.setdefault(key, {})
        if period in by_year:
            raise ContextSensitivityError(
                f"contexto duplicado: {indicator_id}/{entity}/{period}"
            )
        by_year[period] = value
    means: dict[tuple[str, str], Decimal] = {}
    years = set(range(config.context_start_year, config.context_end_year + 1))
    for entity in frontier_config.countries:
        for control in config.controls:
            by_year = values.get((entity, control.indicator_id), {})
            if set(by_year) & years != years:
                raise ContextSensitivityError(
                    f"ventana de contexto incompleta: {control.indicator_id}/{entity}"
                )
            means[(entity, control.indicator_id)] = (
                sum(by_year[year] for year in years) / len(years)
            )
    return means


def _decimal(value: str, label: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError) as error:
        raise ContextSensitivityError(f"{label} inválido") from error
    if not parsed.is_finite():
        raise ContextSensitivityError(f"{label} no finito")
    return parsed


def _transform_context(value: Decimal, control: ContextControl) -> float:
    transformed = float(value)
    if control.transform == "log1p":
        if value <= -1:
            raise ContextSensitivityError(f"log1p fuera de dominio: {control.indicator_id}")
        transformed = math.log1p(transformed)
    if not math.isfinite(transformed):
        raise ContextSensitivityError(f"contexto no finito: {control.indicator_id}")
    return transformed


def _predict_conditional(
    fit: ConditionalQuantileFit, resource: float, context: float
) -> float:
    predicted = fit.intercept + fit.resource_slope * resource + fit.context_slope * context
    return min(100.0, max(0.0, predicted))


def _row_flags(fit: ConditionalQuantileFit) -> set[str]:
    flags = {
        "experimental_only",
        "not_official_iee",
        "ranking_blocked",
        "official_iee_null",
        "context_sensitivity_only",
        "context_control_not_causal",
        "uncertainty_not_estimated",
        "input_conditional",
    }
    if abs(fit.resource_slope) <= 1e-12:
        flags.add("flat_resource_slope")
    return flags


def _model_row(
    dimension: str,
    control: ContextControl,
    sample_size: int,
    fit: ConditionalQuantileFit,
) -> ContextModelRow:
    return ContextModelRow(
        dimension=dimension,
        control_indicator_id=control.indicator_id,
        sample_size=sample_size,
        quantile=fit.quantile,
        intercept=fit.intercept,
        resource_slope=fit.resource_slope,
        context_slope=fit.context_slope,
        pinball_loss=fit.pinball_loss,
        official_iee_score=None,
        flags=tuple(sorted(_row_flags(fit))),
    )


def _validate_paths(
    config: ContextSensitivityConfig,
    frontier_config: EstimatorConfig,
    *paths: str | Path,
) -> None:
    config_path, panel, gates, panel_receipt, context, context_receipt, *outputs = paths
    inputs = {
        Path(config_path).resolve(),
        config.frontier_config_path.resolve(),
        config.context_catalog_path.resolve(),
        config.context_manifest_path.resolve(),
        *(path.resolve() for path in frontier_config.dependency_paths),
        Path(panel).resolve(),
        Path(gates).resolve(),
        Path(panel_receipt).resolve(),
        Path(context).resolve(),
        Path(context_receipt).resolve(),
    }
    resolved_outputs = [Path(path).resolve() for path in outputs]
    if len(resolved_outputs) != len(set(resolved_outputs)):
        raise ContextSensitivityError("las rutas de salida deben ser únicas")
    if set(resolved_outputs) & inputs:
        raise ContextSensitivityError("una salida no puede sobrescribir una entrada")


def _csv_float(value: float) -> str:
    return format(value, ".12g")


def _rows_csv(rows: Sequence[ContextSensitivityRow]) -> bytes:
    fields = [
        "entity", "dimension", "control_indicator_id", "control_value", "control_unit",
        "control_transform", "transformed_control", "sample_size", "baseline_frontier_score",
        "conditional_frontier_score", "base_efficiency_score", "conditional_efficiency_score",
        "delta_from_base", "official_iee_score", "flags",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in sorted(
        rows, key=lambda item: (item.dimension, item.control_indicator_id, item.entity)
    ):
        writer.writerow(
            {
                "entity": row.entity,
                "dimension": row.dimension,
                "control_indicator_id": row.control_indicator_id,
                "control_value": str(row.control_value),
                "control_unit": row.control_unit,
                "control_transform": row.control_transform,
                "transformed_control": _csv_float(row.transformed_control),
                "sample_size": row.sample_size,
                "baseline_frontier_score": _csv_float(row.baseline_frontier_score),
                "conditional_frontier_score": _csv_float(row.conditional_frontier_score),
                "base_efficiency_score": _csv_float(row.base_efficiency_score),
                "conditional_efficiency_score": _csv_float(row.conditional_efficiency_score),
                "delta_from_base": _csv_float(row.delta_from_base),
                "official_iee_score": "",
                "flags": ";".join(row.flags),
            }
        )
    return output.getvalue().encode("utf-8")


def _models_csv(rows: Sequence[ContextModelRow]) -> bytes:
    fields = [
        "dimension", "control_indicator_id", "sample_size", "quantile", "intercept",
        "resource_slope", "context_slope", "pinball_loss", "official_iee_score", "flags",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in sorted(rows, key=lambda item: (item.dimension, item.control_indicator_id)):
        writer.writerow(
            {
                "dimension": row.dimension,
                "control_indicator_id": row.control_indicator_id,
                "sample_size": row.sample_size,
                "quantile": _csv_float(row.quantile),
                "intercept": _csv_float(row.intercept),
                "resource_slope": _csv_float(row.resource_slope),
                "context_slope": _csv_float(row.context_slope),
                "pinball_loss": _csv_float(row.pinball_loss),
                "official_iee_score": "",
                "flags": ";".join(row.flags),
            }
        )
    return output.getvalue().encode("utf-8")
