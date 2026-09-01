from pathlib import Path
import tomllib
import unittest


class PilotSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        config_path = Path(__file__).parents[1] / "config" / "pilot_sources.toml"
        with config_path.open("rb") as config_file:
            self.config = tomllib.load(config_file)
        self.series = self.config["series"]

    def test_catalog_has_one_entry_per_pilot_indicator(self) -> None:
        expected_ids = {
            "SAL-RES-01",
            "SAL-ACC-01",
            "SAL-IN-01",
            "EDU-RES-01",
            "EDU-EQ-01",
            "EDU-IN-01",
            "SEG-RES-01",
            "SEG-EQ-01",
            "SEG-IN-01",
            "ADM-RES-01",
            "ADM-ACC-01",
            "ADM-ACC-02",
            "ADM-IN-01",
        }
        indicator_ids = {entry["indicator_id"] for entry in self.series}
        self.assertEqual(indicator_ids, expected_ids)
        self.assertEqual(len(self.series), len(expected_ids))

    def test_catalog_uses_frozen_validation_date_and_country_pair(self) -> None:
        self.assertEqual(self.config["validation_date"], "2026-08-23")
        self.assertEqual(self.config["countries"], ["COL", "USA"])

    def test_statuses_and_dimensions_are_controlled(self) -> None:
        allowed_statuses = set(self.config["allowed_statuses"])
        actual_statuses = {entry["status"] for entry in self.series}
        self.assertTrue(actual_statuses <= allowed_statuses)
        self.assertEqual(
            {entry["dimension"] for entry in self.series},
            {"salud", "educacion", "seguridad_justicia", "administracion"},
        )
        self.assertTrue(
            {entry["direction"] for entry in self.series} <= {"higher", "lower", "input"}
        )

    def test_each_indicator_keeps_its_expected_role(self) -> None:
        expected_roles = {
            "SAL-RES-01": "resultado",
            "SAL-ACC-01": "acceso",
            "SAL-IN-01": "insumo",
            "EDU-RES-01": "resultado",
            "EDU-EQ-01": "equidad",
            "EDU-IN-01": "insumo",
            "SEG-RES-01": "resultado",
            "SEG-EQ-01": "equidad",
            "SEG-IN-01": "insumo",
            "ADM-RES-01": "resultado",
            "ADM-ACC-01": "acceso",
            "ADM-ACC-02": "acceso",
            "ADM-IN-01": "insumo",
        }
        actual_roles = {entry["indicator_id"]: entry["role"] for entry in self.series}
        self.assertEqual(actual_roles, expected_roles)

    def test_usable_sources_have_traceable_codes_and_urls(self) -> None:
        for entry in self.series:
            if entry["status"] != "design_required":
                with self.subTest(indicator_id=entry["indicator_id"]):
                    self.assertTrue(entry["official_code"].strip())
                    self.assertTrue(entry["exact_url"].startswith("https://"))
                    self.assertIn("latest_col_year", entry)
                    self.assertIn("latest_usa_year", entry)

    def test_derived_indicators_record_all_dependency_urls(self) -> None:
        by_id = {entry["indicator_id"]: entry for entry in self.series}
        for indicator_id in {"SEG-IN-01", "ADM-IN-01"}:
            urls = by_id[indicator_id]["dependency_urls"]
            self.assertTrue(urls)
            self.assertTrue(all(url.startswith("https://") for url in urls))

    def test_public_summary_matches_catalog_status_counts(self) -> None:
        project_root = Path(__file__).parents[1]
        readme = (project_root / "README.md").read_text(encoding="utf-8")
        validation_note = (project_root / "docs" / "source-validation.md").read_text(
            encoding="utf-8"
        )
        for fragment in {
            "6 indicadores validados",
            "3 condicionales",
            "2 en reserva",
            "2 que requieren diseño",
        }:
            self.assertIn(fragment, readme)
        self.assertIn("6 validados, 3 condicionales, 2 en reserva", validation_note)
        self.assertIn("2 que requieren diseño", validation_note)

    def test_status_count_matches_review_decision(self) -> None:
        counts = {
            status: sum(entry["status"] == status for entry in self.series)
            for status in self.config["allowed_statuses"]
        }
        self.assertEqual(
            counts,
            {
                "validated": 6,
                "conditional": 3,
                "reserve": 2,
                "design_required": 2,
            },
        )


if __name__ == "__main__":
    unittest.main()
