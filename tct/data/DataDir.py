from pathlib import Path
import time
from datetime import datetime

import pandas as pd
import slugify
import yaml

from ..logger import Logger
from .output import FileHDF5

class ScanDir():

    def __init__(self, parent, entry, datadir, type=FileHDF5):
        self.entry = entry

        self.folder = Path(parent) / entry
        self.folder.mkdir(exist_ok = False)

        self.datadir = datadir

        self._output = type

        self.meta = self.folder / 'meta'
        self.meta.mkdir(exist_ok = False)
        self.data = self.folder / 'data'
        self.data.mkdir(exist_ok = False)

        self._list = []
        self._count = 0

    def logger(self, print=True, debug=False):
        return Logger(
            [self.datadir.global_log, self.folder / 'log.log'],
            print=print, debug=debug
        )

    def saveConfig(self, scanfile):
        return scanfile.copy(self.meta / 'config.yaml')

    def writeMetaData(self, metadata):
        with open(self.meta / 'info.yaml', 'w') as stream:
            yaml.dump(metadata, stream)

    def writeList(self):
        data = pd.DataFrame.from_dict(self._list)
        data.to_csv(self.meta / 'list.csv')

    def addEntry(self, state):
        prefix = f'A{self._count}'

        metadata = state.copy()
        metadata['_prefix'] = prefix
        self._list.append(metadata)

        self._count += 1
        return self._output(self.data / prefix)


class DataDir():

    def __init__(self, folder):

        self.folder = Path(folder)
        if not self.folder.is_dir():
            self.folder.mkdir()

        self.global_log = self.folder / 'log.txt'

    def createScan(self, name):
        slug = slugify.slugify(name, max_length=30)

        # This should ensure, that we have a new unique folder name
        time.sleep(1)
        entry = f'{datetime.now():%Y%m%d-%H%M%S}_{slug}'

        return ScanDir(self.folder, entry, self)

    def trash(self, entry):
        trash = self.folder / '_trash'
        trash.mkdir(exist_ok=True)

        folder = self.folder / entry
        folder.rename(trash / entry)

        return trash / entry
