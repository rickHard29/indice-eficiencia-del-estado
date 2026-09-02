from __future__ import annotations

import csv
import io
import json
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.ingestion import FetchedPayload, load_download_manifest, run_pipeline


COUNTRIES = (
    "AUS", "AUT", "BEL", "CAN", "CHE", "CHL", "COL", "CRI",
    "CZE", "DEU", "DNK", "ESP", "FIN", "FRA", "GBR", "GRC",
    "HUN", "IRL", "ITA", "JPN", "KOR", "MEX", "NLD", "NOR",
    "POL", "PRT", "SVK", "SWE", "TUR", "USA",
)


def _regional_csv(*, measure: str, unit: str) -> bytes:
    output = io.StringIO()
    fields = [
        "TERRITORIAL_LEVEL", "REF_AREA", "MEASURE", "AGE", "SEX",
        "UNIT_MEASURE", "TIME_PERIOD", "OBS_VALUE", "COUNTRY", "OBS_STATUS",
        "UNIT_MULT",
    ]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for country in COUNTRIES:
        rates = ["1", "2", "3"]
        if country == "COL":
            rates = ["14", "35", "49.5"]
        elif country == "USA":
            rates = ["4.1", "6", "10.2"]
        for index, rate in enumerate(rates, start=1):
            writer.writerow(
                {
                    "TERRITORIAL_LEVEL": "TL2",
                    "REF_AREA": f"{country}{index}",
                    "MEASURE": measure,
                    "AGE": "_T",
                    "SEX": "_T",
                    "UNIT_MEASURE": unit,
                    "TIME_PERIOD": "2021",
                    "OBS_VALUE": rate if measure == "HOMIC" else ["20", "60", "20"][index - 1],
                    "COUNTRY": country,
                    "OBS_STATUS": "A",
                    "UNIT_MULT": "0",
                }
            )
    if measure == "POP":
        writer.writerow(
            {
                "TERRITORIAL_LEVEL": "TL2",
                "REF_AREA": "USZZ",
                "MEASURE": measure,
                "AGE": "_T",
                "SEX": "_T",
                "UNIT_MEASURE": unit,
                "TIME_PERIOD": "2021",
                "OBS_VALUE": "0",
                "COUNTRY": "USA",
                "OBS_STATUS": "A",
                "UNIT_MULT": "0",
            }
        )
    return output.getvalue().encode("utf-8")


class SecurityEquityV23Tests(unittest.TestCase):
    def test_materializes_population_weighted_regional_gap_without_score(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest_path = root / "config" / "downloads_security_equity_v2.3.toml"
        manifest = load_download_manifest(manifest_path)

        self.assertEqual(manifest.version, "2.3")
        self.assertEqual(manifest.series[0].indicator_id, "SEG-EQ-01")
        self.assertEqual(
            manifest.series[0].adapter, "oecd_regional_weighted_interdecile_gap"
        )
        self.assertFalse(manifest.series[0].score_eligible)
        self.assertEqual(manifest.country_universe.frontier_min_countries, 30)
        self.assertEqual(len(manifest.series[0].expected_entities), 30)

        homicide_payload = _regional_csv(measure="HOMIC", unit="CS_10P5PS")
        population_payload = _regional_csv(measure="POP", unit="PS")

        def fetcher(url: str, **_kwargs: object) -> FetchedPayload:
            content = population_payload if "DF_DEMO" in url else homicide_payload
            return FetchedPayload(url, url, content, "text/csv")

        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            result = run_pipeline(
                manifest_path,
                raw_dir=directory / "raw",
                processed_path=directory / "observations.csv",
                provenance_path=directory / "provenance.json",
                fetcher=fetcher,
                retrieved_at="2026-09-02T00:00:00+00:00",
            )

            self.assertEqual(result.observation_count, 30)
            with (directory / "observations.csv").open(newline="", encoding="utf-8") as file:
                rows = {row["entity"]: row for row in csv.DictReader(file)}
            self.assertEqual(Decimal(rows["COL"]["value"]), Decimal("35.5"))
            self.assertEqual(Decimal(rows["USA"]["value"]), Decimal("6.1"))
            self.assertTrue(all(row["observation_kind"] == "derived" for row in rows.values()))
            self.assertTrue(all(row["score_eligible"] == "false" for row in rows.values()))

            receipt = json.loads((directory / "provenance.json").read_text(encoding="utf-8"))
            self.assertEqual(len(receipt["resources"]), 2)
            self.assertEqual(receipt["country_universe"]["input_masks"][0]["included_count"], 30)


if __name__ == "__main__":
    unittest.main()
