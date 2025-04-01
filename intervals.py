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
    if a_start == b_start and a_end < b_end:
        return c.STARTS
    if a_start == b_start and a_end > b_end:
        return c.STARTED_BY
    if a_end == b_end and a_start < b_start:
        return c.FINISHED_BY
    if a_end == b_end and a_start > b_start:
        return c.FINISHES
    if a_start < b_start and a_end > b_end:
        return c.CONTAINS
    if a_start > b_start and a_end < b_end:
        return c.DURING
    if a_start < b_start and b_start < a_end and a_end < b_end:
        return c.OVERLAPS
    if b_start < a_start and a_start < b_end and b_end < a_end:
        return c.OVERLAPPED_BY


def gen(p, q, t=0):
    start = None
    end = None
    time = t
    state = c.UNBORN

    while state != c.DEAD:
        time += 1
        r = rand()

        if state == c.UNBORN and r < p:
            state = c.ALIVE
            start = time
        elif state == c.ALIVE and r < q:
            state = c.DEAD
            end = time

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
    results = {rel: 0 for rel in c.ALLEN_RELATIONS}

    for _ in range(n):
        relation = run(p, q)
        results[relation] += 1

    return results


def simulate_relations(p1, q1, p2, q2, trials=1000):
    results = {rel: 0 for rel in c.ALLEN_RELATIONS}

    for _ in range(trials):
        relation = gen_relation(p1, q1, p2, q2)
        results[relation] += 1

    return results
