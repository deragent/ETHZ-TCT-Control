import numpy as np

from ...physics import constants as pc

from .util import ChargePropagation_1D

from .Run2_PNBonded import Run2_PNNModel

class Run2_PNNModel_Extended(Run2_PNNModel):

    ## This model implements the extended Ramo propagaion of the bonded samples.
    # The main difference with respect to Run2_PNNModel is the addition of the
    # time dependent medium impulse response.
    # For details see the following presentation:
    # 20230201_JWuethrich_ExtendedRamo.pdf
    #
    # Both cases (A and B) are implemented separately

    def __init__(self, Vbias, T, Na, Wp, Wn, RhoP, RhoN, C, R, Gain, Tsample=50e-12):

        super().__init__(Vbias, T, Na, Wp, Wn)

        self._rhoP = RhoP
        self._rhoN = RhoN

        self._rload = R
        self._cload = C
        self._gain = Gain

        self._tsample = Tsample

        if self.WDepletion >= Wp:
            # P-side fully depleted
            self._WImpulse = self._calculateCaseB()
        else:
            # P-side partially depleted
            self._WImpulse = self._calculateCaseA()

    def _calculateCaseA(self):
        dU = self._Wp - self.WDepletion

        sig_avg = ((self._W - self._Wn)/self._rhoN + (self._W - dU)/self._rhoP)/self._W
        l1 = 0.5*(sig_avg - np.sqrt(sig_avg**2 - 4*self.WDepletion/self._W/self._rhoP/self._rhoN))
        l2 = 0.5*(sig_avg + np.sqrt(sig_avg**2 - 4*self.WDepletion/self._W/self._rhoP/self._rhoN))

        tau1 = pc.Si.eps/l1
        tau2 = pc.Si.eps/l2

        mA = [
            [l1, l2],
            [1, 1]
        ]

        mB = [
            self._Wn/self._W/self._rhoN + dU/self._W/self._rhoP,
            self._W/self.WDepletion - 1
        ]

        b, c = np.linalg.solve(mA, mB)

        # Calculate the impulse response
        tau_max = max(tau1, tau2)
        t_max = min(10*tau_max, 1e-6)

        t_w = np.arange(0, t_max, self._tsample)
        w = np.zeros(t_w.shape)

        w[0] = 1
        w = w \
            + b*1/tau1*np.exp(-t_w/tau1)*self._tsample \
            + c*1/tau2*np.exp(-t_w/tau2)*self._tsample

        return w

    def _calculateCaseB(self):
        tau = self._W*pc.Si.eps/(self._Wp/self._rhoN)

        # Calculate the impulse reponse
        t_max = min(10*tau, 1e-6)
        t_w = np.arange(0, t_max, self._tsample)
        w = np.zeros(t_w.shape)

        w[0] = 1
        w = w + self._Wn/self._Wp*1/tau*np.exp(-t_w/tau)*self._tsample

        return w


    def applyMediumResponse(self, signal):
        return signal.convolve(self._WImpulse)


    def post(self, signal):
        ## Resample the signal (default 50ps / 20Gsps)
        signal = signal.resample(self._tsample)

        ## Apply the extended Ramo medium impulse response (from weighting vector)
        signal = self.applyMediumResponse(signal)

        ## Apply the electronics reponse (low pass filter)
        fc = 1/(2*np.pi*self._cload*self._rload)
        signal = signal.filterLowPass(fc, self._gain*self._rload)

        return signal



def createChargePropagationSimulation(
    Vbias, T=pc.T0C+26, Na=4.5e17,
    Wp=503e-6, Wn=490e-6,
    RhoP=21.4e3*1e-2, RhoN=10e3*1e-2,
    C=23e-12, R=50, GainDB=51.52
):

    sim = ChargePropagation_1D()

    sim.dt_max = 1e-9
    sim.dx = 0.2e-6
    sim.t_end = 400e-9

    sim.x_range = (-Wp, 0)

    sim.setModel(Run2_PNNModel_Extended(
        Vbias, T, Na, Wp, Wn,
        RhoP, RhoN,
        C, R, 10**(GainDB/20)
    ))

    return sim
