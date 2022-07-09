import prompt_toolkit as pt
import argparse
import sys
import time
import traceback

# Parse the command line arguments
parser = argparse.ArgumentParser(description='Command-Line Interface (CLI) for the TCT Setup')
parser.add_argument('config',
                    help='The scan config file')

parser.add_argument('--data', '-D', default='./_data',
                    help='The directory where the scan data will be placed. Will be created if not existing! Default: [./_data]')

parser.add_argument('--quiet', dest='print', action='store_false',
                    help='Do not print any log messages to stdout!')
parser.add_argument('--no-confirm', '-N', dest='confirm', action='store_false',
                    help='Do not ask for any confirmation. Important for batch operation!')
parser.add_argument('--no-show', dest='show_plot', action='store_false',
                    help='Do not show the analysis plots at the end!')
parser.add_argument('--abort-on-error', action='store_true',
                    help='Abort the scan if an error occurs.')
parser.add_argument('--ignore-manual', action='store_true',
                    help='Ignores any manual scan steps.')
parser.add_argument('--batch', '-B', action='store_true',
                    help='Combines --no-confirm, --abort-on-error, --no-show and --ignore-manual')

args = parser.parse_args()


import matplotlib.pyplot as plt

# Switch to displayles matplotlib backend if we do not show the plots
if not args.show_plot or args.batch:
    plt.switch_backend('agg')


# Import TCT related classes
from tct.data import DataDir
from tct.config import ScanFile
from tct.system import Setup


# Handle the input and output data structures
scanfile = ScanFile(args.config)
datadir = DataDir(args.data)

scandir = datadir.createScan(scanfile.meta['name'])

# Save the config and metadata file in the scan directory
scandir.saveConfig(scanfile)
scandir.writeMetaData(scanfile.meta)

log = scandir.logger(print=args.print)

if args.confirm and not args.batch:
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

aborted = False

run_entries = 0
run_time = 0

scan = scanfile.getScan()
total_entries = scan.count()
for ee, scan_entry in enumerate(scan):
    log.log('SCAN', f'Scan entry [{ee} of {total_entries}]: {scan_entry}')
    if run_entries > 0:
        time_left = (total_entries - (ee+1))*run_time/run_entries
        log.log('SCAN', f'Time remaining: {int(time_left/60):02}:{int(time_left%60):02}')
    time_start = time.time()

    # Handle change of manual parameters
    if scan_entry.isManual() and not args.ignore_manual and not args.batch:
        text = 'Initial step: Please adjust all manual paramters to their initial value!'
        changed_param = scan_entry.changedParameter()
        if changed_param is not None:
            text = f'Manual step: Please change [{changed_param}] to: {scan_entry.state()[changed_param]}!'

        result = pt.shortcuts.message_dialog(
            title='Manual Scan Step - Continue?',
            text=text
        ).run()

    try:
        setup.FromState(scan_entry.state())

        # Handle of wait (after state change)
        if scan_entry.wait() > 0:
            log.log('SCAN', f'Waiting for {scan_entry.wait()}s')
            time.sleep(scan_entry.wait())
            log.log('SCAN', f'Continue after wait.')

        # TODO extend for single acquisition
        wave = setup.scope.AcquireAverage()

        # Store the metadata and acquired curve
        state = setup.ToState()
        entry = scandir.addEntry(state)
        entry.storeMetaData(state)
        entry.storeCurve(wave.x, wave.y, metadata=setup.scope.WaveToMetadata(wave))
    except KeyboardInterrupt:
        log.log('SCAN', f'WARNING: Received Ctrl+C!')
        aborted = True
        break
    except:
        log.log('SCAN', f'ERROR: Exception during scan:\n{traceback.format_exc()}')
        if args.abort_on_error or args.batch:
            aborted = True
            break

    run_entries += 1
    run_time += time.time() - time_start

if aborted:
    log.log('SCAN', 'Aborting scan!')


scandir.writeList()
log.log('SCAN', 'Finished the scan.')
log.log('SCAN', f'Total time: {int(run_time/60):02}:{int(run_time%60):02}')

# Handle end of state
log.log('SCAN', 'Applying end-state.')
if isinstance(scanfile.end, dict):
    setup.FromState(scanfile.end)
else:
    # By default we turn everything off
    setup.Off()

if aborted:
    sys.exit(-1)



log.log('SCAN', f'Data in [{scandir.entry}]')
log.log('SCAN', f'Folder: {scandir.folder}')


if len(scanfile.analysis) > 0:
    log.log('SCAN', 'Running online analysis.')

    import analysis.data
    import analysis.online

    scandata = analysis.data.Scan(scandir.folder)

    for definition in scanfile.analysis:
        try:

            if definition.type == definition.TYPE_3D:
                plot = analysis.online.Plot3D(definition, scandata)
            elif definition.type == definition.TYPE_2D:
                plot = analysis.online.Plot2D(definition, scandata)
            else:
                log.log('SCAN', f'WARNING: Unexpected analysis type encountered [{definition.type}]')
                continue

            plot.save(scandir.plot)
            plot.generate()

        except KeyboardInterrupt:
            log.log('SCAN', f'WARNING: Received Ctrl+C!')
            break
        except:
            log.log('SCAN', f'ERROR: Exception during analysis [{definition.name()}]:\n{traceback.format_exc()}')

    if args.show_plot and not args.batch:
        plt.show()



if args.confirm and not args.batch:
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
