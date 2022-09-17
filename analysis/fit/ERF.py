import numpy as np
import scipy.optimize
import scipy.stats

class ERF():

    PARAMETERS = ['A', 'B', 'mu', 'sigma']

    def model(self):

        def ERF(x, A, B, mu, sigma):
            return A*scipy.stats.norm.cdf(x, mu, sigma) + B

        return ERF

    def __init__(self, x, y, selection=None, p0={}):

        if selection is not None:
            self.x = x[selection]
            self.y = y[selection]
        else:
            self.x = x
            self.y = y

        self.p0 = {}

        self.p0['B'] = self.y[0]
        self.p0['A'] = self.y[-1] - self.p0['B']
        sign = np.sign(self.p0['A'])

        self.p0['mu'] = self.x[np.argmax(sign*(self.y - self.p0['B']) >= sign*0.5*self.p0['A'])]
        self.p0['sigma'] = self.x[np.argmax(sign*(self.y - self.p0['B']) >= sign*0.8*self.p0['A'])] - self.p0['mu']

        self.p0.update(p0)

        self.doFit()

    def doFit(self):
        p0 = [self.p0[param] for param in self.PARAMETERS]
        popt, pcov = scipy.optimize.curve_fit(self.model(), self.x, self.y, p0=p0)

        self.param = {param: popt[pp] for pp, param in enumerate(self.PARAMETERS)}
        self.pcov = pcov


    def eval(self, x):
        return self.model()(x, **self.param)
