"""Exporta archivos públicos del ranking exploratorio, sin certificar el IEE."""

from __future__ import annotations

import csv
import io
import json
import tomllib
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class ResultsRankingPublicationError(RuntimeError):
    """Error controlado para los archivos públicos del ranking exploratorio."""


def run_results_ranking_publication(
    config_path: str | Path,
    *,
    ranking_output_path: str | Path,
    stability_output_path: str | Path,
) -> dict[str, Any]:
    """Genera CSV reutilizables desde los recibos exploratorios validados."""

    config_file = Path(config_path)
    try:
        config = tomllib.loads(config_file.read_text(encoding="utf-8"))
        ranking_path = config_file.parent / str(config["ranking_input"])
        sensitivity_path = config_file.parent / str(config["sensitivity_input"])
        ranking_bytes = ranking_path.read_bytes()
        sensitivity_bytes = sensitivity_path.read_bytes()
        ranking = json.loads(ranking_bytes.decode("utf-8"))
        sensitivity = json.loads(sensitivity_bytes.decode("utf-8"))
    except (KeyError, OSError, TypeError, UnicodeDecodeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        raise ResultsRankingPublicationError(f"configuración de publicación inválida: {error}") from error

    if (
        str(config.get("version")) != "0.1"
        or str(config.get("schema_version")) != "iee-results-ranking-publication-v1"
        or str(config.get("status")) != "experimental-results-ranking-not-iee"
    ):
        raise ResultsRankingPublicationError("contrato de publicación incompatible")
    _validate_exploratory_receipts(ranking, sensitivity)

    stability_by_country = {str(row["country"]): row for row in sensitivity["rank_stability"]}
    ranking_rows = sorted(ranking["ranking"], key=lambda row: int(row["exploratory_rank"]))
    if set(stability_by_country) != {str(row["country"]) for row in ranking_rows}:
        raise ResultsRankingPublicationError("los recibos no comparten la misma cobertura")

    scores_csv = _csv_bytes(
        [
            "country_iso3",
            "exploratory_rank",
            "exploratory_results_score_0_100",
            "education_score_0_100",
            "health_score_0_100",
            "administration_score_0_100",
            "security_justice_score_0_100",
            "status",
        ],
        [
            [
                row["country"],
                row["exploratory_rank"],
                row["exploratory_results_score_0_100"],
                row["dimension_scores_0_100"]["educacion"],
                row["dimension_scores_0_100"]["salud"],
                row["dimension_scores_0_100"]["administracion"],
                row["dimension_scores_0_100"]["seguridad_justicia"],
                "experimental-results-ranking-not-iee",
            ]
            for row in ranking_rows
        ],
    )
    stability_csv = _csv_bytes(
        [
            "country_iso3",
            "base_rank",
            "best_rank_without_one_dimension",
            "worst_rank_without_one_dimension",
            "rank_span_without_one_dimension",
            "status",
        ],
        [
            [
                row["country"],
                row["base_rank"],
                row["best_rank_without_one_dimension"],
                row["worst_rank_without_one_dimension"],
                row["rank_span_without_one_dimension"],
                "experimental-results-ranking-not-iee",
            ]
            for row in sensitivity["rank_stability"]
        ],
    )
    try:
        _atomic_write_publication(
            (
                (Path(ranking_output_path), scores_csv),
                (Path(stability_output_path), stability_csv),
            )
        )
    except IngestionError as error:
        raise ResultsRankingPublicationError(f"no se pudieron publicar los CSV: {error}") from error
    return {
        "countries": len(ranking_rows),
        "status": "experimental-results-ranking-not-iee",
        "ranking_input_sha256": sha256_hex(ranking_bytes),
        "sensitivity_input_sha256": sha256_hex(sensitivity_bytes),
    }


def _validate_exploratory_receipts(ranking: dict[str, Any], sensitivity: dict[str, Any]) -> None:
    if (
        ranking.get("schema_version") != "iee-results-ranking-v1"
        or sensitivity.get("schema_version") != "iee-results-ranking-sensitivity-v1"
        or ranking.get("status") != "experimental-results-ranking-not-iee"
        or sensitivity.get("status") != "experimental-results-ranking-not-iee"
        or ranking.get("official_iee", {}).get("publication_eligible") is not False
        or sensitivity.get("official_iee", {}).get("publication_eligible") is not False
    ):
        raise ResultsRankingPublicationError("los recibos no conservan el bloqueo del IEE oficial")
    if len(ranking.get("ranking", [])) != 33 or len(sensitivity.get("rank_stability", [])) != 33:
        raise ResultsRankingPublicationError("la publicación requiere exactamente 33 países")


def _csv_bytes(header: list[str], rows: list[list[Any]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")
