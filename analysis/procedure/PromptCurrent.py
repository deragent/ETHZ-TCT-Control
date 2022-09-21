import numpy as np

from analysis.preprocess import generic

class PromptCurrent():

    ## For source of Prompt-Current methode, see: https://ieeexplore.ieee.org/document/5550313
    ## And inspired by Sebastian Papa (CERN-SSD)

    def __init__(self, df, prompt_time, time_key='time[0]', amplitude_key='amplitude[0]', position_key=':position'):
        if ':prompt' not in df:
            df[':prompt'] = float('nan')

        if ':prompt_weighted' not in df:
            df[':prompt_weighted'] = float('nan')

        if ':prompt_efield' not in df:
            df[':prompt_efield'] = float('nan')

        self._df = df

        self._prompt_time = prompt_time

        self._time_key = time_key
        self._amplitude_key = amplitude_key
        self._position_key = position_key


    def full(self, selection=None, bias=None, field_start=None, field_end=None):

        if selection is None:
            selection = [True]*len(self._df.index)

        # Extract the prompt current
        for index, line in self._df[selection].iterrows():
            prompt_idx = np.argmax(line[self._time_key] >= self._prompt_time)
            self._df.loc[index, ':prompt'] = line[self._amplitude_key][prompt_idx]
            # self._df.loc[index, ':prompt'] = generic.MovingAvg(line[self._amplitude_key], Navg=100)[prompt_idx]

        ##  Calculate the weighted prompt current
        # This is an attempt, at renormalizing in places with little to no signal.
        # Not successful so far, with a factor of 0.1 to 0.2!
        eps = self._df.loc[selection, 'integral()'].max()*0
        self._df.loc[selection, ':prompt_weighted'] = self._df.loc[selection, ':prompt']/(eps + self._df.loc[selection, 'integral()'])

        # Calculate the E-Field if the bias voltage is given
        if bias is not None:
            position = self._df.loc[selection, self._position_key]
            prompt_weighted = self._df.loc[selection, ':prompt_weighted']

            # Select the E-Field range subset
            efield_range = position.notna()
            if field_start is not None:
                efield_range &= position >= field_start
            if field_end is not None:
                efield_range &= position <= field_end

            # Calculate the prompt integral (and fix sign if series is inverted)
            # We do for now not accept a series which is not monotonic!
            integral = np.trapz(prompt_weighted[efield_range], position[efield_range])
            if position[efield_range].is_monotonic_decreasing:
                integral *= -1
            elif not position[efield_range].is_monotonic_increasing:
                raise Exception('For E-Field calculation we expect a monotonic position series!')

            # Calculate the e-field via renormalization with the integral
            # This approach assumes, that the mobility (for holes and electrons is constant!)
            # For the bonded sensor samples, this assumption should be full-filled, due to the low electric field.
            # See pages 2296/2297 in the paper cited on top!
            efield = prompt_weighted/integral*bias

            self._df.loc[self._df.index[selection][efield_range], ':prompt_efield'] = efield
