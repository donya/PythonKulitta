import ChordSpaces
import midi
from MusicGrammars import *
import ChordSpaces
import PTGG
from MidiFuns import *

def toAs(ctype, mode):
    scale = None
    if mode == Mode.MAJOR:
        scale = Mode.MAJOR_SCALE + map(lambda x: x + 12, Mode.MAJOR_SCALE)
    else:
        scale = Mode.MINOR_SCALE + map(lambda x: x + 12, Mode.MINOR_SCALE)
    return [scale[ctype], scale[ctype + 2], scale[ctype + 4]]


#===================For Testing ToAs function==========
# for i2 in CType.ALL_CHORD:
#     print(toAs(i2, Mode.MINOR))



class RChord:
    def __init__(self, key, dur, c, v=100, o=0):
        self.key = Key(key.absPitch, key.mode)
        self.dur = dur
        self.ctype = c
        self.vol = v
        self.onset = 0
    def __str__(self):
        return "("+str(self.ctype)+","+str(self.dur)+")"
    def __repr__(self):
        return str(self)



def toChords(terms):
    xe = PTGG.toPairs(PTGG.expand([], terms))
    res = []
    for x in xe:
        # print x
        a, p = x
        # print p.key
        # print p.mode
        key = Key(p.key, p.mode)
        rchord = RChord(key, p.dur, a)
        res.append(rchord)
    return res

def toAbsChords(terms):
    rchords = toChords(terms)
    print "Rchords", rchords
    return map(toAbsChord, rchords)


def toAbsChord(rchord):
    to_as_res = toAs(rchord.ctype, rchord.key.mode)
    absChd = ChordSpaces.t(to_as_res, rchord.key.absPitch)
    key = rchord.key
    return TChord(absChd, rchord.dur) #, rchord.vol, Key(key.absPitch, key.mode), rchord.onset)


#def atTrans(p1, tChords):
#    for tChord in tChords:
#        trans_p(tChord.key, p1)
#        ChordSpaces.t(tChord.absChord, p1)

