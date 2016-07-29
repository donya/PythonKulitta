# Score-level representations and MIDI conversion for some Kulita features
# Code by Wen Sheng and Donya Quick
#
# Notable changes from previous versions:
#
# - Order of arguments to TNote and TChord constructors changed. The new order
#   works better with Python's ability to set default argument values.
#
# - Voice class removed (old code that wasn't being used). A voice is now just
#   a list of TNotes.
#
# - More values are now stored in TNote and TChord (for Haskell compat.)
#
# - More interface options added for working with lists of pitch numbers.
#
# ---------------------------------------
#
# On the to-do list:
# - Fix bug in converting from TChords to voices
# - Introduce handling for rests as pitch -1
# - Handle onset information in an event list format.
#
# ---------------------------------------
#
# Important terms:
#
# - "Absolute pitch" or abspitch/AbsPitch is a pitch number. The Euterpea 
#   library used by the Haskell version of Kulitta uses Euterpea's
#   AbsPitch type, and we use the term here for consistency.
#
# - "Absolute chord" is just a chord consisting of abspitches. Chords are
#   vectors mathematically and implemented as lists in Python (and Haskell).
#
# - A "voice" is essentially a melody: a list of notes where each note starts
#   as soon as the previous one ends. Rests are currently not permitted.
#
# ---------------------------------------
#
# Important constants and bounds:
#
# - Pitches must be within the range 0-127, where pitch number 0 is C_0 in
#   the python-midi library. All pitches are integers.
#
# - The smallest time increment in MIDI is the tick. A lot of software uses 96
#   ticks per beat, so that is used here by default. However, some software
#   uses a lot more. For example, Cakewalk Sonar uses 960.
#
# - Durations in Kulitta are in terms of whole notes in 4/4. A duration of 1.0
#   indicates a whole note, which at 120bpm lasts 2 seconds.
#
# =============================================================================

import midi
import itertools

# Tick resolution constant
RESOLUTION = 96


# Mode definition borrowed from PythonKulitta's MusicGrammars.py
# It defines constants for reference in the form Mode.MAJOR, etc.
class Mode:
    MAJOR = "Major"
    MINOR = "Minor"
    MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
    MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]

# A Key holds a root (absolute pitch) and a mode.
class Key:
    def __init__(self, absPitch, mode_name):
        self.absPitch = absPitch
        self.mode = mode_name

DEFAULT_KEY = Key(0, Mode.MAJOR)
        

# A TNote is a "temporal note" with two pieces of information: 
# a pitch number (abspitch) and a duration.
class TNote:
    def __init__(self, absPitch, dur=1.0, vol=100, key=DEFAULT_KEY, onset=0):
        # deep copy of key
        self.key = Key(key.absPitch, key.mode)
        self.dur = dur
        self.absPitch = absPitch
        self.vol = vol
        self.onset = onset
    def __str__(self):
        return "("+str(self.absPitch)+","+str(self.dur)+")"
    def __repr__(self):
        return str(self)

# A TChord is a "temporal chord." All of the notes have the same 
# duration and are assumed to play simultaneously.
class TChord:
    def __init__(self, absChord, dur=1.0, vol=100, key=DEFAULT_KEY, onset=0):
        # deep copy of abschord, key
        self.key = Key(key.absPitch, key.mode)
        self.dur = dur
        self.absChord = [] + absChord
        self.onset = onset
        self.vol = vol
    def __str__(self):
        return "("+str(self.absChord)+","+str(self.dur)+")"
    def __repr__(self):
        return str(self)
        
# A Voice is a list of TNotes - basically a melody. Each note is 
# assumed to start immediately after the previous note ends.
#class Voice:
#    def __init__(self, tnotes):
#        # deep copy
#        self.tNotes = [TNote(tnote.absPitch, tnote.dur, tnote.vol, tnote.key, tnote.onset) for tnote in tnotes]

#Transforms over TNotes for compatibility with Haskell implementation

def tnK(tNote): # fetch the key information
    return tNote.key

def tnD(tNote): # fetch the duration
    return tNote.dur

def tnP(tNote): # fetch the pitch
    return tNote.absPitch

def newP (tNote, p1): # change just the pitch
    tNote.absPitch = p1

def trans_p(key, p1): 
    key.absPitch = (key.absPitch + p1) % 12


# Converting TChords to a MIDI file
def tChordsToMidi(tChords, filename):
    # Instantiate a MIDI Pattern (contains a list of tracks)
    pattern = midi.Pattern()
    # Set the tick per beat resolution
    pattern.resolution = RESOLUTION
    # Instantiate a MIDI Track (contains a list of MIDI events)
    track = midi.Track()
    # Append the track to the pattern
    pattern.append(track)
    # Iterate through each chord and write it to a track
    for tChord in tChords:
        writeChord(tChord, track)
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    # Save the pattern to disk
    midi.write_midifile(filename + '.mid', pattern)

def voiceToMidi(voice, filename):
    # Instantiate a MIDI Pattern (contains a list of tracks)
    pattern = midi.Pattern()
    # Set the tick per beat resolution
    pattern.resolution = RESOLUTION
    # Instantiate a MIDI Track (contains a list of MIDI events)
    track = midi.Track()
    #track.append(midi.SetTempoEvent())
    # Append the track to the pattern
    pattern.append(track)
    # Iterate through each chord and write it to a track
    for tnote in voice:
        writeNote(tnote, track)
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    # Save the pattern to disk
    midi.write_midifile(filename + '.mid', pattern)

# toVoices converts chords to voices. Mathematically, this is essentially 
# just a matrix transposition of the pitches. Durations for each chord are 
# copied into each of their resulting TNotes. The resulting music will 
# sound exactly the same.
def toVoices(tChords):
    tNoteChords = map(lambda tc: toTNotes(tc), tChords)
    return map(list, zip(*tNoteChords))

# toTNotes converts a single chord to a list of TNotes.
def toTNotes(tChord):
    notes = map (lambda p: TNote(p, tChord.dur, tChord.vol, tChord.key, tChord.onset), tChord.absChord)
    return notes


# toPitch converts a pitch number into a tuple represetation of 
# a pitch class and an octave.
def toPitch(absPitch):
    note_idx = absPitch % 12
    octave_idx = absPitch / 12
    return eval("midi.%s_%d" % (midi.NOTE_NAMES[note_idx], octave_idx))

# Auxilliary function to add a chord to a MIDI track
def writeChord(tChord, track):
    if len(tChord.absChord) == 0:
        return
    absChd = tChord.absChord
    dur = tChord.dur
    tickDur = toMidiTick(dur)
    for a in absChd:
        track.append(midi.NoteOnEvent(tick=0, velocity=tChord.vol, pitch=toMidiPitch(a)))
    track.append(midi.NoteOffEvent(tick = tickDur, pitch = toMidiPitch(absChd[0])))
    for a in absChd[1:]:
        track.append(midi.NoteOffEvent(tick=0, pitch=toMidiPitch(a))) # Bug fix 26-July-2016

def writeNote(tNote, track):
    track.append(midi.NoteOnEvent(tick=0, velocity=tNote.vol, pitch=toMidiPitch(tNote.absPitch)))
    track.append(midi.NoteOffEvent(tick=toMidiTick(tNote.dur), pitch=toMidiPitch(tNote.absPitch)))

# Conversion from Kulitta's durations to MIDI ticks
def toMidiTick(dur):
    ticks = int(round(dur * RESOLUTION * 4)) # bug fix 26-June-2016
    return ticks

# Check whether a pitch is in the appropriate range
def toMidiPitch(pitchVal):
    # Euterpea start from 10 Cff
    if pitchVal < 0:
        raise Exception("Negative pitch value not supported: "+str(pitchVal))
    elif pitchVal > 127:
        raise Exception("Pitch value too large: "+str(pitchVal)+" (must be 0-127)")
    # 0 - 127
    # 0 = C_0
    return pitchVal

# pitchesToMidi writes a list of pitch numbers (0-127 each) to a file with
# default durations and volumes.
def pitchesToMidi(ps, filename, defaultDur=0.25, defaultVol=100):
    v = []
    for p in ps:
        v.append(TNote(p, defaultDur))
    voiceToMidi(v, filename)

# This version uses two lists: one for pitches and one for durations.
def pitchesDursToMidi1(ps, durs, filename, defaultVol=100):
    v = []
    for p,d in itertools.izip(ps,durs):
        v.append(TNote(p, d))
    voiceToMidi(v, filename)

# This version uses a list of pairs of the format: [(p1, d1), (p2, d2), ...]
def pdPairsToMidi(pds, filename, defaultVol=100):
    v = []
    for p,d in pds:
        v.append(TNote(p, d))
    voiceToMidi(v, filename)


# =============================================================================
# Test area

#x = TChord([40,45,47], 0.25, 100, Key(0, Mode.MAJOR))
#print x
#y = toTNotes(x)
#print y

#x = [TChord([40,45,47], 0.25, 100, Key(0, Mode.MAJOR)), TChord([60,63,67], 0.25, 70, Key(0, Mode.MAJOR))]
#print x
#y = toVoices(x)
#print y


#x = [TNote(60, 0.25, 100, Key(0, Mode.MAJOR)) , TNote(67, 0.25, 70, Key(0, Mode.MAJOR))]
#voiceToMidi(x, "test")

#ps = [60, 64, 67]
#pitchesToMidi(ps, "test2")

#ds = [0.25, 0.25, 0.5]
#pitchesDursToMidi1(ps, ds, "test3")

#pds = [(60, 0.25), (64, 0.25), (67, 0.5)]
#pdPairsToMidi(pds, "test4")