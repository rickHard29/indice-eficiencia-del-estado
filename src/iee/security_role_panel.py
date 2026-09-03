"""Integra roles de seguridad en un diagnóstico de cobertura, sin puntuar."""

from __future__ import annotations

import csv
import io
import json
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .experimental_scoring import SourceObservation, read_normalized_observations
from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class SecurityRolePanelError(RuntimeError):
    """Error controlado en el diagnóstico de integración de seguridad."""


@dataclass(frozen=True)
class RoleSpec:
    name: str
    indicator_id: str
    periods: tuple[int, ...]
    required_status: str
    score_eligible: bool


@dataclass(frozen=True)
class SecurityRolePanelConfig:
    path: Path
    sha256: str
    version: str
    schema_version: str
    status: str
    countries: tuple[str, ...]
    integration_min_countries: int
    catalogs: Mapping[str, Path]
    catalog_hashes: Mapping[str, str]
    roles: Mapping[str, RoleSpec]


@dataclass(frozen=True)
class SecurityRolePanelResult:
    panel_count: int
    complete_roles: int
    panel_path: Path
    gate_path: Path
    provenance_path: Path
    output_sha256: Mapping[str, str]


def load_security_role_panel_config(path: str | Path) -> SecurityRolePanelConfig:
    """Carga una definición explícita de resultado, equidad e insumo."""

    config_path = Path(path)
    config_bytes, raw = _load_toml(config_path, "configuración de integración")
    try:
        universe_path = config_path.parent / str(raw["country_universe"])
        _, universe = _load_toml(universe_path, "universo de países")
        catalogs = {
            "result": config_path.parent / str(raw["result_catalog"]),
            "input": config_path.parent / str(raw["input_catalog"]),
            "equity": config_path.parent / str(raw["equity_catalog"]),
        }
        catalog_hashes = {name: sha256_hex(path.read_bytes()) for name, path in catalogs.items()}
        roles = {
            name: _parse_role(name, raw[name])
            for name in ("result", "equity", "input")
        }
        config = SecurityRolePanelConfig(
            path=config_path,
            sha256=sha256_hex(config_bytes),
            version=str(raw["version"]),
            schema_version=str(raw["schema_version"]),
            status=str(raw["status"]),
            countries=tuple(str(country) for country in universe["countries"]),
            integration_min_countries=int(raw["integration_min_countries"]),
            catalogs=catalogs,
            catalog_hashes=catalog_hashes,
            roles=roles,
        )
    except (KeyError, OSError, TypeError, ValueError) as error:
        raise SecurityRolePanelError(
            f"estructura incompleta en {config_path}: {error}"
        ) from error
    _validate_config(config)
    return config


def run_security_role_panel(
    config_path: str | Path,
    *,
    result_observations_path: str | Path,
    result_provenance_path: str | Path,
    equity_observations_path: str | Path,
    equity_provenance_path: str | Path,
    input_observations_path: str | Path,
    input_provenance_path: str | Path,
    panel_path: str | Path,
    gate_path: str | Path,
    provenance_path: str | Path,
    calculated_at: str | None = None,
) -> SecurityRolePanelResult:
    """Publica únicamente una máscara auditable de cobertura de los tres roles."""

    config = load_security_role_panel_config(config_path)
    sources = {
        "result": _read_snapshot(result_observations_path, result_provenance_path, config, "result"),
        "equity": _read_snapshot(equity_observations_path, equity_provenance_path, config, "equity"),
        "input": _read_snapshot(input_observations_path, input_provenance_path, config, "input"),
    }
    selected = {
        name: _select_by_role(rows, config.roles[name], _catalog_entry(config, name))
        for name, (rows, _, _) in sources.items()
    }
    rows = [_build_row(entity, config, selected) for entity in config.countries]
    complete_roles = sum(row["all_roles_complete"] == "true" for row in rows)
    flags = {
        "experimental_only",
        "not_efficiency_score",
        "not_frontier_estimate",
        "not_ranking",
        "official_iee_null",
        "conditional_input",
        "conditional_equity",
    }
    if complete_roles < config.integration_min_countries:
        flags.add(f"sample_below_integration_min:{config.integration_min_countries}")
    gate = {
        "countries_in_frame": len(config.countries),
        "complete_all_roles": complete_roles,
        "integration_min_countries": config.integration_min_countries,
        "integration_sample_eligible": complete_roles >= config.integration_min_countries,
        "experimental_frontier_eligible": False,
        "official_iee_score": None,
        "flags": sorted(flags),
    }
    panel_bytes = _rows_csv(rows)
    gate_bytes = (json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output_hashes = {"panel": sha256_hex(panel_bytes), "gate": sha256_hex(gate_bytes)}
    timestamp = calculated_at or datetime.now(UTC).replace(microsecond=0).isoformat()
    provenance = {
        "schema_version": config.schema_version,
        "version": config.version,
        "status": config.status,
        "calculated_at": timestamp,
        "configuration": {"path": Path(config_path).as_posix(), "sha256": config.sha256},
        "inputs": {
            name: _source_provenance(observations, receipt)
            for name, (_, observations, receipt) in sources.items()
        },
        "role_coverage": gate,
        "publication_gate": {
            "official_iee_score": None,
            "publication_eligible": False,
            "ranking_eligible": False,
            "reasons": [
                "el diagnóstico integra cobertura, no estima eficiencia",
                "resultado, insumo y equidad no comparten una muestra suficiente",
                "insumo y equidad siguen en estado conditional",
            ],
        },
        "outputs": {
            "panel": {"path": Path(panel_path).as_posix(), "records": len(rows), "sha256": output_hashes["panel"]},
            "gate": {"path": Path(gate_path).as_posix(), "records": 1, "sha256": output_hashes["gate"]},
        },
    }
    provenance_bytes = (json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _validate_output_paths(
        (result_observations_path, result_provenance_path, equity_observations_path, equity_provenance_path,
         input_observations_path, input_provenance_path),
        (panel_path, gate_path, provenance_path),
    )
    try:
        _atomic_write_publication(
            ((Path(panel_path), panel_bytes), (Path(gate_path), gate_bytes), (Path(provenance_path), provenance_bytes))
        )
    except IngestionError as error:
        raise SecurityRolePanelError(f"no se pudo publicar el diagnóstico: {error}") from error
    return SecurityRolePanelResult(
        panel_count=len(rows), complete_roles=complete_roles, panel_path=Path(panel_path),
        gate_path=Path(gate_path), provenance_path=Path(provenance_path), output_sha256=output_hashes,
    )


def _load_toml(path: Path, label: str) -> tuple[bytes, Mapping[str, Any]]:
    try:
        payload = path.read_bytes()
        return payload, tomllib.load(io.BytesIO(payload))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise SecurityRolePanelError(f"no se pudo leer {label} {path}: {error}") from error


def _parse_role(name: str, raw: Mapping[str, Any]) -> RoleSpec:
    try:
        selection = str(raw["selection"])
        if selection == "point":
            periods = (int(raw["year"]),)
        elif selection == "mean":
            start, end = int(raw["start_year"]), int(raw["end_year"])
            if end < start:
                raise ValueError("ventana invertida")
            periods = tuple(range(start, end + 1))
        else:
            raise ValueError(f"selección inválida: {selection}")
        return RoleSpec(name, str(raw["indicator_id"]), periods, str(raw["required_status"]), bool(raw["score_eligible"]))
    except (KeyError, TypeError, ValueError) as error:
        raise SecurityRolePanelError(f"rol {name} inválido: {error}") from error


def _validate_config(config: SecurityRolePanelConfig) -> None:
    if config.version != "2.5" or config.schema_version != "iee-security-role-panel-v1":
        raise SecurityRolePanelError("versión o esquema de integración no compatible")
    if config.status != "experimental-not-for-publication":
        raise SecurityRolePanelError("el diagnóstico debe bloquear publicación")
    if len(config.countries) != 38 or len(set(config.countries)) != len(config.countries):
        raise SecurityRolePanelError("el diagnóstico requiere el universo OCDE-38 único")
    if not 3 <= config.integration_min_countries <= len(config.countries):
        raise SecurityRolePanelError("integration_min_countries inválido")
    expected = {
        "result": ("SEG-RES-01", "resultado"),
        "equity": ("SEG-EQ-01", "equidad"),
        "input": ("SEG-IN-02", "insumo"),
    }
    for name, (indicator_id, role) in expected.items():
        spec = config.roles[name]
        if spec.indicator_id != indicator_id:
            raise SecurityRolePanelError(f"indicador inesperado en {name}")
        entry = _catalog_entry(config, name)
        if entry is None or entry.get("dimension") != "seguridad_justicia" or entry.get("role") != role:
            raise SecurityRolePanelError(f"catálogo incoherente para {indicator_id}")
        if entry.get("status") != spec.required_status:
            raise SecurityRolePanelError(f"estado de catálogo incoherente para {indicator_id}")


def _catalog_entry(config: SecurityRolePanelConfig, name: str) -> Mapping[str, Any]:
    _, catalog = _load_toml(config.catalogs[name], f"catálogo {name}")
    entries = {str(entry["indicator_id"]): entry for entry in catalog.get("series", [])}
    entry = entries.get(config.roles[name].indicator_id)
    if entry is None:
        raise SecurityRolePanelError(f"indicador faltante en catálogo {name}")
    return entry


def _read_snapshot(
    observations_path: str | Path, provenance_path: str | Path, config: SecurityRolePanelConfig, name: str
) -> tuple[list[SourceObservation], bytes, bytes]:
    try:
        observations = Path(observations_path).read_bytes()
        receipt = Path(provenance_path).read_bytes()
        raw_receipt = json.loads(receipt.decode("utf-8"))
        if raw_receipt["schema_version"] != "iee-observations-v1":
            raise SecurityRolePanelError(f"esquema incompatible en {name}")
        if tuple(raw_receipt["countries"]) != config.countries:
            raise SecurityRolePanelError(f"universo de {name} distinto a OCDE-38")
        if raw_receipt["processed"]["sha256"] != sha256_hex(observations):
            raise SecurityRolePanelError(f"hash de observaciones inconsistente en {name}")
        if raw_receipt["catalog"]["sha256"] != config.catalog_hashes[name]:
            raise SecurityRolePanelError(f"catálogo de {name} distinto a la integración")
        rows = read_normalized_observations(observations)
        if len(rows) != int(raw_receipt["processed"]["records"]):
            raise SecurityRolePanelError(f"conteo de {name} distinto al recibo")
        return rows, observations, receipt
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise SecurityRolePanelError(f"no se pudo validar snapshot de {name}: {error}") from error


def _select_by_role(
    rows: Sequence[SourceObservation], spec: RoleSpec, catalog: Mapping[str, Any]
) -> Mapping[str, tuple[Decimal, str, tuple[str, ...]]]:
    selected: dict[str, tuple[Decimal, str, tuple[str, ...]]] = {}
    for entity in {row.entity for row in rows}:
        candidates = sorted(
            (row for row in rows if row.entity == entity and row.indicator_id == spec.indicator_id and row.period in spec.periods),
            key=lambda row: row.period,
        )
        if tuple(row.period for row in candidates) != spec.periods:
            continue
        if any(row.source_status != spec.required_status or row.score_eligible != spec.score_eligible for row in candidates):
            continue
        expected = {
            "direction": catalog["direction"],
            "unit": catalog["unit"],
            "source_id": catalog["source_id"],
            "series_code": catalog["official_code"],
        }
        if any(
            {"direction": row.direction, "unit": row.unit, "source_id": row.source_id, "series_code": row.series_code} != expected
            for row in candidates
        ):
            raise SecurityRolePanelError(f"identidad de fuente inconsistente: {spec.indicator_id}")
        if len({row.unit for row in candidates}) != 1:
            continue
        statuses = tuple(sorted({row.observation_status for row in candidates if row.observation_status != "observed"}))
        selected[entity] = (sum((row.value for row in candidates), Decimal()) / Decimal(len(candidates)), candidates[0].unit, statuses)
    return selected


def _build_row(
    entity: str, config: SecurityRolePanelConfig, selected: Mapping[str, Mapping[str, tuple[Decimal, str, tuple[str, ...]]]]
) -> dict[str, str]:
    values = {name: selected[name].get(entity) for name in ("result", "equity", "input")}
    flags = {"experimental_only", "not_efficiency_score"}
    for name, value in values.items():
        if value is None:
            flags.add(f"missing_{name}:{config.roles[name].indicator_id}")
        else:
            flags.update(f"{name}_observation_status:{status}" for status in value[2])
    complete = all(value is not None for value in values.values())
    if not complete:
        flags.add("incomplete_role_set")
    result, equity, input_value = values["result"], values["equity"], values["input"]
    return {
        "entity": entity,
        "result_indicator_id": config.roles["result"].indicator_id,
        "result_value": "" if result is None else str(result[0]),
        "result_unit": "" if result is None else result[1],
        "equity_indicator_id": config.roles["equity"].indicator_id,
        "equity_value": "" if equity is None else str(equity[0]),
        "equity_unit": "" if equity is None else equity[1],
        "input_indicator_id": config.roles["input"].indicator_id,
        "input_value": "" if input_value is None else str(input_value[0]),
        "input_unit": "" if input_value is None else input_value[1],
        "all_roles_complete": str(complete).lower(),
        "flags": ";".join(sorted(flags)),
    }


def _rows_csv(rows: Sequence[Mapping[str, str]]) -> bytes:
    fieldnames = [
        "entity", "result_indicator_id", "result_value", "result_unit", "equity_indicator_id", "equity_value",
        "equity_unit", "input_indicator_id", "input_value", "input_unit", "all_roles_complete", "flags",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(sorted(rows, key=lambda row: row["entity"]))
    return output.getvalue().encode("utf-8")


def _source_provenance(observations: bytes, receipt: bytes) -> Mapping[str, str]:
    return {"observations_sha256": sha256_hex(observations), "provenance_sha256": sha256_hex(receipt)}


def _validate_output_paths(inputs: Sequence[str | Path], outputs: Sequence[str | Path]) -> None:
    resolved_inputs = {Path(path).resolve() for path in inputs}
    resolved_outputs = [Path(path).resolve() for path in outputs]
    if len(set(resolved_outputs)) != len(resolved_outputs) or set(resolved_outputs) & resolved_inputs:
        raise SecurityRolePanelError("las salidas deben ser únicas y no sobrescribir entradas")
