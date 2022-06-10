import numpy as np
import scipy.signal

from . import generic

def Offset(time, signal, cutoff = 9e-9):
    return generic.OffsetMean(time, signal, cutoff)

# Cut Frequency from FFT analysis of
# - P-Side Red (20220420-181650_p301401-e2-p-bias-voltage-scan)
# - Between 27ns and 44ns
# Q estimated from same analysis (BW ~ 0.15 GHz)
def Filter(time, signal, fcut=0.292e9, Q=1):
    dt = time[1]-time[0]
    notch_b, notch_a = scipy.signal.iirnotch(fcut, Q, 1/dt)
    filtered = scipy.signal.lfilter(notch_b, notch_a, signal)

    return filtered

    # return generic.MovingAvg(filtered, Navg=1)


def Full(time, signal):
    signal = Offset(time, signal)
    signal = Filter(time, signal)

    return signal


def RemoveReflection(time, signal):
    # For now use empirical best value
    refl_time = 21.9e-9
    factor = np.max(signal)/2.7

    # Calculate offset in samples
    dt = time[1] - time[0]
    refl_samples = int(np.rint(refl_time/dt))

    signal = np.copy(signal)
    signal[refl_samples:] -= factor*signal[:-refl_samples]

    return signal
