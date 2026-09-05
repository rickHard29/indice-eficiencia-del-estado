"""Cierra técnicamente rutas de recuperación sin abrir puertas de publicación."""

from __future__ import annotations

import json
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class RecoveryResolutionError(RuntimeError):
    """Error controlado al resolver candidatas de recuperación."""


_DECISIONS = {
    "not_adopted_fiscal_scope_mismatch",
    "not_adopted_definition_discontinuity",
    "not_adopted_definition_mismatch",
}


def run_recovery_resolution(config_path: str | Path, *, output_path: str | Path) -> dict[str, Any]:
    config_file = Path(config_path)
    try:
        raw = config_file.read_bytes()
        config = tomllib.loads(raw.decode("utf-8"))
        resolutions = tuple(config["resolutions"])
    except (OSError, KeyError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise RecoveryResolutionError(f"resolución de recuperación inválida: {error}") from error
    if config.get("status") != "technical-cycle-complete-not-for-publication" or len(resolutions) != 3:
        raise RecoveryResolutionError("contrato de resolución incompatible")
    try:
        before = int(config["common_cohort_before"])
        after = int(config["common_cohort_after"])
        minimum = int(config["minimum_common_cohort"])
    except (KeyError, TypeError, ValueError) as error:
        raise RecoveryResolutionError(f"cohorte de resolución inválida: {error}") from error
    if before != 24 or after != before or minimum != 30:
        raise RecoveryResolutionError("la resolución no puede alterar la cohorte ni su umbral")

    records: list[dict[str, Any]] = []
    for item in resolutions:
        try:
            country = str(item["country"])
            dimension = str(item["dimension"])
            decision = str(item["decision"])
            urls = tuple(str(url) for url in item["source_urls"])
            evidence = str(item["evidence"])
        except (KeyError, TypeError) as error:
            raise RecoveryResolutionError(f"resolución incompleta: {error}") from error
        if decision not in _DECISIONS or len(urls) != 2 or not evidence:
            raise RecoveryResolutionError(f"resolución inválida: {country}")
        if not all(url.startswith("https://") for url in urls):
            raise RecoveryResolutionError(f"fuente insegura: {country}")
        records.append({
            "country": country,
            "dimension": dimension,
            "decision": decision,
            "source_urls": urls,
            "evidence": evidence,
            "adopted": False,
        })
    if {record["country"] for record in records} != {"AUS", "GRC", "DEU"}:
        raise RecoveryResolutionError("la resolución debe cerrar exactamente Australia, Grecia y Alemania")

    result = {
        "schema_version": "iee-recovery-resolution-v1",
        "manifest_version": "0.7",
        "status": "technical-cycle-complete-not-for-publication",
        "calculated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "configuration_sha256": sha256_hex(raw),
        "resolutions": records,
        "technical_cycle_complete": True,
        "adopted_observations": 0,
        "cohort": {"before": before, "after": after, "minimum": minimum, "change": 0},
        "aggregate": {"experimental_score": None, "official_iee_score": None, "ranking": None},
    }
    payload = (json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        _atomic_write_publication(((Path(output_path), payload),))
    except IngestionError as error:
        raise RecoveryResolutionError(f"no se pudo publicar la resolución: {error}") from error
    return result
