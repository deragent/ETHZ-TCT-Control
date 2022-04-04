from ..generic import InterfaceIP


class PLH250P(InterfaceIP):

    def __init__(self, ip, port, log):
        super().__init__(ip, port, log=log)

    def on(self):
        return self.query("OP1 1")
    def off(self):
        return self.query("OP1 0")

    def state(self):
        state = self.query("OP1?", resp=True)
        return state == "1"

    def setVoltage(self, voltage):
        return self.query("V1 %f"%voltage)
    def setCurrent(self, current):
        return self.query("I1 %f"%current)

    def voltage(self):
        return float(self.query("V1?", resp=True)[3:])
    def current(self):
        return float(self.query("I1?", resp=True)[3:])

    def measureVoltage(self):
        return float(self.query("V1O?", resp=True).strip("V"))
    def measureCurrent(self):
        return float(self.query("I1O?", resp=True).strip("A"))

    def setCurrentRangeLow(self, low = True):
        return self.query("IRANGE1 %i"%(1 if low else 2))

    def currentRangeLow(self):
        # 1 is for Low Range (up to 0.05A)
        # 2 is for High Range
        return self.query("IRANGE1?", resp=True) == "1"
