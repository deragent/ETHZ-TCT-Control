import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
import scipy.stats

from tct.system import Setup
from tct.logger import Logger

log = Logger(print=True, debug=False)

s = Setup(vlimit=1000, ilimit=0.002, log=log)

Zs = np.linspace(77.8, 78.8, 21)

Xs = np.linspace(0.3, 0.6, 21)
Y = -1.6

data = np.zeros((len(Zs), len(Xs)))

s.scope.scope.TriggerMode(s.scope.scope.TRIGGER_MODE.NORMAL)
s.scope.scope.ClearSweeps('C2')
s.scope.scope.Average('C2', 100)
time.sleep(0.1)
s.scope.scope.GetAverage('C2')

s.laser.LaserSetFrequency(50e3)
s.laser.LaserSetDAC(290)
s.laser.LaserOn()

s.amp.AmpSet(50)
s.amp.AmpOn()

s.bias.SMURampVoltage(120)
s.bias.SMUOn()

def erf(x, A, mu, sigma):
    return A*scipy.stats.norm.cdf(x, mu, sigma)
Xfit = np.linspace(np.min(Xs), np.max(Xs), 101)

for zz, Z in enumerate(Zs):
    for xx, X in enumerate(Xs):

        s.stage.MoveTo(x=X, y=Y, z=Z)

        wave = s.scope.AcquireAverage()

        # Integral of pulse
        sel = wave.x >= 0
        offset = np.mean(wave.y[wave.x < 0])
        amplitude = wave.y[sel] - offset
        data[zz, xx] = np.trapz(amplitude, wave.x[sel])*1e8

        print(f'{X}\t{Y}\t{Z}\t{data[zz, xx]}')


    lines = plt.plot(Xs, data[zz, :], label=f'Focus: {Z:.3f}mm')

    try:
        A, mu, sigma = scipy.optimize.curve_fit(erf, Xs, data[zz, :], p0=[1, 0.42, 0.02])[0]

        plt.plot(Xfit, erf(Xfit, A, mu, sigma), color=lines[0].get_color(), linestyle='--', label=f'sig = {sigma*1e3:.2f} um')
    except Exception as e:
        print(e)
        pass


s.Off()

plt.legend()
plt.xlabel('X-Position [mm]')
plt.ylabel('Pulse Integral [arb]')

plt.show()
