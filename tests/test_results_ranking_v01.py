from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.results_ranking import ResultsRankingError, run_results_ranking


class ResultsRankingV01Tests(unittest.TestCase):
    def test_materializes_33_country_exploratory_ranking_without_iee(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            result = run_results_ranking(
                root / "config/results_ranking_v0.1.toml",
                output_path=Path(temporary) / "ranking.json",
                calculated_at="2026-09-05T15:00:00+00:00",
            )
        self.assertEqual(len(result["ranking"]), 33)
        self.assertEqual(result["ranking"][0]["exploratory_rank"], 1)
        self.assertIsNone(result["official_iee"]["ranking"])
        self.assertFalse(result["official_iee"]["publication_eligible"])

    def test_rejects_changed_declared_coverage(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            config = Path(temporary) / "bad.toml"
            source = (root / "config/results_ranking_v0.1.toml").read_text(encoding="utf-8")
            source = source.replace("../data/processed/", f"{root}/data/processed/")
            config.write_text(source.replace('"AUS"', '"BEL"', 1), encoding="utf-8")
            with self.assertRaisesRegex(ResultsRankingError, "no coincide"):
                run_results_ranking(config, output_path=Path(temporary) / "ranking.json")
