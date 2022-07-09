from ..generic import InterfaceIP

class PiController(InterfaceIP):

    def __init__(self, ip, port, log):
        super().__init__(ip, port, log=log)

    def stageTemperature(self):
        return float(self.query("STAGE:TEMP?", resp=True))

    def holderTemperature(self):
        return float(self.query("HOLDER:TEMP?", resp=True))
    def holderHumidity(self):
        return float(self.query("HOLDER:HUMIDITY?", resp=True))
