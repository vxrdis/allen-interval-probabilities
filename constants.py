# Allen relation symbols
BEFORE = "p"
MEETS = "m"
OVERLAPS = "o"
FINISHED_BY = "F"
CONTAINS = "D"
STARTS = "s"
EQUALS = "e"
STARTED_BY = "S"
DURING = "d"
FINISHES = "f"
OVERLAPPED_BY = "O"
MET_BY = "M"
AFTER = "P"

ALLEN_RELATIONS = [
    BEFORE,
    MEETS,
    OVERLAPS,
    FINISHED_BY,
    CONTAINS,
    STARTS,
    EQUALS,
    STARTED_BY,
    DURING,
    FINISHES,
    OVERLAPPED_BY,
    MET_BY,
    AFTER,
]

# English names for Allen relations
RELATION_NAMES = {
    "p": "Before",
    "m": "Meets",
    "o": "Overlaps",
    "F": "Finished By",
    "D": "Contains",
    "s": "Starts",
    "e": "Equals",
    "S": "Started By",
    "d": "During",
    "f": "Finishes",
    "O": "Overlapped By",
    "M": "Met By",
    "P": "After",
}

# Relation colors for visualization
RELATION_COLORS = {
    "p": "#1f77b4",  # Blue
    "m": "#ff7f0e",  # Orange
    "o": "#2ca02c",  # Green
    "F": "#d62728",  # Red
    "D": "#9467bd",  # Purple
    "s": "#8c564b",  # Brown
    "e": "#e377c2",  # Pink
    "S": "#7f7f7f",  # Gray
    "d": "#bcbd22",  # Yellow-green
    "f": "#17becf",  # Cyan
    "O": "#aec7e8",  # Light blue
    "M": "#ffbb78",  # Light orange
    "P": "#98df8a",  # Light green
}

# Interval states
UNBORN = 0
ALIVE = 1
DEAD = 2

# Theoretical distributions
UNIFORM_DISTRIBUTION = {rel: 1 / 13 for rel in ALLEN_RELATIONS}

FERNANDO_VOGEL_DISTRIBUTION = {
    "p": 1 / 6,
    "m": 0,
    "o": 1 / 6,
    "F": 0,
    "D": 1 / 6,
    "s": 0,
    "e": 0,
    "S": 0,
    "d": 1 / 6,
    "f": 0,
    "O": 1 / 6,
    "M": 0,
    "P": 1 / 6,
}

SULIMAN_DISTRIBUTION = {
    "p": 1 / 9,
    "m": 1 / 9,
    "o": 1 / 27,
    "F": 1 / 27,
    "D": 1 / 27,
    "s": 1 / 9,
    "e": 1 / 9,
    "S": 1 / 9,
    "d": 1 / 27,
    "f": 1 / 27,
    "O": 1 / 27,
    "M": 1 / 9,
    "P": 1 / 9,
}

# Quick sanity check for distribution sums
if __name__ == "__main__":
    for name, dist in {
        "UNIFORM": UNIFORM_DISTRIBUTION,
        "FERNANDO_VOGEL": FERNANDO_VOGEL_DISTRIBUTION,
        "SULIMAN": SULIMAN_DISTRIBUTION,
    }.items():
        print(f"{name} sum: {sum(dist.values()):.6f}")
