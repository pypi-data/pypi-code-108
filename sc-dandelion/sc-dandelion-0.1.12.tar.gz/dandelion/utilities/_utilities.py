#!/usr/bin/env python
# @Author: kt16
# @Date:   2020-05-12 14:01:32
# @Last Modified by:   Kelvin
# @Last Modified time: 2021-08-17 20:25:07

import os
from collections import defaultdict, Iterable
from airr import RearrangementSchema
import pandas as pd
import numpy as np
from subprocess import run
import re
from typing import Sequence, Tuple, Dict, Union, Optional
try:
    from typing import Literal
except ImportError:
    try:
        from typing_extensions import Literal
    except ImportError:

        class LiteralMeta(type):
            """LiteralMeta class."""

            def __getitem__(self, values):
                """Return Literal."""
                if not isinstance(values, tuple):
                    values = (values, )
                return type("Literal_", (Literal, ), dict(__args__=values))

        class Literal(metaclass=LiteralMeta):
            pass


class Tree(defaultdict):
    """Create a recursive defaultdict."""

    def __init__(self, value=None):
        super(Tree, self).__init__(Tree)
        self.value = value


def dict_from_table(meta: pd.DataFrame, columns: Tuple[str, str]) -> Dict:
    """
    Generate a dictionary from a dataframe.

    Parameters
    ----------
    meta
        pandas dataframe or file path
    columns
        column names in dataframe

    Returns
    -------
        dictionary
    """
    if (isinstance(meta, pd.DataFrame)) & (columns is not None):
        meta_ = meta
        if len(columns) == 2:
            sample_dict = dict(zip(meta_[columns[0]], meta_[columns[1]]))
    elif (os.path.isfile(str(meta))) & (columns is not None):
        meta_ = pd.read_csv(meta, sep='\t', dtype='object')
        if len(columns) == 2:
            sample_dict = dict(zip(meta_[columns[0]], meta_[columns[1]]))

    sample_dict = clean_nan_dict(sample_dict)
    return (sample_dict)


def clean_nan_dict(d: Dict) -> Dict:
    """
    Remove nan from dictionary.

    Parameters
    ----------
    d : Dict
        dictionary

    Returns
    -------
        dictionary with no NAs.
    """
    return {k: v for k, v in d.items() if v is not np.nan}


def flatten(l: Sequence) -> Sequence:
    """
    Flatten a list-in-list-in-list.

    Parameters
    ----------
    l : Sequence
        a list-in-list list

    Returns
    -------
        a flattened list.
    """
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el


def makeblastdb(ref: str):
    """
    Run makeblastdb on constant region fasta file.

    Wrapper for makeblastdb.

    Parameters
    ----------
    ref : str
        constant region fasta file
    """
    cmd = ['makeblastdb', '-dbtype', 'nucl', '-parse_seqids', '-in', ref]
    run(cmd)


def bh(pvalues: np.array) -> np.array:
    """
    Compute the Benjamini-Hochberg FDR correction.

    Parameters
    ----------
        pvalues : np.array
            array of p-values to correct
    Returns
    -------
        np.array of corrected p-values
    """
    n = int(pvalues.shape[0])
    new_pvalues = np.empty(n)
    values = [(pvalue, i) for i, pvalue in enumerate(pvalues)]
    values.sort()
    values.reverse()
    new_values = []
    for i, vals in enumerate(values):
        rank = n - i
        pvalue, index = vals
        new_values.append((n / rank) * pvalue)
    for i in range(0, int(n) - 1):
        if new_values[i] < new_values[i + 1]:
            new_values[i + 1] = new_values[i]
    for i, vals in enumerate(values):
        pvalue, index = vals
        new_pvalues[index] = new_values[i]
    return new_pvalues


def is_categorical(array_like) -> bool:
    return array_like.dtype.name == 'category'


def type_check(dataframe, key) -> bool:
    return dataframe[key].dtype == str or dataframe[
        key].dtype == object or is_categorical(
            dataframe[key]) or dataframe[key].dtype == bool


def isGZIP(filename: str) -> bool:
    if filename.split('.')[-1] == 'gz':
        return True
    return False


def isBZIP(filename: str) -> bool:
    if filename.split('.')[-1] == 'pbz2':
        return True
    return False


def check_filepath(s,
                   filename_prefix: Optional[str] = None,
                   endswith: Optional[str] = None,
                   subdir: Optional[str] = None):
    if filename_prefix is None:
        filename_pre = 'filtered'
    else:
        filename_pre = filename_prefix

    if endswith is None:
        ends_with = ''
    else:
        ends_with = endswith

    filePath = None
    if os.path.isfile(str(s)) and str(s).endswith(ends_with):
        filePath = s
    elif os.path.isdir(str(s)):
        files = os.listdir(s)
        for file in files:
            out_ = s.rstrip('/') + '/'
            if os.path.isdir(out_ + os.path.basename(file)):
                if file == 'dandelion':
                    if subdir is None:
                        out_ = out_ + os.path.basename(file) + '/'
                    else:
                        out_ = out_ + os.path.basename(
                            file) + '/' + subdir + '/'
                    for x in os.listdir(out_):
                        if x.endswith(ends_with):
                            if str(x).split(
                                    ends_with)[0] == filename_pre + '_contig':
                                filePath = out_ + x
                            else:
                                continue
            else:
                continue
    return (filePath)


def check_fastapath(fasta, filename_prefix: Optional[str] = None):
    if filename_prefix is None:
        filename_pre = 'filtered'
    else:
        filename_pre = filename_prefix

    filePath = None
    if os.path.isfile(str(fasta)) and str(fasta).endswith('.fasta'):
        filePath = fasta
    elif os.path.isdir(str(fasta)):
        files = os.listdir(fasta)
        for file in files:
            out_ = fasta.rstrip('/') + '/'
            if str(file).endswith(".fasta"):
                if str(file).split('.fasta')[0] == filename_pre + '_contig':
                    filePath = out_ + os.path.basename(file)
                else:
                    continue
    return (filePath)


def cmp(a, b):
    """Python2.x cmp function."""
    return (a > b) - (a < b)


def cmp_str_emptylast(s1, s2):
    """Help sort empty string to last."""
    if not s1 or not s2:
        return bool(s2) - bool(s1)

    return cmp(s1, s2)


def cmp_to_key(mycmp):
    """Convert a cmp= function into a key= function."""
    class K:
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0

    return K


def not_same_call(a, b, pattern):
    """Utility function to check if a == b in terms of pattern."""
    return ((re.search(pattern, a) and not re.search(pattern, b))
            or (re.search(pattern, b) and not re.search(pattern, a)))


def same_call(a, b, c, pattern):
    """Utility function to check if a == b == c in terms of pattern."""
    queries = [a, b, c]
    queries = [q for q in queries if pd.notnull(q)]
    return (all([re.search(pattern, x) for x in queries]))


def present(x):
    """Utility function to check if x is not null or blank."""
    return (pd.notnull(x) and x != '')


def all_missing(x):
    """Utility function to check if all x is not null or blank."""
    return (all(pd.isnull(x)) or all(x == ''))


def check_missing(x):
    """Utility function to check if x is not null or blank."""
    return (pd.isnull(x) or x == '')


def check_mix_dtype(data):
    """Utility function to check if mixed dtypes."""
    return (any([
        True for c in data.columns
        if pd.api.types.infer_dtype(data[c]).startswith("mixed")
    ]))


def return_mix_dtype(data):
    """Utility function to return mixed dtypes columns."""
    check = [
        c for c in data.columns
        if pd.api.types.infer_dtype(data[c]).startswith("mixed")
    ]
    return (check)


def sanitize_data(data, ignore='clone_id'):
    """Quick sanitize dtypes."""
    data = data.astype('object')
    data = data.infer_objects()
    for d in data:
        if d in RearrangementSchema.properties:
            if RearrangementSchema.properties[d]['type'] in [
                    'string', 'boolean', 'integer'
            ]:
                data[d].replace([None, np.nan, pd.NA, ''], '', inplace=True)
                if RearrangementSchema.properties[d]['type'] == 'integer':
                    data[d] = [
                        int(x) if present(x) else ''
                        for x in pd.to_numeric(data[d])
                    ]
            else:
                data[d].replace([None, pd.NA, ''], np.nan, inplace=True)
        else:
            if d != ignore:
                try:
                    data[d] = pd.to_numeric(data[d])
                except:
                    data[d].replace(to_replace=[None, np.nan, pd.NA],
                                    value='',
                                    inplace=True)
        if re.search('mu_freq', d):
            data[d] = [
                float(x) if present(x) else np.nan
                for x in pd.to_numeric(data[d])
            ]
        if re.search('mu_count', d):
            data[d] = [
                int(x) if present(x) else '' for x in pd.to_numeric(data[d])
            ]
    data = check_travdv(data)

    # check if airr-standards is happy
    validate_airr(data)
    return (data)


def sanitize_data_for_saving(data):
    """Quick sanitize dtypes for saving."""
    tmp = data.copy()
    for d in tmp:
        if d in RearrangementSchema.properties:
            if RearrangementSchema.properties[d]['type'] in [
                    'string', 'boolean'
            ]:
                tmp[d].replace([None, np.nan, pd.NA, ''], '', inplace=True)
            if RearrangementSchema.properties[d]['type'] in [
                    'integer', 'number'
            ]:
                tmp[d].replace([None, np.nan, pd.NA, ''], np.nan, inplace=True)
        else:
            try:
                tmp[d] = pd.to_numeric(tmp[d])
            except:
                tmp[d].replace([None, pd.NA, np.nan], '', inplace=True)
    return (tmp)


def validate_airr(data):
    """Validate dtypes in airr table."""
    tmp = data.copy()
    int_columns = []
    for d in tmp:
        try:
            tmp[d].replace(np.nan, pd.NA).astype("Int64")
            int_columns.append(d)
        except:
            pass
    bool_columns = [
        'rev_comp', 'productive', 'vj_in_frame', 'stop_codon', 'complete_vdj'
    ]
    str_columns = list(tmp.dtypes[tmp.dtypes == 'object'].index)
    columns = [
        c for c in list(set(int_columns + str_columns + bool_columns))
        if c in tmp
    ]
    if len(columns) > 0:
        for c in columns:
            tmp[c].fillna('', inplace=True)
    for _, row in tmp.iterrows():
        contig = Contig(row).contig
        for required in [
                'sequence', 'rev_comp', 'sequence_alignment',
                'germline_alignment', 'v_cigar', 'd_cigar', 'j_cigar'
        ]:
            if required not in contig:
                contig.update({required: ''})
    RearrangementSchema.validate_header(contig.keys())
    RearrangementSchema.validate_row(contig)


def check_travdv(data):
    data = load_data(data)
    contig = [x for x in data['sequence_id']]
    v = [x for x in data['v_call']]
    d = [x for x in data['d_call']]
    j = [x for x in data['j_call']]
    c = [x for x in data['c_call']]
    l = [x for x in data['locus']]
    v_dict = dict(zip(contig, v))
    d_dict = dict(zip(contig, d))
    j_dict = dict(zip(contig, j))
    c_dict = dict(zip(contig, c))
    l_dict = dict(zip(contig, l))
    for co in contig:
        if re.search('TRAV.*/DV', v_dict[co]):
            if same_call(j_dict[co], c_dict[co], d_dict[co], 'TRA'):
                if not re.search('TRA', l_dict[co]):
                    l_dict[co] = 'TRA'
            elif same_call(j_dict[co], c_dict[co], d_dict[co], 'TRD'):
                if not re.search('TRD', l_dict[co]):
                    l_dict[co] = 'TRD'
    data['locus'] = pd.Series(l_dict)
    return (data)


def load_data(obj: Union[pd.DataFrame, str]) -> pd.DataFrame:
    """
    Read in or copy dataframe object and set sequence_id as index without dropping.

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


class ContigDict(dict):
    """Class Object to extract the contigs as a dictionary."""

    def __setitem__(self, key, value):
        """Standard __setitem__."""
        super().__setitem__(key, value)

    def __hash__(self):
        """Make it hashable."""
        return hash(tuple(self))


class Contig:
    def __init__(self, contig, mapper=None):
        if mapper is not None:
            mapper.update({k: k for k in contig.keys() if k not in mapper})
            self._contig = ContigDict(
                {mapper[key]: vals
                 for (key, vals) in contig.items()})
        else:
            self._contig = ContigDict(contig)

    @property
    def contig(self):
        return self._contig
