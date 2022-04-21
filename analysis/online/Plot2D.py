import numpy as np
import scipy.optimize
import scipy.stats

from .Plot import Plot

def ERF(x, A, B, mu, sigma):
    return A*scipy.stats.norm.cdf(x, mu, sigma) + B

class Plot2D(Plot):

    def __init__(self, definition, scan):
        super().__init__(definition, scan)

        self._data = []
        self._collectData()

    def _collectData(self):
        if self.definition.group:
            keys = [self.definition.x, self.definition.plot]
            keys.extend(self.definition.group)
            data = self._retrieve(keys)

            self._data = list(data.groupby(self.definition.group))
        else:
            keys = [self.definition.x, self.definition.plot]
            data = self._retrieve(keys)

            self._data = [(None, data)]


    def isMonothonic(self, values):
        diff = np.diff(values)
        return np.all(diff > 0) or np.all(diff < 0)


    def _addERFFit(self, ax, x, y, color):
        try:
            B0 = np.min(y)
            A0 = np.max(y) - B0
            mu0 = x[np.argmax(y - B0 >= 0.5*A0)]

            A, B, mu, sigma = scipy.optimize.curve_fit(ERF, x, y, p0=[A0, B0, mu0, 0.02])[0]

            xfit = np.linspace(np.min(x), np.max(x), 101)
            # The factor of 1e3 (mm -> um) is hardcoded here.
            # This is ok for now, as the main function of this fit is to find the focused beam size (in the order of 10um)
            ax.plot(xfit, ERF(xfit, A, B, mu, sigma), color=color, linestyle='--', label=f'sig = {sigma*1e3:.3f}')

            return True
        except Exception as e:
            import traceback
            print(f'Exception: {e}')
            print(traceback.format_exc())

            # Fit failed, we do nothing
            return False

    def _generate(self):
        fig, ax = self._createFig()

        legend = False

        for group, data in self._data:
            x = np.array(self.transform(self.definition.x, data[self.definition.x]))
            y = np.array(self.transform(self.definition.plot, data[self.definition.plot]))

            # TODO: Add support for log scaling of axis

            linestyle = '-'
            marker = '.'
            if not self.isMonothonic(x):
                linestyle = ''
                marker = 'o'

            label = ''
            if self.definition.group:
                legend = True

                keys = self.definition.group
                if len(self.definition.group) == 1:
                    group = [group]

                label = ' - '.join([
                    self.legend(key, group[kk]) for kk, key in enumerate(keys)
                ])


            lines = ax.plot(x, y, linestyle=linestyle, marker=marker, label=label)

            if self.definition.fit == self.definition.FIT_ERF:
                legend = self._addERFFit(ax, x, y, lines[0].get_color()) and legend


        ax.legend()
        ax.set_xlabel(self.label(self.definition.x))
        ax.set_ylabel(self.label(self.definition.plot))

        return fig, ax
