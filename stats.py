import math
from scipy import stats


def entropy(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0

    probs = [count / total for count in counts.values() if count > 0]
    return -sum(p * math.log2(p) for p in probs)


def chi_square_uniform(counts):
    observed = list(counts.values())
    n = len(observed)
    if n <= 1 or sum(observed) == 0:
        return 1.0

    expected = [sum(observed) / n] * n

    chi2, p_value = stats.chisquare(observed, expected)
    return p_value


def point_meet_start_vs_overlap_during(counts):
    pms_sum = sum(counts.get(rel, 0) for rel in ["p", "m", "s"])
    od_sum = sum(counts.get(rel, 0) for rel in ["o", "d"])

    if od_sum == 0:
        return float("inf")

    return pms_sum / od_sum


def describe(counts):
    return {
        "entropy": entropy(counts),
        "chi_square_p_value": chi_square_uniform(counts),
        "pms_od_ratio": point_meet_start_vs_overlap_during(counts),
        "total_count": sum(counts.values()),
    }
