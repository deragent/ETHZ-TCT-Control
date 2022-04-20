from .Definition import KEY_MAP

class AnalysisDefinition():

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
        'stage.focus': ('Focus', 'Focus', 'mm', 1),
        'bias.hv': ('Bias-Voltage', 'HV', 'V', 1),
        'bias.current': ('Bias-Current', 'Leakage', 'uA', 1e6),
        'laser.dac': ('Laser Threshold (DAC)', 'DAC', '-', 1),
        'laser.frequency': ('Laser Rate', 'Rate', 'kHz', 1e-3),
        'amp.gain': ('Amplifier Gain', 'Gain', '%', 1),
        'min()': ('Minimum Amplitude', 'max()', 'mV', 1e3),
        'max()': ('Maximum Amplitude', 'min(), ''mV', 1e3),
        'integral()': ('Pulse Integral', 'integral()', 'arb', 1e9)
    }

    def mapKey(self, key):
        if key in KEY_MAP:
            return KEY_MAP[key]

        return key


    # TODO In the Future:
    # Implement better checking of values

    def __init__(self, definition):

        self.x = self.mapKey(definition['x'])

        if 'y' in definition:
            self.y = self.mapKey(definition['y'])
            self.type = AnalysisDefinition.TYPE_3D
        else:
            self.type = AnalysisDefinition.TYPE_2D

        self.plot = self.mapKey(definition['plot'])

        self.group = []
        if 'group' in definition:
            groups = definition['group']
            if not isinstance(groups, list):
                groups = [groups]

            for group in groups:
                self.group.append(self.mapKey(group))

        self.fit = None
        if 'fit' in definition:
            self.fit = definition['fit']


    def getMeta(self, key):
        if key not in self.META:
            return key, key, 'na', 1

        return self.META[key]

    def name(self):
        '''Returns a name built from properties.
        To be used for example as a plot filename.'''

        group = '[' + '-'.join(self.group) + ']'
        if self.fit is None:
            fit = 'None'
        else:
            fit = self.fit

        if self.type == self.TYPE_3D:
            return f'Plot3D_{self.x}-{self.y}VS{self.plot}'
        else:
            return f'Plot2D_{self.x}VS{self.plot}{group}_{fit}'

    def title(self):
        '''Returns a human readable title for the analysis.'''

        if self.type == self.TYPE_3D:
            return f'{self.plot} in function of {self.x} and {self.y}'
        else:
            return f'{self.plot} in function of {self.x}'
