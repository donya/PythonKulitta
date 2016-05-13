# Some Simple Kulitta Tests
# Wen Sheng
# Last modified: 13-April-2016
# ===================================
import Search
import Constraints

# test pitch case a, b is same
def testEq (a, b):
    return a % 12 == b % 12
testSpace = [[i2, i2 + 12] for i2 in range(12)]
testMel = [0, 4, 7, 2]
testMelBuckets = [testSpace[i2] for i2 in testMel]

# print testSpace
# print testMel
# print testMelBuckets

# ============Testing allSolns and versions of pairProg============


def testPred (a, b):
    return abs(a - b) <= 7

print "test all solns"
print "expected:"
# expetedAllSolns = [[0,4,7,2],[0,4,7,14],[0,4,19,2],[0,4,19,14],[0,16,7,2],[0,16,7,14],[0,16,19,2],[0,16,19,14],[12,4,7,2],[12,4,7,14],[12,4,19,2],[12,4,19,14],[12,16,7,2],[12,16,7,14],[12,16,19,2],[12,16,19,14]]
print Search.allSols(testSpace, testEq, testMel)
print Search.pairProg(testSpace, testEq, testPred, testMel)


# ============Testing greedyProg and fallBack ============

# def testFallBack(bucket, g, x):
#     if bucket is None or len(bucket) == 0:
#         raise ("error!", "empty")
#     else:
#         return (g, bucket[0])
print "greedyProg"
print Search.greedyProg(testSpace, testEq, testPred, Search.nearFall, testMel)