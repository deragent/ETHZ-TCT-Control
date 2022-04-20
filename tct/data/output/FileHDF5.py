import h5py
import numpy as np

from .TCTOutput import TCTOutput

class FileHDF5(TCTOutput):

    def __init__(self, prefix):
        super().__init__(prefix)
        
        self.stream = None

        self.file = prefix.parent / f'{prefix.name}.hdf5'
        self.stream =  h5py.File(self.file, 'w')

        self.curves = self.stream.create_group("curves")
        self.curves.attrs['count'] = 0

    def storeCurve(self, x, y, metadata={}):
        idx = self.curves.attrs['count']
        self.curves.attrs['count'] = idx+1

        data = np.column_stack((x, y))
        curve = self.curves.create_dataset(f'curve{idx:06d}', data=data)

        for key, value in metadata.items():
            curve.attrs[key] = value

    def storeMetaData(self, metadata):
        for key, value in metadata.items():
            self.stream.attrs[key] = value


    def __del__(self):
        if self.stream:
            self.stream.close()
            self.stream = None
