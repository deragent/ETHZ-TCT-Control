import yaml
import shutil

from .Definition import KEY_MAP

class ConfigFile():

    class ConfigError(Exception):
        def __init__(self, config, msg=None):
            self.file = config._file
            self.msg = msg

        def __str__(self):
            msg = ''
            if self.msg is not None:
                msg = f': {self.msg}'

            return f'Config Error [{self.file}]{msg}'

    class MissingError(ConfigError):
        def __init__(self, config, key):
            super().__init__(config)

            if isinstance(key, list):
                self.keys = key
            else:
                self.keys = [key]

            self.msg = f'Missing key [{".".join(self.keys)}]!'


    def __init__(self, file):
        self._file = file
        self._data = {}

        self._read()

    def _read(self):
        with open(self._file, 'r') as stream:
            self._data = yaml.safe_load(stream)

    def write(self, file):
        with open(file, 'w') as stream:
            yaml.dump(self._data, stream)

    def copy(self, file):
        return shutil.copy(self._file, file)


    def _get(self, keys, required=False):
        if not isinstance(keys, list):
            keys = [keys]

        root = self._data
        for kk, key in enumerate(keys):
            if key not in root:
                if required:
                    raise ConfigFile.MissingError(self, keys[:kk+1])
                else:
                    return None

            root = root[key]

        return root


    def translate(self, key, strict=True):
        if key not in KEY_MAP:
            if strict:
                raise ConfigFile.ConfigError(self, f'Key [{key}] is not valid!')
            else:
                return key

        return KEY_MAP[key]


class ConfigMemory(ConfigFile):

    def __init__(self, data):
        self._file = None
        self._data = data

    def copy(self, file):
        return self.write(file)
