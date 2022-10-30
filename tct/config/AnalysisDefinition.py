from .Definition import KEY_MAP

class AnalysisDefinition():

    TYPE_HIST = 'HIST'
    TYPE_2D = '2D'
    TYPE_3D = '3D'

    PLOT_MAX = 'max()'
    PLOT_MIN = 'min()'
    PLOT_INTEGRAL = 'integral()'

    FUNCTIONS = [
        PLOT_MAX,
        PLOT_MIN,
        PLOT_INTEGRAL,
    ]

    FIT_ERF = 'erf()'

    # Entries are: Name, Unit, Factor
    META = {
        'stage.x': ('x-Position', 'x', 'mm', 1),
        'stage.y': ('y-Position', 'y', 'mm', 1),
        'stage.z': ('z-Position', 'z', 'mm', 1),
        'stage.u': ('u-Angle', 'u', '°', 1),
        'stage.v': ('v-Angle', 'v', '°', 1),
        'stage.w': ('w-Angle', 'w', '°', 1),
        'stage.focus': ('Focus', 'Focus', 'mm', 1),
        'bias.hv': ('Bias-Voltage', 'HV', 'V', 1),
        'bias.current': ('Bias-Current', 'Leakage', 'uA', 1e6),
        'laser.dac': ('Laser Threshold (DAC)', 'DAC', '-', 1),
        'laser.frequency': ('Laser Rate', 'Rate', 'kHz', 1e-3),
        'amp.gain': ('Amplifier Gain', 'Gain', '%', 1),
        'scope.average': ('Oscilloscope Average', 'Average', '-', 1),
        'min()': ('Minimum Amplitude', 'max()', 'mV', 1e3),
        'max()': ('Maximum Amplitude', 'min()', 'mV', 1e3),
        'integral()': ('Pulse Integral', 'integral()', 'arb', 1e9),
        'count': ('Repetition', 'Repeat', '', 1),
        'time': ('Time', 'Time', '', 1),
        'temp.holder.stage': ('Stage Temperature', 'Stage', '°C', 1),
        'temp.holder.temperature': ('Holder Temperature', 'Holder', '°C', 1),
        'temp.holder.humidity': ('Holder Humidity', 'Holder', '%', 1),
    }

    def mapKey(self, key):
        if key in KEY_MAP:
            return KEY_MAP[key]

        return key


    # TODO In the Future:
    # Implement better checking of values

    def __init__(self, definition):
        self.definition = definition

        self.plot = self.mapKey(self._get('plot', required=True))

        if 'x' in definition:
            self.x = self.mapKey(self._get('x', required=True))

            if 'y' in definition:
                self.y = self.mapKey(self._get('y', required=True))
                self.type = AnalysisDefinition.TYPE_3D
            else:
                self.type = AnalysisDefinition.TYPE_2D

        else:
            self.type = AnalysisDefinition.TYPE_HIST

        groups = self._get('group', default=[])
        if not isinstance(groups, list):
            groups = [groups]
        self.group = [self.mapKey(group) for group in groups]

        self.fit = self._get('fit')

        self._title = self._get('title')
        self._name = self._get('name')

        self.scale = {
            'x': 'lin',
            'y': 'lin',
            'color': 'lin'
        }
        scale = self._get('scale', default={})
        for ax in self.scale:
            if ax in scale:
                self.scale[ax] = scale[ax]

    def _get(self, key, default=None, required=False):
        if key in self.definition:
            return self.definition[key]
        elif required:
            raise Exception(f'Missing analysis key [{key}]!')
        else:
            return default

    def getMeta(self, key):
        if key not in self.META:
            return key, key, 'na', 1

        return self.META[key]

    def name(self):
        '''Returns a name built from properties.
        To be used for example as a plot filename.'''
        if self._name is not None:
            return self._name

        group = '[' + '-'.join(self.group) + ']'
        if self.fit is None:
            fit = 'None'
        else:
            fit = self.fit

        if self.type == self.TYPE_3D:
            return f'Plot3D_{self.x}-{self.y}VS{self.plot}'
        elif self.type == self.TYPE_2D:
            return f'Plot2D_{self.x}VS{self.plot}{group}_{fit}'
        else:
            return f'Hist_{self.plot}{group}'

    def title(self):
        '''Returns a human readable title for the analysis.'''
        if self._title is not None:
            return self._title

        if self.type == self.TYPE_3D:
            return f'{self.plot} in function of {self.x} and {self.y}'
        elif self.type == self.TYPE_2D:
            return f'{self.plot} in function of {self.x}'
        else:
            return f'Histogram of {self.plot}'
