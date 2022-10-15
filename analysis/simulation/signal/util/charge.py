import numpy as np
import scipy.stats

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
