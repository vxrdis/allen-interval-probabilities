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


def voc(string):
    if len(string) == 0:
        return {}
    else:
        return string[0].union(voc(string[1:]))


def proj(string, set):
    if len(string) == 0:
        return string
    else:
        h1 = string[0].intersection(set)
        if len(h1) == 0:
            return proj(string[1:], set)
        else:
            return [h1] + proj(string[1:], set)
