"""Implements filtering routines for dimensionality reduction.
    """

import numpy as np
import pandas as pd
from sklearn.preprocessing import scale as autoscale
import logging
from typing import Union

import qsarmodelingpy.lj_cut as lj


def variance_cut(X, cut):
    """Select only columns of `X` with a minimum variance `cut`.

    Args:
        X (DataFrame): The dataframe to be cutted
        cut (float): The minimum variance allowed

    Returns:
        list[int]: A list of all selected indexes.
    """
    v = np.var(X, 0, ddof=1)
    indCut = [i for i in range(len(v)) if v[i] >= cut]
    return indCut


def autoscale1(X):
    m, n = np.shape(X)
    means = np.mean(X, 0)
    stds = np.std(X, 0, ddof=1)
    Xm = X-np.ones((m, 1))*means
    Xa = np.divide(Xm, np.ones((m, 1)))
    return Xa


def correlation_cut(X, y, cut):
    """Select only columns of `X` with a minimum correlation `cut` with the dependent variable `y`.

    Args:
        X (DataFrame): The dataframe to be cutted
        y (DataFrame): The vector of dependent variable
        cut (float): The minimum correlation allowed

    Returns:
        list[int]: A list of all selected indexes.
    """
    corr = abs(np.dot(np.transpose(autoscale(X)), autoscale(y))/(len(y)-1))
    indCut = [i for i in range(len(corr)) if corr[i] >= cut]
    return indCut


def autocorrelation_cut(X: pd.DataFrame, y, cut):
    """Perform the matrix filtering based on autocorrelation.

    Args:
        X (DataFrame): The matrix to be filtered
        y (DataFrame): The vector of dependent variable
        cut (float): The filtering amount. If `cut == 1`, no cutting will be performed; if `cut == 0`, an empty list will be returned.

    Returns:
        list[int]: A list of all selected indexes.

    ## Example of use: 
    Let `X` and `y` be the dataset (matrix and vector). Then to perform an autocorrelation cut of 50%:

    ```python
    filtered_columns = autocorrelation_cut(X, y, 0.5)
    filtered_X = X.loc[:,filtered_columns]
    ```

    """
    m, n = X.shape
    Xcorr = np.corrcoef(X.T)
    var_filtered = []
    for i in range(n):
        for j in range(i+1, n):
            corr = Xcorr[i, j]
            if corr > cut:
                corr_i = abs(
                    np.dot(np.transpose(autoscale(X[:, i])), autoscale(y))/(m-1))
                corr_j = abs(
                    np.dot(np.transpose(autoscale(X[:, j])), autoscale(y))/(m-1))
                if corr_i < corr_j:
                    if i not in var_filtered:
                        var_filtered.append(i)
                else:
                    if j not in var_filtered:
                        var_filtered.append(j)
    var = [i for i in range(n) if i not in var_filtered]
    return var


def filter_matrix(
    X: pd.DataFrame,
    y,
    lj_transform: bool = False,
    var_cut: float = 0,
    corr_cut: float = 0,
    auto_corrcut: float = 1,
) -> pd.DataFrame:
    """Perform Lennard-Jones data transformation, variance cut, correlation cut and autocorrelation cut.

    While others methods in this class returns a list of indexes, `qsarmodelingpy.filter.filter_matrix` returns the filtered matrix ([`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)).

    Args:
        X (DataFrame): The matrix to be filtered.
        y (DataFrame): The dependent variable
        lj_transform (bool, optional): Wether or not to perform Lennard-Jones Data Tranformation (see `qsarmodelingpy.lj_cut`). Defaults to False.
        var_cut (float, optional): See `qsarmodelingpy.filter.variance_cut`. Defaults to 0.
        corr_cut (float, optional): See `qsarmodelingpy.filter.correlation_cut`. Defaults to 0.
        auto_corrcut (float, optional): See `qsarmodelingpy.filter.autocorrelation_cut`. Defaults to 1.

    Returns:
        DataFrame: The filtered matrix.
    """
    # Pre processing
    if lj_transform:
        X = lj.transform(X)

    logging.info(f"Dimensions of the original matrix: {X.shape}")
    # logging.info(X.shape)

    # Variance Cut
    indVar = variance_cut(X.values, var_cut)
    X = X.loc[:, X.columns[indVar]]

    logging.info(f"Dimensions of the matrix after variance cut: {X.shape}")
    # logging.info(X.shape)

    # Correlation Cut
    indCorr = correlation_cut(X.values, y, corr_cut)
    X = X.loc[:, X.columns[indCorr]]

    logging.info(f"Dimensions of the matrix after correlation cut: {X.shape}")
    # logging.info(X.shape)

    # Autocorrelation cut
    indAuto = autocorrelation_cut(X.values, y, auto_corrcut)
    X = X.loc[:, X.columns[indAuto]]

    logging.info(f"Dimensions of the matrix after auto correlation cut: {X.shape}")
    # logging.info(X.shape)

    return X
