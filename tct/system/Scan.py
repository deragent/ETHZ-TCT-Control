
class Scan():

    class Iterator():

        def __init__(self, scan):
            self._scan = scan

            self._index = {param: 0 for param in self._scan._parameters}
            self._valid = self._scan.count() > 0

        def __next__(self):
            if not self._valid:
                raise StopIteration

            result  = {}
            for param, idx in self._index.items():
                result[param] = self._scan._values[param][idx]

            for param in reversed(self._scan._parameters):
                if self._index[param]+1 < len(self._scan._values[param]):
                    self._index[param] += 1
                    break
                else:
                    self._index[param] = 0
            else:
                # We only get here if we did not break
                # Therefore we have reached the last element!
                self._valid = False

            return result

    def __init__(self):

        self._parameters = []
        self._values = {}

    def count(self):
        if len(self._parameters) == 0:
            return 0

        total = 1
        for param in self._parameters:
            total *= len(self._values[param])

        return total

    def addParameter(self, param, values):
        if param in self._parameters:
            raise Exception(f'Trying to add parameter [{param}] a second time to scan!')
        if len(values) < 1:
            raise Exception(f'No values specified for scan paramter [{param}]!')

        self._parameters.append(param)
        self._values[param] = values

    def __iter__(self):
        return Scan.Iterator(self)
