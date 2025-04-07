import math
import numpy as np
from scipy import stats
from scipy.spatial.distance import jensenshannon
import constants as c


# ===============================================
# GLOBAL DISTRIBUTION STATISTICS
# ===============================================


def apply_laplace_smoothing(counts, epsilon=1e-8):
    return {rel: counts.get(rel, 0) + epsilon for rel in c.ALLEN_RELATIONS}


def entropy(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = [v / total for v in counts.values() if v > 0]
    return -sum(p * math.log2(p) for p in probs)


def gini(counts):
    values = np.array(list(counts.values()))
    if values.sum() == 0:
        return 0.0
    sorted_vals = np.sort(values)
    n = len(values)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * sorted_vals)) / (n * np.sum(sorted_vals)) - (n + 1) / n


def coverage(counts):
    return sum(1 for v in counts.values() if v > 0)


def mode_relation(counts):
    return max(counts.items(), key=lambda x: x[1])[0] if counts else None


def stddev(counts):
    values = list(counts.values())
    return float(np.std(values)) if values else 0.0


def chi_square_uniform(counts):
    observed = list(counts.values())
    n = len(observed)
    if n <= 1 or sum(observed) == 0:
        return 1.0
    expected = [max(sum(observed) / n, 1e-6)] * n
    _, p = stats.chisquare(observed, expected)
    return p


def chi_square_against_theory(observed, expected_probs):
    total = sum(observed.values())
    if total == 0:
        return 1.0

    obs = []
    expected = []

    for rel in c.ALLEN_RELATIONS:
        o = observed.get(rel, 0)
        e = expected_probs.get(rel, 0) * total
        if e > 0:
            obs.append(o)
            expected.append(e)

    scale = sum(obs) / sum(expected)
    expected = [e * scale for e in expected]

    try:
        _, p = stats.chisquare(obs, expected)
    except:
        p = 1.0

    return p


def kl_divergence(observed, expected_dict):
    total = sum(observed.values())
    if total == 0:
        return 0.0
    obs = [max(observed.get(rel, 0) / total, 1e-10) for rel in c.ALLEN_RELATIONS]
    exp = [max(expected_dict.get(rel, 0), 1e-10) for rel in c.ALLEN_RELATIONS]
    return float(stats.entropy(obs, exp))


def js_divergence(observed, expected_dict):
    total = sum(observed.values())
    if total == 0:
        return 0.0
    obs = np.array([observed.get(rel, 0) / total for rel in c.ALLEN_RELATIONS])
    exp = np.array([expected_dict.get(rel, 0) for rel in c.ALLEN_RELATIONS])
    epsilon = 1e-10
    obs = np.clip(obs, epsilon, 1)
    exp = np.clip(exp, epsilon, 1)
    return float(jensenshannon(obs, exp) ** 2)


def describe_global(counts, expected_dict=None, smooth=False):
    if smooth:
        counts = apply_laplace_smoothing(counts)

    return {
        "entropy": entropy(counts),
        "gini": gini(counts),
        "coverage": coverage(counts),
        "mode": mode_relation(counts),
        "stddev": stddev(counts),
        "chi_square_uniform": chi_square_uniform(counts),
        "chi_square_theory": (
            chi_square_against_theory(counts, expected_dict) if expected_dict else None
        ),
        "kl_divergence": (
            kl_divergence(counts, expected_dict) if expected_dict else None
        ),
        "js_divergence": (
            js_divergence(counts, expected_dict) if expected_dict else None
        ),
        "total_count": sum(counts.values()),
    }


# ===============================================
# COMPOSITION TABLE CELL STATISTICS
# ===============================================


def normalized_entropy(counts):
    max_entropy = math.log2(len([v for v in counts.values() if v > 0]) or 1)
    return entropy(counts) / max_entropy if max_entropy > 0 else 0.0


def top_k(counts, k=3):
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:k]


def describe_cell(counts):
    return {
        "entropy": entropy(counts),
        "normalized_entropy": normalized_entropy(counts),
        "gini": gini(counts),
        "coverage": coverage(counts),
        "top_3": top_k(counts, k=3),
        "mode": mode_relation(counts),
        "stddev": stddev(counts),
        "total_count": sum(counts.values()),
    }


if __name__ == "__main__":
    dummy = {rel: i for i, rel in enumerate(c.ALLEN_RELATIONS)}
    print(describe_global(dummy))
    print(describe_cell(dummy))


# ===============================================
# LEGACY / EXPERIMENTAL (disabled for now)
# ===============================================

# def precedes_meet_start_vs_overlap_during(counts):
#     pms = sum(counts.get(rel, 0) for rel in ["p", "m", "s"])
#     od = sum(counts.get(rel, 0) for rel in ["o", "d"])
#     return float("inf") if od == 0 else pms / od

# def combineInv(dic):
#     return {
#         c.BEFORE: dic.get(c.BEFORE, 0) + dic.get(c.AFTER, 0),
#         c.MEETS: dic.get(c.MEETS, 0) + dic.get(c.MET_BY, 0),
#         c.OVERLAPS: dic.get(c.OVERLAPS, 0) + dic.get(c.OVERLAPPED_BY, 0),
#         c.FINISHED_BY: dic.get(c.FINISHED_BY, 0),
#         c.CONTAINS: dic.get(c.CONTAINS, 0),
#         c.STARTS: dic.get(c.STARTS, 0) + dic.get(c.STARTED_BY, 0),
#         c.EQUALS: dic.get(c.EQUALS, 0),
#         c.STARTED_BY: dic.get(c.STARTED_BY, 0),
#         c.DURING: dic.get(c.DURING, 0) + dic.get(c.CONTAINS, 0),
#         c.FINISHES: dic.get(c.FINISHES, 0),
#         c.OVERLAPPED_BY: dic.get(c.OVERLAPPED_BY, 0),
#         c.MET_BY: dic.get(c.MET_BY, 0),
#         c.AFTER: dic.get(c.AFTER, 0),
#     }
