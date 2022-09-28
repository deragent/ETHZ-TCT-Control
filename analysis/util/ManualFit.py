import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

import inspect

class ManualFit():

    def __init__(self, model, domain, definition):
        self._model = model
        self._domain = domain

        specs = inspect.getargspec(model)
        self._params = specs.args

        if len(self._params) < 2:
            raise Exception('Model needs to have at least two arguments!')

        if len(specs.defaults) < len(self._params)-1:
            raise Exception('Default values for all model arguments need to be specified!')

        self._p0 = {
            param: specs.defaults[pp] for pp, param in enumerate(self._params[1:])
        }

        self._fig, self._ax = plt.subplots(1,1)

        # Plot default
        [self._line] = self._ax.plot(domain, self._model(domain, **self._p0), label='Model Fit')

        self._fig.subplots_adjust(bottom=0.05*(len(self._params)+1))

        self._sliders = {
            param: Slider(
                self._fig.add_axes([0.15, (pp+1)*0.05, 0.65, 0.03]),
                definition[param][0],
                definition[param][1], definition[param][2],
                valinit=self._p0[param]
            )
            for pp, param in enumerate(self._params[1:])
        }

        for key, slider in self._sliders.items():
            slider.on_changed(self._update(key))

    def _redraw(self):
        data = self._model(self._domain, **self._p0)
        self._line.set_ydata(data)
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
