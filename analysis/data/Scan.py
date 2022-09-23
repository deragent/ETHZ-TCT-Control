from pathlib import Path
import yaml
import atexit
import hashlib
import base64

import numpy as np
import pandas as pd

from .load import FileHDF5

class Scan():

    TYPE_HDF5 = 'hdf5'

    FUNCTIONS = ['max()', 'min()', 'integral()']
    CURVES = ['curve[0]', 'curve[1]']

    def __init__(self, folder, preprocess=None, use_cache=True, update_cache=True):
        self.folder = Path(folder)
        self.entry = self.folder.name

        self.meta = self.folder / 'meta'
        self.data = self.folder / 'data'
        self.plot = self.folder / 'plot'

        for folder in [self.meta, self.data, self.plot]:
            if not folder.is_dir():
                raise Exception(f'Scan folder [{folder}] does not exist.')

        self._list = pd.read_csv(self.meta / 'list.csv', parse_dates=['time'], index_col=[0])

        self._pp = preprocess

        self._use_cache = use_cache
        self._cache = {}
        self._cacheChanged = False
        self._loadCache()

        if update_cache:
            atexit.register(self._writeCache)

    def _cacheID(self, data):
        sha1 = hashlib.sha1(str(data).encode()).digest()
        return base64.b64encode(sha1).decode()

    # Using pandas.read_csv / to_csv for cache file access.
    # This proved to be much faster than for example yaml!

    def _loadCache(self):
        cache_file = self.meta / '.fct.cache'
        if cache_file.is_file():
            df = pd.read_csv(cache_file, index_col=0)
            self._cache = df.to_dict()['cache']

    def _lookupCache(self, id):
        if self._use_cache and id in self._cache:
            return self._cache[id]

        return None

    def _setCache(self, id, value):
        self._cache[id] = float(value)
        self._cacheChanged = True

    def _writeCache(self):
        if self._cacheChanged:
            df = pd.DataFrame.from_dict(self._cache, orient='index', columns=['cache'])
            df.to_csv(self.meta / '.fct.cache')


    def info(self):
        with open(self.meta / 'info.yaml', 'r') as stream:
            return yaml.safe_load(stream)

    def configStr(self):
        with open(self.meta / 'config.yaml', 'r') as stream:
            return stream.read()
    def config(self):
        with open(self.meta / 'config.yaml', 'r') as stream:
            return yaml.safe_load(stream)


    def plots(self):
        plots = sorted(self.plot.glob('*.pdf'))
        return [entry.stem for entry in plots]
    def plotFile(self, plot):
        if plot in self.plots():
            return self.plot / (plot + '.pdf')
        else:
            return None

    def list(self):
        return self._list

    def get(self, entry):
        type = self._list.iloc[entry]['_type']
        prefix = self._list.iloc[entry]['_prefix']

        if type == self.TYPE_HDF5:
            return FileHDF5(self.data / prefix)
        else:
            raise Exception(f'Unknown entry type [{type}]')

    def retrieve(self, keys, index=None):
        list_keys = [key for key in keys if key in self._list]
        other_keys = [key for key in keys if key not in self._list]

        list_data = self._list.copy()[list_keys]
        if index is not None:
            list_data = list_data[index]

        for key in other_keys:

            if key in self.CURVES:
                time_data = []
                amplitude_data = []

                number = int(key.split('[', 1)[1].replace(']', ''))

                for index, line in list_data.iterrows():
                    time, amplitude = self._getCurve(index, number)
                    time_data.append(time)
                    amplitude_data.append(amplitude)

                list_data[f'time[{number}]'] = time_data
                list_data[f'amplitude[{number}]'] = amplitude_data


            elif key in self.FUNCTIONS:
                data = []

                for index, line in list_data.iterrows():
                    # For now we only take the first curve into account.
                    data.append(self._applyFunction(key, index, 0))

                list_data[key] = data

            else:
                raise Exception(f'Unknown function/ curve type [{key}]')

        return list_data

    def _getCurve(self, index, number):
        entry = self.get(index)
        if number >= entry.count():
            raise Exception(f'{self.folder}: Curve [{number}] for entry [{index}] does not exist!')

        time, amplitude = entry.curve(number)
        time, amplitude = self._applyPreprocess(time, amplitude)

        return time, amplitude

    def _applyPreprocess(self, time, amplitude):
        if self._pp is None:
            offset = np.mean(amplitude[time < 0])

            amplitude = amplitude - offset
        else:
            amplitude = self._pp.Full(time, amplitude)

        return time, amplitude


    def _applyFunction(self, fct, index, curve):
        cache_id = self._cacheID((fct, index, curve, 'None' if self._pp is None else self._pp.__name__))

        cache = self._lookupCache(cache_id)
        if cache is not None:
            return cache

        if index not in self._list.index:
            raise Exception(f'{self.folder}: Entry [{index}] does not exist!')

        time, amplitude = self._getCurve(index, curve)

        sel = time >= 0
        time = time[sel]
        amplitude = amplitude[sel]

        if fct == 'min()':
            value = np.min(amplitude)
        elif fct == 'max()':
            value = np.max(amplitude)
        elif fct == 'integral()':
            value = np.trapz(amplitude, time)
        else:
            raise Exception(f'Unknwon function [{fct}]!')

        self._setCache(cache_id, value)

        return value
