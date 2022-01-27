import pandas as pd
import altair as alt
import numpy as np


def plot_corr(df, features=None, width=250, height=250):
    """
    Generates the pearson correlation plot for a list of numeric features in a given dataframe.

    Parameters
    ----------
    data : pandas.core.frame.DataFrame
        The input dataframe
    features : list
        List of feature names as string
        len(features) >=2
        None returns plot of all numeric features
    width: int, default = 250
        The width of the plot. Default set to 250
    height: int, default = 250
        The height of the plot. Default set to 250

    Returns
    -------
    `altair plot`
        An interactive altair correlation plot
    Examples
    --------
    >>> from snapedautility.plot_corr import plot_corr
    >>> df = penguins_data
    >>> plot_corr(df, ["Culmen Length (mm)", "Culmen Depth (mm)", 'Species'])
    """
    # Testing whether the input data frame is pd.DataFrame type
    if isinstance(df, pd.DataFrame) == False:
        raise TypeError("The thing you passed in `df` is not a valid Pandas DataFrame")

    # Tests whether input features is of the type list
    if features is not None:
        if not isinstance(features, list):
            raise TypeError("Please pass in a list for `features`")

    # Testing whether input features has at least two features
    if features is not None:
        if len(features) < 2:
            raise ValueError("At least two features should be selected")

    # Subsetting numerical features from the input dataframe
    if features is None:
        if df.select_dtypes(include="number").shape[1] < 2:
            raise ValueError("Dataframe should have at least two numerical features")
        else:
            df = df.select_dtypes(include="number")
    else:
        if df[features].select_dtypes(include="number").shape[1] < 2:
            raise ValueError(
                "The feature list you entered should have at least two numerical features"
            )
        else:
            df = df[features].select_dtypes(include="number")

    # Creating corr_df dataframe
    corr_df = df.corr().stack().reset_index(name="corr")
    corr_df["abs"] = corr_df["corr"].abs()

    # Correlation plot
    corr_plot = (
        alt.Chart(corr_df, title="Correlation Plot for Numerical Features")
        .mark_rect()
        .encode(
            x=alt.X("level_0", title="Numerical Features"),
            y=alt.Y("level_1", title="Numerical Features"),
            color=alt.Color(
                "corr",
                title="Correlation",
                scale=alt.Scale(domain=(-1, 1),scheme="purpleorange"),
            ),
            tooltip=alt.Tooltip("corr"),
        )
        .properties(width=width, height=height)
    )

    return corr_plot
