import numpy as np
import scipy.stats

import pybragg

from ....physics import constants as pc

def point(Neh, position, e=True, h=True):
    charges = []
    if e:
        charges.append((position, -pc.e0*Neh))
    if h:
        charges.append((position, pc.e0*Neh))

    return charges


def normal(Neh, position, sigma, Nsigma=3, points=31, e=True, h=True):
    norm_range = np.linspace(position - Nsigma*sigma, position + Nsigma*sigma, points)

    norm_pdf = scipy.stats.norm.pdf(norm_range, position, sigma)
    norm_pdf = Neh*norm_pdf/np.sum(norm_pdf)

    charges = []
    for x, val in zip(norm_range, norm_pdf):
        if e:
            charges.append((x, -pc.e0*val))
        if h:
            charges.append((x, pc.e0*val))

    return charges


def exponential(Neh, position, lbda, Nlbda=5, points=26, e=True, h=True):
    pdf_range = np.linspace(0, Nlbda*np.abs(lbda), points)

    exp_pdf = scipy.stats.expon.pdf(pdf_range, 0, np.abs(lbda))
    exp_pdf = Neh*exp_pdf/np.sum(exp_pdf)

    charge_range = np.linspace(position, position + Nlbda*lbda, points)

    charges = []
    for x, val in zip(charge_range, exp_pdf):
        if e:
            charges.append((x, -pc.e0*val))
        if h:
            charges.append((x, pc.e0*val))

    return charges

def alpha(Neh, pos, surface=-503e-6, Npoints=31, e=True, h=True):
    ## pos is the approximate peak location
    ## surface is the location of the silicon wafer surface

    # Based on interaction of Am-241 5.485MeV alpha in Si
    # Based on measurements on the 30.10.2022 (with ca. 9mm air gap)
    # -> Nominal pos ~ -483e-6 / Nominal Neh ~ 1.28e6

    # Constants (fitted to TRIM simulation)
    SIGMA = 8.7e-7
    P = 1.415
    K = 0.002

    peak = pos - surface
    depth = np.linspace(0, peak, Npoints)
    dose_pdf = pybragg.bortfeld(depth, D100=1000, R0=peak+SIGMA, sigma=SIGMA, p=P, k=K)

    # Normalize dose to total Neh
    dose_pdf = Neh*dose_pdf/np.sum(dose_pdf)

    charge_range = np.linspace(surface, pos, Npoints)

    charges = []
    for x, val in zip(charge_range, dose_pdf):
        if e:
            charges.append((x, -pc.e0*val))
        if h:
            charges.append((x, pc.e0*val))

    return charges
