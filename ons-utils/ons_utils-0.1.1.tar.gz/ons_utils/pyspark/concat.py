"""A dataframe concatenation function for PySpark."""
from collections import abc
import functools
from typing import (
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)
import warnings

import pandas as pd
from pyspark.sql import (
    DataFrame as SparkDF,
    functions as F,
)

from ons_utils.generic import list_convert

Key = Sequence[Union[str, Sequence[str]]]

# The order of these is important, big ---> small.
SPARK_NUMBER_TYPES = (
    'decimal(10,0)',
    'double',
    'float',
    'bigint',
    'int',
    'smallint',
    'tinyint',
)


def concat(
    frames: Union[Iterable[SparkDF], Mapping[Key, SparkDF]],
    keys: Optional[Key] = None,
    names: Optional[Union[str, Sequence[str]]] = None,
) -> SparkDF:
    """
    Concatenate pyspark DataFrames with additional key columns.

    Will attempt to cast column data types where schemas are mismatched
    and fill empty columns with Nulls:

    * upcasts to largest number data type present (for that column)
    * casts to string if there is at least one dtype of 'string' for a
      given column

    Parameters
    ----------
    frames : a sequence or mapping of SparkDF
        If a mapping is passed, then the sorted keys will be used as the
        `keys` argument, unless it is passed, in which case the values
        will be selected.
    keys : a sequence of str or str sequences, optional
        The keys to differentiate child dataframes in the concatenated
        dataframe. Each key can have multiple parts but each key should
        have an equal number of parts. The length of `names` should be
        equal to the number of parts. Keys must be passed if `frames` is
        a sequence.
    names : str or list of str, optional
        The name or names to give each new key column. Must match the
        size of each key.

    Returns
    -------
    SparkDF
        A single DataFrame combining the given frames with a
        ``unionByName()`` call. The resulting DataFrame has new columns
        for each given name, that contains the keys which identify the
        child frames.

    Notes
    -----
    This code is mostly adapted from :func:`pandas.concat`.
    """
    if isinstance(frames, (SparkDF, str)):
        raise TypeError(
            "first argument must be an iterable of pyspark DataFrames,"
            f" you passed an object of type '{type(frames)}'"
        )

    if len(frames) == 0:
        raise ValueError("No objects to concatenate")

    if isinstance(frames, abc.Sequence):
        if keys and (len(frames) != len(keys)):
            raise ValueError(
                "keys must be same length as frames"
                " when frames is a list or tuple"
            )

    if isinstance(frames, abc.Mapping):
        if names is None:
            raise ValueError(
                "when the first argument is a mapping,"
                " the names argument must be given"
            )
        if keys is None:
            keys = list(frames.keys())
        # If keys are passed with a mapping, then the mapping is subset
        # using the keys. This also ensures the order is correct.
        frames = [frames[k] for k in keys]
    else:
        frames = list(frames)

    for frame in frames:
        if not isinstance(frame, SparkDF):
            raise TypeError(
                f"cannot concatenate object of type '{type(frame)}'; "
                "only pyspark.sql.DataFrame objs are valid"
            )

    schemas_df = _get_schemas_df(frames, keys, names)
    schemas_are_equal = _compare_schemas(schemas_df)

    # Allows dataframes with inconsistent schemas to be concatenated by
    # filling empty columns with Nulls and casting some column data
    # types where appropriate.
    #
    # Potentially remove when Spark 3.1.0 available.
    if not schemas_are_equal:
        frames = [
            _ensure_consistent_schema(frame, schemas_df)
            for frame in frames
        ]

    # Potentially update with commented line when Spark 3.1.0 available.
    # union = functools.partial(SparkDF.unionByName, allowMissingColumns=True)
    union = SparkDF.unionByName

    # If no keys or names are given then simply union the DataFrames.
    if not names and not keys:
        return functools.reduce(union, frames)

    # Convert names and keys elements to a list if not already, so they
    # can be iterated over in the next step.
    names = list_convert(names)
    keys = [list_convert(key) for key in keys]

    if not all([len(key) == len(names) for key in keys]):
        raise ValueError(
            "the length of each key must equal the length of names"
        )
    if not all([len(key) == len(keys[0]) for key in keys]):
        raise ValueError(
            "all keys must be of equal length"
        )

    frames_to_concat = []
    # Loop through each frame, and add each part in the keys to a new
    # column defined by name.
    for parts, frame in zip(keys, frames):
        for name, part in reversed(tuple(zip(names, parts))):
            frame = frame.select(F.lit(part).alias(name), '*')
        frames_to_concat.append(frame)

    return functools.reduce(union, frames_to_concat)


def _ensure_consistent_schema(
    frame: SparkDF,
    schemas_df: pd.DataFrame,
) -> SparkDF:
    """Ensure the dataframe is consistent with the schema.

    If there are column data type mismatches, (more than one data type
    for a column name in the column schemas) then will try to convert
    the data type if possible:

    * if they are all number data types, then picks the largest number
      type present
    * if one of the types is string, then ensures it casts the column to
      string type

    Also fills any missing columns with Null values, ensuring correct
    dtype.

    Parameters
    ----------
    frame : SparkDF
    column_schemas : set
        A set of simple column schemas in the form (name, dtype) for all
        dataframes set to be concatenated.

    Returns
    -------
    SparkDF
        Input dataframe with consistent schema.
    """
    final_schema = _get_final_schema(schemas_df)
    missing_fields = [f for f in final_schema if f not in frame.dtypes]

    for column, dtype in missing_fields:
        # If current frame missing the column in the schema, then
        # set values to Null.
        vals = (
            F.lit(None) if column not in frame.columns
            else F.col(column)
        )
        # Cast the values with the correct dtype.
        frame = frame.withColumn(column, vals.cast(dtype))

    return frame


def _get_final_schema(
    schemas_df: pd.DataFrame
) -> Sequence[Tuple[str, str]]:
    """Get the final schema by coercing the types."""
    # For a given column, if one of the types is string coerce all types
    # to string.
    schemas_df = schemas_df.mask(
        schemas_df.eq('string').any(axis=1),
        'string',
    )

    # For a given column, if all types are number types coerce all types
    # to the largest spark number type present.
    number_types = (
        schemas_df
        .fillna('int')
        .isin(SPARK_NUMBER_TYPES)
        .all(axis=1)
    )
    largest_num_types = schemas_df[number_types].apply(
        lambda row: _get_largest_number_dtype(row.to_list()),
        axis=1,
    )
    schemas_df = schemas_df.mask(number_types, largest_num_types, axis=0)

    if not _check_equal_schemas(schemas_df).all():
        raise TypeError(
            "Spark column data type mismatch, can't auto-convert between"
            f" types. \n\n{str(schemas_df[~_check_equal_schemas(schemas_df)])}"
        )
    # Return the final schema.
    return [
        (name, dtype)
        # Only need the first two columns.
        for name, dtype, *_ in schemas_df.reset_index().to_numpy()
    ]


def _get_largest_number_dtype(dtypes: Sequence[str]) -> str:
    """Return the largest Spark number data type in the input."""
    return next((
        dtype for dtype in SPARK_NUMBER_TYPES
        if dtype in dtypes
    ))


def _compare_schemas(schemas_df: pd.DataFrame) -> bool:
    """Return True if schemas are equal, else throw warning.

    If unequal, throws a warning that displays the schemas for all the
    unequal columns.

    Parameters
    ----------
    schemas_df : pandas DataFrame
        A dataframe of schemas with columns along the index, dataframe
        name across the columns and the dtypes as the values. Create
        with :func:`_get_schemas_df`.

    Returns
    -------
    bool
        True if column schemas are equal, else False.
    """
    equal_schemas = _check_equal_schemas(schemas_df)

    # Fill types across missing columns. We only want to raise a warning
    # if the types are different.
    schemas_df_filled = schemas_df.bfill(1).ffill(1)
    equal_ignoring_missing_cols = _check_equal_schemas(schemas_df_filled)

    if not equal_ignoring_missing_cols.all():
        warnings.warn(
            "column dtypes in the schemas are not equal, attempting to coerce"
            f"\n\n{str(schemas_df.loc[~equal_schemas])}",
            UnequalSchemaWarning,
        )
        return False
    elif not equal_schemas.all():
        return False
    else:
        return True


def _check_equal_schemas(df: pd.DataFrame) -> pd.DataFrame:
    """Checks that the first schema matches the rest."""
    return df.apply(lambda col: col.eq(df.iloc[:, 0])).all(axis=1)


def _get_schemas_df(
    frames: Sequence[pd.DataFrame],
    keys: Optional[Key] = None,
    names: Optional[Union[str, Sequence[str]]] = None,
) -> pd.DataFrame:
    """Return dataframe of column schemas for given frames."""
    schemas_df = pd.DataFrame()
    for df in frames:
        col_names, dtypes = zip(*df.dtypes)
        schema = pd.Series(dtypes, index=col_names)
        schemas_df = pd.concat([schemas_df, schema], axis=1)

    if keys:
        keys = [list_convert(key) for key in keys]
        names = list_convert(names) if names else names
        schemas_df.columns = pd.MultiIndex.from_tuples(keys, names=names)
    else:
        schemas_df.columns = [f'dtype_{i+1}' for i in range(len(frames))]

    return schemas_df


class UnequalSchemaWarning(Warning):
    pass
