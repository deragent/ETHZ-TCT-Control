import numpy as np
import matplotlib.pyplot as plt

from ..preprocess import generic

class StartTimeFraction():

    def __init__(self, threshold, rise, fraction=0.3):
        self._threshold = threshold
        self._rise = rise

        self._fraction = fraction

    def fit(self, time, amplitude):
        peak = np.max(amplitude)

        start_idx = np.argmax(amplitude >= self._fraction*peak)

        if peak >= self._threshold:
            fit_sel = range(start_idx-1*self._rise, start_idx+2*self._rise)
            pfit = np.polyfit(time[fit_sel], amplitude[fit_sel], 1)

            return -1*pfit[1]/pfit[0]
        else:
            return float('nan')

class StartTimeGradient():
    def __init__(self, threshold, rise):
        self._threshold = threshold
        self._rise = rise

    def fit(self, time, amplitude, debug=False):

        amplitude_filtered =  generic.MovingAvg(amplitude, Navg=40)
        gradient = np.gradient(amplitude_filtered)
        gradient_filtered = generic.MovingAvg(gradient, Navg=40)

        start_idx = np.argmax(gradient_filtered)

        if np.max(amplitude) >= self._threshold:
            fit_sel = range(start_idx-3*self._rise, start_idx+1*self._rise)
            pfit = np.polyfit(time[fit_sel], amplitude[fit_sel], 1)

            start = -1*pfit[1]/pfit[0]
        else:
            start = float('nan')

        if debug:
            return start, (amplitude_filtered, gradient_filtered, start_idx, fit_sel, pfit)
        else:
            return start

    def plot(self, time, amplitude):
        fig, (ax0, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]}, sharex = True)

        start, debug = self.fit(time, amplitude, debug=True)

        ax0.axhline(0, color='k', alpha=0.3)

        lines = ax0.plot(time, amplitude, label='TCT Pulse')
        ax0.plot(time, debug[0], color=lines[0].get_color(), linestyle='--', label='Filtered Pulse')

        time_fit = time[debug[3]]
        ax0.axvspan(time_fit[0], time_fit[-1], color='k', alpha=0.15, label='Fit Range')

        time_plot = np.linspace(start, time_fit[-1], 50)
        ax0.plot(time_plot, np.polyval(debug[4], time_plot), 'k-.', label='Linear Fit')

        ax1.plot(time, debug[1], 'g', label='Filtered Gradient')
        ax0.axvline(time[debug[2]], linestyle='--', color='k')
        ax1.axvline(time[debug[2]], linestyle='--', color='k', label='Maximum Gradient')

        ax0.plot(start, 0, color='r', marker='o', linestyle=None, label=f'Start Time')

        return fig, ax0, ax1



class MedianStartTime():

    def __init__(self, time_key='time[0]', amplitude_key='amplitude[0]', method=StartTimeGradient, **kwargs):
        self._method = method

        self._time_key = time_key
        self._amplitude_key = amplitude_key

        self._start_time = self._method(**kwargs)

    def fit(self, df, apply=None):
        df[':start'] = float('nan')

        for index, line in df.iterrows():
            time = line[self._time_key]
            amplitude = line[self._amplitude_key]

            df.loc[index, ':start'] = self._start_time.fit(time, amplitude)

        start_time = np.median(df.loc[df[':start'].notna(), ':start'])

        # Calculate corrected time series if desired
        if apply is not None:
            df[apply] = None
            for index, line in df.iterrows():
               df.at[index, apply] = line[self._time_key] - start_time

        return start_time
