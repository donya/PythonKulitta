# Python Kulitta examples
# Authors: Wen Sheng and Donya Quick

from MusicGrammars import *
from PTGG import *
import ClassicalFG
import PostProc
r1 = (0.3, (CType.I, lambda p: [v(h(p)), i(h(p))]))
r2 = (0.6, (CType.I, lambda p:[i(h(p)), i(h(p))]))
r3 = (0.1, (CType.I, lambda p:[i(p)]))
r4 = (0.5, (CType.V, lambda p:[iv(h(p)), v(h(p))]))
r5 = (0.4, (CType.V, lambda p:[v(h(p)), v(h(p))]))
r6 = (0.1, (CType.V, lambda p:[v(p)]))
r7 = (0.8, (CType.IV, lambda p:[iv(h(p)), iv(h(p))]))
r8 = (0.2, (CType.IV, lambda p:[iv(p)]))
rs = [r1, r2, r3, r4, r5, r6, r7, r8]

rs2 = [(1.0, (CType.I, lambda p: [i(h(p)), i(h(p))]))]

def smallerThanQN(dur):
    return dur < 0.5

def mapRules(fnDur, rs):
    res = []
    for r in rs:
        # res.append((r[0], toRelDur(fnDur, r[1])))
        res.append((r[0], fnDur, r[1]))
    return res
rules = mapRules(smallerThanQN, rs)


def genMusic(filename = "kullita-test", voiceRange = [[(47, 67), (52, 76), (60, 81)]]):
    startSym = [i(MP(4 * Dur.WN, Mode.MAJOR, 0, 0, 4 * Dur.WN))]
    testMP = MP(4 * Dur.WN, Mode.MAJOR, 0, 0, 4 * Dur.WN)
    h(testMP)
    txt = ""
    # print(testMP.dur)
    # # #test
    # print"startSym dur:", startSym[0].val[1].dur
    absStruct = gen(normalize(rs), startSym, 2)
    print("absStruct", absStruct)

    chords = PostProc.toAbsChords(absStruct)
    print("chords:", chords[0].absChord, chords[0].key.absPitch)
    print("Length of Chords:" + str(len(chords)))
    # ClassicalFG.classicalCS2(chords)
    ClassicalFG.classicalCS2WithRange(chords)
    # print(len(chords))
    PostProc    .tChodsToMusic(chords, filename)

genMusic("test")
