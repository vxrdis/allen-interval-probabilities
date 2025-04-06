import constants as c


def l(x):
    return f"l{x}"


def r(x):
    return f"r{x}"


# Get the vocabulary (set of all endpoints) from a symbolic sequence
def voc(seq):
    return set().union(*seq) if seq else set()


# Superpose two symbolic strings if vocabulary constraints allow
def superpose(s1, s2, v1, v2):
    if not s1 and not s2:
        return [[]]

    results = []
    if s1:
        h1, t1 = s1[0], s1[1:]
        if not h1 & v2:
            for rest in superpose(t1, s2, v1, v2):
                results.append([h1] + rest)
        elif s2:
            h2, t2 = s2[0], s2[1:]
            merged = h1 | h2
            if h1 & v2 <= h2 and h2 & v1 <= h1:
                for rest in superpose(t1, t2, v1, v2):
                    results.append([merged] + rest)

    if s2:
        h2, t2 = s2[0], s2[1:]
        if not h2 & v1:
            for rest in superpose(s1, t2, v1, v2):
                results.append([h2] + rest)

    return results


def super(s1, s2):
    return superpose(s1, s2, voc(s1), voc(s2))


# Project a symbolic sequence to a set of endpoints
def proj(seq, keep):
    return [s & keep for s in seq if s & keep]


# Return symbolic string representation for a given Allen relation
def allen(x, y, rel):
    lx, rx, ly, ry = l(x), r(x), l(y), r(y)
    return {
        c.BEFORE: [{lx}, {rx}, {ly}, {ry}],
        c.MEETS: [{lx}, {rx, ly}, {ry}],
        c.OVERLAPS: [{lx}, {ly}, {rx}, {ry}],
        c.DURING: [{ly}, {lx}, {rx}, {ry}],
        c.STARTS: [{lx, ly}, {rx}, {ry}],
        c.FINISHES: [{ly}, {lx}, {rx, ry}],
        c.AFTER: [{ly}, {ry}, {lx}, {rx}],
        c.MET_BY: [{ly}, {ry, lx}, {rx}],
        c.OVERLAPPED_BY: [{ly}, {lx}, {ry}, {rx}],
        c.CONTAINS: [{lx}, {ly}, {ry}, {rx}],
        c.STARTED_BY: [{lx, ly}, {ry}, {rx}],
        c.FINISHED_BY: [{lx}, {ly}, {rx, ry}],
        c.EQUALS: [{lx, ly}, {rx, ry}],
    }.get(rel)


# Return Allen relation name from a symbolic sequence
def allInv(string, x, y):
    lx, rx, ly, ry = l(x), r(x), l(y), r(y)
    patterns = {
        "p": [{lx}, {rx}, {ly}, {ry}],
        "m": [{lx}, {rx, ly}, {ry}],
        "o": [{lx}, {ly}, {rx}, {ry}],
        "d": [{ly}, {lx}, {rx}, {ry}],
        "s": [{lx, ly}, {rx}, {ry}],
        "f": [{ly}, {lx}, {rx, ry}],
        "P": [{ly}, {ry}, {lx}, {rx}],
        "M": [{ly}, {ry, lx}, {rx}],
        "O": [{ly}, {lx}, {ry}, {rx}],
        "D": [{lx}, {ly}, {ry}, {rx}],
        "S": [{lx, ly}, {ry}, {rx}],
        "F": [{lx}, {ly}, {rx, ry}],
        "e": [{lx, ly}, {rx, ry}],
    }
    for rel, pattern in patterns.items():
        if string == pattern:
            return rel
    return "?"


# Compute composition r1 ∘ r2 using symbolic superposition
def tt(r1, r2):
    results = []
    s1 = allen(0, 1, r1)
    s2 = allen(1, 2, r2)
    for merged in super(s1, s2):
        proj_02 = proj(merged, {l(0), r(0), l(2), r(2)})
        results.append(allInv(proj_02, 0, 2))
    return results


# Print visual debug of symbolic composition
def show(r1, r2):
    s1 = allen(0, 1, r1)
    s2 = allen(1, 2, r2)
    print(" ", s1, f"(depicting 0 {r1} 1)")
    print(" ", s2, f"(depicting 1 {r2} 2)")
    for merged in super(s1, s2):
        rel = allInv(proj(merged, {l(0), r(0), l(2), r(2)}), 0, 2)
        print("   0", rel, "2 from", merged)


if __name__ == "__main__":
    print("Example: tt('p', 'd') =", tt("p", "d"))
    show("p", "d")
