import lecroyparser
import time

from ..Lecroy import WaveRunner8104

class ScopeControl():

    def __init__(self, setup=True, log=None):
        self.scope = WaveRunner8104("10.10.0.11", log=log)
        self._log = log

        self.CH = WaveRunner8104.CHANNEL.C2

        self.scope.COMMHeader(on=False)
        self.scope.COMMFormat(['off', 'byte', 'bin'])

    def __del__(self):
        self.scope = None

    def log(self, cat, msg):
        if self._log is not None:
            self._log.log(cat, msg)

    def Reset(self):
        # TODO
        pass

    def _setupTrigger(self):
        # TODO
        pass

    def SetupSingle(self):
        # TODO
        pass

    def SetupAverage(self):
        # TODO
        pass

    # TODO Implement auto scale of Y-Axis

    def _readWaveform(self):
        # The data sent by the scope (in binary) mode, is equivalent to a .trc file.
        # Use LecroParser for interpreting the byte-stream.
        # The TEMPLATE of the sent data packate can be retrieved via the `TMPL?` command.
        # See also Page 6-22 here: https://cdn.teledynelecroy.com/files/manuals/maui-remote-control-and-automation-manual.pdf
        raw = self.scope.Waveform(self.CH)
        return lecroyparser.ScopeData(data=raw)


    def AcquireAverage(self):
        num_average = self.scope.GetAverage(self.CH)

        self.log('Scope', 'Waiting for initial trigger.')
        while True:
            if self.scope.Acquire(10):
                break
            self.log('Scope', 'Still waiting for a trigger.')

        self.scope.TriggerMode(WaveRunner8104.TRIGGER_MODE.NORMAL)

        self.log('Scope', f'Waiting for {num_average} sweeps.')

        while 1:
            sweeps = self.scope.GetSweeps(self.CH)
            if sweeps >= num_average:
                break
            time.sleep(0.01)

        return self._readWaveform()

    def Acquire(self):
        self.log('Scope', 'Waiting for a trigger.')
        while True:
            if self.scope.Acquire(10):
                break
            self.log('Scope', 'Still waiting for a trigger.')

        return self._readWaveform()
