import pandas as pd


def ratio_per_category(df: pd.DataFrame, primary: str, secondary: str) -> pd.DataFrame:

    return (
        df.groupby([primary, secondary])
        .agg({secondary: "count"})
        .groupby(level=0)
        .apply(lambda x: x * 100 / x.sum())
        .rename({secondary: f"perc_{secondary}"}, axis=1)
        .reset_index()
    )
