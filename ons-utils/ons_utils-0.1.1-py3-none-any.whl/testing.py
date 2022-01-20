"""Test suite utilities."""
from datetime import datetime
from typing import Any, Sequence, Tuple

import pandas as pd


## The following functions are useful for presenting test data in tests.
def to_date(dt: str) -> datetime:
    """Convert date string to datetime.datetime date."""
    return pd.Timestamp(dt).date()


def create_dataframe(data):
    """Create pandas df from tuple data with a header."""
    return pd.DataFrame.from_records(data[1:], columns=data[0])


def create_multi_column_df(data, column_levels):
    """Create pandas df from tuple data with multiple column levels."""
    m_idx = pd.MultiIndex.from_tuples(list(zip(*data[:column_levels])))
    return pd.DataFrame.from_records(data[column_levels:], columns=m_idx)


def create_df_with_multi_indices(
    data: Sequence[Tuple[Any]],
    column_labels: Sequence[str],
    index_labels: Sequence[str],
) -> pd.DataFrame:
    """Create DataFrame with multiple index and column levels.

    Parameters
    ----------
    data : sequence of tuple
        The data for the dataframe. The top x column data tuples (where
        x is the len of column_levels), should be y less in length
        (where y is the len of index_levels) than the remaining tuples.
        See example.
    column_labels : sequence of str
        The labels for the column levels.
    index_labels : sequence of str
        The labels for the index levels.

    Returns
    -------
    pandas DataFrame
        A dataframe with a multilevel indices corresponding to the data
        and given labels.

    Examples
    --------
    >>> df = create_df_with_multi_indices(
    ...     data = [
    ...         (                    'price',     'price',     'weight',    'weight'  ),
    ...         (                    'product_1', 'product_2', 'product_1', 'product_2'),
    ...         ('retailer_1', 'abc', 1.3,         1.3,         5,           6         ),
    ...         ('retailer_1', 'xyz', 1.3,         1.3,         5,           6         ),
    ...         ('retailer_2', 'abc', 1.3,         1.3,         5,           6         ),
    ...         ('retailer_2', 'xyz', 1.3,         1.3,         5,           6         ),
    ...     ],
    ...     column_labels=('value', 'product'),
    ...     index_labels=('retailer', 'group'),
    ... )
    >>> df
    value	           price	                weight
    product	           product_1	product_2	product_1	product_2
    retailer	group
    retailer_1	abc	   1.3	        1.3	        5	        6
                xyz	   1.3	        1.3	        5	        6
    retailer_2	abc	   1.3	        1.3	        5	        6
                xyz	   1.3	        1.3	        5	        6

    """
    if len(column_labels) == 1:
        column_index = pd.Index(data[0], name=column_labels[0])
    else:
        column_index = pd.MultiIndex.from_tuples(
            list(zip(*data[:len(column_labels)])),
            names=column_labels,
        )

    return (
        pd.DataFrame.from_records(data[len(column_labels):])
        .set_index(list(range(len(index_labels))))
        .rename_axis(index_labels)
        .set_axis(column_index, axis=1)
    )
