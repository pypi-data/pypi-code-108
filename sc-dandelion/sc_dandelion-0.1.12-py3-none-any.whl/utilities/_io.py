#!/usr/bin/env python
# @Author: kt16
# @Date:   2020-05-12 14:01:32
# @Last Modified by:   Kelvin
# @Last Modified time: 2021-08-20 16:47:32

import os
import json
import re
import bz2
import gzip
import pandas as pd
import numpy as np
import scipy.sparse
import networkx as nx
import _pickle as cPickle
from ..utilities._utilities import *
from ..utilities._core import *
from os import PathLike
from typing import Union, Sequence, Optional
from collections import defaultdict, OrderedDict

AIRR = [
    'cell_id',
    'sequence_id',
    'sequence',
    'sequence_aa',
    'productive',
    'complete_vdj',
    'vj_in_frame',
    'locus',
    'v_call',
    'd_call',
    'j_call',
    'c_call',
    'junction',
    'junction_aa',
    'consensus_count',
    'duplicate_count',
    'cdr3_start',
    'cdr3_end',
    'sequence_length_10x',
    'high_confidence_10x',
    'is_cell_10x',
    'fwr1_aa',
    'fwr1',
    'cdr1_aa',
    'cdr1',
    'fwr2_aa',
    'fwr2',
    'cdr2_aa',
    'cdr2',
    'fwr3_aa',
    'fwr3',
    'fwr4_aa',
    'fwr4',
    'clone_id',
    'raw_consensus_id_10x',
    'exact_subclonotype_id_10x',
]
CELLRANGER = [
    'barcode',
    'contig_id',
    'sequence',
    'aa_sequence',
    'productive',
    'full_length',
    'frame',
    'chain',
    'v_gene',
    'd_gene',
    'j_gene',
    'c_gene',
    'cdr3_nt',
    'cdr3',
    'reads',
    'umis',
    'cdr3_start',
    'cdr3_stop',
    'length',
    'high_confidence',
    'is_cell',
    'fwr1',
    'fwr1_nt',
    'cdr1',
    'cdr1_nt',
    'fwr2',
    'fwr2_nt',
    'cdr2',
    'cdr2_nt',
    'fwr3',
    'fwr3_nt',
    'fwr4',
    'fwr4_nt',
    'raw_clonotype_id',
    'raw_consensus_id',
    'exact_subclonotype_id',
]


def fasta_iterator(fh: str):
    """Read in a fasta file as an iterator."""
    while True:
        line = fh.readline()
        if line.startswith('>'):
            break
    while True:
        header = line[1:-1].rstrip()
        sequence = fh.readline().rstrip()
        while True:
            line = fh.readline()
            if not line:
                break
            if line.startswith('>'):
                break
            sequence += line.rstrip()
        yield (header, sequence)
        if not line:
            return


def Write_output(out: str, file: str):
    """General line writer."""
    fh = open(file, "a")
    fh.write(out)
    fh.close()
    return ()


def read_pkl(filename: str = 'dandelion_data.pkl.pbz2') -> Dandelion:
    """
    Read in and returns a `Dandelion` class saved using pickle format.

    Parameters
    ----------
    filename : str
        path to `.pkl` file. Depending on the extension, it will try to unzip accordingly.

    Returns
    -------
    Dandelion object.
    """
    if isBZIP(filename):
        data = bz2.BZ2File(filename, 'rb')
        data = cPickle.load(data)
    elif isGZIP(filename):
        data = gzip.open(filename, 'rb')
        data = cPickle.load(data)
    else:
        with open(filename, 'rb') as f:
            data = cPickle.load(f)
    return (data)


def read_h5(filename: str = 'dandelion_data.h5') -> Dandelion:
    """
    Read in and returns a `Dandelion` class from .h5 format.

    Parameters
    ----------
    filename : str
        path to `.h5` file

    Returns
    -------
    `Dandelion` object.
    """
    try:
        data = pd.read_hdf(filename, 'data')
        data = sanitize_data(data)

        if check_mix_dtype(data):
            for x in return_mix_dtype(data):
                data[x].replace('', pd.NA, inplace=True)
            data = sanitize_data(data)
    except:
        raise AttributeError(
            '{} does not contain attribute `data`'.format(filename))
    try:
        metadata = pd.read_hdf(filename, 'metadata')
    except:
        pass

    try:
        edges = pd.read_hdf(filename, 'edges')
    except:
        pass

    try:
        g_0 = pd.read_hdf(filename, 'graph/graph_0')
        g_1 = pd.read_hdf(filename, 'graph/graph_1')
        g_0 = g_0 + 1
        g_0 = g_0.fillna(0)
        g_1 = g_1 + 1
        g_1 = g_1.fillna(0)
        graph0 = nx.from_pandas_adjacency(g_0)
        graph1 = nx.from_pandas_adjacency(g_1)
        for u, v, d in graph0.edges(data=True):
            d['weight'] = d['weight'] - 1
        for u, v, d in graph1.edges(data=True):
            d['weight'] = d['weight'] - 1
        graph = (graph0, graph1)
    except:
        pass

    with h5py.File(filename, 'r') as hf:
        try:
            layout0 = {}
            for k in hf['layout/layout_0'].attrs.keys():
                layout0.update({k: np.array(hf['layout/layout_0'].attrs[k])})
            layout1 = {}
            for k in hf['layout/layout_1'].attrs.keys():
                layout1.update({k: np.array(hf['layout/layout_1'].attrs[k])})
            layout = (layout0, layout1)
        except:
            pass

        germline = {}
        try:
            for g in hf['germline'].attrs:
                germline.update({g: hf['germline'].attrs[g]})
        except:
            pass

        distance = Tree()
        try:
            for d in hf['distance'].keys():
                d_ = pd.read_hdf(filename, 'distance/' + d)
                distance[d] = scipy.sparse.csr_matrix(d_.values)
        except:
            pass

        try:
            threshold = np.float(np.array(hf['threshold']))
        except:
            threshold = None

    constructor = {}
    constructor['data'] = data
    if 'metadata' in locals():
        constructor['metadata'] = metadata
    if 'germline' in locals():
        constructor['germline'] = germline
    if 'edges' in locals():
        constructor['edges'] = edges
    if 'distance' in locals():
        constructor['distance'] = distance
    if 'layout' in locals():
        constructor['layout'] = layout
    if 'graph' in locals():
        constructor['graph'] = graph
    try:
        res = Dandelion(**constructor)
    except:
        res = Dandelion(**constructor, initialize=False)

    if 'threshold' in locals():
        res.threshold = threshold
    else:
        pass
    return (res)


def read_10x_airr(file: str) -> Dandelion:
    """
    Read the 10x AIRR rearrangement .tsv directly and returns a `Dandelion` object.

    Parameters
    ----------
    file : str
        path to `airr_rearrangement.tsv`

    Returns
    -------
    `Dandelion` object of pandas data frame.

    """
    dat = load_data(file)
    # get all the v,d,j,c calls
    if 'locus' not in dat:
        tmp = [(v, d, j, c) for v, d, j, c in zip(
            dat['v_call'], dat['d_call'], dat['j_call'], dat['c_call'])]
        locus = []
        for t in tmp:
            if all('IGH' in x for x in t if pd.notnull(x)):
                locus.append('IGH')
            elif all('IGK' in x for x in t if pd.notnull(x)):
                locus.append('IGK')
            elif all('IGL' in x for x in t if pd.notnull(x)):
                locus.append('IGL')
            elif all('TRA' in x for x in t if pd.notnull(x)):
                locus.append('TRA')
            elif all('TRB' in x for x in t if pd.notnull(x)):
                locus.append('TRB')
            elif all('TRD' in x for x in t if pd.notnull(x)):
                locus.append('TRD')
            elif all('TRG' in x for x in t if pd.notnull(x)):
                locus.append('TRG')
            else:
                locus.append(np.nan)
        dat['locus'] = locus
    null_columns = [col for col in dat.columns if all_missing(dat[col])]
    if len(null_columns) > 0:
        dat.drop(null_columns, inplace=True, axis=1)

    return (Dandelion(dat))


def to_scirpy(data: Dandelion, transfer: bool = False) -> AnnData:
    """
    Convert a `Dandelion` object to scirpy's format.

    Parameters
    ----------
    data : Dandelion
        `Dandelion` object
    transfer : bool
        Whether to execute :func:`dandelion.tl.transfer` to transfer all data
        to the :class:`anndata.AnnData` instance.

    Returns
    -------
    `AnnData` object in the format initialized by `scirpy`.

    """
    try:
        import scirpy as ir
    except:
        raise ImportError('Please install scirpy. pip install scirpy')

    if 'duplicate_count' not in data.data and 'umi_count' in data.data:
        data.data['duplicate_count'] = data.data['umi_count']
    for h in [
            "sequence",
            "rev_comp",
            "sequence_alignment",
            "germline_alignment",
            "v_cigar",
            "d_cigar",
            "j_cigar",
    ]:
        if h not in data.data:
            data.data[h] = None
    return (ir.io.from_dandelion(data, transfer))


def from_scirpy(adata: AnnData) -> Dandelion:
    """
    Read a `scirpy` initialized `AnnData` oject and returns a `Dandelion` object.

    Parameters
    ----------
    adata : AnnData
        `scirpy` initialized `AnnData` object.

    Returns
    -------
    `Dandelion` object.

    """
    try:
        import scirpy as ir
    except:
        raise ImportError('Please install scirpy. pip install scirpy')

    return (ir.io.to_dandelion(adata))


def concat(arrays: Sequence[Union[pd.DataFrame, Dandelion]],
           check_unique: bool = True) -> Dandelion:
    """
    Concatenate dataframe and return as `Dandelion` object.

    Parameters
    ----------
    arrays : Sequence
        List of `Dandelion` class objects or pandas dataframe
    check_unique : bool
        Check the new index for duplicates. Otherwise defer the check until necessary.
        Setting to False will improve the performance of this method.

    Returns
    -------
        `Dandelion` object
    """
    arrays = list(arrays)

    try:
        arrays_ = [x.data.copy() for x in arrays]
    except:
        arrays_ = [x.copy() for x in arrays]

    if check_unique:
        try:
            df = pd.concat(arrays_, verify_integrity=True)
        except:
            for i in range(0, len(arrays)):
                arrays_[i]['sequence_id'] = [
                    x + '__' + str(i) for x in arrays_[i]['sequence_id']
                ]
            arrays_ = [load_data(x) for x in arrays_]
            df = pd.concat(arrays_, verify_integrity=True)
    else:
        df = pd.concat(arrays_)
    try:
        out = Dandelion(df)
    except:
        out = Dandelion(df, initialize=False)
    return (out)


def read_10x_vdj(path: Union[str, PathLike],
                 filename_prefix: Optional[str] = None,
                 return_dandelion: bool = True,
                 verbose: bool = False) -> Union[Dandelion, pd.DataFrame]:
    """
    A parser to read .csv and .json files directly from folder containing 10x cellranger-outouts.

    This function parses the 10x output files into an AIRR compatible format.

    Minimum requirement is one of either {filename_prefix}_contig_annotations.csv or all_contig_annotations.json.

    If .fasta, .json files are found in the same folder, additional info will be appended to the final table.

    Parameters
    ----------
    path : str, PathLike
        path to folder containing `.csv` and/or `.json` files, or path to files directly.
    filename_prefix : str, Optional
        prefix of file name preceding '_contig'. None defaults to 'filtered'.
    return_dandelion : bool
        whether or not to return the output as an initialised `Dandelion` object or as a pandas `DataFrame`.
        Default is True.
    verbose : bool
        whether or not to print which files are read/found. Default is False.
    Returns
    -------
    `Dandelion` or pandas `DataFrame` object.

    """
    if filename_prefix is None:
        filename_pre = 'filtered'
    else:
        filename_pre = filename_prefix

    if os.path.isdir(str(path)):
        files = os.listdir(path)
        filelist = []
        for fx in files:
            if re.search(filename_pre + '_contig', fx):
                if fx.endswith('.fasta') or fx.endswith('.csv'):
                    filelist.append(fx)
            if re.search('all_contig_annotations', fx):
                if fx.endswith('.json'):
                    filelist.append(fx)
        csv_idx = [i for i, j in enumerate(filelist) if j.endswith('.csv')]
        json_idx = [i for i, j in enumerate(filelist) if j.endswith('.json')]
        if len(csv_idx) == 1:
            file = str(path) + '/' + str(filelist[csv_idx[0]])
            if verbose:
                print("Reading {}".format(str(file)))
            raw = pd.read_csv(str(file))
            raw.set_index('contig_id', drop=False, inplace=True)
            fasta_file = str(file).split('_annotations.csv')[0] + '.fasta'
            json_file = re.sub(filename_pre + '_contig_annotations',
                               'all_contig_annotations',
                               str(file).split('.csv')[0] + '.json')
            if os.path.exists(json_file):
                if verbose:
                    print(
                        "Found {} file. Extracting extra information.".format(
                            str(json_file)))
                out = parse_annotation(raw)
                with open(json_file) as f:
                    raw_json = json.load(f)
                out_json = parse_json(raw_json)
                out.update(out_json)
            elif os.path.exists(fasta_file):
                if verbose:
                    print(
                        "Found {} file. Extracting extra information.".format(
                            str(fasta_file)))
                seqs = {}
                fh = open(fasta_file, 'r')
                for header, sequence in fasta_iterator(fh):
                    seqs[header] = sequence
                raw['sequence'] = pd.Series(seqs)
                out = parse_annotation(raw)
            else:
                out = parse_annotation(raw)
        elif len(csv_idx) < 1:
            if len(json_idx) == 1:
                json_file = str(path) + '/' + str(filelist[json_idx[0]])
                if verbose:
                    print("Reading {}".format(json_file))
                if os.path.exists(json_file):
                    with open(json_file) as f:
                        raw = json.load(f)
                    out = parse_json(raw)
            else:
                raise IOError(
                    "{}_contig_annotations.csv and all_contig_annotations.json file(s) not found in {} folder."
                    .format(str(filename_pre), str(path)))
        elif len(csv_idx) > 1:
            raise IOError(
                "There are multiple input .csv files with the same filename prefix {} in {} folder."
                .format(str(filename_pre), str(path)))
    elif os.path.isfile(str(path)):
        file = path
        if str(file).endswith('.csv'):
            if verbose:
                print("Reading {}.".format(str(file)))
            raw = pd.read_csv(str(file))
            raw.set_index('contig_id', drop=False, inplace=True)
            fasta_file = str(file).split('_annotations.csv')[0] + '.fasta'
            json_file = re.sub(filename_pre + '_contig_annotations',
                               'all_contig_annotations',
                               str(file).split('.csv')[0] + '.json')
            if os.path.exists(json_file):
                if verbose:
                    print(
                        "Found {} file. Extracting extra information.".format(
                            str(json_file)))
                out = parse_annotation(raw)
                with open(json_file) as f:
                    raw_json = json.load(f)
                out_json = parse_json(raw_json)
                out.update(out_json)
            elif os.path.exists(fasta_file):
                if verbose:
                    print(
                        "Found {} file. Extracting extra information.".format(
                            str(fasta_file)))
                seqs = {}
                fh = open(fasta_file, 'r')
                for header, sequence in fasta_iterator(fh):
                    seqs[header] = sequence
                raw['sequence'] = pd.Series(seqs)
                out = parse_annotation(raw)
            else:
                out = parse_annotation(raw)
        elif str(file).endswith('.json'):
            if os.path.exists(file):
                if verbose:
                    print("Reading {}".format(file))
                with open(file) as f:
                    raw = json.load(f)
                out = parse_json(raw)
            else:
                raise IOError("{} not found.".format(file))
    else:
        raise IOError("{} not found.".format(path))
    res = pd.DataFrame.from_dict(out, orient='index')
    # quick check if locus is malformed
    res = res[~res['locus'].str.contains('[|]')]
    if return_dandelion:
        return (Dandelion(res))
    else:
        return (res)


def parse_json(data: list) -> defaultdict:
    main_dict1 = {
        "barcode": "cell_id",
        "contig_name": "sequence_id",
        "sequence": "sequence",
        "aa_sequence": "sequence_aa",
        "productive": 'productive',
        "full_length": 'complete_vdj',
        "frame": "vj_in_frame",
        "cdr3_seq": "junction",
        "cdr3": "junction_aa",
    }
    main_dict2 = {
        "read_count": "consensus_count",
        "umi_count": "duplicate_count",
        "cdr3_start": "cdr3_start",
        "cdr3_stop": "cdr3_end",
    }
    main_dict3 = {
        "high_confidence": 'high_confidence_10x',
        "filtered": 'filtered_10x',
        "is_gex_cell": 'is_cell_10x',
        "is_asm_cell": 'is_asm_cell_10x',
    }
    info_dict = {
        "raw_clonotype_id": 'clone_id',
        "raw_consensus_id": 'raw_consensus_id_10x',
        "exact_subclonotype_id": 'exact_subclonotype_id_10x',
    }
    region_type_dict = {
        'L-REGION+V-REGION': 'v_call',
        'D-REGION': 'd_call',
        'J-REGION': 'j_call',
        'C-REGION': 'c_call',
    }
    required_calls = ['v_call', 'd_call', 'j_call', 'c_call']
    region_keys = ['fwr1', 'cdr1', 'fwr2', 'cdr2', 'fwr3', 'fwr4']
    out = defaultdict(OrderedDict)
    for i in range(len(data)):
        if data[i]['contig_name'] is not None:
            key = data[i]['contig_name']
        else:
            continue
        for k in main_dict1.keys():
            if data[i][k] is not None:
                out[key].update({main_dict1[k]: data[i][k]})
            else:
                out[key].update({main_dict1[k]: ''})
        if data[i]['annotations'] is not None:
            chains = []
            for j in range(len(data[i]['annotations'])):
                chains.append(data[i]['annotations'][j]['feature']['chain'])
            out[key].update({'locus': '|'.join(list(set(chains)))})
            for j in range(len(data[i]['annotations'])):
                rtype = data[i]['annotations'][j]['feature']['region_type']
                if rtype in region_type_dict.keys():
                    call = region_type_dict[rtype]
                else:
                    continue
                if data[i]['annotations'][j]['feature'][
                        'gene_name'] is not None:
                    out[key].update({
                        call:
                        data[i]['annotations'][j]['feature']['gene_name']
                    })
                else:
                    out[key].update({call: ''})
        for rc in required_calls:
            if rc not in out[key]:
                out[key].update({rc: ''})
        for k in main_dict2.keys():
            if data[i][k] is not None:
                out[key].update({main_dict2[k]: data[i][k]})
            else:
                out[key].update({main_dict2[k]: np.nan})
        for rk in region_keys:
            if data[i][rk] is not None:
                for k in data[i][rk]:
                    if k == 'start':
                        ka = rk + '_start'
                    elif k == 'stop':
                        ka = rk + '_end'
                    elif k == 'nt_seq':
                        ka = rk + ''
                    elif k == 'aa_seq':
                        ka = rk + '_aa'
                    else:
                        continue
                    out[key].update({ka: data[i][rk][k]})
            else:
                for k in region_keys:
                    out[key].update({k + '_start': np.nan})
                    out[key].update({k + '_end': np.nan})
                    out[key].update({k + '': ''})
                    out[key].update({k + '_aa': ''})
        if data[i]['info'] is not None:
            for info in data[i]['info']:
                if data[i]['info'][info] is not None:
                    out[key].update({info_dict[info]: data[i]['info'][info]})
                else:
                    out[key].update({info_dict[info]: ''})
        for k in main_dict3.keys():
            if data[i][k] is not None:
                out[key].update({main_dict3[k]: data[i][k]})
            else:
                out[key].update({main_dict3[k]: ''})
    return (out)


def parse_annotation(data: pd.DataFrame) -> defaultdict:
    out = defaultdict(OrderedDict)
    swap_dict = dict(zip(CELLRANGER, AIRR))
    for _, row in data.iterrows():
        contig = Contig(row, swap_dict).contig['sequence_id']
        out[contig] = Contig(row, swap_dict).contig
        if out[contig]['locus'] in ['None', 'none', None, np.nan, '']:
            calls = []
            for call in ['v_call', 'd_call', 'j_call', 'c_call']:
                if out[contig][call] not in ['None', 'none', None, np.nan, '']:
                    calls.append(out[contig][call])
            out[contig]['locus'] = '|'.join(
                list(set([str(c)[:3] for c in calls])))
        if out[contig]['locus'] == 'None' or out[contig]['locus'] == '':
            out[contig]['locus'] = '|'
    return (out)


def change_file_location(data: Sequence,
                         filename_prefix: Optional[Union[Sequence,
                                                         str]] = None):
    """
    Move file from tmp folder to dandelion folder.

    Only used for TCR data.

    Parameters
    ----------
    data : Sequence
        list of data folders containing the .tsv files. if provided as a single string, it will first be converted to a
        list; this allows for the function to be run on single/multiple samples.
    filename_prefix : str, Optional
        list of prefixes of file names preceding '_contig'. None defaults to 'filtered'.

    Returns
    -------
    Individual V(D)J data files with v_call_genotyped column containing reassigned heavy chain v calls
    """
    fileformat = 'blast'
    if type(data) is not list:
        data = [data]
    if type(filename_prefix) is not list:
        filename_prefix = [filename_prefix]
    if all(t is None for t in filename_prefix):
        filename_prefix = [None for d in data]

    informat_dict = {
        'changeo': '_igblast_db-pass.tsv',
        'blast': '_igblast_db-pass.tsv',
        'airr': '_igblast_gap.tsv'
    }

    filePath = None

    for i in range(0, len(data)):
        filePath = check_filepath(data[i],
                                  filename_prefix=filename_prefix[i],
                                  endswith=informat_dict[fileformat],
                                  subdir='tmp')
        if filePath is None:
            raise OSError(
                'Path to .tsv file for {} is unknown. '.format(data[i]) +
                'Please specify path to reannotated .tsv file or folder containing reannotated .tsv file.'
            )
        tmp = check_travdv(filePath)
        _airrfile = filePath.replace('_db-pass.tsv', '.tsv')
        airr_output = load_data(_airrfile)
        cols_to_merge = [
            'junction_aa_length', 'fwr1_aa', 'fwr2_aa', 'fwr3_aa', 'fwr4_aa',
            'cdr1_aa', 'cdr2_aa', 'cdr3_aa', 'sequence_alignment_aa',
            'v_sequence_alignment_aa', 'd_sequence_alignment_aa',
            'j_sequence_alignment_aa'
        ]
        for x in cols_to_merge:
            tmp[x] = pd.Series(airr_output[x])
        tmp.to_csv(filePath, sep='\t', index=False)
        cmd = ['rsync', '-azvh', filePath, filePath.rsplit('/', 2)[0]]
        run(cmd)
