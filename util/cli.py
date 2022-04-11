import prompt_toolkit as pt

from tct.lab.control import StageControl

from tct.logger import Logger
log = Logger('.tct_cli.log', print=True, debug=False)

command_completer = pt.completion.NestedCompleter.from_nested_dict({
    'laser': {
        'on': None,
        'off': None,
        'dac': None,
        'frequency': None,
        'state': None,
    },
    'amp': {
        'on': None,
        'off': None,
        'gain': None,
        'state': None,
    },
    'bias': {
        'on': None,
        'off': None,
        'voltage': None,
        'current': None,
        'state': None,
    },
    'stage': {
        'home': None,
        'move': {
            'x', 'y', 'z'
        },
        'goto': {
            'x', 'y', 'z'
        },
        'position': None,
        'state': None,
    },
    'exit': None,
    'quit': None,
})

def printError(msg):
    pt.print_formatted_text(pt.HTML(f'<ansibrightred>ERROR: {msg}!</ansibrightred>'))
def printWarning(msg):
    pt.print_formatted_text(pt.HTML(f'<ansiyellow>WARNING: {msg}!</ansiyellow>'))


## TODO parse command line arguments
## - safe mode
## - HV bias limits

## TODO setup the environment
stage = StageControl(log = log)


## TODO add status rprompt


def handleLaser(input):
    pass

def handleAmp(input):
    pass

def handleBias(input):
    pass

def handleStage(input):
    if input[0] in ['home']:
        result = pt.shortcuts.yes_no_dialog(
            title='Stage Home',
            text='Do you want to execute stage home?'
        ).run()
        if result:
            stage.DoHome()

    elif input[0] in ['move']:
        pass # TODO

    elif input[0] in ['go', 'goto']:
        pass # TODO

    elif input[0] in ['pos', 'position']:
        positions = stage.Position()
        for ax, pos in positions.items():
            print(f'{ax.upper()}:    {pos}mm')

    elif input[0] in ['state']:
        state = stage.StageStatus()

        print ("    {:>10}{:>17}{:>14}{:>13}{:>18}".format('Is Homed','Position [Step]','Current [mA]', 'Voltage [V]', 'Temperature [°C]'))
        for ax, d in state.items():
            print ("{}:  {:>10}{:17.2f}{:14.0f}{:13.3f}{:18.1f}".format(ax, d['is_homed'], d['step'], d['current']*1e3, d['voltage'], d['temperature']))


def handleScope(input):
    pass



# Run the main prompt
while 1:
    try:
        user_input = pt.prompt('TCT > ',
            history = pt.history.FileHistory('.tct_history'),
            auto_suggest = pt.auto_suggest.AutoSuggestFromHistory(),
            completer = command_completer
        )
    except KeyboardInterrupt as e:
        break

    commands = user_input.lower().split(' ')

    if len(commands) < 1:
        continue

    if commands[0] in ['quit', 'exit']:
        break

    if len(commands) < 2:
        printError('Missing arguments!')
        continue

    if commands[0] in ['laser']:
        handleLaser(commands[1:])
    elif commands[0] in ['amp', 'amplifier']:
        handleAmp(commands[1:])
    elif commands[0] in ['bias']:
        handleBias(commands[1:])
    elif commands[0] in ['stage']:
        handleStage(commands[1:])
    elif commands[0] in ['scope']:
        handleScope(commands[1:])

## TODO handle safe shutdown if wanted
