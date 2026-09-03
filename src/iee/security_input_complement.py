"""Combina de forma trazable el insumo OECD de seguridad con Canadá."""

from __future__ import annotations

import json
import tomllib
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from .experimental_scoring import SourceObservation, read_normalized_observations
from .ingestion import IngestionError, _atomic_write_publication, observations_to_csv, sha256_hex


class SecurityInputComplementError(RuntimeError):
    """Error controlado al crear el complemento multifuente."""


def run_security_input_complement(
    config_path: str | Path,
    *,
    base_observations_path: str | Path,
    base_provenance_path: str | Path,
    canada_observations_path: str | Path,
    canada_provenance_path: str | Path,
    processed_path: str | Path,
    provenance_path: str | Path,
    calculated_at: str | None = None,
) -> int:
    """Publica SEG-IN-04 sin sustituir ninguna observación de origen."""

    config_file = Path(config_path)
    try:
        config_bytes = config_file.read_bytes()
        config = tomllib.loads(config_bytes.decode("utf-8"))
        universe = tomllib.loads(
            (config_file.parent / str(config["country_universe"])).read_text(encoding="utf-8")
        )
        catalog_path = config_file.parent / str(config["catalog"])
        catalog_bytes = catalog_path.read_bytes()
        countries = tuple(str(country) for country in universe["countries"])
        canada_entity = str(config["canada_entity"])
        base_entities = tuple(str(country) for country in config["base_countries"])
        base_indicator = str(config["base_indicator_id"])
        canada_indicator = str(config["canada_indicator_id"])
        composite_indicator = str(config["composite_indicator_id"])
        start_year, end_year = int(config["start_year"]), int(config["end_year"])
        source_id = str(config["source_id"])
        series_code = str(config["series_code"])
        unit = str(config["unit"])
    except (KeyError, OSError, TypeError, ValueError, tomllib.TOMLDecodeError) as error:
        raise SecurityInputComplementError(f"configuración de complemento inválida: {error}") from error

    if (
        len(countries) != 38
        or canada_entity not in countries
        or canada_entity in base_entities
        or not set(base_entities) < set(countries)
        or end_year < start_year
    ):
        raise SecurityInputComplementError("universo o ventana del complemento inválidos")
    base_bytes, base_rows = _read_snapshot(base_observations_path, base_provenance_path)
    canada_bytes, canada_rows = _read_snapshot(canada_observations_path, canada_provenance_path)
    periods = tuple(range(start_year, end_year + 1))
    selected_base = _select_complete(
        base_rows, base_indicator, base_entities, periods, "insumo OECD"
    )
    selected_canada = _select_complete(
        canada_rows, canada_indicator, (canada_entity,), periods, "insumo canadiense"
    )
    composite_rows = [
        replace(
            row,
            indicator_id=composite_indicator,
            source_id=source_id,
            series_code=series_code,
            unit=unit,
            resource_id="seg-in-04-composite",
        )
        for row in [*selected_base, *selected_canada]
    ]
    processed_bytes = observations_to_csv(composite_rows)
    processed_hash = sha256_hex(processed_bytes)
    timestamp = calculated_at or datetime.now(UTC).replace(microsecond=0).isoformat()
    provenance = {
        "schema_version": "iee-observations-v1",
        "manifest_version": str(config["version"]),
        "countries": list(countries),
        "catalog": {"path": catalog_path.as_posix(), "sha256": sha256_hex(catalog_bytes)},
        "configuration": {"path": config_file.as_posix(), "sha256": sha256_hex(config_bytes)},
        "retrieved_at": timestamp,
        "sources_by_country": {
            "OECD-COFOG-WDI-PPP": list(base_entities),
            "STATCAN-CCOFOG-WDI-PPP": [canada_entity],
        },
        "inputs": {
            "oecd_snapshot_sha256": sha256_hex(base_bytes),
            "canada_snapshot_sha256": sha256_hex(canada_bytes),
        },
        "processed": {
            "path": Path(processed_path).as_posix(),
            "records": len(composite_rows),
            "sha256": processed_hash,
        },
    }
    provenance_bytes = (
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    try:
        _atomic_write_publication(
            ((Path(processed_path), processed_bytes), (Path(provenance_path), provenance_bytes))
        )
    except IngestionError as error:
        raise SecurityInputComplementError(f"no se pudo publicar el complemento: {error}") from error
    return len(composite_rows)


def _read_snapshot(
    observations_path: str | Path, provenance_path: str | Path
) -> tuple[bytes, list[SourceObservation]]:
    try:
        observations = Path(observations_path).read_bytes()
        receipt = json.loads(Path(provenance_path).read_text(encoding="utf-8"))
        if receipt["schema_version"] != "iee-observations-v1":
            raise SecurityInputComplementError("esquema de recibo incompatible")
        if receipt["processed"]["sha256"] != sha256_hex(observations):
            raise SecurityInputComplementError("hash de snapshot inconsistente")
        return observations, read_normalized_observations(observations)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise SecurityInputComplementError(f"no se pudo validar snapshot: {error}") from error


def _select_complete(
    rows: list[SourceObservation],
    indicator_id: str,
    entities: tuple[str, ...],
    periods: tuple[int, ...],
    label: str,
) -> list[SourceObservation]:
    selected: list[SourceObservation] = []
    for entity in entities:
        matches = sorted(
            (
                row for row in rows
                if row.entity == entity and row.indicator_id == indicator_id and row.period in periods
            ),
            key=lambda row: row.period,
        )
        if tuple(row.period for row in matches) != periods:
            raise SecurityInputComplementError(f"{label} incompleto para {entity}")
        if any(
            row.direction != "input"
            or row.source_status != "conditional"
            or row.score_eligible
            for row in matches
        ):
            raise SecurityInputComplementError(f"{label} con identidad no elegible para {entity}")
        selected.extend(matches)
    return selected
