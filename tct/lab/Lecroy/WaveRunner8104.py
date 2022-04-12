import vxi11

from ..generic import InterfaceVXI11

class WaveRunner8104(InterfaceVXI11):

    class FUNCTION:
        all = ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8']
        F1 = 'f1'
        F2 = 'f2'
        F3 = 'f3'
        F4 = 'f4'
        F5 = 'f5'
        F6 = 'f6'
        F7 = 'f7'
        F8 = 'f8'

    class MEASURE:
        all = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8']
        M1 = 'p1'
        M2 = 'p2'
        M3 = 'p3'
        M4 = 'p4'
        M5 = 'p5'
        M6 = 'p6'
        M7 = 'p7'
        M8 = 'p8'

    class CHANNEL:
        all = ['C1', 'C2', 'C3', 'C4']
        C1 = 'C1'
        C2 = 'C2'
        C3 = 'C3'
        C4 = 'C4'

    class TRIGGER_MODE:
        STOP = 'stopped'
        NORMAL = 'normal'
        SINGLE = 'single'
        AUTO = 'auto'

    def __init__(self, ip, log):
        super().__init__(ip, log=log)

    def _vbsCMD(self, cmd):
        self.query(r"""vbs '%s' """%(cmd))
    def _vbsQuery(self, cmd):
        return self.query(r"""vbs? 'return=%s' """%(cmd), resp=True)

    def reset(self):
        return self.query("*RST")

    def COMMHeader(self, on=True):
        return self.query("COMM_HEADER %s"%("ON" if on else "OFF"))
    def COMMFormat(self, flags):
        return self.query("COMM_FORMAT %s"%(','.join(flags)))

    def Waveform(self, channel):
        data = self.query(f'{channel}:WF? WF', resp=True, raw=True)
        if data[0:2] != b'WF':
            self.log.error(f'Header of [WF?] command is not correct. Expected [WF] - Received [{data[0:2]}]')
            return None

        return data[3:]


    def MeasureValue(self, msr):
        if msr not in self.MEASURE.values():
            return None

        return float(self._vbsQuery('app.measure.%s.out.result.value'%(msr)))


    ## Channel Setup
    def Average(self, channel, num):
        if num < 1:
            return False
        return self._vbsCMD(f'app.Acquisition.{channel}.AverageSweeps = {int(num)}')


    def GetAverage(self, channel):
        return int(self._vbsQuery(f'app.Acquisition.{channel}.AverageSweeps'))


    ## Handle channel sweeps
    def ClearSweeps(self, channel):
        return self._vbsCMD(f'app.Acquisition.{channel}.ClearSweeps')

    def GetSweeps(self, channel):
        return int(self._vbsQuery(f'app.Acquisition.{channel}.Out.Result.Sweeps'))


    ## Handle Trigger
    def WaitUntilIdle(self, timeout):
        return bool(self._vbsQuery(f'app.WaitUntilIdle({timeout})'))

    def Acquire(self, timeout):
        try:
            return bool(self._vbsQuery(f'app.Acquisition.Acquire({timeout}, false)'))
        except vxi11.vxi11.Vxi11Exception as e:
            return False

    def TriggerMode(self, mode):
        return self._vbsCMD(f'app.Acquisition.triggermode = "{mode}"')
