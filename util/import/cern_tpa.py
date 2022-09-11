from tct.data.output import FileHDF5

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

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



    FILE = Path("../Data/2022_08_19_13_59_21_P301401_E2.txt")


    with open(FILE, 'r') as stream:

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


    ## Create the Info data structure
    info = {
        'aperture': None,
        'description': 'CERN-TPA: '+ setup_parameters['comment'],
        'laser': 'CERN-TPA 1550nm',
        'name': FILE.stem,
        'operator': setup_parameters['user'],
        # Hard coded for the CERN TPA measurements in August 2022
        'sample': sample_parameters['Sample'].split('_')[1],
        'wafer': sample_parameters['Sample'].split('_')[0],
        # Need to manually set this!
        'side': 'TODO',
    }


    ## Create the Config data structure
    # For now just reference the CERN setup
    config = {
        'meta': info,
        'extern': 'CERN-TPA',
        'scan': [{param: vectors[param].tolist()} for param in vectors],
    }

    ## Create the list data
    start_time = datetime.datetime.strptime(setup_parameters['startTime'], '%Y_%m_%d_%H_%M_%S')

    list = {
        '_prefix': [f'A{n}' for n in range(NScan)],
        '_type': ['hdf5' for n in range(NScan)],
        'time': [start_time + datetime.timedelta(seconds=offset*1e-3) for offset in state_data['timestamp']],
        'count': state_data['repetition'],
        'scope.average': [int(setup_parameters['numOfAvge']) for n in range(NScan)],
        'stage.x': state_data['x[mm]'],
        'stage.y': state_data['y[mm]'],
        'stage.z': state_data['z[mm]'],
        'stage.u': state_data['u[deg]'],
        'stage.v': state_data['v[deg]'],
        'stage.w': state_data['w[deg]'],
        'laser.frequency': [float(setup_parameters['repFrequ']) for n in range(NScan)],
        'laser.state': [setup_parameters['LASER'] == 'ON' for n in range(NScan)],
        'bias.hv': state_data['Vset[V]'],
        'bias.state': [setup_parameters['HVPS'] == 'ON' for n in range(NScan)],
        'bias.current': state_data['I[mA]']*1e-3,
        'temp.holder.temperature': state_data['PCB_T[C]'],
        'steup.hostname': ['CERN-SSD-TPA' for n in range(NScan)],
    }

    list_df = pd.DataFrame(list)


    ## Store all the data into files
    output_dir = Path(f'output/{FILE.stem}')
    output_dir.mkdir(parents=True, exist_ok=True)

    meta_dir = (output_dir / 'meta')
    plot_dir = (output_dir / 'plot')
    data_dir = (output_dir / 'data')

    for dir in [meta_dir, plot_dir, data_dir]:
        dir.mkdir(exist_ok=True)

    # Write Meta-Data
    with  (meta_dir / 'info.yaml').open('w') as out:
        out.write(yaml.dump(info))

    with  (meta_dir / 'config.yaml').open('w') as out:
        out.write(yaml.dump(config))

    list_df.to_csv(meta_dir / 'list.csv')


    # Write the Data
    time = np.array(range(0, NRecord))*float(setup_parameters['SamplingPeriod[s]'])

    for aa in range(NScan):
        data_file = FileHDF5(data_dir / f'A{aa}')
        data_file.storeCurve(time, scan_data.loc[aa*2, :])
        data_file.storeCurve(time, scan_data.loc[aa*2 + 1, :])
        data_file.close()
