import numpy as np
import mpl_toolkits.axes_grid1

from .Plot import Plot

class Plot3D(Plot):

    def __init__(self, definition, scan):
        super().__init__(definition, scan)

        self._data = []
        self._collectData()

    def _collectData(self):
            keys = [self.definition.x, self.definition.y, self.definition.plot]
            self._data = self._retrieve(keys)

    def _generate(self):
        fig, ax = self._createFig()

        x = np.array(self.transform(self.definition.x, self._data[self.definition.x]))
        y = np.array(self.transform(self.definition.y, self._data[self.definition.y]))
        z = np.array(self.transform(self.definition.plot, self._data[self.definition.plot]))


        bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        width, height = bbox.width, bbox.height
        print(width, height)

        l = fig.dpi*np.min((height/len(np.unique(y)), width/len(np.unique(x))))
        print(fig.dpi)
        print(l)

        scatter = ax.scatter(x, y, c=z, s=3*l**2, alpha=0.8)

        divider = mpl_toolkits.axes_grid1.make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.1)

        fig.colorbar(
            scatter, cax=cax, orientation='vertical',
            label=self.label(self.definition.plot)
        )

        ax.set_xlabel(self.label(self.definition.x))
        ax.set_ylabel(self.label(self.definition.y))

        return fig, ax
