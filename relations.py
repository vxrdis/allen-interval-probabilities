"""
Allen's Interval Algebra Implementation (1983)

This module implements Allen's Interval Algebra (1983) as reinterpreted by Thomas Alspaugh.
The relation codes and ordering follow Alspaugh's Table 1 and Table 4a.

Allen's approach represents temporal knowledge using binary relations between time intervals
rather than points. Each relation has a specific meaning based on the relative positions of
interval endpoints. The framework supports composition operations to derive new relations.

References:
- James F. Allen (1983). "Maintaining knowledge about temporal intervals".
  Communications of the ACM, 26(11), 832-843.
- Thomas Alspaugh: Allen's Interval Algebra
  https://thomasalspaugh.org/pub/fnd/allen.html
"""

# Import constants from the central constants file
from constants import (
    ALLEN_RELATION_ORDER,
    RELATION_NAMES,
    get_relation_name,
)


def l(x):
    """Generate a left endpoint identifier for interval x."""
    return f"l{x}"


def r(x):
    """Generate a right endpoint identifier for interval x."""
    return f"r{x}"


# Cache for relation maps to avoid rebuilding on each call to identify_relation()
_relation_map_cache = {}


def to_canonical_form(config):
    """
    Convert a list of sets to a tuple of frozensets for reliable comparison.

    Used for canonicalizing endpoint configurations.

    Args:
        config: A list of sets representing endpoint configurations

    Returns:
        A tuple of frozen sets (hashable for dictionary keys)
    """
    return tuple(frozenset(s) for s in config)


def get_inverse_relation(rel_code):
    """
    Get the inverse of a relation using Alspaugh's uppercase/lowercase pairing.

    Inverse relations follow a systematic pattern in Alspaugh's notation:
    - Lowercase and uppercase versions of the same letter are inverses of each other
      (e.g., p <-> P, m <-> M, o <-> O, s <-> S, d <-> D, f <-> F)
    - The 'equals' relation (e) is its own inverse

    This pattern makes inverses easy to compute by simply changing case.

    Args:
        rel_code: Relation code to find inverse for

    Returns:
        The inverse relation code, or None if not found
    """
    if rel_code == "e":  # equals is self-inverse
        return "e"
    elif rel_code.islower():  # lowercase -> uppercase inverse (e.g., p -> P)
        return rel_code.upper()
    elif rel_code.isupper():  # uppercase -> lowercase inverse (e.g., P -> p)
        return rel_code.lower()
    else:
        return None


# ----- Allen's 13 basic relations as endpoint configurations -----


def allen_relation(x, y, rel):
    """
    Define Allen's interval relation between intervals x and y, using Alspaugh's notation.

    Each relation is represented as a sequence of endpoint events, where:
    - l(x): left endpoint of interval x
    - r(x): right endpoint of interval x

    The 13 Allen relations form 6 pairs of inverses plus the self-inverse "equals" relation.
    In Alspaugh's notation, inverses are represented by case transformation:
    - p (precedes) <-> P (preceded-by / after)
    - m (meets) <-> M (met-by)
    - o (overlaps) <-> O (overlapped-by)
    - F (finished-by) <-> f (finishes)
    - D (contains) <-> d (during)
    - s (starts) <-> S (started-by)
    - e (equals) is its own inverse

    Args:
        x: First interval identifier
        y: Second interval identifier
        rel: Relation code (p, m, o, F, D, s, e, S, d, f, O, M, P)

    Returns:
        A list of sets, where each set represents coinciding endpoints.

    Raises:
        ValueError: If the relation code is not recognised
    """
    lx, rx = l(x), r(x)
    ly, ry = l(y), r(y)

    # Define all 13 Allen relations using endpoint configurations with Alspaugh's codes
    relations = {
        # Basic relations (following Alspaugh's order with inverses noted)
        "p": [{lx}, {rx}, {ly}, {ry}],
        # p (precedes): x entirely precedes y (inverse: P - preceded-by)
        # Endpoint order: lx < rx < ly < ry
        "m": [{lx}, {rx, ly}, {ry}],
        # m (meets): x's right endpoint coincides with y's left endpoint (inverse: M - met-by)
        # Endpoint order: lx < (rx = ly) < ry
        "o": [{lx}, {ly}, {rx}, {ry}],
        # o (overlaps): x starts before y, they overlap, and x ends before y ends (inverse: O - overlapped-by)
        # Endpoint order: lx < ly < rx < ry
        "F": [{lx}, {ly}, {rx, ry}],
        # F (finished-by): x starts before y, but they end at the same time (inverse: f - finishes)
        # Endpoint order: lx < ly < (rx = ry)
        "D": [{lx}, {ly}, {ry}, {rx}],
        # D (contains): x fully contains y (inverse: d - during)
        # Endpoint order: lx < ly < ry < rx
        "s": [{lx, ly}, {rx}, {ry}],
        # s (starts): x and y start at the same time, but x ends before y (inverse: S - started-by)
        # Endpoint order: (lx = ly) < rx < ry
        "e": [{lx, ly}, {rx, ry}],
        # e (equals): x and y are identical intervals (self-inverse)
        # Endpoint order: (lx = ly) < (rx = ry)
        "S": [{lx, ly}, {ry}, {rx}],
        # S (started-by): x and y start at the same time, but y ends before x (inverse: s - starts)
        # Endpoint order: (lx = ly) < ry < rx
        "d": [{ly}, {lx}, {rx}, {ry}],
        # d (during): x is fully contained within y (inverse: D - contains)
        # Endpoint order: ly < lx < rx < ry
        "f": [{ly}, {lx}, {rx, ry}],
        # f (finishes): x starts after y starts, but they end at the same time (inverse: F - finished-by)
        # Endpoint order: ly < lx < (rx = ry)
        "O": [{ly}, {lx}, {ry}, {rx}],
        # O (overlapped-by): y starts before x, they overlap, and y ends before x (inverse: o - overlaps)
        # Endpoint order: ly < lx < ry < rx
        "M": [{ly}, {ry, lx}, {rx}],
        # M (met-by): y's right endpoint coincides with x's left endpoint (inverse: m - meets)
        # Endpoint order: ly < (ry = lx) < rx
        "P": [{ly}, {ry}, {lx}, {rx}],
        # P (preceded-by/after): y entirely precedes x (inverse: p - precedes)
        # Endpoint order: ly < ry < lx < rx
    }

    if rel not in relations:
        raise ValueError(
            f"Unknown relation code: '{rel}'. Valid codes are: {', '.join(ALLEN_RELATION_ORDER)}"
        )

    return relations[rel]


def identify_relation(endpoint_sequence, x, y):
    """
    Identify which Allen relation corresponds to the given endpoint sequence,
    using Alspaugh's notation.

    Args:
        endpoint_sequence: A list of sets representing endpoint configurations
        x: First interval identifier
        y: Second interval identifier

    Returns:
        The relation code (string) if found, None otherwise
    """
    # Create a cache key from the interval identifiers
    cache_key = (x, y)

    # Try to get the relation map from cache first
    relation_map = _relation_map_cache.get(cache_key)

    # If not in cache, build the relation map
    if relation_map is None:
        lx, rx = l(x), r(x)
        ly, ry = l(y), r(y)

        # Define lookup map using canonical forms of endpoint configurations
        relation_map = {
            # Basic relations (following Alspaugh's order)
            to_canonical_form([{lx}, {rx}, {ly}, {ry}]): "p",  # Before (precedes)
            to_canonical_form([{lx}, {rx, ly}, {ry}]): "m",  # Meets
            to_canonical_form([{lx}, {ly}, {rx}, {ry}]): "o",  # Overlaps
            to_canonical_form([{lx}, {ly}, {rx, ry}]): "F",  # Finished-by
            to_canonical_form([{lx}, {ly}, {ry}, {rx}]): "D",  # Contains
            to_canonical_form([{lx, ly}, {rx}, {ry}]): "s",  # Starts
            to_canonical_form([{lx, ly}, {rx, ry}]): "e",  # Equals
            to_canonical_form([{lx, ly}, {ry}, {rx}]): "S",  # Started-by
            to_canonical_form([{ly}, {lx}, {rx}, {ry}]): "d",  # During
            to_canonical_form([{ly}, {lx}, {rx, ry}]): "f",  # Finishes
            to_canonical_form([{ly}, {lx}, {ry}, {rx}]): "O",  # Overlapped-by
            to_canonical_form([{ly}, {ry, lx}, {rx}]): "M",  # Met-by
            to_canonical_form([{ly}, {ry}, {lx}, {rx}]): "P",  # After (preceded-by)
        }

        # Store in cache for future use
        _relation_map_cache[cache_key] = relation_map

    # Convert input endpoint sequence to canonical form for lookup
    canonical_input = to_canonical_form(endpoint_sequence)

    # Return the relation code or None if not found
    return relation_map.get(canonical_input)


def are_inverse_relations(rel1, rel2):
    """
    Check if two relations are inverses of each other using Alspaugh's notation.

    Inverse relations in Alspaugh's notation have opposite case:
    - p <-> P, m <-> M, o <-> O, etc.
    - e is self-inverse (e <-> e)

    Args:
        rel1: First relation code
        rel2: Second relation code

    Returns:
        True if the relations are inverses, False otherwise
    """
    return get_inverse_relation(rel1) == rel2


def list_all_relations(ordered=True):
    """
    Return a list of all 13 Allen relation codes.

    Args:
        ordered: If True, return relations in Alspaugh's order

    Returns:
        List of relation codes
    """
    if ordered:
        return ALLEN_RELATION_ORDER
    else:
        return list(RELATION_NAMES.keys())


def get_vocabulary(string):
    """
    Extract all unique elements from a sequence of sets.

    Used to determine the "vocabulary" (all endpoint markers) in a sequence.
    """
    if len(string) == 0:
        return set()
    else:
        # Union of the first set with vocabulary of the rest
        return string[0].union(get_vocabulary(string[1:]))


def project(sequence, target_set):
    """
    Project a sequence onto a target set, keeping only elements in the intersection.
    Removes any empty sets created by the projection.

    Used to extract the endpoint sequence for specific intervals after superposition.
    """
    if len(sequence) == 0:
        return sequence
    else:
        # Get intersection of first element with target set
        h1 = sequence[0].intersection(target_set)
        if len(h1) == 0:
            # Skip this element if intersection is empty
            return project(sequence[1:], target_set)
        else:
            # Keep this element and continue with the rest
            return [h1] + project(sequence[1:], target_set)


# ----- Superposition Operation -----


def superpose(seq1, seq2, voc1, voc2):
    """
    Superpose two sequences of sets (representing endpoint configurations).

    This is the core operation that allows computing compositions of Allen relations
    as described in Allen's original paper and formalised in Alspaugh's tables.

    It merges two endpoint sequences while preserving their relative order constraints,
    which is essential for determining the possible relations that can hold between
    intervals x and z when we know x rel1 y and y rel2 z.

    Args:
        seq1: First endpoint sequence
        seq2: Second endpoint sequence
        voc1: Set of all endpoints in seq1
        voc2: Set of all endpoints in seq2

    Returns:
        List of all possible merged endpoint sequences
    """
    if len(seq1) == 0 and len(seq2) == 0:
        # Base case: both sequences are empty
        return [seq1]
    else:
        results = []

        # Case 1: Take from first sequence
        if len(seq1) > 0:
            head1 = seq1[0]
            tail1 = seq1[1:]
            head1_in_voc2 = head1.intersection(voc2)

            if len(head1_in_voc2) == 0:
                # If head1 has no elements from voc2, we can safely take it
                for res in superpose(tail1, seq2, voc1, voc2):
                    results.append([head1] + res)

            # Try to merge heads if possible
            if len(seq2) > 0:
                head2 = seq2[0]
                tail2 = seq2[1:]
                merged_head = head1.union(head2)

                # Check if elements from head1 that are in voc2 are a subset of head2
                # and if elements from head2 that are in voc1 are a subset of head1
                if head1_in_voc2.issubset(head2) and head2.intersection(voc1).issubset(
                    head1
                ):
                    for res in superpose(tail1, tail2, voc1, voc2):
                        results.append([merged_head] + res)

        # Case 2: Take from second sequence
        if len(seq2) > 0:
            head2 = seq2[0]
            tail2 = seq2[1:]
            head2_in_voc1 = head2.intersection(voc1)

            if len(head2_in_voc1) == 0:
                # If head2 has no elements from voc1, we can safely take it
                for res in superpose(seq1, tail2, voc1, voc2):
                    results.append([head2] + res)

        return results


def superpose_relations(seq1, seq2):
    """
    Wrapper around superpose that automatically computes vocabularies.

    This function is used to combine two endpoint sequences representing Allen relations.
    """
    return superpose(seq1, seq2, get_vocabulary(seq1), get_vocabulary(seq2))


# ----- Composition of Allen Relations -----


def compose_relations(rel1, rel2, x=0, y=1, z=2):
    """
    Compute the composition (rel1 ∘ rel2) of two Allen relations using Alspaugh's notation.

    Given x rel1 y and y rel2 z, determines what relation(s) hold between x and z.
    This implements the composition operation shown in Alspaugh's Table 4a.

    Args:
        rel1: First relation code using Alspaugh's notation
        rel2: Second relation code using Alspaugh's notation
        x, y, z: Interval identifiers

    Returns:
        A list of possible relations between x and z
    """
    # Convert relation names to endpoint sequences
    seq1 = allen_relation(x, y, rel1)  # represents x rel1 y
    seq2 = allen_relation(y, z, rel2)  # represents y rel2 z

    # Result will contain all possible relations between x and z
    result = []

    # Superpose the two sequences
    superposed = superpose_relations(seq1, seq2)

    # Extract relations between x and z by projecting onto their endpoints
    for s in superposed:
        # We only care about endpoints of x and z
        relevant_endpoints = {l(x), r(x), l(z), r(z)}
        projected = project(s, relevant_endpoints)
        relation = identify_relation(projected, x, z)
        if relation and relation not in result:
            result.append(relation)

    # Return results in the official Alspaugh ordering
    return sorted(
        result,
        key=lambda r: (
            ALLEN_RELATION_ORDER.index(r) if r in ALLEN_RELATION_ORDER else 999
        ),
    )


def print_composition(rel1, rel2):
    """
    Display the composition process in detail, using Alspaugh's notation.

    Provides a step-by-step explanation of how the composition is computed.

    Args:
        rel1: First relation code
        rel2: Second relation code

    Returns:
        List of result relations (ordered according to Alspaugh's table)
    """
    x, y, z = 0, 1, 2
    seq1 = allen_relation(x, y, rel1)
    seq2 = allen_relation(y, z, rel2)

    print(
        f"Computing composition {rel1} ∘ {rel2} ({get_relation_name(rel1)} ∘ {get_relation_name(rel2)}):"
    )
    print(f"  {seq1} (representing x {rel1} y)")
    print(f"  {seq2} (representing y {rel2} z)")
    print("-" * 60)

    result = []
    for s in superpose_relations(seq1, seq2):
        relevant_endpoints = {l(x), r(x), l(z), r(z)}
        projected = project(s, relevant_endpoints)
        relation = identify_relation(projected, x, z)
        if relation and relation not in result:
            result.append(relation)
        print(f"  Superposition: {s}")
        print(f"  Projection to x,z endpoints: {projected}")
        print(f"  Yields relation: x {relation} ({get_relation_name(relation)}) z")
        print()

    # Sort the results according to Alspaugh's ordering
    ordered_result = sorted(
        result,
        key=lambda r: (
            ALLEN_RELATION_ORDER.index(r) if r in ALLEN_RELATION_ORDER else 999
        ),
    )

    print("-" * 60)
    print(f"Result: {rel1} ∘ {rel2} = {ordered_result}")
    print(
        f"In words: {get_relation_name(rel1)} ∘ {get_relation_name(rel2)} = "
        + ", ".join([get_relation_name(r) for r in ordered_result])
    )

    return ordered_result


# ----- Composition Table Generation -----


def generate_composition_matrix(format="dict", with_entropy=False):
    """
    Generate a composition matrix for Allen's interval relations.

    This function computes all possible compositions of Allen relations
    and returns them in the specified format. It can be used for both
    theoretical analysis and visualization purposes.

    Args:
        format: Output format - either "dict" (default) or "array"
        with_entropy: If True, also calculate entropy values for each composition

    Returns:
        If format="dict":
            Dictionary with keys: "compositions", "cardinality", and optionally "entropy"
        If format="array":
            NumPy array where cell [i,j] contains composition of relations i and j
    """
    import numpy as np
    from shared_utils import calculate_shannon_entropy

    n = len(ALLEN_RELATION_ORDER)
    compositions = {}  # Store raw composition results

    if format == "array":
        # Create a numpy array to hold composition results
        matrix = np.empty((n, n), dtype=object)

    # Calculate cardinality and entropy matrices if needed
    cardinality_matrix = np.zeros((n, n))
    entropy_matrix = np.zeros((n, n)) if with_entropy else None

    # Compute compositions for all relation pairs
    for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
        for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
            # Get composition result
            result = compose_relations(rel1, rel2)

            # Store in appropriate format
            key = (rel1, rel2)
            compositions[key] = result

            if format == "array":
                matrix[i, j] = result

            # Calculate metadata
            cardinality_matrix[i, j] = len(result)

            if with_entropy and len(result) > 0:
                # Calculate entropy with uniform distribution over possible outcomes
                uniform_p = 1.0 / len(result)
                probs = [uniform_p] * len(result)
                entropy_matrix[i, j] = calculate_shannon_entropy(probs)

    # Return results in requested format
    if format == "array":
        return matrix
    else:
        result = {
            "compositions": compositions,
            "cardinality": cardinality_matrix,
        }

        if with_entropy:
            result["entropy"] = entropy_matrix

        return result


def generate_composition_table():
    """
    Generate the complete Allen relation composition table using Alspaugh's notation.

    This produces a table equivalent to Alspaugh's Table 4a.

    Returns:
        Dictionary mapping relation pairs to composition results
    """
    # Use the more general function with appropriate defaults
    result = generate_composition_matrix(format="dict")
    return result["compositions"]


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("Allen's Interval Algebra (using Thomas Alspaugh's notation)")
    print("=" * 80)
    print()

    # Show all relations in Alspaugh's order
    print("Allen's 13 relations in Alspaugh's order:")
    print("  Relation        Name           Inverse Relation")
    print("  ---------------------------------------------")
    for rel in ALLEN_RELATION_ORDER:
        inverse = get_inverse_relation(rel)
        print(
            f"  {rel:<2}: {get_relation_name(rel):<12} <-> {inverse}: {get_relation_name(inverse)}"
        )
    print()

    # Check if all inverses are consistent
    print("Verifying inverse relation consistency:")
    all_consistent = True
    for rel in ALLEN_RELATION_ORDER:
        inverse = get_inverse_relation(rel)
        if get_inverse_relation(inverse) != rel:
            print(
                f"  Inconsistency detected: {rel} <-> {inverse}, but {inverse} <-> {get_inverse_relation(inverse)}"
            )
            all_consistent = False
    if all_consistent:
        print("  All inverse relations are consistent!")

    # Example: Compute composition of "precedes" and "during"
    print("=" * 80)
    print("Example: Detailed computation of relation composition")
    print("=" * 80)
    print_composition("p", "d")  # precedes ∘ during
    print()

    # Example 2: One more example
    print("=" * 80)
    print("Example 2: Another relation composition")
    print("=" * 80)
    print_composition("o", "m")  # overlaps ∘ meets
    print()

    # Uncomment to generate full composition table
    # print("=" * 80)
    # print("Allen relation composition table (Alspaugh's Table 4a):")
    # print("=" * 80)
    # table = generate_composition_table()
    # for rel1 in ALLEN_RELATION_ORDER:
    #     for rel2 in ALLEN_RELATION_ORDER:
    #         result = table[(rel1, rel2)]
    #         print(f"{rel1} ∘ {rel2} = {result}")
