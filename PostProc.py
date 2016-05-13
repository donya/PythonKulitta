import ChordSpaces
import midi
from MusicGrammars import *
import ChordSpaces
import PTGG

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

class Key:
    def __init__(self, absPitch, mode_name):
        self.absPitch = absPitch
        self.mode = mode_name


class TChord:
    def __init__(self, key, dur, absChord):
        # deep copy of abschord, key
        self.key = Key(key.absPitch, key.mode)
        self.dur = dur
        self.absChord = [] + absChord

class RChord:
    def __init__(self, key, dur, c):
        self.key = Key(key.absPitch, key.mode)
        self.dur = dur
        self.ctype = c



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
    return map(toAbsChord, rchords)


def toAbsChord(rchord):
    to_as_res = toAs(rchord.ctype, rchord.key.mode)
    absChd = ChordSpaces.t(to_as_res, rchord.key.absPitch)
    key = rchord.key
    return TChord(Key(key.absPitch, key.mode), rchord.dur, absChd)

class TNote:
    def __init__(self, key, dur, absPitch):
        # deep copy of key
        self.key = Key(key.absPitch, key.mode)
        self.dur = dur
        self.absPitch = absPitch


class Voice:
    def __init__(self, tnotes):
        # deep copy
        self.tNotes = [TNote(tnote.key, tnote.dur, tnote.absPitch) for tnote in tnotes]


def tnK(tNote):
    return tNote.key


def tnD(tNote):
    return tNote.dur


def tnP(tNote):
    return tNote.absPitch


def newP (tNote, p1):
    tNote.absPitch = p1

def trans_p(key, p1):
    key.absPitch = (key.absPitch + p1) % 12


def atTrans(p1, tChords):
    for tChord in tChords:
        trans_p(tChord.key, p1)
        ChordSpaces.t(tChord.absChord, p1)


# left for midi
def tChodsToMusic(tChords, filename):
    # Instantiate a MIDI Pattern (contains a list of tracks)
    pattern = midi.Pattern()
    # Instantiate a MIDI Track (contains a list of MIDI events)
    track = midi.Track()
    # Append the track to the pattern
    pattern.append(track)

    for tChord in tChords:
        writeChord(tChord, track)
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    # Print out the pattern
    print(pattern)
    # Save the pattern to disk
    midi.write_midifile(filename + '.mid', pattern)


def toVoices(tChords):
    voices = []
    tcToList = lambda tcs: map((lambda tc: [tc.key, tc.dur, tc.absChord]), tcs)
    tcList = tcToList(tChords)
    ks, ds, ps = zip(*tcList)
    t_ps = zip(*ps)
    for i2 in range(t_ps):
        absPs = t_ps[i2]
        v = Voice(map(lambda k, d, p: TNote(k, d, p), ks, ds, absPs))
        voices.append(v)
    return voices


# add to_pitch function for intergrate with midi file
# or just use abspitch value
def toPitch(absPitch):
    note_idx = absPitch % 12
    octave_idx = absPitch / 12
    return eval("midi.%s_%d" % (midi.NOTE_NAMES[note_idx], octave_idx))


# class Pitch(absPitch)

def toNotes(voice):
    pass

def vsToMidi(voices, file_name):
    pass

def writeChord(tChord, track):
    if len(tChord.absChord) == 0:
        return
    absChd = tChord.absChord
    dur = tChord.dur
    # print dur
    dur = 0.25

    # print "dur: ", tChord.dur
    # print "k:", tChord.key.absPitch
    for a in absChd:
        track.append(midi.NoteOnEvent(tick=0, velocity=100, pitch=toMidiPitch(a)))
    track.append(midi.NoteOffEvent(tick = toMidiTick(dur), pitch = toMidiPitch(absChd[0])))
    for a in absChd[1:]:
        track.append(midi.NoteOffEvent(tick=toMidiTick(dur), pitch=toMidiPitch(a)))


def toMidiTick(dur):
    return int(dur * 231)
def toMidiPitch(pitchVal):
    # Euterpea start from 10 Cff
    if pitchVal < 0:
        raise Exception( "wrong pitch value")
    # 0 - 127 0 - C_0
    print("pitch:" + str(pitchVal))
    return pitchVal

