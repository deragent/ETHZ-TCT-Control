import h5py
import numpy as np
import shutil

from .TCTData import TCTData

class FileHDF5(TCTData):

    def __init__(self, prefix):
        super().__init__(prefix)

        self.file = prefix.parent / f'{prefix.name}.hdf5'

        self.stream = None
        self._count = None
        self._metadata = None

    def load(self):
        if self.stream is None:
            self.stream = h5py.File(self.file, 'r')

            self._count = self.stream['curves'].attrs['count']
            self._metadata = self.stream.attrs

    def metadata(self):
        self.load()
        self._metadata

    def count(self):
        self.load()
        return self._count

    def curve(self, idx):
        self.load()

        if idx >= self._count:
            return None

        data = np.array(self.stream['curves'][f'curve{idx:06d}'])
        return data.T

    def copy(self, target):
        target_file = target.parent / f'{target.name}.hdf5'

        shutil.copy2(self.file, target_file)
