from ..generic import InterfaceSerial

class SMU2410(InterfaceSerial):

    # Designed for following serial config:
    ## Baud: 9600
    ## Bits: 8
    ## Stop: 1
    ## Parity: None
    ## Terminator: Line-Feed (\n)

    RANGE = {
        'VOLTAGE': {
            '210mV': 0.21,
            '2.2V': 2.1,
            '21V': 21,
            '1100V': 1100,
        },
        'CURRENT': {
            '1.05uA': 0.00000105,
            '10.5uA': 0.0000105,
            '105uA': 0.000105,
            '1.05mA': 0.00105,
            '21mA': 0.021,
            '105mA': 0.105,
            '1.05A': 1.05,
        }
    }
    COMPL = {
        'VOLTAGE': {
            '210mV': 0.21,
            '2.2V': 2.1,
            '21V': 21,
            '1100V': 1100,
        },
        'CURRENT': {
            '1.05uA': 0.00000105,
            '10.5uA': 0.0000105,
            '105uA': 0.000105,
            '1.05mA': 0.00105,
            '21mA': 0.021,
            '105mA': 0.105,
            '1.05A': 1.05,
        }
    }

    class SOURCE_MODE:
        VOLTAGE = "VOLT"
        CURRENT = "CURR"
        MEMORY = "MEM"
        FIXED = "FIX"
        LIST = "LIST"
        SWEEP = "SWE"


    def __init__(self, port, log, baudrate=9600):
        super().__init__(port, baudrate, log=log)
        self.clearConnection()

    def clearConnection(self):
        # See 'RS-323 interface operation' in SMU-2400 user manual
        resp = self.query('\x03', resp=True)
        if not resp.startswith('DCL'):
            raise InterfaceSerial.CommError(self, 'Expected reponse [DCL] for connection reset!', 'DCL [0x03]', resp)

    def abort(self):
        return self.query("ABORT")

    def on(self):
        return self.query("OUTPUT1:STATE 1")
    def off(self):
        return self.query("OUTPUT1:STATE 0")

    def init(self):
        return self.query("INIT")

    def setArmCount(self, count=1, inf=False):
        if inf:
            return self.query("ARM:COUNT INF")
        else:
            return self.query("ARM:COUNT %i"%(count))

    def state(self):
        state = self.query("OUTPUT1:STATE?", resp=True)
        return state == "1"


    def setVoltage(self, voltage):
        return self.query("SOURCE1:VOLTAGE:AMPLITUDE %f"%(voltage))
    def setCurrent(self, current):
        return self.query("SOURCE1:CURRENT:AMPLITUDE %f"%(current))

    def voltage(self):
        resp = self.query("SOURCE1:VOLTAGE:AMPLITUDE?", resp=True)
        return float(resp)

    def current(self):
        resp = self.query("SOURCE1:CURRENT:AMPLITUDE?", resp=True)
        return float(resp)

    def readCurrent(self):
        resp = self.query("SENSE1:DATA:LATEST?", resp=True).split(',')
        return float(resp[1])



    def setVoltageSourceRange(self, magnitude=20, auto=None):
        if auto is not None:
            return self.query("SOURCE1:VOLTAGE:RANGE:AUTO %i"%(1 if auto else 0))
        else:
            return self.query("SOURCE1:VOLTAGE:RANGE %f"%(magnitude))

    def setCurrentSourceRange(self, magnitude=0.0001, auto=None):
        if auto is not None:
            return self.query("SOURCE1:CURRENT:RANGE:AUTO %i"%(1 if auto else 0))
        else:
            return self.query("SOURCE1:CURRENT:RANGE %f"%(magnitude))

    def voltageSourceRangeAuto(self):
        resp = self.query("SOURCE1:VOLTAGE:RANGE:AUTO?", resp=True)
        return resp == '1'
    def voltageSourceRange(self):
        if self.voltageSourceRangeAuto():
            return None
        resp = self.query("SOURCE1:VOLTAGE:RANGE?", resp=True)
        return float(resp)

    def currentSourceRangeAuto(self):
        resp = self.query("SOURCE1:CURRENT:RANGE:AUTO?", resp=True)
        return resp == '1'
    def currentSourceRange(self):
        if self.voltageSourceRangeAuto():
            return None
        resp = self.query("SOURCE1:CURRENT:RANGE?", resp=True)
        return float(resp)


    def setCurrentSenseRange(self, range=0.0001, auto=None):
        if auto is not None:
            return self.query("SENSE1:CURRENT:RANGE:AUTO %i"%(1 if auto else 0))
        else:
            return self.query("SENSE1:CURRENT:RANGE %f"%(range))
    def setVoltageSenseRange(self, range=20, auto=None):
        if auto is not None:
            return self.query("SENSE1:VOLTAGE:RANGE:AUTO %i"%(1 if auto else 0))
        else:
            return self.query("SENSE1:VOLTAGE:RANGE %f"%(range))

    def voltageSenseRangeAuto(self):
        resp = self.query("SENSE1:VOLTAGE:RANGE:AUTO?", resp=True)
        return resp == '1'
    def voltageSenseRange(self):
        if self.voltageSourceRangeAuto():
            return None
        resp = self.query("SENSE1:VOLTAGE:RANGE?", resp=True)
        return float(resp)

    def currentSenseRangeAuto(self):
        resp = self.query("SENSE1:CURRENT:RANGE:AUTO?", resp=True)
        return resp == '1'
    def currentSenseRange(self):
        if self.voltageSourceRangeAuto():
            return None
        resp = self.query("SENSE1:CURRENT:RANGE?", resp=True)
        return float(resp)


    def setCurrentProtection(self, range):
        return self.query("SENSE1:CURRENT:PROTECTION %f"%(range))
    def setVoltageProtection(self, range):
        return self.query("SENSE1:VOLTAGE:PROTECTION %f"%(range))

    def currentProtection(self):
        return float(self.query("SENSE1:CURRENT:PROTECTION?", resp=True))
    def voltageProtection(self):
        return float(self.query("SENSE1:VOLTAGE:PROTECTION?", resp=True))


    def enableVoltageSense(self, on=True):
        return self.query("SENSE1:FUNC:%s \"VOLTAGE\""%("ON" if on else "OFF"))
    def enableCurrentSense(self, on=True):
        return self.query("SENSE1:FUNC:%s \"CURRENT\""%("ON" if on else "OFF"))

    def voltageSense(self):
        return self.query("SENS1:FUNC:STATE? \"VOLTAGE\"", resp=True) == "1"
    def currentSense(self):
        return self.query("SENS1:FUNC:STATE? \"CURRENT\"", resp=True) == "1"

    def setSourceMode(self, mode):
        if mode.upper() in ["VOLTAGE", "CURRENT", "MEMORY", "VOLT", "CURR", "MEM"]:
            return self.query("SOURCE1:FUNCTION:MODE %s"%(mode))
        else:
            return False
    def setSourceVoltageMode(self, mode):
        if mode.upper() in ["FIXED", "LIST", "SWEEP", "FIX", "SWE"]:
            return self.query("SOURCE1:VOLTAGE:MODE %s"%(mode))
        else:
            return False

    def sourceMode(self):
        return self.query("SOURCE1:FUNCTION:MODE?", resp=True)
    def sourceVoltageMode(self):
        return self.query("SOURCE1:VOLTAGE:MODE?", resp=True)
