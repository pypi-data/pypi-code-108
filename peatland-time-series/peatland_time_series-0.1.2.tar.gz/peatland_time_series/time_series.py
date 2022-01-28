import pandas

TIME_SERIES_COLUMNS = ['date', 'data_wtd', 'data_prec']

def read_time_series(filepath: str) -> pandas.DataFrame:
    """Read the time series file as a DataFrame.

    Parameters
    ----------
    filepath
       CSV like file of time series with at least the 3 following columns: 'date', 'data_wtd' and 'data_prec'.
        'date' refers to the date of the data acquisition ("YYYY-MM-DD hh:mm:ss", ex. "2011-06-15 15:00:00").
        'data_wtd' refers to the water table depth to the surface.
        'data_prec' refers to the precipitation measure. 

    Returns
    -------
    pandas.DataFrame
        The time series as a DataFrame.
    """
    time_series = pandas.read_csv(filepath)

    for column in TIME_SERIES_COLUMNS:
        if column not in time_series.columns:
            raise ValueError(f"Columns \"{', '.join(TIME_SERIES_COLUMNS)}\" must be in the time series file: \"{filepath}\"")


    time_series = time_series[TIME_SERIES_COLUMNS]  # Keeping only these columns
    time_series['date'] = pandas.to_datetime(time_series['date'])  # Getting dates

    time_series = time_series.set_index('date')

    return time_series