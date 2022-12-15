KEY_MAP = {
    'gain': 'amp.gain',
    'hv': 'bias.hv',
    'x': 'stage.x',
    'y': 'stage.y',
    'focus': 'stage.focus',
    'frequency': 'laser.frequency',
    'dac': 'laser.dac',
    'average': 'scope.average',
    'amplitude': 'scope.amplitude',
    'repeat': 'count',
}

SETUP_KEYS = [
    'gain',
    'hv',
    'x',
    'y',
    'focus',
    'frequency',
    'dac',
    'average',
    'amplitude',
]


class MODE:
    LASER = 'laser'
    SOURCE = 'source'

    def __init__(self, config):
        if config is None:
            self.mode = self.LASER
        else:
            config = config.strip().lower()
            if config in [self.LASER, self.SOURCE]:
                self.mode = config
            else:
                raise Exception(f'Mode [{config}] is not supported!')

    def laser(self):
        return self.mode == self.LASER
    def source(self):
        return self.mode == self.SOURCE

    def __str__(self):
        return f'Mode [{self.mode}]'
