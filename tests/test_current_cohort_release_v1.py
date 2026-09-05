import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.current_cohort_release import CurrentCohortReleaseError, run_current_cohort_release


class CurrentCohortReleaseV1Tests(unittest.TestCase):
    def test_closes_the_checked_in_common_cohort_without_a_ranking(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "current.json"
            result = run_current_cohort_release(
                root / "config/current_cohort_release_v1.toml",
                output_path=output,
                calculated_at="2026-09-05T12:00:00+00:00",
            )
            self.assertEqual(result["current_common_cohort"]["complete_countries"], 24)
            self.assertEqual(result["current_common_cohort"]["closure"], "reproducible_current_cut")
            self.assertIsNone(result["aggregate"]["ranking"])
            self.assertFalse(result["aggregate"]["publication_eligible"])
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["manifest_version"], "1.0")

    def test_rejects_a_changed_membership(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            config = Path(temporary) / "bad.toml"
            source = (root / "config/current_cohort_release_v1.toml").read_text(encoding="utf-8")
            source = source.replace(
                '"../data/processed/experimental_cohort_v0.3.json"',
                repr(str(root / "data/processed/experimental_cohort_v0.3.json")),
            ).replace(
                '"../data/processed/review_bundle_v0.4.json"',
                repr(str(root / "data/processed/review_bundle_v0.4.json")),
            )
            config.write_text(source.replace('"AUT"', '"AUS"', 1), encoding="utf-8")
            with self.assertRaisesRegex(CurrentCohortReleaseError, "no coincide"):
                run_current_cohort_release(config, output_path=Path(temporary) / "out.json")
