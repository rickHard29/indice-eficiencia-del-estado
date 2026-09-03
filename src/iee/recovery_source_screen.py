"""Registra decisiones de admisibilidad para recuperar una cohorte experimental."""

from __future__ import annotations

import json
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class RecoverySourceScreenError(RuntimeError):
    """Error controlado al evaluar una fuente candidata."""


_DECISIONS = {"not_adopted_incomplete_window", "not_adopted_construct_mismatch", "not_adopted_insufficient_regions"}


def run_recovery_source_screen(
    config_path: str | Path, *, output_path: str | Path, calculated_at: str | None = None
) -> dict[str, Any]:
    """Publica decisiones de fuente; nunca completa una observación faltante."""

    config_file = Path(config_path)
    try:
        config_bytes = config_file.read_bytes()
        config = tomllib.loads(config_bytes.decode("utf-8"))
        candidates = tuple(config["candidates"])
    except (KeyError, OSError, TypeError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise RecoverySourceScreenError(f"configuración de fuente inválida: {error}") from error
    if (
        str(config.get("version")) != "0.5"
        or str(config.get("schema_version")) != "iee-recovery-source-screen-v1"
        or str(config.get("status")) != "experimental-not-for-publication"
    ):
        raise RecoverySourceScreenError("contrato de fuente incompatible")
    if len(candidates) != 6:
        raise RecoverySourceScreenError("el cribado debe cubrir los seis candidatos de primera ola")
    records = []
    seen = set()
    for item in candidates:
        try:
            country = str(item["country"])
            dimension = str(item["dimension"])
            source_url = str(item["source_url"])
            decision = str(item["decision"])
            rationale = str(item["rationale"])
        except (KeyError, TypeError) as error:
            raise RecoverySourceScreenError(f"candidata incompleta: {error}") from error
        if country in seen or decision not in _DECISIONS or not source_url.startswith("https://") or not rationale:
            raise RecoverySourceScreenError(f"candidata inválida: {country}")
        seen.add(country)
        records.append(
            {
                "country": country,
                "dimension": dimension,
                "source_url": source_url,
                "decision": decision,
                "adopted": False,
                "rationale": rationale,
            }
        )
    result = {
        "schema_version": "iee-recovery-source-screen-v1",
        "manifest_version": "0.5",
        "status": "experimental-not-for-publication",
        "calculated_at": calculated_at or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "configuration": {"path": config_file.as_posix(), "sha256": sha256_hex(config_bytes)},
        "candidates": records,
        "adopted_candidates": 0,
        "cohort_change": 0,
        "aggregate": {"experimental_score": None, "official_iee_score": None, "ranking": None, "publication_eligible": False},
    }
    result_bytes = (json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        _atomic_write_publication(((Path(output_path), result_bytes),))
    except IngestionError as error:
        raise RecoverySourceScreenError(f"no se pudo publicar el cribado: {error}") from error
    return result
