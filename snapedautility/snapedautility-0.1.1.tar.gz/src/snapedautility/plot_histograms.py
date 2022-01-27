import pandas as pd
import numpy as np
import altair as alt


def plot_histograms(df, features, facet_columns=3, width=125, height=125):
    """
    Plots histogram given numeric features of the input dataframe, and
    plots bar charts for categorical features of the input dataframe

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        Input dataframe
    features : list
        List of feature names as string
    facet_columns : int
        Number of columns in Facet options.
    width: int
        The width of sub-plot for each feature. Default set to 125
    height: int
        The height of sub-plot for each feature Default set to 125

    Returns
    -------
    `altair plot`
        Returns altair plot

    Examples
    --------
    >>> from snapedautility.plot_histograms import plot_histograms
    >>> df = penguins_data
    >>> plot_histograms(df, ["species", "bill_length_mm", "island"], 100, 100)
    """
    features_set = set(features)

    # Some basic validation on the function's input parameters.
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The data must be in type of Pandas DataFrame.")
    elif ((len(features) == 0) or (features_set.issubset(set(df.columns)) == False)):
        raise ValueError("All features must exist in the columns of the input Pandas DataFrame.")
    elif (not isinstance(width, int)) or (not isinstance(height, int)) or (height <= 0) or (width <= 0):
        raise ValueError("Width and height of the plot must be a positive integer")

    # Select categorical columns and numeric columns
    cat_cols = list(set(df.select_dtypes(include=["object"]).columns).intersection(features_set))
    numeric_cols = list(set(df.select_dtypes(include=np.number).columns).intersection(features_set))

    # Create alt.Chart for categorical features
    categorical_barplot = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(alt.repeat(), type='nominal'),
            y=alt.Y('count()', title="Count of Records"))
        .properties(width=width, height=height)
        .repeat(cat_cols, columns=facet_columns)
    )

    # Create alt.Chart for numeric features.
    numeric_barplot = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(alt.repeat(), type='quantitative', bin=alt.Bin(maxbins=30)),
            y=alt.Y('count()', title="Numberic Features"))
        .properties(width=width, height=height)
        .repeat(numeric_cols, columns=facet_columns)
    )

    #categorical_barplot
    histograms_plot = categorical_barplot & numeric_barplot
    histograms_plot.title = "Histograms for Specified Features"
    return histograms_plot