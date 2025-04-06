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
