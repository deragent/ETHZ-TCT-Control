import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors

plt.rcParams.update({
    'figure.figsize': (12.0, 8.0),
    'font.size': 16,
})


from tct.system import Setup
from tct.logger import Logger

log = Logger(print=True, debug=False)

s = Setup(vlimit=1000, ilimit=0.002, log=log)

Z = 78.2 # mm

Xs = np.linspace(-2.1, -0.9, 7)
Ys = np.linspace(0.3, 1.5, 7)

data = np.zeros((len(Xs), len(Ys)))

s.scope.scope.TriggerMode(s.scope.scope.TRIGGER_MODE.NORMAL)
s.scope.scope.ClearSweeps('C2')
s.scope.scope.Average('C2', 100)
time.sleep(0.1)

s.laser.LaserSetFrequency(50e3)
s.laser.LaserSetDAC(290)
s.laser.LaserOn()

s.amp.AmpSet(50)
s.amp.AmpOn()

s.bias.SMURampVoltage(120)
s.bias.SMUOn()
print(f'Current: {s.bias.SMUCurrent()*1e6:.2f} uA')

for xx, X in enumerate(Xs):
    for yy, Y in enumerate(Ys):

        s.stage.MoveTo(x=X, y=Y, z=Z)

        wave = s.scope.AcquireAverage()

        # # Maximum Amplitude
        # data[xx, yy] = np.max(wave.y)

        # Integral of pulse
        sel = wave.x >= 0
        offset = np.mean(wave.y[wave.x < 0])
        amplitude = wave.y[sel] - offset
        data[xx, yy] = np.trapz(amplitude, wave.x[sel])


        print(f'{X}\t{Y}\t{Z}\t{data[xx, yy]}')

s.Off()


fig = plt.imshow(data.T, extent=[min(Xs),max(Xs),min(Ys),max(Ys)], origin="lower") #, norm=matplotlib.colors.LogNorm())

plt.xlabel('X-Position [mm]')
plt.ylabel('Y-Position [mm]')
plt.colorbar()
plt.show()
