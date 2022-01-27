import pandas as pd
import numpy as np

def summary_suggestions(df, threshold = 0.8):
    """Takes in a pandas dataframe and returns a list object comprising
    of 3 dataframes and a list. The dataframes correspond to the
    summary statistics of numeric and categorical variables each and
    the proportion of unique values for categorical variables. The 
    nested list is of the categorical variables that exceed the threshold
    for considering dropping variables with high unique values.

    Parameters
    ----------
    df : pandas dataframe
        Dataframe to be examined

    threshold : float
        threshold for considering dropping variables with high unique values

    Returns
    -------
    results : list
        List of summary dataframes

    Examples
    --------
    >>> summary_suggestions(df)

    [
    (summary statistics for numeric variables),
    (summary statistics for categorical variables),
    (percentage of unique values for categorical variables),
    [list of variables with percentage of unique values higher than the threshold]
    ]
    
    """

    # check if input is a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input df must be a pandas dataframe object")

    if not ((type(threshold) == float) | (type(threshold) == int)):
        raise TypeError("Input threshold must be a float value between 0 and 1")

    if not (0 < threshold < 1):
        raise TypeError("Input threshold must be a float value between 0 and 1")

    numeric_summary_df = df.select_dtypes(include=np.number).describe()
    categorical_summary_df = df.select_dtypes(include=np.object_).describe()

    results = []
    results.extend([numeric_summary_df, categorical_summary_df])

    unique_val_df = categorical_summary_df[categorical_summary_df.index == 'unique']/len(df)
    filtered_unique_val_df = unique_val_df.loc['unique'] > threshold
    unique_val_vars = [*filter(filtered_unique_val_df.get, filtered_unique_val_df.index)]

    results.extend([unique_val_df, unique_val_vars])
    return results
    