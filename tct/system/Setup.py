from tct.lab.control import *
from tct.logger import Logger

class Setup():

    def __init__(self, vlimit, ilimit, log=None):

        if log is None:
            self.log = Logger(print=True, debug=False)
        else:
            self.log = log

        self.stage = StageControl(log = self.log)
        self.laser = ParticularsLaserControl(log = self.log)
        self.amp = ParticularsAmplifierControl(log = self.log)
        self.bias = BiasSupplyControl(VLimit = vlimit, ILimit = ilimit, log = self.log)
        self.scope = ScopeControl(log = self.log)

    def ToState(self):
        pass # TODO

    def FromState(self):
        pass # TODO

    def Off(self):
        self.laser.LaserOff()
        self.bias.SMUOff()
        self.amp.AmpOff()
