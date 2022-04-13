# Inspired by: https://opensource.com/article/17/5/4-practical-python-libraries

import prompt_toolkit as pt
import argparse
import sys

import numpy as np

from tct.lab.control import *
from tct.logger import Logger


def printError(msg):
    pt.print_formatted_text(pt.HTML(f'<ansibrightred>ERROR: {msg}!</ansibrightred>'))
def printWarning(msg):
    pt.print_formatted_text(pt.HTML(f'<ansiyellow>WARNING: {msg}!</ansiyellow>'))


# Parse the command line arguments
parser = argparse.ArgumentParser(description='Command-Line Interface (CLI) for the TCT Setup')
parser.add_argument('--vlimit', '-V', type=float, required=True,
                    help='Voltage limit for the high-voltage PSU [V].')
parser.add_argument('--ilimit', '-I', type=float, required=True,
                    help='Current limit for the high-voltage PSU [mA].')

args = parser.parse_args()

if np.abs(args.vlimit) > 1000:
    printError('|V-Limit| must be smaller than 1kV!')
    sys.exit(-1)

if np.abs(args.ilimit) > 20:
    printError('|I-Limit| must be smaller than 20mA!')
    sys.exit(-1)


# Create a logger
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
    'off': None,
    'exit': None,
    'quit': None,
})

## Setup the environment
stage = StageControl(log = log)
laser = ParticularsLaserControl(log = log)
amp = ParticularsAmplifierControl(log = log)
bias = BiasSupplyControl(VLimit = args.vlimit, ILimit = args.ilimit*1e-3, log = log)


## TODO add status rprompt


def handleLaser(input):
    if input[0] in ['on']:
        laser.LaserOn()
    elif input[0] in ['off']:
        laser.LaserOff()
    elif input[0] in ['state']:
        print('= ', laser.LaserState())
    elif input[0] in ['dac']:
        if len(input) < 2:
            dac = laser.LaserGetDAC()
            if dac is not None:
                print(f'= {dac}')
            else:
                print('= NA')
        else:
            laser.LaserSetDAC(int(input[1]))
    elif input[0] in ['frequency', 'freq']:
        if len(input) < 2:
            freq = laser.LaserGetFrequency()
            if freq is not None:
                print(f'= {freq/1000:.2f} kHz')
            else:
                print('= NA')
        else:
            laser.LaserSetFrequency(int(float(input[1])))

def handleAmp(input):
    if input[0] in ['on']:
        amp.AmpOn()
    elif input[0] in ['off']:
        amp.AmpOff()
    elif input[0] in ['state']:
        print('= ', amp.AmpState())
    elif input[0] in ['gain']:
        if len(input) < 2:
            print(f'= {amp.AmpGet():.2f} %')
        else:
            amp.AmpSet(float(input[1]))

def handleBias(input):
    if input[0] in ['on']:
        bias.SMUOn()
    elif input[0] in ['off']:
        bias.SMUOff()
    elif input[0] in ['state']:
        print('= ', bias.SMUState())
    elif input[0] in ['current', 'curr', 'cur', 'c']:
        current = bias.SMUCurrent()
        if current is not None:
            print(f'= {current*1e6:.3f} uA')
        else:
            print('= NA')
    elif input[0] in ['voltage', 'volt', 'v']:
        if len(input) < 2:
            print(f'= {bias.SMUVoltage():.3f} V')
        else:
            bias.SMURampVoltage(float(input[1]))


def _parsePosition(input):
    pos = {}

    if len(input) < 2:
        printError('Missing arguments!')

    if input[0] in ['x', 'y', 'z']:
        pos[input[0]] = float(input[1])
    elif len(input) >= 3:
        pos['x'] = float(input[0])
        pos['y'] = float(input[1])
        pos['z'] = float(input[2])
    else:
        printError('Missing arguments!')

    return pos

def handleStage(input):
    if input[0] in ['home']:
        result = pt.shortcuts.yes_no_dialog(
            title='Stage Home',
            text='Do you want to execute stage home?'
        ).run()
        if result:
            stage.DoHome()

    elif input[0] in ['move']:
        delta = _parsePosition(input[1:])
        if delta is None:
            printError('Missing movement!')

        current = stage.Position()
        pos = {ax: delta[ax] + current[ax] for ax in delta}

        stage.MoveTo(**pos)

    elif input[0] in ['go', 'goto']:
        pos = _parsePosition(input[1:])
        if pos is None:
            printError('Missing position!')

        stage.MoveTo(**pos)

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
    pass # TODO



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
    elif commands[0] in ['off']:
        result = pt.shortcuts.yes_no_dialog(
            title='System Off',
            text='Do you want to turn all components off?'
        ).run()
        if result:
            laser.LaserOff()
            bias.SMUOff()
            amp.AmpOff()

        continue
    elif commands[0] in ['on']:
        if laser.LaserGetFrequency() is None:
            laser.LaserSetFrequency(50e3)
        if laser.LaserGetDAC() is None:
            laser.LaserSetDAC(290)
        laser.LaserOn()
        amp.AmpOn()
        bias.SMUOn()

        continue

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
