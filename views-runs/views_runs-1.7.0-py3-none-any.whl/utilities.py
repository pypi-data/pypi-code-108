"""
views_runs.utilities
====================

Some utility functions ported from ViEWS 2, authored by Frederick Hoyles.

    resample:             Alter the distribution of binary values in a dataframe
    balance_panel_last_t: Ensure balanced panel form for dataframe
    assign_into_df:       Assign values from one dataframe into another
    merge_dfs:            Merge a list of unit-time indexed dataframes into one

"""
from typing import List
import functools

import numpy as np
import pandas as pd

def resample(
    df: pd.DataFrame,
    cols: List[str],
    pst_positives: float,
    pst_negatives: float,
    threshold=0,
):
    """
    resample
    ========

    parameters:
        df            (pandas.DataFrame)
        cols          (List[str])
        pst_positives (float)
        pst_negatives (float)
        threshold     (int)

    returns:
        pandas.DataFrame

    This function lets you resample a dataframe based on the desired retained
    percentage of positives and negatives in the column(s) specified in cols.

    Threshold is an integer that can be used to adjust what is defined as a
    "positive". With a threshold of 10, for example, the percentages affect
    values above and below 10, respectively.
    """

    # If both shares are 1 just return the unaltered df
    if pst_positives == 1 and pst_negatives == 1:
        return df

    # Negatives are rows where all cols are close to zero
    mask_negatives = np.isclose(df[cols], threshold).max(axis=1)
    # Positives are all the others
    mask_positives = ~mask_negatives

    df_positives = df.loc[mask_positives]
    df_negatives = df.loc[mask_negatives]

    len_positives = len(df_positives)
    len_negatives = len(df_negatives)

    n_positives_wanted = int(pst_positives * len_positives)
    n_negatives_wanted = int(pst_negatives * len_negatives)

    replacement_pos = pst_positives > 1
    replacement_neg = pst_negatives > 1
    df = pd.concat(
        [
            df_positives.sample(n=n_positives_wanted, replace=replacement_pos),
            df_negatives.sample(n=n_negatives_wanted, replace=replacement_neg),
        ]
    )
    return df

def balance_panel_last_t(df: pd.DataFrame) -> pd.DataFrame:
    """
    balance_panel_last_t
    ====================

    parameters:
        df (pandas.DataFrame): TIME-UNIT indexed dataframe

    returns:
        pandas:DataFrame

    "Balances" a time-unit indexed dataframe, making sure that all UNITs
    present at the last T are present for all T.
    """

    return df.reindex(
        pd.MultiIndex.from_product(
            [
                df.index.levels[0].unique(),
                df.loc[df.index.levels[0].max()].index.unique(),
            ],
            names=df.index.names,
        )
    ).sort_index()


def assign_into_df(df_to: pd.DataFrame, df_from: pd.DataFrame) -> pd.DataFrame:
    """
    assign_into_df
    ==============

    parameters:
        df_to   (pandas.DataFrame)
        df_from (pandas.DataFrame)

    returns:
        pandas.DataFrame

    Only assigns non-missing values from df_from, meaning the same column can
    be inserted multiple times and values be retained if the row coverage is
    different between calls.  So a df_a with col_a covering months 100-110 and
    df_b with col_a covering months 111-120 could be assigned into a single df
    which would get values of col_a for months 100 - 120.
    """

    for col in df_from:
        # Get a Series of the col for all rows
        s = df_from.loc[:, col]

        # Get the "is not null" boolean series to use as mask, ~ is NOT
        mask = ~s.isnull()

        # Get the index from that mask,
        # ix is now index labels of rows with (not missing) data
        ix = s.loc[mask].index
        try:
            df_to.loc[ix, col] = s.loc[ix]
        # Handle KeyError when assigning into a df without all times or locations
        except KeyError:
            try:
                # Only assign ix positions that exist in df_to
                ix = pd.MultiIndex.from_tuples(
                    [tup for tup in ix if tup in df_to.index]
                )
                df_to.loc[ix, col] = s.loc[ix]
            # If it still doesn't work we've got no ix in common.
            except TypeError:
                raise TypeError("No index positions in common.")

    return df_to

def merge_dfs(dfs: List[pd.DataFrame], how="inner")-> pd.DataFrame:
    """
    merge_dfs
    =========

    parameters:
        dfs (List[pandas.DataFrame])

    returns:
        pandas.DataFrame

    Merge a list of data frames using the dataframe indices.
    """

    return functools.reduce(
        lambda left, right: pd.merge(
            left, right, left_index=True, right_index=True, how=how
        ),
        dfs,
    )
