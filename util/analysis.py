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
parser.add_argument('--output', '-O', default=None,
                    help='Ouptput directory, where the plots will be written. If not given, will be written to the scan data directory. Also see `--save`.')

parser.add_argument('--save', dest='save_plot', action='store_true',
                    help='Write the plots to the given output directory.')

parser.add_argument('--no-show', dest='show_plot', action='store_false',
                    help='Do not show the analysis plots at the end!')

args = parser.parse_args()


import matplotlib.pyplot as plt

# Switch to display-les matplotlib backend if we do not show the plots
if not args.show_plot:
    plt.switch_backend('agg')


# Import TCT related classes
from tct.config import AnalysisFile
from tct.logger import Logger

import analysis.data
import analysis.online


# Handle the input and output data structures
analysisfile = AnalysisFile(args.config)

log = Logger(print=True, debug=False)
log.log('ANALYSIS', 'Running online analysis.')

scandata = analysis.data.Scan(args.scan)

output_dir = scandata.plot
if args.output is not None:
    output_dir = args.output

for definition in analysisfile.analysis:
    try:

        if definition.type == definition.TYPE_3D:
            plot = analysis.online.Plot3D(definition, scandata)
        elif definition.type == definition.TYPE_2D:
            plot = analysis.online.Plot2D(definition, scandata)
        else:
            log.log('ANALYSIS', f'WARNING: Unexpected analysis type encountered [{definition.type}]')
            continue

        if args.save_plot:
            plot.save(output_dir)

        plot.generate()

    except KeyboardInterrupt:
        log.log('ANALYSIS', f'WARNING: Received Ctrl+C!')
        break
    except:
        log.log('ANALYSIS', f'ERROR: Exception during analysis [{definition.name()}]:\n{traceback.format_exc()}')

if args.show_plot:
    plt.show()
