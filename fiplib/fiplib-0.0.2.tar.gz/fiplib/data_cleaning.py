import pandas as pd


def nulls(df: pd.DataFrame):
    return df.isna().sum()


def duplicates(df: pd.DataFrame, column: str):
    result = df[df[column].duplicated()]
    return result


def info(df: pd.DataFrame, column: str):
    print("Nulls:\n{0}\n".format(nulls(df)))
    print("Duplicates:\n{0}\n".format(
        pd.DataFrame(duplicates(df, column))))
    return
