import math
from scipy import stats
import constants as c


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


def combineInv(dic):
    temp = {}
    temp[c.PRECEDES] = dic.get(c.PRECEDES, 0) + dic.get(c.PRECEDED_BY, 0)
    temp[c.MEETS] = dic.get(c.MEETS, 0) + dic.get(c.MET_BY, 0)
    temp[c.OVERLAPS] = dic.get(c.OVERLAPS, 0) + dic.get(c.OVERLAPPED_BY, 0)
    temp[c.FINISHED_BY] = dic.get(c.FINISHED_BY, 0)
    temp[c.CONTAINS] = dic.get(c.CONTAINS, 0)
    temp[c.STARTS] = dic.get(c.STARTS, 0) + dic.get(c.STARTED_BY, 0)
    temp[c.EQUALS] = dic.get(c.EQUALS, 0)
    temp[c.STARTED_BY] = dic.get(c.STARTED_BY, 0)
    temp[c.DURING] = dic.get(c.DURING, 0) + dic.get(c.CONTAINS, 0)
    temp[c.FINISHES] = dic.get(c.FINISHES, 0)
    temp[c.OVERLAPPED_BY] = dic.get(c.OVERLAPPED_BY, 0)
    temp[c.MET_BY] = dic.get(c.MET_BY, 0)
    temp[c.PRECEDED_BY] = dic.get(c.PRECEDED_BY, 0)
    return temp


def describe(counts):
    return {
        "entropy": entropy(counts),
        "chi_square_p_value": chi_square_uniform(counts),
        "pms_od_ratio": point_meet_start_vs_overlap_during(counts),
        "total_count": sum(counts.values()),
    }
