import altair as alt
import pandas as pd

def histogram(df, x, y):
    """Plot a histogram with the magma color scheme

    Parameters
    ----------
    df : dataframe
        Dataframe containing the variables for plotting
    x : string
        Column name of the variable to be plotted on the x-axis
    y : string
        An aggregation function to be plotted on the y-axis.
        The supported aggregation operations are: ['average', 'count',
        'distinct', 'max', 'mean', 'median', 'min', 'missing', 'product',
        'q1', 'q3', 'ci0', 'ci1', 'stderr', 'stdev', 'stdevp', 'sum', 
        'valid', 'values', 'variance', 'variancep']

    Returns
    -------
    altair.vegalite.v4.api.Chart
        A histogram displaying distribution based on the aggregation function

    Examples
    --------
    >>> from magmaviz.histogram import histogram
    >>> histogram(mtcars, "cars", "count()")
    """
    # check if the type of df is a pandas DataFrame
    if not isinstance(df, pd.core.frame.DataFrame):
        raise TypeError(
            "'df' should be of type 'pandas.core.frame.DataFrame', a pandas dataframe."
        )
        
    # check if the type of x is a string
    if not isinstance(x, str):
        raise TypeError("'x' should be of type 'str'.")
              
    # check if x is a column in the dataframe
    if x not in list(df.columns):
        raise ValueError("The column specified for 'x' does not exist in the dataframe.")
    
    validate(df, y)
  
    chart = alt.Chart(df).mark_bar().encode(
        x=x,
        y=y,
        color=alt.Color(y, scale=alt.Scale(scheme="magma"))
    )
    return chart

def validate(df, y):
    """A helper function to validate input y
    Parameters
    ----------
    df : dataframe
        The input dataframe
    y : string
        The user specified aggregation function to be plotted on the y-axis.
        The supported aggregation operations are: ['average', 'count',
        'distinct', 'max', 'mean', 'median', 'min', 'missing', 'product',
        'q1', 'q3', 'ci0', 'ci1', 'stderr', 'stdev', 'stdevp', 'sum', 
        'valid', 'values', 'variance', 'variancep']
    Returns
    -------
        This function only raises errors
    Examples
    --------
    >>> validate(data.iris(), 'mean(petalLength)')
    >>> validate(data.iris(), 'count()')
    """
    supported_operations = ['average', 'count',
        'distinct', 'max', 'mean', 'median', 'min', 'missing', 'product',
        'q1', 'q3', 'ci0', 'ci1', 'stderr', 'stdev', 'stdevp', 'sum', 
        'valid', 'values', 'variance', 'variancep']
    # check if the type of y is a string
    if not isinstance(y, str):
        raise TypeError("'y' should be of type 'str'.")
  
    splited_y = y.split("(")
    function_name = splited_y[0]
    
    if len(splited_y) != 2:
        raise ValueError("'y' is not in a correct format as an aggregation function.")
    
    if function_name not in supported_operations:
        raise ValueError(
            "The aggregation function specified for 'y' " +
            "is not one of " + str(supported_operations))
        
    encoding_field = splited_y[1].split(')')[0]
    
    # For aggregation functions that need an encoding field, check if the input
    #   has one and is a valid column
    if function_name in ['average', 'distinct', 'max', 'mean', 
                         'median', 'min', 'missing', 'product',
                         'q1', 'q3', 'ci0', 'ci1', 'stderr', 'stdev', 
                         'stdevp', 'sum', 'valid', 'values', 'variance',
                         'variancep']:
        if encoding_field == '':
            raise ValueError(
            "The encoding field 'y' is specified without a type; " +
            "the type cannot be inferred because it does not match any column in the data"
            )
        
        if encoding_field not in list(df.columns):
            raise ValueError("The encoding field for 'y' does not exist in the dataframe.")