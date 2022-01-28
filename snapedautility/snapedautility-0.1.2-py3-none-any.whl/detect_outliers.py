import numpy as np
import pandas as pd
import altair as alt

def detect_outliers(s, width=250, height=250):
    """
    Detects outliers in a pandas series
    Returns a threshold value for the lower bound and upper bound of the outliers and Plot a violin plot of the observations
    Parameters
    ----------
    s : pandas.core.series.Series
        Pandas Series for which the outliers need to be found
    width: int, default = 250
        The width of the plot. Default set to 250
    height: int, default = 250
        The height of the plot. Default set to 250

    Returns
    -------
    List of integers
        Boolean array with same length as the input,
        indices of outlier marked.
    `altair plot`
        An interactive altair correlation plot
    Examples
    --------
    >>> from snapedautility.detect_outliers import detect_outliers 
    >>> s = pd.Series([1,1,2,3,4,5,6,9,10,13,40])
    >>> detect_outliers(s)
    [-8.0 , 20.0],  alt.Chart(...) 
    """
    if not isinstance(s, pd.Series):
        raise TypeError("s should be a pandas series")
    if s.shape[0] < 1:
        raise ValueError("s should have at least one element")
    if (not isinstance(height, int)) or (not isinstance(width, int)):
        raise TypeError("height and width should be integers")
        
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    factor = 1.5
    inter_quantile_range = q3 - q1

    df = s.rename("values").to_frame()

    # Box Plot
    plt = alt.Chart(df, title="Box Plot with Outliers").mark_boxplot().encode(
        x='values'
    ).properties(width=width, height=height)

    return [q1 - factor * inter_quantile_range, q3 + factor * inter_quantile_range], plt
    