import prompt_toolkit as pt
import argparse
import sys
import traceback

from tct.data import DataDir
from tct.config import ScanFile

from tct.system import Setup



# Parse the command line arguments
parser = argparse.ArgumentParser(description='Command-Line Interface (CLI) for the TCT Setup')
parser.add_argument('config',
                    help='The scan config file')

parser.add_argument('--data', '-D', default='./_data',
                    help='The directory where the scan data will be placed. Will be created if not existing!')

parser.add_argument('--quiet', dest='print', action='store_false',
                    help='Do not print any log messages to stdout!')
parser.add_argument('--no-confirm', '-N', dest='confirm', action='store_false',
                    help='Do not ask for any confirmation. Important for batch operation!')
parser.add_argument('--abort-on-error', action='store_true',
                    help='Abort the scan if an error occurs.')

args = parser.parse_args()

# Handle the input and output data structures
scanfile = ScanFile(args.config)
datadir = DataDir(args.data)

scandir = datadir.createScan(scanfile.meta['name'])

# Save the config and metadata file in the scan directory
scandir.saveConfig(scanfile)
scandir.writeMetaData(scanfile.meta)

log = scandir.logger(print=args.print)

if args.confirm:
    result = pt.shortcuts.yes_no_dialog(
        title='Confirm Voltage and Current Limits',
        text=f'Are the following limit settings corrent?\n\n    Voltage Limit: {scanfile.limits["vlimit"]:.2f} V\n\n    Current Limit: {scanfile.limits["ilimit"]*1e3:.3f} mA'
    ).run()

    if not result:
        log.log('SCAN', 'User input: Limits are not correct, aborting!')

        entry = scandir.entry
        del scandir
        datadir.trash(entry)

        sys.exit(-1)

# Create the setup and load the initial state
setup = Setup(vlimit = scanfile.limits['vlimit'], ilimit = scanfile.limits['ilimit'], log=log)
setup.FromState(scanfile.setup)

setup.amp.AmpOn()
setup.bias.SMUOn()
setup.laser.LaserOn()

# TODO: Handle Scope Setup

log.log('SCAN', 'Start scan.')

scan = scanfile.getScan()
for entry in scan:
    log.log('SCAN', f'Next entry: {entry}')

    try:
        setup.FromState(entry)

        # TODO extend for single acquisition
        wave = setup.scope.AcquireAverage()

        # Store the metadata and acquired curve
        state = setup.ToState()
        entry = scandir.addEntry(state)
        entry.storeMetaData(state)
        entry.storeCurve(wave.x, wave.y, metadata=setup.scope.WaveToMetadata(wave))
    except KeyboardInterrupt:
        log.log('SCAN', f'WARNING: Received Ctrl+C!')
        log.log('SCAN', 'Aboring scan!')
        break
    except:
        log.log('SCAN', f'ERROR: Exception during scan:\n{traceback.format_exc()}')
        if args.abort_on_error:
            log.log('SCAN', 'Aboring scan!')
            break


scandir.writeList()
log.log('SCAN', 'Finished the scan.')

# Handle end of state
log.log('SCAN', 'Applying end-state.')
if isinstance(scanfile.end, dict):
    setup.FromState(scanfile.end)
else:
    # By default we turn everything off
    setup.Off()


# TODO implement Analysis


if args.confirm:
    result = pt.shortcuts.yes_no_dialog(
        title='Save data of this run.',
        text='Do you want to keep the data acquired in this scan?'
    ).run()

    if not result:
        log.log('SCAN', 'User input: Discarding the measured data.')

        entry = scandir.entry
        del scandir
        trashed = datadir.trash(entry)
        log.log('SCAN', f'Moved data to [{trashed}]')
