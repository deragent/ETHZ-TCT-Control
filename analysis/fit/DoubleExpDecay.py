import numpy as np
import scipy.optimize
import scipy.stats

class DoubleExpDecay():

    PARAMETERS = ['T0', 'RC1', 'U1', 'RC2', 'U2']

    def model(self):

        def ExpDecay(t, T0, RC1, U1, RC2, U2):
            return U1*np.exp(-1*(t - T0)/RC1) + U2*np.exp(-1*(t - T0)/RC2)

        return ExpDecay

    def __init__(self, x, y, selection=None, p0={}):

        if selection is not None:
            self.x = x[selection]
            self.y = y[selection]
        else:
            self.x = x
            self.y = y

        self.p0 = {}

        self.p0['T0'] = self.x[0]

        self.p0['U1'] = self.y[0]
        self.p0['RC1'] = self.x[np.argmax(self.y <= 0.6*self.y[0])] - self.p0['T0']

        self.p0['U2'] = self.p0['U1'] / 10
        self.p0['RC2'] = self.p0['RC1'] * 10

        self.p0.update(p0)

        self.doFit()

    def doFit(self):
        p0 = [self.p0[param] for param in self.PARAMETERS]
        popt, pcov = scipy.optimize.curve_fit(self.model(), self.x, self.y, p0=p0)

        self.param = {param: popt[pp] for pp, param in enumerate(self.PARAMETERS)}
        self.pcov = pcov


    def eval(self, x):
        return self.model()(x, **self.param)
