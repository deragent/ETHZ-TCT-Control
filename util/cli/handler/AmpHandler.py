from .CommandHandler import CommandHandler

from tct.lab.control import ParticularsAmplifierControl

class AmpHandler(CommandHandler):

    def __init__(self, log):
        super().__init__(log)

        self._amp = ParticularsAmplifierControl(log=log)

    def commandDict(self):
        return {
            'on': None,
            'off': None,
            'gain': None,
            'state': None,
        }

    def handle(self, input):
        if input[0] in ['on']:
            self._amp.AmpOn()
        elif input[0] in ['off']:
            self._amp.AmpOff()
        elif input[0] in ['state']:
            return self.Value(self._amp.AmpState())
        elif input[0] in ['gain']:
            if len(input) < 2:
                return self.Value(f'{self._amp.AmpGet():.2f} %')
            else:
                self._amp.AmpSet(float(input[1]))

    def on(self):
        self._amp.AmpOn()

    def off(self):
        self._amp.AmpOff()
