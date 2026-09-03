import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.cohort_recovery import CohortRecoveryError, run_cohort_recovery


class CohortRecoveryV03Tests(unittest.TestCase):
    def test_prioritizes_single_missing_component_before_larger_gaps(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._write_fixture(root)

            result = run_cohort_recovery(
                config,
                output_path=root / "recovery.json",
                calculated_at="2026-09-03T12:00:00+00:00",
            )

            self.assertEqual(result["countries_needed"], 2)
            self.assertEqual([item["country"] for item in result["first_wave"]], ["C28", "C29"])
            self.assertEqual(result["first_wave"][0]["missing_dimensions"], ["seguridad"])
            self.assertIsNone(result["aggregate"]["ranking"])

    def test_rejects_a_cohort_that_contains_a_ranking(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._write_fixture(root, ranking=True)

            with self.assertRaisesRegex(CohortRecoveryError, "ranking"):
                run_cohort_recovery(config, output_path=root / "recovery.json")
            self.assertFalse((root / "recovery.json").exists())

    def _write_fixture(self, root: Path, ranking: bool = False) -> Path:
        countries = [f"C{number:02}" for number in range(38)]
        common = countries[:28]
        missing = {
            "educacion": countries[30:],
            "salud": countries[31:],
            "administracion": countries[32:],
            "seguridad": countries[28:30] + countries[33:],
        }
        receipt = {
            "schema_version": "iee-experimental-cohort-v1",
            "countries_in_frame": 38,
            "common_cohort": {"countries": common, "missing_by_dimension": missing},
            "aggregate": {"ranking": ["bad"] if ranking else None},
        }
        (root / "cohort.json").write_text(json.dumps(receipt), encoding="utf-8")
        (root / "recovery.toml").write_text(
            '''version = "0.3"
schema_version = "iee-cohort-recovery-v1"
status = "experimental-not-for-publication"
cohort_receipt = "cohort.json"
target_minimum_countries = 30
max_first_wave = 6
''',
            encoding="utf-8",
        )
        return root / "recovery.toml"
