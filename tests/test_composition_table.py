"""
Unit tests for Allen interval relation composition table.

These tests validate that the composition table for Allen's interval algebra is:
1. Complete - all 13x13=169 compositions are defined
2. Logically consistent - follows the mathematical properties of interval algebra
3. Symmetric with respect to inverses - relation inverses behave as expected
"""

import unittest
import sys
import os
import numpy as np
from itertools import product

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from relations import (
    compose_relations,
    get_inverse_relation,
    ALLEN_RELATION_ORDER,
    generate_composition_matrix,
)


class CompositionTableTests(unittest.TestCase):
    """Test suite for Allen relation composition table."""

    def setUp(self):
        """Set up the composition matrix for testing."""
        # Get the composition data
        self.comp_data = generate_composition_matrix(format="dict", with_entropy=True)

        # Extract the composition dictionary for easier access
        self.compositions = self.comp_data["compositions"]

        # Create inverse relation mapping for testing inverse properties
        self.inverse_map = {
            rel: get_inverse_relation(rel) for rel in ALLEN_RELATION_ORDER
        }

    def test_composition_table_completeness(self):
        """Test that the composition table contains all 13x13=169 combinations."""
        # Check that every pair of relations has a defined composition
        for rel1, rel2 in product(ALLEN_RELATION_ORDER, ALLEN_RELATION_ORDER):
            key = f"{rel1},{rel2}"
            self.assertIn(key, self.compositions, f"Missing composition for {key}")

            # Check that the result is a list
            self.assertIsInstance(
                self.compositions[key],
                list,
                f"Composition result for {key} should be a list",
            )

            # Check that the result is not empty
            self.assertGreater(
                len(self.compositions[key]),
                0,
                f"Composition result for {key} should not be empty",
            )

            # Check that all results are valid relations
            for result_rel in self.compositions[key]:
                self.assertIn(
                    result_rel,
                    ALLEN_RELATION_ORDER,
                    f"Invalid relation {result_rel} in composition {key}",
                )

    def test_equals_identity_property(self):
        """Test that 'equals' acts as an identity element in composition."""
        # For every relation r, e◦r = r and r◦e = r
        equals_rel = "e"

        for rel in ALLEN_RELATION_ORDER:
            # Test e◦r = r
            e_composed_r = self.compositions[f"{equals_rel},{rel}"]
            self.assertEqual(
                len(e_composed_r),
                1,
                f"e◦{rel} should give exactly one relation, got {e_composed_r}",
            )
            self.assertEqual(
                e_composed_r[0], rel, f"e◦{rel} should equal {rel}, got {e_composed_r}"
            )

            # Test r◦e = r
            r_composed_e = self.compositions[f"{rel},{equals_rel}"]
            self.assertEqual(
                len(r_composed_e),
                1,
                f"{rel}◦e should give exactly one relation, got {r_composed_e}",
            )
            self.assertEqual(
                r_composed_e[0], rel, f"{rel}◦e should equal {rel}, got {r_composed_e}"
            )

    def test_inverse_composition_property(self):
        """
        Test the inverse property of composition.

        For any relations a and b, if a◦b = {c1,c2,...,cn},
        then (b^-1)◦(a^-1) = {(c1^-1),(c2^-1),...,(cn^-1)}
        """
        for rel1, rel2 in product(ALLEN_RELATION_ORDER, ALLEN_RELATION_ORDER):
            # Get the composition a◦b
            forward_key = f"{rel1},{rel2}"
            forward_comp = self.compositions[forward_key]

            # Compute the inverses
            inv_rel1 = self.inverse_map[rel1]
            inv_rel2 = self.inverse_map[rel2]

            # Get the composition (b^-1)◦(a^-1)
            # Note the order is reversed for inverses
            inverse_key = f"{inv_rel2},{inv_rel1}"
            inverse_comp = self.compositions[inverse_key]

            # The inverse of the compositions should match
            expected_inverse_comp = [self.inverse_map[r] for r in forward_comp]

            # Sort both lists for comparison regardless of order
            expected_inverse_comp.sort()
            inverse_comp_sorted = sorted(inverse_comp)

            self.assertEqual(
                expected_inverse_comp,
                inverse_comp_sorted,
                f"Inverse composition property failed for {forward_key} and {inverse_key}",
            )

    def test_specific_known_compositions(self):
        """Test specific compositions that have known results from the literature."""
        # Define some known composition results
        known_compositions = {
            "p,p": ["p"],  # before◦before = before
            "m,m": ["p"],  # meets◦meets = before
            "p,m": ["p"],  # before◦meets = before
            "m,p": ["p"],  # meets◦before = before
            "d,D": ["e"],  # during◦contains = equals
            "s,S": ["e"],  # starts◦started-by = equals
            "f,F": ["e"],  # finishes◦finished-by = equals
            "o,O": [
                "d",
                "s",
                "f",
                "e",
                "D",
                "S",
                "F",
            ],  # overlaps◦overlapped-by gives multiple relations
            "e,e": ["e"],  # equals◦equals = equals
        }

        for comp_key, expected_result in known_compositions.items():
            # Sort both for comparison regardless of order
            actual_result = sorted(self.compositions[comp_key])
            expected_result = sorted(expected_result)

            self.assertEqual(
                expected_result,
                actual_result,
                f"Known composition {comp_key} should be {expected_result}, got {actual_result}",
            )

    def test_composition_size_distribution(self):
        """Test the distribution of composition result sizes."""
        # Get sizes of all compositions
        sizes = [len(comp) for comp in self.compositions.values()]

        # Count how many compositions have each size
        size_counts = {}
        for size in sizes:
            size_counts[size] = size_counts.get(size, 0) + 1

        # Check theoretical constraints
        self.assertLessEqual(
            max(sizes),
            13,
            f"No composition should yield more than 13 relations, max found: {max(sizes)}",
        )

        self.assertGreaterEqual(
            min(sizes),
            1,
            f"Every composition should yield at least 1 relation, min found: {min(sizes)}",
        )

        # Check specific expectations based on interval algebra theory
        self.assertIn(
            1,  # There should be compositions that yield exactly one relation
            size_counts,
            "Expected some compositions to yield a single relation",
        )

        # Known theoretical result: there should be compositions that yield all 13 relations
        self.assertIn(
            13, size_counts, "Expected some compositions to yield all 13 relations"
        )

    def test_composition_transitivity(self):
        """Test transitivity for specific cases with known transitive closures."""
        # Test case: (p◦p)◦p = p◦(p◦p) = p
        # This tests that before is transitive: if A before B and B before C, then A before C
        comp_pp = self.compositions["p,p"]  # p◦p = p
        self.assertEqual(comp_pp, ["p"])

        comp_ppp_left = self.compositions[f"{comp_pp[0]},p"]  # (p◦p)◦p
        comp_ppp_right = self.compositions[f"p,{comp_pp[0]}"]  # p◦(p◦p)

        self.assertEqual(comp_ppp_left, ["p"])
        self.assertEqual(comp_ppp_right, ["p"])

        # Test case: (d◦d)◦d = d◦(d◦d) = d
        # This tests that during is transitive
        comp_dd = self.compositions["d,d"]  # d◦d = d
        self.assertEqual(comp_dd, ["d"])

        comp_ddd_left = self.compositions[f"{comp_dd[0]},d"]  # (d◦d)◦d
        comp_ddd_right = self.compositions[f"d,{comp_dd[0]}"]  # d◦(d◦d)

        self.assertEqual(comp_ddd_left, ["d"])
        self.assertEqual(comp_ddd_right, ["d"])

    def test_entropy_values(self):
        """Test that entropy values are calculated correctly."""
        # Check entropy array shape
        self.assertEqual(
            self.comp_data["entropy"].shape, (13, 13), "Entropy matrix should be 13x13"
        )

        # Check entropy values are non-negative
        self.assertTrue(
            np.all(self.comp_data["entropy"] >= 0),
            "All entropy values should be non-negative",
        )

        # Entropy should be 0 for compositions with a single result
        for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
            for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
                key = f"{rel1},{rel2}"
                if len(self.compositions[key]) == 1:
                    self.assertEqual(
                        self.comp_data["entropy"][i, j],
                        0.0,
                        f"Entropy for single-relation composition {key} should be 0",
                    )
                else:
                    # Entropy for uniform distribution over n outcomes is log2(n)
                    n = len(self.compositions[key])
                    expected_entropy = np.log2(n)
                    self.assertAlmostEqual(
                        self.comp_data["entropy"][i, j],
                        expected_entropy,
                        places=5,
                        msg=f"Entropy for {key} with {n} outcomes should be ~{expected_entropy}",
                    )


if __name__ == "__main__":
    unittest.main()
