import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.experimental_cohort import (
    ExperimentalCohortError,
    load_experimental_cohort_config,
    run_experimental_cohort,
)


class ExperimentalCohortV03Tests(unittest.TestCase):
    def test_reports_the_intersection_without_opening_an_aggregate_gate(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._write_fixture(root)

            result = run_experimental_cohort(
                config,
                output_path=root / "cohort.json",
                calculated_at="2026-09-03T12:00:00+00:00",
            )

            common = result["common_cohort"]
            self.assertEqual(common["countries"], ["A", "B"])
            self.assertFalse(common["experimental_aggregate_eligible"])
            self.assertIsNone(result["aggregate"]["ranking"])
            publication = json.loads((root / "cohort.json").read_text(encoding="utf-8"))
            self.assertIn("common_cohort_below_minimum", publication["aggregate"]["blockers"])

    def test_rejects_duplicate_members_before_writing(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._write_fixture(root, duplicate=True)

            with self.assertRaisesRegex(ExperimentalCohortError, "membresías inconsistentes"):
                run_experimental_cohort(config, output_path=root / "cohort.json")
            self.assertFalse((root / "cohort.json").exists())

    def test_loads_the_checked_in_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        config = load_experimental_cohort_config(root / "config/experimental_cohort_v0.3.toml")
        self.assertEqual(config.minimum_countries, 30)
        self.assertEqual(len(config.panels), 4)

    def test_v04_creates_a_separate_24_country_exploratory_gate(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            result = run_experimental_cohort(
                root / "config/experimental_cohort_v0.4.toml",
                output_path=Path(temporary) / "cohort-v04.json",
                calculated_at="2026-09-05T21:00:00+00:00",
            )

        self.assertEqual(result["manifest_version"], "0.4")
        self.assertEqual(result["minimum_countries"], 24)
        self.assertEqual(result["common_cohort"]["complete_countries"], 24)
        self.assertTrue(result["common_cohort"]["experimental_aggregate_eligible"])
        self.assertIsNone(result["aggregate"]["official_iee_score"])
        self.assertIsNone(result["aggregate"]["ranking"])

    def _write_fixture(self, root: Path, duplicate: bool = False) -> Path:
        countries = ["A", "B", "C", "D", "E", "F", *[f"X{number:02}" for number in range(1, 33)]]
        (root / "universe.toml").write_text(
            "countries = [" + ", ".join(f'"{country}"' for country in countries) + "]\n",
            encoding="utf-8",
        )
        fixtures = {
            "education": ["A", "B", "C"],
            "health": ["A", "B", "D"],
            "admin": ["A", "B", "E"],
            "security": ["A", "B", "F"],
        }
        for name, members in fixtures.items():
            marker = "all_roles_complete" if name == "security" else "sample_member"
            columns = ["entity", marker]
            if name != "security":
                columns.append("dimension")
            with (root / f"{name}.csv").open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=columns)
                writer.writeheader()
                extra = ["A"] if duplicate and name == "education" else []
                for member in members + extra:
                    row = {"entity": member, marker: "true"}
                    if name != "security":
                        row["dimension"] = {
                            "education": "educacion",
                            "health": "salud",
                            "admin": "administracion",
                        }[name]
                    writer.writerow(row)
        config = root / "cohort.toml"
        config.write_text(
            '''version = "0.3"
schema_version = "iee-experimental-cohort-v1"
status = "experimental-not-for-publication"
country_universe = "universe.toml"
minimum_countries = 3

[[panels]]
id = "educacion"
label = "Educación"
path = "education.csv"
membership_column = "sample_member"
expected_dimension = "educacion"

[[panels]]
id = "salud"
label = "Salud"
path = "health.csv"
membership_column = "sample_member"
expected_dimension = "salud"

[[panels]]
id = "administracion"
label = "Administración"
path = "admin.csv"
membership_column = "sample_member"
expected_dimension = "administracion"

[[panels]]
id = "seguridad_justicia"
label = "Seguridad y justicia"
path = "security.csv"
membership_column = "all_roles_complete"
''',
            encoding="utf-8",
        )
        return config
