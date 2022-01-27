import numpy as np
import pandas as pd
import numpy as np
import re


import numpy as np
import pandas as pd
import re

def get_matching_column_names(data, pattern):
    """Returns a subset of the columns whose names match the pattern.
    
    Matching columns are columns whose names start
    with the given pattern and end with an incrementing integer.
    
    Parameters
    ----------
    data : pandas dataframe
        The dataframe from which to extract columns
    pattern : string
        The prefix of the column names to extract
        
    Returns
    ----------
    columns : list of strings
        A list of strings that match the pattern

    Raises
    ----------
    TypeError
        If the type of data is not a pandas dataframe or
        if the pattern is not a string
    Examples
    ----------
    >>> data = {
        "week_payment1": [1, 2, 3],
        "week_payment2": [1, 2, 3],
        "week_payment3": [1, 2, 3],
        "othercolumn": [5, 6, 7]}
    >>> df = pd.DataFrame(data)
    >>> get_matching_column_names(df, "week_payment")
        ["week_payment1", "week_payment2", "week_payment3"]

    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("The data variable needs to be a pandas dataframe")
    if not isinstance(pattern, str):
        raise TypeError("The pattern variable needs to be a string")

    pattern = rf"{pattern}\d+"
    columns = [colname for colname in data.columns if re.match(pattern, colname)]

    if columns == []:
        raise ValueError(f"No columns matched the given pattern: {pattern}")

    return columns


def calculate_standard_deviation(data, pattern):
    """Returns a dataframe with standard deviation of specific columns.

    Calculating standard deviation of columns inputed.

    Parameters
    ----------
    data : pandas dataframe
        The dataframe to calculate standard deviation
    pattern : string
        The prefix of the column names to extract

    Returns
    ----------
    columns : pandas dataframe
        A dataframe with input columns and standard deviation
    Raises
    ----------
    TypeError
        If the data variable needs to be a pandas dataframe
        If the pattern variable needs to be a string
        If the data frame selected by pattern has non-numeric columns
    Examples
    ----------
    >>> data = {
        "week_payment1": [1, 1, 1],
        "week_payment2": [1, 1, 1],
        "week_payment3": [1, 1, 1],
        "othercolumn": [5, 6, 7]}
    >>> df = pd.DataFrame(data)
    >>> calculate_standard_deviation(df, "week_payment")
        week_payment_std
     0              0.0   
     1              0.0   
     2              0.0   
    """
    
    if not isinstance(data, pd.DataFrame):
        raise TypeError("The data variable needs to be a pandas dataframe")
    if not isinstance(pattern, str):
        raise TypeError("The pattern variable needs to be a string")

    columns = get_matching_column_names(data, pattern)
    data_cal = data[columns].fillna(0)

    num_columns = data_cal.select_dtypes(include=np.number).columns.tolist()
    if sorted(columns) != sorted(num_columns):
        nonum_columns = set(columns).difference(set(num_columns))
        raise TypeError(f"Data frame selected by pattern:'{pattern}' has non-numeric columns: {nonum_columns}.")

    out_val = np.var(data_cal, axis=1)
    out_col = pattern+'_std'

    return pd.DataFrame(out_val, columns=[out_col])
    
    
def calculate_percentage_change(
    df, pattern, compare_period=(2, 2), time_filter=None, changed_name=None
):
    """Calculate percentage change over a time period
    (months over months or weeks over weeks)
    for the given column pattern.

    Use case:
        This function aims to generate features to capture trend
        in data for a given comparison period. Example:
        Telcom - Predict customers who are more likely to decline their revenue next month/week.
        Finance - Predict customers who are going to default next month/week.

    Steps:
        1. Get matching columns for the pattern.

        2. Apply time_filter if available.
        Example: time_filter = (1, 2, 3, 4) filters out columns corresponding to
        weeks 1, 2 , 3 and 4 out of all the weeks available.
        week 1 represent last week data, week 2 last to last week and so on.

        3. Determine start and end comparison period.
        Example: compare_period = (2, 3), corresponds to the percentage for
        last 2 weeks vs previous 3 weeks (with respect to last 2 weeks)

        4. Calculate percentage change between two periods.
        Example: Percentage change of normalized week_payment in last 2 weeks
         vs percentage change in normalized week payment in
         previous 3 weeks (with rest to last 3 weeks)

    Parameters
    ----------
    df : pandas.DataFrame
        A pandas dataframe
    pattern : str
        A column pattern:
        pay_amt represents pay_amt1, pay_amt2...
    compare_period: tuple
        Comparison period:
        for 2 months over 2 months , compare_period = (2, 2)
    time_filter: tuple
        Time filter (months or weeks) for comparison

    Returns
    -----------
    percent_change: array_like
        A numpy array containing percentage change

    Raises
    ----------
    TypeError
        If the type of df is not a pandas dataframe
        If the pattern is not a string
        If compare_period is not a tuple
        If time_filter is not a tuple
    ValueError
        If sum of start period and end period is greater than total number of columns
        If column pattern from time_filter is not present in all columns

    Examples
    ----------
    >>> data = {
        "week_payment1": [10, 5, 20],
        "week_payment2": [50, 20, 5],
        "week_payment3": [100, 20, 5]
        }
    >>> df = pd.DataFrame(data)
    >>> calculate_percentage_change(df, "week_payment", compare_period=(1, 1))
    array([-80., -75., 300.])
    >>> calculate_percentage_change(df, "week_payment", compare_period=(1, 1),
        time_filter=(1, 3))
    array([-90., -75., 300.])
    """
    # Check input types
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input df must be pandas dataframe")

    if not isinstance(pattern, str):
        raise TypeError("pattern must be a string")

    if not isinstance(compare_period, tuple):
        raise TypeError("compare_period must be a tuple")

    if time_filter and not isinstance(time_filter, tuple):
        raise TypeError("time_filter must be a tuple")

    # Get matching columns
    columns = sorted(get_matching_column_names(df, pattern))

    # Time filter
    if time_filter:
        columns = sorted(
            [
                column
                for column in columns
                if int(re.findall(r"\d+", column)[-1]) in time_filter
            ]
        )

        if len(columns) != len(time_filter):
            raise ValueError(
                f"""Column pattern from time_filter is not present in all columns 
            Expected: {[pattern + str(i) for i in time_filter]}
            Got: {columns}
            """
            )

    # start, end
    start, end = compare_period

    # sum of start and end should not exceed number of columns
    if start + end > len(columns):
        raise ValueError(
            """Sum of start period and end period must not exceed 
        total number of columns"""
        )

    # Create p1 and p2
    # p1 = sum of columns in period 1
    # p2 = sum of columns in period 2
    df = df.assign(p1=df[columns[:start]].sum(axis=1)).assign(
        p2=df[columns[start : start + end]].sum(axis=1) / (end / start),
    )

    # fill na to zero
    for col_ in ["p1", "p2"]:
        df[col_] = df[col_].fillna(0)

    # Calculate percentage change
    percent_change = np.where(
        (df.p1 == 0) & (df.p2 == 0),
        0,
        np.where(
            df.p2 == 0,
            (df.p1 - df.p2) * 100 / 0.01,
            (df.p1 - df.p2) * 100 / df.p2,
        ),
    )

    return percent_change



def calculate_average(df, pattern):
    """
    Returns a np array with average of specific columns matching pattern.

    Parameters
    ----------
    df : pandas dataframe
        The dataframe to calculate average
    pattern : string
        The prefix of the column names to calculate average. For example,  "week_payment"

    Returns
    ----------
    numpy array
        A numpy array of calculated average

    Raises
    ----------
    TypeError
        If the type of data is not a pandas dataframe or
        if the pattern is not a matching string

    Examples
    ----------
    >>> data = {
        "week_payment1": [1, 2, 3],
        "week_payment2": [1, 2, 3],
        "week_payment3": [1, 2, 3],
        "othercolumn": [5, 6, 7]}
    >>> df = pd.DataFrame(data)
    >>> calculate_average(df, "week_payment")
        [1.0, 2.0, 3.0]
    """
    # check input type
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas dataframe")
    if not isinstance(pattern, str):
        raise TypeError("pattern must be a string")

    # get matching columns
    columns = get_matching_column_names(df, pattern)

    # calculate average from matching columns
    df_avg = df[columns].mean(axis=1)

    # convert to np array
    df_avg = df_avg.to_numpy()

    return df_avg
