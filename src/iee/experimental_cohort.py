"""Mide la cohorte común de cortes experimentales sin agregar indicadores."""

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


class ExperimentalCohortError(RuntimeError):
    """Error controlado al examinar la cohorte común experimental."""


@dataclass(frozen=True)
class CohortPanelSpec:
    id: str
    label: str
    path: Path
    membership_column: str
    expected_dimension: str | None


@dataclass(frozen=True)
class ExperimentalCohortConfig:
    path: Path
    version: str
    schema_version: str
    status: str
    countries: tuple[str, ...]
    minimum_countries: int
    panels: tuple[CohortPanelSpec, ...]


def load_experimental_cohort_config(path: str | Path) -> ExperimentalCohortConfig:
    """Carga un contrato de intersección, no un contrato de puntajes."""

    config_path = Path(path)
    try:
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
        universe = tomllib.loads(
            (config_path.parent / str(raw["country_universe"])).read_text(encoding="utf-8")
        )
        panels = tuple(
            CohortPanelSpec(
                id=str(item["id"]),
                label=str(item["label"]),
                path=config_path.parent / str(item["path"]),
                membership_column=str(item["membership_column"]),
                expected_dimension=(
                    str(item["expected_dimension"])
                    if item.get("expected_dimension") is not None
                    else None
                ),
            )
            for item in raw["panels"]
        )
        config = ExperimentalCohortConfig(
            path=config_path,
            version=str(raw["version"]),
            schema_version=str(raw["schema_version"]),
            status=str(raw["status"]),
            countries=tuple(str(country) for country in universe["countries"]),
            minimum_countries=int(raw["minimum_countries"]),
            panels=panels,
        )
    except (KeyError, OSError, TypeError, ValueError, tomllib.TOMLDecodeError) as error:
        raise ExperimentalCohortError(f"configuración de cohorte inválida: {error}") from error

    allowed_contracts = {
        "0.3": "experimental-not-for-publication",
        "0.4": "experimental-cohort-24-not-for-publication",
    }
    if config.version not in allowed_contracts or config.schema_version != "iee-experimental-cohort-v1":
        raise ExperimentalCohortError("versión o esquema de cohorte incompatible")
    if config.status != allowed_contracts[config.version]:
        raise ExperimentalCohortError("la cohorte debe bloquear publicación")
    if len(config.countries) != 38 or len(config.countries) != len(set(config.countries)):
        raise ExperimentalCohortError("el universo OCDE-38 no es válido")
    if not 3 <= config.minimum_countries <= len(config.countries):
        raise ExperimentalCohortError("mínimo de cohorte inválido")
    if config.version == "0.4" and config.minimum_countries != 24:
        raise ExperimentalCohortError("la cohorte exploratoria v0.4 debe conservar el mínimo de 24")
    ids = [panel.id for panel in config.panels]
    if len(config.panels) != 4 or len(ids) != len(set(ids)):
        raise ExperimentalCohortError("se requieren cuatro paneles de dimensión únicos")
    return config


def run_experimental_cohort(
    config_path: str | Path,
    *,
    output_path: str | Path,
    calculated_at: str | None = None,
) -> dict[str, Any]:
    """Publica la intersección y los faltantes sin calcular eficiencia."""

    config = load_experimental_cohort_config(config_path)
    panel_records = [_read_panel(panel, set(config.countries)) for panel in config.panels]
    samples = {record["id"]: set(record.pop("members")) for record in panel_records}
    common = set.intersection(*samples.values())
    payload = {
        "schema_version": config.schema_version,
        "manifest_version": config.version,
        "status": config.status,
        "calculated_at": calculated_at
        or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "countries_in_frame": len(config.countries),
        "minimum_countries": config.minimum_countries,
        "panels": panel_records,
        "common_cohort": {
            "countries": sorted(common),
            "complete_countries": len(common),
            "experimental_aggregate_eligible": len(common) >= config.minimum_countries,
            "missing_by_dimension": {
                panel.id: sorted(set(config.countries) - samples[panel.id]) for panel in config.panels
            },
        },
        "aggregate": {
            "experimental_score": None,
            "official_iee_score": None,
            "ranking": None,
            "publication_eligible": False,
            "blockers": [
                "common_cohort_below_minimum"
                if len(common) < config.minimum_countries
                else "methodology_v1_not_frozen",
                "conditional_inputs_remain",
                "open_methodological_review_pending",
            ],
        },
    }
    payload_bytes = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    try:
        _atomic_write_publication(((Path(output_path), payload_bytes),))
    except IngestionError as error:
        raise ExperimentalCohortError(f"no se pudo publicar la cohorte: {error}") from error
    return payload


def _read_panel(panel: CohortPanelSpec, universe: set[str]) -> dict[str, Any]:
    try:
        panel_bytes = panel.path.read_bytes()
        rows = list(csv.DictReader(io.StringIO(panel_bytes.decode("utf-8"))))
        members = [row["entity"] for row in rows if row[panel.membership_column] == "true"]
    except (OSError, KeyError, UnicodeDecodeError, csv.Error) as error:
        raise ExperimentalCohortError(f"panel inválido para {panel.id}: {error}") from error
    if not rows or len(members) != len(set(members)) or not set(members) <= universe:
        raise ExperimentalCohortError(f"membresías inconsistentes en {panel.id}")
    if panel.expected_dimension is not None and any(
        row.get("dimension") != panel.expected_dimension for row in rows
    ):
        raise ExperimentalCohortError(f"dimensión inconsistente en {panel.id}")
    return {
        "id": panel.id,
        "label": panel.label,
        "complete_countries": len(members),
        "source_panel": {"path": panel.path.as_posix(), "sha256": sha256_hex(panel_bytes)},
        "members": members,
    }
