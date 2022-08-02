import lecroyparser
import time

import numpy as np

from ..Lecroy import WaveRunner8104

class ScopeControl():

    def WaveToMetadata(self, wave):

        metadata = {
            'instrument': wave.instrumentName,
            'instrumentNumber': wave.instrumentNumber,
            'waveArrayCount': wave.waveArrayCount,
            'verticalGain': wave.verticalGain,
            'verticalOffset': wave.verticalOffset,
            'nominalBits': wave.nominalBits,
            'horizInterval': wave.horizInterval,
            'horizOffset': wave.horizOffset,
            'triggerTime': wave.triggerTime,
            'recordType': wave.recordType,
            'processingDone': wave.processingDone,
            'timeBase': wave.timeBase,
            'verticalCoupling': wave.verticalCoupling,
            'bandwidthLimit': wave.bandwidthLimit,
            'waveSource': wave.waveSource,
        }

        return metadata

    def __init__(self, setup=True, log=None):
        self.scope = WaveRunner8104("10.10.0.11", log=log)
        self._log = log

        self.CH = WaveRunner8104.CHANNEL.C2

        self.scope.COMMHeader(on=False)
        self.scope.COMMFormat(['off', 'byte', 'bin'])

        # TODO do check and setup if necessary

    def __del__(self):
        self.scope = None

    def log(self, cat, msg):
        if self._log is not None:
            self._log.log(cat, msg)

    def check(self):
        # TODO Implement
        # - Check CH2 active
        # - Check CH2 DC-50Ohm
        # - Check CH2 No BW limit
        # - Check Acquisition at 20GSps
        # - Check Trigger Ext
        # - Check Trigger Edge Pos @ -500mV

        pass

    def ToState(self, state={}):
        # TODO properly implement

        # TODO this should call a higher order function in ScopeControl
        state['scope.average'] = self.scope.GetAverage(self.CH)

        # TODO implement
        # state['scope.time'] = self.GetHorRange()

        state['scope.amplitude'] = self.GetVertRange()

        return state

    def FromState(self, state):
        if 'scope.average' in state:
            self.SetAverage(state['scope.average'])

        if 'scope.amplitude' in state:
            range = state['scope.amplitude']
            try:
                self.SetVertRange(( float(range[0]), float(range[1]) ))
            except (TypeError, ValueError) as e:
                self.log('ERROR', f'`scope.amplitude` is not properly structured: [{range}]!')

        if 'scope.time' in state:
            # TODO implement
            pass

    def Reset(self):
        # TODO
        pass

    def _setupTrigger(self):
        # TODO
        pass

    def SetAverage(self, navg):
        if self.scope.GetAverage(self.CH) != navg and navg > 0:
            self.log('Scope', f'Set Average to [{navg}].')
            self.scope.Average(self.CH, navg)

    # TODO Implement auto scale of Y-Axis

    def _readWaveform(self):
        # The data sent by the scope (in binary) mode, is equivalent to a .trc file.
        # Use LecroParser for interpreting the byte-stream.
        # The TEMPLATE of the sent data packate can be retrieved via the `TMPL?` command.
        # See also Page 6-22 here: https://cdn.teledynelecroy.com/files/manuals/maui-remote-control-and-automation-manual.pdf
        raw = self.scope.Waveform(self.CH)
        return lecroyparser.ScopeData(data=raw)


    def GetVertRange(self):
        scale = self.scope.GetVerScale(self.CH)
        offset = self.scope.GetVerOffset(self.CH)

        return (-0.5*self.scope.N_DIV*scale - offset, 0.5*self.scope.N_DIV*scale - offset)

    def SetVertRange(self, range):
        self.log('Scope', f'Require vertical range of {range}.')

        scale = self.scope.SCALE.find((range[1]-range[0])/self.scope.N_DIV)
        offset = -1*(range[1]+range[0])/2

        self.log('Scope', f'Set vertical axis to {scale} V/div + {offset} V.')
        self.scope.VerScale(self.CH, scale)
        self.scope.VerOffset(self.CH, offset)


    def AutoScale(self):
        self.log('Scope', 'Auto find vertical scale.')

        ## Alternative (slower) implementation via the built in FindScale function
        # num_average = self.scope.GetAverage(self.CH)
        # self.scope.Average(self.CH, 1)
        # self.scope.ClearSweeps(self.CH)
        # self.scope.WaitUntilIdle(1)
        #
        # self.scope.FindScale(self.CH)
        # self.scope.WaitUntilIdle(1)
        #
        # self.scope.Average(self.CH, num_average)
        

        # Set initial scale: -2.5V / 2.5V
        # This should fit any TCT signal, as the amplifier limits before that.
        self.scope.VerOffset(self.CH, 0)
        self.scope.VerScale(self.CH, 0.5)

        # Get a single (non averaged trigger)
        num_average = self.scope.GetAverage(self.CH)
        self.scope.TriggerMode(WaveRunner8104.TRIGGER_MODE.STOP)
        self.scope.Average(self.CH, 1)
        self.scope.ClearSweeps(self.CH)
        self.scope.WaitUntilIdle(1)

        while True:
            if self.scope.Acquire(10):
                break

        # Set range based on acquired waveform
        wave = self._readWaveform()
        range = (np.min(wave.y)*1.5, np.max(wave.y)*1.5)

        self.SetVertRange(range)

        self.scope.Average(self.CH, num_average)
        self.scope.TriggerMode(WaveRunner8104.TRIGGER_MODE.NORMAL)

    def AcquireAverage(self):
        # Clear the previous sweeps
        self.scope.TriggerMode(WaveRunner8104.TRIGGER_MODE.STOP)
        self.scope.ClearSweeps(self.CH)
        self.scope.WaitUntilIdle(1)

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
