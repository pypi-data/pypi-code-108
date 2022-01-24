import logging
from typing import Callable, List, Tuple

import altair as alt
import numpy as np
import pandas as pd

from profiling.metrics import getloss
from profiling.utils import df_to_json_table


def metrics(
    func: Callable[[pd.DataFrame], pd.Series], x: pd.DataFrame, y: pd.Series, kind: str
) -> str:
    if kind == "regression":
        loss_list = ["Rmse", "Mae", "TrimmedRmse", "MeanPrediction", "MeanActual"]
    elif kind == "binary":
        loss_list = ["Accuracy", "AUC", "MeanPrediction", "MeanActual"]
    else:
        raise NotImplementedError(f"Unknown endpoint kind: {kind}")

    pred = func(x)
    losses = [getloss(ll) for ll in loss_list]
    loss_names = [loss.name for loss in losses]
    loss_values = [loss.metric(pred, y) for loss in losses]
    table = pd.DataFrame({"Metric": loss_names, "Value": loss_values})

    return df_to_json_table(table, date_format="iso", date_unit="s", double_precision=2)


def largest_errors(
    func: Callable[[pd.DataFrame], pd.Series],
    x: pd.DataFrame,
    y: pd.Series,
    profile_columns: List[str],
    n: int = 25,
) -> str:
    """Return observations with largest errors in predictions"""
    pred = func(x).to_numpy()
    y = y.to_numpy()  # to avoid issues due to indices

    df = (
        x[profile_columns]
        .assign(y=y, pred=pred)  # to numpy is needed to help time inference
        .astype({"y": float, "pred": float})  # account for boolean output/predictions
        .assign(Delta=lambda k: np.abs(k["y"] - k["pred"]))
    )

    df = df.sort_values("Delta", ascending=False).head(n)
    df = df.rename(columns={"pred": "Predicted Value", "y": "Actual Value"})

    # Move new columns to the beginning
    cols = df.columns.to_list()
    first = ["Predicted Value", "Actual Value", "Delta"]
    last = [c for c in cols if c not in first]
    df = df.reindex(columns=first + last)

    return df_to_json_table(df, date_format="iso", date_unit="s", double_precision=2)


def calibration(
    func: Callable[[pd.DataFrame], pd.Series],
    x: pd.DataFrame,
    y: pd.Series,
    bins: int = 10,
) -> alt.Chart:
    """Plot calibration"""
    preds = func(x).to_numpy()
    pred_grp = pd.qcut(preds, q=bins, duplicates="drop")

    df = pd.DataFrame(
        # conversion to numpy is required so booleans are handled correctly
        {"Actual Value": y.to_numpy(), "Predicted Value": preds, "Group": pred_grp}
    )
    df = df.groupby("Group").agg("mean").reset_index().drop(columns=["Group"])

    # Set aspect ratio to 1
    min_val = df[["Predicted Value", "Actual Value"]].min().min()
    max_val = df[["Predicted Value", "Actual Value"]].max().max()
    line_length = max_val - min_val
    domain = (min_val - 0.1 * line_length, max_val + 0.1 * line_length)
    df_diagonal = pd.DataFrame({"Predicted Value": domain, "Actual Value": domain})

    diagonal_line = (
        alt.Chart(df_diagonal)
        .mark_line(strokeDash=[1, 1])
        .encode(
            x=alt.X("Predicted Value:Q", scale=alt.Scale(domain=domain)),
            y=alt.Y("Actual Value:Q", scale=alt.Scale(domain=domain)),
        )
    )

    points = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("Predicted Value:Q", scale=alt.Scale(domain=domain)),
            y=alt.Y("Actual Value:Q", scale=alt.Scale(domain=domain)),
            tooltip=[
                alt.Tooltip("Predicted Value:Q", format=".2f"),
                alt.Tooltip("Actual Value:Q", format=".2f"),
            ],
        )
        .interactive()
    )

    return diagonal_line + points


def binary_tpr_fpr(y: np.array, preds: np.array) -> Tuple[np.array, np.array]:
    """Return the true postive rates and false postive rates for different binary classification thresholds.
    Inspired by: https://github.com/scikit-learn/scikit-learn/blob/95119c13af77c76e150b753485c662b7c52a41a2/sklearn/metrics/_ranking.py#L653
    (License: BSD-3)
    """
    # Sort by predicted probability
    sorted_prob_idx = np.argsort(preds)[::-1]

    y = y[sorted_prob_idx]
    preds = preds[sorted_prob_idx]

    # Choose unique probabilities
    distinct_threshold_idx = np.where(np.diff(preds))[0]
    threshold_idx = np.concatenate([distinct_threshold_idx, [y.size - 1]])

    # Sum the total true positives and false positives for each threshold
    tp_cumsum = np.cumsum(y)[threshold_idx]
    fp_cumsum = np.cumsum(1 - y)[threshold_idx]

    tp_cumsum = np.concatenate([[0], tp_cumsum])
    fp_cumsum = np.concatenate([[0], fp_cumsum])

    if fp_cumsum[-1] <= 0:
        logging.warning("No false values in y")
        fpr = np.repeat(0, fp_cumsum.shape)
    else:
        fpr = fp_cumsum / fp_cumsum[-1]

    if tp_cumsum[-1] <= 0:
        logging.warning("No true values in y")
        tpr = np.repeat(0, tp_cumsum.shape)
    else:
        tpr = tp_cumsum / tp_cumsum[-1]

    return tpr, fpr


def roc_curve(
    func: Callable[[pd.DataFrame], pd.Series], x: pd.DataFrame, y: pd.Series,
) -> alt.Chart:
    """Plot ROC curve for binary endpoints"""

    preds = func(x).to_numpy()
    y = y.to_numpy()

    tpr, fpr = binary_tpr_fpr(y, preds)

    roc_curve_df = pd.DataFrame({"False Positive Rate": fpr, "True Positive Rate": tpr})

    # Subset df for smaller vega specs
    subset = np.unique(np.round(np.linspace(0, len(roc_curve_df) - 1, num=1000)))
    roc_curve_df = roc_curve_df.iloc[subset, :]

    # Add the 45 degree line for the random classifier
    dotted_line_df = pd.DataFrame(
        {"False Positive Rate": [0, 1], "True Positive Rate": [0, 1],}
    )

    roc_curve = (
        alt.Chart(roc_curve_df)
        .mark_line()
        .encode(
            x=alt.X("False Positive Rate", axis=alt.Axis(format="%")),
            y=alt.Y("True Positive Rate", axis=alt.Axis(format="%")),
            tooltip=[
                alt.Tooltip("False Positive Rate", format=".2%"),
                alt.Tooltip("True Positive Rate", format=".2%"),
            ],
        )
        .interactive()
    )

    dotted_line = (
        alt.Chart(dotted_line_df)
        .mark_line(strokeDash=[1, 1])
        .encode(
            x=alt.X("False Positive Rate", axis=alt.Axis(format="%"),),
            y=alt.Y("True Positive Rate", axis=alt.Axis(format="%"),),
        )
    )

    return roc_curve + dotted_line
