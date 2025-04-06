from random import random as rand
import constants as c
import stats

# Track global tallies by (pBorn, pDie)
tally = {}


def allen_relation_order():
    return c.ALLEN_RELATIONS


def updateState(state, pBorn, pDie):
    toss = rand()
    if state == c.UNBORN and toss < pBorn:
        return c.ALIVE
    elif state == c.ALIVE and toss < pDie:
        return c.DEAD
    return state


# Allen relation codes from transition histories
def arCode(hist):
    rel_map = {
        ((0, 0), (1, 1), (2, 2)): "e",
        ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2)): "p",
        ((0, 0), (0, 1), (0, 2), (1, 2), (2, 2)): "P",
        ((0, 0), (1, 0), (1, 1), (2, 1), (2, 2)): "o",
        ((0, 0), (0, 1), (1, 1), (1, 2), (2, 2)): "O",
        ((0, 0), (1, 0), (2, 1), (2, 2)): "m",
        ((0, 0), (0, 1), (1, 2), (2, 2)): "M",
        ((0, 0), (0, 1), (1, 1), (2, 1), (2, 2)): "d",
        ((0, 0), (1, 0), (1, 1), (1, 2), (2, 2)): "D",
        ((0, 0), (1, 1), (2, 1), (2, 2)): "s",
        ((0, 0), (1, 1), (1, 2), (2, 2)): "S",
        ((0, 0), (0, 1), (1, 1), (2, 2)): "f",
        ((0, 0), (1, 0), (1, 1), (2, 2)): "F",
    }
    return rel_map.get(tuple(map(tuple, hist)), "unknown")


def arInitDic():
    return {rel: 0 for rel in allen_relation_order()}


def simulateRun(pBorn, pDie):
    hist = [[0, 0]]
    while hist[-1] != [2, 2]:
        a, b = hist[-1]
        next_a = updateState(a, pBorn, pDie)
        next_b = updateState(b, pBorn, pDie)
        if [next_a, next_b] != hist[-1]:
            hist.append([next_a, next_b])
    return hist


def simulateRed(pBorn, pDie, trials):
    return [simulateRun(pBorn, pDie) for _ in range(trials)]


def scoreRed(histories):
    counts = arInitDic()
    for h in histories:
        rel = arCode(h)
        if rel in counts:
            counts[rel] += 1
    return counts


def updateTally(pBorn, pDie, dic):
    key = f"{pBorn},{pDie}"
    if key not in tally:
        tally[key] = arInitDic()
    for rel in dic:
        tally[key][rel] += dic[rel]


def arSimulate(pBorn, pDie, trials):
    runs = simulateRed(pBorn, pDie, trials)
    counts = scoreRed(runs)
    updateTally(pBorn, pDie, counts)
    return counts


# Optional: dump tally to a file
def dump_tally(file_path):
    with open(file_path, "w") as f:
        for k in tally:
            f.write(f"{k}: {tally[k]}\n")


# Demo for sanity checking
if __name__ == "__main__":
    for p, q, trials in [(0.5, 0.5, 1000), (0.1, 0.1, 1000)]:
        print(f"Simulating p={p}, q={q}")
        counts = arSimulate(p, q, trials)
        print(counts, "\n")
