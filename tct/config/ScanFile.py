import yaml
import re
import shutil
import numpy as np

from ..system import Scan
from .Definition import KEY_MAP, SETUP_KEYS
from .AnalysisDefinition import AnalysisDefinition

class ScanFile():

    class ConfigError(Exception):
        def __init__(self, config, msg=None):
            self.file = config._file
            self.msg = msg

        def __str__(self):
            msg = ''
            if self.msg is not None:
                msg = f': {self.msg}'

            return f'ScanFile Config Error [{self.file}]{msg}'

    class MissingError(ConfigError):
        def __init__(self, config, key):
            super().__init__(config)

            if isinstance(key, list):
                self.keys = key
            else:
                self.keys = [key]

            self.msg = f'Missing key [{".".join(self.keys)}]!'

    META_KEYS = ['name', 'description', 'operator', 'laser', 'aperture', 'sample', 'wafer', 'side']


    LIN_REG = r'^\s*lin\(\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*\)\s*$'
    LOG_REG = r'^\s*log\(\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*\)\s*$'
    RANGE_REG = r'^\s*range\(\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*\)\s*$'


    def __init__(self, file):
        self._file = file
        self._data = {}

        self._read()

        # Load all the data - This also verifies the file
        self.meta = self._getMeta()
        self.limits = self._getLimits()
        self.setup = self._getSetup()
        self.scope = self._getScope()
        self.end = self._getEnd()
        self.getScan()
        self.analysis = self._getAnalysis()

    def _read(self):
        with open(self._file, 'r') as stream:
            self._data = yaml.safe_load(stream)

    def write(self, file):
        with open(file, 'w') as stream:
            yaml.dump(self._data, stream)

    def copy(self, file):
        return shutil.copy(self._file, file)


    def _get(self, keys, required=False):
        if not isinstance(keys, list):
            keys = [keys]

        root = self._data
        for kk, key in enumerate(keys):
            if key not in root:
                if required:
                    raise ScanFile.MissingError(self, keys[:kk+1])
                else:
                    return None

            root = root[key]

        return root


    def translate(self, key):
        if key not in KEY_MAP:
            raise ScanFile.ConfigError(self, f'Key [{key}] is not valid!')

        return KEY_MAP[key]



    def _getMeta(self):
        meta = self._get(['meta'], required=True)

        values = {}
        for key in ScanFile.META_KEYS:
            values[key] = self._get(['meta', key], required=True)

        for key in meta:
            if key not in ScanFile.META_KEYS:
                values[key] = self._get(['meta', key])

        return values

    def _getLimits(self):
        return {
            'vlimit': self._get(['limits', 'voltage'], required=True),
            'ilimit': self._get(['limits', 'current'], required=True),
        }

    def _getSetup(self):
        state = {}

        state['amp.state'] = True
        state['laser.state'] = True
        state['bias.state'] = True

        for key in SETUP_KEYS:
            state[self.translate(key)] = self._get(['setup', key], required=True)

        return state

    def _getEnd(self):
        end = self._get(['end'])

        if end == 'on' or end is True:
            return {}
        elif isinstance(end, dict):
            state = {}
            for key in SETUP_KEYS:
                value = self._get(['end', key], required=False)
                if value is not None:
                    state[self.translate(key)] = value

            return state
        else:
            # Also for 'end' not present or 'end': off / False
            return False

    def _getScope(self):
        # TODO review

        # scope = self._get(['scope'], required=True)
        #
        # if scope == 'single':
        #     return {'type': 'single', 'count': 1}
        # elif 'single' in scope:
        #     return {'type': 'single', 'count': int(scope['single'])}
        # elif 'average' in scope:
        #     return {'type': 'average', 'count': int(scope['average'])}
        # else:
        #     raise ScanFile.ConfigError(self, '[scope] has a bad definition!')

        # average is now part of the state / setup

        pass


    def _parseScanValues(self, definition):
        values = []

        for entry in definition:
            if isinstance(entry, str):
                lin = re.search(ScanFile.LIN_REG, entry)
                log = re.search(ScanFile.LOG_REG, entry)
                range = re.search(ScanFile.RANGE_REG, entry)
                if lin:
                    values.extend(np.linspace(float(lin.group(1)), float(lin.group(2)), int(lin.group(3))))
                elif log:
                    values.extend(np.geomspace(float(log.group(1)), float(log.group(2)), int(log.group(3))))
                elif range:
                    values.extend(np.arange(float(range.group(1)), float(range.group(2)), float(range.group(3))))
                else:
                    raise Exception()

            else:
                values.append(entry)

        return values

    def getScan(self):
        scan = Scan()

        data = self._get(['scan'], required=True)
        if not isinstance(data, list):
            raise ScanFile.ConfigError(self, '[scan] needs to be a list of parameter with values!')

        for line in data:
            try:
                key = list(line.keys())[0]
                param = self.translate(key)
                definition = line[key]

                if not isinstance(definition, list):
                    definition = [definition]

                scan.addParameter(param, self._parseScanValues(definition))

            except:
                raise ScanFile.ConfigError(self, f'Error while parsing scan entry [{line}]')

        return scan

    def _getAnalysis(self):
        analysis = self._get(['analysis'], required=False)
        if analysis is None:
            return []

        if isinstance(analysis, dict):
            analysis = [analysis]

        definitions = []
        for entry in analysis:
            definitions.append(AnalysisDefinition(entry))

        return definitions
