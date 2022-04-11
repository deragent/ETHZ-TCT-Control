from ..generic import InterfaceHIDParticulars

# This implementation is based and partially copied from the work done by Matías Senger at UZH
# https://github.com/SengerM/PyticularsTCT/blob/master/PyticularsTCT/ParticularsLaserController.py
# In contrast to the version of Matías, this class is only designed for Linux Operation

class LaserLA01(InterfaceHIDParticulars):

    STATUS_BYTE = 6

    def __init__(self, log, vendor=0xc251, product=0x2201):
        super().__init__(vendor, product, log=log)

        # We only have a local state, as for now the frequency and dac can not be read from the laser!
        self._frequency = None
        self._dac = None

    def on(self):
        if self._frequency is None or  self._dac is None:
            return False

        self._sendDAC(self._dac)
        self._sendFrequency(self._frequency)

        self.send(bytes([91])) # Corresponds to 'Hardware Sequence Enable'

        return True

    def off(self):
        self.send(bytes([90])) # Corresponds to 'Hardware Sequence Disable'
        self.send(bytes([4]))

        return True

    def state(self):
        return self.read()[LaserLA01.STATUS_BYTE] == 1


    def setFrequency(self, frequency):
        if frequency < 50 or frequency > 100e3:
            return False
        self._frequency = frequency
        return True

    def frequency(self):
        return self._frequency

    def _sendFrequency(self, frequency):
        value = 500000000/frequency - 440
        value = int(value/180 + 1)

        self.send(bytes([99]) + value.to_bytes(2, 'little'))

    def setDAC(self, value):
        if value < 0 or value >= 1024:
            return False
        self._dac = value

        return True

    def DAC(self):
        return self._dac

    def _sendDAC(self, dac):
        value = int(dac)
        self.send(bytes([94]) + value.to_bytes(2, 'little'))


    def enableDAC(self):
        self.send(bytes([92]))
    def disableDAC(self):
        self.send(bytes([93]))


    def readADC(self):
        # TODO Implement
        pass
