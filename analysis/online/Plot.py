from pathlib import Path

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

class Plot():

    def __init__(self, definition, scan):
        self.definition = definition
        self.scan = scan

    def _createFig(self):
        fig, ax = plt.subplots()

        ax.set_title(self.definition.title())

        return fig, ax

    def _generate(self):
        raise NotImplementedError()


    # Data / Scan handling
    def _retrieve(self, keys):
        list = self.scan.list()
        list_keys = [key for key in keys if key in list]
        other_keys = [key for key in keys if key not in list]

        list_data = list.copy()[list_keys]

        for key in other_keys:
            data = []

            for index, line in list.iterrows():
                entry = self.scan.get(index)
                if entry.count() < 1:
                    raise Exception(f'No data for entry [{index}]')

                # For now we only take the first curve into account.
                x, y = entry.curve(0)

                if key in self.definition.FUNCTIONS:
                    data.append(self.apply(key, x, y))
                else:
                    raise Exception(f'Unknown function type [{key}]')

            list_data[key] = data

        return list_data


    def apply(self, fct, time, amplitude):
        sel = time >= 0

        offset = np.mean(amplitude[time < 0])
        amplitude = amplitude[sel] - offset

        if fct == 'min()':
            return np.min(amplitude)
        elif fct == 'max()':
            return np.max(amplitude)
        elif fct == 'integral()':
            return np.trapz(amplitude, time[sel])
        else:
            raise Exception(f'Unknwon plot function [{fct}]!')


    # Label and Legend Handling
    def transform(self, key, values):
        _, _, _, factor = self.definition.getMeta(key)

        return values*factor

    def label(self, key):
        name, _, unit, _ = self.definition.getMeta(key)

        return f'{name} [{unit}]'

    def legend(self, key, value):
        _, short, unit, factor = self.definition.getMeta(key)
        return f'{short}: {value*factor} {unit}'


    def generate(self):
        fig, ax = self._generate()

    def save(self, folder):
        output = Path(folder) / f'{self.definition.name()}.pdf'

        with matplotlib.rc_context({
            'figure.figsize': (12.0, 8.0),
            'font.size': 16,
            # This is a hack to keep saved scatter dots to scale!
            # DPI should not matter in this context, as we do not have any raster data.
            # But the scatter(s=..) parameter is given in dots² so somehow this still maters.
            'figure.dpi': 35,
        }):
            fig, ax = self._generate()

            fig.tight_layout()
            fig.savefig(output)

            plt.close(fig)
