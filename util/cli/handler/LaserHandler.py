from .CommandHandler import CommandHandler

from tct.lab.control import ParticularsLaserControl

class LaserHandler(CommandHandler):

    def __init__(self, log):
        super().__init__(log)

        self._laser = ParticularsLaserControl(log=log)

    def commandDict(self):
        return {
            'on': None,
            'off': None,
            'dac': None,
            'frequency': None,
            'state': None,
        }

    def handle(self, input):
        if input[0] in ['on']:
            self._laser.LaserOn()
        elif input[0] in ['off']:
            self._laser.LaserOff()
        elif input[0] in ['state']:
            return self.Value(self._laser.LaserState())
        elif input[0] in ['dac']:
            if len(input) < 2:
                dac = self._laser.LaserGetDAC()
                if dac is not None:
                    return self.Value(f'= {dac}')
                else:
                    return self.NA()
            else:
                self._laser.LaserSetDAC(int(input[1]))
        elif input[0] in ['frequency', 'freq']:
            if len(input) < 2:
                freq = self._laser.LaserGetFrequency()
                if freq is not None:
                    return self.Value(f'{freq/1000:.2f} kHz')
                else:
                    return self.NA()
            else:
                self._laser.LaserSetFrequency(int(float(input[1])))

    def on(self):
        if self._laser.LaserGetFrequency() is None:
            self._laser.LaserSetFrequency(50e3)
        if self._laser.LaserGetDAC() is None:
            self._laser.LaserSetDAC(290)
        self._laser.LaserOn()

    def off(self):
        self._laser.LaserOff()
