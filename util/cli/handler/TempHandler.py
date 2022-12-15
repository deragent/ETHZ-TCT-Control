from .CommandHandler import CommandHandler

from tct.lab.control import TemperatureControl

class TempHandler(CommandHandler):

    def __init__(self, log):
        super().__init__(log)

        self._temp = TemperatureControl(log=log)

    def commandDict(self):
        return {
            'stage': { 'temperature' },
            'holder': { 'temperature', 'humidity' },
            'state': None,
            'control': {
                'on',
                'off',
                'temperature',
                'state',
            }
        }

    def handle(self, input):
        if input[0] in['stage', 'holder'] and len(input) == 2:
            if input[0] in ['stage'] and input[1] in ['temp', 'temperature']:
                return self.Value(f'{self._temp.StageTemperature()}')

            elif input[0] in ['holder'] and input[1] in ['temp', 'temperature']:
                return self.Value(f'{self._temp.HolderTemperature()}')

            elif input[0] in ['holder'] and input[1] in ['hum', 'humidity']:
                return self.Value(f'{self._temp.HolderHumidity()}')

        elif input[0] in ['state']:
            return self.Text([
                f'Stage\tTemperature:\t{self._temp.StageTemperature():.2f}°C',
                f'Holder\tTemperature:\t{self._temp.HolderTemperature():.2f}°C',
                f'\tHumidity:\t{self._temp.HolderHumidity():.2f}%'
            ])

        elif input[0] in ['control']:
            return self.Warning('Not yet implemented!')
