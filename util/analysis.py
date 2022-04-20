import prompt_toolkit as pt
import argparse
import sys
import traceback

# Parse the command line arguments
parser = argparse.ArgumentParser(description='Utility to run analysis on a TCT scan.')
parser.add_argument('config',
                    help='The analysis config file. Can also be a scan config file, of which only the analysis section will be taken into account!')

parser.add_argument('scan',
                    help='Scan data directory.')
parser.add_argument('--output' '-O', default=None,
                    help='Ouptput directory, where the plots will be written. If not given, will be written to the scan data directory. Also see `--no-save`.')


parser.add_argument('--no-show', dest='show_plot', action='store_false',
                    help='Do not show the analysis plots at the end!')
parser.add_argument('--no-save', dest='save_plot', action='store_false',
                    help='Do not write the plots to the scan data directory.')

args = parser.parse_args()


import matplotlib.pyplot as plt

# Switch to display-les matplotlib backend if we do not show the plots
if not args.show_plot:
    plt.switch_backend('agg')


# Import TCT related classes
from tct.data import ScanDir
from tct.config import AnalysisFile

import analysis.data
import analysis.online


# Handle the input and output data structures
scanfile = ScanFile(args.config)

# TODO Load the Scan


# TODO review loggin
log.log('SCAN', 'Running online analysis.')

scandata = analysis.data.Scan()# TODO

for definition in scanfile.analysis:
    try:

        if definition.type == definition.TYPE_3D:
            plot = analysis.online.Plot3D(definition, scandata)
        elif definition.type == definition.TYPE_2D:
            plot = analysis.online.Plot2D(definition, scandata)
        else:
            log.log('SCAN', f'WARNING: Unexpected analysis type encountered [{definition.type}]')
            continue

        if args.save_plot:
            plot.save() # TODO also use args.output

        plot.generate()

    except KeyboardInterrupt:
        log.log('SCAN', f'WARNING: Received Ctrl+C!')
        break
    except:
        log.log('SCAN', f'ERROR: Exception during analysis [{definition.name()}]:\n{traceback.format_exc()}')

if args.show_plot
    plt.show()
