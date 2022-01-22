import datetime as dt
from itertools import accumulate
from typing import List, Optional

import finnhub as fh
import numpy as np
import pandas as pd
import os


class FinnhubResource:

    def __init__(self, api_key=None):
        api_key = api_key or os.environ.get('FINNHUB_API')
        self.client = fh.Client(api_key=api_key)
        
    def get_data(self, symbol: str, columns: List[str], aliases: Optional[List[str]],
                 first_day: dt.datetime, last_day: dt.datetime, all_calendar_days=True):
        """
        :param symbol: the equity's symbol
        :param columns: list of columns to extract. Choose from 't', 'o', 'c', 'h', 'l', 'v'
        :param aliases: list of new names for those columns, maybe None
        :param first_day: beginning of the time series or first available data, whichever is later
        :param last_day: end of the time series of last available data, whichever is earlier
        :param all_calendar_days: if True, adds non-biz days replacing Nones reasonably from prev non-None rows
        :return: a pandas DataFrame with the 't' (or renamed) column already as dt.date.
        """
        start = int(first_day.timestamp())
        end = int(last_day.timestamp())
        data = self.client.stock_candles(symbol, 'D', start, end)
        df = pd.DataFrame.from_dict(data)
        df['t'] = df['t'].apply(lambda t: dt.datetime.fromtimestamp(t).date())
        
        if all_calendar_days:
            df = fill_calendar(df)

        if not columns:
            columns = ['t', 'o', 'h', 'l', 'c', 'v']
        if aliases:
            mapping = {k: v for (k, v) in zip(columns, aliases)}
            df.rename(columns=mapping, inplace=True)
            columns = aliases
            
        df = df[columns]

        return df.copy()    


def fill_calendar(df: pd.DataFrame):
    """
    Extends the finnhub daily candle dataframe with the remaining non-biz calendar days.
    Fills volume with zero and all prices with most recent close, i.e. reasonable "no-biz" data.
    """
    all_dates = pd.DataFrame(pd.date_range(min(df['t']), max(df['t'])))
    all_dates.columns = ['t']
    all_dates['t'] = all_dates['t'].apply(lambda t: t.date())
    df = all_dates.merge(df, on='t', how='outer')
    # close takes the value of prev day's close
    df['c'] = list(accumulate(df['c'], lambda acc, new: acc if pd.isna(new) else new))
    # open takes the day's close, which is the prev day's close
    df['o'] = np.where(df['o'].isna(), df['c'], df['o'])
    # high takes the day's close, which is the prev day's close
    df['h'] = np.where(df['h'].isna(), df['c'], df['h'])
    # low takes the day's close, which is the prev day's close
    df['l'] = np.where(df['l'].isna(), df['c'], df['l'])
    # Volume is simply 0
    df['v'] = np.where(df['v'].isna(), 0, df['v'])
    return df
