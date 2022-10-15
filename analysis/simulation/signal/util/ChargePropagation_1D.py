import pandas as pd
import numpy as np

from .signal import SignalExtensible

class ChargePropagation_1D():

    class Model():

        def Ew(self, x):
            raise NotImplementedError()

        def v(self, x, charge):
            raise NotImplementedError()


    def __init__(self):

        self.dt_min = 5e-12     # s
        self.dt_max = 100e-12   # s
        self.dx = 0.5e-6        # m

        self.x_range = (-503e-6, 0) # m

        self.t_end = 150e-9     # s
        self.t_pre = 20*self.dt_max  # s

        self.dt_report = 1000*self.dt_min # s

        self._model = None


    def setModel(self, model):
        self._model = model

    def run(self, charges, retEH=True):
        if not isinstance(self._model, ChargePropagation_1D.Model):
            raise Exception('No valid model set!')

        # Create the charge data DataFrame
        charge_data = pd.DataFrame([(x, q, 0.0) for x, q in charges], columns=['pos', 'q', 'v'])

        t_curr = 0
        t_report = 0


        e_signal = SignalExtensible()
        h_signal = SignalExtensible()
        # Add pre-trigger 0 start value
        if self.t_pre > self.dt_min:
            e_signal.add(-self.t_pre, 0)
            h_signal.add(-self.t_pre, 0)

        e_signal.add(-self.dt_min, 0)
        h_signal.add(-self.dt_min, 0)


        # Run the main simulation loop
        while t_curr <= self.t_end:
            # if self.dt_report > 0 and t_curr >= t_report + self.dt_report:
            #     print(f'{t_curr*1e9:.1f} ns:\t{e_signal.samples()} samples')
            #     t_report = t_curr

            # Calculate all veloities
            charge_data['v'] = self._model.v(charge_data['pos'], charge_data['q'])

            max_v = np.max(np.abs(charge_data['v']))

            # Stop the simulation when all charges stopped
            if max_v == 0:
                e_signal.add(t_curr, 0)
                h_signal.add(t_curr, 0)
                break

            # Calculate the time step
            # Note: This should be review, for partial time steps, when charges reach the boundaries!
            dt = self.dx / max_v
            if dt < self.dt_min:
                dt = self.dt_min
            if dt > self.dt_max:
                dt = self.dt_max

            # Calculate induced current
            Iind = charge_data['q']*charge_data['v']*self._model.Ew(charge_data['pos'])
            e_signal.add(t_curr, np.sum(Iind[charge_data['q'] < 0]))
            h_signal.add(t_curr, np.sum(Iind[charge_data['q'] > 0]))

            # Propagate all charges
            charge_data['pos'] = charge_data['pos'] + charge_data['v']*dt

            # Remove charges outside of boundaries
            outside = (charge_data['pos'] >= self.x_range[1]) | (charge_data['pos'] <= self.x_range[0])
            charge_data.loc[outside, 'v'] = 0
            charge_data.loc[outside, 'q'] = 0

            t_curr += dt


        # Add 0 end-point if necessary
        if t_curr < self.t_end:
            e_signal.add(self.t_end, 0)
            h_signal.add(self.t_end, 0)

        total = e_signal + h_signal

        if retEH:
            return total, e_signal, h_signal
        else:
            return total
