# Chord Spaces Implementation for Python
# Ported from Haskell implementation
# Author: Donya Quck
# Last modified: 28-Oct-2014
#
# This file implements the functions from the original
# ChordSpaces.lhs associated with Kulitta (Haskell) in
# Python. A 1:1 implementation was possible in most
# cases. An additional in-place randomization method
# is also included.


#=====================================================
# PITCH SPACE GENERATION

from itertools import product


def makeRange(ranges):
    def f(a): return list(range(a[0],a[1]+1))
    fullRanges = list(map (f, ranges))
    return list(map (list, list(product(*fullRanges))))

# Generating filtered space

def nextValue(x,ranges):
    def updatePoint(x,i,ranges):
        if i >= len(x) :
            x.append(-1)
        elif x[i] == ranges[i][1]:
            x[i] = ranges[i][0]
            updatePoint(x, i+1, ranges)
        else:
            x[i] = x[i]+1
    updatePoint(x,0,ranges)
    
def searchRange(f, ranges):
    def searchFrom(f,x,ranges,xs):
        while len(x) == len(ranges):
            if f(x): xs.append(list(x))
            nextValue(x,ranges)
        return xs
    x0 = list(map(lambda x: x[0], ranges))
    return list(searchFrom(f, x0, ranges, []))



#=====================================================
# OPTIC RELATIONS

# Atomic operations
# Note: these are not in place

def o(chord,octs):
    return list(map (lambda a, b: a+12*b, chord, octs))

def t(chord, k):
    return list(map (lambda c: c+k, chord))


# Normalizations
# Note: these are not in place

def normO(chord):
    return list(map (lambda x: x % 12, chord))

def normT(chord):
    if chord == []:
        return []
    else: 
        return t(chord,-chord[0])

def normP(chord): return sorted(chord)

def normC(chord): return list(set(chord))

def normOP(chord): return normP(normO(chord))
def normOC(chord): return normC(normO(chord))
def normOT(chord): return normO(normT(chord)) 
def normPT(chord): return normT(normP(chord))
def normPC(chord): return normC(normP(chord))
def normTC(chord): return normC(normT(chord))
def normOPC(chord): return normC(normOP(chord))


# Equivalence relations based on normalizations

def normToEqRel(n,a,b): return n(a) == n(b)

def oEq(c1,c2): return normToEqRel(normO,c1,c2)
def pEq(c1,c2): return normToEqRel(normP,c1,c2)
def tEq(c1,c2): return normToEqRel(normT,c1,c2)
def cEq(c1,c2): return normToEqRel(normC,c1,c2)
def opEq(c1,c2): return normToEqRel(normOP,c1,c2)
def ocEq(c1,c2): return normToEqRel(normOC,c1,c2)
def otEq(c1,c2): return normToEqRel(normOT,c1,c2)
def ptEq(c1,c2): return normToEqRel(normPT,c1,c2)
def pcEq(c1,c2): return normToEqRel(normPC,c1,c2)
def tcEq(c1,c2): return normToEqRel(normTC,c1,c2)

# Equivalence relations requiring other algorithms

# [TO-DO: OPT]
# [TO-DO: OPTC]

#=====================================================
# QUOTIENT SPACE IMPLEMENTATION

def partition(eqRel,items):
    if items==[]:
        return []
    else:
        eqClass, otherItems = split(lambda x: eqRel(items[0],x), items)
        if otherItems==[]:
            return [eqClass]
        else:
            otherClasses = partition(eqRel, otherItems)
            return [eqClass]+otherClasses

def split(pred, items):
    predYes = []
    predNo = []
    for x in items:
        if pred(x):
            predYes.append(x)
        else:
            predNo.append(x)
    return predYes, predNo

def eqClass(eqRel,qSpace,x):
    return next((y for y in qSpace if eqRel(x,y[0])),None)

#=====================================================
# RANDOMIZATION

from random import seed, shuffle

# The "randomize" function just becomes "shuffle"
# Note: user has to choose in place or using a copy.
# To return a list,x to its sorted order, use x.sort()

def randomizeInPlace(items,rSeed):
    seed(rSeed)
    shuffle(items)

# To maintain consistency with the Haskell version,
# the main "randomize" definition copies the list rather
# than sorting it in-place.

def randomize(items,rSeed):
    newItems = list(items)
    randomizeInPlace(newItems, rSeed)
    return newItems
    


#=====================================================
# TESTING
    
x = [0,0,4,7]
y = [0,3,7]
z = [60,64,67]
def f(a,b): return a==b
def g(a): return a<2

q = partition(oEq, [x,y,z])
foo = [12,16,19]


#s = makeRange([(0,50),(0,50),(0,50),(0,50)])

def opEqTo(aSet,x):
    xs = filter(lambda y: opEq(x,y), aSet)
    return list(xs)

import time

def benchTest(set):
    t1 = time.time()
    print(len(set))
    t2 = time.time()
    # print(len(opEqTo(s,x)))
    t3 = time.time();
    print (t2-t1)
    print (t3-t2)
    
def bench2():
    t1 = time.time()
    xs = searchRange((lambda w: opEq(w,[0,0,4,7])), [(0,30),(0,30),(0,30),(0,30)])
    print (xs)
    t2 = time.time()
    print (t2-t1)

#bench2()
