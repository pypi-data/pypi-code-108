
import numpy as np
import pandas as pd
import os
from pathlib import Path

def polylox_merge(location_files_in, sample_names, location_dir_out, file_name_out):

    print('Merging data ... ', end='', flush=True)

    # validate types and values of user input
    validate_user_input_merge(location_files_in, sample_names, location_dir_out, file_name_out)

    # create output folder if not exists
    create_outdir(location_dir_out)

    # collect and merge individual files to a merged dataframe
    df = collect_files(location_files_in, sample_names)

    # save dataframe as tab-separated values file (TSV, as .txt)
    df.to_csv(os.path.join(location_dir_out, file_name_out + '.txt'), sep='\t')

    print('Done')
    return df

def collect_files(location_files_in, sample_names):

    # loop over files and collect the individual dataframes
    df_all = list()
    for i in range(len(location_files_in)):
        df_all.append(read_single_file(location_files_in[i], sample_names[i]))

    # merging of the individual dataframes to one dataframe
    # (concat will create duplicate barcodes if they appear in multiple data sets;
    # hence we group by the same barcodes and sum up the double entries for each sample
    # (which is adding one value>0 with some other zeros from the initial NaNs))
    df_merged = pd.concat(df_all, ignore_index=True).fillna(0)
    df_merged = df_merged.groupby(df_merged['Barcode']).agg('sum').astype(int)

    # barcode rows are now sorted by total reads, starting with highest value
    df_merged['SumOfAllSamples'] = df_merged.sum(axis=1)
    df_merged.sort_values(by='SumOfAllSamples', ascending=False, inplace=True)
    df_merged.drop(columns=['SumOfAllSamples'], inplace=True)

    return df_merged

def read_single_file(location, sample_name):
    # read barcodes; checking that two first entries are 'total' and 'intact', then removing them
    pre_barcodes = np.loadtxt(location, usecols=0, delimiter='\t', dtype=str)
    if not np.all(pre_barcodes[0:2]==['total', 'intact']):
        raise ValueError('Provided barcode.count.txt file should start with \'total\', \'intact\' rows.')
    pre_barcodes = pre_barcodes[2:]

    # read the corresponding reads, skipping the removed 'total' and 'intact' rows
    pre_reads = np.loadtxt(location, usecols=1, skiprows=2, delimiter='\t', dtype=int)

    # create a pandas dataframe
    df = pd.DataFrame({'Barcode': pre_barcodes, sample_name: pre_reads})

    return df

def create_outdir(location_dir_out):
    # creates an output directory if it does not exist; e.g.
    # location_file_out = '/my/directory'
    Path(location_dir_out).mkdir(exist_ok=True)

def validate_user_input_merge(location_files_in, sample_names, location_dir_out, file_name_out):
    # check types for the input
    if not type(location_files_in)==list:
        raise TypeError('List of str expected for location_files_in.')
    if not all(type(e)==str for e in location_files_in):
        raise TypeError('List of str expected for location_files_in.')

    if not type(sample_names)==list:
        raise TypeError('List of str expected for sample_names.')
    if not all(type(e)==str for e in sample_names):
        raise TypeError('List of str expected for sample_names.')

    if not type(location_dir_out)==str:
        raise TypeError('Str expected for location_dir_out.')

    if not type(file_name_out)==str:
        raise TypeError('Str expected for file_name_out.')

    # check for same length of samples and location files
    if not len(location_files_in)==len(sample_names):
        raise ValueError('Same length expected for location_files_in and sample_names.')

    # check for reserved and unique sample_names
    if 'SumOfAllSamples' in sample_names:
        raise ValueError('\'SumOfAllSamples\' is a reserved column name.')
    if len(sample_names) > len(set(sample_names)):
        raise ValueError('Names in sample_names have to be unique.')
