import socket
import time

from ...logger import CommLogger

class InterfaceIP:

    # Reopen the socket if it has been open for > 30min
    OPEN_TIMEOUT = 30*60

    # Reopen the socket if the last command was > 10min ago
    LAST_TIMEOUT = 10*60


    class CommError(Exception):

        def __init__(self, iface, msg, op=None, ret=None):
            self.iface = iface
            self.msg = msg
            self.op = op
            self.ret = ret

        def __str__(self):
            base = "%s [%s:%i]: %s"%(type(self.iface).__name__, self.iface.ip, self.iface.port, self.msg)
            if self.op is not None:
                base += "\nCMD Sent: %s"%(self.op)
            if self.ret is not None:
                base += "\nReturn Value: %s"%(self.ret)
            return base


    def __init__(self, ip, port, log=None):
        self.ip = ip
        self.port = port

        self.log = CommLogger(log, type(self).__name__)

        self._openSocket()

        self.time_last = time.time()

    def __del__(self):
        self._closeSocket()


    def _openSocket(self):
        try:
            #create an AF_INET, STREAM socket (TCP)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            error = self.CommError(self, 'Failed to create the socket!')
            self.log.error(str(error))
            raise error

        try:
            #Connect to remote server
            self.sock.connect((self.ip , self.port))
        except socket.error:
            error = self.CommError(self, 'Failed to connect to the IP!')
            self.log.error(str(error))
            raise error

        self.time_open = time.time()

    def _closeSocket(self):
        self.sock.close()
        time.sleep(.300)


    def close(self):
        self._closeSocket()


    def query(self, cmd, resp=False, len=4096):
        """
        Sends a command to the instrument and receives data if needed.

        The cmd string is encoded to bytes and a NEWLINE is appended.
        This function waits to receive data in return if resp=True is passed as an argument.
        The returned data is decoded into a string and the NEWLINE is stripped.
        """

        # Reopen the socket if the last cmd was a long time ago, or of the socket was open too long
        if self.time_last < time.time() - InterfaceIP.LAST_TIMEOUT or self.time_open < time.time() - InterfaceIP.OPEN_TIMEOUT:
            self.log.warning("Socket will be reopened due to timeout.")
            self._closeSocket()
            self._openSocket()

        self.time_last = time.time()


        try:
            self.log.sent(cmd)
            #Send cmd string
            self.sock.sendall(cmd.encode() + b'\n')
            time.sleep(0.02)
        except socket.error:
            error = self.CommError(self, 'Failed to send', op=cmd)
            self.log.error(str(error))
            raise error

        if resp:
            reply = self.sock.recv(int(len))
            reply = reply.decode().strip('\n\r')

            self.log.recv(reply)
            return reply

        else:
            return True

    ## -----------------------------------------

    def id(self):
        return self.query("*IDN?", True)
