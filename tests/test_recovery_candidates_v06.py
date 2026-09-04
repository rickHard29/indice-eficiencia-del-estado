from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.recovery_candidates import RecoveryCandidatesError, run_recovery_candidates


class RecoveryCandidatesV06Tests(unittest.TestCase):
    def test_checked_in_registry_keeps_candidates_separate_from_adoption(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            result = run_recovery_candidates(root / "config/recovery_candidates_v0.6.toml", output_path=Path(temporary) / "out.json")
        self.assertEqual(sum(row["status"] == "candidate_for_materialization" for row in result["candidates"]), 3)
        self.assertEqual(result["adopted_observations"], 0)
        self.assertIsNone(result["aggregate"]["ranking"])

    def test_rejects_incorrect_candidate_balance(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = Path(__file__).resolve().parents[1] / "config/recovery_candidates_v0.6.toml"
            bad = source.read_text(encoding="utf-8").replace("candidate_for_materialization", "blocked")
            config = root / "bad.toml"
            config.write_text(bad, encoding="utf-8")
            with self.assertRaisesRegex(RecoveryCandidatesError, "tres candidatas"):
                run_recovery_candidates(config, output_path=root / "out.json")
