"""Mide un núcleo común de resultados sin presentarlo como eficiencia."""

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


class OutcomesCoreCohortError(RuntimeError):
    """Error controlado para el núcleo de resultados comparables."""


@dataclass(frozen=True)
class OutcomePanel:
    id: str
    label: str
    path: Path
    result_value_column: str
    expected_dimension: str | None


def run_outcomes_core_cohort(
    config_path: str | Path,
    *,
    output_path: str | Path,
    calculated_at: str | None = None,
) -> dict[str, Any]:
    """Publica solo la intersección de resultados, sin puntajes ni ranking."""

    config_file = Path(config_path)
    try:
        raw = config_file.read_bytes()
        config = tomllib.loads(raw.decode("utf-8"))
        universe = tomllib.loads(
            (config_file.parent / str(config["country_universe"])).read_text(encoding="utf-8")
        )
        panels = tuple(
            OutcomePanel(
                id=str(item["id"]),
                label=str(item["label"]),
                path=config_file.parent / str(item["path"]),
                result_value_column=str(item["result_value_column"]),
                expected_dimension=(
                    str(item["expected_dimension"])
                    if item.get("expected_dimension") is not None
                    else None
                ),
            )
            for item in config["panels"]
        )
        expected_countries = tuple(str(country) for country in config["expected_countries"])
    except (KeyError, OSError, TypeError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise OutcomesCoreCohortError(f"configuración de núcleo de resultados inválida: {error}") from error

    countries = tuple(str(country) for country in universe["countries"])
    if (
        str(config.get("version")) != "1.0"
        or str(config.get("schema_version")) != "iee-outcomes-core-cohort-v1"
        or str(config.get("status")) != "outcomes-only-not-efficiency"
    ):
        raise OutcomesCoreCohortError("contrato de núcleo de resultados incompatible")
    if len(countries) != 38 or len(countries) != len(set(countries)):
        raise OutcomesCoreCohortError("universo OCDE-38 inválido")
    if len(panels) != 4 or len({panel.id for panel in panels}) != 4:
        raise OutcomesCoreCohortError("se requieren cuatro paneles de resultado únicos")
    if len(expected_countries) < 30 or len(expected_countries) != len(set(expected_countries)):
        raise OutcomesCoreCohortError("el núcleo esperado debe contener al menos 30 países únicos")

    records = [_read_panel(panel, set(countries)) for panel in panels]
    members = {record["id"]: set(record.pop("members")) for record in records}
    common = tuple(sorted(set.intersection(*members.values())))
    if common != tuple(sorted(expected_countries)):
        raise OutcomesCoreCohortError("el núcleo calculado no coincide con el corte declarado")

    payload: dict[str, Any] = {
        "schema_version": "iee-outcomes-core-cohort-v1",
        "manifest_version": "1.0",
        "status": "outcomes-only-not-efficiency",
        "calculated_at": calculated_at
        or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "countries_in_frame": len(countries),
        "outcome_panels": records,
        "outcomes_core": {
            "countries": list(common),
            "complete_countries": len(common),
            "minimum_countries": 30,
            "minimum_met": len(common) >= 30,
            "missing_by_outcome": {
                panel.id: sorted(set(countries) - members[panel.id]) for panel in panels
            },
        },
        "aggregate": {
            "experimental_score": None,
            "official_iee_score": None,
            "ranking": None,
            "publication_eligible": False,
            "blockers": [
                "resources_not_included",
                "access_and_equity_not_included",
                "outcomes_core_is_not_efficiency_index",
            ],
        },
    }
    payload_bytes = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    try:
        _atomic_write_publication(((Path(output_path), payload_bytes),))
    except IngestionError as error:
        raise OutcomesCoreCohortError(f"no se pudo publicar el núcleo de resultados: {error}") from error
    return payload


def _read_panel(panel: OutcomePanel, universe: set[str]) -> dict[str, Any]:
    try:
        raw = panel.path.read_bytes()
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
        members = [row["entity"] for row in rows if row.get(panel.result_value_column, "").strip()]
    except (OSError, KeyError, UnicodeDecodeError, csv.Error) as error:
        raise OutcomesCoreCohortError(f"panel de resultado inválido para {panel.id}: {error}") from error
    if not rows or len(members) != len(set(members)) or not set(members) <= universe:
        raise OutcomesCoreCohortError(f"membresías inconsistentes en {panel.id}")
    if panel.expected_dimension is not None and any(
        row.get("dimension") != panel.expected_dimension for row in rows
    ):
        raise OutcomesCoreCohortError(f"dimensión inconsistente en {panel.id}")
    return {
        "id": panel.id,
        "label": panel.label,
        "complete_countries": len(members),
        "source_panel": {"path": panel.path.as_posix(), "sha256": sha256_hex(raw)},
        "members": members,
    }
