"""
Allen's Interval Algebra Constants

This module defines constants shared across the Allen interval algebra implementation:
- Relation colors for consistent visualization
- Relation names and their mappings
- Standard ordering of relations

These constants ensure consistency across all visualizations and analyses.
"""

# Define the specific order of relations according to Alspaugh's table
ALLEN_RELATION_ORDER = ["p", "m", "o", "F", "D", "s", "e", "S", "d", "f", "O", "M", "P"]

# Map relation codes to their formal names
RELATION_NAMES = {
    "p": "Before",  # precedes (was 'b')
    "m": "Meets",
    "o": "Overlaps",
    "F": "Finished-by",  # was 'fi'
    "D": "Contains",  # was 'di'
    "s": "Starts",
    "e": "Equals",  # was 'eq'
    "S": "Started-by",  # was 'si'
    "d": "During",  # same code
    "f": "Finishes",  # same code
    "O": "Overlapped-by",  # was 'oi'
    "M": "Met-by",  # was 'mi'
    "P": "After",  # was 'bi'
}

# Define consistent color schemes for visualization
RELATION_COLOURS = {
    "p": "#1f77b4",  # blue
    "m": "#ff7f0e",  # orange
    "o": "#2ca02c",  # green
    "F": "#d73027",  # red
    "D": "#9467bd",  # purple
    "s": "#8c564b",  # brown
    "e": "#e377c2",  # pink
    "S": "#7f7f7f",  # gray
    "d": "#bcbd22",  # olive
    "f": "#17becf",  # cyan
    "O": "#aec7e8",  # light blue
    "M": "#ffbb78",  # light orange
    "P": "#98df8a",  # light green
}


def get_relation_name(rel_code):
    """
    Get the formal name of an Allen relation from its Alspaugh code.

    Args:
        rel_code: Relation code (p, m, o, etc.)

    Returns:
        The formal name of the relation or "Unknown relation" if not found
    """
    return RELATION_NAMES.get(rel_code, f"Unknown relation '{rel_code}'")


def get_inverse_relation(rel_code):
    """
    Get the inverse of a relation using Alspaugh's uppercase/lowercase pairing.

    Args:
        rel_code: Relation code to find inverse for

    Returns:
        The inverse relation code, or None if not found
    """
    if rel_code == "e":  # equals is self-inverse
        return "e"
    elif rel_code.islower():  # lowercase -> uppercase inverse
        return rel_code.upper()
    elif rel_code.isupper():  # lowercase -> uppercase inverse
        return rel_code.lower()
    else:
        return None
