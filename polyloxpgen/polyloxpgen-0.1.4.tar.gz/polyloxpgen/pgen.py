
import numpy as np
import pandas as pd
import zipfile
import os
from pathlib import Path
from .merge import create_outdir

def polylox_pgen(location_file_in, pgen_location_dir_out, pgen_file_name_out,
                                path_matrix_type='uniform',
                                decimal_float='.'):

    print('Loading input data ... ', end='', flush=True)
    # validate types and values of user input
    validate_user_input_pgen(location_file_in, pgen_location_dir_out, pgen_file_name_out)

    # load and validate input dataframe
    df_in = pd.read_csv(location_file_in, sep='\t', index_col=0)
    validate_user_input_dataframe(df_in)

    # extract pre_barcodes and pre_reads (unpurged data) from df_in
    pre_barcodes, pre_reads, sample_names = get_pre_data(df_in)
    print('Done')

    print('Loading Polylox libraries ... ', end='', flush=True)
    barcodelib, minrecs, path_matrix = load_libraries(path_matrix_type=path_matrix_type)
    print('Done')

    print('Purging barcodes and reads ... ', end='', flush=True)
    purged_barcodes, purged_reads = purge(pre_barcodes, pre_reads, barcodelib)
    print('Done')

    print('Finding minimal recombinations ... ', end='', flush=True)
    data_minrecs = get_data_minrecs(purged_barcodes, barcodelib, minrecs)
    minrec_distr = compute_minrec_distr(data_minrecs)
    print('Done')

    print('Computing generation probabilities ... ', end='', flush=True)
    data_pgens = compute_pgens(purged_barcodes, minrec_distr, barcodelib, path_matrix)
    print('Done')

    print('Creating output ... ', end='', flush=True)
    # create output folder if not exists
    create_outdir(pgen_location_dir_out)

    df_pgen = create_df_pgen(sample_names, purged_barcodes, purged_reads,
                            data_minrecs, data_pgens)

    # save dataframe as tab-separated values file (TSV, as .txt)
    df_pgen.to_csv(os.path.join(pgen_location_dir_out, pgen_file_name_out + '.txt'), sep='\t',
                        decimal=decimal_float)
    print('Done')

    return df_pgen

def get_pre_data(df_in):
    # read out the pre (unpurged) data from the pandas dataframe
    pre_barcodes = df_in.index.to_numpy(dtype=str)
    pre_reads = df_in.values
    sample_names = df_in.columns.to_numpy(dtype=str)

    # make sure that reads is 2d (also for one sample)
    # (this should be the case using pandas .values)
    if not len(pre_reads.shape)==2:
        raise ValueError('Unexpected error, please file issue.')

    return pre_barcodes, pre_reads, sample_names

def load_libraries(path_matrix_type='uniform'):
    # os-independent path to data files; os.pardir goes one dir up ('..' on macOS)
    floc = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'data')

    with zipfile.ZipFile(os.path.join(floc, 'polylox_barcodelib.txt.zip')) as z:
        with z.open('polylox_barcodelib.txt', 'r') as f:
            barcodelib = np.loadtxt(f, dtype=str) # [l.decode('utf-8').replace('\n', '') for l in f.readlines()]
            # we add the '' quotes for protecting barcodes (default RPBPBR output)
            barcodelib = np.array(["'" + bc + "'" for bc in barcodelib])

    with zipfile.ZipFile(os.path.join(floc, 'polylox_minrecs.txt.zip')) as z:
        with z.open('polylox_minrecs.txt', 'r') as f:
            minrecs = np.loadtxt(f, dtype=int) # [int(l.decode('utf-8').replace('\n', '')) for l in f.readlines()]

    if path_matrix_type=='uniform':
        with zipfile.ZipFile(os.path.join(floc, 'polylox_path_matrix_uniform.txt.zip')) as z:
            with z.open('polylox_path_matrix_uniform.txt', 'r') as f:
                path_matrix = np.loadtxt(f, delimiter=',')
    elif path_matrix_type=='ld_2017':
        with zipfile.ZipFile(os.path.join(floc, 'polylox_path_matrix_ld_2017_reorder.txt.zip')) as z:
            with z.open('polylox_path_matrix_ld_2017_reorder.txt', 'r') as f:
                path_matrix = np.loadtxt(f, delimiter=',')

    return barcodelib, minrecs, path_matrix

def purge(pre_barcodes, pre_reads, barcodelib):
    # pre_barcodes with shape (#barcodes,)
    # pre_reads with shape (#barcodes, #samples)

    # first filter
    # boolean array indicates for each element in data_barcodes
    # if it is in barcodelib; also removes 'total' and 'intact' if still present
    isinlib = np.isin(pre_barcodes, barcodelib)

    # second filter
    # remove barcodes with zero reads (summed over all samples), otherwise
    # this would inflate the minimal recombination distribution
    isnonzero = np.sum(pre_reads, axis=1) > 0.0

    # filter barcodes and reads on both (logical "and")
    purged_barcodes = pre_barcodes[isinlib & isnonzero]
    purged_reads = pre_reads[isinlib & isnonzero, :]

    return purged_barcodes, purged_reads

def get_data_minrecs(purged_barcodes, barcodelib, minrecs):
    # preallocate min rec array
    data_minrecs = np.zeros(len(purged_barcodes), dtype=int)

    # create lookup dict mapping barcode to its minrec number
    barcodelib_minrecs = dict(zip(barcodelib, minrecs))

    for (i, bc) in enumerate(purged_barcodes):
        data_minrecs[i] = barcodelib_minrecs[bc]

    return data_minrecs

def compute_minrec_distr(data_minrecs):
    # preallocate min rec distribution with 11 entries
    # for 0 to 10 (inclusive) minimal recombinations
    minrec_distr = np.zeros((11,))

    # loop over data minrecs and count occurences
    for mr in data_minrecs:
        minrec_distr[mr] += 1.0

    # normalise to get a (frequency) distribution
    minrec_distr /= np.sum(minrec_distr)

    return minrec_distr

def compute_pgens(purged_barcodes, minrec_distr, barcodelib, path_matrix):
    # computation of barcode generation probabilities

    # first, we find an index array containing the barcode position of the
    # purged barcodes in the whole library
    barcodelib_lookup = dict(zip(barcodelib, range(len(barcodelib))))
    datainds = np.array([barcodelib_lookup[bc] for bc in purged_barcodes], dtype=int)

    # with this, extract a sub-matrix of the path matrix for the set of purged barcodes
    data_path_matrix = path_matrix[datainds, :]

    # pgens calculation is then weighting the probabilities to reach a certain
    # barcode after i steps with the probability to have seen i steps
    data_pgens = np.dot(data_path_matrix, minrec_distr)

    return data_pgens

def create_df_pgen(sample_names, purged_barcodes, purged_reads,
                        data_minrecs, data_pgens):

    # create a pandas dataframe with barcodes (as index column)
    # minimal rec, pgen, and all samples (in this order)
    df_pgen = pd.DataFrame(purged_reads, columns=sample_names)
    df_pgen['Barcode'] = purged_barcodes
    df_pgen['MinRec'] = data_minrecs
    df_pgen['Pgen'] = data_pgens
    df_pgen.set_index('Barcode', inplace=True)
    df_pgen = df_pgen.reindex(columns=['MinRec', 'Pgen'] + list(sample_names))

    return df_pgen

def validate_user_input_pgen(location_file_in, pgen_location_dir_out, pgen_file_name_out):
    # check types for the input
    if not type(location_file_in)==str:
        raise TypeError('Str expected for location_file_in.')

    if not type(pgen_location_dir_out)==str:
        raise TypeError('Str expected for pgen_location_dir_out.')

    if not type(pgen_file_name_out)==str:
        raise TypeError('Str expected for pgen_file_name_out.')

def validate_user_input_dataframe(df_in):
    # check that the index name (first displayed column) is Barcode
    if not df_in.index.name=='Barcode':
        raise ValueError('Index name expected to be \'Barcode\'.')

    # check that all other columns (sample names) are unique and are not
    # called Barcode
    if len(df_in.columns) > len(set(df_in.columns)):
        raise ValueError('Sample names are not unique.')
    if 'Barcode' in df_in.columns:
        raise ValueError('\'Barcode\' is not a valid sample name.')

    # check that the barcodes themselves are unique
    if len(df_in.index) > len(set(df_in.index)):
        raise ValueError('Barcodes are not unique.')

    # we don't have to check for empty barcodes or samples here
    # empty barcodes are later purged anyway, empty samples don't matter for
    # pgen calculation (which happens over all samples, as of now)
