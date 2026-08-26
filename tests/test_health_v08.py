from pathlib import Path
import tomllib
import unittest
from unittest.mock import patch

from iee.experimental_frontier import ExperimentalFrontierError, load_estimator_config
from iee.frontier_estimate import main as frontier_main
from iee.frontier_panel import load_frontier_panel_config
from iee.ingestion import load_download_manifest


class HealthV08Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).parents[1]
        with (self.root / "config" / "health_input_sources_v0.8.toml").open("rb") as file:
            self.catalog = tomllib.load(file)
        with (self.root / "config" / "downloads_health_v0.8.toml").open("rb") as file:
            self.manifest = tomllib.load(file)

    def test_direct_constant_ppp_input_is_explicitly_conditional(self) -> None:
        series = self.catalog["series"]
        self.assertEqual(len(series), 1)
        entry = series[0]
        self.assertEqual(entry["indicator_id"], "SAL-IN-03")
        self.assertEqual(entry["status"], "conditional")
        self.assertEqual(entry["unit"], "Dólares estadounidenses PPA constantes de 2020 por habitante")
        self.assertIn("HF1", entry["official_code"])
        self.assertEqual(entry["latest_col_value"], "1177.410")
        self.assertEqual(entry["latest_usa_value"], "10078.994")

    def test_manifest_freezes_all_oecd_members_and_sha_dimensions(self) -> None:
        loaded = load_download_manifest(self.root / "config" / "downloads_health_v0.8.toml")
        self.assertEqual(loaded.version, "0.8")
        self.assertEqual(len(loaded.countries), 38)
        self.assertEqual(len(loaded.series), 1)
        spec = loaded.series[0]
        self.assertEqual(spec.expected_entities, loaded.countries)
        self.assertEqual(spec.minimum_observations_per_entity, 5)
        self.assertFalse(spec.score_eligible)
        self.assertEqual(
            spec.dimension_filters,
            {
                "FREQ": "A",
                "MEASURE": "EXP_HEALTH",
                "UNIT_MEASURE": "USD_PPP_PS",
                "FINANCING_SCHEME": "HF1",
                "FINANCING_SCHEME_REV": "_Z",
                "FUNCTION": "_T",
                "MODE_PROVISION": "_T",
                "PROVIDER": "_T",
                "FACTOR_PROVISION": "_Z",
                "ASSET_TYPE": "_Z",
                "PRICE_BASE": "Q",
            },
        )
        self.assertIsNotNone(loaded.country_universe)
        assert loaded.country_universe is not None
        self.assertEqual(loaded.country_universe.input_masks[0].excluded_countries, ())

    def test_health_panel_is_a_separate_resource_sensitivity(self) -> None:
        panel = load_frontier_panel_config(self.root / "config" / "frontier_panel_v0.8.toml")
        self.assertEqual(panel.version, "0.8")
        self.assertEqual(panel.status, "experimental-not-for-publication")
        self.assertEqual(len(panel.dimensions), 1)
        dimension = panel.dimensions[0]
        self.assertEqual(dimension.outcome_indicator_id, "SAL-RES-01")
        self.assertEqual(dimension.input_indicator_id, "SAL-IN-03")
        self.assertEqual(dimension.input_periods, (2019, 2020, 2021))

    def test_estimator_uses_the_existing_health_outcome_contract(self) -> None:
        estimator = load_estimator_config(self.root / "config" / "frontier_estimator_v0.8.toml")
        self.assertEqual(estimator.version, "0.8")
        self.assertEqual(estimator.panel_input_indicators, {"salud": "SAL-IN-03"})
        self.assertEqual(len(estimator.rules), 1)
        self.assertEqual(estimator.rules[0].outcome_indicator_id, "SAL-RES-01")

    def test_frontier_cli_reports_a_controlled_error(self) -> None:
        with patch(
            "iee.frontier_estimate.run_experimental_frontier",
            side_effect=ExperimentalFrontierError("entrada inválida"),
        ):
            with self.assertRaises(SystemExit) as raised:
                frontier_main([])
        self.assertEqual(raised.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
