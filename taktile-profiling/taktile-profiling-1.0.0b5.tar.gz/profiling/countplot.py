import logging

import altair as alt
import numpy as np
import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

from profiling.utils import vega_sanitize


def countplot(x_var: pd.Series):
    """Plot loss metric by quantile/category"""
    if is_categorical_dtype(x_var) or is_bool_dtype(x_var) or is_object_dtype(x_var):
        return countplot_cat(x_var)
    elif is_numeric_dtype(x_var):
        return countplot_num(x_var)
    elif is_datetime64_any_dtype(x_var):
        return countplot_datetime(x_var)
    else:
        logging.warning(
            f"Data type ({x_var.dtype}) not detected for {x_var.name}, will not generate count plot"
        )


def trim_outliers(x_var: pd.Series, n_std=4) -> pd.Series:
    """Remove values +/- n_std standard deviations from the mean."""
    mean = np.mean(x_var)
    std = np.std(x_var)

    return x_var[(x_var <= (mean + n_std * std)) & (x_var >= (mean - n_std * std))]


def get_bins(x_var: pd.Series, n_bins=25) -> pd.DataFrame:
    """Divide the numerical series into equally spaced bins."""
    return (
        pd.cut(x_var, bins=n_bins)
        .map(lambda x: (x.right + x.left) / 2)  # get interval midpoint
        .value_counts()
        .rename("Counts")
        .reset_index()
        .rename(columns={"index": x_var.name})
    )


def countplot_num(x_var: pd.Series) -> alt.Chart:
    """Plot counts by bins for numerical variables."""
    non_missing = ~x_var.isna()
    x_var = x_var[non_missing]

    x_var = trim_outliers(x_var)
    df_bins = get_bins(x_var)

    var_sanitized = vega_sanitize(
        x_var.name, datatype="Q"
    )  # format as quantitative type

    return alt.Chart(df_bins).mark_bar().encode(x=var_sanitized, y="Counts")


def countplot_cat(x_var: pd.Series, n_categories: int = 25) -> alt.Chart:
    """Plot counts by category for categorical variables."""
    var = x_var.name
    non_missing = ~x_var.isna()
    x_var = x_var[non_missing]

    df = (
        x_var.astype({var: "category"})
        .value_counts()
        .rename("Counts")
        .reset_index()
        .rename(columns={"index": var})
        .sort_values(by="Counts", ascending=False)
        .head(n_categories)
    )

    if is_categorical_dtype(x_var) == False:
        df[var] = df[var].cat.remove_unused_categories()
        ordered_categories = list(df[var].values)  # sort unordered uncategorical
    elif x_var.cat.ordered:
        ordered_categories = x_var.cat.categories
        df[var].cat.categories = ordered_categories
        df[var] = df[var].cat.remove_unused_categories()
        ordered_categories = list(df[var].cat.categories)
    else:
        df[var] = df[var].cat.remove_unused_categories()
        ordered_categories = list(df[var].values)  # sort unordered categories

    var_sanitized = vega_sanitize(var, datatype="N")  # format as nominal type

    return (
        alt.Chart(df)
        .mark_bar()
        .encode(x="Counts", y=alt.Y(var_sanitized, sort=ordered_categories))
    )


def countplot_datetime(x_var: pd.Series) -> alt.Chart:
    """Plot counts by bins for datetime variables."""
    non_missing = ~x_var.isna()
    x_var = x_var[non_missing]
    dateime_dtype = x_var.dtype

    x_var = trim_outliers(pd.to_numeric(x_var))
    df_bins = get_bins(x_var).astype({x_var.name: dateime_dtype})

    var_sanitized = vega_sanitize(x_var.name, datatype="T")  # format as datetime

    return alt.Chart(df_bins).mark_bar().encode(x=var_sanitized, y="Counts")
