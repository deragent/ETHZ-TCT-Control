import numpy as np
import pandas as pd

import yaml
import datetime
from pathlib import Path

def readSeparator(stream):
    line = stream.readline().strip()

    if line != '================':
        raise Exception('Expected separator [================]')

def readHeader(stream):
    header = [stream.readline().strip() for ll in range(2)]

    if header[0] != 'SSD measurement file' or header[1] != 'version: 1.4':
        raise Exception(f'Unknown header found: {str(header)}')

def readSampleParam(stream, param):
    name = stream.readline().strip()

    if name != f':{param}':
        raise Exception(f'Unexpected parameter [{name}], expecting [{param}]!')

    if param.startswith('Irradiation') or param.startswith('Annealing_history'):
        return ''

    value = stream.readline().strip()

    return value

def readSetupParam(stream, param):
    line = stream.readline().strip()

    name, value = line.split(':', 2)

    if name != param:
        raise Exception(f'Unexpected parameter [{name}], expecting [{param}]!')

    return value.strip()

def readVector(stream, param):
    data = {}

    for aspect in [f'{param}Min', f'{param}Max', f'delta{param}', f'n{param}', f'{param}Vector']:
        name, value = stream.readline().strip().split(':', 2)

        if name.strip() != aspect:
            raise Exception(f'Unexpected vector aspect [{name}], expecting [{aspect}]')

        data[aspect] = value.strip()

    N = int(data[f'n{param}'])
    values = np.array(data[f'{param}Vector'].split(' '), dtype=np.float64)

    if len(values) != N:
        raise Exception(f'Unexpected number of vector values [{len(values)}] for vector [{param}], expecting [{N}] values!')

    return values



if __name__ == "__main__":

    import argparse

    from tct.logger import Logger
    from tct.data import DataDir
    from tct.config.ConfigFile import ConfigMemory

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Utility to import a CERN-SSD-TPA data file (version 1.4).')
    parser.add_argument('input',
                        help='The TPA data file to be imported!')

    parser.add_argument('--data', '-D', default='./_data',
                        help='The directory where the scan data will be placed. Will be created if not existing! Default: [./_data]')

    parser.add_argument('--no-save', dest='write_data', action='store_false',
                        help='Do not write out any data. This allows to verify the correct loading of a TPA data file.')

    parser.add_argument('--name',
                        help='Store the imported data with the given dataset name.')

    parser.add_argument('--side', default='NA',
                        help='Sets the side attribute of the used sample.')
    parser.add_argument('--description', default=None,
                        help='Adds additonal description data.')

    args = parser.parse_args()


    FILE = Path(args.input)

    datadir = DataDir(args.data)
    log = Logger([datadir.global_log], print=True, debug=False)

    with open(FILE, 'r') as stream:

        log.log('TPA-IMPORT', f'Openend file [{FILE}] for import.')

        readSeparator(stream)
        readHeader(stream)
        readSeparator(stream)


        ## Read the parameters from the sample
        # This is hard-coded, especially to the scans taken in August 2022!
        sample_parameter_names = [
            'Sample', 'Producer', 'Run', 'Wafer',
            'TREC', 'Area[cm-2]', 'Thickness[um]', 'Support_Wafer_Thickness[um]', 'Resistivity[ohm.cm]',
            'Sample_comment', 'Material',
            'Irradiation(Location,Fluence/Dose,Units,Particle,Date)', 'Annealing_history(time[min],Temp[C],Date)'
        ]

        sample_parameters = {}

        for name in sample_parameter_names:
            sample_parameters[name] = readSampleParam(stream, name)

        ## Read the parameters of the setup
        # This is hard-coded, especially to the scans taken in August 2022!
        setup_parameter_names = [
            'COOLING', 'HVPS', 'STAGES',
            None, None, None, None, None, None, # Represent the coordinate transform lines!
            'LASER', 'repFrequ', 'lambdaLaser', 'LVPS',
            'numOfAvge', 'RecordLength', 'SamplingPeriod[s]',
            'scanType', 'startTime', 'user', 'comment',
            'ampGain', 'ShutterAperture', 'biasTeeResistance', 'numOfScans', 'repetitions'
        ]

        setup_parameters = {}

        for name in setup_parameter_names:
            if name is None:
                stream.readline()
            else:
                setup_parameters[name] = readSetupParam(stream, name)


        ## Read the scanned vector values
        # This is hard-coded, especially to the scans taken in August 2022!
        vector_names = [
            'Temperature', 'Voltage',
            'X', 'Y', 'Z',
            'U', 'V', 'W'
        ]

        vectors = {}

        for name in vector_names:
            vectors[name] = readVector(stream, name)


        ## Check of number of scans is consitent
        NScan = int(setup_parameters['numOfScans'])
        NVector = np.prod([len(v) for v in vectors.values()])
        if NScan != NVector:
            raise Exception(f'\'numberOfScans\' [{NScan}] does not agree with multiplied vector space [{NVector}]!')

        NRecord = int(setup_parameters['RecordLength'])

        log.log('TPA-IMPORT', f'File contains {NScan} scans.')
        log.log('TPA-IMPORT', f'Record length is {NRecord} samples.')

        ## Read the state header
        readSeparator(stream)
        state_names = stream.readline().strip().split(' ')
        readSeparator(stream)


        ## Save the current position, so we can return here for the second data pass
        start_of_data = stream.tell()

        ## Read the state vectors
        # In order to get the states we want the following rows: 0, 3, 6, 9 etc.
        state_data = pd.read_csv(stream, delimiter=' ', header=None, names=state_names, skiprows=lambda row: (row % 3 != 0))

        if len(state_data.index) != NScan:
            raise Exception(f'Expected [{NScan}] scan points, only [{len(state_data.index)}] state rows were found!')


        ## Read the data vectors
        stream.seek(start_of_data)
        scan_data = pd.read_csv(stream, delimiter=' ', header=None, skiprows=lambda row: (row % 3 == 0), names=list(range(0, NRecord+1)), usecols=lambda col: (col < NRecord))

        if len(scan_data.index) != 2*NScan:
            raise Exception(f'Expected [{NScan}] scan points, only [{len(state_data.index)/2}] data rows were found!')

        log.log('TPA-IMPORT', f'Data file loaded succesfully.')

    start_time = datetime.datetime.strptime(setup_parameters['startTime'], '%Y_%m_%d_%H_%M_%S')

    dataset_name = FILE.stem
    if args.name is not None:
        dataset_name = args.name

    ## Create the Info data structure
    info = {
        'aperture': '-',
        'description':
            'CERN-TPA: '+ setup_parameters['comment']
            + (f'-- {args.description}' if args.description is not None else ''),
        'laser': 'CERN-TPA 1550nm',
        'name': dataset_name,
        'operator': setup_parameters['user'],
        # Hard coded for the CERN TPA measurements in August 2022
        'sample': sample_parameters['Sample'].split('_')[1],
        'wafer': sample_parameters['Sample'].split('_')[0],
        'side': args.side,
    }


    ## Create the Config data structure
    # For now just reference the CERN setup
    config = ConfigMemory({
        'meta': info,
        'extern': 'CERN-TPA',
        'scan': [{param: vectors[param].tolist()} for param in vectors],
    })


    if args.write_data:

        # Create a new scan with given name and start-time
        scan = datadir.createScan(dataset_name, start_time)

        log.log('TPA-IMPORT', f'Write data to scan [{scan.entry}]')
        log.log('TPA-IMPORT', f'Folder: {scan.folder}')

        scan.writeMetaData(info)
        scan.saveConfig(config)

        # Calculate Time Vector
        # Use constant 6ns offset to give samples for automatic offset compensation!
        time = np.array(range(0, NRecord))*float(setup_parameters['SamplingPeriod[s]']) - 6e-9

        # Write the data
        for aa in range(NScan):
            state = {
                'time': (start_time + datetime.timedelta(seconds=state_data['timestamp'][aa]*1e-3)).isoformat(),
                'count': state_data['repetition'][aa],
                'scope.average': int(setup_parameters['numOfAvge']),
                'stage.x': state_data['x[mm]'][aa],
                'stage.y': state_data['y[mm]'][aa],
                'stage.z': state_data['z[mm]'][aa],
                'stage.u': state_data['u[deg]'][aa],
                'stage.v': state_data['v[deg]'][aa],
                'stage.w': state_data['w[deg]'][aa],
                'laser.frequency': float(setup_parameters['repFrequ']),
                'laser.state': setup_parameters['LASER'] == 'ON',
                'bias.hv': state_data['Vset[V]'][aa],
                'bias.state': setup_parameters['HVPS'] == 'ON',
                'bias.current': state_data['I[mA]'][aa]*1e-3,
                'temp.holder.temperature': state_data['PCB_T[C]'][aa],
                'steup.hostname': 'CERN-SSD-TPA',
            }

            data_file = scan.addEntry(state)
            data_file.storeMetaData(state)

            data_file.storeCurve(time, scan_data.loc[aa*2, :])
            data_file.storeCurve(time, scan_data.loc[aa*2 + 1, :])
            data_file.close()

        scan.writeList()

        log.log('TPA-IMPORT', f'{NScan} scans written succesfully.')
        log.log('TPA-IMPORT', 'Import complete!')
