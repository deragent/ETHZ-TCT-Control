import re
import numpy as np

from ..system import Scan
from .ConfigFile import ConfigFile
from .Definition import SETUP_KEYS
from .AnalysisDefinition import AnalysisDefinition

class ScanFile(ConfigFile):

    META_KEYS = ['name', 'description', 'operator', 'laser', 'aperture', 'sample', 'wafer', 'side']


    LIN_REG = r'^\s*lin\(\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*\)\s*$'
    LOG_REG = r'^\s*log\(\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*\)\s*$'
    RANGE_REG = r'^\s*range\(\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*,\s*([+\-0-9Ee.]+)\s*\)\s*$'


    def __init__(self, file):
        super().__init__(file)

        # Load all the data - This also verifies the file
        self.meta = self._getMeta()
        self.limits = self._getLimits()
        self.setup = self._getSetup()
        self.scope = self._getScope()
        self.end = self._getEnd()
        self.getScan()
        self.analysis = self._getAnalysis()


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
        #     raise ConfigFile.ConfigError(self, '[scope] has a bad definition!')

        # average is now part of the state / setup

        pass


    def _parseScanValues(self, definition, values=None):
        if values is None:
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

            elif isinstance(entry, list):
                self._parseScanValues(entry, values)
            else:
                values.append(entry)

        return values

    def getScan(self):
        scan = Scan()

        data = self._get(['scan'], required=True)
        if not isinstance(data, list):
            raise ConfigFile.ConfigError(self, '[scan] needs to be a list of parameter with values!')

        for line in data:
            try:
                key = list(line.keys())[0]
                definition = line[key]

                # Detect parameter which is iterated manually
                if key.startswith('manual-'):
                    manual = True
                    param = key
                else:
                    manual = False
                    param = self.translate(key)

                if not isinstance(definition, list):
                    definition = [definition]

                scan.addParameter(param, self._parseScanValues(definition), manual=manual)

            except:
                raise ConfigFile.ConfigError(self, f'Error while parsing scan entry [{line}]')

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
