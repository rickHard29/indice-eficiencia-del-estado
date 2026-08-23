import unittest

from iee.scoring import bounded_scores, weighted_geometric_mean, weighted_mean


class ScoringTests(unittest.TestCase):
    def test_bounded_scores_respects_direction(self) -> None:
        self.assertEqual(
            bounded_scores([10, 20, 30], lower_bound=10, upper_bound=30),
            [0.0, 50.0, 100.0],
        )
        self.assertEqual(
            bounded_scores(
                [10, 20, 30], lower_bound=10, upper_bound=30, higher_is_better=False
            ),
            [100.0, 50.0, 0.0],
        )

    def test_bounded_scores_clips_outliers(self) -> None:
        self.assertEqual(
            bounded_scores([-5, 15, 40], lower_bound=0, upper_bound=30),
            [0.0, 50.0, 100.0],
        )

    def test_weighted_mean(self) -> None:
        result = weighted_mean({"a": 80.0, "b": 40.0}, {"a": 0.75, "b": 0.25})
        self.assertAlmostEqual(result, 70.0)

    def test_weighted_mean_requires_matching_keys(self) -> None:
        with self.assertRaisesRegex(ValueError, "mismas claves"):
            weighted_mean({"a": 80.0}, {"b": 1.0})

    def test_weighted_geometric_mean_limits_compensation(self) -> None:
        geometric = weighted_geometric_mean(
            {"a": 100.0, "b": 25.0}, {"a": 0.5, "b": 0.5}
        )
        arithmetic = weighted_mean({"a": 100.0, "b": 25.0}, {"a": 0.5, "b": 0.5})
        self.assertAlmostEqual(geometric, 50.0)
        self.assertLess(geometric, arithmetic)


if __name__ == "__main__":
    unittest.main()
