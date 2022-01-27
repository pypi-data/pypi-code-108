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
        .transform_fold(cat_cols)
        .mark_bar()
        .encode(alt.X("value:N"), y="count()")
        .properties(width=width, height=height)
        .facet(facet="Categorical Features:N", columns=facet_columns)
    )

    # Create alt.Chart for numeric features.
    numeric_barplot = (
        alt.Chart(df)
        .transform_fold(numeric_cols)
        .mark_bar()
        .encode(alt.X("value:Q", title="value", bin=True), y="count()")
        .properties(width=width, height=height)
        .facet(facet="Numeric Features:N", columns=facet_columns)
        .resolve_scale(x="independent")
    )

    histograms_plot = categorical_barplot & numeric_barplot
    histograms_plot.title = "Histograms for Specified Features"
    return histograms_plot