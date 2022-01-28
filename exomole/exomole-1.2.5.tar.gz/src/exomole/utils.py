"""Module grouping some useful data-structures and functionality used by other modules
in the `exomole` package.

This module only groups *helper* functions and classes, which are not designed to be
used by the end-users of the `exomole` package.
"""

import warnings
from pathlib import Path

import pandas
import requests

from .exceptions import (
    APIError,
    LineWarning,
    LineCommentError,
    LineValueError,
    DataParseError,
)


def get_file_raw_text_over_api(
    which, molecule_slug=None, isotopologue_slug=None, dataset_name=None
):
    """Get the raw text of any ExoMol file over the ExoMol api.

    Exomol *.def* or *.all* file are supported, controlled by the `which` argument.
    For ``which='all'``, all the other optional arguments are ignored.
    The file is requested over *https* under the relevant URL via the ExoMol public API.

    Parameters
    ----------
    which : {'all', 'def'}
    molecule_slug, isotopologue_slug, dataset_name : str, optional
        Ignored if ``which == 'all'``.

    Returns
    -------
    raw_text : str
        The raw text of the file requested.

    Raises
    ------
    APIError
        If the arguments passed result in a request with an unsuccessful response.
    """
    base_url = "https://www.exomol.com/db/"
    if which == "all":
        url = f"{base_url}/exomol.all"
    elif which == "def" and all([molecule_slug, isotopologue_slug, dataset_name]):
        url = (
            f"{base_url}{molecule_slug}/{isotopologue_slug}/"
            f"{dataset_name}/{isotopologue_slug}__{dataset_name}.def"
        )
    else:
        raise ValueError(f"Unrecognised arguments passed")

    response = requests.get(url)
    if response.status_code != 200:
        raise APIError(f"Unsuccessful response received from {url}")
    raw_text = response.text
    return raw_text


def parse_exomol_line(
    lines,
    n_orig,
    expected_comment=None,
    file_name=None,
    val_type=None,
    warn_on_comments=False,
):
    """A helper line parser for the ExoMol files (*.all* and *.def*).

    List of the file lines is passed as well as the original length of the list
    `n_orig`.
    The top line of `lines` is popped (`lines` gets changed as an externality) and the
    line value is extracted, cast to the final data type (`val_type`) and returned.
    The list of `lines` is therefore being consumed line by line with each call of this
    function.
    If the `expected_comment` is passed, the comment in the top line
    (after the ``#`` symbol) is checked against the `expected_comment`,
    and if they do not match and `warn_on_comment` is set to ``True``, the
    `LineWarning` is raised.
    If the `val_type` is passed, the value is cast to the passed type.

    Parameters
    ----------
    lines : list of str
        At first containing all the lines of the file which are then being
        consumed one by one.
    n_orig : int
        The number of lines of the full file (for error raising only).
    expected_comment : str, optional
        The comment after the ``#`` symbol on each line is expected to match the
        passed `expected_comment`.
    file_name : str, optional
        The name of the file that `lines` belonged to (for error raising only).
    val_type : type, optional
        The intended `type` of the parsed value, the value will be cast to.
    warn_on_comments : bool, optional
        If ``True``, the `LineWarning` will be raised if the parsed comment
        does not match the `expected_comment`.

    Returns
    -------
    str or int or float
        Value belonging to the top line of `lines` passed. Type is either `str`,
        or the `val_type` passed.

    Raises
    ------
    LineCommentError
        If the top line does not have the required format of ``value # comment``
    LineValueError
        If the value parsed from the top line cannot be cast to the `val_type`.

    Warnings
    --------
    LineWarning
        If `warn_on_comment` set to ``True`` and the comment parsed from the top line
        does not match the `expected_comment` passed, the `LineWarning` is raised.
        Also raised if an empty line is detected anywhere (irrespective of the
        `warn_on_comment` value).
    """

    while True:
        try:
            line = lines.pop(0).strip()
        except IndexError:
            msg = f"Run out of lines"
            if file_name:
                msg += f" in {file_name}"
            raise LineValueError(msg)
        line_num = n_orig - len(lines)
        if line:
            break
        else:
            msg = f"Empty line detected on line {line_num}"
            if file_name:
                msg += f" in {file_name}"
            warnings.warn(msg, LineWarning)
    try:
        val, comment = line.split("# ")
        val = val.strip()
    except ValueError:
        msg = f"Unexpected line format detected on line {line_num}"
        if file_name:
            msg += f" in {file_name}"
        raise LineCommentError(msg)
    if val_type:
        try:
            val = val_type(val)
        except ValueError:
            msg = f"Unexpected value type detected on line {line_num}"
            if file_name:
                msg += f" in {file_name}"
            raise LineValueError(msg)
    if expected_comment and warn_on_comments and comment != expected_comment:
        msg = f"Unexpected comment detected on line {line_num}!"
        if file_name:
            msg += f" in {file_name}"
        warnings.warn(msg, LineWarning)
    return val


def load_dataframe_chunks(
    file_path,
    chunk_size,
    first_col_is_index=False,
    column_names=None,
    dtype=None,
    check_num_columns=True,
):
    """Generates chunks of a compressed ExoMol data file.

    Chunks of either *.states.bz2* file or *.trans.bz2* file are loaded from the
    local file system with the specified chunk size.
    Generator of `pandas.DataFrames` is returned.
    No decompression is necessary beforehand.
    If `column_names` are passed, and `check_num_columns` is ``True``, it verifies that
    ``len(column_names)`` matches to the number of columns in the file,
    otherwise an exception is raised.

    Parameters
    ----------
    file_path : str or Path
        Path to the *.bz2* compressed file I want to load. Either *.states* or *.trans*
        file.
    chunk_size : int
        Appropriate value depending on RAM available.
    first_col_is_index : bool, optional
        If ``True``, the first data column values are set as the chunk index (and the
        first column name is therefore ignored - but still must be present in
        `column_names`).
    column_names : list of str, optional
        Column names of the file loaded. If ``first_column_is_index is True``,
        the `column_names` *still have to contain* the index (first) column.
    dtype : type, optional
        Data ``type`` to cast to `pandas.read_csv`. By default, data type determination
        is left to `pandas`.
    check_num_columns : bool, optional
        If ``True`` and `column_names` passed, check is performed to verify that the
        `column_names` are consistent with the number of columns in the data file.
        This check will likely result in some slowdown as the file will be decompressed
        twice.

    Returns
    -------
    df_chunks : pandas.io.parsers.TextFileReader
        Generator of `pandas.DataFrame` chunks. Access by
        ``for chunk in df_chunks: ...``, where each chunk is a `pandas.DataFrame`.

    Raises
    ------
    DataParseError
        When ``check_num_columns is True`` and `column_names` are inconsistent with the
        number of columns in the data file being read.
    """
    if check_num_columns and column_names:
        file_name = Path(file_path).name
        num_cols = get_num_columns(file_path)
        if num_cols != len(column_names):
            raise DataParseError(
                f"{file_name} has {num_cols} columns, but column names "
                f"{column_names} were passed."
            )

    df_chunks = pandas.read_csv(
        file_path,
        compression=_get_compression(file_path),
        sep=r"\s+",
        header=None,
        index_col=None if not first_col_is_index else 0,
        names=column_names
        if not (column_names and first_col_is_index)
        else column_names[1:],
        chunksize=chunk_size,
        iterator=True,
        low_memory=False,
        dtype=dtype,
    )
    return df_chunks


def _get_compression(file_path):
    """Function extracting the file compression out of the `file_path` passed.

    Parameters
    ----------
    file_path : str or Path

    Returns
    -------
    str or NoneType
    """
    if str(file_path).endswith("bz2"):
        return "bz2"
    else:
        return None


def get_num_columns(file_path):
    """Gets the number of columns in the *.bz2* compressed either *.states*, or
    *.trans* file under the `file_path`.

    Parameters
    ----------
    file_path : str or Path

    Returns
    -------
    int
    """
    for chunk in load_dataframe_chunks(file_path, chunk_size=1):
        _, num_cols = chunk.shape
        return int(num_cols)


class DataClass:
    """Base class for all the data-classes used to store data from the parsed *.all*
    and *.def* files."""

    def __init__(self, **kwargs):
        for attr, val in kwargs.items():
            setattr(self, attr, val)

    def __repr__(self):
        cls_name = self.__class__.__name__
        attrs_str = ", ".join(f"{attr}={val}" for attr, val in vars(self).items())
        return f"{cls_name}({attrs_str})"
