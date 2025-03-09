# convert to numpy ??
# import numpy as np

# keep an array of pairs [a-state,b-state] where state = 0,1,2
# initially [[0,0]]  both  unborn   #  u = np.array([[0,0]])  # [a-state,b-state]
# grow until the last pair is [2,2]   # both dead
#  e.g. [[0,0],[1,1],[2,2]]  for Allen equal
#       [[0,0],[1,0],[2,1],[2,2]] for Allen meet
#       [[0,0],[1,0],[2,0],[2,1],[2,2]]  for Allen <

from random import *

tally = {}  # parametrized tally with parameter = str(pBorn) + "," + str(pDie)


def demo():
    print("arSimulate(0.5,0.5,1000)", arSimulate(0.5, 0.5, 1000))
    print("arSimulate(0.1,0.1,1000)", arSimulate(0.1, 0.1, 1000))
    print("arSimulate(0.01,0.01,1000)", arSimulate(0.01, 0.01, 1000))
    print("arSimulate(0.001,0.001,1000)", arSimulate(0.001, 0.001, 1000))
    print("arSimulate(0.2,0.1,1000)", arSimulate(0.2, 0.1, 1000))
    print("arSimulate(0.02,0.01,1000)", arSimulate(0.02, 0.01, 1000))
    print("arSimulate(0.002,0.001,1000)", arSimulate(0.002, 0.001, 1000))
    print("Updated tally and probabilities in file outputPy")
    ta2file("outputPy")
    pr2file("outputPy")
    print("Iterating demo() updates tally and outputPy")


def arSimulate(probBorn, probDie, trials):
    redRuns = simulateRed(probBorn, probDie, trials)
    dic = scoreRed(redRuns)
    p = probDic(dic, trials)
    #   print(" Probabilities combining inverses ", combineInv(p))
    updateTally(probBorn, probDie, dic)
    #   print(" New tally for ",probBorn,probDie," is ", tally[str(probBorn)+","+str(probDie)])
    return dic


def simulateRed(pBorn, pDie, trials):
    temp = []
    for run in range(trials):
        hist = [[0, 0]]
        while not (hist[-1] == [2, 2]):
            first = updateState(hist[-1][0], pBorn, pDie)
            second = updateState(hist[-1][1], pBorn, pDie)
            if not (hist[-1] == [first, second]):  # no need to reduce/destutter
                hist.append([first, second])
        temp.append(hist)
    return temp


def updateState(state, pBorn, pDie):
    toss = random()
    if state == 0 and toss < pBorn:
        return 1
    elif state == 1 and toss < pDie:
        return 2
    else:
        return state


def scoreRed(reducedRuns):
    dic = arInitDic()
    for r in reducedRuns:
        dic[arCode(r)] += 1
    return dic


def arCode(Hist):
    if Hist == [[0, 0], [1, 1], [2, 2]]:
        return "eq"
    elif Hist == [[0, 0], [1, 0], [2, 0], [2, 1], [2, 2]]:
        return "b"
    elif Hist == [[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]]:
        return "bi"
    elif Hist == [[0, 0], [1, 0], [1, 1], [2, 1], [2, 2]]:
        return "o"
    elif Hist == [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2]]:
        return "oi"
    elif Hist == [[0, 0], [1, 0], [2, 1], [2, 2]]:
        return "m"
    elif Hist == [[0, 0], [0, 1], [1, 2], [2, 2]]:
        return "mi"
    elif Hist == [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]]:
        return "d"
    elif Hist == [[0, 0], [1, 0], [1, 1], [1, 2], [2, 2]]:
        return "di"
    elif Hist == [[0, 0], [1, 1], [2, 1], [2, 2]]:
        return "s"
    elif Hist == [[0, 0], [1, 1], [1, 2], [2, 2]]:
        return "si"
    elif Hist == [[0, 0], [0, 1], [1, 1], [2, 2]]:
        return "f"
    elif Hist == [[0, 0], [1, 0], [1, 1], [2, 2]]:
        return "fi"


def arInitDic():
    dic = {}
    for i in [
        "eq",
        "b",
        "bi",
        "s",
        "si",
        "m",
        "mi",  # "dummy",
        "o",
        "oi",
        "d",
        "di",
        "f",
        "fi",
    ]:
        dic[i] = 0
    return dic


def updateTally(pBorn, pDie, dic):
    pStr = str(pBorn) + "," + str(pDie)  # converts pair to string for dictionary
    if not (pStr in tally):
        tally[pStr] = arInitDic()
    for i in [
        "eq",
        "b",
        "bi",
        "s",
        "si",
        "m",
        "mi",  # "dummy",
        "o",
        "oi",
        "d",
        "di",
        "f",
        "fi",
    ]:
        tally[pStr][i] = tally[pStr][i] + dic[i]


def probDic(dic, trials):
    temp = {}
    for k in dic:
        temp[k] = dic[k] / trials
    return temp


def combineInv(dic):
    temp = {}
    temp["eq"] = dic["eq"]
    temp["b"] = dic["b"] + dic["bi"]
    temp["o"] = dic["o"] + dic["oi"]
    temp["d"] = dic["d"] + dic["di"]
    temp["s"] = dic["s"] + dic["si"]
    temp["m"] = dic["m"] + dic["mi"]
    temp["f"] = dic["f"] + dic["fi"]
    #   print("Sum is",checkSum(temp))
    return temp


def talProb():
    temp = {}
    for k in tally:
        temp[k] = score2prob(combineInv(tally[k]))  # combining inverses
    return temp


def score2prob(dic):
    trials = checkSum(dic)
    temp = {}
    for k in dic:
        temp[k] = dic[k] / trials
    return temp


def tal(pBorn, pDie):
    return tally[str(pBorn) + "," + str(pDie)]


def tallyProb(pBorn, pDie):
    return score2prob(tally[str(pBorn) + "," + str(pDie)])


def checkSum(dic):
    sum = 0
    for i in dic:
        sum = sum + dic[i]
    return sum


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


def w2file(file, dic):
    try:
        geeky_file = open(file, "a")
        geeky_file.write(str(dic) + "\n")
        geeky_file.close()
    except:
        print("Unable to append to file")
