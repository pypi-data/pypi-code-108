#!/usr/bin/env python
# @Author: Kelvin
# @Date:   2021-02-11 12:22:40
# @Last Modified by:   Kelvin
# @Last Modified time: 2022-01-27 21:27:31

import os
from collections import defaultdict
import pandas as pd
import numpy as np
import re
import copy
from changeo.IO import readGermlines
import warnings
import h5py
import networkx as nx
import bz2
import gzip
from anndata import AnnData
import _pickle as cPickle
from scanpy import logging as logg
from ..utilities._utilities import *
from ..utilities._io import *
from typing import Union, Sequence, Tuple, Dict, Optional


class Dandelion:
    """
    `Dandelion` class object.

    Main class object storing input/ouput slots for all functions.

    """

    def __init__(self,
                 data=None,
                 metadata=None,
                 germline=None,
                 distance=None,
                 edges=None,
                 layout=None,
                 graph=None,
                 initialize=True,
                 **kwargs):
        self.data = data
        self.metadata = metadata
        self.distance = distance
        self.edges = edges
        self.layout = layout
        self.graph = graph
        self.threshold = None
        self.germline = {}
        self.querier = None

        if germline is not None:
            self.germline.update(germline)

        if os.path.isfile(str(self.data)):
            self.data = load_data(self.data)

        if self.data is not None:
            self.data = sanitize_data(self.data)
            self.n_contigs = self.data.shape[0]
            if metadata is None:
                if initialize is True:
                    update_metadata(self, **kwargs)
                try:
                    self.n_obs = self.metadata.shape[0]
                except:
                    self.n_obs = 0
            else:
                self.metadata = metadata
                self.n_obs = self.metadata.shape[0]
        else:
            self.n_contigs = 0
            self.n_obs = 0

    def _gen_repr(self, n_obs, n_contigs) -> str:
        # inspire by AnnData's function
        descr = f"Dandelion class object with n_obs = {n_obs} and n_contigs = {n_contigs}"
        for attr in ["data", "metadata", "distance", "edges"]:
            try:
                keys = getattr(self, attr).keys()
            except:
                keys = []
            if len(keys) > 0:
                descr += f"\n    {attr}: {str(list(keys))[1:-1]}"
            else:
                descr += f"\n    {attr}: {str(None)}"
        if self.layout is not None:
            descr += f"\n    layout: {', '.join(['layout for '+ str(len(x)) + ' vertices' for x in (self.layout[0], self.layout[1])])}"
        else:
            descr += f"\n    layout: {str(None)}"
        if self.graph is not None:
            descr += f"\n    graph: {', '.join(['networkx graph of '+ str(len(x)) + ' vertices' for x in (self.graph[0], self.graph[1])])} "
        else:
            descr += f"\n    graph: {str(None)}"
        return descr

    def __repr__(self) -> str:
        # inspire by AnnData's function
        return self._gen_repr(self.n_obs, self.n_contigs)

    def copy(self):
        """
        Performs a deep copy of all slots in `Dandelion` class.

        Parameters
        ----------
        self : Dandelion
            `Dandelion` object.

        Returns
        -------
        a deep copy of `Dandelion` class.
        """
        return copy.deepcopy(self)

    def update_plus(
        self,
        option: Literal[
            'all', 'sequence', 'mutations', 'cdr3 lengths',
            'mutations and cdr3 lengths'] = 'mutations and cdr3 lengths'):
        """
        Retrieve additional data columns that are useful.
        Parameters
        ----------
        self : Dandelion
            `Dandelion` object.
        option : Literal
            One of 'all', 'sequence', 'mutations', 'cdr3 lengths',
            'mutations and cdr3 lengths'
        Returns
        -------
        Udpated metadata.
        """
        mutations_type = ['mu_count', 'mu_freq']
        mutationsdef = [
            'cdr_r', 'cdr_s', 'fwr_r', 'fwr_s', '1_r', '1_s', '2_r', '2_s',
            '3_r', '3_s', '4_r', '4_s', '5_r', '5_s', '6_r', '6_s', '7_r',
            '7_s', '8_r', '8_s', '9_r', '9_s', '10_r', '10_s', '11_r', '11_s',
            '12_r', '12_s', '13_r', '13_s', '14_r', '14_s', '15_r', '15_s',
            '16_r', '16_s', '17_r', '17_s', '18_r', '18_s', '19_r', '19_s',
            '20_r', '20_s', '21_r', '21_s', '22_r', '22_s', '23_r', '23_s',
            '24_r', '24_s', '25_r', '25_s', '26_r', '26_s', '27_r', '27_s',
            '28_r', '28_s', '29_r', '29_s', '30_r', '30_s', '31_r', '31_s',
            '32_r', '32_s', '33_r', '33_s', '34_r', '34_s', '35_r', '35_s',
            '36_r', '36_s', '37_r', '37_s', '38_r', '38_s', '39_r', '39_s',
            '40_r', '40_s', '41_r', '41_s', '42_r', '42_s', '43_r', '43_s',
            '44_r', '44_s', '45_r', '45_s', '46_r', '46_s', '47_r', '47_s',
            '48_r', '48_s', '49_r', '49_s', '50_r', '50_s', '51_r', '51_s',
            '52_r', '52_s', '53_r', '53_s', '54_r', '54_s', '55_r', '55_s',
            '56_r', '56_s', '57_r', '57_s', '58_r', '58_s', '59_r', '59_s',
            '60_r', '60_s', '61_r', '61_s', '62_r', '62_s', '63_r', '63_s',
            '64_r', '64_s', '65_r', '65_s', '66_r', '66_s', '67_r', '67_s',
            '68_r', '68_s', '69_r', '69_s', '70_r', '70_s', '71_r', '71_s',
            '72_r', '72_s', '73_r', '73_s', '74_r', '74_s', '75_r', '75_s',
            '76_r', '76_s', '77_r', '77_s', '78_r', '78_s', '79_r', '79_s',
            '80_r', '80_s', '81_r', '81_s', '82_r', '82_s', '83_r', '83_s',
            '84_r', '84_s', '85_r', '85_s', '86_r', '86_s', '87_r', '87_s',
            '88_r', '88_s', '89_r', '89_s', '90_r', '90_s', '91_r', '91_s',
            '92_r', '92_s', '93_r', '93_s', '94_r', '94_s', '95_r', '95_s',
            '96_r', '96_s', '97_r', '97_s', '98_r', '98_s', '99_r', '99_s',
            '100_r', '100_s', '101_r', '101_s', '102_r', '102_s', '103_r',
            '103_s', '104_r', '104_s', 'cdr1_r', 'cdr1_s', 'cdr2_r', 'cdr2_s',
            'fwr1_r', 'fwr1_s', 'fwr2_r', 'fwr2_s', 'fwr3_r', 'fwr3_s', 'v_r',
            'v_s'
        ]
        mutations = [] + mutations_type
        for m in mutations_type:
            for d in mutationsdef:
                mutations.append(m + '_' + d)

        vdjlengths = [
            'junction_length',
            'junction_aa_length',
            'np1_length',
            'np2_length',
        ]
        seqinfo = [
            'sequence', 'sequence_alignment', 'sequence_alignment_aa',
            'junction', 'junction_aa', 'germline_alignment', 'fwr1', 'fwr1_aa',
            'fwr2', 'fwr2_aa', 'fwr3', 'fwr3_aa', 'fwr4', 'fwr4_aa', 'cdr1',
            'cdr1_aa', 'cdr2', 'cdr2_aa', 'cdr3', 'cdr3_aa',
            'v_sequence_alignment_aa', 'd_sequence_alignment_aa',
            'j_sequence_alignment_aa'
        ]
        mutations = [x for x in mutations if x in self.data]
        vdjlengths = [x for x in vdjlengths if x in self.data]
        seqinfo = [x for x in seqinfo if x in self.data]

        if option == 'all':
            if len(mutations) > 0:
                update_metadata(self,
                                retrieve=mutations,
                                retrieve_mode='split and average')
                update_metadata(self,
                                retrieve=mutations,
                                retrieve_mode='average')
            if len(vdjlengths) > 0:
                update_metadata(self,
                                retrieve=vdjlengths,
                                retrieve_mode='split and average')
            if len(seqinfo) > 0:
                update_metadata(self,
                                retrieve=seqinfo,
                                retrieve_mode='split and unique only')
        if option == 'sequence':
            if len(seqinfo) > 0:
                update_metadata(self,
                                retrieve=seqinfo,
                                retrieve_mode='split and unique only')
        if option == 'mutations':
            if len(mutations) > 0:
                update_metadata(self,
                                retrieve=mutations,
                                retrieve_mode='split and average')
                update_metadata(self,
                                retrieve=mutations,
                                retrieve_mode='average')
        if option == 'cdr3 lengths':
            if len(vdjlengths) > 0:
                update_metadata(self,
                                retrieve=vdjlengths,
                                retrieve_mode='split and average')
        if option == 'mutations and cdr3 lengths':
            if len(mutations) > 0:
                update_metadata(self,
                                retrieve=mutations,
                                retrieve_mode='split and average')
                update_metadata(self,
                                retrieve=mutations,
                                retrieve_mode='average')
            if len(vdjlengths) > 0:
                update_metadata(self,
                                retrieve=vdjlengths,
                                retrieve_mode='split and average')

    def update_germline(self,
                        corrected: Optional[Union[Dict, str]] = None,
                        germline: Optional[str] = None,
                        org: Literal['human', 'mouse'] = 'human'):
        """
        Update germline reference with corrected sequences and store in `Dandelion` object.

        Parameters
        ----------
        self : Dandelion
            `Dandelion` object.
        corrected : dict, str, Optional
            dictionary of corrected germline sequences or file path to corrected germline sequences fasta file.
        germline : str, Optional
            path to germline database folder. Defaults to `$GERMLINE` environmental variable.
        org : str
            organism of reference folder. Default is 'human'.

        Returns
        -------
        updated germline reference diciontary in `.germline` slot.
        """
        start = logg.info('Updating germline reference')
        env = os.environ.copy()
        if germline is None:
            try:
                gml = env['GERMLINE']
            except:
                raise OSError(
                    'Environmental variable GERMLINE must be set. Otherwise, please provide path to folder containing germline IGHV, IGHD, and IGHJ fasta files.'
                )
            gml = gml + 'imgt/' + org + '/vdj/'
        else:
            if os.path.isdir(germline):
                gml = germline
            elif type(germline) is not list:
                germline_ = [germline]
                if len(germline_) < 3:
                    raise OSError(
                        'Input for germline is incorrect. Please provide path to folder containing germline IGHV, IGHD, and IGHJ fasta files, or individual paths to the germline IGHV, IGHD, and IGHJ fasta files (with .fasta extension) as a list.'
                    )
                else:
                    gml = []
                    for x in germline_:
                        if not x.endswith('.fasta'):
                            raise OSError(
                                'Input for germline is incorrect. Please provide path to folder containing germline IGHV, IGHD, and IGHJ fasta files, or individual paths to the germline IGHV, IGHD, and IGHJ fasta files (with .fasta extension) as a list.'
                            )
                        gml.append(x)
            elif type(germline) is list:
                if len(germline) < 3:
                    raise OSError(
                        'Input for germline is incorrect. Please provide path to folder containing germline IGHV, IGHD, and IGHJ fasta files, or individual paths to the germline IGHV, IGHD, and IGHJ fasta files (with .fasta extension) as a list.'
                    )
                else:
                    gml = []
                    for x in germline:
                        if not x.endswith('.fasta'):
                            raise OSError(
                                'Input for germline is incorrect. Please provide path to folder containing germline IGHV, IGHD, and IGHJ fasta files, or individual paths to the germline IGHV, IGHD, and IGHJ fasta files (with .fasta extension) as a list.'
                            )
                        gml.append(x)

        if type(gml) is not list:
            gml = [gml]

        germline_ref = readGermlines(gml)
        if corrected is not None:
            if type(corrected) is dict:
                personalized_ref_dict = corrected
            elif os.path.isfile(str(corrected)):
                personalized_ref_dict = readGermlines([corrected])
            # update with the personalized germline database
            if 'personalized_ref_dict' in locals():
                germline_ref.update(personalized_ref_dict)
            else:
                raise OSError(
                    'Input for corrected germline fasta is incorrect. Please provide path to file containing corrected germline fasta sequences.'
                )

        self.germline.update(germline_ref)
        logg.info(' finished',
                  time=start,
                  deep=('Updated Dandelion object: \n'
                        '   \'germline\', updated germline reference\n'))

    def write_pkl(self, filename: str = 'dandelion_data.pkl.pbz2', **kwargs):
        """
        Writes a `Dandelion` class to .pkl format.

        Parameters
        ----------
        filename
            path to `.pkl` file.
        **kwargs
            passed to `_pickle`.
        """
        if isBZIP(filename):
            try:
                with bz2.BZ2File(filename, 'wb') as f:
                    cPickle.dump(self, f, **kwargs)
            except:
                with bz2.BZ2File(filename, 'wb') as f:
                    cPickle.dump(self, f, protocol=4, **kwargs)
        elif isGZIP(filename):
            try:
                with gzip.open(filename, 'wb') as f:
                    cPickle.dump(self, f, **kwargs)
            except:
                with gzip.open(filename, 'wb') as f:
                    cPickle.dump(self, f, protocol=4, **kwargs)
        else:
            f = open(filename, 'wb')
            cPickle.dump(self, f, **kwargs)
            f.close()

    def write_airr(self, filename: str = 'dandelion_airr.tsv', **kwargs):
        """
        Writes a `Dandelion` class to .pkl format.

        Parameters
        ----------
        filename
            path to `.pkl` file.
        **kwargs
            passed to `_pickle`.
        """
        from airr import create_rearrangement
        writer = create_rearrangement(filename,
                                      fields=[x for x in self.data],
                                      **kwargs)
        for _, row in self.data.iterrows():
            writer.write(row)

    def write_h5(self,
                 filename: str = 'dandelion_data.h5ddl',
                 keep_distance: bool = False,
                 complib: Literal['zlib', 'lzo', 'bzip2', 'blosc',
                                  'blosc:blosclz', 'blosc:lz4', 'blosc:lz4hc',
                                  'blosc:snappy', 'blosc:zlib',
                                  'blosc:zstd'] = None,
                 compression: Literal['zlib', 'lzo', 'bzip2', 'blosc',
                                      'blosc:blosclz', 'blosc:lz4',
                                      'blosc:lz4hc', 'blosc:snappy',
                                      'blosc:zlib', 'blosc:zstd'] = None,
                 compression_level: Optional[int] = None,
                 **kwargs):
        """
        Writes a `Dandelion` class to .h5 format.

        Parameters
        ----------
        filename
            path to `.h5` file.
        complib : str, Optional
            method for compression for data frames. see (https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_hdf.html) for more options.
        compression : str, Optional
            same call as complib. Just a convenience option.
        compression_opts : {0-9}, Optional
            Specifies a compression level for data. A value of 0 disables compression.
        **kwargs
            passed to `pd.DataFrame.to_hdf`.
        """
        if compression_level is None:
            compression_level = 9
        else:
            compression_level = compression_level

        # a little hack to overwrite the existing file?
        with h5py.File(filename, "w") as hf:
            for datasetname in hf.keys():
                del hf[datasetname]

        if complib is None and compression is None:
            comp = None
        elif complib is not None and compression is None:
            comp = complib
        elif complib is None and compression is not None:
            comp = compression
        if complib is not None and compression is not None:
            raise ValueError(
                'Please specify only complib or compression. They do the same thing.'
            )

        # now to actually saving
        data = self.data.copy()
        data = sanitize_data(data)
        data = sanitize_data_for_saving(data)
        data.to_hdf(filename,
                    "data",
                    complib=comp,
                    complevel=compression_level,
                    **kwargs)

        if self.metadata is not None:
            metadata = self.metadata.copy()
            for col in metadata.columns:
                weird = (metadata[[col]].applymap(type) !=
                         metadata[[col]].iloc[0].apply(type)).any(axis=1)
                if len(metadata[weird]) > 0:
                    metadata[col] = metadata[col].where(
                        pd.notnull(metadata[col]), '')
            metadata.to_hdf(filename,
                            "metadata",
                            complib=comp,
                            complevel=compression_level,
                            format='table',
                            nan_rep=np.nan,
                            **kwargs)
        try:
            if 'index' in self.edges.columns:
                self.edges.drop('index', axis=1, inplace=True)
            self.edges.to_hdf(filename,
                              "edges",
                              complib=comp,
                              complevel=compression_level,
                              **kwargs)
        except:
            pass

        graph_counter = 0
        try:
            for g in self.graph:
                G = nx.to_pandas_adjacency(g, nonedge=np.nan)
                G.to_hdf(filename,
                         "graph/graph_" + str(graph_counter),
                         complib=comp,
                         complevel=compression_level,
                         **kwargs)
                graph_counter += 1
        except:
            pass

        if keep_distance:
            try:
                for d in self.distance:
                    # how to make this faster?
                    dat = pd.DataFrame(self.distance[d].toarray())
                    dat.to_hdf(filename,
                               "distance/" + d,
                               complib=comp,
                               complevel=compression_level,
                               **kwargs)
            except:
                pass

        with h5py.File(filename, "a") as hf:
            try:
                layout_counter = 0
                for l in self.layout:
                    try:
                        hf.create_group('layout/layout_' + str(layout_counter))
                    except:
                        pass
                    for k in l.keys():
                        hf['layout/layout_' +
                           str(layout_counter)].attrs[k] = l[k]
                    layout_counter += 1
            except:
                pass

            if len(self.germline) > 0:
                try:
                    hf.create_group('germline')
                except:
                    pass
                for k in self.germline.keys():
                    hf['germline'].attrs[k] = self.germline[k]
            if self.threshold is not None:
                tr = self.threshold
                hf.create_dataset('threshold', data=tr)

    write = write_h5ddl = write_h5  # shortcut


class Query:
    def __init__(self, data):
        self.data = data
        self.Cell = Tree()
        for contig, row in data.iterrows():
            self.Cell[Contig(row).contig['cell_id']][Contig(
                row).contig].value = 1

    @property
    def querydtype(self):
        return (str(self.data[self.query].dtype))

    def retrieve(self, query, retrieve_mode):
        self.query = query
        ret = {}
        for cell in self.Cell:
            cols, vdj, vj = {}, [], []
            for contig in self.Cell[cell]:
                if isinstance(contig, dict):
                    if contig['locus'] in ['IGH', 'TRB', 'TRD']:
                        vdj.append(contig[query])
                    elif contig['locus'] in ['IGK', 'IGL', 'TRA', 'TRG']:
                        vj.append(contig[query])
            if retrieve_mode == 'split and unique only':
                if len(vdj) > 0:
                    cols.update({
                        query + '_VDJ':
                        '|'.join(
                            str(x) for x in list(dict.fromkeys(vdj))
                            if present(x))
                    })
                if len(vj) > 0:
                    cols.update({
                        query + '_VJ':
                        '|'.join(
                            str(x) for x in list(dict.fromkeys(vj))
                            if present(x))
                    })
            elif retrieve_mode == 'merge and unique only':
                cols.update({
                    query:
                    '|'.join(str(x) for x in set(vdj + vj) if present(x))
                })
            elif retrieve_mode == 'split and sum':
                if len(vdj) > 0:
                    cols.update({
                        query + '_VDJ':
                        np.sum([float(x) for x in vdj if present(x)])
                    })
                else:
                    cols.update({query + 'VDJ': np.nan})
                if len(vj) > 0:
                    cols.update({
                        query + '_VJ':
                        np.sum([float(x) for x in vj if present(x)])
                    })
                else:
                    cols.update({query + 'VJ': np.nan})
            elif retrieve_mode == 'split and average':
                if len(vdj) > 0:
                    cols.update({
                        query + '_VDJ':
                        np.mean([float(x) for x in vdj if present(x)])
                    })
                else:
                    cols.update({query + '_VDJ': np.nan})
                if len(vj) > 0:
                    cols.update({
                        query + '_VJ':
                        np.mean([float(x) for x in vj if present(x)])
                    })
                else:
                    cols.update({query + '_VJ': np.nan})
            elif retrieve_mode == 'merge':
                cols.update(
                    {query: '|'.join(x for x in set(vdj + vj) if present(x))})
            elif retrieve_mode == 'split':
                if len(vdj) > 0:
                    for i in range(1, len(vdj) + 1):
                        cols.update({query + '_VDJ_' + str(i): vdj[i - 1]})
                if len(vj) > 0:
                    for i in range(1, len(vj) + 1):
                        cols.update({query + '_VJ_' + str(i): vj[i - 1]})
            elif retrieve_mode == 'sum':
                cols.update({
                    query:
                    np.sum([float(x) for x in vdj + vj if present(x)])
                })
                if not present(cols[query]):
                    cols.update({query: np.nan})
            elif retrieve_mode == 'average':
                cols.update({
                    query:
                    np.mean([float(x) for x in vdj + vj if present(x)])
                })
                if not present(cols[query]):
                    cols.update({query: np.nan})
            ret.update({cell: cols})
        out = pd.DataFrame.from_dict(ret, orient='index')
        if retrieve_mode not in [
                'split and sum', 'split and average', 'sum', 'average'
        ]:
            if retrieve_mode == 'split':
                for x in out:
                    try:
                        out[x] = pd.to_numeric(out[x])
                    except:
                        out[x].fillna('', inplace=True)
            else:
                out.fillna('', inplace=True)
        return (out)


def initialize_metadata(self, cols: Sequence, clonekey: str,
                        collapse_alleles: bool) -> Dandelion:
    init_dict = {}
    for col in cols:
        init_dict.update(
            {col: {
                'query': col,
                'retrieve_mode': 'split and unique only',
            }})
    if clonekey in init_dict:
        init_dict.update({
            clonekey: {
                'query': clonekey,
                'retrieve_mode': 'merge and unique only',
            }
        })
    if 'sample_id' in init_dict:
        init_dict.update({
            'sample_id': {
                'query': 'sample_id',
                'retrieve_mode': 'merge and unique only',
            }
        })
    if self.querier is None:
        querier = Query(self.data)
        self.querier = querier
    else:
        querier = self.querier

    meta_ = defaultdict(dict)
    for k, v in init_dict.copy().items():
        if all_missing(self.data[k]):
            init_dict.pop(k)
            continue
        meta_[k] = querier.retrieve(**v)
        if k in ['duplicate_count', 'umi_count', 'mu_count', 'mu_freq']:
            v.update({'retrieve_mode': 'split'})
            meta_[k + '_split'] = querier.retrieve(**v)
    tmp_metadata = pd.concat(meta_.values(), axis=1, join="inner")

    if 'locus_VDJ' in tmp_metadata:
        suffix_h = '_VDJ'
        suffix_l = '_VJ'
    else:
        suffix_h = ''
        suffix_l = ''

    if clonekey in init_dict:
        tmp_metadata[str(clonekey)] = tmp_metadata[str(clonekey)].replace(
            '', 'unassigned')

        clones = tmp_metadata[str(clonekey)].str.split('|', expand=False)
        tmpclones = []
        for i in clones:
            while 'unassigned' in i:
                i.remove('unassigned')
                if len(i) == 1:
                    break
            tmpclones.append(i)
        tmpclones = [
            '|'.join(sorted(list(set(x)), key=cmp_to_key(cmp_str_emptylast)))
            for x in tmpclones
        ]
        tmpclonesdict = dict(zip(tmp_metadata.index, tmpclones))
        tmp_metadata[str(clonekey)] = pd.Series(tmpclonesdict)
        tmp = tmp_metadata[str(clonekey)].str.split('|', expand=True).stack()
        tmp = tmp.reset_index(drop=False)
        tmp.columns = ['cell_id', 'tmp', str(clonekey)]
        clone_size = tmp[str(clonekey)].value_counts()
        if "" in clone_size.index:
            clone_size = clone_size.drop("", axis=0)
        clonesize_dict = dict(clone_size)
        size_of_clone = pd.DataFrame.from_dict(clonesize_dict, orient='index')
        size_of_clone.reset_index(drop=False, inplace=True)
        size_of_clone.columns = [str(clonekey), 'clone_size']
        size_of_clone[str(clonekey) + '_by_size'] = size_of_clone.index + 1
        size_dict = dict(
            zip(size_of_clone[clonekey],
                size_of_clone[str(clonekey) + '_by_size']))
        size_dict.update({'': 'unassigned'})
        tmp_metadata[str(clonekey) + '_by_size'] = [
            '|'.join(
                sorted(list(set([str(size_dict[c_]) for c_ in c.split('|')]))))
            if len(c.split('|')) > 1 else str(size_dict[c])
            for c in tmp_metadata[str(clonekey)]
        ]
        tmp_metadata[str(clonekey) +
                     '_by_size'] = tmp_metadata[str(clonekey) +
                                                '_by_size'].astype('category')
        tmp_metadata = tmp_metadata[
            [str(clonekey), str(clonekey) + '_by_size'] + [
                cl for cl in tmp_metadata if cl not in
                [str(clonekey), str(clonekey) + '_by_size']
            ]]

    for i in tmp_metadata.index:
        if 'locus' + suffix_h in tmp_metadata:
            if not check_missing(tmp_metadata.loc[i, 'locus' + suffix_h]):
                if 'locus' + suffix_l in tmp_metadata:
                    if not check_missing(tmp_metadata.loc[i,
                                                          'locus' + suffix_l]):
                        tmp_metadata.at[i, 'status'] = tmp_metadata.loc[
                            i, 'locus' +
                            suffix_h] + ' + ' + tmp_metadata.loc[i, 'locus' +
                                                                 suffix_l]
                    else:
                        tmp_metadata.at[i, 'status'] = tmp_metadata.loc[
                            i, 'locus' + suffix_h] + '_only'
                else:
                    tmp_metadata.at[i, 'status'] = tmp_metadata.loc[
                        i, 'locus' + suffix_h] + '_only'
            else:
                if 'locus' + suffix_l in tmp_metadata:
                    if not check_missing(tmp_metadata.loc[i,
                                                          'locus' + suffix_l]):
                        tmp_metadata.at[i, 'status'] = tmp_metadata.loc[
                            i, 'locus' + suffix_l] + '_only'
                    else:
                        tmp_metadata.at[i, 'status'] = 'unassigned'
                else:
                    tmp_metadata.at[i, 'status'] = 'unassigned'
        else:
            if 'locus' + suffix_l in tmp_metadata:
                if not check_missing(tmp_metadata.loc[i, 'locus' + suffix_l]):
                    tmp_metadata.at[i, 'status'] = tmp_metadata.loc[
                        i, 'locus' + suffix_l] + '_only'
                else:
                    tmp_metadata.at[i, 'status'] = 'unassigned'
            else:
                tmp_metadata.at[i, 'status'] = 'unassigned'

    tmp_metadata['status_summary'] = [
        'Multi' if '|' in i else i for i in tmp_metadata['status']
    ]

    for i in tmp_metadata.index:
        if 'productive' + suffix_h in tmp_metadata:
            if not check_missing(tmp_metadata.loc[i, 'productive' + suffix_h]):
                if 'productive' + suffix_l in tmp_metadata:
                    if not check_missing(
                            tmp_metadata.loc[i, 'productive' + suffix_l]):
                        tmp_metadata.at[i, 'productive'] = tmp_metadata.loc[
                            i, 'productive' +
                            suffix_h] + ' + ' + tmp_metadata.loc[i,
                                                                 'productive' +
                                                                 suffix_l]
                    else:
                        tmp_metadata.at[i, 'productive'] = tmp_metadata.loc[
                            i, 'productive' + suffix_h]
                else:
                    tmp_metadata.at[i, 'productive'] = tmp_metadata.loc[
                        i, 'productive' + suffix_h]
            else:
                if 'productive' + suffix_l in tmp_metadata:
                    if not check_missing(
                            tmp_metadata.loc[i, 'productive' + suffix_l]):
                        tmp_metadata.at[i, 'productive'] = tmp_metadata.loc[
                            i, 'productive' + suffix_l]
                    else:
                        tmp_metadata.at[i, 'productive'] = 'unassigned'
                else:
                    tmp_metadata.at[i, 'productive'] = 'unassigned'
        else:
            if 'productive' + suffix_l in tmp_metadata:
                if not check_missing(
                        tmp_metadata.loc[i, 'productive' + suffix_l]):
                    tmp_metadata.at[i, 'productive'] = tmp_metadata.loc[
                        i, 'productive' + suffix_l]
                else:
                    tmp_metadata.at[i, 'productive'] = 'unassigned'
            else:
                tmp_metadata.at[i, 'productive'] = 'unassigned'

    tmp_metadata['productive_summary'] = [
        'Multi' if '|' in i else i for i in tmp_metadata['productive']
    ]

    conversion_dict = {
        'igha': 'IgA',
        'igha1': 'IgA',
        'igha2': 'IgA',
        'ighd': 'IgD',
        'ighe': 'IgE',
        'ighg': 'IgG',
        'ighg1': 'IgG',
        'ighg2': 'IgG',
        'ighg3': 'IgG',
        'ighg4': 'IgG',
        'ighg2a': 'IgG',
        'ighg2b': 'IgG',
        'ighg2c': 'IgG',
        'ighga': 'IgG',
        'ighgb': 'IgG',
        'ighgc': 'IgG',
        'ighm': 'IgM',
        'igkc': 'IgK',
        'iglc': 'IgL',
        'iglc1': 'IgL',
        'iglc2': 'IgL',
        'iglc3': 'IgL',
        'iglc4': 'IgL',
        'iglc5': 'IgL',
        'iglc6': 'IgL',
        'iglc7': 'IgL',
        'na': 'unassigned',
        'nan': 'unassigned',
        '': 'unassigned',
        'none': 'unassigned',
        'trac': 'unassigned',
        'trbc': 'unassigned',
        'trbc1': 'unassigned',
        'trbc2': 'unassigned',
        'trdc': 'unassigned',
        'trgc': 'unassigned',
        'trgc1': 'unassigned',
        'trgc2': 'unassigned',
        'trgc3': 'unassigned',
        'trgc4': 'unassigned',
        'unassigned': 'unassigned',
        None: 'unassigned',
        np.nan: 'unassigned',
    }

    isotype = []
    if 'c_call' + suffix_h in tmp_metadata:
        for k in tmp_metadata['c_call' + suffix_h]:
            if isinstance(k, str):
                if ',' in k:
                    k = '|'.join(k.split(','))
                if '|' in k:
                    isotype.append('|'.join([
                        str(z) for z in [
                            conversion_dict[y.lower()] for y in set(
                                [re.sub('[0-9]', '', x) for x in k.split('|')])
                        ]
                    ]))
                else:
                    isotype.append(conversion_dict[k.lower()])
            else:
                isotype.append('unassigned')
        tmp_metadata['isotype'] = isotype
        tmp_metadata['isotype_summary'] = [
            i
            if i == 'IgM|IgD' or i == 'IgD|IgM' else 'Multi' if '|' in i else i
            for i in tmp_metadata['isotype']
        ]

    vdj_gene_calls = ['v_call', 'd_call', 'j_call']
    if collapse_alleles:
        for x in vdj_gene_calls:
            if x in self.data:
                for c in tmp_metadata:
                    if x in c:
                        tmp_metadata[c] = [
                            '|'.join([
                                '|'.join(list(set(yy.split(','))))
                                for yy in list(
                                    set([
                                        re.sub('[*][0-9][0-9]', '', tx)
                                        for tx in t.split('|')
                                    ]))
                            ]) for t in tmp_metadata[c]
                        ]
    multi = {}
    multic = {}
    for i in tmp_metadata.index:
        try:
            if 'v_call_genotyped' in cols:
                if 'v_call_genotyped' + suffix_h in tmp_metadata:
                    hv_ = tmp_metadata.at[i, 'v_call_genotyped' +
                                          suffix_h].split('|')
            else:
                if 'v_call' + suffix_h in tmp_metadata:
                    hv_ = tmp_metadata.at[i, 'v_call' + suffix_h].split('|')
        except:
            if 'v_call_genotyped' in cols:
                if 'v_call_genotyped' + suffix_h in tmp_metadata:
                    hv_ = tmp_metadata.at[i, 'v_call_genotyped' + suffix_h]
            else:
                if 'v_call' + suffix_h in tmp_metadata:
                    hv_ = tmp_metadata.at[i, 'v_call' + suffix_h]
        if 'd_call' + suffix_h in tmp_metadata:
            try:
                hd_ = tmp_metadata.at[i, 'd_call' + suffix_h].split('|')
            except:
                hd_ = tmp_metadata.at[i, 'd_call' + suffix_h]
        if 'd_call' + suffix_l in tmp_metadata:
            tmp_metadata.drop('d_call' + suffix_l, axis=1, inplace=True)

        if 'j_call' + suffix_h in tmp_metadata:
            try:
                hj_ = tmp_metadata.at[i, 'j_call' + suffix_h].split('|')
            except:
                hj_ = tmp_metadata.at[i, 'j_call' + suffix_h]
        try:
            if 'v_call_genotyped' in cols:
                if 'v_call_genotyped' + suffix_l in tmp_metadata:
                    lv_ = tmp_metadata.at[i, 'v_call_genotyped' +
                                          suffix_l].split('|')
            else:
                if 'v_call' + suffix_l in tmp_metadata:
                    lv_ = tmp_metadata.at[i, 'v_call' + suffix_l].split('|')
        except:
            if 'v_call_genotyped' in cols:
                if 'v_call_genotyped' + suffix_l in tmp_metadata:
                    lv_ = tmp_metadata.at[i, 'v_call_genotyped' + suffix_l]
            else:
                if 'v_call' + suffix_l in tmp_metadata:
                    lv_ = tmp_metadata.at[i, 'v_call' + suffix_l]
        if 'j_call' + suffix_l in tmp_metadata:
            try:
                lj_ = tmp_metadata.at[i, 'j_call' + suffix_l].split('|')
            except:
                lj_ = tmp_metadata.at[i, 'j_call' + suffix_l]
        if 'c_call' + suffix_h in tmp_metadata:
            try:
                hc_ = tmp_metadata.at[i, 'c_call' + suffix_h].split('|')
            except:
                hc_ = tmp_metadata.at[i, 'c_call' + suffix_h]
        if 'c_call' + suffix_l in tmp_metadata:
            try:
                lc_ = tmp_metadata.at[i, 'c_call' + suffix_l].split('|')
            except:
                lc_ = tmp_metadata.at[i, 'c_call' + suffix_l]
        multi_h = []
        multi_l = []
        multi_hc = []
        multi_lc = []
        if 'hv_' in locals():
            if len(hv_) > 1:
                multi_h.append(['Multi' + suffix_h + '_v'])
        if 'hd_' in locals():
            if len(hd_) > 1:
                multi_h.append(['Multi' + suffix_h + '_d'])
        if 'hj_' in locals():
            if len(hj_) > 1:
                multi_h.append(['Multi' + suffix_h + '_j'])
        if 'lv_' in locals():
            if len(lv_) > 1:
                multi_l.append(['Multi' + suffix_l + '_v'])
        if 'lj_' in locals():
            if len(lj_) > 1:
                multi_l.append(['Multi' + suffix_l + '_j'])
        if 'hc_' in locals():
            if len(hc_) > 1:
                if 'isotype_summary' in tmp_metadata:
                    if (tmp_metadata.at[i, 'isotype_summary'] == 'IgM|IgD'
                        ) or (tmp_metadata.at[i, 'isotype_summary']
                              == 'IgD|IgM'):
                        multi_hc.append(
                            [tmp_metadata.at[i, 'isotype_summary']])
                    else:
                        multi_hc.append(['Multi' + suffix_h + '_c'])
        if 'lc_' in locals():
            if len(lc_) > 1:
                multi_lc.append(['Multi' + suffix_l + '_c'])
        if len(multi_hc) < 1:
            multi_hc.append(['Single'])
        if len(multi_h) < 1:
            multi_h.append(['Single'])
        if 'lv_' in locals() and 'lj_' in locals():
            if (len(lv_) == 1) & (len(lj_) == 1):
                if ('' not in lv_) and ('' not in lj_):
                    if len(multi_l) < 1:
                        multi_l.append(['Single'])
        if 'lc_' in locals():
            if len(lc_) == 1:
                if ('' not in lc_):
                    if len(multi_lc) < 1:
                        multi_lc.append(['Single'])
        multih = '|'.join(list(set(flatten(multi_h))))
        multil = '|'.join(list(set(flatten(multi_l))))
        multihc = '|'.join(list(set(flatten(multi_hc))))
        multilc = '|'.join(list(set(flatten(multi_lc))))
        if len(multih) > 0:
            if len(multil) > 0:
                multi[i] = multih + ' + ' + multil
            else:
                multi[i] = multih
        else:
            multi[i] = 'unassigned'
        if len(multihc) > 0:
            if len(multilc) > 0:
                multic[i] = multihc + ' + ' + multilc
            else:
                multic[i] = multihc
        else:
            multic[i] = 'unassigned'
    tmp_metadata['vdj_status'] = pd.Series(multi)
    tmp_metadata['vdj_status_summary'] = [
        'Multi' if 'Multi' + suffix_h in i else 'Single'
        for i in tmp_metadata['vdj_status']
    ]
    tmp_metadata['constant_status_summary'] = [
        'Multi' if 'Multi' + suffix_h in i else 'Single'
        for i in pd.Series(multic)
    ]
    if 'isotype' in tmp_metadata:
        if all(tmp_metadata['isotype'] == 'unassigned'):
            tmp_metadata.drop(['isotype', 'isotype_summary'],
                              axis=1,
                              inplace=True)

    self.metadata = tmp_metadata.copy()


def update_metadata(self: Dandelion,
                    retrieve: Optional[Union[Sequence, str]] = None,
                    clone_key: Optional[str] = None,
                    retrieve_mode: Literal[
                        'split and unique only', 'merge and unique only',
                        'split and sum', 'split and average', 'split', 'merge',
                        'sum', 'average'] = 'split and unique only',
                    collapse_alleles: bool = True,
                    reinitialize: bool = False,
                    verbose: bool = False) -> Dandelion:
    """
    A `Dandelion` initialisation function to update and populate the `.metadata` slot.

    Parameters
    ----------
    self : Dandelion
        `Dandelion` object.
    retrieve : str, sequence, Optional
        Column name in `.data` slot to retrieve and update the metadata.
    clone_key : str, Optional
        Column name of clone id. None defaults to 'clone_id'.
    retrieve_mode: str
        One of ['split and unique only', 'merge and unique only', 'split and sum', 'split and average', 'split', 'merge', 'sum', 'average'].
        `split and unique only` returns the retrieval splitted into two columns, i.e. one for VDJ and one for VJ chains, separated by '|' for unique elements.
        `merge and unique only` returns the retrieval merged into one column, separated by '|' for unique elements.
        `split` returns the retrieval splitted into separate columns for each contig.
        `merge` returns the retrieval merged into one columns for each contig, separated by '|' for unique elements.
        'split and sum' returns the retrieval sumed in the VDJ and VJ columns (separately).
        'split and average' returns the retrieval averaged in the VDJ and VJ columns (separately).
        'sum' returns the retrieval sumed into one column for all contigs.
        'average' returns the retrieval averaged into one column for all contigs.
    collapse_alleles : bool
        Returns the V(D)J genes with allelic calls if False.
    reinitialize : bool
        Whether or not to reinitialize the current metadata. Useful when updating older versions of `dandelion` to newer version.
    Returns
    -------
    `Dandelion` object with `.metadata` slot initialized.
    """

    if clone_key is None:
        clonekey = 'clone_id'
    else:
        clonekey = clone_key

    cols = [
        'sequence_id', 'cell_id', 'locus', 'productive', 'v_call', 'd_call',
        'j_call', 'c_call', 'duplicate_count', 'junction_aa'
    ]

    if 'duplicate_count' not in self.data:
        try:
            self.data['duplicate_count'] = self.data['umi_count']
        except:
            cols = list(
                map(lambda x: 'umi_count'
                    if x == 'duplicate_count' else x, cols))
            if 'umi_count' not in self.data:
                raise ValueError(
                    "Unable to initialize metadata due to missing keys. Please ensure either 'umi_count' or 'duplicate_count' is in the input data."
                )
    if 'cell_id' not in self.data:  # shortcut for bulk data to pretend every unique sequence is a cell?
        self.data['cell_id'] = self.data['sequence_id']

    if not all([c in self.data for c in cols]):
        raise ValueError(
            'Unable to initialize metadata due to missing keys. Please ensure the input data contains all the following columns: {}'
            .format(cols))

    if 'sample_id' in self.data:
        cols = ['sample_id'] + cols

    if 'v_call_genotyped' in self.data:
        cols = list(
            map(lambda x: 'v_call_genotyped' if x == 'v_call' else x, cols))

    for c in ['sequence_id', 'cell_id']:
        cols.remove(c)

    if clonekey in self.data:
        if not all(pd.isnull(self.data[clonekey])):
            cols = [clonekey] + cols

    metadata_status = self.metadata
    if (metadata_status is None) or reinitialize:
        initialize_metadata(self, cols, clonekey, collapse_alleles)

    tmp_metadata = self.metadata.copy()

    if retrieve is not None:
        if self.querier is None:
            querier = Query(self.data)
            self.querier = querier
        else:
            querier = self.querier
        ret_dict = {}
        if type(retrieve) is str:
            retrieve = [retrieve]
        if type(retrieve_mode) is str:
            retrieve_mode = [retrieve_mode]
            if len(retrieve) > len(retrieve_mode):
                retrieve_mode = [x for x in retrieve_mode for i in retrieve]
        for ret, mode in zip(retrieve, retrieve_mode):
            ret_dict.update({ret: {
                'query': ret,
                'retrieve_mode': mode,
            }})

        vdj_gene_ret = ['v_call', 'd_call', 'j_call']

        retrieve_ = defaultdict(dict)
        for k, v in ret_dict.items():
            if k in self.data.columns:
                retrieve_[k] = querier.retrieve(**v)
            else:
                raise KeyError(
                    'Cannot retrieve \'%s\' : Unknown column name.' % k)
        ret_metadata = pd.concat(retrieve_.values(), axis=1, join="inner")
        ret_metadata.dropna(axis=1, how='all', inplace=True)
        for col in ret_metadata:
            if all_missing(ret_metadata[col]):
                ret_metadata.drop(col, axis=1, inplace=True)

        if collapse_alleles:
            for k in ret_dict.keys():
                if k in vdj_gene_ret:
                    for c in ret_metadata:
                        if k in c:
                            ret_metadata[c] = [
                                '|'.join([
                                    '|'.join(list(set(yy.split(','))))
                                    for yy in list(
                                        set([
                                            re.sub('[*][0-9][0-9]', '', tx)
                                            for tx in t.split('|')
                                        ]))
                                ]) for t in ret_metadata[c]
                            ]

        for r in ret_metadata:
            tmp_metadata[r] = pd.Series(ret_metadata[r])
        self.metadata = tmp_metadata.copy()


def load_data(obj: Union[pd.DataFrame, str]) -> pd.DataFrame:
    """
    Reads in or copy dataframe object and set sequence_id as index without dropping.

    Parameters
    ----------
    obj : DataFrame, str
        file path to .tsv file or pandas DataFrame object.

    Returns
    -------
    pandas DataFrame object.
    """
    if os.path.isfile(str(obj)):
        try:
            obj_ = pd.read_csv(obj, sep='\t')
        except FileNotFoundError as e:
            print(e)
    elif isinstance(obj, pd.DataFrame):
        obj_ = obj.copy()
    else:
        raise TypeError(
            "Either input is not of <class 'pandas.core.frame.DataFrame'> or file does not exist."
        )

    if 'sequence_id' in obj_.columns:
        obj_.set_index('sequence_id', drop=False, inplace=True)
    else:
        raise KeyError("'sequence_id' not found in columns of input")

    return (obj_)
