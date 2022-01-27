import pandas as pd
import numpy as np
import csv

def daily_growth_rate(df, col_name):

    """Function to calculate daily growth rate 
    Parameters
    ----------
    df : pandas DataFrame
        Data frame with date and price data.
    col_name: str
        Name of the column holding daily ending price data. 

    Returns
    -------
    df:
        A dataframe with a new column of daily growth rate

    Examples
    -------
    >>> daily_growth_rate(price_df, closing_price)
               
    """
    # Test whether input data is of pd.DataFrame type
    if not isinstance(df, pd.DataFrame):
        raise TypeError("The input dataframe must be of pd.DataFrame type")

    # Test whether input "col_name" is a string
    if not isinstance(col_name, str):
        raise TypeError("The input name of column must be of string type")
    
    # Test whether input col_name is of type numbers
    if df[col_name].dtype != np.float64:
        raise TypeError("input col_name must be of float type")
    
        
    return  pd.DataFrame({"daily_growth_rate": df[col_name].pct_change()})
    
    
    
