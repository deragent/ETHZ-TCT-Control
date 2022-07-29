from ..Temperature import PiController

class TemperatureControl():

    def __init__(self, ip="10.10.0.20", port=5025, log=None):
        self.pi = PiController(ip, port, log=log)
        self._log = log

        # For now just temperature readout, so no checking necessary.

    def __del__(self):
        self.pi = None

    def log(self, cat, msg):
        if self._log is not None:
            self._log.log(cat, msg)

    def setup(self):
        pass

    def ToState(self, state={}):
        state['temp.stage.temperature'] = self.StageTemperature()
        state['temp.holder.temperature'] = self.HolderTemperature()
        state['temp.holder.humidity'] = self.HolderHumiditiy()

        return state

    def FromState(self, state):
        pass


    def StageTemperature(self):
        return self.pi.stageTemperature()

    def HolderTemperature(self):
        return self.pi.holderTemperature()
    def HolderHumidity(self):
        return self.pi.holderHumidity()
