import pandas as pd


def standardize(series):
    return (series - series.mean()) / series.std()


def check_missing_dates(df, date_column="Date", frequency="MS"):
    print(pd.date_range(start=df[date_column].min(), end=df[date_column].max(), freq=frequency).difference(
        df[date_column]))
