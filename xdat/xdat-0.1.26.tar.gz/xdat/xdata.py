import pandas as pd
import numpy as np
from slugify import slugify
from munch import Munch as Dict
from . import xsettings, xpd


def read_csv(csv_path, na_values=None, low_memory=False):
    """
    A simple wrapper for read_csv that cleans it up a bit in the process..
    """
    na_values = xsettings.get_default(xsettings.NAN_TEXTS, na_values)

    df = pd.read_csv(csv_path, keep_default_na=False, na_values=na_values, low_memory=low_memory)
    xpd.x_clean_column_names(df, inplace=True)

    return df


def read_excel(excel_path, na_values=None):
    """
    A simple wrapper for read_excel that cleans it up a bit in the process,
      as well as returns a different dataframe for each sheet
    """
    na_values = xsettings.get_default(xsettings.NAN_TEXTS, na_values)

    res = pd.read_excel(excel_path, sheet_name=None, na_values=na_values)

    res_new = Dict()
    for k in list(res.keys()):
        k_new = slugify(k, separator='_')
        df = res[k]
        xpd.x_clean_column_names(df, inplace=True)
        assert k_new not in res_new, k_new
        res_new[k_new] = df

    return res_new


def filter_all_on(*args, on=None):
    """
    Given two or more dataframes, returns them filtered as if they went through an inner-join
    """

    assert on, "must provide 'on' parameter"
    if len(args) < 2:
        return args

    set_all = args[0][on].unique()
    for df in args[1:]:
        set_curr = df[on].unique()
        set_all = np.intersect1d(set_all, set_curr)

    filtered = []
    for df in args:
        df = df[df[on].isin(set_all)]
        filtered.append(df)

    return tuple(filtered)

