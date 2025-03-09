from superp import *


def allen(x, y, rel):
    lx = l(x)
    rx = r(x)
    ly = l(y)
    ry = r(y)
    if rel == "b":
        return [{lx}, {rx}, {ly}, {ry}]
    elif rel == "o":
        return [{lx}, {ly}, {rx}, {ry}]
    elif rel == "m":
        return [{lx}, {rx, ly}, {ry}]
    elif rel == "d":
        return [{ly}, {lx}, {rx}, {ry}]
    elif rel == "s":
        return [{lx, ly}, {rx}, {ry}]
    elif rel == "f":
        return [{ly}, {lx}, {rx, ry}]
    if rel == "bi":
        return [{ly}, {ry}, {lx}, {rx}]
    elif rel == "oi":
        return [{ly}, {lx}, {ry}, {rx}]
    elif rel == "mi":
        return [{ly}, {ry, lx}, {rx}]
    elif rel == "di":
        return [{lx}, {ly}, {ry}, {rx}]
    elif rel == "si":
        return [{lx, ly}, {ry}, {rx}]
    elif rel == "fi":
        return [{lx}, {ly}, {rx, ry}]
    elif rel == "eq":
        return [{lx, ly}, {rx, ry}]


def l(x):
    return "l" + str(x)


def r(x):
    return "r" + str(x)


def allInv(string, x, y):
    lx = l(x)
    rx = r(x)
    ly = l(y)
    ry = r(y)
    if string == [{lx}, {rx}, {ly}, {ry}]:
        return "b"
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
        return "bi"
    elif string == [{ly}, {lx}, {ry}, {rx}]:
        return "oi"
    elif string == [{ly}, {ry, lx}, {rx}]:
        return "mi"
    elif string == [{lx}, {ly}, {ry}, {rx}]:
        return "di"
    elif string == [{lx, ly}, {ry}, {rx}]:
        return "si"
    elif string == [{lx}, {ly}, {rx, ry}]:
        return "fi"
    elif string == [{lx, ly}, {rx, ry}]:
        return "eq"


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
    print('e.g. tt("b",d") =', tt("b", "d"), "by superposing")
    show("b", "d")
