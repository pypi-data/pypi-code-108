import pandas as pd
import altair as alt

def numeric_plots(df):
    """
    Creating a matrix of correlation plots with the numeric features.

    Parameters
    ----------
        df: pandas.dataframe
            A pandas dataframe

    Returns
    -------
        splom: Altair chart object
        The Altair object for the plots

    Example
    -------
    >>> from EDAhelper.numeric_plots import numeric_plots
    >>> splom = numeric_plot(df) 
    """

    # Data validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("'df' should be of type 'pandas.DataFrame'.")

    numeric_cols = df.select_dtypes(include=['float64', 'int64'])

    splom = alt.Chart(numeric_cols).mark_point(opacity=0.3, size=10).encode(
        alt.X(
            alt.repeat('row'),
            type='quantitative',
            scale=alt.Scale(zero=False)
        ),
        alt.Y(
            alt.repeat('column'),
            type='quantitative',
            scale=alt.Scale(zero=False)
        )
    ).properties(
        width=120,
        height=120
    ).repeat(
        column=list(numeric_cols.columns),
        row=list(numeric_cols.columns)
    ).configure_axis(
        labelFontSize=8,
        titleFontSize=8
    )

    return splom


print(numeric_plots.__doc__)
