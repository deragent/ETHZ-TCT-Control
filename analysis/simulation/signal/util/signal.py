import numpy as np
import scipy.interpolate

class Signal():

    def __init__(self, time, signal):
        self._time = np.array(time)
        self._signal = np.array(signal)

    def time(self):
        return self._time

    def signal(self):
        return self._signal

    def samples(self):
        return len(self._time)

    def __add__(self, o):
        if not np.array_equal(self.time(), o.time()):
            raise Exception('Can not add two signals with different time sampling!')

        return Signal(self.time(), self.signal() + o.signal())

    def resample(self, dt):
        time = self.time()
        signal = self.signal()

        fcubic = scipy.interpolate.interp1d(time, signal)
        time_even = np.arange(np.min(time), np.max(time), dt)
        signal_even = fcubic(time_even)

        return SignalEven(time_even[0], dt, signal_even)


class SignalExtensible(Signal):

    def __init__(self):
        self._time = []
        self._signal = []

    def time(self):
        return np.array(self._time)

    def signal(self):
        return np.array(self._signal)

    def add(self, time, signal):
        self._time.append(time)
        self._signal.append(signal)


class SignalEven(Signal):

    def __init__(self, tstart, dt, signal):
        N = len(signal)
        time = np.linspace(tstart, tstart+N*dt, N, endpoint=False)

        self._tstart = tstart
        self._dt = dt

        super().__init__(time, signal)

    def __add__(self, o):
        if type(o) is SignalEven:
            if self._tstart != o._tstart or self._dt != o._dt:
                raise Exception('Can not add two signals with different time sampling!')

            return SignalEvent(self._tstart, self._dt, self.signal() + o.signal())
        else:
            super().__add__(o)

    def filterLowPass(self, fc, gain=1):
        sos_filter = sos_filter = scipy.signal.butter(1, fc, btype='low', analog=False, output='sos', fs=1/self._dt)

        signal_filter = scipy.signal.sosfilt(sos_filter, self.signal())
        signal_filter = signal_filter*gain

        return SignalEven(self._tstart, self._dt, signal_filter)
