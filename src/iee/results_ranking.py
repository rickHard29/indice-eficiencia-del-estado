"""Publica un ranking exploratorio de resultados, separado del IEE."""

from __future__ import annotations

import csv
import io
import json
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .ingestion import IngestionError, _atomic_write_publication, sha256_hex


class ResultsRankingError(RuntimeError):
    """Error controlado para el ranking exploratorio de resultados."""


@dataclass(frozen=True)
class RankingPanel:
    id: str
    label: str
    path: Path
    value_column: str
    direction: str
    expected_dimension: str | None


def run_results_ranking(
    config_path: str | Path,
    *,
    output_path: str | Path,
    calculated_at: str | None = None,
) -> dict[str, Any]:
    """Calcula una media de posiciones por resultados y bloquea el IEE oficial."""

    config_file = Path(config_path)
    try:
        config = tomllib.loads(config_file.read_text(encoding="utf-8"))
        panels = tuple(
            RankingPanel(
                id=str(item["id"]),
                label=str(item["label"]),
                path=config_file.parent / str(item["path"]),
                value_column=str(item["value_column"]),
                direction=str(item["direction"]),
                expected_dimension=(str(item["expected_dimension"]) if item.get("expected_dimension") else None),
            )
            for item in config["panels"]
        )
        expected_countries = tuple(str(country) for country in config["expected_countries"])
    except (KeyError, OSError, TypeError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise ResultsRankingError(f"configuración de ranking inválida: {error}") from error

    if (
        str(config.get("version")) != "0.1"
        or str(config.get("schema_version")) != "iee-results-ranking-v1"
        or str(config.get("status")) != "experimental-results-ranking-not-iee"
    ):
        raise ResultsRankingError("contrato de ranking exploratorio incompatible")
    if len(panels) != 4 or len({panel.id for panel in panels}) != 4:
        raise ResultsRankingError("se requieren cuatro resultados únicos")
    if len(expected_countries) != 33 or len(set(expected_countries)) != 33:
        raise ResultsRankingError("el ranking exploratorio requiere exactamente 33 países declarados")

    series = [_read_panel(panel) for panel in panels]
    common = tuple(sorted(set.intersection(*(set(item["values"]) for item in series))))
    if common != tuple(sorted(expected_countries)):
        raise ResultsRankingError("la cobertura calculada no coincide con los 33 países declarados")

    scores = {country: {} for country in common}
    panel_metadata = []
    for item in series:
        normalized = _rank_scores(
            {country: item["values"][country] for country in common}, item["direction"]
        )
        for country, score in normalized.items():
            scores[country][item["id"]] = score
        panel_metadata.append(
            {
                "id": item["id"],
                "label": item["label"],
                "direction": item["direction"],
                "complete_countries": len(item["values"]),
                "source_panel": item["source_panel"],
            }
        )

    rows = []
    for country in common:
        composite = sum(scores[country].values(), Decimal("0")) / Decimal(len(panels))
        raw_values = {item["id"]: str(item["values"][country]) for item in series}
        rows.append(
            {
                "country": country,
                "raw_values": raw_values,
                "dimension_scores_0_100": {key: str(value) for key, value in scores[country].items()},
                "exploratory_results_score_0_100": str(composite.quantize(Decimal("0.0001"))),
            }
        )
    rows.sort(key=lambda row: (-Decimal(row["exploratory_results_score_0_100"]), row["country"]))
    for position, row in enumerate(rows, start=1):
        row["exploratory_rank"] = position

    payload: dict[str, Any] = {
        "schema_version": "iee-results-ranking-v1",
        "manifest_version": "0.1",
        "status": "experimental-results-ranking-not-iee",
        "calculated_at": calculated_at or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "method": {
            "name": "media simple de posiciones normalizadas por dimensión",
            "countries": len(common),
            "weights": {panel.id: "0.25" for panel in panels},
            "tie_rule": "promedio de posiciones; desempate visual por código ISO3",
        },
        "panels": panel_metadata,
        "ranking": rows,
        "official_iee": {
            "score": None,
            "ranking": None,
            "publication_eligible": False,
            "blockers": [
                "ranking_measures_results_not_efficiency",
                "resources_access_and_equity_not_included",
                "methodological_review_pending",
            ],
        },
    }
    payload_bytes = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        _atomic_write_publication(((Path(output_path), payload_bytes),))
    except IngestionError as error:
        raise ResultsRankingError(f"no se pudo publicar el ranking exploratorio: {error}") from error
    return payload


def _read_panel(panel: RankingPanel) -> dict[str, Any]:
    try:
        raw = panel.path.read_bytes()
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
        values = {
            row["entity"]: Decimal(row[panel.value_column])
            for row in rows
            if row.get(panel.value_column, "").strip()
        }
    except (OSError, KeyError, UnicodeDecodeError, csv.Error, ValueError) as error:
        raise ResultsRankingError(f"panel inválido para {panel.id}: {error}") from error
    if not rows or len(values) != len([row for row in rows if row.get(panel.value_column, "").strip()]):
        raise ResultsRankingError(f"valores duplicados o ausentes en {panel.id}")
    if panel.direction not in {"higher", "lower"}:
        raise ResultsRankingError(f"dirección inválida en {panel.id}")
    if panel.expected_dimension and any(row.get("dimension") != panel.expected_dimension for row in rows):
        raise ResultsRankingError(f"dimensión inconsistente en {panel.id}")
    return {
        "id": panel.id,
        "label": panel.label,
        "direction": panel.direction,
        "values": values,
        "source_panel": {"path": panel.path.as_posix(), "sha256": sha256_hex(raw)},
    }


def _rank_scores(values: dict[str, Decimal], direction: str) -> dict[str, Decimal]:
    ordered = sorted(values.items(), key=lambda pair: (pair[1], pair[0]), reverse=direction == "higher")
    positions: dict[str, Decimal] = {}
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        average_position = (Decimal(index + 1) + Decimal(end)) / Decimal("2")
        for country, _ in ordered[index:end]:
            positions[country] = average_position
        index = end
    denominator = Decimal(len(ordered) - 1)
    return {country: (Decimal("100") * (Decimal(len(ordered)) - position) / denominator) for country, position in positions.items()}
