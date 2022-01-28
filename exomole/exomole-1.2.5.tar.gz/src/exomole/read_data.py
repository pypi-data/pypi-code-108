"""Module containing functionality for reading ExoMole data files.

Two stand-alone functions are provided for reading *bz2*-compressed ExoMol files
with states (*.states.bz2* files) and with transitions (*.trans.bz2*).
"""

from pathlib import Path

from .exceptions import DataParseError, StatesParseError, TransParseError
from .utils import load_dataframe_chunks, get_num_columns


def states_chunks(states_path, chunk_size, columns):
    """
    Get a generator of chunks of the dataset *.states.bz2* file.

    Generator of `pandas.DataFrame` chunks of the *.states* file, with
    rows indexed by the values of the first column in the *.states* file.

    The `columns` argument passed needs to contain names for *all* the columns
    *including the first* column, which is assumed to be the `states` index.
    The first column `columns[0]` needs to be "i" as so it is explicitly asserted
    that it is included.

    The generated `pandas.DataFrames` are cast explicitly to ``dtype=str``,
    to avoid possible nasty surprises caused by `pandas` guessing the types itself.
    The index, however, is cast to "int64" explicitly.
    The columns can be re-casted downstream to the more appropriate data types
    for faster processing. An example for the energy column might be as follows:
    ``state_chunk['E'] = state_chunk['col'].astype('float64')``

    Parameters
    ----------
    states_path : str or Path
        Path to the *.states* file on the local file system.
    chunk_size : int
        Chunk size, should be chosen appropriately with regards to the RAM size.
        Roughly 1_000_000 per 1GB consumed.
    columns : iterable of str
        Column names for all the columns in the *.states* file including the (first)
        index column named "i".
        Therefore, ``len(columns)`` must be equal the number of actual columns
        in the *.states* file.

    Yields
    ------
    states_chunk : pandas.DataFrame
        Generated chunks of the *.states* file, each is a `pandas.DataFrame` with
        columns according to the `columns` passed, and indexed by the values in the
        first column in the *.states* file.
        The whole `DataFrame` is of string (``"O"``) data type, except the index, which
        is ``"int64"``.

    Raises
    ------
    StatesParseError
        If ``len(columns)`` inconsistent with the number of columns in the *.states*
        file.

    Examples
    --------
    >>> sp = "tests/resources/dummy_states_10x5_int_float_int_str_int.states.bz2"
    >>> states_columns = ["i", "col1", "col2", "col3", "col4"]
    >>> for df in states_chunks(states_path=sp, chunk_size=5, columns=states_columns):
    ...     print(df)  # synthetic, unphysical data as an example
    ...     break
                      col1 col2 col3 col4
    1   0.4745999608668017   88    a    4
    2  0.47729879282298115   90    b    7
    3  0.32392489118966217   57    c    6
    4   0.4704792592345922   95    d    1
    5   0.8168636898850669    6    e    9
    """
    if columns[0] != "i":
        raise StatesParseError("The first column of any .states file needs to be 'i'.")
    try:
        chunks = load_dataframe_chunks(
            file_path=states_path,
            chunk_size=chunk_size,
            first_col_is_index=True,
            column_names=columns,
            dtype=str,
            check_num_columns=True,
        )
    except DataParseError as e:
        raise StatesParseError(str(e))
    for chunk in chunks:
        chunk.index = chunk.index.astype("int64")
        yield chunk


def trans_chunks(trans_paths, chunk_size):
    """
    Get a generator of chunks of the dataset *.trans.bz* files.

    Generator of `pandas.DataFrame` chunks of all the *.trans* files passed as the
    `trans_paths` argument value.
    The columns are auto-named as ``"i", "f", "A_if" [, "v_if"]``.
    The ``"i"`` and ``"f"`` columns will correspond to the index of the `DataFrames`
    yielded by the `states_chunks` generator.
    No explicit data type casting is performed and `pandas` is trusted to correctly
    identify the ``"i"`` and ``"f"`` columns as ``"int64"`` and rest as ``"float64"``
    data types.

    Parameters
    ----------
    trans_paths : iterable of (str or Path)
        Paths to the *.trans* files on the local file system. They all need to belong to
        the same dataset, but no checks are made to assert that!
    chunk_size : int
        Chunk size, should be chosen appropriately with regards to RAM size, roughly
        10_000_000 per 1GB consumed.

    Yields
    ------
    trans_chunk : pd.DataFrame
        Generated chunks of all the *.trans* files, each is a `pandas.DataFrame` with
        auto-named columns.

    Raises
    ------
    TransParseError
        If the first *.trans* file has number of columns other than ``{3, 4}``.

    Examples
    --------
    >>> tr_paths = sorted(Path("tests/resources").glob("*.trans*0*.bz2"))
    >>> for tr_path in tr_paths:
    ...     print(tr_path)
    tests/resources/dummy_trans_5x4_int_int_float_float.trans01.bz2
    tests/resources/dummy_trans_5x4_int_int_float_float.trans02.bz2
    tests/resources/dummy_trans_5x4_int_int_float_float.trans03.bz2

    >>> for df in trans_chunks(trans_paths=tr_paths, chunk_size=3):
    ...     print(df)  # synthetic, unphysical data as an example
    ...     break
       i  f      A_if      v_if
    0  7  5  0.275477  0.121660
    1  6  8  0.446633  0.290420
    2  2  8  0.723996  0.426885
    """
    trans_paths = sorted(trans_paths)

    num_cols = get_num_columns(trans_paths[0])
    columns = ["i", "f", "A_if"]
    if num_cols == 4:
        columns.append("v_if")
    elif num_cols != 3:
        raise TransParseError(
            f"Unexpected number of columns in {Path(trans_paths[0]).name}: {num_cols}"
        )
    assert num_cols in {3, 4}
    # yield all the chunks from all the files:
    for file_path in trans_paths:
        chunks = load_dataframe_chunks(
            file_path=file_path, chunk_size=chunk_size, column_names=columns
        )
        for chunk in chunks:
            yield chunk
