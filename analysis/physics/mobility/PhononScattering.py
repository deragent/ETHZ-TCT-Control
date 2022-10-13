from dataclasses import dataclass

import numpy as np

from .. import ID

class PhononScatteringMobilityModel():
    '''
    Basic phonon scattering mobility model.
    Implemented based on the Sentaurus SDevice documentation (O-2018.06).
    See "Mobility due to Phonon Scattering" on page 322.
    Parameters implemented here are for electrons and holes in Silicon, as per table 46.
    '''

    @dataclass
    class Parameters:
        uL: float           # [m²/Vs]
        zeta: float         # [-]

    SILICON = {
        ID.e: Parameters(0.1417, 2.5),
        ID.h: Parameters(0.04705, 2.2),
    }

    def __init__(self, type, parameters=None):

        # By default we choose Si parameters
        if parameters is not None:
            self.P = parameters
        else:
            self.P = self.SILICON[type]

    def __call__(self, T, **kwargs):
        return self.mobility(T, **kwargs)

    def mobility(self, T, **kwargs):
        '''Phonon-scattering mobility for the given temperature

        :param T: Temperature in [K]

        :returns: Mobility in [m²/Vs]
        '''
        return self.P.uL*np.power(T/300, -self.P.zeta)
