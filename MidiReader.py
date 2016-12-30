'''
MIDI to PythonEuterpea Conversion
Donya Quick

Assumptions:
- No mixed-channel tracks (but there can be more than one track with the same channel)
- Ticks per beat = 96

Output format:
- Outermost Par(s) are by instrument
- Within an instrument's subtree, everything is still parallelized - each note is
  simply offset by a rest representing its onset time.
- All "expression" events like aftertouch, modulation, etc. are ignored.

Things not yet supported:
- Tempo change events (currently everything is 120bpm with on changes)
- ProgramChange events ocurring in the middle of a track. Currently assuming
  one track per instrument per channel.
'''

from midi import *
from PythonEuterpea import *
from MusicPlayer import *

def findNoteDuration(pitch, events):
    '''
    Scan through a list of MIDI events looking for a matching note-off.
    A note-on of the same pitch will also count to end the current note,
    assuming an instrument can't play the same note twice simultaneously.
    If no note-off is found, the end of the track is used to truncate
    the current note.
    :param pitch:
    :param events:
    :return:
    '''
    sumTicks = 0
    for e in events:
        sumTicks = sumTicks + e.tick
        c = e.__class__.__name__
        if c == "NoteOffEvent" or c == "NoteOnEvent":
            if e.data[0] == pitch:
                return sumTicks
    return sumTicks


def toPatch(channel, patch):
    '''
    Convert MIDI patch info to PythonEuterpea's version.
    :param channel: if this is 9, it's the drum track
    :param patch:
    :return: a tuple of an int and boolean, (patch, isDrums)
    '''
    if channel==9:
        return (patch, PERC)
    else:
        return (patch, INST)


def tickToDur(ticks):
    '''
    Convert from pythonmidi ticks back to PythonEuterpea durations
    :param ticks:
    :return:
    '''
    return float(ticks) / float((RESOLUTION * 4))

def getChannel(track):
    '''
    Determine the channel assigned to a track.
    ASSUMPTION: all events in the track should have the same channel.
    :param track:
    :return:
    '''
    if len(track) > 0:
        e = track[0]
        if (e.__class__.__name__ == "EndOfTrackEvent"):
            return -1
        return track[0].channel
    return -1

def trackToMEvents(track):
    '''
    Turn a pythonmidi track (list of events) into MEvents
    :param track:
    :return:
    '''
    currTicks = 0
    currPatch = -1
    channel = getChannel(track);
    mevs = []
    for i in range(0,len(track)):
        e = track[i]
        c = e.__class__.__name__
        currTicks = currTicks + e.tick # add time after last event
        if e.__class__.__name__ == "ProgramChangeEvent":
            print "INSTRUMENT", e
            # assign new instrument
            currPatch = e.data[0]
        elif c == "NoteOnEvent":
            # 1. find matching noteOn event OR another note on with the same pitch & channel
            noteDur = findNoteDuration(e.data[0], track[(i+1):])
            # 2. create an MEvent for the note
            #print "Note on ", currTicks, e.data, noteDur
            n = MEvent(tickToDur(currTicks), e.data[0], tickToDur(noteDur), e.data[1], patch=toPatch(channel, currPatch))
            mevs.append(n)
        elif c == "SetTempoEvent":
            print "Tempo change ignored (not supported yet): ", e
        elif c == "EndOfTrackEvent" or c == "NoteOffEvent":
            pass # nothing to do here
        else:
            print "Unsupported event type (ignored): ", e
    return mevs

def checkPatch(mevs):
    '''
    Determines the PythonEuterpea patch for a collection of MEvents.
    :param mevs:
    :return:
    '''
    retVal = (-1,INST)
    if len(mevs) > 0:
        retVal = mevs[0].patch
    return retVal

def mEventsToMusic(mevs):
    '''
    Convert a list of MEvents to a Music value
    :param mevs:
    :return:
    '''
    mVals = []
    patch = checkPatch(mevs) # NEED TO UPDATE THIS
    for e in mevs:
        n = Note(e.pitch, e.dur, e.vol)
        r = Rest(e.eTime)
        mVals.append(line([r,n]))
    mTotal = chord(mVals)
    if (patch[0] >= 0):
        i = Instrument(patch[0], patch[1])
        print "Instrument: ", i
        mTotal = Modify(i, mTotal)
    return mTotal

def midiToMusic(filename):
    '''
    Read a MIDI file and convert it to a Music structure.
    :param filename:
    :return:
    '''
    pattern = read_midifile(filename) # a list of tracks
    mVals = []
    for t in pattern:
        evs = trackToMEvents(t)
        if len(evs) > 0:
            mVals.append(mEventsToMusic(evs))
    return Music(chord(mVals), 120)



