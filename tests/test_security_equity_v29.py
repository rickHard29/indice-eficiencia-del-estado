from __future__ import annotations

import csv
import io
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.ingestion import FetchedPayload, load_download_manifest, run_pipeline


def _regional_csv(countries: tuple[str, ...], levels: dict[str, str], measure: str) -> bytes:
    output = io.StringIO()
    fields = [
        "TERRITORIAL_LEVEL", "REF_AREA", "MEASURE", "AGE", "SEX",
        "UNIT_MEASURE", "TIME_PERIOD", "OBS_VALUE", "COUNTRY", "OBS_STATUS",
        "UNIT_MULT",
    ]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for country in countries:
        level = levels.get(country, "TL2")
        rates = ["1", "2", "3"]
        if country == "COL":
            rates = ["14", "35", "49.5"]
        elif country == "USA":
            rates = ["4.1", "6", "10.2"]
        elif country == "EST":
            rates = ["0.7", "0.8", "1", "1.2", "1.5"]
        elif country == "LTU":
            rates = ["0.9", "1", "1.2", "1.4", "1.6", "1.8", "2", "2.2", "2.5", "3.1"]
        elif country == "SVN":
            rates = ["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.6", "0.4", "0.2"]
        for number, rate in enumerate(rates, start=1):
            writer.writerow({
                "TERRITORIAL_LEVEL": level,
                "REF_AREA": f"{country}{number}",
                "MEASURE": measure,
                "AGE": "_T",
                "SEX": "_T",
                "UNIT_MEASURE": "CS_10P5PS" if measure == "HOMIC" else "PS",
                "TIME_PERIOD": "2021",
                "OBS_VALUE": rate if measure == "HOMIC" else "100",
                "COUNTRY": country,
                "OBS_STATUS": "A",
                "UNIT_MULT": "0",
            })
    return output.getvalue().encode("utf-8")


class SecurityEquityV29Tests(unittest.TestCase):
    def test_mixed_tl2_tl3_sensitivity_materializes_without_score(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest_path = root / "config" / "downloads_security_equity_v2.9.toml"
        manifest = load_download_manifest(manifest_path)
        spec = manifest.series[0]

        self.assertEqual(spec.indicator_id, "SEG-EQ-02")
        self.assertEqual(len(spec.expected_entities), 33)
        self.assertEqual(dict(spec.territorial_levels), {"EST": "TL3", "LTU": "TL3", "SVN": "TL3"})
        homicide = _regional_csv(spec.expected_entities, dict(spec.territorial_levels), "HOMIC")
        population = _regional_csv(spec.expected_entities, dict(spec.territorial_levels), "POP")

        def fetcher(url: str, **_kwargs: object) -> FetchedPayload:
            content = population if "DF_DEMO" in url else homicide
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
            self.assertEqual(result.observation_count, 33)
            with (directory / "observations.csv").open(newline="", encoding="utf-8") as file:
                rows = {row["entity"]: row for row in csv.DictReader(file)}
            self.assertEqual(Decimal(rows["COL"]["value"]), Decimal("35.5"))
            self.assertEqual(Decimal(rows["USA"]["value"]), Decimal("6.1"))
            self.assertEqual(rows["EST"]["score_eligible"], "false")

