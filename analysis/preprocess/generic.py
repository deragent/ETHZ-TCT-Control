import numpy as np

def OffsetMean(time, signal, cutoff = 9e-9):
    offset = np.mean(signal[time < cutoff])
    return signal - offset

def MovingAvg(signal, Navg=60):
    return np.convolve(signal, 1/Navg*np.array([1]*Navg), 'same')
