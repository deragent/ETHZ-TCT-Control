
class Scan():

    class Entry():

        def __init__(self, changed_param, state, manual=False, wait=None, autoscale=False):
            self._change = changed_param
            self._state = state
            self._manual = manual

            self._wait = wait
            if wait is None or wait < 0:
                self._wait = 0

            self._autoscale = autoscale

        def __str__(self):
            return str(self._state)

        def changedParameter(self):
            return self._change

        def state(self):
            return self._state

        def isManual(self):
            return self._manual

        def wait(self):
            return self._wait

        def isAutoScale(self):
            return self._autoscale

    class Iterator():

        def __init__(self, scan):
            self._scan = scan

            self._index = {param: 0 for param in self._scan._parameters}
            self._valid = self._scan.count() > 0

            self._last_change = None

        def __next__(self):
            if not self._valid:
                raise StopIteration

            result  = {}
            for param, idx in self._index.items():
                result[param] = self._scan._values[param][idx]

            # Handling of manually changed parameters and wait
            changed_param = self._last_change
            if changed_param is None:
                # Initial entry: check if any parameter is manual
                manual = any(self._scan._manual.values())
                autoscale = any(self._scan._autoscale.values())
                wait = 0
            else:
                manual = self._scan._manual[changed_param]
                autoscale = self._scan._autoscale[changed_param]
                wait = self._scan._wait[changed_param]

            for param in reversed(self._scan._parameters):
                if self._index[param]+1 < len(self._scan._values[param]):
                    self._index[param] += 1
                    self._last_change = param
                    break
                else:
                    self._index[param] = 0
            else:
                # We only get here if we did not break
                # Therefore we have reached the last element!
                self._valid = False

            return Scan.Entry(changed_param, result, manual, wait, autoscale)

    def __init__(self):

        self._parameters = []
        self._values = {}
        self._manual = {}
        self._wait = {}
        self._autoscale = {}

    def count(self):
        if len(self._parameters) == 0:
            return 0

        total = 1
        for param in self._parameters:
            total *= len(self._values[param])

        return total

    def addParameter(self, param, values, manual=False, wait=0, autoscale=False):
        if param in self._parameters:
            raise Exception(f'Trying to add parameter [{param}] a second time to scan!')
        if len(values) < 1:
            raise Exception(f'No values specified for scan paramter [{param}]!')

        self._parameters.append(param)
        self._values[param] = values
        self._manual[param] = manual
        self._wait[param] = float(wait)
        self._autoscale[param] = autoscale

    def __iter__(self):
        return Scan.Iterator(self)
