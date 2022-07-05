from pathlib import Path

import pandas as pd

from .Scan import Scan

class DataDirCollection():

    def __init__(self, folder_list):

        self._dirs = []
        for folder in folder_list:
            self._dirs.append(DataDir(folder))

        self._rejoinInfo()

    def _rejoinInfo(self):
        infos = []
        for dir in self._dirs:
            infos.append(dir.scans())

        self._info = pd.concat(infos, axis=0)

    def reload(self):
        for dir in self._dirs:
            dir.reload()

        self._rejoinInfo()

    def scans(self):
        return self._info

    def scan(self, dataset):
        for dir in self._dirs:
            if dataset in dir._scans:
                return dir.scan(dataset)

        return None


class DataDir():

    def __init__(self, folder):

        self.folder = Path(folder)
        if not self.folder.is_dir():
            raise Exception(f'Data directory [{self.folder}] does not exist.')

        # self.global_log = self.folder / 'log.txt'

        self._info = None
        self._scans = {}
        self.reload()

    def _loadScan(self, path):
        dataset = path.name

        scan = Scan(path)
        info = scan.info()

        return dataset, info, scan

    def reload(self):
        info = {}
        self._scans = {}

        for path in self.folder.iterdir():
            if path.is_dir():
                try:
                    dataset, meta, scan = self._loadScan(path)

                    info[dataset] = meta
                    self._scans[dataset] = scan
                except Exception as e:
                    print(e)
                    pass

        self._info = pd.DataFrame.from_dict(info, orient='index')

    def scans(self):
        return self._info

    def scan(self, dataset):
        if dataset in self._scans:
            return self._scans[dataset]

        return None
