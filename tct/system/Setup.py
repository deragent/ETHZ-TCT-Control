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

    def ToState(self, state={}):
        self.stage.ToState(state)
        self.laser.ToState(state)
        self.amp.ToState(state)
        self.bias.ToState(state)

        # TODO handle scope
        return state

    def FromState(self, state):
        self.stage.FromState(state)
        self.laser.FromState(state)
        self.amp.FromState(state)
        self.bias.FromState(state)

        # TODO handle scope

    def Off(self):
        self.laser.LaserOff()
        self.bias.SMUOff()
        self.amp.AmpOff()
