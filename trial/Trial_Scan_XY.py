import time
import numpy as np
import matplotlib.pyplot as plt

from tct.system import Setup
from tct.logger import Logger

log = Logger(print=True, debug=False)

s = Setup(vlimit=1000, ilimit=0.002, log=log)

Z = 73.133 # mm

Xs = np.linspace(0, 2, 21)
Ys = np.linspace(-2.5, -0.5, 21)

data = np.zeros((len(Xs), len(Ys)))

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

for xx, X in enumerate(Xs):
    for yy, Y in enumerate(Ys):

        s.stage.MoveTo(x=X, y=Y, z=Z)

        wave = s.scope.AcquireAverage()

        data[xx, yy] = np.max(wave.y)

        print(f'{X}\t{Y}\t{Z}\t{data[xx, yy]}')


s.Off()


fig = plt.imshow(data.T, extent=[min(Xs),max(Xs),min(Ys),max(Ys)], origin="lower") #, norm=matplotlib.colors.LogNorm())

plt.xlabel('X-Position [mm]')
plt.ylabel('Y-Position [mm]')
plt.colorbar()
plt.show()
