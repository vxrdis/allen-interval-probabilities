from random import random as rand
import constants as c


def get_relation(a_start, a_end, b_start, b_end):
    if a_end < b_start:
        return c.BEFORE
    if a_end == b_start:
        return c.MEETS
    if b_end < a_start:
        return c.AFTER
    if b_end == a_start:
        return c.MET_BY
    if a_start == b_start and a_end == b_end:
        return c.EQUALS
    if a_start == b_start:
        return c.STARTS if a_end < b_end else c.STARTED_BY
    if a_end == b_end:
        return c.FINISHED_BY if a_start < b_start else c.FINISHES
    if a_start < b_start and a_end > b_end:
        return c.CONTAINS
    if a_start > b_start and a_end < b_end:
        return c.DURING
    if a_start < b_start < a_end < b_end:
        return c.OVERLAPS
    if b_start < a_start < b_end < a_end:
        return c.OVERLAPPED_BY


def gen(p, q, t=0):
    start, end, state = None, None, c.UNBORN
    time = t
    while state != c.DEAD:
        time += 1
        r = rand()
        if state == c.UNBORN and r < p:
            state, start = c.ALIVE, time
        elif state == c.ALIVE and r < q:
            state, end = c.DEAD, time
    return (start, end, time)


def run(p, q, t=0):
    a = gen(p, q, t)
    b = gen(p, q, t)
    return get_relation(a[0], a[1], b[0], b[1])


def gen_relation(p1, q1, p2, q2, t=0):
    a_start, a_end, _ = gen(p1, q1, t)
    b_start, b_end, _ = gen(p2, q2, t)
    return get_relation(a_start, a_end, b_start, b_end)


def many(p, q, n=1000):
    counts = {rel: 0 for rel in c.ALLEN_RELATIONS}
    for _ in range(n):
        counts[run(p, q)] += 1
    return counts


def simulate_relations(p1, q1, p2, q2, trials=1000):
    counts = {rel: 0 for rel in c.ALLEN_RELATIONS}
    for _ in range(trials):
        counts[gen_relation(p1, q1, p2, q2)] += 1
    return counts


if __name__ == "__main__":
    print("Sample distribution:", many(0.5, 0.5, 10000))
