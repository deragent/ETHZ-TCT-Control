import h5py
import numpy as np

from .TCTData import TCTData

class FileHDF5(TCTData):

    def __init__(self, prefix):
        super().__init__(prefix)

        self.file = prefix.parent / f'{prefix.name}.hdf5'
        self.stream = h5py.File(self.file, 'r')

        self._count = self.stream['curves'].attrs['count']

        self._metadata = None

    def metadata(self):
        if self._metadata is None:
            self._metadata = self.stream.attrs

        self._metadata

    def count(self):
        return self._count

    def curve(self, idx):
        if idx >= self._count:
            return None

        data = np.array(self.stream['curves'][f'curve{idx:06d}'])

        return data.T
