import Search
import math
import sys
from ChordSpaces import *

def sorted(chord):
    return all(chord[i] <= chord[i + 1] for i in xrange(len(chord) - 1))

def spaced(lims, chord):
    cPairs = zip(chord[0:len(chord)-2], chord[1:])
    def f(lim,pair):
        diff = abs(pair[1] - pair[0])
        return (diff >= lim[0] and diff <=lim[1])
    return all([f(a,b) for (a,b) in zip(lims,cPairs)])

# doubled :: [AbsChord] -> Predicate AbsChord
# doubled templates x = elem (normOP x) allTriads where
#     allTriads = concatMap (\c -> map (normOP . t c) templates) [0..11]


triads = [[0, 0, 4, 7], [0, 4, 7, 7], [0, 0, 3, 7], [0, 3, 7, 7], [0, 0, 3, 6]]

def flatten(x):
    return [val for sublist in x for val in sublist]

def doubled(templates, x):
    allTriads = flatten(map(lambda c: map(lambda v: normOP(t(v,c)), templates), range(0,12)))
    xn = normOP(x)
    return xn in allTriads


# satbFilter x = and $ map ($x) [sorted, spaced satbLimits, doubled triads]
satbLimits = [(3,12), (3,12), (3,12), (3,12)]
def satbFilter(x): return sorted(x) and doubled(triads,x) and spaced(satbLimits,x)

# check if parrallel exist
def hNotPar1(chord1, chord2):
    if not len(chord1) == len(chord2):
        print("the length of chords are different!")
        return True #???
    diff = [chord1[i2] - chord2[i2] for i2 in range(len(chord1))]
    return len(set(diff)) == len(diff)

# check if rank is the same
def hNotCross(chord1, chord2):
    if not len(chord1) == len(chord2):
        print("the length of chords are different!")
        return True #???
    rank1 = sorted(range(len(chord1)), key=lambda k: chord1[k])
    rank2 = sorted(range(len(chord2)), key=lambda k: chord2[k])
    return rank1 == rank2

def euclideanDist(chord1, chord2):
    if not len(chord1) == len(chord2):
        print("the length of chords are different!")
        return sys.maxint
    return math.sqrt(sum((a - b) ** 2 for a,b in zip(chord1, chord2)))

def maxStepDist(chord1, chord2):
    if not len(chord1) == len(chord2):
        print("the length of chords are different!")
        return sys.maxint
    return max(abs(a - b) for a, b in zip(chord1, chord2))
# parameters
# dist function, constraints, chord1, chrod2
def distClass(distFun, predicate, chord1, chord2):
    # return predicate (distFun, chord1, chord2)
    pass

# # ======= Test Case for hNotPar1 ======
# c1 = [60, 64, 67]
# c2 = [61, 70, 68]
# print("hNotPar1 should return False")
# print(hNotPar1(c1, c2))
#
# # ======= Test Case for hNotCross ======
#
# c3 = [60, 64, 67]
# c4 = [66, 65, 67]
# print("hNotCross should return False")
# print(hNotCross(c3, c4))
