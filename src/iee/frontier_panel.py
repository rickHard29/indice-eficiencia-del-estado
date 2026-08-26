"""Construye un panel de frontera experimental sin calcular un IEE oficial."""

from __future__ import annotations

import csv
import io
import json
import re
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .experimental_scoring import SourceObservation, read_normalized_observations
from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class FrontierPanelError(RuntimeError):
    """Error controlado al preparar el panel multinacional de frontera."""


@dataclass(frozen=True)
class DimensionSpec:
    id: str
    label: str
    outcome_indicator_id: str
    outcome_materialized: bool
    outcome_selection: str
    outcome_periods: tuple[int, ...]
    input_indicator_id: str
    input_selection: str
    input_periods: tuple[int, ...]
    input_status_required: str


@dataclass(frozen=True)
class FrontierPanelConfig:
    path: Path
    sha256: str
    version: str
    schema_version: str
    status: str
    countries: tuple[str, ...]
    frontier_min_countries: int
    result_snapshot_sha256: str
    input_snapshot_sha256: str
    result_catalog_path: Path
    result_catalog_sha256: str
    input_catalog_path: Path
    input_catalog_sha256: str
    dimensions: tuple[DimensionSpec, ...]


@dataclass(frozen=True)
class PanelRow:
    entity: str
    dimension: str
    outcome_indicator_id: str
    outcome_period_start: int
    outcome_period_end: int
    outcome_value: Decimal | None
    outcome_unit: str
    input_indicator_id: str
    input_period_start: int
    input_period_end: int
    input_value: Decimal | None
    input_unit: str
    sample_member: bool
    flags: tuple[str, ...]


@dataclass(frozen=True)
class DimensionGate:
    dimension: str
    label: str
    countries_in_frame: int
    complete_pairs: int
    frontier_min_countries: int
    experimental_sample_eligible: bool
    official_frontier_eligible: bool
    official_iee_score: None
    flags: tuple[str, ...]


@dataclass(frozen=True)
class FrontierPanelResult:
    panel_count: int
    gate_count: int
    panel_path: Path
    gates_path: Path
    provenance_path: Path
    output_sha256: Mapping[str, str]


_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SELECTIONS = {"point", "mean"}


def load_frontier_panel_config(path: str | Path) -> FrontierPanelConfig:
    """Carga la definición de un panel experimental y sus catálogos congelados."""

    config_path = Path(path)
    config_bytes, raw = _load_toml(config_path, "configuración del panel de frontera")
    try:
        universe_path = config_path.parent / str(raw["country_universe"])
        result_catalog_path = config_path.parent / str(raw["result_catalog"])
        input_catalog_path = config_path.parent / str(raw["input_catalog"])
        _, universe = _load_toml(universe_path, "universo de países")
        result_catalog_bytes, result_catalog = _load_toml(
            result_catalog_path, "catálogo de resultados"
        )
        input_catalog_bytes, input_catalog = _load_toml(
            input_catalog_path, "catálogo de insumos"
        )
        countries = tuple(str(value) for value in universe["countries"])
        dimensions = tuple(_parse_dimension(item) for item in raw["dimensions"])
        config = FrontierPanelConfig(
            path=config_path,
            sha256=sha256_hex(config_bytes),
            version=str(raw["version"]),
            schema_version=str(raw["schema_version"]),
            status=str(raw["status"]),
            countries=countries,
            frontier_min_countries=int(raw["frontier_min_countries"]),
            result_snapshot_sha256=str(raw["result_snapshot_sha256"]),
            input_snapshot_sha256=str(raw["input_snapshot_sha256"]),
            result_catalog_path=result_catalog_path,
            result_catalog_sha256=sha256_hex(result_catalog_bytes),
            input_catalog_path=input_catalog_path,
            input_catalog_sha256=sha256_hex(input_catalog_bytes),
            dimensions=dimensions,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise FrontierPanelError(f"estructura incompleta en {config_path}: {error}") from error

    _validate_config(config, result_catalog, input_catalog)
    return config


def _load_toml(path: Path, label: str) -> tuple[bytes, Mapping[str, Any]]:
    try:
        payload = path.read_bytes()
        return payload, tomllib.load(io.BytesIO(payload))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise FrontierPanelError(f"no se pudo leer {label} {path}: {error}") from error


def _parse_dimension(raw: Mapping[str, Any]) -> DimensionSpec:
    try:
        outcome_selection = str(raw["outcome_selection"])
        input_selection = str(raw["input_selection"])
        return DimensionSpec(
            id=str(raw["id"]),
            label=str(raw["label"]),
            outcome_indicator_id=str(raw["outcome_indicator_id"]),
            outcome_materialized=raw.get("outcome_materialized", True),
            outcome_selection=outcome_selection,
            outcome_periods=_selection_periods(raw, "outcome", outcome_selection),
            input_indicator_id=str(raw["input_indicator_id"]),
            input_selection=input_selection,
            input_periods=_selection_periods(raw, "input", input_selection),
            input_status_required=str(raw["input_status_required"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise FrontierPanelError(f"dimensión de panel incompleta: {error}") from error


def _selection_periods(raw: Mapping[str, Any], prefix: str, selection: str) -> tuple[int, ...]:
    if selection not in _SELECTIONS:
        raise FrontierPanelError(f"selección inválida para {prefix}: {selection}")
    if selection == "point":
        return (int(raw[f"{prefix}_year"]),)
    start = int(raw[f"{prefix}_start_year"])
    end = int(raw[f"{prefix}_end_year"])
    if end < start:
        raise FrontierPanelError(f"ventana inválida para {prefix}: {start}-{end}")
    return tuple(range(start, end + 1))


def _validate_config(
    config: FrontierPanelConfig,
    result_catalog: Mapping[str, Any],
    input_catalog: Mapping[str, Any],
) -> None:
    if config.version not in {"0.3", "0.6", "0.8", "0.9"}:
        raise FrontierPanelError("la configuración debe declarar una versión de panel compatible")
    if config.status != "experimental-not-for-publication":
        raise FrontierPanelError("el panel v0.3 debe bloquear publicación")
    if not config.countries or len(config.countries) != len(set(config.countries)):
        raise FrontierPanelError("el universo debe contener países únicos")
    if not 3 <= config.frontier_min_countries <= len(config.countries):
        raise FrontierPanelError("frontier_min_countries inválido")
    if not _HEX_SHA256.fullmatch(config.result_snapshot_sha256):
        raise FrontierPanelError("hash de resultados inválido")
    if not _HEX_SHA256.fullmatch(config.input_snapshot_sha256):
        raise FrontierPanelError("hash de insumos inválido")
    ids = [dimension.id for dimension in config.dimensions]
    if not ids or len(ids) != len(set(ids)):
        raise FrontierPanelError("las dimensiones deben ser únicas")

    result_by_id = _catalog_by_id(result_catalog, "resultados")
    input_by_id = _catalog_by_id(input_catalog, "insumos")
    for dimension in config.dimensions:
        result = result_by_id.get(dimension.outcome_indicator_id)
        if dimension.outcome_materialized and result is None:
            raise FrontierPanelError(f"resultado desconocido en {dimension.id}")
        input_entry = input_by_id.get(dimension.input_indicator_id)
        if input_entry is None:
            raise FrontierPanelError(f"insumo desconocido en {dimension.id}")
        if not isinstance(dimension.outcome_materialized, bool):
            raise FrontierPanelError(f"outcome_materialized inválido en {dimension.id}")
        if result is not None and (
            result.get("dimension") != dimension.id or result.get("role") != "resultado"
        ):
            raise FrontierPanelError(f"resultado incoherente en {dimension.id}")
        if result is not None and result.get("status") != "validated":
            raise FrontierPanelError(f"resultado no validado en {dimension.id}")
        if input_entry.get("dimension") != dimension.id or input_entry.get("role") != "insumo":
            raise FrontierPanelError(f"insumo incoherente en {dimension.id}")
        if input_entry.get("status") != dimension.input_status_required:
            raise FrontierPanelError(f"estado de insumo incoherente en {dimension.id}")


def _catalog_by_id(catalog: Mapping[str, Any], label: str) -> Mapping[str, Mapping[str, Any]]:
    raw_series = catalog.get("series")
    if not isinstance(raw_series, list) or not raw_series:
        raise FrontierPanelError(f"catálogo de {label} sin series")
    entries = {str(entry["indicator_id"]): entry for entry in raw_series}
    if len(entries) != len(raw_series):
        raise FrontierPanelError(f"catálogo de {label} con indicadores duplicados")
    return entries


def run_frontier_panel(
    config_path: str | Path,
    *,
    result_observations_path: str | Path,
    result_provenance_path: str | Path,
    input_observations_path: str | Path,
    input_provenance_path: str | Path,
    panel_path: str | Path,
    gates_path: str | Path,
    provenance_path: str | Path,
    calculated_at: str | None = None,
) -> FrontierPanelResult:
    """Une snapshots congelados y publica un panel experimental, no una frontera."""

    config = load_frontier_panel_config(config_path)
    _validate_paths(
        config,
        config_path,
        result_observations_path,
        result_provenance_path,
        input_observations_path,
        input_provenance_path,
        panel_path,
        gates_path,
        provenance_path,
    )
    result_bytes, result_receipt_bytes, result_receipt = _read_snapshot(
        result_observations_path,
        result_provenance_path,
        expected_sha256=config.result_snapshot_sha256,
        expected_catalog_sha256=config.result_catalog_sha256,
        countries=config.countries,
        label="resultados",
    )
    input_bytes, input_receipt_bytes, input_receipt = _read_snapshot(
        input_observations_path,
        input_provenance_path,
        expected_sha256=config.input_snapshot_sha256,
        expected_catalog_sha256=config.input_catalog_sha256,
        countries=config.countries,
        label="insumos",
    )
    result_rows = read_normalized_observations(result_bytes)
    input_rows = read_normalized_observations(input_bytes)
    if len(result_rows) != int(result_receipt["processed"]["records"]):
        raise FrontierPanelError("conteo de resultados difiere del recibo")
    if len(input_rows) != int(input_receipt["processed"]["records"]):
        raise FrontierPanelError("conteo de insumos difiere del recibo")

    _, result_catalog = _load_toml(config.result_catalog_path, "catálogo de resultados")
    _, input_catalog = _load_toml(config.input_catalog_path, "catálogo de insumos")
    _validate_snapshot_identity(result_rows, _catalog_by_id(result_catalog, "resultados"))
    _validate_snapshot_identity(input_rows, _catalog_by_id(input_catalog, "insumos"))

    rows: list[PanelRow] = []
    gates: list[DimensionGate] = []
    for dimension in config.dimensions:
        dimension_rows = [
            _build_panel_row(config, dimension, entity, result_rows, input_rows)
            for entity in config.countries
        ]
        rows.extend(dimension_rows)
        complete_pairs = sum(row.sample_member for row in dimension_rows)
        flags = {
            "experimental_only",
            "not_efficiency_score",
            "publication_blocked",
            "official_iee_null",
            "input_conditional",
        }
        if complete_pairs < config.frontier_min_countries:
            flags.add(f"sample_below_frontier_min:{config.frontier_min_countries}")
        if not any(row.outcome_value is not None for row in dimension_rows):
            flags.add("outcome_not_materialized")
        gates.append(
            DimensionGate(
                dimension=dimension.id,
                label=dimension.label,
                countries_in_frame=len(config.countries),
                complete_pairs=complete_pairs,
                frontier_min_countries=config.frontier_min_countries,
                experimental_sample_eligible=complete_pairs >= config.frontier_min_countries,
                official_frontier_eligible=False,
                official_iee_score=None,
                flags=tuple(sorted(flags)),
            )
        )

    panel_bytes = _panel_csv(rows)
    gates_bytes = _gates_csv(gates)
    output_hashes = {"panel": sha256_hex(panel_bytes), "gates": sha256_hex(gates_bytes)}
    timestamp = calculated_at or datetime.now(UTC).replace(microsecond=0).isoformat()
    provenance = {
        "schema_version": config.schema_version,
        "version": config.version,
        "status": config.status,
        "calculated_at": timestamp,
        "inputs": {
            "results": _snapshot_provenance(
                result_observations_path, result_provenance_path, result_bytes, result_receipt_bytes
            ),
            "inputs": _snapshot_provenance(
                input_observations_path, input_provenance_path, input_bytes, input_receipt_bytes
            ),
        },
        "configuration": {
            "path": Path(config_path).as_posix(),
            "sha256": config.sha256,
            "result_catalog_sha256": config.result_catalog_sha256,
            "input_catalog_sha256": config.input_catalog_sha256,
            "frontier_min_countries": config.frontier_min_countries,
        },
        "countries": list(config.countries),
        "dimension_gates": [
            {
                "dimension": gate.dimension,
                "complete_pairs": gate.complete_pairs,
                "experimental_sample_eligible": gate.experimental_sample_eligible,
                "official_frontier_eligible": gate.official_frontier_eligible,
                "flags": list(gate.flags),
            }
            for gate in gates
        ],
        "publication_gate": {
            "official_iee_score": None,
            "publication_eligible": False,
            "ranking_eligible": False,
            "reasons": [
                "los insumos v0.2 siguen en estado conditional",
                "faltan roles obligatorios en las dimensiones del piloto",
                "el panel no estima todavía una frontera ni incertidumbre",
            ],
        },
        "outputs": {
            "panel": {"path": Path(panel_path).as_posix(), "records": len(rows), "sha256": output_hashes["panel"]},
            "gates": {"path": Path(gates_path).as_posix(), "records": len(gates), "sha256": output_hashes["gates"]},
        },
    }
    provenance_bytes = (json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        _atomic_write_publication(
            ((Path(panel_path), panel_bytes), (Path(gates_path), gates_bytes), (Path(provenance_path), provenance_bytes))
        )
    except IngestionError as error:
        raise FrontierPanelError(f"no se pudo publicar el panel v0.3: {error}") from error
    return FrontierPanelResult(
        panel_count=len(rows),
        gate_count=len(gates),
        panel_path=Path(panel_path),
        gates_path=Path(gates_path),
        provenance_path=Path(provenance_path),
        output_sha256=output_hashes,
    )


def _read_snapshot(
    observations_path: str | Path,
    provenance_path: str | Path,
    *,
    expected_sha256: str,
    expected_catalog_sha256: str,
    countries: tuple[str, ...],
    label: str,
) -> tuple[bytes, bytes, Mapping[str, Any]]:
    try:
        observations = Path(observations_path).read_bytes()
        receipt_bytes = Path(provenance_path).read_bytes()
        receipt = json.loads(receipt_bytes.decode("utf-8"))
        actual_hash = sha256_hex(observations)
        if actual_hash != expected_sha256:
            raise FrontierPanelError(f"hash de {label} difiere de la configuración")
        if receipt["processed"]["sha256"] != actual_hash:
            raise FrontierPanelError(f"hash de {label} difiere del recibo")
        if receipt["schema_version"] != "iee-observations-v1":
            raise FrontierPanelError(f"esquema de {label} no compatible")
        if receipt["catalog"]["sha256"] != expected_catalog_sha256:
            raise FrontierPanelError(f"catálogo de {label} difiere de la configuración")
        if tuple(receipt["countries"]) != countries:
            raise FrontierPanelError(f"universo de {label} difiere de la configuración")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise FrontierPanelError(f"no se pudo validar snapshot de {label}: {error}") from error
    return observations, receipt_bytes, receipt


def _validate_snapshot_identity(
    rows: Sequence[SourceObservation], catalog: Mapping[str, Mapping[str, Any]]
) -> None:
    for row in rows:
        entry = catalog.get(row.indicator_id)
        if entry is None:
            raise FrontierPanelError(f"indicador no declarado en snapshot: {row.indicator_id}")
        identity = {
            "direction": row.direction,
            "unit": row.unit,
            "source_id": row.source_id,
            "source_status": row.source_status,
            "series_code": row.series_code,
        }
        expected = {
            "direction": entry["direction"],
            "unit": entry["unit"],
            "source_id": entry["source_id"],
            "source_status": entry["status"],
            "series_code": entry["official_code"],
        }
        if identity != expected:
            raise FrontierPanelError(f"identidad de fuente inconsistente: {row.indicator_id}")


def _build_panel_row(
    config: FrontierPanelConfig,
    dimension: DimensionSpec,
    entity: str,
    result_rows: Sequence[SourceObservation],
    input_rows: Sequence[SourceObservation],
) -> PanelRow:
    outcome, outcome_flags = _select_value(
        result_rows, entity, dimension.outcome_indicator_id, dimension.outcome_periods,
        required_status="validated", require_score_eligible=True,
    )
    if not dimension.outcome_materialized:
        outcome = None
        outcome_flags = (f"outcome_not_materialized:{dimension.outcome_indicator_id}",)
    input_value, input_flags = _select_value(
        input_rows, entity, dimension.input_indicator_id, dimension.input_periods,
        required_status=dimension.input_status_required, require_score_eligible=False,
    )
    flags = set(outcome_flags) | set(input_flags) | {"experimental_only", "not_efficiency_score"}
    complete = outcome is not None and input_value is not None
    if not complete:
        flags.add("incomplete_pair")
    if input_value is not None:
        flags.add("input_conditional")
    return PanelRow(
        entity=entity,
        dimension=dimension.id,
        outcome_indicator_id=dimension.outcome_indicator_id,
        outcome_period_start=dimension.outcome_periods[0],
        outcome_period_end=dimension.outcome_periods[-1],
        outcome_value=None if outcome is None else outcome[0],
        outcome_unit="" if outcome is None else outcome[1],
        input_indicator_id=dimension.input_indicator_id,
        input_period_start=dimension.input_periods[0],
        input_period_end=dimension.input_periods[-1],
        input_value=None if input_value is None else input_value[0],
        input_unit="" if input_value is None else input_value[1],
        sample_member=complete,
        flags=tuple(sorted(flags)),
    )


def _select_value(
    rows: Sequence[SourceObservation],
    entity: str,
    indicator_id: str,
    periods: tuple[int, ...],
    *,
    required_status: str,
    require_score_eligible: bool,
) -> tuple[tuple[Decimal, str] | None, tuple[str, ...]]:
    selected = sorted(
        (row for row in rows if row.entity == entity and row.indicator_id == indicator_id and row.period in periods),
        key=lambda row: row.period,
    )
    if tuple(row.period for row in selected) != periods:
        return None, (f"missing_window:{indicator_id}",)
    if any(row.source_status != required_status for row in selected):
        return None, (f"unexpected_status:{indicator_id}",)
    if require_score_eligible and any(not row.score_eligible for row in selected):
        return None, (f"outcome_not_score_eligible:{indicator_id}",)
    if not require_score_eligible and any(row.score_eligible for row in selected):
        return None, (f"input_marked_score_eligible:{indicator_id}",)
    if len({row.unit for row in selected}) != 1:
        return None, (f"variable_unit:{indicator_id}",)
    flags = {f"observation_status:{status}" for row in selected for status in [row.observation_status] if status != "observed"}
    return (
        sum((row.value for row in selected), Decimal()) / Decimal(len(selected)),
        selected[0].unit,
    ), tuple(sorted(flags))


def _validate_paths(config: FrontierPanelConfig, *paths: str | Path) -> None:
    config_path, result_obs, result_receipt, input_obs, input_receipt, *outputs = paths
    inputs = {
        Path(config_path).resolve(), config.result_catalog_path.resolve(), config.input_catalog_path.resolve(),
        Path(result_obs).resolve(), Path(result_receipt).resolve(), Path(input_obs).resolve(), Path(input_receipt).resolve(),
    }
    resolved_outputs = [Path(path).resolve() for path in outputs]
    if len(resolved_outputs) != len(set(resolved_outputs)):
        raise FrontierPanelError("las rutas de salida deben ser únicas")
    if set(resolved_outputs) & inputs:
        raise FrontierPanelError("una salida no puede sobrescribir una entrada")


def _snapshot_provenance(
    observations_path: str | Path, provenance_path: str | Path, observations: bytes, receipt: bytes
) -> Mapping[str, str]:
    return {
        "observations_path": Path(observations_path).as_posix(),
        "observations_sha256": sha256_hex(observations),
        "provenance_path": Path(provenance_path).as_posix(),
        "provenance_sha256": sha256_hex(receipt),
    }


def _panel_csv(rows: Sequence[PanelRow]) -> bytes:
    fieldnames = [
        "entity", "dimension", "outcome_indicator_id", "outcome_period_start", "outcome_period_end", "outcome_value", "outcome_unit", "input_indicator_id", "input_period_start", "input_period_end", "input_value", "input_unit", "sample_member", "flags",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in sorted(rows, key=lambda item: (item.dimension, item.entity)):
        writer.writerow({
            "entity": row.entity, "dimension": row.dimension, "outcome_indicator_id": row.outcome_indicator_id,
            "outcome_period_start": row.outcome_period_start, "outcome_period_end": row.outcome_period_end,
            "outcome_value": "" if row.outcome_value is None else str(row.outcome_value), "outcome_unit": row.outcome_unit,
            "input_indicator_id": row.input_indicator_id, "input_period_start": row.input_period_start,
            "input_period_end": row.input_period_end, "input_value": "" if row.input_value is None else str(row.input_value),
            "input_unit": row.input_unit, "sample_member": str(row.sample_member).lower(), "flags": ";".join(row.flags),
        })
    return output.getvalue().encode("utf-8")


def _gates_csv(rows: Sequence[DimensionGate]) -> bytes:
    fieldnames = ["dimension", "label", "countries_in_frame", "complete_pairs", "frontier_min_countries", "experimental_sample_eligible", "official_frontier_eligible", "official_iee_score", "flags"]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in sorted(rows, key=lambda item: item.dimension):
        writer.writerow({
            "dimension": row.dimension, "label": row.label, "countries_in_frame": row.countries_in_frame,
            "complete_pairs": row.complete_pairs, "frontier_min_countries": row.frontier_min_countries,
            "experimental_sample_eligible": str(row.experimental_sample_eligible).lower(),
            "official_frontier_eligible": str(row.official_frontier_eligible).lower(),
            "official_iee_score": "", "flags": ";".join(row.flags),
        })
    return output.getvalue().encode("utf-8")
