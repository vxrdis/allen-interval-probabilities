"""
Unit tests for Allen interval relation identification functions.

These tests validate the accuracy of the identify_relation function,
ensuring it correctly identifies all 13 Allen relations based on
different endpoint sequences.
"""

import unittest
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from relations import identify_relation, l, r


class RelationIdentificationTests(unittest.TestCase):
    """Test suite for relation identification functions."""

    def setUp(self):
        """Set up common endpoint functions for different intervals."""
        # Create endpoints for different intervals
        self.la, self.ra = l("a"), r("a")  # Interval a endpoints
        self.lb, self.rb = l("b"), r("b")  # Interval b endpoints
        self.lx, self.rx = l("x"), r("x")  # Interval x endpoints
        self.ly, self.ry = l("y"), r("y")  # Interval y endpoints

    def test_precedes_relation(self):
        """Test identification of 'precedes' (p) relation."""
        # a precedes b: la < ra < lb < rb
        sequence = [{self.la}, {self.ra}, {self.lb}, {self.rb}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "p", "Failed to identify precedes relation")

        # Test with different interval labels
        sequence = [{self.lx}, {self.rx}, {self.ly}, {self.ry}]
        relation = identify_relation(sequence, "x", "y")
        self.assertEqual(
            relation, "p", "Failed to identify precedes relation with different labels"
        )

    def test_meets_relation(self):
        """Test identification of 'meets' (m) relation."""
        # a meets b: la < ra = lb < rb
        sequence = [{self.la}, {self.ra, self.lb}, {self.rb}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "m", "Failed to identify meets relation")

    def test_overlaps_relation(self):
        """Test identification of 'overlaps' (o) relation."""
        # a overlaps b: la < lb < ra < rb
        sequence = [{self.la}, {self.lb}, {self.ra}, {self.rb}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "o", "Failed to identify overlaps relation")

    def test_during_relation(self):
        """Test identification of 'during' (d) relation."""
        # a during b: lb < la < ra < rb
        sequence = [{self.lb}, {self.la}, {self.ra}, {self.rb}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "d", "Failed to identify during relation")

    def test_starts_relation(self):
        """Test identification of 'starts' (s) relation."""
        # a starts b: la = lb < ra < rb
        sequence = [{self.la, self.lb}, {self.ra}, {self.rb}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "s", "Failed to identify starts relation")

    def test_finishes_relation(self):
        """Test identification of 'finishes' (f) relation."""
        # a finishes b: lb < la < ra = rb
        sequence = [{self.lb}, {self.la}, {self.ra, self.rb}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "f", "Failed to identify finishes relation")

    def test_equals_relation(self):
        """Test identification of 'equals' (e) relation."""
        # a equals b: la = lb < ra = rb
        sequence = [{self.la, self.lb}, {self.ra, self.rb}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "e", "Failed to identify equals relation")

    def test_preceded_by_relation(self):
        """Test identification of 'preceded by' (P) relation."""
        # a preceded by b: lb < rb < la < ra
        sequence = [{self.lb}, {self.rb}, {self.la}, {self.ra}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "P", "Failed to identify preceded by relation")

    def test_met_by_relation(self):
        """Test identification of 'met by' (M) relation."""
        # a met by b: lb < rb = la < ra
        sequence = [{self.lb}, {self.rb, self.la}, {self.ra}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "M", "Failed to identify met by relation")

    def test_overlapped_by_relation(self):
        """Test identification of 'overlapped by' (O) relation."""
        # a overlapped by b: lb < la < rb < ra
        sequence = [{self.lb}, {self.la}, {self.rb}, {self.ra}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "O", "Failed to identify overlapped by relation")

    def test_contains_relation(self):
        """Test identification of 'contains' (D) relation."""
        # a contains b: la < lb < rb < ra
        sequence = [{self.la}, {self.lb}, {self.rb}, {self.ra}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "D", "Failed to identify contains relation")

    def test_started_by_relation(self):
        """Test identification of 'started by' (S) relation."""
        # a started by b: la = lb < rb < ra
        sequence = [{self.la, self.lb}, {self.rb}, {self.ra}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "S", "Failed to identify started by relation")

    def test_finished_by_relation(self):
        """Test identification of 'finished by' (F) relation."""
        # a finished by b: la < lb < ra = rb
        sequence = [{self.la}, {self.lb}, {self.ra, self.rb}]
        relation = identify_relation(sequence, "a", "b")
        self.assertEqual(relation, "F", "Failed to identify finished by relation")

    def test_symmetry_of_inverse_relations(self):
        """Test that swapping intervals produces the inverse relation."""
        # Test all relation pairs
        relation_pairs = [
            # (sequence for a rel b, relation, inverse relation)
            (
                [{self.la}, {self.ra}, {self.lb}, {self.rb}],
                "p",
                "P",
            ),  # precedes/preceded-by
            ([{self.la}, {self.ra, self.lb}, {self.rb}], "m", "M"),  # meets/met-by
            (
                [{self.la}, {self.lb}, {self.ra}, {self.rb}],
                "o",
                "O",
            ),  # overlaps/overlapped-by
            ([{self.lb}, {self.la}, {self.ra}, {self.rb}], "d", "D"),  # during/contains
            ([{self.la, self.lb}, {self.ra}, {self.rb}], "s", "S"),  # starts/started-by
            (
                [{self.lb}, {self.la}, {self.ra, self.rb}],
                "f",
                "F",
            ),  # finishes/finished-by
            (
                [{self.la, self.lb}, {self.ra, self.rb}],
                "e",
                "e",
            ),  # equals (self-inverse)
        ]

        for sequence, rel, inverse_rel in relation_pairs:
            # Test forward relation
            self.assertEqual(
                identify_relation(sequence, "a", "b"),
                rel,
                f"Failed to identify {rel} relation",
            )

            # Test inverse relation by swapping interval labels
            self.assertEqual(
                identify_relation(sequence, "b", "a"),
                inverse_rel,
                f"Failed to identify {inverse_rel} as inverse of {rel}",
            )

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Empty sequence
        with self.assertRaises(Exception):
            identify_relation([], "a", "b")

        # Sequence with unexpected structure
        with self.assertRaises(Exception):
            identify_relation([{self.la}], "a", "b")  # Too short

        # Sequence with unknown interval endpoints
        unknown_sequence = [{l("c")}, {r("c")}, {l("d")}, {r("d")}]
        with self.assertRaises(Exception):
            # Trying to identify relation between a and b using c and d endpoints
            identify_relation(unknown_sequence, "a", "b")

    def test_relation_completeness(self):
        """Test that all 13 Allen relations are correctly identified."""
        # Dictionary mapping each endpoint sequence pattern to expected relation
        sequences = {
            # Sequence pattern: expected relation
            "la,ra,lb,rb": "p",  # precedes
            "la,ralb,rb": "m",  # meets (ra=lb)
            "la,lb,ra,rb": "o",  # overlaps
            "lb,la,ra,rb": "d",  # during
            "lalb,ra,rb": "s",  # starts (la=lb)
            "lb,la,rarb": "f",  # finishes (ra=rb)
            "lalb,rarb": "e",  # equals (la=lb, ra=rb)
            "lb,rb,la,ra": "P",  # preceded by
            "lb,rbla,ra": "M",  # met by (rb=la)
            "lb,la,rb,ra": "O",  # overlapped by
            "la,lb,rb,ra": "D",  # contains
            "lalb,rb,ra": "S",  # started by (la=lb)
            "la,lb,rarb": "F",  # finished by (ra=rb)
        }

        # Test each sequence pattern
        for seq_pattern, expected_rel in sequences.items():
            # Convert pattern to actual sequence
            sequence = self._pattern_to_sequence(seq_pattern)
            relation = identify_relation(sequence, "a", "b")
            self.assertEqual(
                relation,
                expected_rel,
                f"Failed to identify {expected_rel} relation from pattern {seq_pattern}",
            )

    def _pattern_to_sequence(self, pattern):
        """Convert a string pattern to an endpoint sequence."""
        # Dictionary to map combined endpoints like "ralb" to sets of endpoints
        endpoint_map = {
            "la": self.la,
            "ra": self.ra,
            "lb": self.lb,
            "rb": self.rb,
            "lalb": {self.la, self.lb},
            "rarb": {self.ra, self.rb},
            "ralb": {self.ra, self.lb},
            "rbla": {self.rb, self.la},
        }

        # Split pattern by comma and convert to endpoint sets
        sequence = []
        for part in pattern.split(","):
            if part in endpoint_map:
                # If it's a simple endpoint or a known combined endpoint
                endpoint = endpoint_map[part]
                sequence.append(
                    {endpoint} if not isinstance(endpoint, set) else endpoint
                )
            else:
                # For any combined endpoints not in our map
                endpoints = set()
                if "la" in part:
                    endpoints.add(self.la)
                if "ra" in part:
                    endpoints.add(self.ra)
                if "lb" in part:
                    endpoints.add(self.lb)
                if "rb" in part:
                    endpoints.add(self.rb)
                sequence.append(endpoints)

        return sequence


if __name__ == "__main__":
    unittest.main()
