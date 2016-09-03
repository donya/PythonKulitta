# ===============================================================================
# PythonEuterpea: a Python port of Haskell Euterpea's core score-level features.
# Author: Donya Quick
# Last modified: 02-Sept-2016
#
# This file requires GMInstruments.py and the python-midi library:
# https://github.com/vishnubob/python-midi
#
# Python-midi can be installed with: pip install python-midi
#
# Euterpea is a library for music representation and creation in the Haskell
# programming language. This file represents a port of the "core" features
# of Euterpea's score-level or note-level features. This includes classes that
# mirror the various constructors of the Music data type as well as functions
# for conversion to MIDI.
#
# Haskell Euterpea's "Music a" polymorphism is captured in the Note class by
# way of optional parameters like vol (volume) and params (any type). There is
# also an optional params field that is not used by the MIDI export backend.
# ===============================================================================

from copy import deepcopy
import midi # This is the python-midi library
from GMInstruments import * # Bring in a bunch of GM instrument names

class EuterpeaException(Exception):
    """
    For throwing errors
    """
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


# =================================================================
# DURATION CONSTANTS
# =================================================================

WN = 1.0        # whole note = one measure in 4/4
DHN = 0.75      # dotted half
HN = 0.5        # half note
DQN = 0.375     # dotted quarter
QN = 0.25       # quarter note
DEN = 0.1875    # dotted eighth
EN = 0.125      # eighth note
DSN = 0.09375   # dotted sixteenth
SN = 0.0625     # sixteenth note
DTN = 0.046875  # dotted thirtysecond
TN = 0.03125    # thirtysecond note


# =================================================================
# MUSICAL STRUCTURE REPRESENTATIONS
# Haskell Euterpea features a type called Music, that is polymorphic
# and has several constructors. In Python, these constructors are
# represented as different classes that can (but do not have to)
# fall under an umbrella Music class to store everything.
# =================================================================

class Music:
    """
    A piece of music consists of a tree of musical structures interpreted within
    a particular base or reference tempo, the default for which is 120bpm.
    """
    def __init__(self, tree, bpm=120):
        self.tree = tree
        self.bpm = bpm

    def __str__(self):
        return 'Music(' + str(self.tree) + ', ' + str(self.bpm)+' bpm)'

    def __repr__(self):
        return str(self)


class Note:
    """
    A Euterpea Note has a pitch, duration, volume, and other possible parameters.
    (these other parameters are application-specific)
    """
    # TODO?: store params?  Perhaps as python dictionary param: **params ?
    def __init__(self, pitch, dur=0.25, vol=100, params=None):
        self.pitch = pitch
        self.dur = dur
        self.vol = vol
        self.params = params
    def __str__(self):
        return 'Note' + str((self.pitch, self.dur, self.vol))

    def __repr__(self):
        return str(self)


class Rest:
    """
    A Euterpea Rest has just a duration. It's a temporal place-holder just like a
    rest on a paper score.
    """
    def __init__(self, dur=0.25, params=None):
        self.dur = dur
        self.params = params
    def __str__(self):
        return 'Rest(' + str(self.dur) + ')'

    def __repr__(self):
        return str(self)


class Seq:
    """
    Seq is equivalent to Haskell Euterpexa's (:+:) operator. It composes two
    musical objects in sequence: left then right.
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return '(' + str(self.left) + ') :+: (' + str(self.right) + ')'

    def __repr__(self):
        return str(self)


class Par:  # For composing two things in parallel
    """
    Par is equivalent to Haskell Euterpea's (:=:) operator. It composes two
    musical objects in parallel: left and right happen starting at the same
    time.
    """
    def __init__(self, top, bot):
        self.top = top
        self.bot = bot

    def __str__(self):
        return '(' + str(self.top) + ') :=: (' + str(self.bot) + ')'

    def __repr__(self):
        return str(self)


class Modify:
    """
    Modify is equivalent to Haskell Euterpea's Modify constructor and allows
    alterations to a musical tree.  Which modifiers are allowed are application
    specific.
    """
    def __init__(self, modifier, tree):
        self.mod = modifier
        self.tree = tree

    def __str__(self):
        return 'Mod(' + str(self.mod) + ', ' + str(self.tree)+')'

    def __repr__(self):
        return str(self)


class Tempo:
    """
    A Tempo class to be used with the Modify class.
    Tempos are scaling factors, not bpm. If the current tempo is 120bpm
    and a Tempo(2.0) is applied, it results in 240bpm.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'Tempo(' + str(self.value) + ')'

    def __repr__(self):
        return str(self)


# Constants for instrument creation
PERC = True
INST = False


class Instrument:
    """
    An Instrument class to be used with the Modify class.
    """
    def __init__(self, value, itype=False):
        if isinstance(value, int):
            self.patch = (value, itype)
            self.name = gmName(self.patch)  # need to update this - should look up from patch
        elif isinstance(value, basestring):
            self.name = value
            if self.name=="DRUMS":
                self.patch = (0, itype)
            else:
                self.patch = (gmNames.index(self.name), itype)

    def __str__(self):
        return self.name + '(' + str(self.patch[0]) + ')'

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
# OPERATIONS ON MUSICAL STRUCTURES
# Haskell Euterpea provides a number of basic operations on the
# Music type. Only a few of them are presented here.
# =================================================================

def dur(x):
    """
    Computes the duration of a music tree. Values are relative to the overall
    bpm for the entire tree, such that 0.25 is a quarter note.
    :param x: the music structure
    :return: the duration of x in whole notes (wn = 1.0)
    """
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
        raise EuterpeaException("Unrecognized musical structure: "+str(x))


def line(musicVals):
    """
    The line function build a "melody" with Seq constructors
    out of a list of music substructures. Values are NOT copied.
    :param musicVals: a list of musical structures
    :return: the sequential composition of the input list
    """
    tree = None
    for m in musicVals:
        if tree is None: tree = m
        else: tree = Seq(tree, m)
    return tree



def chord(musicVals):
    '''
    The chord function build a "chord" with Par constructors
    out of a list of music substructures. Values are NOT copied.
    :param musicVals: a list of music structures
    :return: the parallel composition of the input
    '''
    tree = None
    for m in musicVals:
        if tree is None: tree = m
        else: tree = Par(tree, m)
    return tree


def mMap(f, x):
    '''
    The mMap function maps a function over the Notes in a Music value.
    :param f: Function to map over Notes
    :param x: the music structure to operate on
    :return: an in-place modification of the music structure
    '''
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
        raise EuterpeaException("Unrecognized musical structure: "+str(x))



def mMapAll(f, x):
    '''
    The mMapDur function is not found in Haskell Euterpea but may prove useful.
    It maps a function over Notes and Rests and applies it to the entire musical
    structure. Note: the function MUST handle the constructors directly if using
    something other than dur.
    :param f: The function to apply to durations (v.dur for a Note or Rest)
    :param x: the music structure to traverse
    :return: an in-place altered version of the music structure
    '''
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
        raise EuterpeaException("Unrecognized musical structure: "+str(x))



def transpose(x, amount):
    '''
    transpose directly alters the Notes of the supplied structure.
    Each Note's pitch number has amount added to it.
    :param x:
    :param amount:
    :return:
    '''
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


def checkMidiCompatible(x):
    '''
    Check whether pitch and volume values are within 0-127.
    If they are not, an exception is thrown.
    :param x: the music structure to search through
    :return: nothing if successful - otherwise an exception is thrown.
    '''
    def f(xNote):
        if xNote.vol < 0 or xNote.vol > 127:
            raise EuterpeaException("Invalid volume found: "+str(xNote.vol))
        if xNote.pitch < 0 or xNote.pitch > 127:
            raise EuterpeaException("Invalid pitch found: "+str(xNote.pitch))
    mMap (f,x)


def forceMidiCompatible(x):
    '''
    Check whether pitch and volume values are within 0-127.
    Values <0 are converted to 0 and those >127 become 127.
    :param x: the music structure to alter
    :return: a MIDI-compatible version of the input
    '''
    def f(xNote):
        if xNote.vol < 0: xNote.vol = 0
        elif xNote.vol > 127: xNote.vol = 127
        if xNote.pitch <0: xNote.pitch = 0
        elif xNote.pitch >127: xNote.pitch = 127
    mMap (f,x)


def reverse(x):
    '''
    Reverse a musical structure in place (last note is first, etc.)
    :param x: the music structure to reverse.
    :return: the reversal of the input.
    '''
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
        dTop = dur(x.top)
        dBot = dur(x.bot)
        # reversal affects relative start time of each section. Must add rests to correct.
        if dTop < dBot:
            x.top = Seq(Rest(dBot-dTop), x.top)
        elif dBot < dTop:
            x.bot = Seq(Rest(dTop-dBot), x.bot)
    elif (x.__class__.__name__ == 'Modify'):
        reverse(x.tree)
    else: raise EuterpeaException("Unrecognized musical structure: "+str(x))


def times(music, n):
    '''
    Returns a new value that is n repetitions of the input musical structure.
    Deep copy is used, so there will be no shared references between the input
    and the output.
    :param music: the music structure to repeat
    :param n: how many times to repeat?
    :return: a new structure (so this should be called as a = times(b,n)
    '''
    if n <= 0: return Rest(0)
    else:
        m = deepcopy(music)
        return Seq(m, times(music, n-1))


def cut(x, amount):
    '''
    Keeps only the first duration amount of a musical structure. The amount
    is in measures at the reference duration, which is 120bpm unless specified
    by the Music constructor. Note that this operation is messy - it can leave
    a lot of meaningless structure in place, with leaves occupied by Rest(0).
    :param x: the music value to alter
    :param amount: how many whole notes worth to take.
    :return: the furst amount of the music structure by time (whole note = 1.0)
    '''
    if (x.__class__.__name__ == 'Music'):
        cut(x.tree, amount)
    elif (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        if amount <= x.dur:
            x.dur = amount
    elif (x.__class__.__name__ == 'Seq'):
        dLeft = dur(x.left)
        if dLeft >= amount: # do we have enough duration on the left?
            cut(x.left, amount)
            x.right = Rest(0) # right side becomes nonexistent
        elif dLeft+dur(x.right) >= amount: # do we have enough duration on the right?
            cut(x.right, amount-dLeft)
    elif (x.__class__.__name__ == 'Par'):
        cut(x.top, amount)
        cut(x.bot, amount)
    elif (x.__class__.__name__ == 'Modify'):
        if (x.mod.__class__.__name__ == 'Tempo'):
            cut(x.tree, amount*x.mod.value)
        else:
            cut(x.tree, amount)
    else: raise EuterpeaException("Unrecognized musical structure: " + str(x))


def remove(x, amount):
    '''
    The opposite of "cut," chopping away the first amount. Note that this
    operation is messy - it can leave a lot of meaningless structure in
    place, with leaves occupied by Rest(0).
    :param x: the music structure to alter
    :param amount: how much to cut off of the beginning?
    :return:
    '''
    if amount<=0: pass # nothing to remove!
    elif (x.__class__.__name__ == 'Music'):
        remove(x.tree, amount)
    elif (x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest'):
        if amount >= x.dur:
            x.dur = 0
        if amount < x.dur:
            x.dur = x.dur - amount
    elif (x.__class__.__name__ == 'Seq'):
        dLeft = dur(x.left)
        if dLeft >= amount:
            remove(x.left, amount)
        elif dLeft + dur(x.right) >= amount:
            x.left = Rest(0) # remove all of the left side
            remove(x.right, amount-dLeft)
    elif (x.__class__.__name__ == 'Par'):
        remove(x.top, amount)
        remove(x.bot, amount)
    elif (x.__class__.__name__ == 'Modify'):
        if (x.mod.__class__.__name__ == 'Tempo'):
            remove(x.tree, amount*x.mod.value)
        else:
            remove(x.tree, amount)
    else: raise EuterpeaException("Unrecognized musical structure: " + str(x))


def mFold(x, noteOp, restOp, seqOp, parOp, modOp):
    '''
    The mFold operation traverses a music value with a series of operations
    for the various constructors. noteOp takes a Note, restOp takes a Rest,
    seqOp and parOp take the RESULTS of mFolding over their arguments, and
    modOp takes a modifier (x.mod) and the RESULT of mFolding over its
    tree (x.tree).
    :param x:
    :param noteOp:
    :param restOp:
    :param seqOp:
    :param parOp:
    :param modOp:
    :return:
    '''
    if (x.__class__.__name__ == 'Music'):
        return mFold(x.tree, noteOp, restOp, seqOp, parOp, modOp)
    elif (x.__class__.__name__ == 'Note'):
        return noteOp(x)
    elif (x.__class__.__name__ == 'Rest'):
        return restOp(x)
    elif (x.__class__.__name__ == 'Seq'):
        leftVal = mFold(x.left, noteOp, restOp, seqOp, parOp, modOp)
        rightVal = mFold(x.right, noteOp, restOp, seqOp, parOp, modOp)
        return seqOp(leftVal, rightVal)
    elif (x.__class__.__name__ == 'Par'):
        topVal = mFold(x.top, noteOp, restOp, seqOp, parOp, modOp)
        botVal = mFold(x.bot, noteOp, restOp, seqOp, parOp, modOp)
        return parOp(topVal, botVal)
    elif (x.__class__.__name__ == 'Modify'):
        val = mFold(x.tree, noteOp, restOp, seqOp, parOp, modOp)
        return modOp(x.mod, val)
    else: raise EuterpeaException("Unrecognized musical structure: " + str(x))

def firstPitch(x):
    '''
    The firstPitch function returns the first pitch in the Music value.
    None is returned if there are no notes. Preference is lef tand top.
    :param x:
    :return:
    '''
    if (x.__class__.__name__ == 'Music'):
        return firstPitch(x.tree)
    elif (x.__class__.__name__ == 'Note'):
        return x.pitch
    elif (x.__class__.__name__ == 'Rest'):
        return None
    elif (x.__class__.__name__ == 'Seq'):
        leftVal = firstPitch(x.left)
        if leftVal==None: return firstPitch(x.right)
        else: return leftVal
    elif (x.__class__.__name__ == 'Par'):
        topVal = firstPitch(x.top)
        if topVal==None: return firstPitch(x.bot)
        else: return topVal
    elif (x.__class__.__name__ == 'Modify'):
        return firstPitch(x.tree)
    else: raise EuterpeaException("Unrecognized musical structure: " + str(x))


def getPitches(m):
    '''
    An application of mFold to extract all pitches in the music
    structure as a list.
    :param m:
    :return:
    '''
    def fn(n): return [n.pitch]
    def fr(r): return []
    def fcat(a,b): return a+b
    def fm(m,t): return t
    return mFold(m, fn, fr, fcat, fcat, fm)


def invertAt(m, pitchRef):
    '''
    Musical inversion around a reference pitch. Metrical structure
    is preserved; only pitches are altered.
    :param m:
    :param pitchRef:
    :return:
    '''
    def f(aNote): aNote.pitch = 2 * pitchRef - aNote.pitch
    mMap(f, m)

def invert(m):
    '''
    Musical inversion around the first pitch in a musical structure.
    :param m:
    :return:
    '''
    p = firstPitch(m)
    invertAt(m, p)

def instrument(m, value):
    '''
    Shorthand for setting an instrument.
    :param m:
    :param value:
    :return:
    '''
    return Modify(Instrument(value), m)




def removeInstruments(x):
    '''
    Remove Instrument modifiers from a musical structure
    :param x:
    :return:
    '''
    def checkInstMod(x): # function to get rid of individual nodes
        if x.__class__.__name__ == 'Modify':
            if x.mod.__class__.__name__ == 'Instrument': return x.tree
            else: return x
        else: return x
    if x.__class__.__name__ == 'Music':
        tNew = checkInstMod(x.tree)
        removeInstruments(x.tree)
    elif x.__class__.__name__ == 'Note' or x.__class__.__name__ == 'Rest':
        pass
    elif x.__class__.__name__ == 'Seq':
        x.left = checkInstMod(x.left)
        x.right = checkInstMod(x.right)
        removeInstruments(x.left)
        removeInstruments(x.right)
    elif x.__class__.__name__ == 'Par':
        x.top = checkInstMod(x.top)
        x.bot = checkInstMod(x.bot)
        removeInstruments(x.top)
        removeInstruments(x.bot)
    elif x.__class__.__name__ == 'Modify':
        xNew = checkInstMod(x)
        x = xNew
    else: raise EuterpeaException("Unrecognized musical structure: " + str(x))

def changeInstrument(m, value):
    removeInstruments(m)
    instrument(value, m)

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



def applyTempo(x, tempo=1.0):
    '''
    applyTempo copies its input and interprets its Tempo modifiers. This
    scales durations in the tree and removes Modify nodes for Tempo. The
    original input structure, however, is left unchanged.
    :param x:
    :param tempo:
    :return:
    '''
    y = deepcopy(x)
    y = applyTempoInPlace(y, tempo)
    return y


def applyTempoInPlace(x, tempo=1.0):
    '''
    applyTempoInPlace performs in-place interpretation of Tempo modifiers.
    However, it still has to be used as: foo = applyTempoInPace(foo)
    :param x:
    :param tempo:
    :return:
    '''
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
        raise EuterpeaException("Unrecognized musical structure: "+str(x))


class MEvent:
    '''
    MEvent is a fairly direct representation of Haskell Euterpea's MEvent type,
    which is for event-style reasoning much like a piano roll representation.
    eTime is absolute time for a tempo of 120bpm. So, 0.25 is a quarter note at
    128bpm. The patch field should be a patch number, like the patch field of
    the Instrument class.
    '''
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


def musicToMEvents(x, currentTime=0, currentInstrument=(-1,INST)):
    '''
    The musicToMEvents function converts a tree of Notes and Rests into an
    event structure.
    :param x:
    :param currentTime:
    :param currentInstrument:
    :return:
    '''
    if (x.__class__.__name__ == 'Music'):
        y = applyTempo(x) # interpret all tempo scaling factors before continuing
        return musicToMEvents(y.tree, 0, -1)
    elif (x.__class__.__name__ == 'Note'):
        if x.dur > 0:
            return [MEvent(currentTime, x.pitch, x.dur, x.vol, currentInstrument)] # one note = one event
        else: # when duration is <0, there should be no event.
            return []
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
        raise EuterpeaException("Unrecognized musical structure: "+str(x))





# =================================================================
# MIDI CONVERSION BACKEND
# From this point onwards, we deviate from the Haskell Euterpea and
# provide classes and functions specific to peforming conversion to
# MIDI in Python.
# =================================================================

#First, some constants:
ON = 1 # note on event type
OFF = 0 # note off event type

class MEventMidi:
    '''
    This is an intermediate type to aid in conversion to MIDI. A single
    MEvent will get split into two events, an on and off event. These
    will need to be sorted by event time (eTime) in larger lists.
    Field information:
     - eTime will be either relative to the last event depending on the
       current step on the way to conversion to MIDI.
     - eType should be either ON=1 or OFF=0.
    '''
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

def mEventsToOnOff(mevs):
    '''
    This function is an intermediate on the way from the MEvent-style
    representation to MIDI format.
    :param mevs:
    :return:
    '''
    def f(e):
        return [MEventMidi(e.eTime, ON, e.pitch, e.vol, e.patch),
                MEventMidi(e.eTime+e.dur, OFF, e.pitch, e.vol, e.patch)]
    onOffs = []
    for e in mevs:
        onOffs = onOffs + f(e)
    return sorted(onOffs, key=lambda e: e.eTime)


def onOffToRelDur(evs):
    '''
    This function will convert an event sequence with an eTime field into
    a relative time stamp format (time since the last event). This is intended
    for use with the MEventMidi type.
    :param evs:
    :return:
    '''
    durs = [0] + map (lambda e: e.eTime, evs)
    for i in range(0, len(evs)):
        evs[i].eTime -= durs[i]


def eventPatchList(mevs):
    patches = map (lambda e: e.patch, mevs) # extract just the patch from each note
    return list(set(patches)) # remove duplicates


def linearPatchMap(patchList):
    '''
    A linearPatchMap assigns channels to instruments exculsively and top to bottom
    with the exception of percussion, which will always fall on channel 9. Note that
    this implementation allows the creation of tracks without any program changes
    through the use of negative numbers.
    :param patchList:
    :return:
    '''
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


def splitByPatch(mevs, pListIn=[]):
    '''
    This function splits a list of MEvents (or MEventMidis) by their
    patch number.
    :param mevs:
    :param pListIn:
    :return:
    '''
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



def mEventsToPattern(mevs):
    '''
    Converting MEvents to a MIDI file. The following function takes a music structure
    (Music, Seq, Par, etc.) and converts it to a pythonmidi Pattern. File-writing is
    not performed at this step.
    :param mevs:
    :return:
    '''
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


def musicToMidi(filename, music):
    '''
    musicToMidi takes a filename (which must end in ".mid") and a music structure and writes
    a MIDI file.
    :param filename:
    :param music:
    :return:
    '''
    checkMidiCompatible(music) # are the volumes and pitches within 0-127?
    e = musicToMEvents(music) # convert to MEvents
    p = mEventsToPattern(e) # convert to a pythonmidi Pattern
    midi.write_midifile(filename, p) # write the MIDI file


# =============================================================================================
# Some extra supporting functions for compatibility with more pure vector/list
# representations of melodies and chords.


# Convert a pitch number to a single note.
def pitchToNote(p, defDur=0.25, defVol=100):
    if p==None:
        return Rest(defDur)
    else:
        return Note(p, defDur, defVol)

# Convert a list of pitches to a melody using a default note duration.
def pitchListToMusic(ps, defDur=0.25, defVol=100):
    ns = map(pitchToNote, ps)
    return line(ns)

# Convert a list of pitch+duration pairs to a melody (a bunch of Notes in sequence).
def pdPairsToMusic(pds, defVol=100):
    """
    pdPair = pitch-duration pair
    :param pds:
    :param defVol:
    :return:
    """
    ns = map(lambda x: Note(x[0], x[1], defVol), pds)
    return line(ns)

# Convert a list of pitches to a chord (a bunch of Notes in parallel).
def pitchListToChord(ps, defDur=0.25, defVol=100):
    if ps == None:
        return Rest(defDur)
    else:
        ns = map (lambda p: Note(p, defDur, defVol), ps)
        return chord(ns)

# Convert a list of chords (a list of lists of pitches) to a music structure.
def chordListToMusic(chords, defDur=0.25, defVol=100):
    cList = map(lambda x: pitchListToChord(x, defDur, defVol), chords)
    return line(cList)

