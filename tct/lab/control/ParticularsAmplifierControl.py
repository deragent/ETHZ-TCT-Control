from ..TTi import PLH250P

import numpy as np

class ParticularsAmplifierControl():

    Amp_Current = 0.250
    Amp_Limit = 15

    # Amplifier behaviour from http://www.particulars.si/downloads/ParticularsAmps-Manuals.pdf
    ## Page 3 - AM-02A 53db - Gain
    ## Extracted with https://apps.automeris.io/wpd/

    ## Polynom: Relative Gain = Pol[0] + Pol[1]*V + Pol[2]*V² + Pol[3]*V³
    Gain_Pol = [-7.277, 2.123, -0.181, 0.005]

    Gain_Points = np.array([
        # Voltage,              Relative Gain
        [5.930294906166219,     0.],
        [6.1876675603217155,    0.14888178913738015],
        [7.10455764075067,      0.5105431309904154],
        [7.8083109919571045,    0.6958466453674121],
        [9.151474530831099,     0.9437699680511182],
        [10.595174262734584,    0.9853035143769969],
        [12.002680965147452,    1.],
    ])

    def __init__(self, ip="10.10.0.10", port=9221, log=None):
        self.plh = PLH250P(ip, port, log=log)
        self._log = log

        if not self.check():
            self.setup()

    def __del__(self):
        self.plh = None

    def log(self, cat, msg):
        if self._log is not None:
            self._log.log(cat, msg)

    def check(self):
        """Check the state of the Power supply

        Mainly:
            - Current Range
            - HV Current
        """

        if self.plh.currentRangeLow():
            self.log("Amp-PSU", "Amp current range is not correct!")
            return False

        if self.plh.current() != ParticularsAmplifierControl.Amp_Current:
            self.log("Amp-PSU", "Amplifier current limit is not correct!")
            return False

        if self.plh.voltage() > ParticularsAmplifierControl.Amp_Limit:
            self.log("Amp-PSU", "Amplifier voltage is too high!")
            return False


        self.log("Amp-PSU", "Amp-PSU state is OK!")
        return True


    def setup(self):
        self.plh.off()

        self.plh.setCurrentRangeLow(low = False)
        self.plh.setVoltage(0)
        self.plh.setCurrent(ParticularsAmplifierControl.Amp_Current)
        self.log("Amp-PSU", f"Configured PSU: (0V - {ParticularsAmplifierControl.Amp_Current:.3f}A - High Range)")

    def ToState(self, state={}):
        state['amp.gain'] = self.AmpGet()
        state['amp.state'] = self.AmpState()

        state['amp.voltage'] = self.AmpVoltage()
        state['amp.current'] = self.AmpCurrent()

        return state

    def FromState(self, state):
        if 'amp.gain' in state:
            self.AmpSet(float(state['amp.gain']))
        if 'amp.state' in state:
            if state['amp.state']:
                self.AmpOn()
            else:
                self.AmpOff()


    ## Control the HV
    def AmpSet(self, percentage):
        if percentage > 100 or percentage < 0:
            self.log("Amp-PSU", f"Error: Set percentage [{percentage:.1f}%] out of range [0%, 100%]")
            return False

        voltage = np.interp(percentage/100, ParticularsAmplifierControl.Gain_Points[:, 1], ParticularsAmplifierControl.Gain_Points[:, 0])

        self.AmpSetVoltage(voltage)

    def AmpSetVoltage(self, voltage):
        if voltage > ParticularsAmplifierControl.Amp_Limit or voltage < 0:
            self.log("Amp-PSU", f"Error: Set voltage [{voltage:.2f}V] out of range [0V, 15V]")
            return False

        self.plh.setVoltage(voltage)
        self.log("Amp-PSU", "Set amplifier supply to %fV"%(voltage))

    def AmpOn(self):
        self.plh.on()
        self.log("Amp-PSU", "Turn amplifier on")

    def AmpOff(self):
        self.plh.off()
        self.log("Amp-PSU", "Turn amplifier off")

    def AmpState(self):
        return self.plh.state()

    def AmpVoltage(self):
        return self.plh.voltage()


    def AmpGet(self):
        voltage = self.AmpVoltage()

        gain = 100*np.interp(voltage, ParticularsAmplifierControl.Gain_Points[:, 0], ParticularsAmplifierControl.Gain_Points[:, 1])
        return gain

    ## Measure currents
    def AmpCurrent(self):
        return self.plh.measureCurrent()
