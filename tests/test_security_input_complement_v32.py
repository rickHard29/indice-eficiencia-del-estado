import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.ingestion import sha256_hex
from iee.security_input_complement import run_security_input_complement


HEADER = (
    "entity,period,indicator_id,value,direction,unit,source_id,series_code,"
    "source_status,score_eligible,observation_status,observation_kind,resource_id\n"
)


class SecurityInputComplementV32Tests(unittest.TestCase):
    def test_combines_the_oecd_base_and_canada_without_replacing_sources(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            countries = ["CAN", "C01", "C02", *[f"X{number:02}" for number in range(35)]]
            (root / "universe.toml").write_text(
                "countries = [" + ", ".join(f'"{country}"' for country in countries) + "]\n",
                encoding="utf-8",
            )
            (root / "catalog.toml").write_text("", encoding="utf-8")
            (root / "config.toml").write_text(
                '''version = "3.2"
schema_version = "iee-security-input-complement-v1"
status = "experimental-not-for-publication"
country_universe = "universe.toml"
catalog = "catalog.toml"
base_indicator_id = "SEG-IN-02"
canada_indicator_id = "SEG-IN-03"
composite_indicator_id = "SEG-IN-04"
canada_entity = "CAN"
base_countries = ["C01", "C02"]
start_year = 2019
end_year = 2021
source_id = "OECD-COFOG+STATCAN-WDI-PPP"
series_code = "composite"
unit = "PPA"
''',
                encoding="utf-8",
            )
            base_rows = [
                _row(entity, year, "SEG-IN-02")
                for entity in ("C01", "C02")
                for year in (2019, 2020, 2021)
            ]
            canada_rows = [_row("CAN", year, "SEG-IN-03") for year in (2019, 2020, 2021)]
            base_path = root / "base.csv"
            canada_path = root / "canada.csv"
            base_path.write_text(HEADER + "".join(base_rows), encoding="utf-8")
            canada_path.write_text(HEADER + "".join(canada_rows), encoding="utf-8")
            _write_receipt(root / "base.json", base_path)
            _write_receipt(root / "canada.json", canada_path)

            count = run_security_input_complement(
                root / "config.toml",
                base_observations_path=base_path,
                base_provenance_path=root / "base.json",
                canada_observations_path=canada_path,
                canada_provenance_path=root / "canada.json",
                processed_path=root / "composite.csv",
                provenance_path=root / "composite.json",
                calculated_at="2026-09-03T12:00:00+00:00",
            )

            self.assertEqual(count, 9)
            with (root / "composite.csv").open(encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual({row["indicator_id"] for row in rows}, {"SEG-IN-04"})
            self.assertEqual({row["source_id"] for row in rows}, {"OECD-COFOG+STATCAN-WDI-PPP"})
            receipt = json.loads((root / "composite.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["sources_by_country"]["STATCAN-CCOFOG-WDI-PPP"], ["CAN"])


def _row(entity: str, year: int, indicator: str) -> str:
    return (
        f"{entity},{year},{indicator},10,input,PPA,source,code,conditional,false,"
        "observed,derived,resource\n"
    )


def _write_receipt(path: Path, observation_path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "iee-observations-v1",
                "processed": {"sha256": sha256_hex(observation_path.read_bytes())},
            }
        ),
        encoding="utf-8",
    )
