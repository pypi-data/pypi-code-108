import pandas as pd
import numpy as np


def preprocess(path, method=None, fill_value=None, read_func=pd.read_csv, **kwarg):
    """
    Preprocess data in txt, csv, Excel, etc. by dealing with missing values in numeric columns.

    Parameters
    ----------
    path : str
        The path of the data file.

    method : {None, 'most_frequent', 'mean', 'median', 'constant'},  default=None
        The imputation method.

        If None, then missing values are treated as numpy.NaN.

        If 'mean', then replace missing values using the mean along each column.

        If 'median', then replace missing values using the median along each column.

        If 'most_frequent', then replace missing using the most frequent value along each column. If there is more than one such value, only the smallest is returned.

        If 'constant', then replace missing values with fill_value.

    fill_value : {None, numerical values}, default=None
        When method='constant', fill_value is used to replace all occurrences of missing values.
        If left to the default, fill_value will be 0 when imputing numerical data.

    read_func : panadas.read_* function name, default=pandas.read_csv
        Any function reading data from pandas (e.g. read_csv, read_fwf, read_pickle).

    **kwarg : arbitrary keyword arguments
        Any keyword arguments are defined in @read_func.

    Returns
    -------
    pandas.DataFrame
        The processed table.

    Examples
    -------
    >>> from EDAhelper import EDAhelper
    >>> file_path = 'https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv'
    >>> EDAhelper.preprocess(file_path)
    """

    # Input check
    if not isinstance(path, str):
        raise Exception('Err msg: wrong path input')
    # if method not in (None, 'mean', 'median', 'most_frequent', 'constant'):
    #     raise Exception('Err msg: wrong method input')
    if (method == 'constant') & (fill_value is not None) & (not isinstance(fill_value, (float, int))):
        raise Exception("Err msg: wrong fill_value input when method = 'constant'")

    try:
        df = read_func(path, **kwarg)
    except Exception as e:
        raise e

    if method is None:
        return df

    df_num = df.select_dtypes(include='number')
    num_col = df_num.columns
    for col in num_col:
        if df[col].isnull().values.any():
            val_filled = 0
            if method == 'mean':
                val_filled = df[col].mean()
            elif method == 'median':
                val_filled = df[col].median()
            elif method == 'most_frequent':
                val_filled = df[col].mode()[0]
            elif method == 'constant':
                if fill_value:
                    val_filled = fill_value
            else:
                raise Exception('Err msg: wrong method input')

            df.loc[df[col].isnull(), col] = val_filled

    return df
