import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.experimental_readiness import (
    ExperimentalReadinessError,
    load_experimental_readiness_config,
    run_experimental_readiness,
)


class ExperimentalReadinessV02Tests(unittest.TestCase):
    def test_packages_four_tracks_without_creating_a_score_or_ranking(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._write_fixture(root)

            result = run_experimental_readiness(
                config,
                output_path=root / "release.json",
                calculated_at="2026-09-03T12:00:00+00:00",
            )

            self.assertEqual(result["dimensions_with_experimental_track"], 4)
            self.assertIsNone(result["aggregate"]["experimental_score"])
            self.assertIsNone(result["aggregate"]["ranking"])
            self.assertFalse(result["aggregate"]["publication_eligible"])
            publication = json.loads((root / "release.json").read_text(encoding="utf-8"))
            self.assertEqual(publication["evidence"][0]["complete_countries"], 35)
            self.assertEqual(publication["evidence"][3]["complete_countries"], 30)

    def test_rejects_an_official_gate_before_writing_a_release(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._write_fixture(root, official=True)

            with self.assertRaisesRegex(ExperimentalReadinessError, "no segura"):
                run_experimental_readiness(config, output_path=root / "release.json")
            self.assertFalse((root / "release.json").exists())

    def test_loads_the_checked_in_manifest(self) -> None:
        root = Path(__file__).resolve().parents[1]
        config = load_experimental_readiness_config(root / "config/experimental_release_v0.2.toml")
        self.assertEqual(config.minimum_countries, 30)
        self.assertEqual(len(config.evidence), 4)

    def _write_fixture(self, root: Path, official: bool = False) -> Path:
        for identifier, dimension, complete in (
            ("education", "educacion", 35),
            ("health", "salud", 34),
            ("admin", "administracion", 34),
        ):
            (root / f"{identifier}.csv").write_text(
                "dimension,label,countries_in_frame,complete_pairs,frontier_min_countries,"
                "experimental_sample_eligible,official_frontier_eligible,official_iee_score,flags\n"
                f"{dimension},Example,38,{complete},30,true,{'true' if official else 'false'},,experimental_only\n",
                encoding="utf-8",
            )
        (root / "security.json").write_text(
            json.dumps(
                {
                    "complete_all_roles": 30,
                    "countries_in_frame": 38,
                    "integration_sample_eligible": True,
                    "official_iee_score": None,
                }
            ),
            encoding="utf-8",
        )
        config = root / "release.toml"
        config.write_text(
            '''version = "0.2"
schema_version = "iee-experimental-readiness-v1"
status = "experimental-not-for-publication"
countries_in_frame = 38
minimum_countries = 30

[[evidence]]
id = "educacion"
label = "Educación"
kind = "frontier_gate_csv"
gate = "education.csv"
expected_dimension = "educacion"

[[evidence]]
id = "salud"
label = "Salud"
kind = "frontier_gate_csv"
gate = "health.csv"
expected_dimension = "salud"

[[evidence]]
id = "administracion"
label = "Administración"
kind = "frontier_gate_csv"
gate = "admin.csv"
expected_dimension = "administracion"

[[evidence]]
id = "seguridad_justicia"
label = "Seguridad y justicia"
kind = "role_coverage_gate_json"
gate = "security.json"
''',
            encoding="utf-8",
        )
        return config
