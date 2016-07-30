# ===============================================================================
# PythonEuterpea: a Python port of Haskell Euterpea's core score-level features.
# Author: Donya Quick
#
# This file requires GMInstruments.py and the pythonmidi library:
# https://github.com/vishnubob/python-midi
#
# Euterpea is a library for music representation and creation in the Haskell
# programming language. This file represents a port of the "core" features
# of Euterpea's score-level or note-level features. This includes classes that
# mirror the various constructors of the Music data type as well as functions
# for conversion to MIDI.
#
# Haskell Euterpea's "Music a" polymorphism is captured in the Note class by
# way of optional parameters like volume. There is also an optional params
# field that is not used by the MIDI export backend.
#
# Haskell Euterpea's Control structures are implemented a bit differently. This
# is how they work in Python:
#     - Tempo and Instrument are essentially the same.
#     - Transpose will not be used. Please use deepcopy and the transpose
#       function instead.
#     - Phrase and PhraseAttribute are not implemented.
#     - KeySig is not currently impemented.
#     - There is no direct equivalent of the Custom constructor.  Users can
#       supply other classes and modify the conversion to MEvents accordingly.
#
# Unfinished functions: cut, remove, invertAt, invert, removeInstruments,
# changeInstruments.
# ===============================================================================

from copy import deepcopy
import midi
from GMInstruments import *

# For throwing errors
class CustomException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)


# =================================================================
# DURATION CONSTANTS
# =================================================================

WN = 1.0 # whole note = one measure in 4/4
DHN = 0.75 # dotted half
HN = 0.5 #half note
DQN = 0.375 # dotted quarter
QN = 0.25 # quarter note
DEN = 0.1875 #dotted eighth
EN = 0.125 # eighth note
DSN = 0.09375 # dotted sixteenth
SN = 0.0625 # sixteenth note
DTN = 0.046875 # dotted thirtysecond
TN = 0.03125 # thirtysecond note



# =================================================================
# MUSICAL STRUCTURE REPRESENTATIONS
# Haskell Euterpea features a type called Music, that is polymorphic
# and has several constructors. In Python, these constructors are
# represented as different classes that can (but do not have to)
# fall under an umbrella Music class to store everything.
# =================================================================

# A piece of music consists of a tree of musical structures interpreted within
# a particular base or reference tempo, the default for which is 120bpm.
class Music:
    def __init__(self, tree, bpm=120):
        self.tree=tree
        self.bpm=bpm
    def __str__(self):
        return ('Music('+str(self.tree)+ ', ' + str(self.bpm)+' bpm)')
    def __repr__(self):
        return str(self)

# A Euterpea Note has a pitch, duration, volume, and other possible parameters.
# (these other parameters are application-specific)
class Note:
    def __init__(self, pitch, dur=0.25, vol=100, params=None):
        self.pitch = pitch
        self.dur = dur
        self.vol = vol
    def __str__(self):
        return ('Note'+str((self.pitch, self.dur, self.vol)))
    def __repr__(self):
        return str(self)

# A Euterpea Rest has just a duration. It's a temporal place-holder just like a
# rest on a paper score.
class Rest:
    def __init__(self, dur):
        self.dur = dur
    def __str__(self):
        return ('Rest('+str(self.dur)+')')
    def __repr__(self):
        return str(self)

# Seq is equivalent to Haskell Euterpea's (:+:) operator. It composes two
# musical objects in sequence: left then right.
class Seq:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __str__(self):
        return ('('+str(self.left)+ ') :+: (' + str(self.right)+')')
    def __repr__(self):
        return str(self)

# Par is equivalent to Haskell Euterpea's (:=:) operator. It composes two
# musical objects in parallel: left and right happen starting at the same
# time.
class Par: # For composint two things in parallel
    def __init__(self, top, bot):
        self.top = top
        self.bot = bot
    def __str__(self):
        return ('('+str(self.top)+ ') :=: (' + str(self.bot)+')')
    def __repr__(self):
        return str(self)

# Modify is equivalent to Haskell Euterpea's Modify constructor and allows
# alterations to a musical tree. Which modifers are allowed are application
# specific.
class Modify:
    def __init__(self, modifier, tree):
        self.mod = modifier
        self.tree = tree
    def __str__(self):
        return ('Mod('+str(self.mod)+ ', ' + str(self.tree)+')')
    def __repr__(self):
        return str(self)

# A Tempo class to be used with the Modify class.
# Tempos are scaling factors, not bpm. If the current tempo is 120bpm
# and a Tempo(2.0) is applied, it results in 240bpm.
class Tempo:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return ('Tempo('+str(self.value)+')')
    def __repr__(self):
        return str(self)

# An Instrument class to be used with the Modify class.
PERC = True
INST = False
class Instrument:
    def __init__(self, value, itype=False):
        if isinstance(value, int):
            self.patch = (value, itype)
            self.name = gmName(self.patch) # need to update this - should look up from patch
        elif isinstance(value, basestring):
            self.name = value
            if self.name=="DRUMS":
                self.patch = (0, itype)
            else: self.patch = (gmNames.index(self.name), itype)
    def __str__(self):
        return (self.name+'('+str(self.patch[0])+')')
    def __repr__(self):
        return str(self)

def gmName(patch):
    if patch[0] < 0 or patch[0] > 127:
        return "NO_INSTRUMENT"
    elif patch[1]:
        return "DRUMS"
    else:
        return gmNames[patch[0]]


# =================================================================
# OPERATIOSN ON MUSICAL STRUCTURES
# Haskell Euterpea provides a number of basic operations on the
# Music type. Only a few of them are presented here.
# =================================================================

# Computes the duration of a music tree. Values are relative to the overall
# bpm for the entire tree, such that 0.25 is a quarter note.
def dur(x):
    if (x.__class__.__name__ == 'Music'):
        d = dur(x.tree)
        return d * (120/x.tempo)
    elif (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        return x.dur
    elif (x.__class__.__name__ == 'Seq'):
        return (dur(x.left) + dur(x.right))
    elif (x.__class__.__name__ == 'Par'):
        return max(dur(x.top), dur(x.bot))
    elif (x.__class__.__name__ == 'Modify'):
        if (x.mod.__class__.__name__ == 'Tempo'):
            d = dur(x.tree)
            return d / x.mod.value
        else:
            return dur(x.tree)
    else:
        raise CustomException("Unrecognized musical structure: "+str(x))

# The line function build a "melody" with Seq constructors
# out of a list of music substructures. Values are NOT copied.
def line(musicVals):
    tree = None
    for m in musicVals:
        if tree is None: tree = m
        else: tree = Seq(tree, m)
    return tree


# The chord function build a "chord" with Par constructors
# out of a list of music substructures. Values are NOT copied.
def chord(musicVals):
    tree = None
    for m in musicVals:
        if tree is None: tree = m
        else: tree = Par(tree, m)
    return tree

# The mMap function maps a function over the Notes in a Music value.
def mMap(f, x):
    if (x.__class__.__name__ == 'Music'):
        mMap(f, x.tree)
    elif (x.__class__.__name__ == 'Note'):
        f(x)
    elif (x.__class__.__name__ == 'Rest'):
        pass # nothing to do to a Rest
    elif (x.__class__.__name__ == 'Seq'):
        mMap(f, x.left)
        mMap(f, x.right)
    elif (x.__class__.__name__ == 'Par'):
        mMap(f, x.top)
        mMap(f, x.bot)
    elif (x.__class__.__name__ == 'Modify'):
        mMap(f, x.tree)
    else:
        raise CustomException("Unrecognized musical structure: "+str(x))


# The mMapDur function is not found in Haskell Euterpea but may prove useful.
# It maps a function over Notes and Rests and applies it to the entire musical
# structure. Note: the function MUST handle the constructors directly if using
# something other than dur.
def mMapAll(f, x):
    if (x.__class__.__name__ == 'Music'):
        mMapAll(f, x.tree)
    elif (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        f(x)
    elif (x.__class__.__name__ == 'Seq'):
        mMapAll(f, x.left)
        mMapAll(f, x.right)
    elif (x.__class__.__name__ == 'Par'):
        mMapAll(f, x.top)
        mMapAll(f, x.bot)
    elif (x.__class__.__name__ == 'Modify'):
        mMapAll(f, x.tree)
    else:
        raise CustomException("Unrecognized musical structure: "+str(x))


# transpose directly alters the Notes of the supplied structure.
# Each Note's pitch number has amount added to it.
def transpose(x, amount):
    def f(xNote): xNote.pitch = xNote.pitch+amount
    mMap(f, x)

# The following volume-related functions deviate slightly from
# Haskell Euterpea's methods of handling volume. This is because
# the volume is stored directly in the Note class in Python, which
# is not the case in Haskell Euterpea. Note: volumes are not
# guaranteed to be integers with scaleVolume. You sould use
# intVolume before converting to MIDI. You may wish to use
# scaleVolumeInt instead.

def setVolume(x, volume): # set everything to a constant volume
    def f(xNote): xNote.vol = volume
    mMap(f,x)

def scaleVolume(x, factor): # multiply all volumes by a factor
    def f(xNote): xNote.vol = xNote.vol * factor
    mMap (f,x)

def scaleVolumeInt(x, factor): # multiply but then round to an integer
    def f(xNote): xNote.vol = int(round(xNote.vol * factor))
    mMap (f,x)

def adjustVolume(x, amount): # add a constant amount to all volumes
    def f(xNote): xNote.vol = xNote.vol + amount
    mMap (f,x)

# Check whether pitch and volume values are within 0-127.
# If they are not, an exception is thrown.
def checkMidiCompatible(x):
    def f(xNote):
        if xNote.vol < 0 or xNote.vol > 127:
            raise CustomException("Invalid volume found: "+str(xNote.vol))
        if xNote.pitch < 0 or xNote.pitch > 127:
            raise CustomException("Invalid pitch found: "+str(xNote.pitch))
    mMap (f,x)

# Check whether pitch and volume values are within 0-127.
# Values <0 are converted to 0 and those >127 become 127.
def forceMidiCompatible(x):
    def f(xNote):
        if xNote.vol < 0: xNote.vol = 0
        elif xNote.vol > 127: xNote.vol = 127
        if xNote.pitch <0: xNote.pitch = 0
        elif xNote.pitch >127: xNote.pitch = 127
    mMap (f,x)

# Reverse a musical structure in place (last note is first, etc.)
def reverse(x):
    if (x.__class__.__name__ == 'Music'):
        reverse(x.tree)
    elif (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        pass # nothing to do
    elif (x.__class__.__name__ == 'Seq'):
        temp = x.left
        x.left = x.right
        x.right = temp
        reverse(x.left)
        reverse(x.right)
    elif (x.__class__.__name__ == 'Par'):
        reverse(x.top)
        reverse(x.bot)
    elif (x.__class__.__name__ == 'Modify'):
        reverse(x.tree)
    else:
        raise CustomException("Unrecognized musical structure: "+str(x))

# Returns a new value that is n repetitions of the input musical structure
def times(music, n):
    if n <= 0: return Rest(0)
    else:
        m = deepcopy(music)
        return Seq(m, times(music, n-1))

# Returns the first duration amount of a musical structure
def cut(m, duration):
    if duration<=0: return Rest(0)
    else: pass

# The opposite of "cut," dropping the first duration amount
# and returning the rest.
def remove(m, duration):
    if duration<=0: return deepcopy(m)
    else: pass

def invertAt(m, pitch): pass

def invert(m): pass

def removeInstruments(m): pass

def changeInstrument(m, value): pass

# Scale all durations in a music structure by the same amount.
def scaleDurations(m, factor):
    def f(x): x.dur = x.dur*factor
    mMapAll(f, m)




# =================================================================
# EVENT-STYLE REPRESENTATION
# Euterpea features an event-based representation of music called
# MEvent. Conversion from Music to MEvent requires processing of
# certain modifiers, such as Tempo.
# =================================================================


# applyTempo copies its input and interprets its Tempo modifiers. This
# scales durations in the tree and removes Modify nodes for Tempo. The
# original input structure, however, is left unchanged.
def applyTempo(x, tempo=1.0):
    y = deepcopy(x)
    y = applyTempoInPlace(y, tempo)
    return y

# applyTempoInPlace performs in-place interpretation of Tempo modifiers.
# However, it still has to be used as: foo = applyTempoInPace(foo)
def applyTempoInPlace(x, tempo=1.0):
    if (x.__class__.__name__ == 'Music'):
        x.tree = applyTempo(x.tree, 120/x.bpm)
        x.bpm = 120
        return x
    elif (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        x.dur = x.dur / tempo
        return x
    elif (x.__class__.__name__ == 'Seq'):
        x.left = applyTempo(x.left, tempo)
        x.right = applyTempo(x.right, tempo)
        return x
    elif (x.__class__.__name__ == 'Par'):
        x.top = applyTempo(x.top, tempo)
        x.bot = applyTempo(x.bot, tempo)
        return x
    elif (x.__class__.__name__ == 'Modify'):
        if (x.mod.__class__.__name__ == 'Tempo'):
            x.tree = applyTempo(x.tree, x.mod.value)
            return x.tree
        else:
            x.tree = applyTempo(x.tree, tempo)
            return x
    else:
        raise CustomException("Unrecognized musical structure: "+str(x))

# MEvent is a fairly direct representation of Haskell Euterpea's MEvent type,
# which is for event-style reasoning much like a piano roll representation.
# eTime is absolute time for a tempo of 120bpm. So, 0.25 is a quarter note at
# 128bpm. The patch field should be a patch number, like the patch field of
# the Instrument class.
class MEvent:
    def __init__(self, eTime, pitch, dur, vol=100, patch=(-1, INST)):
        self.eTime=eTime
        self.pitch=pitch
        self.dur=dur
        self.vol=vol
        self.patch=patch
    def __str__(self):
        return "MEvent("+str(self.eTime)+","+str(self.pitch)+","+str(self.dur) +")" # +","+str(self.patch)+")"
    def __repr__(self):
        return str(self)

# The musicToMEvents function converts a tree of Notes and Rests into an
# event structure.
def musicToMEvents(x, currentTime=0, currentInstrument=(-1,INST)):
    if (x.__class__.__name__ == 'Music'):
        y = applyTempo(x) # interpret all tempo scaling factors before continuing
        return musicToMEvents(y.tree, 0, -1)
    elif (x.__class__.__name__ == 'Note'):
        return [MEvent(currentTime, x.pitch, x.dur, x.vol, currentInstrument)] # one note = one event
    elif (x.__class__.__name__ == 'Rest'):
        return [] # rests don't contribute to an event representation
    elif (x.__class__.__name__ == 'Seq'):
        leftEvs = musicToMEvents(x.left, currentTime, currentInstrument)
        rightEvs = musicToMEvents(x.right, currentTime+dur(x.left), currentInstrument)
        return leftEvs + rightEvs # events can be concatenated, doesn't require sorting
    elif (x.__class__.__name__ == 'Par'):
        topEvs = musicToMEvents(x.top, currentTime, currentInstrument)
        botEvs = musicToMEvents(x.bot, currentTime, currentInstrument)
        return sorted(topEvs+botEvs, key=lambda e: e.eTime) # need to sort events by onset
    elif (x.__class__.__name__ == 'Modify'):
        if (x.mod.__class__.__name__ == 'Tempo'):
            y = applyTempo(x)
            return musicToMEvents(y, currentTime, currentInstrument)
        elif (x.mod.__class__.__name__ == 'Instrument'):
            return musicToMEvents(x.tree, currentTime, x.mod.patch)
    else:
        raise CustomException("Unrecognized musical structure: "+str(x))





# =================================================================
# MIDI CONVERSION BACKEND
# From this point onwards, we deviate from the Haskell Euterpea and
# provide classes and functions specific to peforming conversion to
# MIDI in Python.
# =================================================================

#First, some constants:
ON = 1 # note on event type
OFF = 0 # note off event type

# This is an intermediate type to aid in conversion to MIDI. A single
# MEvent will get split into two events, an on and off event. These
# then will need to be sorted by event time (eTime) in larger lists.
# Field information:
# - eTime will be either relative to the last event depending on the
#   current step on the way to conversion to MIDI.
# - eType should be either ON=1 or OFF=0.
class MEventMidi:
    def __init__(self, eTime, eType, pitch, vol=100, patch=-1):
        self.eTime = eTime
        self.eType = eType
        self.pitch = pitch
        self.vol = vol
        self.patch = patch
    def typeStr(self):
        return ["OFF", "ON"][self.eType]
    def __str__(self):
        return "MEMidi("+str(self.eTime)+","+str(self.pitch)+","+self.typeStr()+")"
    def __repr__(self):
        return str(self)

# This function is an intermediate on the way from the MEvent-style
# representation to MIDI format.
def mEventsToOnOff(mevs):
    def f(e):
        return [MEventMidi(e.eTime, ON, e.pitch, e.vol, e.patch),
                MEventMidi(e.eTime+e.dur, OFF, e.pitch, e.vol, e.patch)]
    onOffs = []
    for e in mevs:
        onOffs = onOffs + f(e)
    return sorted(onOffs, key=lambda e: e.eTime)

# This function will convert an event sequence with an eTime field into
# a relative time stamp format (time since the last event). This is intended
# for use with the MEventMidi type.
def onOffToRelDur(evs):
    durs = [0] + map (lambda e: e.eTime, evs)
    for i in range(0, len(evs)):
        evs[i].eTime -= durs[i]


def eventPatchList(mevs):
    patches = map (lambda e: e.patch, mevs) # extract just the patch from each note
    return list(set(patches)) # remove duplicates

# A linearPatchMap assigns channels to instruments exculsively and top to bottom
# with the exception of percussion, which will always fall on channel 9. Note that
# this implementation allows the creation of tracks without any program changes
# through the use of negative numbers.
def linearPatchMap(patchList):
    currChan = 0 # start from channel 0 and work upward
    pmap = [] # initialize patch map to be empty
    for p in patchList:
        if p[1]: # do we have percussion?
            pmap.append((p,9))
        else:
            if currChan==15:
                print "ERROR: too many instruments. Only 15 unique instruments with percussion (channel 9) is allowed in MIDI."
            else:
                pmap.append((p,currChan)) # update channel map
                if currChan==8: currChan = 10 # step over percussion channel
                else: currChan = currChan+1 # increment channel counter
    return sorted(pmap, key = lambda x: x[1])

# This function splits a list of MEvents (or MEventMidis) by their
# patch number.
def splitByPatch(mevs, pListIn=[]):
    pList = []
    # did we already get a patch list?
    if len(pListIn)==0: pList = eventPatchList(mevs) # no - need to build it
    else: pList = pListIn # use what we already were supplied
    evsByPatch = [] # list of lists to sort events
    unsorted = mevs # our starting list to work with
    for p in pList: # for each patch...
        pEvs = [x for x in unsorted if x.patch == p] # fetch the list of matching events
        evsByPatch.append(pEvs) # add them to the outer list of lists
        unsorted = [x for x in unsorted if x not in pEvs] # which events are left over?
    return evsByPatch


# Tick resolution constant
RESOLUTION = 96

# Conversion from Kulitta's durations to MIDI ticks
def toMidiTick(dur):
    ticks = int(round(dur * RESOLUTION * 4)) # bug fix 26-June-2016
    return ticks

# Create a pythonmidi event from an MEventMidi value.
def toMidiEvent(onOffMsg):
    m = None
    ticks = toMidiTick(onOffMsg.eTime)
    p = int(onOffMsg.pitch)
    v = int(onOffMsg.vol)
    if onOffMsg.eType==ON: m = midi.NoteOnEvent(tick=ticks, velocity=v, pitch=p)
    else: m = midi.NoteOffEvent(tick=ticks, velocity=v, pitch=p)
    return m


# Converting MEvents to a MIDI file. The following function takes a music structure
# (Music, Seq, Par, etc.) and converts it to a pythonmidi Pattern. File-writing is
# not performed at this step.
def mEventsToPattern(mevs):
    pattern = midi.Pattern() # Instantiate a MIDI Pattern (contains a list of tracks)
    pattern.resolution = RESOLUTION # Set the tick per beat resolution
    pList = eventPatchList(mevs) # get list of active patches
    pmap = linearPatchMap(pList) # linear patch/channel assignment
    usedChannels = map(lambda p: p[1], pmap) # which channels are we using? (Important for drum track)
    mevsByPatch = splitByPatch(mevs, pList) # split event list by patch
    currChan = 0; # channel counter
    for i in range(0, len(pmap)):
        track = midi.Track()
        if currChan in usedChannels: # are we using this channel?
            # if yes, then we add events to it
            mevsP = mevsByPatch[i] # get the relevant collection of events
            if pmap[i][0][0] >= 0: # are we assigning an instrument?
                track.append(midi.ProgramChangeEvent(value=pmap[i][0][0])) # set the instrument
            mevsOnOff = mEventsToOnOff(mevsP) # convert to on/off messages
            onOffToRelDur(mevsOnOff) # convert to relative timestamps
            for e in mevsOnOff: # for each on/off event...
                m = toMidiEvent(e) # turn it into a pythonmidi event
                track.append(m) # add that event to the track
        currChan += 1 # increment channel counter
        track.append(midi.EndOfTrackEvent(tick=1)) # close the track (not optional!)
        pattern.append(track) # add the track to the pattern
    return pattern


# Backup definition prior to adding program change event handling
def mEventsToPatternOld(mevs):
    pattern = midi.Pattern() # Instantiate a MIDI Pattern (contains a list of tracks)
    pattern.resolution = RESOLUTION # Set the tick per beat resolution
    pList = eventPatchList(mevs) # get list of active patches
    pmap = linearPatchMap(pList) # linear patch/channel assignment
    print pmap
    mevsByPatch = splitByPatch(mevs, pList) # split event list by patch
    print "Number of unique patches: ", len(mevsByPatch)
    #for mevsP in mevsByPatch:
    for i in range(0, len(pList)):
        mevsP = mevsByPatch[i]
        track = midi.Track()
        track.append(midi.ProgramChangeEvent(value=pmap[i][0][0]))
        mevsOnOff = mEventsToOnOff(mevsP)
        print "On-Off: ", mevsOnOff
        onOffToRelDur(mevsOnOff)
        print "On-Off Rel: ", mevsOnOff
        #print "MEVS: ", mevsOnOff
        for e in mevsOnOff:
            m = toMidiEvent(e)
            track.append(m)
        track.append(midi.EndOfTrackEvent(tick=1)) # close the track
        pattern.append(track) # place the track in the pattern
    print "MIDI values: ", pattern
    return pattern

# musicToMidi takes a filename (which must end in ".mid") and a music structure and writes
# a MIDI file.
def musicToMidi(filename, music):
    checkMidiCompatible(music) # are the volumes and pitches within 0-127?
    e = musicToMEvents(music) # convert to MEvents
    p = mEventsToPattern(e) # convert to a pythonmidi Pattern
    midi.write_midifile(filename, p) # write the MIDI file




#=============================================================================================
# Testing Area

m1 = Modify(Tempo(2.0), line([Note(60, QN), Note(64,QN), Note(67,HN)]))
m2 = Modify(Tempo(2.0), chord([Note(60, WN), Note(64,WN), Note(67,WN)]))
m3 = Modify(Tempo(0.5), line([Note(67, QN), Note(64,QN), Note(60,HN)]))
t1 = Seq(m1,Seq(m2, m3))

print t1

t2 = deepcopy(t1)
reverse(t2)

print t2

mAll = Par(Modify(Instrument("BASS_LEAD"), t1), Modify(Instrument("OBOE"), t2))

musicToMidi("x.mid", mAll)
