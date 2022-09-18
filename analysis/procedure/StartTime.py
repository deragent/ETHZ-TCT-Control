import numpy as np

class StartTime():

    def __init__(self, threshold, rise):
        self._threshold = threshold
        self._rise = rise

    def fit(self, time, amplitude):
        peak = np.max(amplitude)

        start_idx = np.argmax(amplitude >= 0.3*peak)

        if peak >= self._threshold:
            fit_sel = range(start_idx-1*self._rise, start_idx+2*self._rise)
            pfit = np.polyfit(time[fit_sel], amplitude[fit_sel], 1)

            return -1*pfit[1]/pfit[0]
        else:
            return float('nan')


class MedianStartTime():

    def __init__(self, time_key='time[0]', amplitude_key='amplitude[0]', **kwargs):
        self._time_key = time_key
        self._amplitude_key = amplitude_key

        self._start_time = StartTime(**kwargs)

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
