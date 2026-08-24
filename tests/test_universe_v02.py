from pathlib import Path
import tomllib
import unittest


class UniverseV02Tests(unittest.TestCase):
    def setUp(self) -> None:
        path = Path(__file__).parents[1] / "config" / "country_universe_v0.2.toml"
        with path.open("rb") as config_file:
            self.config = tomllib.load(config_file)

    def test_oecd_frame_is_frozen_and_unique(self) -> None:
        countries = self.config["countries"]
        self.assertEqual(self.config["frame"], "OECD-38")
        self.assertEqual(self.config["membership_count"], 38)
        self.assertEqual(len(countries), 38)
        self.assertEqual(len(countries), len(set(countries)))
        self.assertEqual(countries, sorted(countries))
        self.assertIn("COL", countries)
        self.assertIn("USA", countries)

    def test_estimation_fails_closed_by_dimension(self) -> None:
        self.assertEqual(self.config["estimation_sample"], "per-dimension")
        self.assertEqual(self.config["frontier_min_countries"], 30)
        self.assertTrue(self.config["require_complete_indicator_window"])
        self.assertFalse(self.config["allow_imputation_for_eligibility"])

    def test_reference_masks_are_internally_consistent(self) -> None:
        universe = set(self.config["countries"])
        windows = self.config["reference_windows"]
        self.assertEqual(len({window["indicator_id"] for window in windows}), len(windows))
        for window in windows:
            with self.subTest(indicator_id=window["indicator_id"]):
                missing = set(window["missing_complete_window"])
                self.assertTrue(missing <= universe)
                self.assertEqual(
                    window["expected_eligible_countries"],
                    len(universe - missing),
                )
                self.assertGreaterEqual(window["expected_eligible_countries"], 30)
                if window["selection"] == "point":
                    self.assertIn("year", window)
                    self.assertNotIn("start_year", window)
                else:
                    self.assertEqual(window["selection"], "mean")
                    self.assertLessEqual(window["start_year"], window["end_year"])

    def test_input_masks_cover_the_frozen_frame_explicitly(self) -> None:
        universe = set(self.config["countries"])
        masks = self.config["input_masks"]
        self.assertEqual(
            {mask["indicator_id"] for mask in masks},
            {"SAL-IN-02", "EDU-IN-02", "SEG-IN-02", "ADM-IN-02"},
        )
        for mask in masks:
            with self.subTest(indicator_id=mask["indicator_id"]):
                included = set(mask["included_countries"])
                excluded = set(mask["excluded_countries"])
                self.assertFalse(included & excluded)
                self.assertEqual(included | excluded, universe)
                self.assertGreaterEqual(
                    len(included), self.config["frontier_min_countries"]
                )

    def test_accession_candidates_are_sensitivity_only(self) -> None:
        expansion = self.config["sensitivity_expansion"]
        candidates = expansion["countries"]
        self.assertEqual(expansion["status"], "sensitivity_only")
        self.assertEqual(len(candidates), 8)
        self.assertFalse(set(candidates) & set(self.config["countries"]))


if __name__ == "__main__":
    unittest.main()
