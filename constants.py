# Allen relation symbols
PRECEDES = "p"  # x precedes y
MEETS = "m"  # x meets y
OVERLAPS = "o"  # x overlaps y
FINISHED_BY = "F"  # x finished by y
CONTAINS = "D"  # x contains y
STARTS = "s"  # x starts y
EQUALS = "e"  # x equals y
STARTED_BY = "S"  # x started by y
DURING = "d"  # x during y
FINISHES = "f"  # x finishes y
OVERLAPPED_BY = "O"  # x overlapped by y
MET_BY = "M"  # x met by y
PRECEDED_BY = "P"  # x preceded by y

# States for simulation
STATE_BEFORE = 0  # Before birth
STATE_DURING = 1  # During lifetime
STATE_AFTER = 2  # After death

# Canonical order of Allen relations
ALLEN_RELATIONS = [
    PRECEDES,
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
    PRECEDED_BY,
]
