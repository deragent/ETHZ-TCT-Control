## (Recursive) Merge of dict
# Mainly used to unite multiple config files.
def mergeDict(base, tomerge):
    # We use dict here as a sort of sorted-set
    key_dict = dict.fromkeys(base.keys(), None)
    for other in tomerge:
        key_dict.update(dict.fromkeys(other.keys(), None))

    keys = key_dict.keys()

    output = {}
    for key in keys:
        same = True
        all_dict = type(base.get(key)) is dict

        for other in tomerge:
            if base.get(key) != other.get(key):
                same = False
            if type(other.get(key)) is not dict:
                all_dict = False

        if same:
            output[key] = base.get(key)
        else:
            if all_dict:
                # If all entries are dicts we merge recursively
                output[key] = mergeDict(base[key], [other[key] for other in tomerge])
            else:
                # Otherwise we just append the key multiple times
                output[key] = base.get(key)
                for oo, other in enumerate(tomerge):
                    output[f'{key}-concat[{oo+1}]'] = other[key]

    return output


if __name__ == "__main__":

    import prompt_toolkit as pt

    import pandas as pd

    import argparse
    import sys, os
    import shutil
    import tempfile

    from tct.logger import Logger
    from tct.config.ConfigFile import ConfigMemory
    from tct.data import DataDir
    import analysis.data

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Utility to merge / concatenate multiple datasets.')
    parser.add_argument('base_dataset',
                        help='The first dataset to be appended to.')
    parser.add_argument('append_dataset', nargs='+',
                        help='The datasets to be appended.')

    parser.add_argument('--data', '-D', default='./_data',
                        help='The directory where the scan data will be placed. Will be created if not existing! Default: [./_data]')

    args = parser.parse_args()

    datadir = DataDir(args.data)
    _, temp_log = tempfile.mkstemp(text=True)
    log = Logger([datadir.global_log, temp_log], print=True, debug=False)

    base_data = analysis.data.Scan(args.base_dataset)
    append_data = [analysis.data.Scan(append) for append in args.append_dataset]

    log.log('DATASET-MERGE', f'Concatenating the following datasets:')
    for scan in [base_data] + append_data:
        log.log('DATASET-MERGE', f'\t- [{scan.entry}]')


    # Check if all scans have data
    for scan in [base_data] + append_data:
        if len(scan.list().index) == 0:
            log.log('DATASET-MERGE', f'Dataset [{scan.entry}] has not entries!')
            log.log('DATASET-MERGE', f'Abort!')

            sys.exit(-1)

    # Check if the scans are compatible
    base_columns = base_data.list().columns
    for scan in append_data:
        scan_columns = scan.list().columns
        if not base_columns.equals(scan_columns):
            log.log('DATASET-MERGE', f'Dataset [{base_data.entry}] is not compatible with [{scan.entry}]!')
            log.log('DATASET-MERGE', f'Not in [{base_data.entry}]: {scan_columns.difference(base_columns)}')
            log.log('DATASET-MERGE', f'Not in [{scan.entry}]: {base_columns.difference(scan_columns)}')
            log.log('DATASET-MERGE', f'Abort!')

            sys.exit(-1)


    # Create the new (merged) scan with the name and time of the first dataset
    output_scan = datadir.createScan('Concat:' + base_data.info()['name'], base_data.list()['time'].iloc[0])

    log.log('DATASET-MERGE', f'Write data to scan [{output_scan.entry}]')
    log.log('DATASET-MERGE', f'Folder: {output_scan.folder}')



    # Merge the info.yaml files
    base_info = base_data.info()
    append_info = [scan.info() for scan in append_data]

    concat_info = mergeDict(base_info, append_info)
    output_scan.writeMetaData(concat_info)

    log.log('DATASET-MERGE', f'Merged info data.')


    # Merge the config.yaml files
    base_config = base_data.config()
    append_config = [scan.config() for scan in append_data]

    concat_config = ConfigMemory(mergeDict(base_config, append_config))
    output_scan.saveConfig(concat_config)

    log.log('DATASET-MERGE', f'Merged config data.')


    # Merge the data
    total_entries = 0
    for scan in [base_data] + append_data:
        entries = len(scan.list().index)
        total_entries += entries
        log.log('DATASET-MERGE', f'[{scan.entry}]: {entries} entries')

    log.log('DATASET-MERGE', f'Found a total of {total_entries} scan points.')

    output_list = pd.DataFrame(columns=base_data.list().columns, index=range(0, total_entries))

    current_entry = 0
    for scan in [base_data] + append_data:
        log.log('DATASET-MERGE', f'Start copy of [{scan.entry}] data.')

        with pt.shortcuts.ProgressBar() as pb:
            for index, line in pb(scan.list().iterrows(), total=len(scan.list().index)):
                output_list.iloc[current_entry] = line

                prefix = f'A{current_entry}'
                output_list['_prefix'].iloc[current_entry] = prefix
                scan.get(index).copy(output_scan.data / prefix)

                current_entry += 1

    output_scan.writeList(output_list)


    log.log('DATASET-MERGE', 'Dataset concatenation done!')

    # Merge the logs
    # Close to log, so that it can also be copied
    log.close()

    with open(output_scan.folder / 'log.log', 'wb') as output_log:
        for scan in [base_data] + append_data:
            with open(scan.folder / 'log.log','rb') as input_log:
                shutil.copyfileobj(input_log, output_log)

        with open(temp_log, 'rb') as merge_log:
            shutil.copyfileobj(merge_log, output_log)

    # Remove the temporary log file
    os.remove(temp_log)



    # Prompt for manual post-processing tasks
    print('Please review the merged config and info files:')
    for file in ['config.yaml', 'info.yaml']:
        print(f'\t\t{output_scan.meta / file}')
    print()

    print('To generate the plots of the concatenated scan run:')
    print(f'\t\tpython -m util.analysis --save {output_scan.meta / "config.yaml"} {output_scan.folder}\n')
