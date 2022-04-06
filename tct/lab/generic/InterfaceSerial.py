import serial
import time

from ...logger import CommLogger

class InterfaceSerial:

    class CommError(Exception):

        def __init__(self, iface, msg, op=None, ret=None):
            self.iface = iface
            self.msg = msg
            self.op = op
            self.ret = ret

        def __str__(self):
            base = "%s [%s]: %s"%(type(self.iface).__name__, self.iface.port, self.msg)
            if self.op is not None:
                base += "\nCMD Sent: %s"%(self.op)
            if self.ret is not None:
                base += "\nReturn Value: %s"%(self.ret)
            return base


    def __init__(self, port, baud, log=None, line_end=b'\n', serial_config=None):
        if serial_config is None:
            serial_config = {}

        self.port = port
        self.baud = baud
        self.line_end = line_end
        self.serial_config = serial_config

        self._if = None

        self.log = CommLogger(log, type(self).__name__)

        self._openPort()

    def __del__(self):
        self._closePort()


    def _openPort(self):
        self._if = serial.Serial(self.port, self.baud, **self.serial_config)

    def _closePort(self):
        if self._if is not None:
            self._if.close()
            self._if = None

    def close(self):
        self._closePort()


    def query(self, cmd, resp=False, len=4096):
        """
        Sends a command to the instrument and receives data if needed.

        The cmd string is encoded to bytes and a NEWLINE is appended.
        This function waits to receive data in return if resp=True is passed as an argument.
        The returned data is decoded into a string and the NEWLINE is stripped.
        """

        if self._if is None:
            return False

        self.log.sent(cmd)
        #Send cmd string
        self._if.write(cmd.encode() + self.line_end)
        time.sleep(0.2)

        if resp:
            reply = self._if.read_until(self.line_end)
            reply = reply.decode().strip('\n\r')

            self.log.recv(reply)
            return reply

        else:
            return True

    ## -----------------------------------------

    def id(self):
        return self.query("*IDN?", True)

    def cls(self):
        return self.query("*CLS", True)
    def rst(self):
        return self.query("*RST", True)
