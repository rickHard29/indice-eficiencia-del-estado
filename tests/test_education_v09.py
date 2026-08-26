from pathlib import Path
import unittest

from iee.experimental_frontier import load_estimator_config
from iee.frontier_panel import load_frontier_panel_config


class EducationV09Tests(unittest.TestCase):
    def test_panel_preserves_the_pre_outcome_resource_window(self) -> None:
        root = Path(__file__).parents[1]
        panel = load_frontier_panel_config(root / "config" / "frontier_panel_v0.9.toml")
        self.assertEqual(panel.version, "0.9")
        self.assertEqual(panel.status, "experimental-not-for-publication")
        self.assertEqual(len(panel.countries), 38)
        self.assertEqual(len(panel.dimensions), 1)
        dimension = panel.dimensions[0]
        self.assertEqual(dimension.id, "educacion")
        self.assertEqual(dimension.outcome_indicator_id, "EDU-RES-01")
        self.assertEqual(dimension.outcome_periods, (2020,))
        self.assertEqual(dimension.input_indicator_id, "EDU-IN-02")
        self.assertEqual(dimension.input_periods, (2019, 2020))
        self.assertEqual(dimension.input_status_required, "conditional")

    def test_estimator_uses_the_canonical_learning_scale(self) -> None:
        root = Path(__file__).parents[1]
        estimator = load_estimator_config(root / "config" / "frontier_estimator_v0.9.toml")
        self.assertEqual(estimator.version, "0.9")
        self.assertEqual(estimator.panel_input_indicators, {"educacion": "EDU-IN-02"})
        self.assertEqual(len(estimator.rules), 1)
        rule = estimator.rules[0]
        self.assertEqual(rule.outcome_indicator_id, "EDU-RES-01")
        self.assertEqual(rule.bound_status, "technical_scale")
        self.assertEqual((rule.lower_bound, rule.upper_bound), (300, 625))


if __name__ == "__main__":
    unittest.main()
