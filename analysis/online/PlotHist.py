import numpy as np

from .Plot import Plot
from ..fit import ERF

class PlotHist(Plot):

    def __init__(self, definition, scan):
        super().__init__(definition, scan)

        self._data = []
        self._collectData()

    def _collectData(self):
        keys = [self.definition.plot]

        if self.definition.group:
            keys.extend(self.definition.group)
            data = self._retrieve(keys)

            self._data = list(data.groupby(self.definition.group))
        else:
            data = self._retrieve(keys)

            self._data = [(None, data)]

    def _generate(self):
        fig, ax = self._createFig()

        legend = False

        labels = []
        datasets = []
        max_count = 0
        total_count = 0

        for group, data in self._data:
            data = np.array(self.transform(self.definition.plot, data[self.definition.plot]))

            # TODO: Add support for log scaling of axis

            label = ''
            if self.definition.group:
                legend = True

                keys = self.definition.group
                if len(self.definition.group) == 1:
                    group = [group]

                label = ' - '.join([
                    self.legend(key, group[kk]) for kk, key in enumerate(keys)
                ])

                labels.append(label)

            datasets.append(data)
            max_count = max(max_count, len(data))
            total_count += len(data)

        patches = ax.hist(datasets, int(np.sqrt(total_count)), label=labels, histtype='step')

        if legend:
            ax.legend()

        ax.set_xlabel(self.label(self.definition.plot))
        ax.set_ylabel('Count [-]')

        ax.grid()

        return fig, ax
