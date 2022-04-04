class CommLogger():

    def __init__(self, logger, iface):
        self._log = logger
        self.iface = iface

    def sent(self, msg):
        if self._log is not None and self._log.debug:
            self._log.log("%s<SENT>"%(self.iface), msg)

    def recv(self, msg):
        if self._log is not None and self._log.debug:
            self._log.log("%s<RECV>"%(self.iface), msg)

    def warning(self, msg):
        if self._log is not None and self._log.debug:
            self._log.log("%s<WARNING>"%(self.iface), msg)

    def status(self, msg):
        if self._log is not None:
            self._log.log("%s<STATUS>"%(self.iface), msg)

    def error(self, msg):
        if self._log is not None:
            self._log.log("%s<ERROR>"%(self.iface), msg)

    def log(self, cat, msg):
        if self._log is not None:
            self._log.log(cat, msg)
