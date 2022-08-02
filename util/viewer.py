import argparse
import sys
import threading
import queue
import time

import numpy as np
import matplotlib.pyplot as plt

from tct.lab.control import ScopeControl
from tct.logger import Logger


class ScopeHandler(threading.Thread):

    def __init__(self):
        super().__init__()

        self._scope = ScopeControl()

        self._data = queue.Queue(maxsize=1)
        self._cmd = queue.Queue()

        self.daemon = True

    def run(self):

        self._scope.scope.Average('C2', 100)

        while True:
            self._handleCmd()

            if self._data.full():
                time.sleep(0.01)
                continue

            self._data.put(self._scope.AcquireAverage())


    def _handleCmd(self):
        while True:
            try:
                cmd, cmd_data = self._cmd.get(False)

                if cmd == CommandInput.CMD_AMPLITUDE:
                    if cmd_data is None:
                        self._scope.AutoScale()
                    else:
                        self._scope.SetVertRange(cmd_data)
                elif cmd == CommandInput.CMD_AVERAGE:
                    self._scope.SetAverage(cmd_data)

            except queue.Empty:
                break


    def get(self):
        try:
            wave = self._data.get(False)
            return wave
        except queue.Empty:
            return None

    def command(self, cmd):
        self._cmd.put(cmd)



class CommandInput(threading.Thread):

    CMD_EXIT = 0
    CMD_PAUSE = 1
    CMD_RUN = 2
    CMD_SINGLE = 3
    CMD_AMPLITUDE = 4
    CMD_AVERAGE = 5

    def __init__(self):
        super().__init__()

        self._queue = queue.Queue()
        self._running = False
        self.daemon = True

    def run(self):
        self._running = True

        while self._running:
            line = sys.stdin.readline().strip().lower()

            if line in ['exit', 'close']:
                self._queue.put((self.CMD_EXIT, None))
            elif line in ['pause']:
                self._queue.put((self.CMD_PAUSE, None))
            elif line in ['run']:
                self._queue.put((self.CMD_RUN, None))
            elif line in ['single']:
                self._queue.put((self.CMD_SINGLE, None))
            elif line.startswith('amplitude '):
                parts = line.split(' ')

                if len(parts) > 1 and parts[1] == 'auto':
                    self._queue.put((self.CMD_AMPLITUDE, None))
                elif len(parts) > 2:
                    try:
                        self._queue.put(
                            (self.CMD_AMPLITUDE, (float(parts[1]), float(parts[2])))
                        )
                    except:
                        pass
            elif line.startswith('average '):
                parts = line.split(' ')

                if len(parts) > 1:
                    try:
                        self._queue.put(
                            (self.CMD_AVERAGE, float(parts[1]))
                        )
                    except:
                        pass


    def get(self):
        try:
            return self._queue.get(False)
        except queue.Empty:
            return (None, None)

    def stop(self):
        self._running = False


class ViewInterface():

    def __init__(self):

        plt.ion()
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot(1, 1, 1)
        self._ax.set_xlabel('Time [ns]')
        self._ax.set_ylabel('Amplitude [mV]')
        self._ax.grid()

        self.setTitle('Running')

    def setTitle(self, state=None):
        title = 'Live TCT View'
        if state is not None:
            title += f' [{state}]'
        self._ax.set_title(title)

    def update(self, wave):
        if len(self._ax.lines) > 0:
            self._ax.lines.remove(self._ax.lines[-1])
        self._ax.plot(wave.x*1e9, wave.y*1e3, 'g')

        self._fig.canvas.draw_idle()

    def loop(self):
        self._fig.canvas.start_event_loop(0.05)



# Create the child threads
cmdHandler = CommandInput()
cmdHandler.start()

scopeHandler = ScopeHandler()
scopeHandler.start()

view = ViewInterface()


##
## Run the main state-machine
##
PAUSE = 0
RUN = 1
SINGLE = 2

state = RUN

while True:

    if state in [RUN, SINGLE]:
        wave = scopeHandler.get()

        if wave is not None:
            view.update(wave)

            if state == SINGLE:
                view.setTitle('Single')
                state = PAUSE


    ## Handle the commands from stdin
    cmd, cmd_data = cmdHandler.get()

    if cmd == cmdHandler.CMD_EXIT:
        break
    elif cmd == cmdHandler.CMD_PAUSE:
        state = PAUSE
        view.setTitle('Paused')
    elif cmd == cmdHandler.CMD_RUN:
        state = RUN
        view.setTitle('Running')
        scopeHandler.get() # Retrieve (and clear) any stale data
    elif cmd == cmdHandler.CMD_SINGLE:
        state = SINGLE
        view.setTitle('Wait')
        scopeHandler.get() # Retrieve (and clear) any stale data
    elif cmd in [cmdHandler.CMD_AMPLITUDE, cmdHandler.CMD_AVERAGE]:
        scopeHandler.command((cmd, cmd_data))

    view.loop()
