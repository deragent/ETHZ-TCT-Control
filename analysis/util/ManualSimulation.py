import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

import inspect

class ManualSimulation():

    def __init__(self, sim, domain, definition):
        self._sim = sim
        self._domain = domain

        specs = inspect.getargspec(sim)
        self._params = specs.args

        if len(specs.defaults) < len(self._params):
            raise Exception('Default values for all simulation arguments need to be specified!')

        self._p0 = {
            param: specs.defaults[pp] for pp, param in enumerate(self._params)
        }

        self._fig, self._ax = plt.subplots(1,1)

        # Plot default
        x, y, delta = self._sim(**self._p0)
        [self._line] = self._ax.plot(x, y, label='Simulation')
        if delta is not None:
            [self._delta] = self._ax.plot(x, delta, linestyle='-.', color=self._line.get_color(), label='Difference')

        self._fig.subplots_adjust(bottom=0.05*(len(self._params)+2))

        self._sliders = {
            param: Slider(
                self._fig.add_axes([0.15, (pp+1)*0.05, 0.65, 0.03]),
                definition[param][0],
                definition[param][1], definition[param][2],
                valinit=self._p0[param]
            )
            for pp, param in enumerate(self._params)
        }

        for key, slider in self._sliders.items():
            slider.on_changed(self._update(key))

    def _redraw(self):
        x, y, delta = self._sim(**self._p0)
        self._line.set_data(x, y)
        if delta is not None:
            self._delta.set_data(x, delta)
        self._fig.canvas.draw_idle()

    def _update(self, param):
        def func(val):
            self._p0[param] = val
            self._redraw()
        return func

    def getAx(self):
        return self._ax

    def run(self):
        self._fig.show()
        plt.show()
