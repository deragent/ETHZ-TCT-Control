from .CommandHandler import CommandHandler

from tct.lab.control import BiasSupplyControl

class BiasHandler(CommandHandler):

    def __init__(self, VLimit, ILimit, log):
        super().__init__(log)

        self._bias = BiasSupplyControl(VLimit=VLimit, ILimit=ILimit, log=log)

    def commandDict(self):
        return  {
            'on': None,
            'off': None,
            'voltage': None,
            'current': None,
            'state': None,
        }

    def handle(self, input):
        if input[0] in ['on']:
            self._bias.SMUOn()
        elif input[0] in ['off']:
            self._bias.SMUOff()
        elif input[0] in ['state']:
            return self.Value(self._bias.SMUState())
        elif input[0] in ['current', 'curr', 'cur', 'c']:
            current = self._bias.SMUCurrent()
            if current is not None:
                return self.Value(f'{current*1e6:.3f} uA')
            else:
                return self.NA()
        elif input[0] in ['voltage', 'volt', 'v']:
            if len(input) < 2:
                return self.Value(f'{self._bias.SMUVoltage():.3f} V')
            else:
                self._bias.SMURampVoltage(float(input[1]))

    def on(self):
        self._bias.SMUOn()

    def off(self):
        self._bias.SMUOff()
