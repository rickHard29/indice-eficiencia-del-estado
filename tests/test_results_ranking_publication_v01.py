import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.results_ranking_publication import ResultsRankingPublicationError, run_results_ranking_publication


class ResultsRankingPublicationV01Tests(unittest.TestCase):
    def test_exports_33_country_files_with_the_official_block_preserved(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            output = Path(temporary)
            result = run_results_ranking_publication(
                root / "config/results_ranking_publication_v0.1.toml",
                ranking_output_path=output / "ranking.csv",
                stability_output_path=output / "stability.csv",
            )
            with (output / "ranking.csv").open(newline="", encoding="utf-8") as file:
                ranking_rows = list(csv.DictReader(file))
            with (output / "stability.csv").open(newline="", encoding="utf-8") as file:
                stability_rows = list(csv.DictReader(file))
        self.assertEqual(result["countries"], 33)
        self.assertEqual(ranking_rows[0]["country_iso3"], "JPN")
        self.assertEqual(ranking_rows[0]["status"], "experimental-results-ranking-not-iee")
        self.assertEqual(len(stability_rows), 33)
        self.assertEqual(next(row for row in stability_rows if row["country_iso3"] == "COL")["rank_span_without_one_dimension"], "1")

    def test_rejects_a_receipt_that_claims_the_official_iee_is_publishable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            ranking = (root / "data/processed/results_ranking_v0.1.json").read_text(encoding="utf-8")
            invalid_ranking = temporary_path / "ranking.json"
            invalid_ranking.write_text(ranking.replace('"publication_eligible": false', '"publication_eligible": true', 1), encoding="utf-8")
            config = temporary_path / "publication.toml"
            source = (root / "config/results_ranking_publication_v0.1.toml").read_text(encoding="utf-8")
            config.write_text(
                source.replace("../data/processed/results_ranking_v0.1.json", str(invalid_ranking)).replace(
                    "../data/processed/results_ranking_sensitivity_v0.1.json",
                    str(root / "data/processed/results_ranking_sensitivity_v0.1.json"),
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ResultsRankingPublicationError, "bloqueo"):
                run_results_ranking_publication(
                    config,
                    ranking_output_path=temporary_path / "ranking.csv",
                    stability_output_path=temporary_path / "stability.csv",
                )
