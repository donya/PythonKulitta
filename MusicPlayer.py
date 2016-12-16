import pygame.midi as pm
import PythonEuterpea as pe
import time

class MusicPlayer:
    def __init__(self, output_port=0, init=True, startupDelay = 0.2):
        self.output_port = output_port
        self.buffer = list()
        self.model = None
        self.is_recording = False
        self.run_relay = True
        self.startupDelay = startupDelay # Needed to avoid messed up timing on first note played
        if (init):
            self.initialize()
            self.outDev = pm.Output(self.output_port)


    def initialize(self):
        pm.init()
        if self.startupDelay > 0:
            time.sleep(self.startupDelay)

    def close(self):
        self.outDev.close()

    def setOutputDevice(self, output_port):
        self.output_port = output_port
        self.outDev = pm.Output(output_port)


    def interactiveSetup(self):
        self.printDevices()

        # get an input ID from the console
        #self.input_port = pm.Input(int(input("Enter input device number: ")))

        # get an output ID from the console
        self.output_port = pm.Output(int(input("Enter output device number: ")))

    def printDevices(self):
        inputs, outputs = list(), list()
        bad_devices = list()    # TODO: Dead code consider revising or adding items to catch
        for i in range(0, pm.get_count()):
            info = pm.get_device_info(i)
            if info[1] not in bad_devices:
                target = inputs if info[2] > 0 else outputs
                target.append((i, info[1]))

        # print list of input devices
        #print "Input devices: "
        #for i in range(len(inputs)):
        #    print inputs[i]

        # print list of output devices
        print "Output devices: "
        for i in range(len(outputs)):
            print outputs[i]

    def playMusic(self, music):
        """
        NOTE: this implementation will have a "time leak" - if the CPU gets
        delayed, that time is lost and everything is pushed back. Generally
        we don't want this, but it protects against "note avalanches" in the
        event the CPU gets horribly delayed (so it can be useful for testing).
        """
        self.initialize()
        mEvs = pe.musicToMEvents(music)                 # convert to note event representation
        onOffs = pe.mEventsToOnOff(mEvs)                # convert to on-off pairs
        pe.onOffToRelDur(onOffs)                        # convert durations to relative durs
        onsetToSeconds(onOffs)                          # convert Euterpea time to seconds
        patches = pe.eventPatchList(mEvs)               # which Instruments are in use?
        pmap = pe.linearPatchMap(patches)               # build a patch map
        for p in pmap:                                  # for each patch that needs to be assigned...
            if p[0][0] > 0:
                self.outDev.set_instrument(p[0][0], p[1])      # set instrument for channel (instID, chan)
        for e in onOffs:                                # for each on/off event...
            time.sleep(e.eTime)                         # wait until the event should occur
            chanID = findChannel(pmap, e.patch)         # which channel are we on?
            if e.eType == pe.ON:                        # turn a note on?
                self.outDev.note_on(e.pitch, e.vol, chanID)    # need to update channel
            elif e.eType == pe.OFF:                     # turn a note off?
                self.outDev.note_off(e.pitch, e.vol, chanID)   # need to update channel


    def playMusicS(self, music):
        """
        This version of the playback function tries to correct for lost time
        by shifting future events forward in time if the current one gets delayed.
        """
        mEvs = pe.musicToMEvents(music)             # convert to note event representation
        onOffs = pe.mEventsToOnOff(mEvs)            # convert to on-off pairs
        pe.onOffToRelDur(onOffs)                    # convert durations to relative durs
        onsetToSeconds(onOffs)                      # convert Euterpea time to seconds
        patches = pe.eventPatchList(mEvs)           # which Instruments are in use?
        pmap = pe.linearPatchMap(patches)           # build a patch map
        for p in pmap:                              # for each patch that needs to be assigned...
            if p[0][0] > 0:
                self.outDev.set_instrument(p[0][0], p[1])  # set instrument for channel (instID, chan)
        t = time.time()     # get the current time
        tDelta = 0
        for e in onOffs:    # for each on/off event...
            # debugging: print 'time, delta:', e.eTime, tDelta, e.eTime - tDelta
            time.sleep(max(0, e.eTime - tDelta))        # wait until the event should occur, correcting for lateness
            chanID = findChannel(pmap, e.patch)         # which channel are we on?
            if e.eType == pe.ON:                        # turn a note on?
                self.outDev.note_on(e.pitch, e.vol, chanID)    # need to update channel
            elif e.eType == pe.OFF:                     # turn a note off?
                self.outDev.note_off(e.pitch, e.vol, chanID)   # need to update channel
            tActual = time.time() - t                   # how long did we actually sleep?
            tDelta = tActual - e.eTime  # max(0, tActual - e.eTime) # if we slept too long, speed up the next event
            t = time.time()                             # update our last timestamp



def onsetToSeconds(events):
    for e in events:
        e.eTime = e.eTime * 2  # 1 measure in Euterpea is 2 seconds at 120bpm


def findChannel(pmap, patch):
    i = 0
    while i < len(pmap):
        if patch == pmap[i][0]:
            return pmap[i][1]
        i += 1
    return -1