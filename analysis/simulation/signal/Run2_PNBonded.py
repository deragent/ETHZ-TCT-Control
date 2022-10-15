import numpy as np

from ...physics import constants as pc
from ...physics import ID
from ...physics.mobility import Mobility, HighFieldSaturation

from .util import ChargePropagation_1D


class Run2_PNNModel(ChargePropagation_1D.Model):

    def __init__(self, Vbias, T, Na, Wp, Wn):

        self._W = Wp + Wn
        self._Vbias = Vbias
        self._T = T
        self._Na = Na

        # Create Mobility Models
        self._eSat = HighFieldSaturation(ID.e, Mobility(ID.e))
        self._hSat = HighFieldSaturation(ID.h, Mobility(ID.h))

        Vdep = 0.5*Na*pc.e0/pc.Si.eps*Wp**2
        print(f'Depletion Voltage: {Vdep} V')

        if Vbias < Vdep:
            Wdep = -1*np.sqrt(2*Vbias*pc.Si.eps/(pc.e0*Na))

            def Efield(x):
                E = pc.e0*Na/pc.Si.eps*(Wdep - x)
                E[x <= Wdep] = 0.0
                return E

        else:
            Wdep = -Wp
            def Efield(x):
                E0 = -1*(Vbias - Vdep)/Wp
                return E0 + pc.e0*Na/pc.Si.eps*(-1*Wp - x)

        self._E = Efield
        print(f'Depletion Width: {Wdep*1e6} um')

    def Ew(self, x):
        return 1/self._W

    def v(self, x, charge):
        E = self._E(x)

        # Use saturating mobility model
        mu = x*0.0

        mu[charge > 0] = self._hSat(self._T, np.abs(E[charge > 0]))
        mu[charge < 0] = self._eSat(self._T, np.abs(E[charge < 0]))

        return E*mu*np.sign(charge)


def createChargePropagationSimulation(Vbias, T=pc.T0C+26, Na=4.5e17, Wp=503e-6, Wn=490e-6):

    sim = ChargePropagation_1D()
    sim.x_range = (-Wp, 0)

    sim.setModel(Run2_PNNModel(Vbias, T, Na, Wp, Wn))

    return sim
