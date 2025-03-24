import constants as c
from random import random as rand

tally = {}


def allen_relation_order():
    return c.ALLEN_RELATIONS


def updateState(state, pBorn, pDie):
    toss = rand()
    if state == c.UNBORN and toss < pBorn:
        return c.ALIVE
    elif state == c.ALIVE and toss < pDie:
        return c.DEAD
    else:
        return state


def arCode(Hist):
    if Hist == [[0, 0], [1, 1], [2, 2]]:
        return "e"
    elif Hist == [[0, 0], [1, 0], [2, 0], [2, 1], [2, 2]]:
        return "p"
    elif Hist == [[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]]:
        return "P"
    elif Hist == [[0, 0], [1, 0], [1, 1], [2, 1], [2, 2]]:
        return "o"
    elif Hist == [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2]]:
        return "O"
    elif Hist == [[0, 0], [1, 0], [2, 1], [2, 2]]:
        return "m"
    elif Hist == [[0, 0], [0, 1], [1, 2], [2, 2]]:
        return "M"
    elif Hist == [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]]:
        return "d"
    elif Hist == [[0, 0], [1, 0], [1, 1], [1, 2], [2, 2]]:
        return "D"
    elif Hist == [[0, 0], [1, 1], [2, 1], [2, 2]]:
        return "s"
    elif Hist == [[0, 0], [1, 1], [1, 2], [2, 2]]:
        return "S"
    elif Hist == [[0, 0], [0, 1], [1, 1], [2, 2]]:
        return "f"
    elif Hist == [[0, 0], [1, 0], [1, 1], [2, 2]]:
        return "F"


def arInitDic():
    return {i: 0 for i in allen_relation_order()}


def checkSum(dic):
    return sum(dic.values())


def w2file(file, dic):
    try:
        geeky_file = open(file, "a")
        geeky_file.write(str(dic) + "\n")
        geeky_file.close()
    except:
        print("Unable to append to file")


def probDic(dic, trials):
    return {k: dic[k] / trials for k in dic}


def score2prob(dic):
    trials = checkSum(dic)
    return {k: dic[k] / trials for k in dic}


def combineInv(dic):
    temp = {}
    temp["p"] = dic["p"] + dic["P"]
    temp["m"] = dic["m"] + dic["M"]
    temp["o"] = dic["o"] + dic["O"]
    temp["F"] = dic["F"]
    temp["D"] = dic["D"]
    temp["s"] = dic["s"] + dic["S"]
    temp["e"] = dic["e"]
    temp["S"] = dic["S"]
    temp["d"] = dic["d"] + dic["D"]
    temp["f"] = dic["f"]
    temp["O"] = dic["O"]
    temp["M"] = dic["M"]
    temp["P"] = dic["P"]
    return temp


def simulateRed(pBorn, pDie, trials):
    temp = []
    for run in range(trials):
        hist = [[0, 0]]
        while not (hist[-1] == [2, 2]):
            first = updateState(hist[-1][0], pBorn, pDie)
            second = updateState(hist[-1][1], pBorn, pDie)
            if not (hist[-1] == [first, second]):
                hist.append([first, second])
        temp.append(hist)
    return temp


def scoreRed(reducedRuns):
    dic = arInitDic()
    for r in reducedRuns:
        dic[arCode(r)] += 1
    return dic


def updateTally(pBorn, pDie, dic):
    pStr = str(pBorn) + "," + str(pDie)
    if not (pStr in tally):
        tally[pStr] = arInitDic()
    for i in allen_relation_order():
        if i in dic:
            tally[pStr][i] = tally[pStr][i] + dic[i]


def tal(pBorn, pDie):
    return tally[str(pBorn) + "," + str(pDie)]


def tallyProb(pBorn, pDie):
    return score2prob(tally[str(pBorn) + "," + str(pDie)])


def talProb():
    return {k: score2prob(combineInv(tally[k])) for k in tally}


def ta2file(file):
    w2file(file, "Raw tally")
    for p in tally:
        w2file(file, str(checkSum(tally[p])) + " trials of " + p)
        w2file(file, tally[p])
    w2file(file, "\n")


def pr2file(file):
    dic = talProb()
    w2file(file, "Tally probabilities (combining inverses)")
    for p in dic:
        w2file(file, p + ":")
        w2file(file, dic[p])
    w2file(file, "\n")


def arSimulate(probBorn, probDie, trials):
    redRuns = simulateRed(probBorn, probDie, trials)
    dic = scoreRed(redRuns)
    p = probDic(dic, trials)
    updateTally(probBorn, probDie, dic)
    return dic


def demo():
    for params in [
        (0.5, 0.5, 1000),
        (0.1, 0.1, 1000),
        (0.01, 0.01, 1000),
        (0.001, 0.001, 1000),
        (0.2, 0.1, 1000),
        (0.02, 0.01, 1000),
        (0.002, 0.001, 1000),
    ]:
        pBorn, pDie, trials = params
        print(f"arSimulate({pBorn},{pDie},{trials})")
        result = arSimulate(pBorn, pDie, trials)
        ordered_result = {k: result.get(k, 0) for k in allen_relation_order()}
        print(ordered_result)
        print(f"Total count: {checkSum(result)}")
        print()


if __name__ == "__main__":
    demo()
