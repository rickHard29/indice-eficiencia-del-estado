import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.recovery_source_screen import RecoverySourceScreenError, run_recovery_source_screen


class RecoverySourceScreenV05Tests(unittest.TestCase):
    def test_records_six_rejections_without_changing_the_cohort(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._write_config(root)
            result = run_recovery_source_screen(config, output_path=root / "screen.json")
            self.assertEqual(len(result["candidates"]), 6)
            self.assertEqual(result["adopted_candidates"], 0)
            self.assertEqual(result["cohort_change"], 0)
            self.assertIsNone(result["aggregate"]["ranking"])

    def test_rejects_a_candidate_marked_as_adopted(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._write_config(root).read_text(encoding="utf-8").replace(
                'decision = "not_adopted_incomplete_window"', 'decision = "adopted"', 1
            )
            (root / "screen.toml").write_text(config, encoding="utf-8")
            with self.assertRaisesRegex(RecoverySourceScreenError, "candidata inválida"):
                run_recovery_source_screen(root / "screen.toml", output_path=root / "screen.json")
            self.assertFalse((root / "screen.json").exists())

    def _write_config(self, root: Path) -> Path:
        candidates = []
        for country in ("AUS", "BEL", "CAN", "DEU", "GRC", "ISL"):
            candidates.append(
                f'''[[candidates]]
country = "{country}"
dimension = "example"
source_url = "https://example.org/{country}"
decision = "not_adopted_incomplete_window"
rationale = "Incomplete evidence."
'''
            )
        path = root / "screen.toml"
        path.write_text(
            '''version = "0.5"
schema_version = "iee-recovery-source-screen-v1"
status = "experimental-not-for-publication"

'''
            + "\n".join(candidates),
            encoding="utf-8",
        )
        return path
