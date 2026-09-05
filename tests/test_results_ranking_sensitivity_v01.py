from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.results_ranking_sensitivity import ResultsRankingSensitivityError, run_results_ranking_sensitivity


class ResultsRankingSensitivityV01Tests(unittest.TestCase):
    def test_materializes_leave_one_dimension_out_stability_without_iee(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            result = run_results_ranking_sensitivity(
                root / "config/results_ranking_sensitivity_v0.1.toml",
                output_path=Path(temporary) / "sensitivity.json",
                calculated_at="2026-09-05T16:00:00+00:00",
            )
        self.assertEqual(len(result["scenarios"]), 5)
        self.assertEqual(len(result["rank_stability"]), 33)
        self.assertEqual(result["scenarios"][0]["id"], "base_all_four")
        self.assertEqual(
            [item["rank"] for item in result["scenarios"][0]["ranking"]],
            [item["base_rank"] for item in result["rank_stability"]],
        )
        self.assertGreater(max(item["rank_span_without_one_dimension"] for item in result["rank_stability"]), 0)
        self.assertIsNone(result["official_iee"]["ranking"])
        self.assertFalse(result["official_iee"]["publication_eligible"])

    def test_rejects_changed_declared_coverage(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            config = Path(temporary) / "bad.toml"
            source = (root / "config/results_ranking_sensitivity_v0.1.toml").read_text(encoding="utf-8")
            source = source.replace("../data/processed/", f"{root}/data/processed/")
            config.write_text(source.replace('"AUS"', '"BEL"', 1), encoding="utf-8")
            with self.assertRaisesRegex(ResultsRankingSensitivityError, "no coincide"):
                run_results_ranking_sensitivity(config, output_path=Path(temporary) / "sensitivity.json")
