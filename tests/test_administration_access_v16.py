from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.ingestion import FetchedPayload, load_download_manifest, run_pipeline


COUNTRIES = (
    "AUS", "AUT", "BEL", "CAN", "CHE", "CHL", "COL", "CRI",
    "CZE", "DEU", "DNK", "ESP", "EST", "FIN", "FRA", "GBR",
    "GRC", "HUN", "IRL", "ISL", "ISR", "ITA", "JPN", "KOR",
    "LTU", "LUX", "LVA", "MEX", "NLD", "NOR", "NZL", "POL",
    "PRT", "SVK", "SVN", "SWE", "TUR", "USA",
)


class AdministrationAccessV16Tests(unittest.TestCase):
    def test_materializes_the_full_oecd_business_access_panel_without_score(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest_path = root / "config" / "downloads_admin_access_v1.6.toml"
        manifest = load_download_manifest(manifest_path)

        self.assertEqual(manifest.version, "1.6")
        self.assertEqual(manifest.countries, COUNTRIES)
        self.assertEqual(manifest.series[0].indicator_id, "ADM-ACC-02")
        self.assertEqual(manifest.series[0].direction, "lower")
        self.assertFalse(manifest.series[0].score_eligible)
        self.assertEqual(manifest.country_universe.frontier_min_countries, 30)

        records = []
        for country in COUNTRIES:
            year = "2024"
            value = "10"
            if country == "COL":
                year, value = "2023", "26.16919518"
            elif country == "USA":
                year, value = "2024", "5.754378796"
            records.append(
                {
                    "countryiso3code": country,
                    "date": year,
                    "value": value,
                    "obs_status": "",
                }
            )
        payload = json.dumps([{"page": 1, "pages": 1}, records]).encode("utf-8")

        def fetcher(url: str, **_kwargs: object) -> FetchedPayload:
            return FetchedPayload(
                requested_url=url,
                final_url=url,
                content=payload,
                content_type="application/json",
            )

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

            self.assertEqual(result.observation_count, 38)
            self.assertEqual(result.series_count, 1)
            with (directory / "observations.csv").open(newline="", encoding="utf-8") as file:
                rows = {row["entity"]: row for row in csv.DictReader(file)}
            self.assertEqual(Decimal(rows["COL"]["value"]), Decimal("26.16919518"))
            self.assertEqual(Decimal(rows["USA"]["value"]), Decimal("5.754378796"))
            self.assertTrue(all(row["direction"] == "lower" for row in rows.values()))
            self.assertTrue(all(row["score_eligible"] == "false" for row in rows.values()))

            receipt = json.loads((directory / "provenance.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["series_counts"], {"automatic": 1, "manual_control": 0, "materialized": 1})
            self.assertEqual(receipt["country_universe"]["input_masks"][0]["included_count"], 38)


if __name__ == "__main__":
    unittest.main()
