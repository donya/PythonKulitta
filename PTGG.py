#####################################################################
## This module is a Python version of Kulitta's PTGG module, which 
## was originally written in Haskell.
##
## Author: Donya Quick
## Last modified: 28-Nov-2015
## Python 2 and 3 compatible version of PTGG generative functions
#####################################################################

from random import *
from copy import *

# Nonterminal class
class NT:
    def __init__(self, val):
        self.val=val
    def __str__(self):
        return ('NT '+str(self.val))
    def __repr__(self):
        return str(self)

# Let statement class to handle statements of the form: let x = A in exp
class Let:
    def __init__(self, x, val, exp):
        self.x=x
        self.val=val
        self.exp=exp
    def __str__(self):
        return ('Let '+str(self.x)+' = '+str(self.val)+' in '+str(self.exp))
    def __repr__(self):
        return str(self)
# Variable class for handling instances of variables within expressions
class Var:
    def __init__(self, name):
        self.name=name # this is assumed to be a string
    def __str__(self):
        return ('Var '+self.name)
    def __repr__(self):
        return str(self)



# This version of applyRule assumes that we have already
# picked an appropriate rule. This is the version that
# will be used normally. It has a probabilistic version
# as well that allows for rules that have a probability
# attached as (p, (lhs, rhs)).

def applyRule(r,sym):
    return (r[1](sym[1]))

def applyRuleP(r,sym):
    return (r[1][1](sym[1]))

# For choose(xs), we assume that xs is a list of tuples.
# The first element in each tuple is the probability. We
# assume that probabilities sum to 1.0.

def choose(xs):
    n = len(xs)
    if n> 0: # Do we have things to choose from?
        r = random() # in [0.0, 1.0)
        i = 0
        while i < n: # Search through the items
            p = xs[i][0]
            if p >= r: # Have we used up the probability mass?
                return xs[i][1] # Yes - pick current element
            r = r-p # Subtract some probability mass
            i=i+1 # go to next index
        return xs[n-1] # Catch-all case for bad prob. mass distribution
    else:
        raise Exception('Empty list supplied to choose function')

# A Python version of the filter function from Haskell

def filter(seq, f):
    return [elem for elem in seq if f(elem)]

# Rule matching functions.

def sameLhs(x,r): # assumes r=(lhs,rhs)
    return (x==r[0])
 
def sameLhsP(x,r): # assumes r=(p,(lhs,rhs))
    return (x==r[1][0])

def findRules(rules,x): # assumes rules have form (lhs, rhs)
    xRules = list(filter(rules, lambda r: sameLhs(x,r)))
    return xRules

def findRulesP(prules,x): # assumes rules have form (p,(lhs,rhs))
    xRules = filter(prules, lambda r: sameLhsP(x,r))
    return xRules

# Update function to apply rules left to right over
# a sequence of symbols.

def update(prules, seq):
    newSeq = [] # new sequence
    for x in seq: # update each symbol in the sequence
        if (x.__class__.__name__ == 'Var'):
            newSeq.append(x)
        elif (x.__class__.__name__ == 'Let'):
            newVal = update(prules, x.val)
            newExp = update(prules, x.exp)
            newSeq = [Let(x.x, newVal, newExp)]
        elif (x.__class__.__name__ == 'NT'):
            okRs = findRulesP(prules, x.val[0]) # which rules can we use?
            if len(okRs) > 0: # did we find any rules?
                r = choose(okRs) # pick a rule stochastically
                newX = applyRule(r,x.val) # apply the rule
                # print(newSeq)
                # print(type(list(newX)))
                newSeq = newSeq+newX # grow the new sequence
            else: # no rules available - symbol is a terminal.
                newSeq.append(x)
        else:
            raise Exception("Unrecognized symbol: " + str(x)+"Type: "+type(x).__class__.__name__)
    return newSeq

# The gen function for n iterations

def gen(prules, seq, n):
    if n<=0: # are we done?
        return seq
    else: # not done, so generate one more level
        newSeq = update(prules, seq)
        return gen(prules, newSeq, n-1)

# Wraps a list of pairs with the NT constructor.
def toNT(seq):
    for x in seq:
        yield (NT(x))

# expand instantiates all Lets. Either an existing environment
# can be supplied or [] for statements containing all necessary
# definitions as Lets.
def expand(env, seq):
    newSeq = [] # create a new local sequence to build
    for x in seq:
        if (x.__class__.__name__ == 'Var'): 
            xVal = lookupLast(env,x.name) # find variable definition
            newSeq = newSeq +xVal # add its definition to the new sequence
        elif (x.__class__.__name__ == 'Let'):
            env.append((x.x, x.val)) # add x's definition
            newXs = expand(env,x.exp) # recurse into the expression
            newSeq = newSeq+newXs # add result to new sequence
            env.pop() # remove x's definition
        elif (x.__class__.__name__ == 'NT'):
            newSeq.append(x) # just add the symbol
        else: 
            raise Exception("Unrecognized symbol: " + str(x)+"Type: "+type(x).__class__.__name__)
    return newSeq

def lookupLast(env, v):
    n = len(env)
    i = n-1
    while i>=0: # walk backwards through list
        if (v==env[i][0]): # found a match?
            return env[i][1]
        i = i-1
    raise Exception('No table entry for variable name '+v)


# The toPairs function expands the term and strips NT constructors
def toPairs(seq):
    newSeq = []
    for x in seq:
        if (x.__class__.__name__ == 'Var'):
            raise Exception('No definition for variable '+x.name)
        elif (x.__class__.__name__ == 'Let'):
            newSeq = newSeq + expand([],x)
        elif (x.__class__.__name__ == 'NT'):
            newSeq.append(x.val)
        else:
            raise Exception("Unrecognized symbol: " + str(x)+"Type: "+type(x).__class__.__name__)
    return newSeq

# tMap transforms the data values in a term (operates on NT and Let).
# The original value is unaffected; a copy is made before any changes.
def tMap(f, seq0):
    seq = deepcopy(seq0)
    for x in seq:
        if (x.__class__.__name__ == 'Let'):
            x.val = tMap(f,x.val)
            x.exp = tMap(f,x.exp)
        elif (x.__class__.__name__ == 'NT'):
            x.val = f(x.val)
        elif (x.__class__.__name__ != 'Var'):
            raise Exception("Unrecognized symbol: " + str(x)+"Type: "+type(x).__class__.__name__)
    return seq

# normalize fixes the probability distribution for a rule set.
# The original value is unaffected; a copy is made before any changes.
def normalize(prules0):
    if len(prules0) <= 0:
        return []
    else: 
        prules = deepcopy(prules0)
        x0 = prules[0][1][0]
        rules1 = fixProbs (findRulesP(prules,x0))
        rules2 = normalize(findRulesPNot(prules, x0))
        return (rules1 + rules2)
    
# fixProbs is one step of normalization for rules with the same lhs.
# The original value is unaffected; a copy is made before any changes.
def fixProbs(prules):
    s = sum (map (lambda r: r[0], prules))
    newRules = []
    for r in prules:
        newRules.append((r[0]/s,r[1]))
    return newRules

# The opposite of fineRulesP (finds non-matching lhs rules)
def findRulesPNot(prules,x): # assumes rules have form (p,(lhs,rhs))
    xRules = list(filter(prules, lambda r: not(sameLhsP(x,r))))
    return xRules

#================================
# TESTING

# Testing with arbitrary numbers

rules2 = [(0.5, (0, lambda p: [NT ((0,p)), NT((0,p+1))])),
          (0.5, (0, lambda p: [NT ((1,p))])),
          (3.0, (1, lambda p: [NT ((1,p))])), # not normalized (for testing purposes)
          (6.0, (1, lambda p: [NT ((2,p))]))] # not normalized (for testing purposes)

def foo(x): # for testing tMap
    if x[0] == 0:
        return ('a',x[1]) # map 0 to a
    else:
        return ('b',x[1]) # map 1 to b

def testIt2(seedVal, n):
    seed(seedVal)
    x0 = [Let('x', [NT((0,0))], [Var('x'), Var('x')])] # starting value
    xn = gen(normalize(rules2), x0, n) # test gen
    xe = toPairs(expand ([], xn)) # test toPairs
    xf = tMap(foo,xn) # test tMap
    return (x0, xn, xf, xe)

# print(testIt2(5,4))
 
# Testing with chord-based PTGG prototype 
 
I = 0
V = 4

rules3 = [(0.5, (I, lambda p: [NT((V,p/2)), NT((I,p/2))])), # I^t --> V^(t/2) I^(t/2)
          (0.5, (I, lambda p: [NT((I,p/2)), NT((I,p/2))])), # I^t --> I^(t/2) I^(t/2)
          (1.0, (V, lambda p: [NT((V,p))]))]  # V^t --> V^t
 
def testIt3(seedVal, n):
    seed(seedVal)
    x0 = [Let('x', [NT((I,4.0))], [Var('x'), Var('x')])] # test case 1 (lets)
    #x0 = [NT((I,4.0))] # test case 2 (no lets)
    xn = gen(normalize(rules3), x0, n) # test gen
    xe = toPairs(expand ([], xn)) # test toPairs
    return (x0, xn, xe)


