"""Cierra un corte común experimental sin convertirlo en un ranking."""

from __future__ import annotations

import json
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class CurrentCohortReleaseError(RuntimeError):
    """Error controlado al preparar el cierre de la cohorte vigente."""


def run_current_cohort_release(
    config_path: str | Path,
    *,
    output_path: str | Path,
    calculated_at: str | None = None,
) -> dict[str, Any]:
    """Emite un recibo de cohorte completa, sin habilitar agregación."""

    config_file = Path(config_path)
    try:
        config_bytes = config_file.read_bytes()
        config = tomllib.loads(config_bytes.decode("utf-8"))
        cohort_path = config_file.parent / str(config["cohort_receipt"])
        review_path = config_file.parent / str(config["review_bundle"])
        cohort_bytes = cohort_path.read_bytes()
        review_bytes = review_path.read_bytes()
        cohort = json.loads(cohort_bytes.decode("utf-8"))
        review = json.loads(review_bytes.decode("utf-8"))
        expected_countries = tuple(str(country) for country in config["expected_countries"])
    except (
        KeyError,
        OSError,
        TypeError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        tomllib.TOMLDecodeError,
    ) as error:
        raise CurrentCohortReleaseError(f"configuración de cierre inválida: {error}") from error

    if (
        str(config.get("version")) != "1.0"
        or str(config.get("schema_version")) != "iee-current-cohort-release-v1"
        or str(config.get("status")) != "experimental-not-for-publication"
    ):
        raise CurrentCohortReleaseError("contrato de cierre incompatible")
    if len(expected_countries) != 24 or len(expected_countries) != len(set(expected_countries)):
        raise CurrentCohortReleaseError("la cohorte esperada debe contener 24 países únicos")
    if cohort.get("schema_version") != "iee-experimental-cohort-v1":
        raise CurrentCohortReleaseError("recibo de cohorte incompatible")
    if review.get("schema_version") != "iee-review-bundle-v1":
        raise CurrentCohortReleaseError("paquete de revisión incompatible")

    common = tuple(str(country) for country in cohort.get("common_cohort", {}).get("countries", []))
    if common != tuple(sorted(expected_countries)):
        raise CurrentCohortReleaseError("la cohorte calculada no coincide con el corte declarado")
    if cohort.get("common_cohort", {}).get("complete_countries") != len(expected_countries):
        raise CurrentCohortReleaseError("conteo de cohorte inconsistente")
    if cohort.get("common_cohort", {}).get("experimental_aggregate_eligible") is not False:
        raise CurrentCohortReleaseError("la cohorte no puede habilitar agregación")
    if cohort.get("aggregate", {}).get("ranking") is not None:
        raise CurrentCohortReleaseError("el recibo de cohorte no puede contener ranking")
    if review.get("review", {}).get("approval_recorded") is not False:
        raise CurrentCohortReleaseError("el cierre no puede declarar revisión aprobada")

    payload: dict[str, Any] = {
        "schema_version": "iee-current-cohort-release-v1",
        "manifest_version": "1.0",
        "status": "experimental-not-for-publication",
        "calculated_at": calculated_at
        or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "current_common_cohort": {
            "countries": list(common),
            "complete_countries": len(common),
            "frame_countries": cohort["countries_in_frame"],
            "minimum_for_aggregate": cohort["minimum_countries"],
            "closure": "reproducible_current_cut",
        },
        "evidence": {
            "cohort_receipt": {
                "path": cohort_path.as_posix(),
                "sha256": sha256_hex(cohort_bytes),
            },
            "review_bundle": {
                "path": review_path.as_posix(),
                "sha256": sha256_hex(review_bytes),
                "artifact_count": len(review.get("artifacts", [])),
            },
        },
        "aggregate": {
            "experimental_score": None,
            "official_iee_score": None,
            "ranking": None,
            "publication_eligible": False,
            "blockers": [
                "common_cohort_below_minimum",
                "methodology_v1_not_frozen",
                "independent_review_not_approved",
            ],
        },
    }
    payload_bytes = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    try:
        _atomic_write_publication(((Path(output_path), payload_bytes),))
    except IngestionError as error:
        raise CurrentCohortReleaseError(f"no se pudo publicar el cierre: {error}") from error
    return payload
