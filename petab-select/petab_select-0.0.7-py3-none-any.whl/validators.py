import pandas as pd

from ModelSpace import get_model_space_df


def validate_model_space_file(
    filename: str
):
    model_space_df = get_model_space_df(filename)
    return validate_model_space_df(model_space_df)


def validate_model_space_df(
    model_space_df: pd.DataFrame,
):
    pass
