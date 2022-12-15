from .CommandHandler import CommandHandler

import subprocess
import sys

class ViewHandler(CommandHandler):

    def __init__(self, log):
        super().__init__(log)

        self._viewer = None

    def commandDict(self):
        return {
            'open': None,
            'close': None,
        }

    def handle(self, input):
        if input[0] in ['open'] and self._viewer is None:
            self._viewer = subprocess.Popen([sys.executable, "-m", "util.viewer"], stdin=subprocess.PIPE)
        elif input[0] in ['close']:
            self.terminate()

        # TODO need to handle the scope commands (average, amplitude etc.)

    def terminate(self):
        if self._viewer is not None:
            self._viewer.terminate()
            self._viewer = None
