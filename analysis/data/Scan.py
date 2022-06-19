from pathlib import Path

import numpy as np
import pandas as pd

from .load import FileHDF5

class Scan():

    TYPE_HDF5 = 'hdf5'

    FUNCTIONS = ['max()', 'min()', 'integral()']

    def __init__(self, folder, preprocess=None):
        self.folder = Path(folder)

        self.meta = self.folder / 'meta'
        self.data = self.folder / 'data'
        self.plot = self.folder / 'plot'

        self._list = pd.read_csv(self.meta / 'list.csv')

        self._pp = preprocess

    def list(self):
        return self._list

    def get(self, entry):
        type = self._list.iloc[entry]['_type']
        prefix = self._list.iloc[entry]['_prefix']

        if type == self.TYPE_HDF5:
            return FileHDF5(self.data / prefix)
        else:
            raise Exception(f'Unknown entry type [{type}]')

    def retrieve(self, keys):
        list_keys = [key for key in keys if key in self._list]
        other_keys = [key for key in keys if key not in self._list]

        list_data = self._list.copy()[list_keys]

        for key in other_keys:
            data = []

            for index, line in self._list.iterrows():
                # For now we only take the first curve into account.
                if key in self.FUNCTIONS:
                    # For now we only take the first curve into account.
                    data.append(self._applyFunction(key, index, 0))
                else:
                    raise Exception(f'Unknown function type [{key}]')

            list_data[key] = data

        return list_data


    def _applyFunction(self, fct, index, curve):
        if index not in self._list.index:
            raise Exception(f'{self.folder}: Entry [{index}] does not exist!')
        entry = self.get(index)
        if curve >= entry.count():
            raise Exception(f'{self.folder}: Curve [{curve}] for entry [{index}] does not exist!')

        time, amplitude = entry.curve(curve)
        sel = time >= 0

        if self._pp is None:
            offset = np.mean(amplitude[time < 0])

            amplitude = amplitude - offset
        else:
            amplitude = self._pp.Full(time, amplitude)
            amplitude = self._pp.RemoveReflection(time, amplitude)

        time = time[sel]
        amplitude = amplitude[sel]

        if fct == 'min()':
            return np.min(amplitude)
        elif fct == 'max()':
            return np.max(amplitude)
        elif fct == 'integral()':
            return np.trapz(amplitude, time)
        else:
            raise Exception(f'Unknwon function [{fct}]!')
