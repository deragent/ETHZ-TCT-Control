import prompt_toolkit as pt
import argparse
import sys
import time
import traceback

import numpy as np
import matplotlib.pyplot as plt

# Parse the command line arguments
parser = argparse.ArgumentParser(description='Leakage scan utility for the TCT Setup')

parser.add_argument('--vlimit', '-V', type=float, required=True,
                    help='Voltage limit for the high-voltage PSU [V].')
parser.add_argument('--ilimit', '-I', type=float, required=True,
                    help='Current limit for the high-voltage PSU [mA].')

parser.add_argument('--measurements', '-M', default=1, type=int,
                    help='Number of leakage current measurements at each voltage.')

parser.add_argument('--scan-voltage', required=True, type=float,
                    help='Maximum voltage to scan.')
parser.add_argument('--scan-step', default=1, type=float,
                    help='Voltage step for the leakage scan.')

parser.add_argument('--output', '-O', required=True,
                    help='The file to output the leakage data to (as .csv).')

parser.add_argument('--quiet', dest='print', action='store_false',
                    help='Do not print any log messages to stdout!')
parser.add_argument('--no-confirm', '-N', dest='confirm', action='store_false',
                    help='Do not ask for any confirmation. Important for batch operation!')
parser.add_argument('--no-show', dest='show_plot', action='store_false',
                    help='Do not show the analysis plots at the end!')
parser.add_argument('--abort-on-error', action='store_true',
                    help='Abort the scan if an error occurs.')
parser.add_argument('--batch', '-B', action='store_true',
                    help='Combines --no-confirm, --abort-on-error and --no-show')

args = parser.parse_args()


import matplotlib.pyplot as plt

# Switch to displayles matplotlib backend if we do not show the plots
if not args.show_plot or args.batch:
    plt.switch_backend('agg')


# Import TCT related classes
from tct.system import Setup
from tct.logger import Logger


# Handle the input and output data structures
log = Logger(print=args.print)

if args.confirm and not args.batch:
    result = pt.shortcuts.yes_no_dialog(
        title='Confirm Voltage and Current Limits',
        text=f'Are the following limit settings corrent?\n\n    Voltage Limit: {args.vlimit:.2f} V\n\n    Current Limit: {args.ilimit:.3f} mA'
    ).run()

    if not result:
        log.log('SCAN', 'User input: Limits are not correct, aborting!')
        sys.exit(-1)


# Create the list of bias_voltages
bias_voltages = np.linspace(0.0, args.scan_voltage, int(args.scan_voltage/args.scan_step)+1)
leakage_current = np.zeros((len(bias_voltages), args.measurements))


# Create the setup and load the initial state
setup = Setup(vlimit = args.vlimit, ilimit = args.ilimit*1e-3, log=log)

setup.bias.SMURampVoltage(0)
setup.bias.SMUOn()

log.log('SCAN', 'Start leakage scan.')

aborted = False

for bb, bias in enumerate(bias_voltages):
    log.log('SCAN', f'Next Bias Voltage: {bias:.3f} V')

    try:
        setup.bias.SMURampVoltage(bias)

        for mm in range(args.measurements):
            time.sleep(0.1)
            leakage_current[bb, mm] = setup.bias.SMUCurrent()

    except KeyboardInterrupt:
        log.log('SCAN', f'WARNING: Received Ctrl+C!')
        aborted = True
        break
    except:
        log.log('SCAN', f'ERROR: Exception during scan:\n{traceback.format_exc()}')
        if args.abort_on_error or args.batch:
            aborted = True
            break

if aborted:
    log.log('SCAN', 'Aborting scan!')

log.log('SCAN', 'Finished the scan.')

# Handle end of state
log.log('SCAN', 'Applying end-state.')
setup.bias.SMURampVoltage(0)
setup.bias.SMUOff()

if aborted:
    sys.exit(-1)



if args.show_plot and not args.batch:
    log.log('SCAN', 'Running online analysis.')

    try:
        fig = plt.figure()
        plt.plot(bias_voltages, leakage_current*1e3, 'kx')

        plt.title('Measured Leakage Current')
        plt.xlabel('Bias Voltage [V]')
        plt.ylabel('Leakage Current [mA]')
        plt.grid()

        plt.show()

    except KeyboardInterrupt:
        log.log('SCAN', f'WARNING: Received Ctrl+C!')
    except:
        log.log('SCAN', f'ERROR: Exception during analysis [{definition.name()}]:\n{traceback.format_exc()}')


    plt.show()

result = True
if args.confirm and not args.batch:
    result = pt.shortcuts.yes_no_dialog(
        title='Save data of this run.',
        text='Do you want to keep the data acquired in this scan?'
    ).run()

if result:
    np.savetxt(args.output, np.hstack((bias_voltages[None].T, leakage_current)), delimiter=',', header='# Bias Voltage [V], Leakage Current [A]')
