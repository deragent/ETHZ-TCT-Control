from dataclasses import dataclass

import numpy as np

from .. import ID

class HighFieldSaturationModel():

    def __init__(self, type, low_field_model):
        raise NotImplementedError()

    def __call__(self, T, E, **kwargs):
        return self.mobility(T, E, **kwargs)

    def mobility(self, T, E, **kwargs):
        '''Mobility for the given temperature and field

        :param T: Temperature in [K]
        :param E: Electric field in [V/m]

        :returns: Mobility in [m²/Vs]
        '''
        raise NotImplementedError()

def SaturationVelocityModel():
    def __init__(self, type):
        raise NotImplementedError()

    def __call__(self, T, **kwargs):
        return self.saturationVelocity(T, **kwargs)

    def saturationVelocity(self, T, **kwargs):
        '''Saturation Velocity for the given temperature

        :param T: Temperature in [K]

        :returns: Saturation Velocity in [m/s]
        '''
        raise NotImplementedError(SaturationVelocityModel)


class ExtendedCanaliVelocityModel():
    '''
    Saturation velocit model.
    Implemented based on the Sentaurus SDevice documentation (O-2018.06).
    See "VelocitySaturationModels" on page 372.
    This model is recommended for Silicon
    '''

    @dataclass
    class Parameters:
        vsat0: float        # [m/s]
        vsatexp: float      # [-]

    SILICON = {
        ID.e: Parameters(1.07e5, 0.87),
        ID.h: Parameters(8.37e4, 0.52),
    }

    def __init__(self, type, parameters=None):

        # By default we choose Si parameters
        if parameters is not None:
            self.P = parameters
        else:
            self.P = self.SILICON[type]

    def __call__(self, T, **kwargs):
        return self.saturationVelocity(T, **kwargs)

    def saturationVelocity(self, T, **kwargs):
        '''Saturation Velocity for the given temperature

        :param T: Temperature in [K]

        :returns: Mobility in [m/s]
        '''
        return self.P.vsat0*np.power(300/T, self.P.vsatexp)


class ExtendedCanaliMobilityModel(HighFieldSaturationModel):
    '''
    High field mobility saturation model.
    Implemented based on the Sentaurus SDevice documentation (O-2018.06).
    See "Extended Canali Model" on page 367.
    Parameters implemented here are for electrons and holes in Silicon, as per table 67.
    By default (for Si e/h) uses Canali saturation velocity model.
    '''

    @dataclass
    class Parameters:
        beta0: float        # [-]
        betaexp: float      # [-]
        alpha: float        # [-]

        vsat: SaturationVelocityModel

    SILICON = {
        ID.e: Parameters(1.109, 0.66, 0, ExtendedCanaliVelocityModel(ID.e)),
        ID.h: Parameters(1.213, 0.17, 0, ExtendedCanaliVelocityModel(ID.h)),
    }

    def __init__(self, type, low_field_model, parameters=None):

        self._mulow = low_field_model

        # By default we choose Si parameters
        if parameters is not None:
            self.P = parameters
        else:
            self.P = self.SILICON[type]

    def mobility(self, T, E, **kwargs):
        '''Mobility for the given temperature and field

        :param T: Temperature in [K]
        :param E: Electric field in [V/m]

        :returns: Mobility in [m²/Vs]
        '''
        mulow = self._mulow(T)
        b = self.P.beta0*np.power(T/300, self.P.betaexp)
        vsat = self.P.vsat(T)
        a = self.P.alpha

        return (a + 1)*mulow/(a + np.power(1 + np.power((a+1)*mulow*E / vsat, b), 1/b))


## Define default High Field Saturation Model
# Default is always for Silicon
HighFieldSaturation = ExtendedCanaliMobilityModel
