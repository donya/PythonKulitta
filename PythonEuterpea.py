# ===============================================================================
# PythonEuterpea: a Python port of Haskell Euterpea's core score-level features.
# Author: Donya Quick
#
# Euterpea is a library for music representation and creation in the Haskell
# programming language. This file represents a port of the "core" features
# of Euterpea's score-level or note-level features. This includes classes that
# mirror the various constructors of the Music data type as well as functions
# for conversion to MIDI.
#
# ===============================================================================

from copy import deepcopy


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
            self.patch = 0 # need to update this - should look up from name
    def __str__(self):
        return (self.name+'('+str(self.patch[0])+')')
    def __repr__(self):
        return str(self)

def gmName(patch):
    if patch[0] < 0:
        return "NO_INSTRUMENT"
    elif patch[1]:
        return "DRUMS"
    else:
        return "INSTR" # NEED TO UPDATE WITH ACTUAL GM LOOKUP


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
        print ("Unrecognized musical structure: "+str(x))
        raise

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
        print ("Unrecognized musical structure: "+str(x))
        raise


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
        print ("Unrecognized musical structure: "+str(x))
        raise


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

def setVolume(x, volume):
    def f(xNote): xNote.vol = volume
    mMap(f,x)

def scaleVolume(x, factor):
    def f(xNote): xNote.vol = xNote.vol * factor
    mMap (f,x)

def scaleVolumeInt(x, factor):
    def f(xNote): xNote.vol = round(xNote.vol * factor)
    mMap (f,x)

def adjustVolume(x, amount):
    def f(xNote): xNote.vol = xNote.vol + amount
    mMap (f,x)

def checkMidiCompatible(x):
    def f(xNote):
        if xNote.vol < 0 or xNote.vol > 127:
            print ("Invalid volume found: "+str(xNote.vol))
            raise
        if xNote.pitch < 0 or xNote.pitch > 127:
            print ("Invalid pitch found: "+str(xNote.pitch))
            raise
    mMap (f,x)

def forceMidiCompatible(x):
    def f(xNote):
        if xNote.vol < 0: xNote.vol = 0
        elif xNote.vol > 127: xNote.vol = 127
        if xNote.pitch <0: xNote.pitch = 0
        elif xNote.pitch >127: xNote.pitch = 127
    mMap (f,x)



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
        raise Exception("Unrecognized musical structure: "+str(x))

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
        return "MEvent("+str(self.eTime)+","+str(self.pitch)+","+str(self.dur)+","+str(self.patch)+")"
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
        rightEvs = musicToMEvents(x.right, dur(x.left), currentInstrument)
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
        raise Exception("Unrecognized musical structure: "+str(x))





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
    def toMidiEvent(self):
        if self.eType==ON:
            return None
        elif self.eType==OFF:
            return None
        else:
            print ("Unrecognized musical structure: "+str(x))
            raise
    def __str__(self):
        return "MEMidi("+str(self.eTime)+","+str(self.pitch)+","+self.typeStr()+")"
    def __repr__(self):
        return str(self)

# This function is an intermediate on the way from the MEvent-style
# representation to MIDI format.
def mEventsToOnOff(mevs):
    print "Input: ", mevs
    def f(e):
        return [MEventMidi(e.eTime, ON, e.pitch, e.vol, e.patch),
                MEventMidi(e.eTime+e.dur, OFF, e.pitch, e.vol, e.patch)]
    onOffs = []
    for e in mevs:
        onOffs = onOffs + f(e)
    #mevsPairs = map (lambda e: f(e), mevs)
    #print mevsPairs
    #mevsFlat = [item for sublist in mevsPairs for item in sublist]
    return sorted(onOffs, key=lambda e: e.eTime)

# This function will convert an event sequence with an eTime field into
# a relative time stamp format (time since the last event). This is intended
# for use with the MEventMidi type.
def onOffToRelDur(evs):
    currTime = 0
    nextTime = 0
    for i in range(0, len(evs)):
        nextTime = evs[i].eTime
        evs[i].eTime = evs[i].eTime - currTime
        currTime = nextTime


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
                print "ERROR: too many instruments. Only 15 unique instruments + percussion is allowed in MIDI."
            else:
                pmap.append((p,currChan)) # update channel map
                if currChan==8: currChan = 10 # step over percussion channel
                else: currChan = currChan+1 # increment channel counter


def splitByPatch(mevs):
    pmap = linearPatchMap(eventPatchList(mevs))




#=============================================================================================
# Testing Area

m = Modify(Instrument(7), Modify(Tempo(0.5), chord([Note(60, 0.25), Note(64,0.25), Note(67,0.50)])))
transpose(m,2)
scaleVolume(m,1.2)
print m
e = musicToMEvents(m)
print e
print eventPatchList(e)
