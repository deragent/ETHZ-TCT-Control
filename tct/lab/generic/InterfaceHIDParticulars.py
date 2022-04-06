import usb.core
import usb.util
import time

from ...logger import CommLogger

# This implementation is based and partially copied from the work done by Matías Senger at UZH
# https://github.com/SengerM/PyticularsTCT/blob/master/PyticularsTCT/ParticularsLaserController.py
# In contrast to the version of Matías, this class is only designed for Linux Operation

class InterfaceHIDParticulars:
    """The main use case of this driver class, is for the Particulars Laser.
    They connect as a USB HID device.

    Usually they have the following device descriptor:
    # ID c251:2201 Keil Software, Inc. LASER Driver IJS"""

    class CommError(Exception):

        def __init__(self, iface, msg, op=None, ret=None):
            self.iface = iface
            self.msg = msg
            self.op = op
            self.ret = ret

        def __str__(self):
            base = "%s [%s:%i]: %s"%(type(self.iface).__name__, self.iface.id_vendor, self.iface.id_product, self.msg)
            if self.op is not None:
                base += "\nCMD Sent: %s"%(self.op)
            if self.ret is not None:
                base += "\nReturn Value: %s"%(self.ret)
            return base


    def __init__(self, vendor, product, log=None):
        self.id_vendor = vendor
        self.id_product = product

        self.log = CommLogger(log, type(self).__name__)

        self.device = None
        self.interface = None
        self.endpoint = None

        self._openDevice()

    def __del__(self):
        self._closeDevice()


    def _openDevice(self):
        # Find all corresponding devices
        devices = list(usb.core.find(idVendor=self.id_vendor, idProduct=self.id_product, find_all=True))
        if len(devices) < 1:
            raise InterfaceHIDParticulars.CommError(self, 'Could not find any matching USB devices!')

        if len(devices) > 1:
            raise InterfaceHIDParticulars.CommError(self, 'Multiple matching devices found!')

        # Select the device, first configuration and default interface
        # See: https://unix.stackexchange.com/a/682662
        self.device = devices[0]
        self.interface = self.device[0].interfaces()[0]

        # Detach the linux kernel driver from the interface (see: https://stackoverflow.com/a/36505328)
        # This is only possible / necessary on linux (see: https://stackoverflow.com/a/42227085)
        if self.device.is_kernel_driver_active(self.interface.bInterfaceNumber):
            self.device.detach_kernel_driver(self.interface.bInterfaceNumber)

        # Select the default endpoint
        self.endpoint = self.interface.endpoints()[0]

    def _closeDevice(self):
        if self.device is not None:
            usb.util.dispose_resources(self.device)


    def close(self):
        self._closeDevice()


    def send(self, data_bytes):
        if self.device is None:
            self.log.error('Attempting to send on a closed device!')
            return False

        # bytes should not be longer than 64!
        data = data_bytes + (64-len(data_bytes))*b'0'

        self.log.sent('0x' + data_bytes.hex())

        # For documentation on control transfer (always to enpoint 0):
        # https://www.usb.org/sites/default/files/documents/hid1_11.pdf (Section 7.2.2)
        bytes_sent = self.device.ctrl_transfer(
            bmRequestType = 0x21,    # Host to Device
            bRequest = 9,            # SET_REPORT
            wValue = 0x200,          # Report Type
            wIndex = 0,              # Interface 0
            data_or_wLength = data,
        )
        if bytes_sent != len(data):
            raise InterfaceHIDParticulars.CommError(self, 'Error during ctrl_transfer', ret=bytes_sent)

        # Pause in between comands
        time.sleep(.01)

        return bytes_sent

    def read(self):
        if self.endpoint is None:
            self.log.error('Attempting to receive from a closed device!')
            return False

        for k in [1,2]: # Read twice as first response tends to be empty
            data = self.endpoint.read(size_or_buffer = 64)

        data = bytes(data)
        self.log.recv('0x' + data.hex())

        return data
