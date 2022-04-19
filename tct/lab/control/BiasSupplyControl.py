from ..Keithley import SMU2410

import time
import numpy as np

class BiasSupplyControl():

    VOLTAGE_RAMP = 20 # V / s

    def __init__(self, port='/dev/ttyUSB0', log=None, VLimit=1000, ILimit=0.02):
        self.smu = SMU2410(port, log=log)
        self._log = log

        self.voltage_limit = VLimit

        # Determine voltage range corresponding to given voltage limit
        for key, value in SMU2410.RANGE['VOLTAGE'].items():
            if value >= np.abs(VLimit):
                self.voltage_range = value
                break


        self.current_limit = ILimit

        # Determine current sense range corresponding to given current limit
        for key, value in SMU2410.RANGE['CURRENT'].items():
            if value >= np.abs(ILimit):
                self.current_range = value
                break

        if not self.check():
            self.setup()

    def __del__(self):
        self.smu = None

    def log(self, cat, msg):
        if self._log is not None:
            self._log.log(cat, msg)

    def check(self):
        """Check the state of the SMU

        Mainly:
            - Supply Mode
            - Voltage Supply Range
            - Voltage Supply Current Compliance
            - Current Sense Range
            - Sense Mode
        """

        if self.smu.sourceMode() != SMU2410.SOURCE_MODE.VOLTAGE:
            self.log("Bias-SMU", "Source mode is not correct!")
            return False
        if self.smu.sourceVoltageMode() != SMU2410.SOURCE_MODE.FIXED:
            self.log("Bias-SMU", "Source voltage mode is not correct!")
            return False

        if self.smu.currentProtection() != self.current_limit:
            self.log("Bias-SMU", "Current compliance is not correct!")
            return False

        if self.smu.voltageSourceRange() != self.voltage_range:
            self.log("Bias-SMU", "Voltage source range is not correct!")
            return False

        if self.smu.currentSenseRange() != self.current_range:
            self.log("Bias-SMU", "Current sense range is not correct!")
            return False

        if not self.smu.currentSense():
            self.log("Bias-SMU", "SMU is not in current sense mode!")
            return False


        self.log("Bias-SMU", "Bias-SMU state is OK!")
        return True


    def setup(self):
        self.SMUOff()
        self.smu.setVoltage(0)

        self.smu.setSourceMode(SMU2410.SOURCE_MODE.VOLTAGE)
        self.smu.setSourceVoltageMode(SMU2410.SOURCE_MODE.FIXED)

        self.smu.setCurrentProtection(self.current_limit)
        self.smu.setVoltageSourceRange(self.voltage_range)

        self.smu.setCurrentSenseRange(self.current_range)

        self.smu.enableCurrentSense()

        self.log("Bias-SMU", f"Configured SMU: ({self.voltage_range} Voltage Range -- {self.current_limit} Current Compliance)")

    # Control the Bias HV
    # Implement ramp up and ramp down
    def SMURampVoltage(self, voltage):
        if not (min(0, self.voltage_limit) <= voltage <= max(0, self.voltage_limit)):
            self.log("Bias-SMU", f"Error: Set voltage [{voltage:.2f}V] out of range [0V, {self.voltage_limit:.2f}V]")
            return False

        if not self.smu.state():
            if voltage != self.smu.voltage():
                self.smu.setVoltage(voltage)
                self.log("Bias-SMU", "Set voltage to %fV"%(voltage))

        else:
            current = self.smu.voltage()

            if voltage != current:
                prev = time.time()
                self.log("Bias-SMU", "Start bias ramp at %fV"%(current))

                while current != voltage:
                    time.sleep(0.2)

                    delta = (time.time() - prev)*BiasSupplyControl.VOLTAGE_RAMP*np.sign(voltage - current)
                    prev = time.time()

                    if (current + delta) <= voltage and voltage <= current:
                        current = voltage
                    elif (current + delta) >= voltage and voltage >= current:
                        current = voltage
                    else:
                        current = current + delta

                    self.smu.setVoltage(current)

                self.log("Bias-SMU", "Ramp bias to %fV"%(voltage))

        return True

    def SMUOn(self):
        if not self.smu.state():
            voltage = self.smu.voltage()
            self.smu.setVoltage(0)

            self.smu.on()
            self.log("Bias-SMU", "Turn SMU on")

            # Ramp voltage up to set value
            return self.SMURampVoltage(voltage)

        return True

    def SMUOff(self):
        # Ramp voltage down to 0
        if self.smu.state():
            self.SMURampVoltage(0)

            self.smu.off()
            self.log("Bias-SMU", "Turn SMU off")

        return True

    def SMUState(self):
        return self.smu.state()

    def SMUVoltage(self):
        return self.smu.voltage()

    def SMUCurrent(self):
        if not self.smu.state():
            return None


        # Trigger one current measurement
        self.smu.setArmCount(1)
        self.smu.init()

        return self.smu.readCurrent()
