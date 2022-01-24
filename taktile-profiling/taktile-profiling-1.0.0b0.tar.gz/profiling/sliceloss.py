import logging
from typing import Callable

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

from profiling.metrics import getloss
from profiling.t import SliceLoss
from profiling.utils import format_time, vega_sanitize


def slice_loss(
    func: Callable[[pd.DataFrame], pd.Series],
    x: pd.DataFrame,
    y: pd.Series,
    var: str,
    loss: SliceLoss,
):
    """Plot loss metric by quantile/category"""
    if is_categorical_dtype(x[var]):
        return slice_loss_cat(func, x, y, var, loss)
    elif is_bool_dtype(x[var]):
        return slice_loss_cat(func, x, y, var, loss)
    elif is_object_dtype(x[var]):
        return slice_loss_cat(func, x, y, var, loss)
    elif is_numeric_dtype(x[var]):
        return slice_loss_num(func, x, y, var, loss)
    elif is_datetime64_any_dtype(x[var]):
        return slice_loss_datetime(func, x, y, var, loss)
    else:
        logging.warning("Data type not detected, will not generate slice loss")


def flatten_index(df: pd.DataFrame):
    """Flatten hiearchical column index"""
    df.columns = df.columns.to_flat_index()
    return df


def get_slice_metrics(df: pd.DataFrame, loss: SliceLoss):
    """Get the loss for a given data slice for the chosen variable"""

    df[loss] = getloss(loss).metric(df.__pred__, df.__y__)

    return df


def groupby_var_loss(df: pd.DataFrame, var: str, loss: SliceLoss, n_max: int):
    """Group the data by var and calculate the loss for each var sorting by prediction
    count and keep most frequent categories or times"""
    df_group = (
        df.groupby(var)
        .apply(get_slice_metrics, loss)
        .groupby(var, as_index=False, observed=True)
        .agg({loss: "mean", "__pred__": ["mean", "count"]})
        .pipe(flatten_index)
        .sort_values(("__pred__", "count"), ascending=False)
        .head(n_max)  # to keep most frequent categories or times
    )
    return df_group


def groupby_groups_loss(df: pd.DataFrame, var: str, loss: SliceLoss):
    """Group the data by quantiles and calculate the loss"""
    df_group = (
        df.groupby("taktile_num_groups")
        .apply(get_slice_metrics, loss)
        .groupby("taktile_num_groups")
        .agg({var: "mean", loss: ["mean", "count"]})
        .pipe(flatten_index)
        .rename(
            columns={
                (var, "mean"): var,
                (loss, "mean"): loss,
                (loss, "count"): "Counts",
            }
        )
        .reset_index(drop=True)
    )
    return df_group


def slice_loss_num(
    func: Callable[[pd.DataFrame], pd.Series],
    x: pd.DataFrame,
    y: pd.Series,
    var: str,
    loss: SliceLoss,
    n_cut: int = 10,
):
    """Loss metric plot by quantile for numerical variables"""

    non_missing = ~x[var].isna()
    x = x[non_missing]
    y = y[non_missing]
    pred = func(x).to_numpy()

    df = x.assign(__pred__=pred, __y__=y)

    if df[var].nunique() > n_cut:
        groupvar = df[var] + 1e-6 * np.random.uniform(size=len(df))
        df["taktile_num_groups"] = pd.qcut(groupvar, n_cut, duplicates="drop")
    else:
        df["taktile_num_groups"] = df[var]

    df_plot = groupby_groups_loss(df=df, var=var, loss=loss)

    var_sanitized = vega_sanitize(var, datatype="Q")

    chart = (
        alt.Chart(df_plot)
        .mark_line(opacity=0.9, point=True)
        .encode(
            x=alt.X(var_sanitized, scale=alt.Scale(zero=False)),
            y=alt.Y(loss, scale=alt.Scale(zero=False),),
            tooltip=[
                alt.Tooltip("Counts", title="Data Points", format="d"),
                alt.Tooltip(var_sanitized, format=".2f"),
                alt.Tooltip(loss, format=".2f"),
            ],
        )
        .configure_point(size=60)
        .interactive()
    )

    return chart


def slice_loss_cat(
    func: Callable[[pd.DataFrame], pd.Series],
    x: pd.DataFrame,
    y: pd.Series,
    var: str,
    loss: SliceLoss,
    n_categories: int = 25,
) -> alt.Chart:
    """Loss metric plot by category for categorical variables"""

    pred = func(x).to_numpy()

    df = x.assign(__pred__=pred, __y__=y).astype({var: "category"})

    df_plot = (
        groupby_var_loss(df=df, var=var, loss=loss, n_max=n_categories)
        .sort_values(("__pred__", "mean"), ascending=False)
        .rename(
            columns={
                (var, ""): var,
                (loss, "mean"): loss,
                ("__pred__", "count"): "Counts",
            }
        )
        .drop(columns=[("__pred__", "mean")])
    )

    df_plot[var] = df_plot[var].cat.remove_unused_categories()
    ordered_categories = list(df_plot[var].cat.categories)

    var_sanitized = vega_sanitize(var, datatype="N")

    chart = (
        alt.Chart(df_plot)
        .mark_circle(opacity=0.9)
        .encode(
            x=alt.X(loss, scale=alt.Scale(zero=False)),
            y=alt.Y(var, scale=alt.Scale(zero=False), sort=ordered_categories),
            tooltip=[
                alt.Tooltip("Counts", title="Data Points", format="d"),
                alt.Tooltip(var_sanitized),
                alt.Tooltip(loss, format=".2f"),
            ],
        )
        .interactive()
    )

    return chart


def slice_loss_datetime(
    func: Callable[[pd.DataFrame], pd.Series],
    x: pd.DataFrame,
    y: pd.Series,
    var: str,
    loss: SliceLoss,
    n_max: int = 100,
) -> alt.Chart:
    """Loss metric plot by quantile for datatime variables"""

    non_missing = ~x[var].isna()
    x = x[non_missing]
    y = y[non_missing]
    pred = func(x).to_numpy()

    df = x.assign(__pred__=pred, __y__=y)

    df_plot = (
        groupby_var_loss(df=df, var=var, loss=loss, n_max=n_max)
        .rename(
            columns={
                (var, ""): var,
                (loss, "mean"): loss,
                ("__pred__", "count"): "Counts",
            }
        )
        .drop(columns=[("__pred__", "mean")])
    )

    var_sanitized = vega_sanitize(var, datatype="T")

    # Format datetimes correctly
    formatted_time = format_time(x, var)

    chart = (
        alt.Chart(df_plot)
        .mark_line(opacity=0.9, point=True)
        .encode(
            x=alt.X(var, scale=alt.Scale(zero=False)),
            y=alt.Y(loss, scale=alt.Scale(zero=False),),
            tooltip=[
                alt.Tooltip("Counts", title="Data Points", format="d"),
                alt.Tooltip(var_sanitized, format=formatted_time),
                alt.Tooltip(loss, format=".2f"),
            ],
        )
        .configure_point(size=60)
        .interactive()
    )

    return chart
