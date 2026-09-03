"""Prioriza recuperación de cobertura a partir de una cohorte ya auditada."""

from __future__ import annotations

import json
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class CohortRecoveryError(RuntimeError):
    """Error controlado al priorizar recuperación de cohorte."""


def run_cohort_recovery(
    config_path: str | Path,
    *,
    output_path: str | Path,
    calculated_at: str | None = None,
) -> dict[str, Any]:
    """Publica prioridades de evidencia; no completa ni imputa ningún dato."""

    config_file = Path(config_path)
    try:
        config_bytes = config_file.read_bytes()
        config = tomllib.loads(config_bytes.decode("utf-8"))
        cohort_path = config_file.parent / str(config["cohort_receipt"])
        target_minimum = int(config["target_minimum_countries"])
        max_first_wave = int(config["max_first_wave"])
        receipt_bytes = cohort_path.read_bytes()
        receipt = json.loads(receipt_bytes.decode("utf-8"))
    except (KeyError, OSError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        raise CohortRecoveryError(f"configuración o recibo de recuperación inválido: {error}") from error
    if (
        str(config.get("version")) != "0.3"
        or str(config.get("schema_version")) != "iee-cohort-recovery-v1"
        or str(config.get("status")) != "experimental-not-for-publication"
    ):
        raise CohortRecoveryError("contrato de recuperación incompatible")
    if receipt.get("schema_version") != "iee-experimental-cohort-v1":
        raise CohortRecoveryError("recibo de cohorte incompatible")
    try:
        countries_in_frame = int(receipt["countries_in_frame"])
        common = set(str(country) for country in receipt["common_cohort"]["countries"])
        missing_by_dimension = {
            str(dimension): set(str(country) for country in countries)
            for dimension, countries in receipt["common_cohort"]["missing_by_dimension"].items()
        }
    except (KeyError, TypeError, ValueError) as error:
        raise CohortRecoveryError(f"cohorte sin faltantes interpretables: {error}") from error
    if countries_in_frame != 38 or not 3 <= target_minimum <= countries_in_frame:
        raise CohortRecoveryError("universo o meta de recuperación inválidos")
    if receipt.get("aggregate", {}).get("ranking") is not None:
        raise CohortRecoveryError("el recibo de cohorte no puede contener un ranking")
    universe = set().union(common, *missing_by_dimension.values())
    if len(universe) != countries_in_frame or len(common) >= target_minimum:
        raise CohortRecoveryError("la recuperación solo aplica a una cohorte incompleta OCDE-38")
    candidates = []
    for country in sorted(universe - common):
        missing = sorted(dimension for dimension, countries in missing_by_dimension.items() if country in countries)
        if not missing:
            raise CohortRecoveryError(f"país fuera de cohorte sin faltantes: {country}")
        candidates.append({"country": country, "missing_dimensions": missing, "missing_count": len(missing)})
    candidates.sort(key=lambda item: (item["missing_count"], item["country"]))
    needed = target_minimum - len(common)
    first_wave = [item for item in candidates if item["missing_count"] == 1][: min(needed, max_first_wave)]
    payload = {
        "schema_version": "iee-cohort-recovery-v1",
        "manifest_version": str(config["version"]),
        "status": str(config["status"]),
        "calculated_at": calculated_at
        or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "cohort_receipt": {"path": cohort_path.as_posix(), "sha256": sha256_hex(receipt_bytes)},
        "current_common_countries": len(common),
        "target_minimum_countries": target_minimum,
        "countries_needed": needed,
        "first_wave": first_wave,
        "remaining_candidates": candidates,
        "aggregate": {
            "experimental_score": None,
            "official_iee_score": None,
            "ranking": None,
            "publication_eligible": False,
            "rule": "priorities_are_coverage_tasks_not_country_performance",
        },
    }
    payload_bytes = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        _atomic_write_publication(((Path(output_path), payload_bytes),))
    except IngestionError as error:
        raise CohortRecoveryError(f"no se pudo publicar la prioridad: {error}") from error
    return payload
