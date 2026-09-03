import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from iee.ingestion import sha256_hex
from iee.security_role_panel import (
    SecurityRolePanelError,
    load_security_role_panel_config,
    run_security_role_panel,
)


HEADER = (
    "entity,period,indicator_id,value,direction,unit,source_id,series_code,"
    "source_status,score_eligible,observation_status,observation_kind,resource_id\n"
)


class SecurityRolePanelV25Tests(unittest.TestCase):
    def test_v32_configuration_uses_the_explicit_multisource_sensitivity(self) -> None:
        root = Path(__file__).resolve().parents[1]
        config = load_security_role_panel_config(
            root / "config" / "security_role_integration_v3.2.toml"
        )

        self.assertEqual(config.version, "3.2")
        self.assertEqual(config.roles["equity"].indicator_id, "SEG-EQ-02")
        self.assertEqual(config.roles["input"].indicator_id, "SEG-IN-04")

    def _prepare(self, root: Path) -> dict[str, Path]:
        countries = [f"C{i:02}" for i in range(38)]
        (root / "universe.toml").write_text(
            "countries = [" + ", ".join(f'\"{country}\"' for country in countries) + "]\n",
            encoding="utf-8",
        )
        definitions = {
            "result": ("SEG-RES-01", "resultado", "validated", "true", "lower", "homicidios", "UNODC-WDI", "VC.IHR.PSRC.P5"),
            "equity": ("SEG-EQ-01", "equidad", "conditional", "false", "lower", "brecha", "OECD-REG-SAFETY", "P90_w(HOMIC_TL2) - P10_w(HOMIC_TL2)"),
            "input": ("SEG-IN-02", "insumo", "conditional", "false", "input", "PPA", "OECD-COFOG-WDI-PPP", "GF03 PT_B1GQ / 100 × NY.GDP.PCAP.PP.KD"),
        }
        paths: dict[str, Path] = {}
        for name, (indicator, role, status, eligible, direction, unit, source, code) in definitions.items():
            catalog = root / f"{name}.toml"
            catalog.write_text(
                f'''[[series]]
indicator_id = "{indicator}"
dimension = "seguridad_justicia"
role = "{role}"
direction = "{direction}"
status = "{status}"
source_id = "{source}"
official_code = "{code}"
unit = "{unit}"
''',
                encoding="utf-8",
            )
            observations = root / f"{name}.csv"
            included = countries if name != "equity" else countries[:30]
            years = [2021] if name == "equity" else [2019, 2020, 2021]
            rows = []
            for entity in included:
                for year in years:
                    rows.append(
                        f"{entity},{year},{indicator},10,{direction},{unit},{source},{code},"
                        f"{status},{eligible},observed,reported,{name}-resource\n"
                    )
            observations.write_text(HEADER + "".join(rows), encoding="utf-8")
            receipt = root / f"{name}.json"
            receipt.write_text(
                json.dumps({
                    "schema_version": "iee-observations-v1",
                    "countries": countries,
                    "catalog": {"sha256": sha256_hex(catalog.read_bytes())},
                    "processed": {"sha256": sha256_hex(observations.read_bytes()), "records": len(rows)},
                }),
                encoding="utf-8",
            )
            paths[f"{name}_observations"] = observations
            paths[f"{name}_provenance"] = receipt
            paths[f"{name}_catalog"] = catalog
        config = root / "integration.toml"
        config.write_text(
            f'''version = "2.5"
schema_version = "iee-security-role-panel-v1"
status = "experimental-not-for-publication"
country_universe = "universe.toml"
result_catalog = "result.toml"
input_catalog = "input.toml"
equity_catalog = "equity.toml"
integration_min_countries = 30

[result]
indicator_id = "SEG-RES-01"
selection = "mean"
start_year = 2019
end_year = 2021
required_status = "validated"
score_eligible = true

[equity]
indicator_id = "SEG-EQ-01"
selection = "point"
year = 2021
required_status = "conditional"
score_eligible = false

[input]
indicator_id = "SEG-IN-02"
selection = "mean"
start_year = 2019
end_year = 2021
required_status = "conditional"
score_eligible = false
''',
            encoding="utf-8",
        )
        paths.update({"config": config, "panel": root / "panel.csv", "gate": root / "gate.json", "provenance": root / "provenance.json"})
        return paths

    def test_integrates_three_roles_and_blocks_on_small_intersection(self) -> None:
        with TemporaryDirectory() as temporary:
            paths = self._prepare(Path(temporary))
            config = load_security_role_panel_config(paths["config"])
            self.assertEqual(config.roles["equity"].periods, (2021,))
            result = run_security_role_panel(
                paths["config"],
                result_observations_path=paths["result_observations"], result_provenance_path=paths["result_provenance"],
                equity_observations_path=paths["equity_observations"], equity_provenance_path=paths["equity_provenance"],
                input_observations_path=paths["input_observations"], input_provenance_path=paths["input_provenance"],
                panel_path=paths["panel"], gate_path=paths["gate"], provenance_path=paths["provenance"],
                calculated_at="2026-09-02T00:00:00+00:00",
            )
            self.assertEqual(result.panel_count, 38)
            self.assertEqual(result.complete_roles, 30)
            gate = json.loads(paths["gate"].read_text(encoding="utf-8"))
            self.assertTrue(gate["integration_sample_eligible"])
            self.assertFalse(gate["experimental_frontier_eligible"])
            self.assertIsNone(gate["official_iee_score"])
            with paths["panel"].open(newline="", encoding="utf-8") as file:
                panel = list(csv.DictReader(file))
            self.assertEqual(panel[-1]["all_roles_complete"], "false")
            self.assertIn("missing_equity:SEG-EQ-01", panel[-1]["flags"])
            provenance = json.loads(paths["provenance"].read_text(encoding="utf-8"))
            self.assertFalse(provenance["publication_gate"]["publication_eligible"])

    def test_rejects_a_changed_snapshot_before_writing(self) -> None:
        with TemporaryDirectory() as temporary:
            paths = self._prepare(Path(temporary))
            paths["input_observations"].write_text(HEADER, encoding="utf-8")
            with self.assertRaisesRegex(SecurityRolePanelError, "hash de observaciones"):
                run_security_role_panel(
                    paths["config"],
                    result_observations_path=paths["result_observations"], result_provenance_path=paths["result_provenance"],
                    equity_observations_path=paths["equity_observations"], equity_provenance_path=paths["equity_provenance"],
                    input_observations_path=paths["input_observations"], input_provenance_path=paths["input_provenance"],
                    panel_path=paths["panel"], gate_path=paths["gate"], provenance_path=paths["provenance"],
                )
            self.assertFalse(paths["panel"].exists())
