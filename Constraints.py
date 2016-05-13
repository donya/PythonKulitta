import Search
import math
import sys

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
