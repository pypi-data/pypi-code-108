import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from bluebelt.datetime import holidays

# series

def add_datetime_metadata(series):
    frame = pd.DataFrame(data={'datetime': series.index.values, 'values': series.values})
    frame['year'] = frame['datetime'].dt.year
    frame['quarter'] = frame['datetime'].dt.quarter
    frame['month'] = frame['datetime'].dt.month
    frame['day'] = frame['datetime'].dt.day
    frame['weekday'] = frame['datetime'].dt.weekday
    frame['day_name'] = frame['datetime'].dt.day_name()
    frame['iso_year'] = frame['datetime'].dt.isocalendar().year
    frame['iso_week'] = frame['datetime'].dt.isocalendar().week

    return frame
    

def year(series, **kwargs):
    return series.dt.year

def quarter(series, **kwargs):
    return series.dt.quarter

def month(series, **kwargs):
    return series.dt.month

def day(series, **kwargs):
    return series.dt.day

def weekday(series, **kwargs):
    return series.dt.weekday

def day_name(series, **kwargs):
    return series.dt.day_name()

def is_holiday(series, **kwargs):
    return series.apply(lambda x: holidays.holidays(x))

def is_weekend(series, **kwargs):
    weekend_days = kwargs.get('weekend_days', [5, 6])
    return series.apply(lambda x: pd.to_datetime(x).date().weekday() in weekend_days)

def iso_year(series, **kwargs):
    return series.dt.isocalendar().year

def iso_week(series, **kwargs):
    return series.dt.isocalendar().week

def week(series, **kwargs):
    return series.dt.isocalendar().week

# dataframe
def date_from_weeknumber(df,
                         year=None,
                         week=None,
                         day=0,
                         ):


    # data checks
    if isinstance(year, (list, pd.Series, np.ndarray, int, float)) and isinstance(week, (list, pd.Series, np.ndarray, int, float)):
        year = pd.Series(year)
        week = pd.Series(week)
        if year.shape[0] == week.shape[0]:
            df = pd.DataFrame({'year': year, 'week': week})
        else:
            raise ValueError("'year' and 'week' need to have equal lengths")
    elif isinstance(df, pd.DataFrame) and isinstance(year, str) and isinstance(week, str):
        df = pd.DataFrame({'year': df[year], 'week': df[week]})
    else:
        raise ValueError("arguments not in the right format")

    def weeknum(row, year=None, week=None, day=0):
        d = pd.to_datetime(f'4 jan {row[year]}')  # The Jan 4th must be in week 1 according to ISO
        result =  d + pd.Timedelta(weeks=(row[week])-1, days=-(d.weekday()) + day)
        return result
    
    return df.apply(lambda x: weeknum(x, year=year, week=week, day=day), axis=1)
