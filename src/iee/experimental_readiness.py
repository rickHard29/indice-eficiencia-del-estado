"""Empaqueta puertas experimentales sin producir un ranking IEE."""

from __future__ import annotations

import csv
import io
import json
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class ExperimentalReadinessError(RuntimeError):
    """Error controlado al preparar el paquete de preparación experimental."""


@dataclass(frozen=True)
class EvidenceSpec:
    id: str
    label: str
    kind: str
    gate_path: Path
    expected_dimension: str | None


@dataclass(frozen=True)
class ExperimentalReadinessConfig:
    path: Path
    version: str
    schema_version: str
    status: str
    countries_in_frame: int
    minimum_countries: int
    evidence: tuple[EvidenceSpec, ...]


_KINDS = {"frontier_gate_csv", "role_coverage_gate_json"}


def load_experimental_readiness_config(path: str | Path) -> ExperimentalReadinessConfig:
    """Carga el manifiesto de evidencia experimental sin aceptar un IEE publicable."""

    config_path = Path(path)
    try:
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
        evidence = tuple(
            EvidenceSpec(
                id=str(item["id"]),
                label=str(item["label"]),
                kind=str(item["kind"]),
                gate_path=config_path.parent / str(item["gate"]),
                expected_dimension=(
                    str(item["expected_dimension"])
                    if item.get("expected_dimension") is not None
                    else None
                ),
            )
            for item in raw["evidence"]
        )
        config = ExperimentalReadinessConfig(
            path=config_path,
            version=str(raw["version"]),
            schema_version=str(raw["schema_version"]),
            status=str(raw["status"]),
            countries_in_frame=int(raw["countries_in_frame"]),
            minimum_countries=int(raw["minimum_countries"]),
            evidence=evidence,
        )
    except (KeyError, OSError, TypeError, ValueError, tomllib.TOMLDecodeError) as error:
        raise ExperimentalReadinessError(f"configuración de preparación inválida: {error}") from error

    if config.version != "0.2" or config.schema_version != "iee-experimental-readiness-v1":
        raise ExperimentalReadinessError("versión o esquema de preparación incompatible")
    if config.status != "experimental-not-for-publication":
        raise ExperimentalReadinessError("el manifiesto debe bloquear publicación")
    if config.countries_in_frame < config.minimum_countries or config.minimum_countries < 3:
        raise ExperimentalReadinessError("universo o mínimo de países inválido")
    ids = [item.id for item in config.evidence]
    if len(config.evidence) != 4 or len(ids) != len(set(ids)):
        raise ExperimentalReadinessError("el paquete debe declarar cuatro dimensiones únicas")
    if any(item.kind not in _KINDS for item in config.evidence):
        raise ExperimentalReadinessError("tipo de puerta experimental desconocido")
    return config


def run_experimental_readiness(
    config_path: str | Path,
    *,
    output_path: str | Path,
    calculated_at: str | None = None,
) -> dict[str, Any]:
    """Publica un recibo de preparación; nunca agrega ni ordena países."""

    config = load_experimental_readiness_config(config_path)
    evidence = [_read_evidence(spec, config) for spec in config.evidence]
    payload = {
        "schema_version": config.schema_version,
        "manifest_version": config.version,
        "status": config.status,
        "calculated_at": calculated_at
        or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "countries_in_frame": config.countries_in_frame,
        "minimum_countries": config.minimum_countries,
        "dimensions_with_experimental_track": len(evidence),
        "evidence": evidence,
        "aggregate": {
            "experimental_score": None,
            "official_iee_score": None,
            "ranking": None,
            "publication_eligible": False,
            "blockers": [
                "methodology_v1_not_frozen",
                "no_predeclared_common_cohort",
                "conditional_inputs_remain",
                "open_methodological_review_pending",
            ],
        },
    }
    payload_bytes = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    try:
        _atomic_write_publication(((Path(output_path), payload_bytes),))
    except IngestionError as error:
        raise ExperimentalReadinessError(f"no se pudo publicar el recibo: {error}") from error
    return payload


def _read_evidence(spec: EvidenceSpec, config: ExperimentalReadinessConfig) -> dict[str, Any]:
    try:
        gate_bytes = spec.gate_path.read_bytes()
    except OSError as error:
        raise ExperimentalReadinessError(f"no se pudo leer la puerta {spec.id}: {error}") from error
    if spec.kind == "frontier_gate_csv":
        return _read_frontier_gate(spec, config, gate_bytes)
    return _read_role_coverage_gate(spec, config, gate_bytes)


def _read_frontier_gate(
    spec: EvidenceSpec, config: ExperimentalReadinessConfig, gate_bytes: bytes
) -> dict[str, Any]:
    try:
        rows = list(csv.DictReader(io.StringIO(gate_bytes.decode("utf-8"))))
        if len(rows) != 1:
            raise ValueError("debe contener exactamente una fila")
        row = rows[0]
        dimension = str(row["dimension"])
        complete = int(row["complete_pairs"])
        in_frame = int(row["countries_in_frame"])
        eligible = row["experimental_sample_eligible"] == "true"
        official = row["official_frontier_eligible"] == "true"
        score = row["official_iee_score"]
    except (KeyError, UnicodeDecodeError, ValueError, csv.Error) as error:
        raise ExperimentalReadinessError(f"puerta de frontera inválida para {spec.id}: {error}") from error
    if dimension != spec.expected_dimension or in_frame != config.countries_in_frame:
        raise ExperimentalReadinessError(f"identidad de puerta inconsistente para {spec.id}")
    if complete < config.minimum_countries or not eligible or official or score:
        raise ExperimentalReadinessError(f"puerta experimental no segura para {spec.id}")
    return {
        "id": spec.id,
        "label": spec.label,
        "kind": spec.kind,
        "complete_countries": complete,
        "experimental_track_eligible": True,
        "official_iee_score": None,
        "source_gate": {"path": spec.gate_path.as_posix(), "sha256": sha256_hex(gate_bytes)},
    }


def _read_role_coverage_gate(
    spec: EvidenceSpec, config: ExperimentalReadinessConfig, gate_bytes: bytes
) -> dict[str, Any]:
    try:
        row = json.loads(gate_bytes.decode("utf-8"))
        complete = int(row["complete_all_roles"])
        in_frame = int(row["countries_in_frame"])
        eligible = row["integration_sample_eligible"] is True
        official_score = row["official_iee_score"]
    except (KeyError, UnicodeDecodeError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise ExperimentalReadinessError(f"puerta de roles inválida para {spec.id}: {error}") from error
    if in_frame != config.countries_in_frame or complete < config.minimum_countries or not eligible:
        raise ExperimentalReadinessError(f"puerta de roles no segura para {spec.id}")
    if official_score is not None:
        raise ExperimentalReadinessError(f"la puerta de roles no puede contener puntaje IEE: {spec.id}")
    return {
        "id": spec.id,
        "label": spec.label,
        "kind": spec.kind,
        "complete_countries": complete,
        "experimental_track_eligible": True,
        "official_iee_score": None,
        "source_gate": {"path": spec.gate_path.as_posix(), "sha256": sha256_hex(gate_bytes)},
    }
