"""
Unit tests for Allen interval simulations.

These tests validate the simulation algorithms, particularly focusing on
the statistical properties of the generated distributions.
"""

import unittest
import sys
import os
import numpy as np

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulations import (
    IntervalSimulator,
    arSimulate,
    simulate_parallel,
    set_random_seed,
    clear_cache,
)
from constants import ALLEN_RELATION_ORDER


class SimulationValidityTests(unittest.TestCase):
    """Test suite for validating simulation statistics."""

    def setUp(self):
        """Set up the test environment."""
        # Clear cache to ensure clean test runs
        clear_cache()
        # Use fixed seed for reproducibility
        set_random_seed(42)

    def test_probabilities_sum_to_one(self):
        """Test that all probability distributions from simulations sum to approximately 1.0."""
        # Test cases with various parameter combinations
        test_cases = [
            (0.1, 0.1, 1000),  # Equal, small probabilities
            (0.5, 0.5, 1000),  # Equal, medium probabilities
            (0.9, 0.9, 1000),  # Equal, high probabilities
            (0.1, 0.5, 1000),  # Different probabilities
            (0.01, 0.8, 1000),  # Very different probabilities
            (0.2, 0.2, 100),  # Fewer trials
            (0.3, 0.3, 5000),  # More trials
        ]

        for pBorn, pDie, trials in test_cases:
            with self.subTest(pBorn=pBorn, pDie=pDie, trials=trials):
                # Run simulation
                simulator = IntervalSimulator(pBorn, pDie, trials)
                simulator.simulate()

                # Get probabilities
                probs = simulator.get_probabilities()

                # Check sum is approximately 1.0 (allowing for floating-point error)
                prob_sum = sum(probs.values())
                self.assertAlmostEqual(
                    prob_sum,
                    1.0,
                    places=6,
                    msg=f"Probabilities should sum to 1.0, got {prob_sum} for pBorn={pBorn}, pDie={pDie}",
                )

                # Verify all relations have non-negative probabilities
                for rel, prob in probs.items():
                    self.assertGreaterEqual(
                        prob,
                        0.0,
                        msg=f"Probability for relation {rel} should be non-negative, got {prob}",
                    )

    def test_parallel_simulation_probability_sum(self):
        """Test that parallel simulations also produce valid probability distributions."""
        # Test with both small and large trial counts
        for trials in [500, 2000]:
            with self.subTest(trials=trials):
                # Run parallel simulation
                results = simulate_parallel(0.2, 0.2, trials, verbose=False)

                # Calculate probabilities
                total = sum(results.values())
                if total > 0:  # Avoid division by zero
                    probs = {rel: count / total for rel, count in results.items()}

                    # Check sum is approximately 1.0
                    prob_sum = sum(probs.values())
                    self.assertAlmostEqual(
                        prob_sum,
                        1.0,
                        places=6,
                        msg=f"Parallel simulation probabilities should sum to 1.0, got {prob_sum}",
                    )

    def test_all_relations_possible(self):
        """Test that with sufficient trials, all 13 relations have a chance to occur."""
        # Use parameters known to produce a diverse distribution
        pBorn, pDie = 0.2, 0.2
        trials = 10000  # Large number of trials to ensure all relations appear

        # Run simulation
        results = arSimulate(pBorn, pDie, trials)

        # Check that every relation has at least one occurrence
        all_relations_found = all(results[rel] > 0 for rel in ALLEN_RELATION_ORDER)
        self.assertTrue(
            all_relations_found,
            msg="With sufficient trials, all 13 relations should have non-zero probability",
        )

        # Check relation counts sum to total trials
        total_count = sum(results.values())
        self.assertEqual(
            total_count,
            trials,
            msg=f"Total relation count ({total_count}) should equal trials ({trials})",
        )

    def test_probabilities_normalized_correctly(self):
        """Test that raw counts are correctly normalized to probabilities."""
        # Create a simulator with known counts
        simulator = IntervalSimulator(0.1, 0.1, 1000)

        # Manually set results to a known distribution
        simulator.results = {
            rel: (i + 1) * 10 for i, rel in enumerate(ALLEN_RELATION_ORDER)
        }

        # Get normalized probabilities
        probs = simulator.get_probabilities()

        # Calculate expected probabilities
        total = sum(simulator.results.values())
        expected_probs = {
            rel: count / total for rel, count in simulator.results.items()
        }

        # Check probabilities match expected values
        for rel in ALLEN_RELATION_ORDER:
            self.assertAlmostEqual(
                probs[rel],
                expected_probs[rel],
                places=6,
                msg=f"Probability for {rel} incorrectly normalized",
            )

        # Check sum is 1.0
        self.assertAlmostEqual(sum(probs.values()), 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
