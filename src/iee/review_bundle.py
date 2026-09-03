"""Construye un paquete de revisión metodológica sin certificar el IEE."""

from __future__ import annotations

import json
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class ReviewBundleError(RuntimeError):
    """Error controlado al preparar el paquete para revisión."""


def run_review_bundle(
    config_path: str | Path,
    *,
    output_path: str | Path,
    calculated_at: str | None = None,
) -> dict[str, Any]:
    """Enumera artefactos para revisión; no produce aprobación ni puntajes."""

    config_file = Path(config_path)
    try:
        config_bytes = config_file.read_bytes()
        config = tomllib.loads(config_bytes.decode("utf-8"))
        artifacts = tuple(
            {"id": str(item["id"]), "label": str(item["label"]), "path": config_file.parent / str(item["path"])}
            for item in config["artifacts"]
        )
    except (KeyError, OSError, TypeError, ValueError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise ReviewBundleError(f"configuración de revisión inválida: {error}") from error
    if (
        str(config.get("version")) != "0.4"
        or str(config.get("schema_version")) != "iee-review-bundle-v1"
        or str(config.get("status")) != "review-ready-not-approved"
    ):
        raise ReviewBundleError("contrato de revisión incompatible")
    ids = [artifact["id"] for artifact in artifacts]
    if len(artifacts) < 6 or len(ids) != len(set(ids)):
        raise ReviewBundleError("el paquete debe contener al menos seis artefactos únicos")
    records = []
    for artifact in artifacts:
        try:
            payload = artifact["path"].read_bytes()
        except OSError as error:
            raise ReviewBundleError(f"artefacto no disponible: {artifact['id']}: {error}") from error
        if not payload.strip():
            raise ReviewBundleError(f"artefacto vacío: {artifact['id']}")
        records.append(
            {
                "id": artifact["id"],
                "label": artifact["label"],
                "path": artifact["path"].as_posix(),
                "sha256": sha256_hex(payload),
            }
        )
    result = {
        "schema_version": "iee-review-bundle-v1",
        "manifest_version": "0.4",
        "status": "review-ready-not-approved",
        "calculated_at": calculated_at
        or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "artifacts": records,
        "review": {
            "status": "not_started",
            "approval_recorded": False,
            "required_actions": [
                "independent_methodological_review",
                "public_response_to_comments",
                "versioned_methodology_decision",
            ],
        },
        "aggregate": {
            "experimental_score": None,
            "official_iee_score": None,
            "ranking": None,
            "publication_eligible": False,
        },
    }
    result_bytes = (json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        _atomic_write_publication(((Path(output_path), result_bytes),))
    except IngestionError as error:
        raise ReviewBundleError(f"no se pudo publicar el paquete de revisión: {error}") from error
    return result
