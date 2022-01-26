from typing import Callable, List

import altair as alt
import numpy as np
import pandas as pd

from profiling.metrics import getloss


def varimp(
    func: Callable,
    x: pd.DataFrame,
    profile_columns: List[str] = None,
    metric: str = "Rmse",
    n_max: int = 10000,
):

    # Sample from large dataframes
    if len(x) > n_max:
        sample = np.random.choice(len(x), n_max, replace=False)
        x = x.iloc[sample]

    # Baseline predictions
    pred = func(x)
    pred = np.array(pred)

    # Calculate change in predictions when permuting columns
    if profile_columns is None:
        profile_columns = x.columns

    loss = getloss(metric)
    results = {}

    for col in profile_columns:
        x_jumbled = x.copy()
        col_jumbled = x_jumbled[col].sample(frac=1, replace=True).values
        x_jumbled[col] = col_jumbled
        pred_jumbled = func(x_jumbled)
        loss_jumbled = loss.metric(pred_jumbled, pred)
        results[col] = loss_jumbled

    # Plot
    data = {"Variable": list(results.keys()), "Importance": list(results.values())}

    df = (
        pd.DataFrame.from_dict(data)
        .sort_values("Importance", ascending=loss.greater_is_better)
        .astype({"Variable": "category"})
    )

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x="Importance",
            y=alt.Y("Variable", sort=None),
            tooltip=[
                alt.Tooltip("Variable"),
                alt.Tooltip("Importance:Q", format=".2f"),
            ],
        )
    )

    # List of variables by importance
    varlist = df["Variable"].tolist()

    return chart, varlist
