from CovidTracker.get_covid_data import get_covid_data 
import pandas as pd
from datetime import datetime, timedelta
import altair as alt
import re

def plot_ts(df, metric, start=None, end=None):
    """Creates a plot displaying the number of 
       covid cases over time.
       
    Parameters
    ----------
    df : pd.DataFrame
        Pandas dataframe containing covid data to plot.
        
    metric : str
        A column chosen from the dataframe to plot in time order
        
    start : datetime, optional
        The beginning date of the time series plot. 
        Format needs to be: YYYY-MM-DD
        
    end : datetime, optional
        The ending date of the time series plot
        Format needs to be: YYYY-MM-DD
        
    Returns
    ----------
    Plot object
    
    Examples
    ----------
    >>> plot_ts(covid_df, "active_cases")
    """
    
    if type(metric) != str:
        raise Exception("The input of the parameter 'metric' should be a string")

    if type(df) != pd.DataFrame:
        raise Exception("The input of the parameter 'df' should be a dataframe.")

    if metric not in df.columns:
        raise ValueError(f"Cannot find the chosen metric. Please choose one from: {list(df.columns)}")

    if ('date' in metric) or ('province' in metric):
        raise ValueError("Chosen metric must not be date or province.")
    
    if metric == 'testing_info':
        raise ValueError("This column is not available for plotting, please choose another column.")
    
    # Find and convert the date column
    for i in df.columns:
        if 'date' in i:
            date_col = i    
    df[date_col] = pd.to_datetime(df[date_col], format = '%d-%m-%Y')
    
    if (start is not None) and (end is not None):
        if pd.to_datetime(start, format = '%Y-%m-%d') >= pd.to_datetime(end, format = '%Y-%m-%d'):
            raise ValueError("The start date must be before the ending date.")
    else:
        if start is None:
            start = min(df[date_col])
        else:
            if type(start) != str:
                raise Exception("The input of the parameter 'start' should be a string")
            else:
                if not re.match(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$', start):
                    raise ValueError("Input date must follow YYYY-MM-DD format")
                else:
                    start = pd.to_datetime(start, format = '%Y-%m-%d')
                    if start < min(df[date_col]):
                        raise ValueError(f"The start date must not be before {min(df[date_col])}.")

        if end is None:
            end = max(df[date_col])
        else:
            if type(end) != str:
                raise Exception("The input of the parameter 'end' should be a string")
            else:
                if not re.match(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$', end):
                    raise ValueError("Input date must follow YYYY-MM-DD format")
                else:
                    end = pd.to_datetime(end, format = '%Y-%m-%d')
                    if end > max(df[date_col]):
                        raise ValueError(f"The ending date must not be after {max(df[date_col])}.")

    df = df[(df[date_col] >= start) & (df[date_col] <= end)]
    
    plot = alt.Chart(df).mark_line().encode(
        x=alt.X(date_col+ ':T', title='Date', axis=alt.Axis(format='%Y-%b-%e')),
        y = metric
    ).properties(
        height=500, width = 1000
    )
    
    return plot