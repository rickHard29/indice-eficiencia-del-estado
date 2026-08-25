import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.frontier_panel import FrontierPanelError, load_frontier_panel_config, run_frontier_panel
from iee.ingestion import sha256_hex


_HEADER = (
    "entity,period,indicator_id,value,direction,unit,source_id,series_code,"
    "source_status,score_eligible,observation_status,observation_kind,resource_id\n"
)


class FrontierPanelTests(unittest.TestCase):
    def _prepare(self, directory: Path) -> dict[str, Path]:
        universe = directory / "universe.toml"
        result_catalog = directory / "results.toml"
        input_catalog = directory / "inputs.toml"
        result_observations = directory / "results.csv"
        input_observations = directory / "inputs.csv"
        result_receipt = directory / "results.json"
        input_receipt = directory / "inputs.json"

        universe.write_text('countries = ["AAA", "BBB", "CCC"]\n', encoding="utf-8")
        result_catalog.write_text(
            """[[series]]
indicator_id = "OUT-01"
dimension = "salud"
role = "resultado"
direction = "higher"
status = "validated"
source_id = "RESULT-SOURCE"
official_code = "OUT-CODE"
unit = "resultado"
""",
            encoding="utf-8",
        )
        input_catalog.write_text(
            """[[series]]
indicator_id = "IN-01"
dimension = "salud"
role = "insumo"
direction = "input"
status = "conditional"
source_id = "INPUT-SOURCE"
official_code = "IN-CODE"
unit = "PPA constante"
""",
            encoding="utf-8",
        )
        result_observations.write_text(
            _HEADER
            + "AAA,2020,OUT-01,10,higher,resultado,RESULT-SOURCE,OUT-CODE,validated,true,observed,reported,out\n"
            + "BBB,2020,OUT-01,20,higher,resultado,RESULT-SOURCE,OUT-CODE,validated,true,observed,reported,out\n"
            + "CCC,2020,OUT-01,30,higher,resultado,RESULT-SOURCE,OUT-CODE,validated,true,observed,reported,out\n",
            encoding="utf-8",
        )
        input_observations.write_text(
            _HEADER
            + "AAA,2020,IN-01,100,input,PPA constante,INPUT-SOURCE,IN-CODE,conditional,false,observed,derived,in\n"
            + "BBB,2020,IN-01,200,input,PPA constante,INPUT-SOURCE,IN-CODE,conditional,false,observed,derived,in\n"
            + "CCC,2020,IN-01,300,input,PPA constante,INPUT-SOURCE,IN-CODE,conditional,false,observed,derived,in\n",
            encoding="utf-8",
        )
        result_hash = sha256_hex(result_observations.read_bytes())
        input_hash = sha256_hex(input_observations.read_bytes())
        result_catalog_hash = sha256_hex(result_catalog.read_bytes())
        input_catalog_hash = sha256_hex(input_catalog.read_bytes())
        receipt = lambda payload_hash, catalog_hash: {
            "schema_version": "iee-observations-v1",
            "countries": ["AAA", "BBB", "CCC"],
            "catalog": {"sha256": catalog_hash},
            "processed": {"sha256": payload_hash, "records": 3},
        }
        result_receipt.write_text(
            json.dumps(receipt(result_hash, result_catalog_hash)), encoding="utf-8"
        )
        input_receipt.write_text(
            json.dumps(receipt(input_hash, input_catalog_hash)), encoding="utf-8"
        )
        config = directory / "frontier.toml"
        config.write_text(
            f'''version = "0.3"
schema_version = "iee-frontier-panel-v1"
status = "experimental-not-for-publication"
country_universe = "{universe.name}"
result_catalog = "{result_catalog.name}"
input_catalog = "{input_catalog.name}"
result_snapshot_sha256 = "{result_hash}"
input_snapshot_sha256 = "{input_hash}"
frontier_min_countries = 3

[[dimensions]]
id = "salud"
label = "Salud"
outcome_indicator_id = "OUT-01"
outcome_selection = "point"
outcome_year = 2020
input_indicator_id = "IN-01"
input_selection = "point"
input_year = 2020
input_status_required = "conditional"
''',
            encoding="utf-8",
        )
        return {
            "config": config,
            "result_observations": result_observations,
            "result_receipt": result_receipt,
            "input_observations": input_observations,
            "input_receipt": input_receipt,
            "panel": directory / "panel.csv",
            "gates": directory / "gates.csv",
            "provenance": directory / "provenance.json",
        }

    def test_prepares_complete_pairs_and_keeps_official_gate_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            paths = self._prepare(Path(temporary))
            config = load_frontier_panel_config(paths["config"])
            self.assertEqual(config.frontier_min_countries, 3)
            result = run_frontier_panel(
                paths["config"],
                result_observations_path=paths["result_observations"],
                result_provenance_path=paths["result_receipt"],
                input_observations_path=paths["input_observations"],
                input_provenance_path=paths["input_receipt"],
                panel_path=paths["panel"],
                gates_path=paths["gates"],
                provenance_path=paths["provenance"],
                calculated_at="2026-08-24T00:00:00+00:00",
            )
            self.assertEqual(result.panel_count, 3)
            with paths["gates"].open(newline="", encoding="utf-8") as file:
                gates = list(csv.DictReader(file))
            self.assertEqual(gates[0]["complete_pairs"], "3")
            self.assertEqual(gates[0]["experimental_sample_eligible"], "true")
            self.assertEqual(gates[0]["official_frontier_eligible"], "false")
            provenance = json.loads(paths["provenance"].read_text(encoding="utf-8"))
            self.assertIsNone(provenance["publication_gate"]["official_iee_score"])
            self.assertFalse(provenance["publication_gate"]["publication_eligible"])

    def test_rejects_changed_snapshot_before_writing_any_output(self) -> None:
        with TemporaryDirectory() as temporary:
            paths = self._prepare(Path(temporary))
            paths["input_observations"].write_text(_HEADER, encoding="utf-8")
            with self.assertRaisesRegex(FrontierPanelError, "hash de insumos"):
                run_frontier_panel(
                    paths["config"],
                    result_observations_path=paths["result_observations"],
                    result_provenance_path=paths["result_receipt"],
                    input_observations_path=paths["input_observations"],
                    input_provenance_path=paths["input_receipt"],
                    panel_path=paths["panel"],
                    gates_path=paths["gates"],
                    provenance_path=paths["provenance"],
                )
            self.assertFalse(paths["panel"].exists())
            self.assertFalse(paths["gates"].exists())
            self.assertFalse(paths["provenance"].exists())


if __name__ == "__main__":
    unittest.main()
