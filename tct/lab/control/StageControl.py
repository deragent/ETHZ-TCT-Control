import time

from ..Standa import Ximc8SMC5USB

class StageControl():
    """Controls the Particulars X-Y-Z Standa Stage

    - All positions in mm"""

    AXIS = ['x', 'y', 'z']

    # Movement limits for each axis (in mm)
    DEFAULT_LIMITS = {
        'x': [-45, 45],
        'y': [-45, 45],
        'z': [0, 95]
    }

    # Position of the center from home (in mm)
    ZERO_FROM_HOME = {
        'x': 50,
        'y': 50,
        'z': 0
    }

    KEY_MAP = {
        'x': 'stage.x',
        'y': 'stage.y',
        'z': 'stage.focus',
    }

    # mm/step
    MMPERSTEP = 2.5e-3

    def MM2STEPS(pos):
        return pos/StageControl.MMPERSTEP

    def STEPS2MM(steps):
        return steps*StageControl.MMPERSTEP


    def __init__(self, serials={'x': 30086, 'y': 30084, 'z': 30031}, log=None, limits=None):

        self.stages = {ax: None for ax in StageControl.AXIS}
        for ax in StageControl.AXIS:
            self.stages[ax] = Ximc8SMC5USB(serials[ax], log=log)

        if limits is None:
            self.limits = StageControl.DEFAULT_LIMITS
        else:
            self.limits = limits

        self._log = log

        self._valid = True
        self.check()

    def __del__(self):
        for ax, stage in self.stages.items():
            if stage is not None:
                del stage
                self.stages[ax] = None

    def log(self, cat, msg):
        if self._log is not None:
            self._log.log(cat, msg)

    def _logMoveTo(self, targets):
        self.log('StageControl', 'Moved to %s'%(' and '.join([f'{ax} = {value}mm' for ax, value in targets.items()])))

    def check(self):
        for ax, stage in self.stages.items():
            if not stage.home():
                self._valid = False
                self.log('StageControl', f'WARNING: Axis [{ax}] has not been home!')

    def IsValid(self):
        return self._valid


    def ToState(self, state={}):
        pos = self.Position()
        for ax, value in pos.items():
            state[StageControl.KEY_MAP[ax]] = value

        for ax, stage in self.stages.items():
            status = stage.status()
            for key, value in status.items():
                state[f'stage.status.{ax}.{key}'] = value

        return state

    def FromState(self, state):
        pos = {}
        for ax, key in StageControl.KEY_MAP.items():
            if key in state:
                pos[ax] = float(state[key])
        self.MoveTo(**pos)


    def _moveTo(self, ax, pos, blocking=False, nolimit=False):
        if not nolimit:
            lim = self.limits[ax]
            if pos < lim[0] or pos > lim[1]:
                self.log('StageControl', f'WARNING: Target [{pos}mm] of axis [{ax}] out of bounds [{lim[0]}mm, {lim[1]}mm]')
                return False

        return self.stages[ax].moveTo(StageControl.MM2STEPS(pos), blocking)

    def _waitForStop(self):
        for ax, stage in self.stages.items():
            stage.waitForStop()

        return True


    def DoHome(self):
        self.log('StageControl', f'Start home sequence.')

        for ax, stage in self.stages.items():
            stage.doHome(blocking=False)

        self._waitForStop()
        time.sleep(1)

        for ax, stage in self.stages.items():
            stage.doZero()
        time.sleep(1)

        self.log('StageControl', f'Moved to home position.')

        for ax, stage in self.stages.items():
            if not stage.home():
                # TODO treat error, probably raise an exception here!
                return False

        for ax, stage in self.stages.items():
            # As this is the movement from the home position to the new zero, limits do not apply!
            self._moveTo(ax, StageControl.ZERO_FROM_HOME[ax], blocking=False, nolimit=True)

        self._waitForStop()

        for ax, stage in self.stages.items():
            stage.doZero()

        self.log('StageControl', f'Moved to zero / center position.')

    def PositionMoveTo(self, x=None, y=None):
        if x is None and y is None:
            return True

        targets = {}
        if x is not None:
            self._moveTo('x', x, blocking=False)
            targets['X'] = x
        if y is not None:
            self._moveTo('y', y, blocking=False)
            targets['X'] = x

        ret = self._waitForStop()

        self._logMoveTo(targets)
        return ret

    def FocusMoveTo(self, z):
        targets = {'Z': z}
        ret = self._moveTo('z', z, blocking=True)

        self._logMoveTo(targets)
        return ret

    def MoveTo(self, x=None, y=None, z=None):
        if x is None and y is None and z is None:
            return True

        targets = {}
        if x is not None:
            self._moveTo('x', x, blocking=False)
            targets['X'] = x
        if y is not None:
            self._moveTo('y', y, blocking=False)
            targets['Y'] = y
        if z is not None:
            self._moveTo('z', z, blocking=False)
            targets['Z'] = z

        ret = self._waitForStop()

        self._logMoveTo(targets)
        return ret

    def Position(self):
        data = {}
        for ax, stage in self.stages.items():
            data[ax] = StageControl.STEPS2MM(stage.position())

        return data

    def StageStatus(self):
        data = {}
        for ax, stage in self.stages.items():
            data[ax] = stage.status()

        return data
