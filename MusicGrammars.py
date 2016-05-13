from fractions import Fraction
from PTGG import NT

class Mode:
    MAJOR = "Major"
    MINOR = "Minor"
    MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
    MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]


class CType:
    I, II, III, IV, V, VI, VII = range(7)
    ALL_CHORD = [I, II, III, IV, V, VI, VII]





class Dur(object):
    WN = 1.0
    HN = 0.5
    QN = 0.25
    EN = 0.125
    SN = 0.0625
    TN = 0.03125
    dur_dict = {"WN": WN,
    "HN": HN,
    "QN": QN,
    "EN": EN,
    "SN": SN,
    "TN": TN,
    WN:"WN", HN:"HN", QN: "QN", EN: "EN", SN: "SN", TN: "TN"
    }



class MP:
    def __init__(self, dur=Dur.WN, mode=Mode.MAJOR, key=0, onset=0, sDur=Dur.WN):
        self.dur = dur  # float
        self.mode = mode  # str
        self.sDur = sDur
        # later defined
        self.key = key
        self.onset = onset
        # print("dur:", self.dur)


def isMaj(mode):
    return mode == Mode.MAJOR


def isMin(mode):
    return mode == Mode.MINOR



def dFac(x, mp):
    mp.dur *= x

def getScale(mode):
    if mode == Mode.MINOR:
        return Mode.MINOR_SCALE
    elif mode == Mode.MAJOR:
        return Mode.MAJOR_SCALE
    else:
        return []
# i, ii, iii, iv, v, vi, vii = [(lambda p: NT((c, p)) for c in CType.ALL_CHORD)]
i = lambda p: NT((CType.I, p))
ii = lambda p: NT((CType.II, p))
iii = lambda p: NT((CType.III, p))
iv = lambda p: NT((CType.IV, p))
v = lambda p: NT((CType.V, p))
vi = lambda p: NT((CType.VI, p))
vii = lambda p: NT((CType.VII, p))
def h(p):
    dFac(0.5, p)
    return p

# # test
# p = MP()
# print(h(p).dur)


def toRelDur(fnDur, rule): # rule is a tuple like (CType.I, rfun)
    left, right = rule
    newRight = lambda p:[NT((left, p))] if fnDur(p.dur) else right(p)
    return (left, newRight)

def toRelDur2(fnDur, rule):
    # left, right = rule
    # newRight = 0
    # return(left,newRight)
    pass

