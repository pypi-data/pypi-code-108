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

from profiling.utils import format_time, vega_sanitize


def partialdep(func: Callable[[pd.DataFrame], pd.Series], x: pd.DataFrame, var: str):
    """Plot partial dependence"""
    if is_categorical_dtype(x[var]):
        return partialdep_cat(func=func, x=x, var=var)
    elif is_bool_dtype(x[var]):
        return partialdep_cat(func=func, x=x, var=var)
    elif is_object_dtype(x[var]):
        return partialdep_cat(func=func, x=x, var=var)
    elif is_numeric_dtype(x[var]):
        return partialdep_num(func=func, x=x, var=var)
    elif is_datetime64_any_dtype(x[var]):
        return partialdep_datetime(func, x=x, var=var)
    else:
        pass


def flatten_index(df):
    """Flatten hiearchical column index"""
    df.columns = df.columns.to_flat_index()
    return df


def partialdep_num(
    func: Callable[[pd.DataFrame], pd.Series], x: pd.DataFrame, var: str
) -> alt.Chart:
    """Plot partial dependence for numerical variables"""
    non_missing = ~x[var].isna()
    x = x[non_missing]

    # Downsample large dataframes
    n_obs = len(x)
    n_max = 100
    if n_obs > n_max:
        id_sample = np.random.choice(n_obs, size=n_max, replace=False)
        x = x.iloc[id_sample]

    # Determine evaluation points (deciles)
    n_cut = 10
    if x[var].nunique() >= n_cut:
        quantiles = np.quantile(
            x[var],
            q=np.linspace(1 / (2 * n_cut), 1 - (1 / (2 * n_cut)), n_cut - 1),
            interpolation="nearest",
        )
    else:
        quantiles = np.sort(x[var].unique())

    # Calculate centered ICE plots
    df_ice = pd.DataFrame()
    for i, quantile in enumerate(quantiles):
        x_mod = x.copy()
        x_mod[var] = quantile
        pred_q = func(x_mod)

        if i == 0:
            offset = pred_q - np.mean(pred_q)  # for centering
            if isinstance(offset, pd.Series):
                offset = offset.values

        pred_q_centered = pred_q - offset
        df_ice_q = pd.DataFrame(
            {
                "id": np.arange(len(x_mod)),
                var: quantile,
                "Predicted Value": pred_q_centered,
            }
        )
        df_ice = df_ice.append(df_ice_q, ignore_index=True, sort=False)

    df_mean = df_ice.groupby(by=var, as_index=False).agg({"Predicted Value": "mean"})

    # Create plot
    var_sanitized = vega_sanitize(var, datatype="Q")

    lines = (
        alt.Chart(df_ice)
        .mark_line(strokeOpacity=0.3, color="grey", strokeWidth=2)
        .encode(
            x=var_sanitized,
            y=alt.Y("Predicted Value:Q", scale=alt.Scale(zero=False)),
            detail="id",
        )
    )
    mean = (
        alt.Chart(df_mean)
        .mark_line(strokeWidth=3, point=True)
        .encode(
            x=var_sanitized,
            y=alt.Y("Predicted Value:Q", scale=alt.Scale(zero=False)),
            tooltip=[
                alt.Tooltip(var_sanitized, format=".2f"),
                alt.Tooltip(f"Predicted Value:Q", format=".2f"),
            ],
        )
        .interactive()
    )
    return lines + mean


def partialdep_cat(
    func: Callable[[pd.DataFrame], pd.Series],
    x: pd.DataFrame,
    var: str,
    n_categories: int = 25,
    n_sample: int = 50,
) -> alt.Chart:
    """Plot partial dependence for categorical variables"""
    pred = func(x)

    df_agg = (
        x.assign(pred=pred)
        .astype({var: "category"})
        .groupby(var, as_index=False, observed=True)
        .agg({"pred": ["mean", "count"]})
        .pipe(flatten_index)
        .sort_values(("pred", "count"), ascending=False)
        .head(n_categories)  # keep most frequent
        .sort_values(("pred", "mean"), ascending=False)
        .rename(columns={(var, ""): var})
    )

    df_agg[var] = df_agg[var].cat.remove_unused_categories()
    ordered_categories = list(df_agg[var].cat.categories)

    df_plot = pd.DataFrame()

    for q in ordered_categories:
        x_mod = x.copy()
        x_mod[var] = pd.Series([q] * len(x), dtype=x[var].dtype)
        pred_q = func(x_mod)
        rowid = np.arange(len(x_mod))
        df_plot_q = pd.DataFrame(
            {"id": rowid, var: x_mod[var], "Predicted Value": pred_q.values}
        )
        df_plot = df_plot.append(df_plot_q, ignore_index=True, sort=False)

    # Convert to categorical for plotting
    df_plot[var] = (
        df_plot[var]
        .astype("category")
        .cat.add_categories("Missing")
        .fillna("Missing")
        .cat.remove_unused_categories()
    )

    df_plot_summary = (
        df_plot.groupby(var)
        .agg({"Predicted Value": "mean"})
        .sort_values("Predicted Value", ascending=False)
        .reset_index()
    )

    # Sample
    df_plot_sample = df_plot.query(f"id < {n_sample}")

    # Create plot
    var_sanitized = vega_sanitize(var, "N")

    lines = (
        alt.Chart(df_plot_sample)
        .mark_line(strokeOpacity=0.3, color="grey", strokeWidth=2)
        .encode(
            x=alt.X("Predicted Value", scale=alt.Scale(zero=False)),
            y=alt.Y(
                var_sanitized, sort=ordered_categories, scale=alt.Scale(zero=False),
            ),
            detail="id",
        )
    )
    mean = (
        alt.Chart(df_plot_summary)
        .mark_line(point=True, width=3)
        .encode(
            x="Predicted Value",
            y=alt.Y(
                var_sanitized, sort=ordered_categories, scale=alt.Scale(zero=False),
            ),
            tooltip=[
                alt.Tooltip(var_sanitized),
                alt.Tooltip(f"Predicted Value:Q", format=".2f"),
            ],
        )
        .interactive()
    )

    return lines + mean


def partialdep_datetime(
    func: Callable[[pd.DataFrame], pd.Series], x: pd.DataFrame, var: str
) -> alt.Chart:
    """Plot partial dependence for datetime variables"""
    non_missing = ~x[var].isna()
    x = x[non_missing]

    # Downsample large dataframes
    n_obs = len(x)
    n_max = 100
    if n_obs > n_max:
        id_sample = np.random.choice(n_obs, size=n_max, replace=False)
        x = x.iloc[id_sample]

    # Determine evaluation points (deciles)
    n_cut = 10
    if x[var].nunique() >= n_cut:
        quantiles = np.quantile(
            x[var],
            q=np.linspace(1 / (2 * n_cut), 1 - (1 / (2 * n_cut)), n_cut - 1),
            interpolation="nearest",
        )
    else:
        quantiles = np.sort(x[var].unique())

    # Calculate centered ICE plots
    df_ice = pd.DataFrame()
    for i, quantile in enumerate(quantiles):
        x_mod = x.copy()
        x_mod[var] = quantile
        pred_q = func(x_mod)

        if i == 0:
            offset = pred_q - np.mean(pred_q)  # for centering

        pred_q_centered = pred_q - offset
        df_ice_q = pd.DataFrame(
            {
                "id": np.arange(len(x_mod)),
                var: quantile,
                "Predicted Value": pred_q_centered,
            }
        )
        df_ice = df_ice.append(df_ice_q, ignore_index=True, sort=False)

    df_mean = df_ice.groupby(by=var, as_index=False).agg({"Predicted Value": "mean"})

    # Create plot
    var_sanitized = vega_sanitize(var, datatype="T")

    # Format datetimes correctly
    formatted_time = format_time(x, var)

    lines = (
        alt.Chart(df_ice)
        .mark_line(strokeOpacity=0.3, color="grey", strokeWidth=2)
        .encode(
            x=var_sanitized,
            y=alt.Y("Predicted Value:Q", scale=alt.Scale(zero=False)),
            detail="id",
        )
    )
    mean = (
        alt.Chart(df_mean)
        .mark_line(strokeWidth=3, point=True)
        .encode(
            x=var_sanitized,
            y=alt.Y("Predicted Value:Q", scale=alt.Scale(zero=False)),
            tooltip=[
                alt.Tooltip(var_sanitized, format=formatted_time),
                alt.Tooltip(f"Predicted Value:Q", format=".2f"),
            ],
        )
        .interactive()
    )
    return lines + mean
