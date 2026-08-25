from pathlib import Path
import tomllib
import unittest

from iee.ingestion import load_download_manifest


class ResultsV03Tests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).parents[1]
        with (root / "config" / "result_sources_v0.3.toml").open("rb") as file:
            self.catalog = tomllib.load(file)
        with (root / "config" / "downloads_results_v0.3.toml").open("rb") as file:
            self.manifest = tomllib.load(file)

    def test_catalog_contains_only_the_automatable_validated_results(self) -> None:
        series = self.catalog["series"]
        self.assertEqual(
            {entry["indicator_id"] for entry in series},
            {"SAL-RES-01", "SAL-ACC-01", "EDU-RES-01", "SEG-RES-01"},
        )
        self.assertTrue(all(entry["status"] == "validated" for entry in series))
        self.assertTrue(all(entry["role"] in {"resultado", "acceso"} for entry in series))

    def test_manifest_keeps_the_full_oecd_frame(self) -> None:
        countries = self.manifest["countries"]
        self.assertEqual(len(countries), 38)
        self.assertEqual(len(countries), len(set(countries)))
        self.assertEqual(countries, sorted(countries))
        self.assertIn("COL", countries)
        self.assertIn("USA", countries)
        for entry in self.manifest["series"]:
            with self.subTest(indicator_id=entry["indicator_id"]):
                self.assertEqual(entry["expected_entities"], countries)
                self.assertEqual(entry["source_status"], "validated")
                self.assertTrue(entry["score_eligible"])
                self.assertIn(entry["direction"], {"higher", "lower"})
                self.assertGreaterEqual(entry["minimum_observations_per_entity"], 1)

    def test_manifest_is_executable_and_matches_its_catalog(self) -> None:
        root = Path(__file__).parents[1]
        loaded = load_download_manifest(root / "config" / "downloads_results_v0.3.toml")
        catalog = {entry["indicator_id"]: entry for entry in self.catalog["series"]}
        self.assertEqual(loaded.version, "0.3")
        self.assertEqual(len(loaded.countries), 38)
        self.assertEqual(len(loaded.series), 4)
        self.assertIsNone(loaded.country_universe)
        for spec in loaded.series:
            with self.subTest(indicator_id=spec.indicator_id):
                self.assertEqual(spec.url, catalog[spec.indicator_id]["exact_url"])
                self.assertEqual(set(spec.expected_latest_year), {"COL", "USA"})


if __name__ == "__main__":
    unittest.main()
