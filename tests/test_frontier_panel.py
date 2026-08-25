import csv
import json
import math
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.frontier_panel import FrontierPanelError, load_frontier_panel_config, run_frontier_panel
from iee.experimental_frontier import (
    ExperimentalFrontierError,
    EstimatorConfig,
    FrontierRule,
    _anchor_noncrossing,
    _normalize,
    _read_gates,
    _read_inputs,
    fit_monotone_quantile,
    run_experimental_frontier,
)
from iee.ingestion import sha256_hex


_HEADER = (
    "entity,period,indicator_id,value,direction,unit,source_id,series_code,"
    "source_status,score_eligible,observation_status,observation_kind,resource_id\n"
)


class FrontierPanelTests(unittest.TestCase):
    def test_v06_education_bridge_uses_pre_outcome_proxy_window(self) -> None:
        root = Path(__file__).resolve().parents[1]
        config = load_frontier_panel_config(root / "config/frontier_panel_v0.6.toml")

        self.assertEqual(config.version, "0.6")
        self.assertEqual(config.status, "experimental-not-for-publication")
        self.assertEqual(len(config.dimensions), 1)
        education = config.dimensions[0]
        self.assertEqual(education.id, "educacion")
        self.assertEqual(education.outcome_periods, (2020,))
        self.assertEqual(education.input_periods, (2019, 2020))
        self.assertEqual(education.input_status_required, "conditional")

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
            + "AAA,2020,OUT-01,10,higher,resultado,RESULT-SOURCE,OUT-CODE,"
            "validated,true,observed,reported,out\n"
            + "BBB,2020,OUT-01,20,higher,resultado,RESULT-SOURCE,OUT-CODE,"
            "validated,true,observed,reported,out\n"
            + "CCC,2020,OUT-01,30,higher,resultado,RESULT-SOURCE,OUT-CODE,"
            "validated,true,observed,reported,out\n",
            encoding="utf-8",
        )
        input_observations.write_text(
            _HEADER
            + "AAA,2020,IN-01,100,input,PPA constante,INPUT-SOURCE,IN-CODE,"
            "conditional,false,observed,derived,in\n"
            + "BBB,2020,IN-01,200,input,PPA constante,INPUT-SOURCE,IN-CODE,"
            "conditional,false,observed,derived,in\n"
            + "CCC,2020,IN-01,300,input,PPA constante,INPUT-SOURCE,IN-CODE,"
            "conditional,false,observed,derived,in\n",
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

    def test_quantile_fit_is_monotone_and_respects_a_flat_boundary(self) -> None:
        increasing = fit_monotone_quantile([0, 1, 2, 3], [0, 1, 2, 3], 0.9)
        self.assertAlmostEqual(increasing.intercept, 0.0)
        self.assertAlmostEqual(increasing.slope, 1.0)
        self.assertAlmostEqual(increasing.pinball_loss, 0.0)

        decreasing = fit_monotone_quantile([0, 1, 2, 3], [3, 2, 1, 0], 0.9)
        self.assertAlmostEqual(decreasing.intercept, 3.0)
        self.assertAlmostEqual(decreasing.slope, 0.0)
        self.assertGreater(decreasing.pinball_loss, 0.0)

    def test_outcome_transform_and_quantile_sensitivities_follow_contract(self) -> None:
        rule = FrontierRule(
            id="seguridad_justicia",
            outcome_indicator_id="SEG-RES-01",
            direction="lower",
            transform="log1p",
            lower_bound=Decimal("0"),
            upper_bound=Decimal("50"),
            bound_status="provisional",
            bound_reference="Prueba",
        )
        score, flags = _normalize(Decimal("10"), rule)
        expected = 100.0 * (1.0 - math.log1p(10.0) / math.log1p(50.0))
        self.assertAlmostEqual(score, expected)
        self.assertEqual(flags, ())

        adjusted = _anchor_noncrossing(
            {0.85: 80.0, 0.90: 70.0, 0.95: 65.0}, base_quantile=0.90
        )
        self.assertEqual(adjusted, {0.85: 70.0, 0.90: 70.0, 0.95: 70.0})

    def test_rejects_gate_minimum_below_panel_contract(self) -> None:
        payload = (
            b"dimension,complete_pairs,frontier_min_countries,"
            b"experimental_sample_eligible,official_frontier_eligible\n"
            b"salud,3,2,true,false\n"
        )
        with self.assertRaisesRegex(ExperimentalFrontierError, "mínimo muestral"):
            _read_gates(payload, 3)

    def test_rejects_semantically_altered_panel_provenance(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            panel = root / "panel.csv"
            gates = root / "gates.csv"
            provenance = root / "provenance.json"
            panel.write_bytes(b"panel")
            gates.write_bytes(b"gates")
            receipt = {
                "schema_version": "iee-frontier-panel-v1",
                "version": "0.3",
                "status": "altered",
                "countries": ["AAA"],
                "configuration": {
                    "sha256": "1" * 64,
                    "frontier_min_countries": 30,
                },
                "inputs": {
                    "results": {"observations_sha256": "2" * 64},
                    "inputs": {"observations_sha256": "3" * 64},
                },
                "outputs": {
                    "panel": {"sha256": sha256_hex(panel.read_bytes())},
                    "gates": {"sha256": sha256_hex(gates.read_bytes())},
                },
                "publication_gate": {
                    "official_iee_score": None,
                    "publication_eligible": False,
                    "ranking_eligible": False,
                },
            }
            provenance.write_text(json.dumps(receipt), encoding="utf-8")
            config = EstimatorConfig(
                path=root / "estimator.toml",
                sha256="0" * 64,
                version="0.3",
                schema_version="iee-experimental-frontier-v1",
                status="experimental-not-for-publication",
                countries=("AAA",),
                panel_config_path=root / "panel.toml",
                panel_config_sha256="1" * 64,
                diagnostic_config_path=root / "diagnostic.toml",
                diagnostic_config_sha256="4" * 64,
                panel_sha256=sha256_hex(panel.read_bytes()),
                gates_sha256=sha256_hex(gates.read_bytes()),
                panel_provenance_sha256=sha256_hex(provenance.read_bytes()),
                frontier_min_countries=30,
                result_snapshot_sha256="2" * 64,
                input_snapshot_sha256="3" * 64,
                frontier_quantile=0.9,
                sensitivity_quantiles=(0.85, 0.95),
                input_transform="log1p",
                require_non_decreasing_frontier=True,
                bootstrap_replications=50,
                confidence_level=0.9,
                random_seed=1,
                panel_input_indicators={},
                dependency_paths=(),
                rules=(),
            )
            with self.assertRaisesRegex(ExperimentalFrontierError, "estado de procedencia"):
                _read_inputs(config, panel, gates, provenance)

    def test_runs_experimental_frontier_without_opening_official_gate(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = self._prepare(root)
            panel_result = run_frontier_panel(
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
            diagnostic_config = root / "diagnostic.toml"
            diagnostic_config.write_text(
                '''[[indicators]]
indicator_id = "OUT-01"
direction = "higher"
transform = "linear"
lower_bound = 0.0
upper_bound = 100.0
bound_status = "natural_scale"
bound_reference = "Escala sintética de prueba."
''',
                encoding="utf-8",
            )
            estimator_config = root / "estimator.toml"
            estimator_config.write_text(
                f'''version = "0.3"
schema_version = "iee-experimental-frontier-v1"
status = "experimental-not-for-publication"
panel_config = "{paths['config'].name}"
panel_config_sha256 = "{sha256_hex(paths['config'].read_bytes())}"
diagnostic_config = "{diagnostic_config.name}"
diagnostic_config_sha256 = "{sha256_hex(diagnostic_config.read_bytes())}"
panel_sha256 = "{panel_result.output_sha256['panel']}"
gates_sha256 = "{panel_result.output_sha256['gates']}"
panel_provenance_sha256 = "{sha256_hex(paths['provenance'].read_bytes())}"
frontier_quantile = 0.90
sensitivity_quantiles = [0.85, 0.95]
input_transform = "log1p"
require_non_decreasing_frontier = true
bootstrap_replications = 50
confidence_level = 0.90
random_seed = 20260824

[[dimensions]]
id = "salud"
outcome_indicator_id = "OUT-01"
direction = "higher"
transform = "linear"
lower_bound = 0.0
upper_bound = 100.0
bound_status = "natural_scale"
bound_reference = "Escala sintética de prueba."
''',
                encoding="utf-8",
            )
            estimates = root / "estimates.csv"
            models = root / "models.csv"
            sensitivity = root / "sensitivity.csv"
            frontier_provenance = root / "frontier-provenance.json"
            result = run_experimental_frontier(
                estimator_config,
                panel_path=paths["panel"],
                gates_path=paths["gates"],
                panel_provenance_path=paths["provenance"],
                estimates_path=estimates,
                models_path=models,
                sensitivity_path=sensitivity,
                provenance_path=frontier_provenance,
                calculated_at="2026-08-24T00:00:00+00:00",
            )
            self.assertEqual(result.estimate_count, 3)
            self.assertEqual(result.model_count, 1)
            self.assertEqual(result.sensitivity_count, 9)
            with sensitivity.open(newline="", encoding="utf-8") as file:
                sensitivity_rows = list(csv.DictReader(file))
            by_entity: dict[str, list[tuple[float, float]]] = {}
            for row in sensitivity_rows:
                by_entity.setdefault(row["entity"], []).append(
                    (float(row["quantile"]), float(row["frontier_score"]))
                )
            for rows in by_entity.values():
                ordered = [frontier for _, frontier in sorted(rows)]
                self.assertEqual(ordered, sorted(ordered))
            with models.open(newline="", encoding="utf-8") as file:
                model = next(csv.DictReader(file))
            self.assertEqual(model["experimental_sample_eligible"], "true")
            self.assertEqual(model["official_frontier_eligible"], "false")
            receipt = json.loads(frontier_provenance.read_text(encoding="utf-8"))
            self.assertIsNone(receipt["publication_gate"]["official_iee_score"])
            self.assertFalse(receipt["publication_gate"]["ranking_eligible"])

            first_provenance = frontier_provenance.read_bytes()
            repeated = run_experimental_frontier(
                estimator_config,
                panel_path=paths["panel"],
                gates_path=paths["gates"],
                panel_provenance_path=paths["provenance"],
                estimates_path=estimates,
                models_path=models,
                sensitivity_path=sensitivity,
                provenance_path=frontier_provenance,
                calculated_at="2026-08-24T00:00:00+00:00",
            )
            self.assertEqual(result.output_sha256, repeated.output_sha256)
            self.assertEqual(first_provenance, frontier_provenance.read_bytes())


if __name__ == "__main__":
    unittest.main()
