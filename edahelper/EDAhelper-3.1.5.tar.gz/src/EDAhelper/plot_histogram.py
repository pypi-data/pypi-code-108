import pandas as pd
import altair as alt


def plot_histogram(data, columns=["all"], num_bins=30):
    """
    Creates histograms for numerical features within a dataframe using Altair.

    Parameters
    ----------
    data : pd.DataFrame
        A pandas dataframe
    columns : list, default=["all"]
        A list of numerical features for which to create histograms, or by default will plot all numerical features in dataframe.
    num_bins : integer, default=30
        Number of bins in histogram plot, default is 30 bins.
    
    Returns
    ------
    plot : altair.Chart object
        An Altair plot for each specified numerical feature
    
    Examples
    --------
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B' : [1.5, 2.5, 3.5], 'C' : ['one', 'two', 'three']}),
    >>> plot_histogram(df, columns = ['A', 'B'])
    """

    # Check inputs
    if not isinstance(data, pd.DataFrame):
        raise TypeError("'data' should be a pandas.DataFrame object")

    if not isinstance(columns, list):
        raise TypeError("'columns' should be a list object")
        
    if not isinstance(num_bins, int):
        raise TypeError("'num_bins' should be an integer")
        
    if columns == ["all"]:
        numeric_cols = list(data.select_dtypes("number"))
    else:
        numeric_cols = columns

    plot = alt.Chart(data).mark_bar().encode(x=alt.X(alt.repeat(), type="quantitative", bin=alt.Bin(maxbins=num_bins)), y=alt.Y("count()")).properties(height=200, width=200).repeat(repeat=numeric_cols, columns=3)

    return plot