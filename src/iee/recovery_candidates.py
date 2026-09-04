"""Registra rutas de materialización sin alterar contratos base."""

from __future__ import annotations

import json
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class RecoveryCandidatesError(RuntimeError):
    pass


def run_recovery_candidates(config_path: str | Path, *, output_path: str | Path) -> dict[str, Any]:
    config_file = Path(config_path)
    try:
        raw = config_file.read_bytes()
        config = tomllib.loads(raw.decode("utf-8"))
        candidates = tuple(config["candidates"])
    except (OSError, KeyError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise RecoveryCandidatesError(f"registro de candidatas inválido: {error}") from error
    if config.get("status") != "experimental-not-for-publication" or len(candidates) != 6:
        raise RecoveryCandidatesError("contrato de candidatas incompatible")
    records = []
    for item in candidates:
        country, route, url, status = (
            str(item["country"]), str(item["route"]), str(item["source_url"]), str(item["status"])
        )
        if not url.startswith("https://") or status not in {"candidate_for_materialization", "blocked"}:
            raise RecoveryCandidatesError(f"candidata inválida: {country}")
        records.append({"country": country, "route": route, "source_url": url, "status": status})
    if sum(item["status"] == "candidate_for_materialization" for item in records) != 3:
        raise RecoveryCandidatesError("la exploración debe conservar tres candidatas y tres bloqueos")
    result = {
        "schema_version": "iee-recovery-candidates-v1",
        "manifest_version": "0.6",
        "status": "experimental-not-for-publication",
        "calculated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "configuration_sha256": sha256_hex(raw),
        "candidates": records,
        "adopted_observations": 0,
        "cohort_change": 0,
        "aggregate": {"experimental_score": None, "official_iee_score": None, "ranking": None},
    }
    payload = (json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        _atomic_write_publication(((Path(output_path), payload),))
    except IngestionError as error:
        raise RecoveryCandidatesError(f"no se pudo publicar el registro: {error}") from error
    return result
