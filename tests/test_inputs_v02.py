from pathlib import Path
from tempfile import TemporaryDirectory
import tomllib
import unittest

from iee.ingestion import IngestionError, load_download_manifest


class InputsV02Tests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).parents[1]
        with (root / "config" / "country_universe_v0.2.toml").open("rb") as file:
            self.universe = tomllib.load(file)
        with (root / "config" / "input_sources_v0.2.toml").open("rb") as file:
            self.catalog = tomllib.load(file)
        with (root / "config" / "downloads_inputs_v0.2.toml").open("rb") as file:
            self.manifest = tomllib.load(file)

    def test_four_dimensions_share_one_constant_ppp_unit(self) -> None:
        series = self.catalog["series"]
        self.assertEqual(len(series), 4)
        self.assertEqual(
            {entry["dimension"] for entry in series},
            {"salud", "educacion", "seguridad_justicia", "administracion"},
        )
        self.assertEqual(
            {entry["unit"] for entry in series},
            {"Dólares internacionales constantes de 2021 por habitante"},
        )
        self.assertTrue(all(entry["status"] == "conditional" for entry in series))

    def test_manifest_uses_subsets_without_trimming_the_universe(self) -> None:
        universe = set(self.universe["countries"])
        self.assertEqual(self.manifest["countries"], self.universe["countries"])
        by_id = {entry["indicator_id"]: entry for entry in self.manifest["series"]}
        self.assertEqual(set(by_id["SAL-IN-02"]["expected_entities"]), universe)
        self.assertEqual(set(by_id["EDU-IN-02"]["expected_entities"]), universe)
        for indicator_id in {"SEG-IN-02", "ADM-IN-02"}:
            expected = set(by_id[indicator_id]["expected_entities"])
            self.assertEqual(universe - expected, {"CAN", "MEX", "NZL", "TUR"})
            self.assertGreaterEqual(len(expected), self.universe["frontier_min_countries"])

    def test_inputs_are_context_until_methodology_approves_them(self) -> None:
        for entry in self.manifest["series"]:
            with self.subTest(indicator_id=entry["indicator_id"]):
                self.assertEqual(entry["direction"], "input")
                self.assertFalse(entry["score_eligible"])
                self.assertEqual(entry["source_status"], "conditional")
                self.assertTrue(entry["url"].startswith("https://"))
                self.assertTrue(entry["level_url"].startswith("https://"))
                self.assertEqual(
                    set(entry["expected_latest_year"]),
                    {"COL", "USA"},
                )

    def test_executable_manifest_matches_the_catalog(self) -> None:
        root = Path(__file__).parents[1]
        manifest = load_download_manifest(root / "config" / "downloads_inputs_v0.2.toml")
        self.assertEqual(len(manifest.countries), 38)
        self.assertEqual(len(manifest.series), 4)
        self.assertEqual(
            {len(spec.expected_entities) for spec in manifest.series},
            {34, 38},
        )
        self.assertIsNotNone(manifest.country_universe)
        assert manifest.country_universe is not None
        self.assertEqual(manifest.country_universe.frame, "OECD-38")
        self.assertEqual(len(manifest.country_universe.input_masks), 4)
        self.assertTrue(manifest.country_universe.sha256)
        self.assertTrue(all(spec.reference_year == 2023 for spec in manifest.series))

    def test_catalog_freezes_primary_and_dependency_urls(self) -> None:
        root = Path(__file__).parents[1]
        catalog = {entry["indicator_id"]: entry for entry in self.catalog["series"]}
        manifest = load_download_manifest(root / "config" / "downloads_inputs_v0.2.toml")
        for spec in manifest.series:
            with self.subTest(indicator_id=spec.indicator_id):
                self.assertEqual(spec.url, catalog[spec.indicator_id]["exact_url"])

        with TemporaryDirectory() as directory:
            temporary = Path(directory)
            for filename in (
                "downloads_inputs_v0.2.toml",
                "input_sources_v0.2.toml",
                "country_universe_v0.2.toml",
            ):
                source = root / "config" / filename
                (temporary / filename).write_bytes(source.read_bytes())
            manifest_path = temporary / "downloads_inputs_v0.2.toml"
            original = self.manifest["series"][0]["level_url"]
            text = manifest_path.read_text(encoding="utf-8").replace(
                f'level_url = "{original}"',
                'level_url = "https://example.test/changed-level"',
                1,
            )
            manifest_path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(IngestionError, "dependencias difieren"):
                load_download_manifest(manifest_path)

        with TemporaryDirectory() as directory:
            temporary = Path(directory)
            for filename in (
                "downloads_inputs_v0.2.toml",
                "input_sources_v0.2.toml",
                "country_universe_v0.2.toml",
            ):
                source = root / "config" / filename
                (temporary / filename).write_bytes(source.read_bytes())
            manifest_path = temporary / "downloads_inputs_v0.2.toml"
            original = self.manifest["series"][0]["url"]
            text = manifest_path.read_text(encoding="utf-8").replace(
                f'url = "{original}"',
                'url = "https://example.test/changed-primary"',
                1,
            )
            manifest_path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(IngestionError, "URL automática difiere"):
                load_download_manifest(manifest_path)

    def test_universe_masks_are_enforced_by_the_manifest_loader(self) -> None:
        root = Path(__file__).parents[1]
        with TemporaryDirectory() as directory:
            temporary = Path(directory)
            for filename in (
                "downloads_inputs_v0.2.toml",
                "input_sources_v0.2.toml",
                "country_universe_v0.2.toml",
            ):
                source = root / "config" / filename
                (temporary / filename).write_bytes(source.read_bytes())
            universe_path = temporary / "country_universe_v0.2.toml"
            text = universe_path.read_text(encoding="utf-8").replace(
                'excluded_countries = ["CAN", "MEX", "NZL", "TUR"]',
                'excluded_countries = ["MEX", "NZL", "TUR"]',
                1,
            )
            universe_path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(IngestionError, "máscara de países inválida"):
                load_download_manifest(temporary / "downloads_inputs_v0.2.toml")


if __name__ == "__main__":
    unittest.main()
