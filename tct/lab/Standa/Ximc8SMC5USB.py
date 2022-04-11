import ctypes

from . import pyximc

class Ximc8SMC5USB():

    class XimcError(Exception):

        def __init__(self, iface, msg):
            self.iface = iface
            self.msg = msg

        def __str__(self):
            base = "%s [%i]: %s"%(type(self.iface).__name__, self.iface.serial_nr, self.msg)
            return base

    def __init__(self, serial, log=None, usteps=256):
        self.id = None
        self.serial_nr = serial
        self.usteps = usteps

        self._log = log

        self._open(serial)

    def __del__(self):
        self._close()

    def log(self, cat, msg):
        if self._log is not None:
            self._log.log(cat, msg)

    def _open(self, serial):
        if self.id is None:
            hex_id = serial.to_bytes(4, 'big').hex().upper()
            dev_str = f'xi-com:/dev/ximc/{hex_id}'.encode()

            id = pyximc.lib.open_device(dev_str)

            if id < 0:
                self.log('Ximc8SMC5USB', f'Error: Could not open driver under [{dev_str}]')
                raise Ximc8SMC5USB.XimcError(self, f'Could not open driver under [{dev_str}]')

            self.id = id

    def _close(self):
        if self.id is not None:
            pyximc.lib.close_device(ctypes.byref(
                ctypes.cast(self.id, ctypes.POINTER(ctypes.c_int))
            ))

    def _getStatus(self):
        status = pyximc.status_t()
        res = pyximc.lib.get_status(self.id, ctypes.byref(status))

        return status

    def status(self):
        status = self._getStatus()

        data = {
            'home': (status.Flags & pyximc.StateFlags.STATE_IS_HOMED > 0),
            'position': status.CurPosition + status.uCurPosition / self.usteps,
            'current': status.Ipwr*1e-3,
            'voltage': status.Upwr*1e-3,
            'temperature': status.CurT*1e-1,
        }

        return data

    def home(self):
        status = self._getStatus()

        if status.Flags & pyximc.StateFlags.STATE_IS_HOMED:
            return True
        else:
            return False

    def doHome(self, blocking=False):
        res = pyximc.lib.command_home(self.id)

        if blocking:
            return self.waitForStop()

        return True

    def doZero(self):
        res = pyximc.lib.command_zero(self.id)

        return True


    def moveTo(self, position, blocking=False):
        steps = int(position)
        usteps = int((position - steps)*self.usteps)

        res = pyximc.lib.command_move(self.id, steps, usteps)

        if blocking:
            return self.waitForStop()

        return True

    def position(self):
        pos = pyximc.get_position_t()
        res = pyximc.lib.get_position(self.id, ctypes.byref(pos))

        position = pos.Position + pos.uPosition / self.usteps

        return position


    def waitForStop(self):
        res = pyximc.lib.command_wait_for_stop(self.id, 50)
        return True
