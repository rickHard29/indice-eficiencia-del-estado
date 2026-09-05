from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.recovery_resolution import RecoveryResolutionError, run_recovery_resolution


class RecoveryResolutionV07Tests(unittest.TestCase):
    def test_closes_all_three_routes_without_adopting_data(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            result = run_recovery_resolution(
                root / "config/recovery_resolution_v0.7.toml", output_path=Path(temporary) / "out.json"
            )
        self.assertTrue(result["technical_cycle_complete"])
        self.assertEqual(result["adopted_observations"], 0)
        self.assertEqual(result["cohort"]["after"], 24)
        self.assertIsNone(result["aggregate"]["ranking"])

    def test_rejects_an_artificial_cohort_gain(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = Path(__file__).resolve().parents[1] / "config/recovery_resolution_v0.7.toml"
            bad = source.read_text(encoding="utf-8").replace("common_cohort_after = 24", "common_cohort_after = 25")
            config = root / "bad.toml"
            config.write_text(bad, encoding="utf-8")
            with self.assertRaisesRegex(RecoveryResolutionError, "no puede alterar la cohorte"):
                run_recovery_resolution(config, output_path=root / "out.json")
