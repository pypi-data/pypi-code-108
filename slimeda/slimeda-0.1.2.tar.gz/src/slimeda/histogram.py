import altair as alt
import pandas as pd

def histogram(df, columns):
    """
    Creates histogram chart objects for specific columns in a data frame
    Parameters
    ----------
    df: pd.DataFrame
        pandas dataframe
    columns: list
        list of columns to create histograms for
    Returns
    -------
    Chart[]
    Examples
    --------
    >>>from slimeda import histogram
    >>>histogram(df, ['age', 'income'])
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("'df' should be of type pd.DataFrame")

    if not isinstance(columns, list):
        raise TypeError("'columns' should be of type list")

    if len(columns) == 0:
        raise ValueError("There should be at least column in the dataframe 'df' provided")

    for col in columns:
        if col not in df.columns:
            raise ValueError(f"The column {col} is not in the dataframe provided 'df'") 

    charts = []
    for col in columns:
        current_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(col, bin=True),
            y="count()"
        )
        charts.append(current_chart)
    return charts