from datetime import datetime
import os
import sys
import socket
import git

from tct.lab.control import *
from tct.logger import Logger

class Setup():

    def __init__(self, vlimit, ilimit, log=None, use_laser=True):

        if log is None:
            self.log = Logger(print=True, debug=False)
        else:
            self.log = log

        # Computer and script metadata
        self._system = {}
        self._system['setup.hostname'] = socket.gethostname()
        self._system['setup.user'] = os.getlogin()
        self._system['code.script'] = os.path.basename(sys.argv[0])

        repo = git.Repo(search_parent_directories=True)
        if repo:
            self._system['code.git.hash'] = repo.head.object.hexsha
            self._system['code.git.branch'] = repo.active_branch.name
            self._system['code.git.dirty'] = repo.is_dirty()
        else:
            self._system['code.git.hash'] = None
            self._system['code.git.branch'] = None
            self._system['code.git.dirty'] = None

        # Container for manual states
        self._manual = {}

        # Dummy state to allow for repetition of scans
        self.count = 0

        # Create the setup control classes
        self.stage = StageControl(log = self.log)
        if use_laser:
            self.laser = ParticularsLaserControl(log = self.log)
        else:
            self.laser = None
        self.amp = ParticularsAmplifierControl(log = self.log)
        self.bias = BiasSupplyControl(VLimit = vlimit, ILimit = ilimit, log = self.log)
        self.scope = ScopeControl(log = self.log)
        self.temp = TemperatureControl(log = self.log)

    def ToState(self, state={}):
        state['time'] = datetime.now().isoformat()
        state['count'] = self.count

        self.scope.ToState(state)
        self.stage.ToState(state)
        if self.laser is not None:
            self.laser.ToState(state)
        self.amp.ToState(state)
        self.bias.ToState(state)
        self.temp.ToState(state)

        state.update(self._manual)
        state.update(self._system)

        return state

    def FromState(self, state):
        self.scope.FromState(state)
        self.stage.FromState(state)
        if self.laser is not None:
            self.laser.FromState(state)
        self.amp.FromState(state)
        self.bias.FromState(state)
        self.temp.FromState(state)

        if 'count' in state:
            self.count = int(state['count'])

        for key, value in state.items():
            if key.startswith('manual-'):
                self._manual[key] = value

    def Off(self):
        if self.laser is not None:
            self.laser.LaserOff()
        self.bias.SMUOff()
        self.amp.AmpOff()
