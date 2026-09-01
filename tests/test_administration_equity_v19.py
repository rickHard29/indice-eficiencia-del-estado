from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.ingestion import FetchedPayload, load_download_manifest, run_pipeline


COUNTRIES = (
    "AUT", "BEL", "CAN", "CHE", "CHL", "COL", "CRI", "CZE",
    "DEU", "DNK", "ESP", "FIN", "FRA", "GBR", "GRC", "HUN",
    "IRL", "ISL", "ISR", "ITA", "JPN", "KOR", "LTU", "LVA",
    "MEX", "NLD", "NOR", "NZL", "POL", "PRT", "SVN", "SWE",
    "TUR", "USA",
)


class AdministrationEquityV19Tests(unittest.TestCase):
    def test_materializes_territorial_gap_without_score(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest_path = root / "config" / "downloads_admin_equity_v1.9.toml"
        manifest = load_download_manifest(manifest_path)

        self.assertEqual(manifest.version, "1.9")
        self.assertEqual(manifest.series[0].indicator_id, "ADM-EQ-03")
        self.assertEqual(manifest.series[0].adapter, "world_bank_absolute_gap")
        self.assertFalse(manifest.series[0].score_eligible)
        self.assertEqual(manifest.country_universe.frontier_min_countries, 30)
        self.assertEqual(len(manifest.series[0].expected_entities), 34)

        urban_records = []
        rural_records = []
        for country in COUNTRIES:
            rural, urban = "90", "92"
            if country == "COL":
                rural, urban = "97.536757962324", "98.9038513392265"
            elif country == "USA":
                rural, urban = "86.1299167271381", "93.5827214886651"
            urban_records.append({"countryiso3code": country, "date": "2024", "value": urban})
            rural_records.append({"countryiso3code": country, "date": "2024", "value": rural})
        urban_payload = json.dumps([{"page": 1, "pages": 1}, urban_records]).encode("utf-8")
        rural_payload = json.dumps([{"page": 1, "pages": 1}, rural_records]).encode("utf-8")

        def fetcher(url: str, **_kwargs: object) -> FetchedPayload:
            content = rural_payload if "RU.ZS" in url else urban_payload
            return FetchedPayload(url, url, content, "application/json")

        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            result = run_pipeline(
                manifest_path,
                raw_dir=directory / "raw",
                processed_path=directory / "observations.csv",
                provenance_path=directory / "provenance.json",
                fetcher=fetcher,
                retrieved_at="2026-09-01T00:00:00+00:00",
            )

            self.assertEqual(result.observation_count, 34)
            with (directory / "observations.csv").open(newline="", encoding="utf-8") as file:
                rows = {row["entity"]: row for row in csv.DictReader(file)}
            self.assertEqual(Decimal(rows["COL"]["value"]), Decimal("1.3670933769025"))
            self.assertEqual(Decimal(rows["USA"]["value"]), Decimal("7.452804761527"))
            self.assertTrue(all(row["observation_kind"] == "derived" for row in rows.values()))
            self.assertTrue(all(row["score_eligible"] == "false" for row in rows.values()))

            receipt = json.loads((directory / "provenance.json").read_text(encoding="utf-8"))
            self.assertEqual(len(receipt["resources"]), 2)
            self.assertEqual(receipt["country_universe"]["input_masks"][0]["included_count"], 34)


if __name__ == "__main__":
    unittest.main()
