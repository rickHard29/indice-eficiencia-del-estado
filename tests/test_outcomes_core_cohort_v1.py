from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.outcomes_core_cohort import OutcomesCoreCohortError, run_outcomes_core_cohort


class OutcomesCoreCohortV1Tests(unittest.TestCase):
    def test_materializes_33_comparable_outcomes_without_efficiency(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            result = run_outcomes_core_cohort(
                root / "config/outcomes_core_cohort_v1.toml",
                output_path=Path(temporary) / "core.json",
                calculated_at="2026-09-05T12:00:00+00:00",
            )
        self.assertEqual(result["outcomes_core"]["complete_countries"], 33)
        self.assertTrue(result["outcomes_core"]["minimum_met"])
        self.assertIsNone(result["aggregate"]["ranking"])
        self.assertFalse(result["aggregate"]["publication_eligible"])

    def test_rejects_a_declared_country_that_is_not_in_the_intersection(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            config = Path(temporary) / "bad.toml"
            source = (root / "config/outcomes_core_cohort_v1.toml").read_text(encoding="utf-8")
            source = source.replace(
                'country_universe = "country_universe_v2.9.toml"',
                f'country_universe = "{root / "config/country_universe_v2.9.toml"}"',
            )
            source = source.replace("../data/processed/", f"{root}/data/processed/")
            config.write_text(source.replace('"AUS"', '"BEL"', 1), encoding="utf-8")
            with self.assertRaisesRegex(OutcomesCoreCohortError, "no coincide"):
                run_outcomes_core_cohort(config, output_path=Path(temporary) / "out.json")
