from pathlib import Path

import pandas as pd

from .load import FileHDF5

class Scan():

    TYPE_HDF5 = 'hdf5'

    def __init__(self, folder):
        self.folder = Path(folder)

        self.meta = self.folder / 'meta'
        self.data = self.folder / 'data'

        self._list = pd.read_csv(self.meta / 'list.csv')

    def list(self):
        return self._list

    def get(self, entry):
        type = self._list.iloc[entry]['_type']
        prefix = self._list.iloc[entry]['_prefix']

        if type == self.TYPE_HDF5:
            return FileHDF5(self.data / prefix)
        else:
            raise Exception(f'Unknown entry type [{type}]')
