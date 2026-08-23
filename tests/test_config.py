from pathlib import Path
import tomllib
import unittest


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        config_path = Path(__file__).parents[1] / "config" / "methodology.toml"
        with config_path.open("rb") as config_file:
            self.config = tomllib.load(config_file)

    def test_pilot_dimension_weights_sum_to_one(self) -> None:
        weights = [dimension["weight"] for dimension in self.config["dimensions"]]
        self.assertEqual(sum(weights), 1.0)
        self.assertTrue(all(weight > 0.0 for weight in weights))

    def test_coverage_thresholds_are_probabilities(self) -> None:
        self.assertTrue(0.0 < self.config["minimum_indicator_coverage"] <= 1.0)
        self.assertTrue(0.0 < self.config["minimum_dimension_coverage"] <= 1.0)


if __name__ == "__main__":
    unittest.main()
