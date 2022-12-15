from .CommandHandler import CommandHandler

import prompt_toolkit as pt

from tct.lab.control import StageControl

class StageHandler(CommandHandler):

    def __init__(self, log):
        super().__init__(log)

        self._stage = StageControl(log=log)

    def commandDict(self):
        return {
            'home': None,
            'move': {
                'x', 'y', 'z'
            },
            'goto': {
                'x', 'y', 'z'
            },
            'position': None,
            'state': None,
        }

    def _parsePosition(self, input):
        pos = {}

        if len(input) < 2:
            raise self.Exception('Missing arguments!')

        if input[0] in ['x', 'y', 'z']:
            pos[input[0]] = float(input[1])
        elif len(input) >= 3:
            pos['x'] = float(input[0])
            pos['y'] = float(input[1])
            pos['z'] = float(input[2])
        else:
            raise self.Exception('Missing arguments!')

        return pos

    def handle(self, input):
        try:
            if input[0] in ['home']:
                result = pt.shortcuts.yes_no_dialog(
                    title='Stage Home',
                    text='Do you want to execute stage home?'
                ).run()
                if result:
                    self._stage.DoHome()

            elif input[0] in ['move']:
                delta = self._parsePosition(input[1:])

                current = self._stage.Position()
                pos = {ax: delta[ax] + current[ax] for ax in delta}

                self._stage.MoveTo(**pos)

            elif input[0] in ['go', 'goto']:
                pos = self._parsePosition(input[1:])
                self._stage.MoveTo(**pos)

            elif input[0] in ['pos', 'position']:
                positions = self._stage.Position()
                return self.Text([
                    f'{ax.upper()}:    {pos}mm' for ax, pos in positions.items()
                ])

            elif input[0] in ['state']:
                state = self._stage.StageStatus()

                text = ["    {:>10}{:>17}{:>14}{:>13}{:>18}".format('Is Homed','Position [Step]','Current [mA]', 'Voltage [V]', 'Temperature [°C]')]
                for ax, d in state.items():
                    text.append("{}:  {:>10}{:17.2f}{:14.0f}{:13.3f}{:18.1f}".format(ax, d['is_homed'], d['step'], d['current']*1e3, d['voltage'], d['temperature']))

                return self.Text(text)

        except CommandHandler.Exception as e:
            return self.Error(str(e))
