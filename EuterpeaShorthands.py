from PythonEuterpea import *

# Capital letters had to be used here to avoid conflict with "as" to mean a-sharp

def pcToNote(pcnum, oct, dur, vol=100):
    return Note(pcnum+(oct+1)*12, dur, vol)

def Cf(oct, dur, vol=100):
    return pcToNote(-1, oct, dur, vol)

def C(oct, dur, vol=100):
    return pcToNote(0, oct, dur, vol)

def Cs(oct, dur, vol=100):
    return pcToNote(1, oct, dur, vol)

def Df(oct, dur, vol=100):
    return pcToNote(1, oct, dur, vol)

def D(oct, dur, vol=100):
    return pcToNote(2, oct, dur, vol)

def Ds(oct, dur, vol=100):
    return pcToNote(3, oct, dur, vol)

def Ef(oct, dur, vol=100):
    return pcToNote(3, oct, dur, vol)

def E(oct, dur, vol=100):
    return pcToNote(4, oct, dur, vol)

def F(oct, dur, vol=100):
    return pcToNote(5, oct, dur, vol)

def Fs(oct, dur, vol=100):
    return pcToNote(6, oct, dur, vol)

def Gf(oct, dur, vol=100):
    return pcToNote(6, oct, dur, vol)

def G(oct, dur, vol=100):
    return pcToNote(7, oct, dur, vol)

def Gs(oct, dur, vol=100):
    return pcToNote(8, oct, dur, vol)

def Af(oct, dur, vol=100):
    return pcToNote(8, oct, dur, vol)

def A(oct, dur, vol=100):
    return pcToNote(9, oct, dur, vol)

def As(oct, dur, vol=100):
    return pcToNote(10, oct, dur, vol)

def Bf(oct, dur, vol=100):
    return pcToNote(10, oct, dur, vol)

def B(oct, dur, vol=100):
    return pcToNote(11, oct, dur, vol)

def Bs(oct, dur, vol=100):
    return pcToNote(12, oct, dur, vol)

