import csv
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from iee.experimental_scoring import (
    ExperimentalScoringError,
    load_experiment_config,
    run_experiment,
)


PROJECT_ROOT = Path(__file__).parents[1]
REPOSITORY_CONFIG = PROJECT_ROOT / "config" / "scoring_experiment.toml"
CATALOG = PROJECT_ROOT / "config" / "pilot_sources.toml"
METHODOLOGY = PROJECT_ROOT / "config" / "methodology.toml"
FIXED_TIME = "2026-08-24T12:00:00+00:00"
EXPECTED_SENSITIVITY_SCENARIOS = {
    "arithmetic_aggregation",
    "result_weight_minus_25pct",
    "result_weight_plus_25pct",
    "health_pre_pandemic_2017_2019",
    "avoidable_mortality_cap_400",
    "avoidable_mortality_cap_600",
    "pisa_gap_cap_110",
    "pisa_gap_cap_120",
    "pisa_gap_cap_200",
    "homicide_cap_30",
    "homicide_cap_75",
    "homicide_mean_linear",
    "homicide_point_2023_log1p",
    "exclude_sampling_caution",
}

CSV_FIELDS = [
    "entity",
    "period",
    "indicator_id",
    "value",
    "direction",
    "unit",
    "source_id",
    "series_code",
    "source_status",
    "score_eligible",
    "observation_status",
    "observation_kind",
    "resource_id",
]

SERIES = {
    "SAL-RES-01": {
        "direction": "lower",
        "unit": "Muertes evitables estandarizadas por edad por 100.000 habitantes",
        "source_id": "OECD-HEALTH",
        "source_status": "validated",
        "score_eligible": True,
        "observation_kind": "reported",
        "series_code": "DSD_HEALTH_STAT@DF_AM | AVM | DT_10P5HB | _T | STANDARD",
    },
    "SAL-ACC-01": {
        "direction": "higher",
        "unit": "Índice de cobertura de servicios esenciales, 0 a 100",
        "source_id": "WHO-UHC",
        "source_status": "validated",
        "score_eligible": True,
        "observation_kind": "reported",
        "series_code": "SH_UHC_SCI",
    },
    "SAL-IN-01": {
        "direction": "input",
        "unit": "Dólares internacionales corrientes por habitante",
        "source_id": "WHO-GHED",
        "source_status": "conditional",
        "score_eligible": False,
        "observation_kind": "reported",
        "series_code": "SH.XPD.GHED.PP.CD",
    },
    "EDU-RES-01": {
        "direction": "higher",
        "unit": "Puntaje armonizado en unidades equivalentes a TIMSS",
        "source_id": "WB-HCI",
        "source_status": "validated",
        "score_eligible": True,
        "observation_kind": "reported",
        "series_code": "HD.HCI.HLOS | source=63",
    },
    "EDU-EQ-01": {
        "direction": "lower",
        "unit": "Puntos PISA",
        "source_id": "OECD-PISA",
        "source_status": "validated",
        "score_eligible": True,
        "observation_kind": "manual_control",
        "series_code": "Diferencia en matemáticas entre cuartiles superior e inferior de ESCS",
    },
    "SEG-RES-01": {
        "direction": "lower",
        "unit": "Víctimas por 100.000 habitantes",
        "source_id": "UNODC-WDI",
        "source_status": "validated",
        "score_eligible": True,
        "observation_kind": "reported",
        "series_code": "VC.IHR.PSRC.P5",
    },
    "SEG-IN-01": {
        "direction": "input",
        "unit": "Dólares internacionales corrientes por habitante, serie derivada",
        "source_id": "OECD-COFOG",
        "source_status": "reserve",
        "score_eligible": False,
        "observation_kind": "derived",
        "series_code": "DSD_NASEC10@DF_TABLE11 | S13 | OTE | GF03 | V",
    },
    "ADM-RES-01": {
        "direction": "higher",
        "unit": "Índice de 0 a 1",
        "source_id": "UN-EGDI",
        "source_status": "validated",
        "score_eligible": True,
        "observation_kind": "manual_control",
        "series_code": "OSI | Technical Appendix Table 7",
    },
    "ADM-IN-01": {
        "direction": "input",
        "unit": "Porcentaje del PIB",
        "source_id": "OECD-COFOG",
        "source_status": "conditional",
        "score_eligible": False,
        "observation_kind": "derived",
        "series_code": "100 × (D1 + P2 in S13/GF01) / B1GQ",
    },
}


def _row(
    entity: str,
    period: int,
    indicator_id: str,
    value: float,
    *,
    observation_status: str = "observed",
) -> dict[str, str]:
    metadata = SERIES[indicator_id]
    return {
        "entity": entity,
        "period": str(period),
        "indicator_id": indicator_id,
        "value": str(value),
        "direction": str(metadata["direction"]),
        "unit": str(metadata["unit"]),
        "source_id": str(metadata["source_id"]),
        "series_code": str(metadata["series_code"]),
        "source_status": str(metadata["source_status"]),
        "score_eligible": str(metadata["score_eligible"]).lower(),
        "observation_status": observation_status,
        "observation_kind": str(metadata["observation_kind"]),
        "resource_id": indicator_id.lower(),
    }


def _fixture_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    mortality = {
        "COL": {2017: 252, 2018: 253, 2019: 247, 2020: 328, 2021: 419},
        "USA": {2017: 275, 2018: 270, 2019: 267, 2020: 328, 2021: 363},
    }
    homicide = {
        "COL": {2021: 25.5801274, 2022: 24.9488076, 2023: 24.9134420},
        "USA": {2021: 6.7797220, 2022: 6.5126743, 2023: 5.7634079},
    }
    administration_input = {
        "COL": {2022: 1.985, 2023: 1.990486, 2024: 1.843968},
        "USA": {2022: 1.556808, 2023: 1.518381, 2024: 1.511817},
    }
    for entity in ("COL", "USA"):
        for year, value in mortality[entity].items():
            rows.append(_row(entity, year, "SAL-RES-01", value))
        rows.append(_row(entity, 2021, "SAL-ACC-01", 82 if entity == "COL" else 87))
        rows.append(_row(entity, 2024, "SAL-IN-01", 1226 if entity == "COL" else 7269))
        rows.append(_row(entity, 2020, "EDU-RES-01", 419.02753 if entity == "COL" else 511.79868))
        rows.append(
            _row(
                entity,
                2022,
                "EDU-EQ-01",
                79 if entity == "COL" else 102,
                observation_status=(
                    "observed" if entity == "COL" else "source:sampling_caution"
                ),
            )
        )
        for year, value in homicide[entity].items():
            rows.append(_row(entity, year, "SEG-RES-01", value))
        rows.append(_row(entity, 2024, "SEG-IN-01", 430.63 if entity == "COL" else 1551.23))
        rows.append(_row(entity, 2024, "ADM-RES-01", 0.7521 if entity == "COL" else 0.9136))
        for year, value in administration_input[entity].items():
            rows.append(
                _row(
                    entity,
                    year,
                    "ADM-IN-01",
                    value,
                    observation_status=(
                        "provisional" if entity == "COL" and year >= 2023 else "observed"
                    ),
                )
            )
    return sorted(rows, key=lambda row: (row["entity"], int(row["period"]), row["indicator_id"]))


def _csv_bytes(
    rows: list[dict[str, str]],
    fieldnames: list[str] | None = None,
) -> bytes:
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames or CSV_FIELDS,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def _records(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


class ExperimentalScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.config_path = self.root / "scoring_experiment.toml"
        self.observations_path = self.root / "pilot_observations.csv"
        self.ingestion_receipt_path = self.root / "pilot_provenance.json"
        self.indicator_path = self.root / "indicator_diagnostics.csv"
        self.diagnostic_path = self.root / "diagnostics.csv"
        self.sensitivity_path = self.root / "sensitivity.csv"
        self.context_path = self.root / "context.csv"
        self.provenance_path = self.root / "experimental_provenance.json"
        (self.root / "pilot_sources.toml").write_bytes(CATALOG.read_bytes())
        (self.root / "methodology.toml").write_bytes(METHODOLOGY.read_bytes())
        self.rows = _fixture_rows()
        self._prepare()
        network_guard = patch(
            "socket.create_connection",
            side_effect=AssertionError("las pruebas experimentales no pueden usar internet"),
        )
        network_guard.start()
        self.addCleanup(network_guard.stop)

    @property
    def output_paths(self) -> tuple[Path, ...]:
        return (
            self.indicator_path,
            self.diagnostic_path,
            self.sensitivity_path,
            self.context_path,
            self.provenance_path,
        )

    def _prepare(
        self,
        rows: list[dict[str, str]] | None = None,
        *,
        configured_sha256: str | None = None,
        receipt_sha256: str | None = None,
        receipt_records: int | None = None,
        csv_fields: list[str] | None = None,
    ) -> str:
        current_rows = self.rows if rows is None else rows
        payload = _csv_bytes(current_rows, csv_fields)
        source_hash = hashlib.sha256(payload).hexdigest()
        self.observations_path.write_bytes(payload)

        config_text = REPOSITORY_CONFIG.read_text(encoding="utf-8")
        replacement_hash = configured_sha256 or source_hash
        config_text, replacements = re.subn(
            r'^input_sha256 = "[0-9a-f]{64}"$',
            f'input_sha256 = "{replacement_hash}"',
            config_text,
            count=1,
            flags=re.MULTILINE,
        )
        self.assertEqual(replacements, 1)
        self.config_path.write_text(config_text, encoding="utf-8")

        receipt = {
            "schema_version": "iee-observations-v1",
            "retrieved_at": "2026-08-23T20:01:56+00:00",
            "catalog": {
                "path": "pilot_sources.toml",
                "sha256": hashlib.sha256(CATALOG.read_bytes()).hexdigest(),
            },
            "countries": ["COL", "USA"],
            "processed": {
                "path": self.observations_path.as_posix(),
                "records": len(current_rows) if receipt_records is None else receipt_records,
                "sha256": receipt_sha256 or source_hash,
            },
        }
        self.ingestion_receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return source_hash

    def _run(self):
        return run_experiment(
            self.config_path,
            observations_path=self.observations_path,
            ingestion_provenance_path=self.ingestion_receipt_path,
            indicator_path=self.indicator_path,
            diagnostic_path=self.diagnostic_path,
            sensitivity_path=self.sensitivity_path,
            context_path=self.context_path,
            provenance_path=self.provenance_path,
            calculated_at=FIXED_TIME,
        )

    def _assert_nothing_published(self) -> None:
        self.assertTrue(all(not path.exists() for path in self.output_paths))

    def test_repository_configuration_is_explicitly_experimental(self) -> None:
        config = load_experiment_config(REPOSITORY_CONFIG)

        self.assertEqual(config.status, "experimental-not-for-publication")
        self.assertEqual(config.countries, ("COL", "USA"))
        self.assertEqual(config.frontier_min_countries, 30)
        self.assertTrue(all(not dimension.input_compatible for dimension in config.dimensions))
        self.assertEqual(
            {scenario.id for scenario in config.sensitivity},
            EXPECTED_SENSITIVITY_SCENARIOS,
        )

    def test_controlled_run_is_deterministic_and_hashes_every_output(self) -> None:
        first = self._run()
        first_bytes = {path.name: path.read_bytes() for path in self.output_paths}
        second = self._run()
        second_bytes = {path.name: path.read_bytes() for path in self.output_paths}

        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual(first.output_sha256, second.output_sha256)
        self.assertEqual(first.indicator_count, 12)
        self.assertEqual(first.diagnostic_count, 10)
        self.assertEqual(first.sensitivity_count, 150)
        self.assertEqual(first.context_count, 8)
        self.assertEqual(first.official_iee_score, None)
        self.assertFalse(first.publication_eligible)
        output_mapping = {
            "indicators": self.indicator_path,
            "diagnostics": self.diagnostic_path,
            "sensitivity": self.sensitivity_path,
            "context": self.context_path,
        }
        for name, path in output_mapping.items():
            with self.subTest(output=name):
                expected_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(first.output_sha256[name], expected_hash)
                self.assertRegex(expected_hash, r"^[0-9a-f]{64}$")
        provenance = json.loads(self.provenance_path.read_text(encoding="utf-8"))
        self.assertEqual(provenance["calculated_at"], FIXED_TIME)
        for name, expected_hash in first.output_sha256.items():
            self.assertEqual(provenance["outputs"][name]["sha256"], expected_hash)

        indicators = {
            (row["entity"], row["indicator_id"]): row
            for row in _records(self.indicator_path)
        }
        self.assertEqual(indicators[("COL", "EDU-RES-01")]["bound_status"], "technical_scale")
        self.assertEqual(indicators[("COL", "SAL-ACC-01")]["bound_status"], "natural_scale")
        self.assertEqual(indicators[("COL", "ADM-RES-01")]["bound_status"], "natural_scale")
        self.assertTrue(indicators[("COL", "EDU-RES-01")]["bound_reference"])

    def test_official_scores_and_publication_gates_remain_null(self) -> None:
        result = self._run()
        diagnostics = _records(self.diagnostic_path)
        provenance = json.loads(self.provenance_path.read_text(encoding="utf-8"))

        self.assertIsNone(result.official_iee_score)
        self.assertFalse(result.publication_eligible)
        self.assertTrue(all(row["official_iee_score"] == "" for row in diagnostics))
        self.assertTrue(all(row["publication_eligible"] == "false" for row in diagnostics))
        self.assertTrue(all(row["frontier_eligible"] == "false" for row in diagnostics))
        self.assertTrue(all(0.0 <= float(row["coverage"]) <= 1.0 for row in diagnostics))
        for row in diagnostics:
            flags = set(row["flags"].split(";"))
            self.assertIn("official_iee_null", flags)
            self.assertIn("publication_blocked", flags)
        composite_rows = [row for row in diagnostics if row["level"] == "composite"]
        self.assertTrue(all("ranking_blocked" in row["flags"] for row in composite_rows))
        self.assertTrue(all(row["coverage"] == "0.5" for row in composite_rows))
        gate = provenance["publication_gate"]
        self.assertIsNone(gate["official_iee_score"])
        self.assertFalse(gate["publication_eligible"])
        self.assertFalse(gate["ranking_eligible"])
        self.assertEqual(len(gate["reasons"]), 4)

    def test_dimension_coverage_and_missing_roles_are_explicit(self) -> None:
        self._run()
        rows = {
            (row["entity"], row["component_id"]): row
            for row in _records(self.diagnostic_path)
            if row["level"] == "dimension"
        }
        for entity in ("COL", "USA"):
            self.assertEqual(rows[(entity, "salud")]["coverage"], "0.75")
            self.assertEqual(rows[(entity, "salud")]["missing_roles"], "equidad")
            self.assertEqual(rows[(entity, "educacion")]["coverage"], "0.75")
            self.assertEqual(rows[(entity, "educacion")]["missing_roles"], "acceso")
            self.assertEqual(rows[(entity, "seguridad_justicia")]["coverage"], "0.5")
            self.assertEqual(
                rows[(entity, "seguridad_justicia")]["missing_roles"], "acceso;equidad"
            )
            self.assertEqual(rows[(entity, "administracion")]["coverage"], "0.5")
            self.assertIn("coverage_below_075", rows[(entity, "administracion")]["flags"])

    def test_sensitivity_scenarios_are_complete_and_base_delta_is_zero(self) -> None:
        self._run()
        rows = _records(self.sensitivity_path)
        by_scenario: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            by_scenario.setdefault(row["scenario_id"], []).append(row)

        self.assertEqual(set(by_scenario), {"base"} | EXPECTED_SENSITIVITY_SCENARIOS)
        self.assertTrue(
            all(len(rows_for_scenario) == 10 for rows_for_scenario in by_scenario.values())
        )
        self.assertTrue(all(float(row["delta_from_base"]) == 0.0 for row in by_scenario["base"]))

    def test_health_window_and_pisa_cap_change_the_diagnostic_signal(self) -> None:
        self._run()
        rows = _records(self.sensitivity_path)
        lookup = {
            (row["scenario_id"], row["entity"], row["level"], row["component_id"]): float(
                row["diagnostic_score"]
            )
            for row in rows
        }

        base_col = lookup[("base", "COL", "dimension", "salud")]
        base_usa = lookup[("base", "USA", "dimension", "salud")]
        pre_col = lookup[
            ("health_pre_pandemic_2017_2019", "COL", "dimension", "salud")
        ]
        pre_usa = lookup[
            ("health_pre_pandemic_2017_2019", "USA", "dimension", "salud")
        ]
        self.assertLess(base_col, base_usa)
        self.assertGreater(pre_col, pre_usa)

        pre_pandemic_rows = [
            row
            for row in rows
            if row["scenario_id"] == "health_pre_pandemic_2017_2019"
            and (row["component_id"] == "salud" or row["level"] == "composite")
        ]
        for row in pre_pandemic_rows:
            flags = set(row["flags"].split(";"))
            self.assertNotIn("pandemic_sensitive", flags)
            self.assertIn("pandemic_window_excluded", flags)

        cap_110_col = lookup[("pisa_gap_cap_110", "COL", "dimension", "educacion")]
        cap_110_usa = lookup[("pisa_gap_cap_110", "USA", "dimension", "educacion")]
        cap_120_col = lookup[("pisa_gap_cap_120", "COL", "dimension", "educacion")]
        cap_120_usa = lookup[("pisa_gap_cap_120", "USA", "dimension", "educacion")]
        self.assertGreater(cap_110_col, cap_110_usa)
        self.assertLess(cap_120_col, cap_120_usa)

        for entity in ("COL", "USA"):
            mortality_cap_400 = lookup[
                ("avoidable_mortality_cap_400", entity, "dimension", "salud")
            ]
            mortality_cap_600 = lookup[
                ("avoidable_mortality_cap_600", entity, "dimension", "salud")
            ]
            homicide_cap_30 = lookup[
                ("homicide_cap_30", entity, "dimension", "seguridad_justicia")
            ]
            homicide_cap_75 = lookup[
                ("homicide_cap_75", entity, "dimension", "seguridad_justicia")
            ]
            homicide_mean_linear = lookup[
                ("homicide_mean_linear", entity, "dimension", "seguridad_justicia")
            ]
            homicide_point = lookup[
                (
                    "homicide_point_2023_log1p",
                    entity,
                    "dimension",
                    "seguridad_justicia",
                )
            ]
            self.assertLess(mortality_cap_400, mortality_cap_600)
            self.assertLess(homicide_cap_30, homicide_cap_75)
            self.assertNotEqual(homicide_mean_linear, homicide_cap_75)
            self.assertNotEqual(homicide_point, homicide_cap_75)

    def test_weight_sensitivity_does_not_move_single_role_dimensions(self) -> None:
        self._run()
        rows = _records(self.sensitivity_path)
        for row in rows:
            if (
                row["scenario_id"] in {
                    "result_weight_minus_25pct",
                    "result_weight_plus_25pct",
                }
                and row["level"] == "dimension"
                and row["component_id"] in {"seguridad_justicia", "administracion"}
            ):
                self.assertAlmostEqual(float(row["delta_from_base"]), 0.0)

    def test_pisa_sampling_caution_propagates_and_can_be_excluded(self) -> None:
        self._run()
        indicators = {
            (row["entity"], row["indicator_id"]): row for row in _records(self.indicator_path)
        }
        self.assertIn(
            "source_sampling_caution",
            indicators[("USA", "EDU-EQ-01")]["flags"].split(";"),
        )
        self.assertEqual(
            indicators[("USA", "EDU-EQ-01")]["observation_statuses"],
            "source:sampling_caution",
        )

        rows = _records(self.sensitivity_path)
        base_usa = next(
            row
            for row in rows
            if row["scenario_id"] == "base"
            and row["entity"] == "USA"
            and row["level"] == "dimension"
            and row["component_id"] == "educacion"
        )
        excluded_usa = next(
            row
            for row in rows
            if row["scenario_id"] == "exclude_sampling_caution"
            and row["entity"] == "USA"
            and row["level"] == "dimension"
            and row["component_id"] == "educacion"
        )
        self.assertIn("source_sampling_caution", base_usa["flags"].split(";"))
        self.assertNotIn("source_sampling_caution", excluded_usa["flags"].split(";"))
        self.assertIn("missing_required_role:equidad", excluded_usa["flags"].split(";"))
        excluded_education = [
            row
            for row in rows
            if row["scenario_id"] == "exclude_sampling_caution"
            and row["level"] == "dimension"
            and row["component_id"] == "educacion"
        ]
        self.assertEqual({row["entity"] for row in excluded_education}, {"COL", "USA"})
        for row in excluded_education:
            flags = set(row["flags"].split(";"))
            self.assertIn("globally_excluded_indicator:EDU-EQ-01", flags)
            self.assertIn("missing_required_role:equidad", flags)

    def test_context_is_never_scored_and_missing_education_input_is_null(self) -> None:
        self._run()
        rows = _records(self.context_path)
        self.assertTrue(all(row["input_compatible"] == "false" for row in rows))
        self.assertTrue(all("not_scored" in row["flags"].split(";") for row in rows))
        education = [row for row in rows if row["dimension"] == "educacion"]
        self.assertEqual(len(education), 2)
        self.assertTrue(all(row["value"] == "" for row in education))
        self.assertTrue(
            all("input_not_materialized" in row["flags"].split(";") for row in education)
        )
        colombia_administration = next(
            row
            for row in rows
            if row["entity"] == "COL" and row["dimension"] == "administracion"
        )
        self.assertIn("provisional", colombia_administration["flags"].split(";"))

    def test_incomplete_input_window_becomes_null_context_not_zero(self) -> None:
        rows = [
            row
            for row in self.rows
            if not (
                row["entity"] == "COL"
                and row["indicator_id"] == "ADM-IN-01"
                and row["period"] == "2023"
            )
        ]
        self._prepare(rows)
        self._run()

        context = next(
            row
            for row in _records(self.context_path)
            if row["entity"] == "COL" and row["dimension"] == "administracion"
        )
        self.assertEqual(context["value"], "")
        self.assertEqual(context["period_start"], "")
        flags = set(context["flags"].split(";"))
        self.assertIn("input_window_incomplete", flags)
        self.assertIn("input_not_materialized", flags)

    def test_rejects_snapshot_changed_after_configuration_freeze(self) -> None:
        self._prepare(configured_sha256="0" * 64)

        with self.assertRaisesRegex(ExperimentalScoringError, "snapshot normalizado difiere"):
            self._run()
        self._assert_nothing_published()

    def test_rejects_ingestion_receipt_hash_mismatch(self) -> None:
        self._prepare(receipt_sha256="f" * 64)

        with self.assertRaisesRegex(ExperimentalScoringError, "hash del CSV no coincide"):
            self._run()
        self._assert_nothing_published()

    def test_rejects_ingestion_receipt_record_count_mismatch(self) -> None:
        self._prepare(receipt_records=len(self.rows) + 1)

        with self.assertRaisesRegex(ExperimentalScoringError, "conteo del CSV no coincide"):
            self._run()
        self._assert_nothing_published()

    def test_incomplete_base_window_aborts_without_partial_publication(self) -> None:
        rows = [
            row
            for row in self.rows
            if not (
                row["entity"] == "COL"
                and row["indicator_id"] == "SAL-RES-01"
                and row["period"] == "2020"
            )
        ]
        self._prepare(rows)

        with self.assertRaisesRegex(
            ExperimentalScoringError,
            r"ventana incompleta en SAL-RES-01/COL",
        ):
            self._run()
        self._assert_nothing_published()

    def test_incomplete_sensitivity_window_aborts_without_partial_publication(self) -> None:
        rows = [
            row
            for row in self.rows
            if not (
                row["entity"] == "COL"
                and row["indicator_id"] == "SAL-RES-01"
                and row["period"] == "2017"
            )
        ]
        self._prepare(rows)

        with self.assertRaisesRegex(
            ExperimentalScoringError,
            r"ventana incompleta en SAL-RES-01/COL",
        ):
            self._run()
        self._assert_nothing_published()

    def test_duplicate_normalized_key_is_rejected(self) -> None:
        rows = self.rows + [dict(self.rows[0])]
        self._prepare(rows)

        with self.assertRaisesRegex(ExperimentalScoringError, "clave duplicada"):
            self._run()
        self._assert_nothing_published()

    def test_noneligible_result_observation_is_rejected(self) -> None:
        rows = [dict(row) for row in self.rows]
        target = next(
            row
            for row in rows
            if row["entity"] == "USA"
            and row["indicator_id"] == "SEG-RES-01"
            and row["period"] == "2022"
        )
        target["score_eligible"] = "false"
        self._prepare(rows)

        with self.assertRaisesRegex(ExperimentalScoringError, "elegibilidad inconsistente"):
            self._run()
        self._assert_nothing_published()

    def test_receipt_lineage_must_match_schema_catalog_and_countries(self) -> None:
        cases = (
            (
                "schema",
                lambda receipt: receipt.__setitem__("schema_version", "wrong-schema"),
                "esquema del recibo",
            ),
            (
                "catalog",
                lambda receipt: receipt["catalog"].__setitem__("sha256", "0" * 64),
                "catálogo del recibo",
            ),
            (
                "countries",
                lambda receipt: receipt.__setitem__("countries", ["USA", "COL"]),
                "países del recibo",
            ),
        )
        for name, mutate, expected_error in cases:
            with self.subTest(lineage=name):
                self._prepare()
                receipt = json.loads(
                    self.ingestion_receipt_path.read_text(encoding="utf-8")
                )
                mutate(receipt)
                self.ingestion_receipt_path.write_text(
                    json.dumps(receipt, ensure_ascii=False, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ExperimentalScoringError, expected_error):
                    self._run()
                self._assert_nothing_published()

    def test_csv_identity_must_match_catalog_for_both_countries(self) -> None:
        for field, bad_value in (
            ("unit", "unidad alterada"),
            ("source_id", "fuente-alterada"),
            ("series_code", "código-alterado"),
        ):
            with self.subTest(field=field):
                rows = [dict(row) for row in self.rows]
                target = next(
                    row
                    for row in rows
                    if row["entity"] == "USA" and row["indicator_id"] == "SAL-ACC-01"
                )
                target[field] = bad_value
                self._prepare(rows)
                with self.assertRaisesRegex(ExperimentalScoringError, f"{field} difiere"):
                    self._run()
                self._assert_nothing_published()

    def test_unconfigured_eligible_series_and_incomplete_schema_are_rejected(self) -> None:
        extra = dict(self.rows[0])
        extra.update(
            {
                "period": "2024",
                "indicator_id": "SEG-EQ-01",
                "score_eligible": "true",
            }
        )
        self._prepare(self.rows + [extra])
        with self.assertRaisesRegex(ExperimentalScoringError, "fuera del experimento"):
            self._run()
        self._assert_nothing_published()

        self._prepare(csv_fields=[field for field in CSV_FIELDS if field != "resource_id"])
        with self.assertRaisesRegex(ExperimentalScoringError, "faltan columnas normalizadas"):
            self._run()
        self._assert_nothing_published()

    def test_invalid_experimental_parameters_fail_during_config_load(self) -> None:
        cases = (
            (
                "point_without_year",
                'override_selection = "mean"',
                'override_selection = "point"',
                "falta año puntual alternativo",
            ),
            (
                "negative_role_weight",
                "resultado = 0.50",
                "resultado = -0.50",
                "pesos de roles deben ser positivos",
            ),
            (
                "reversed_input_window",
                "input_start_year = 2022",
                "input_start_year = 2025",
                "ventana de insumo inválida",
            ),
            (
                "duplicate_official_role",
                'official_roles = ["resultado", "acceso", "equidad"]',
                'official_roles = ["resultado", "resultado", "acceso", "equidad"]',
                "official_roles debe contener roles únicos",
            ),
            (
                "orphan_override",
                'id = "arithmetic_aggregation"',
                'id = "arithmetic_aggregation"\noverride_upper_bound = 120.0',
                "override sin indicador objetivo",
            ),
        )
        for name, original, replacement, expected_error in cases:
            with self.subTest(parameter=name):
                self._prepare()
                config_text = self.config_path.read_text(encoding="utf-8")
                self.assertIn(original, config_text)
                self.config_path.write_text(
                    config_text.replace(original, replacement, 1),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ExperimentalScoringError, expected_error):
                    load_experiment_config(self.config_path)

    def test_five_file_publication_rolls_back_as_a_unit(self) -> None:
        old_content = {
            path: f"old:{path.name}".encode("utf-8") for path in self.output_paths
        }
        for path, content in old_content.items():
            path.write_bytes(content)

        from iee.ingestion import os as ingestion_os

        real_replace = ingestion_os.replace
        replace_calls = 0

        def fail_on_third_replace(source, destination):
            nonlocal replace_calls
            replace_calls += 1
            if replace_calls == 3:
                raise OSError("simulated publication failure")
            return real_replace(source, destination)

        with patch("iee.ingestion.os.replace", side_effect=fail_on_third_replace):
            with self.assertRaisesRegex(
                ExperimentalScoringError,
                "no se pudo publicar el diagnóstico",
            ):
                self._run()

        for path, content in old_content.items():
            with self.subTest(path=path.name):
                self.assertEqual(path.read_bytes(), content)

    def test_output_paths_cannot_collide_with_inputs_or_each_other(self) -> None:
        common_arguments = {
            "observations_path": self.observations_path,
            "ingestion_provenance_path": self.ingestion_receipt_path,
            "sensitivity_path": self.sensitivity_path,
            "context_path": self.context_path,
            "provenance_path": self.provenance_path,
            "calculated_at": FIXED_TIME,
        }
        with self.subTest(collision="input"):
            with self.assertRaisesRegex(
                ExperimentalScoringError,
                "salida no puede sobrescribir una entrada",
            ):
                run_experiment(
                    self.config_path,
                    indicator_path=self.observations_path,
                    diagnostic_path=self.diagnostic_path,
                    **common_arguments,
                )
        with self.subTest(collision="another output"):
            with self.assertRaisesRegex(
                ExperimentalScoringError,
                "rutas de salida deben ser únicas",
            ):
                run_experiment(
                    self.config_path,
                    indicator_path=self.indicator_path,
                    diagnostic_path=self.indicator_path,
                    **common_arguments,
                )
        self._assert_nothing_published()


if __name__ == "__main__":
    unittest.main()
