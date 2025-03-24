import constants as c


def l(x):
    return "l" + str(x)


def r(x):
    return "r" + str(x)


def voc(string):
    if len(string) == 0:
        return {}
    else:
        return string[0].union(voc(string[1:]))


def superpose(string1, string2, voc1, voc2):
    if len(string1) == len(string2) == 0:
        return [string1]
    else:
        temp = []
        if len(string1) > 0:
            h1 = string1[0]
            t1 = string1[1:]
            h1v2 = h1.intersection(voc2)
            if len(h1v2) == 0:
                for res in superpose(t1, string2, voc1, voc2):
                    temp.append([h1] + res)
            if len(string2) > 0:
                h2 = string2[0]
                t2 = string2[1:]
                h3 = h1.union(h2)
                if h1v2.issubset(h2):
                    h2v1 = h2.intersection(voc1)
                    if h2v1.issubset(h1):
                        for res in superpose(t1, t2, voc1, voc2):
                            temp.append([h3] + res)
        if len(string2) > 0:
            h2 = string2[0]
            t2 = string2[1:]
            h2v1 = h2.intersection(voc1)
            if len(h2v1) == 0:
                for res in superpose(string1, t2, voc1, voc2):
                    temp.append([h2] + res)
        return temp


def super(s1, s2):
    return superpose(s1, s2, voc(s1), voc(s2))


def proj(string, set):
    if len(string) == 0:
        return string
    else:
        h1 = string[0].intersection(set)
        if len(h1) == 0:
            return proj(string[1:], set)
        else:
            return [h1] + proj(string[1:], set)


def allen(x, y, rel):
    lx = l(x)
    rx = r(x)
    ly = l(y)
    ry = r(y)
    if rel == c.PRECEDES:
        return [{lx}, {rx}, {ly}, {ry}]
    elif rel == c.OVERLAPS:
        return [{lx}, {ly}, {rx}, {ry}]
    elif rel == c.MEETS:
        return [{lx}, {rx, ly}, {ry}]
    elif rel == c.DURING:
        return [{ly}, {lx}, {rx}, {ry}]
    elif rel == c.STARTS:
        return [{lx, ly}, {rx}, {ry}]
    elif rel == c.FINISHES:
        return [{ly}, {lx}, {rx, ry}]
    if rel == c.PRECEDED_BY:
        return [{ly}, {ry}, {lx}, {rx}]
    elif rel == c.OVERLAPPED_BY:
        return [{ly}, {lx}, {ry}, {rx}]
    elif rel == c.MET_BY:
        return [{ly}, {ry, lx}, {rx}]
    elif rel == c.CONTAINS:
        return [{lx}, {ly}, {ry}, {rx}]
    elif rel == c.STARTED_BY:
        return [{lx, ly}, {ry}, {rx}]
    elif rel == c.FINISHED_BY:
        return [{lx}, {ly}, {rx, ry}]
    elif rel == c.EQUALS:
        return [{lx, ly}, {rx, ry}]


def allInv(string, x, y):
    lx = l(x)
    rx = r(x)
    ly = l(y)
    ry = r(y)
    if string == [{lx}, {rx}, {ly}, {ry}]:
        return "p"
    elif string == [{lx}, {ly}, {rx}, {ry}]:
        return "o"
    elif string == [{lx}, {rx, ly}, {ry}]:
        return "m"
    elif string == [{ly}, {lx}, {rx}, {ry}]:
        return "d"
    elif string == [{lx, ly}, {rx}, {ry}]:
        return "s"
    elif string == [{ly}, {lx}, {rx, ry}]:
        return "f"
    elif string == [{ly}, {ry}, {lx}, {rx}]:
        return "P"
    elif string == [{ly}, {lx}, {ry}, {rx}]:
        return "O"
    elif string == [{ly}, {ry, lx}, {rx}]:
        return "M"
    elif string == [{lx}, {ly}, {ry}, {rx}]:
        return "D"
    elif string == [{lx, ly}, {ry}, {rx}]:
        return "S"
    elif string == [{lx}, {ly}, {rx, ry}]:
        return "F"
    elif string == [{lx, ly}, {rx, ry}]:
        return "e"


def tt(r1, r2):
    temp = []
    for s in super(allen(0, 1, r1), allen(1, 2, r2)):
        temp.append(allInv(proj(s, {l(0), r(0), l(2), r(2)}), 0, 2))
    return temp


def show(r1, r2):
    s1 = allen(0, 1, r1)
    s2 = allen(1, 2, r2)
    print(" ", s1, "(depicting 0", r1, "1) and")
    print(" ", s2, "(depicting 1", r2, "2)")
    for s in super(s1, s2):
        print("   0", allInv(proj(s, {l(0), r(0), l(2), r(2)}), 0, 2), "2 from ", s)


def test():
    print("Allen relations from [{'l0'}, {'r0'}] superposed with [{'l1'}, {'r1'}]")
    al = super([{"l0"}, {"r0"}], [{"l1"}, {"r1"}])
    for s in al:
        print(" ", allInv(s, 0, 1), s)
    print("Allen transitivity table tt(r1,r2)")
    print('e.g. tt("p",d") =', tt("p", "d"), "by superposing")
    show("p", "d")


if __name__ == "__main__":
    test()
