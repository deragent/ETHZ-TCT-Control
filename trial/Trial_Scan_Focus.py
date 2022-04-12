import time
import numpy as np
import matplotlib.pyplot as plt

from tct.system import Setup
from tct.logger import Logger

log = Logger(print=True, debug=False)

s = Setup(vlimit=1000, ilimit=0.002, log=log)

# Zs = np.linspace(77.5, 79.5, 101)
Zs = np.linspace(65, 95, 91)

# Ideal seems to be 77.5

X = 0.9
Y = -1.6

data = np.zeros((len(Zs)))

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

for zz, Z in enumerate(Zs):

    s.stage.MoveTo(x=X, y=Y, z=Z)

    wave = s.scope.AcquireAverage()

    # Maximum Amplitude
    # data[zz] = np.max(wave.y)

    # Integral of pulse
    sel = wave.x >= 0
    offset = np.mean(wave.y[wave.x < 0])
    amplitude = wave.y[sel] - offset
    data[zz] = np.trapz(amplitude, wave.x[sel])

    print(f'{X}\t{Y}\t{Z}\t{data[zz]}')

fig = plt.plot(Zs, data)
plt.show()

s.Off()
