from pathlib import Path
import unittest

from iee.experimental_frontier import load_estimator_config
from iee.frontier_panel import load_frontier_panel_config


class SecurityV10Tests(unittest.TestCase):
    def test_panel_aligns_outcome_and_resource_windows_without_replacing_baseline(self) -> None:
        root = Path(__file__).parents[1]
        panel = load_frontier_panel_config(root / "config" / "frontier_panel_v1.0.toml")
        self.assertEqual(panel.version, "1.0")
        self.assertEqual(panel.status, "experimental-not-for-publication")
        self.assertEqual(len(panel.countries), 38)
        self.assertEqual(len(panel.dimensions), 1)
        dimension = panel.dimensions[0]
        self.assertEqual(dimension.id, "seguridad_justicia")
        self.assertEqual(dimension.outcome_indicator_id, "SEG-RES-01")
        self.assertEqual(dimension.input_indicator_id, "SEG-IN-02")
        self.assertEqual(dimension.outcome_periods, (2019, 2020, 2021))
        self.assertEqual(dimension.input_periods, (2019, 2020, 2021))
        self.assertEqual(dimension.input_status_required, "conditional")

    def test_estimator_uses_the_canonical_homicide_transform(self) -> None:
        root = Path(__file__).parents[1]
        estimator = load_estimator_config(root / "config" / "frontier_estimator_v1.0.toml")
        self.assertEqual(estimator.version, "1.0")
        self.assertEqual(
            estimator.panel_input_indicators,
            {"seguridad_justicia": "SEG-IN-02"},
        )
        self.assertEqual(len(estimator.rules), 1)
        rule = estimator.rules[0]
        self.assertEqual(rule.outcome_indicator_id, "SEG-RES-01")
        self.assertEqual(rule.direction, "lower")
        self.assertEqual(rule.transform, "log1p")
        self.assertEqual((rule.lower_bound, rule.upper_bound), (0, 50))


if __name__ == "__main__":
    unittest.main()
