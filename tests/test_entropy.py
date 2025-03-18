"""
Unit tests for entropy calculation functions.

These tests validate the correctness of Shannon entropy calculations
used throughout the Allen's interval algebra visualization and analysis code.
"""

import unittest
import numpy as np
import math
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared_utils import calculate_shannon_entropy
from analysis_utils import analyze_distribution


class EntropyCalculationTests(unittest.TestCase):
    """Test suite for entropy calculation functions."""

    def test_uniform_distribution_entropy(self):
        """Test that uniform distributions have entropy = log2(n)."""
        # Test cases: (probabilities, expected_entropy)
        test_cases = [
            ([0.5, 0.5], 1.0),  # 2 equally likely outcomes: entropy = log2(2) = 1.0
            ([1 / 3, 1 / 3, 1 / 3], math.log2(3)),  # 3 equally likely outcomes
            (
                [0.25, 0.25, 0.25, 0.25],
                2.0,
            ),  # 4 equally likely outcomes: entropy = log2(4) = 2.0
            (
                [1 / 13] * 13,
                math.log2(13),
            ),  # 13 equally likely outcomes (Allen relations)
        ]

        for probs, expected in test_cases:
            with self.subTest(probabilities=probs, expected=expected):
                entropy = calculate_shannon_entropy(probs)
                self.assertAlmostEqual(
                    entropy,
                    expected,
                    places=6,
                    msg=f"Uniform entropy calculation failed for {len(probs)} items",
                )

    def test_deterministic_distribution_entropy(self):
        """Test that deterministic distributions (single outcome) have zero entropy."""
        # Test cases: distributions with a single certain outcome
        test_cases = [
            ([1.0, 0.0], 0.0),
            ([0.0, 1.0], 0.0),
            ([0.0, 0.0, 1.0], 0.0),
            ([1.0, 0.0, 0.0, 0.0], 0.0),
            ([0.0] * 12 + [1.0], 0.0),  # One certain outcome among 13 possibilities
        ]

        for probs, expected in test_cases:
            with self.subTest(probabilities=probs, expected=expected):
                entropy = calculate_shannon_entropy(probs)
                self.assertAlmostEqual(
                    entropy,
                    expected,
                    places=6,
                    msg=f"Deterministic entropy should be 0 but got {entropy}",
                )

    def test_known_entropy_distributions(self):
        """Test entropy calculations against known values."""
        # Test cases with manually calculated entropy values
        test_cases = [
            ([0.75, 0.25], -(0.75 * math.log2(0.75) + 0.25 * math.log2(0.25))),
            (
                [0.5, 0.25, 0.25],
                -(
                    0.5 * math.log2(0.5)
                    + 0.25 * math.log2(0.25)
                    + 0.25 * math.log2(0.25)
                ),
            ),
            (
                [0.1, 0.1, 0.2, 0.6],
                -(
                    0.1 * math.log2(0.1)
                    + 0.1 * math.log2(0.1)
                    + 0.2 * math.log2(0.2)
                    + 0.6 * math.log2(0.6)
                ),
            ),
        ]

        for probs, expected in test_cases:
            with self.subTest(probabilities=probs, expected=expected):
                entropy = calculate_shannon_entropy(probs)
                self.assertAlmostEqual(
                    entropy,
                    expected,
                    places=6,
                    msg=f"Entropy calculation incorrect for distribution {probs}",
                )

    def test_edge_cases(self):
        """Test entropy calculation with edge cases."""
        # Empty list should raise an exception or return 0
        with self.assertRaises(ValueError):
            calculate_shannon_entropy([])

        # Single probability of 1.0 should have zero entropy
        self.assertEqual(calculate_shannon_entropy([1.0]), 0.0)

        # Zero probabilities should be handled correctly (ignored in calculation)
        entropy = calculate_shannon_entropy([0.5, 0.5, 0.0, 0.0])
        self.assertAlmostEqual(entropy, 1.0, places=6)

        # Very small probabilities should not cause numerical issues
        small_prob = 1e-10
        remainder = 1.0 - small_prob
        entropy = calculate_shannon_entropy([small_prob, remainder])
        expected = -(
            small_prob * math.log2(small_prob) + remainder * math.log2(remainder)
        )
        self.assertAlmostEqual(entropy, expected, places=6)

    def test_dictionary_input(self):
        """Test that the analyze_distribution function correctly calculates entropy."""
        # Create a mock distribution dictionary like those used in the Allen relations code
        from constants import ALLEN_RELATION_ORDER

        # Create a uniform distribution across relations
        uniform_counts = {rel: 100 for rel in ALLEN_RELATION_ORDER}
        uniform_analysis = analyze_distribution(uniform_counts)
        self.assertAlmostEqual(
            uniform_analysis["entropy"],
            math.log2(len(ALLEN_RELATION_ORDER)),
            places=6,
            msg="Uniform distribution across relations should have entropy = log2(13)",
        )

        # Create a deterministic distribution (all counts for one relation)
        deterministic_counts = {rel: 0 for rel in ALLEN_RELATION_ORDER}
        deterministic_counts["e"] = 1000  # All counts for "equals" relation
        deterministic_analysis = analyze_distribution(deterministic_counts)
        self.assertAlmostEqual(
            deterministic_analysis["entropy"],
            0.0,
            places=6,
            msg="Deterministic distribution should have zero entropy",
        )

    def test_normalization_requirement(self):
        """Test that probabilities must be normalized (sum to 1)."""
        # Non-normalized probabilities should raise an exception
        with self.assertRaises(ValueError):
            calculate_shannon_entropy([0.5, 0.6])  # Sum = 1.1

        with self.assertRaises(ValueError):
            calculate_shannon_entropy([0.3, 0.3, 0.3])  # Sum = 0.9

    def test_numerical_stability(self):
        """Test numerical stability with extreme probability distributions."""
        # Create a distribution with extremely skewed probabilities
        n = 100
        probs = [0.99] + [0.01 / (n - 1)] * (n - 1)

        # This should not raise any numerical errors
        entropy = calculate_shannon_entropy(probs)

        # Expected entropy can be calculated with high precision
        p_main = 0.99
        p_others = 0.01 / (n - 1)
        expected = -(
            p_main * math.log2(p_main) + (n - 1) * p_others * math.log2(p_others)
        )

        self.assertAlmostEqual(entropy, expected, places=4)


if __name__ == "__main__":
    unittest.main()
