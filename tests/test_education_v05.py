from __future__ import annotations

from pathlib import Path
import tomllib
import unittest

from iee.ingestion import load_download_manifest


ROOT = Path(__file__).resolve().parents[1]


class EducationV05Tests(unittest.TestCase):
    def test_manifest_freezes_three_roles_and_pisa_masks(self) -> None:
        manifest = load_download_manifest(ROOT / "config/downloads_education_v0.5.toml")

        self.assertEqual(len(manifest.countries), 38)
        specs = {spec.indicator_id: spec for spec in manifest.series}
        self.assertEqual(set(specs), {"EDU-RES-01", "EDU-ACC-02", "EDU-EQ-01"})
        self.assertEqual(len(specs["EDU-RES-01"].expected_entities), 38)
        self.assertEqual(len(specs["EDU-ACC-02"].expected_entities), 37)
        self.assertEqual(len(specs["EDU-EQ-01"].expected_entities), 36)
        self.assertNotIn("LUX", specs["EDU-ACC-02"].expected_entities)
        self.assertNotIn("CRI", specs["EDU-EQ-01"].expected_entities)
        self.assertEqual(specs["EDU-ACC-02"].adapter, "oecd_pisa_xlsx")
        self.assertEqual(specs["EDU-EQ-01"].value_column, "T")

    def test_catalog_records_temporal_gap_and_validated_roles(self) -> None:
        catalog = tomllib.loads((ROOT / "config/education_sources_v0.5.toml").read_text())
        series = {entry["indicator_id"]: entry for entry in catalog["series"]}

        self.assertEqual({entry["role"] for entry in series.values()}, {"resultado", "acceso", "equidad"})
        self.assertTrue(all(entry["status"] == "validated" for entry in series.values()))
        self.assertEqual(series["EDU-RES-01"]["reference_year"], 2020)
        self.assertEqual(series["EDU-ACC-02"]["reference_year"], 2022)
        self.assertEqual(series["EDU-EQ-01"]["reference_year"], 2022)

