from pathlib import Path
import unittest

from iee.experimental_context import (
    ContextSensitivityError,
    fit_conditional_monotone_quantile,
    load_context_sensitivity_config,
)


class ContextSensitivityTests(unittest.TestCase):
    def test_conditional_fit_recovers_a_monotone_resource_frontier(self) -> None:
        fit = fit_conditional_monotone_quantile(
            resources=[0.0, 1.0, 3.0, 4.0],
            contexts=[0.0, 1.0, 0.0, 1.0],
            outcomes=[10.0, 15.0, 16.0, 21.0],
            quantile=0.9,
        )
        self.assertAlmostEqual(fit.intercept, 10.0)
        self.assertAlmostEqual(fit.resource_slope, 2.0)
        self.assertAlmostEqual(fit.context_slope, 3.0)
        self.assertAlmostEqual(fit.pinball_loss, 0.0)

    def test_conditional_fit_rejects_collinear_resources_and_context(self) -> None:
        with self.assertRaisesRegex(ContextSensitivityError, "colineales"):
            fit_conditional_monotone_quantile(
                resources=[0.0, 1.0, 2.0, 3.0],
                contexts=[0.0, 1.0, 2.0, 3.0],
                outcomes=[1.0, 2.0, 3.0, 4.0],
                quantile=0.9,
            )

    def test_committed_contract_uses_one_context_control_per_sensitivity(self) -> None:
        root = Path(__file__).parents[1]
        config = load_context_sensitivity_config(root / "config" / "context_sensitivity_v0.4.toml")
        self.assertEqual(config.dimensions, ("salud", "educacion"))
        self.assertEqual(config.minimum_sample, 30)
        self.assertEqual(config.context_start_year, 2019)
        self.assertEqual(config.context_end_year, 2021)
        self.assertEqual(
            {(control.indicator_id, control.transform) for control in config.controls},
            {("CTX-AGE-01", "linear"), ("CTX-DENS-01", "log1p")},
        )
        self.assertEqual(config.uncertainty, "not-estimated-for-context-sensitivity")


if __name__ == "__main__":
    unittest.main()
