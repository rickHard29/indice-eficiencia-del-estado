from pathlib import Path
import tomllib
import unittest

from iee.ingestion import load_download_manifest


class ContextV04Tests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).parents[1]
        with (root / "config" / "context_sources_v0.4.toml").open("rb") as file:
            self.catalog = tomllib.load(file)
        with (root / "config" / "downloads_context_v0.4.toml").open("rb") as file:
            self.manifest = tomllib.load(file)

    def test_catalog_keeps_context_separate_from_scores_and_resources(self) -> None:
        series = self.catalog["series"]
        self.assertEqual({item["indicator_id"] for item in series}, {"CTX-AGE-01", "CTX-DENS-01"})
        self.assertTrue(all(item["role"] == "contexto" for item in series))
        self.assertTrue(all(item["direction"] == "input" for item in series))
        self.assertTrue(all(item["status"] == "validated" for item in series))
        self.assertEqual({item["transform"] for item in series}, {"linear", "log1p"})

    def test_manifest_freezes_full_oecd_frame_and_annual_coverage(self) -> None:
        countries = self.manifest["countries"]
        self.assertEqual(len(countries), 38)
        self.assertEqual(countries, sorted(countries))
        self.assertIn("COL", countries)
        self.assertIn("USA", countries)
        for series in self.manifest["series"]:
            with self.subTest(indicator_id=series["indicator_id"]):
                self.assertEqual(series["expected_entities"], countries)
                self.assertEqual(series["direction"], "input")
                self.assertFalse(series["score_eligible"])
                self.assertEqual(series["minimum_observations_per_entity"], 14)
                self.assertEqual(series["expected_latest_year"], {"COL": 2023, "USA": 2023})

    def test_manifest_matches_frozen_catalog(self) -> None:
        root = Path(__file__).parents[1]
        loaded = load_download_manifest(root / "config" / "downloads_context_v0.4.toml")
        catalog = {item["indicator_id"]: item for item in self.catalog["series"]}
        self.assertEqual(loaded.version, "0.4")
        self.assertEqual(len(loaded.countries), 38)
        self.assertEqual(len(loaded.series), 2)
        for spec in loaded.series:
            with self.subTest(indicator_id=spec.indicator_id):
                entry = catalog[spec.indicator_id]
                self.assertEqual(spec.url, entry["exact_url"])
                self.assertEqual(spec.series_code, entry["official_code"])
                self.assertFalse(spec.score_eligible)


if __name__ == "__main__":
    unittest.main()
