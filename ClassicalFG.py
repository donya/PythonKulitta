import ChordSpaces
import Search
def pianoFilter(chords): # [[0, 1]]
    res = []
    for chd in chords:
        if not len(set(chd)) == len(chd):
            continue
        new_chd = sorted(chd)
        if new_chd not in res:
            res.append(new_chd)
    return res



def testPred (a, b):
    for idx in range(len(a)):
        if abs(a[idx] - b[idx]) > 7:
            return False
    return True

def testPred2(a, b):
    return True

def classicalCS2(tchords):
    allChords = pianoFilter(ChordSpaces.makeRange([(47, 67), (52, 76), (60, 81)]))
    # print(allChords[:10])
    qSpace = ChordSpaces.partition(ChordSpaces.opEq, allChords)
    # print(qSpace)
    chords = map(lambda x: x.absChord, tchords)
    # print(chords)
    newChords = Search.greedyProg(qSpace, ChordSpaces.opEq, testPred, Search.nearFall, chords)
    print(newChords)
    for i in range(len(tchords)):
        tchords[i].absChord = [] + newChords[i]

def classicalCS2WithRange(tchords, voiceRange = [(47, 67), (52, 76), (60, 81)]):
    allChords = pianoFilter(ChordSpaces.makeRange(voiceRange))
    # print(allChords[:10])
    qSpace = ChordSpaces.partition(ChordSpaces.opEq, allChords)
    # print(qSpace)
    chords = map(lambda x: x.absChord, tchords)
    # print(chords)
    newChords = Search.greedyProg(qSpace, ChordSpaces.opEq, testPred, Search.nearFall, chords)
    print(newChords)
    for i in range(len(tchords)):
        tchords[i].absChord = [] + newChords[i]

