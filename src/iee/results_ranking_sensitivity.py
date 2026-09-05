"""Prueba de sensibilidad del ranking exploratorio de resultados."""

from __future__ import annotations

import json
import tomllib
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class ResultsRankingSensitivityError(RuntimeError):
    """Error controlado para la sensibilidad del ranking exploratorio."""


def run_results_ranking_sensitivity(
    config_path: str | Path,
    *,
    output_path: str | Path,
    calculated_at: str | None = None,
) -> dict[str, Any]:
    """Recalcula posiciones al omitir una dimensión, sin certificar el IEE."""

    config_file = Path(config_path)
    try:
        config = tomllib.loads(config_file.read_text(encoding="utf-8"))
        dimensions = tuple(str(item) for item in config["dimensions"])
        expected_countries = tuple(str(item) for item in config["expected_countries"])
        ranking_path = config_file.parent / str(config["ranking_input"])
        ranking_bytes = ranking_path.read_bytes()
        ranking = json.loads(ranking_bytes.decode("utf-8"))
    except (KeyError, OSError, TypeError, UnicodeDecodeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        raise ResultsRankingSensitivityError(f"configuración de sensibilidad inválida: {error}") from error

    if (
        str(config.get("version")) != "0.1"
        or str(config.get("schema_version")) != "iee-results-ranking-sensitivity-v1"
        or str(config.get("status")) != "experimental-results-ranking-not-iee"
    ):
        raise ResultsRankingSensitivityError("contrato de sensibilidad incompatible")
    if len(dimensions) != 4 or len(set(dimensions)) != 4:
        raise ResultsRankingSensitivityError("se requieren exactamente cuatro dimensiones únicas")
    if len(expected_countries) != 33 or len(set(expected_countries)) != 33:
        raise ResultsRankingSensitivityError("la sensibilidad requiere exactamente 33 países declarados")
    if (
        ranking.get("schema_version") != "iee-results-ranking-v1"
        or ranking.get("status") != "experimental-results-ranking-not-iee"
        or ranking.get("official_iee", {}).get("publication_eligible") is not False
    ):
        raise ResultsRankingSensitivityError("el insumo no es un ranking exploratorio válido")

    rows = ranking.get("ranking")
    if not isinstance(rows, list) or len(rows) != len(expected_countries):
        raise ResultsRankingSensitivityError("el insumo no contiene los 33 países requeridos")
    countries = tuple(str(row.get("country")) for row in rows)
    if tuple(sorted(countries)) != tuple(sorted(expected_countries)) or len(set(countries)) != len(countries):
        raise ResultsRankingSensitivityError("la cobertura del insumo no coincide con la declarada")

    base_rank: dict[str, int] = {}
    scores: dict[str, dict[str, Decimal]] = {}
    for row in rows:
        country = str(row["country"])
        try:
            base_rank[country] = int(row["exploratory_rank"])
            dimensions_scores = row["dimension_scores_0_100"]
            if set(dimensions_scores) != set(dimensions):
                raise KeyError("dimensiones")
            scores[country] = {dimension: Decimal(str(dimensions_scores[dimension])) for dimension in dimensions}
        except (KeyError, ValueError) as error:
            raise ResultsRankingSensitivityError(f"fila de ranking inválida para {country}: {error}") from error

    scenarios: list[dict[str, Any]] = []
    scenario_ranks: dict[str, dict[str, int]] = {}
    scenario_definitions = (("base_all_four", None),) + tuple(
        (f"without_{dimension}", dimension) for dimension in dimensions
    )
    for scenario_id, omitted_dimension in scenario_definitions:
        included = tuple(dimension for dimension in dimensions if dimension != omitted_dimension)
        rank_rows = _rank_scenario(scores, included)
        scenario_ranks[scenario_id] = {row["country"]: row["rank"] for row in rank_rows}
        scenarios.append(
            {
                "id": scenario_id,
                "omitted_dimension": omitted_dimension,
                "included_dimensions": list(included),
                "weights": {dimension: str(Decimal("1") / Decimal(len(included))) for dimension in included},
                "ranking": rank_rows,
            }
        )

    if scenario_ranks["base_all_four"] != base_rank:
        raise ResultsRankingSensitivityError("el escenario base no reproduce el ranking publicado")

    stability = []
    for country in sorted(countries, key=lambda item: base_rank[item]):
        counterfactual_ranks = [scenario_ranks[scenario_id][country] for scenario_id, _ in scenario_definitions[1:]]
        stability.append(
            {
                "country": country,
                "base_rank": base_rank[country],
                "best_rank_without_one_dimension": min(counterfactual_ranks),
                "worst_rank_without_one_dimension": max(counterfactual_ranks),
                "rank_span_without_one_dimension": max(counterfactual_ranks) - min(counterfactual_ranks),
                "scenario_ranks": {scenario_id: scenario_ranks[scenario_id][country] for scenario_id, _ in scenario_definitions},
            }
        )

    payload: dict[str, Any] = {
        "schema_version": "iee-results-ranking-sensitivity-v1",
        "manifest_version": "0.1",
        "status": "experimental-results-ranking-not-iee",
        "calculated_at": calculated_at or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "source_ranking": {"path": ranking_path.as_posix(), "sha256": sha256_hex(ranking_bytes)},
        "method": {
            "name": "omitir una dimensión a la vez",
            "countries": len(countries),
            "base_dimensions": list(dimensions),
            "scenarios": len(scenarios),
            "tie_rule": "desempate visual por código ISO3 para posiciones mostradas",
        },
        "scenarios": scenarios,
        "rank_stability": stability,
        "official_iee": {
            "score": None,
            "ranking": None,
            "publication_eligible": False,
            "blockers": [
                "ranking_measures_results_not_efficiency",
                "sensitivity_is_not_statistical_uncertainty",
                "resources_access_and_equity_not_included",
                "methodological_review_pending",
            ],
        },
    }
    payload_bytes = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        _atomic_write_publication(((Path(output_path), payload_bytes),))
    except IngestionError as error:
        raise ResultsRankingSensitivityError(f"no se pudo publicar la sensibilidad: {error}") from error
    return payload


def _rank_scenario(scores: dict[str, dict[str, Decimal]], dimensions: tuple[str, ...]) -> list[dict[str, Any]]:
    rows = []
    for country, country_scores in scores.items():
        composite = sum((country_scores[dimension] for dimension in dimensions), Decimal("0")) / Decimal(len(dimensions))
        rows.append({"country": country, "score_0_100": str(composite.quantize(Decimal("0.0001")))})
    rows.sort(key=lambda row: (-Decimal(row["score_0_100"]), row["country"]))
    for position, row in enumerate(rows, start=1):
        row["rank"] = position
    return rows
