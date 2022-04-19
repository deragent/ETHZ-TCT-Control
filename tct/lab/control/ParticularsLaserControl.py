from ..Particulars import LaserLA01

class ParticularsLaserControl():

    def __init__(self, frequency=None, dac=None, log=None):
        self.laser = LaserLA01(log=log)
        self._log = log

        # We can not check for correct settings as the laser does not give feedback.
        # Always setup to defaults
        self.setup(frequency, dac)

    def __del__(self):
        self.laser = None

    def log(self, cat, msg):
        if self._log is not None:
            self._log.log(cat, msg)

    def setup(self, frequency, dac):
        if dac is not None:
            if dac < 0 or dac >= 1024:
                dac = 300
            self.laser.setDAC(dac)

            self.log("Laser", f"Configured the laser DAC to {int(dac)}.")

        if frequency is not None:
            if frequency < 50 or frequency > 100e3:
                frequency = 1000

            self.laser.setFrequency(frequency)

            self.log("Laser", f"Configured the laser frequency to {frequency/1000:0.0f}kHz.")

    def ToState(self, state={}):
        state['laser.frequency'] = self.LaserGetFrequency()
        state['laser.dac'] = self.LaserGetDAC()
        state['laser.state'] = self.LaserState()

        return state

    def FromState(self, state):
        if 'laser.frequency' in state:
            self.LaserSetFrequency(float(state['laser.frequency']))
        if 'laser.dac' in state:
            self.LaserSetDAC(int(state['laser.dac']))
        if 'laser.state' in state:
            if state['laser.state']:
                self.LaserOn()
            else:
                self.LaserOff()


    def LaserOn(self):
        if self.laser.on():
            self.log("Laser", f"Turned the laser on.")
        else:
            self.log("Laser", f"WARNING: Laser could not be turned on!")

    def LaserOff(self):
        self.laser.off()
        self.log("Laser", f"Turned the laser off.")

    def LaserState(self):
        return self.laser.state()


    def LaserSetFrequency(self, frequency):
        if frequency < 50 or frequency > 100e3:
            self.log("Laser", f"Error: Frequency [{frequency/1000:0.0f}kHz] not in [50 Hz, 100kHz]!")
            return False

        self.laser.setFrequency(frequency)
        if self.laser.state():
            self.laser.on()

        self.log("Laser", f"Set the laser frequency to {frequency/1000:0.0f}kHz.")


    def LaserSetDAC(self, dac):
        if dac < 0 or dac >= 1024:
            self.log("Laser", f"Error: DAC [{int(dac)}] not in [0, 1024[!")
            return False

        state = self.laser.state()

        self.laser.off()
        self.laser.enableDAC()
        self.laser.setDAC(int(dac))

        if state:
            self.laser.on()

        self.log("Laser", f"Set the laser DAC to {int(dac)}.")

    def LaserGetFrequency(self):
        return self.laser.frequency()

    def LaserGetDAC(self):
        return self.laser.DAC()
