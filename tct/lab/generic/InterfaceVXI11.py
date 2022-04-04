import vxi11

from ...logger import CommLogger

class InterfaceVXI11():

    class CommError(Exception):

        def __init__(self, iface, msg, op=None, ret=None):
            self.iface = iface
            self.msg = msg
            self.op = op
            self.ret = ret

        def __str__(self):
            base = "%s [VXI11: %s]: %s"%(type(self.iface).__name__, self.iface.ip, self.msg)
            if self.op is not None:
                base += "\nCMD Sent: %s"%(self.op)
            if self.ret is not None:
                base += "\nReturn Value: %s"%(self.ret)
            return base


    def __init__(self, ip, log=None):
        self.ip = ip

        self.log = CommLogger(log, type(self).__name__)

        self.conn = None
        self._openVXI11()

    def __del__(self):
        self._closeVXI11()

    def _openVXI11(self):
        self.conn = vxi11.Instrument(self.ip)

    def _closeVXI11(self):
        pass

    def close(self):
        self._closeVXI11()


    def query(self, cmd, resp=False, len=None):
        """
        Sends a command to the instrument and receives data if needed.
        """

        if resp:
            return self.conn.ask(cmd)
        else:
            self.conn.write(cmd)

        return True

    ## -----------------------------------------

    def id(self):
        return self.query("*IDN?", True)
