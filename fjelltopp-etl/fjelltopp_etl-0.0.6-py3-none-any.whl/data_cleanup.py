import pandas as pd
from slugify import slugify
from etl import decorators

@decorators.log_start_and_finalisation("slugifing column names")
def slugify_column_name(df:pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        slugified_col = slugify(column)
        if slugified_col == column:
            continue
        df[slugified_col] = df[column]
        df.drop(columns=column, inplace=True)
    return df
