import datetime as dt
import requests
from io import StringIO
import pandas as pd
from itertools import accumulate
import numpy as np


class YahooResource:

    @staticmethod
    def ohlcav(symbol, from_, to_, all_calendar_days=True):
        """
        Returns open/high/low/close/adjusted/volume in a dataframe
        """
        if isinstance(from_, dt.date):
            from_ = int(dt.datetime(from_.year, from_.month, from_.day, 0).timestamp())        
        if isinstance(to_, dt.date):
            to_ = int(dt.datetime(to_.year, to_.month, to_.day, 0).timestamp())        
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?" + \
              f"period1={from_}&period2={to_}&interval=1d&includeAdjustedClose=true"

        res = requests.get(url)

        if res.status_code != 200:
            raise ValueError(f'Failed to download data for {symbol}')

        string = res._content.decode('UTF8')  # noqa

        df = pd.read_csv(StringIO(string), sep=',')
        
        df['Date'] = df['Date'].apply(lambda d: dt.datetime.strptime(d, "%Y-%m-%d").date())

        if all_calendar_days:
            df = fill_calendar(df)

        return df


def fill_calendar(df: pd.DataFrame):
    """
    Extends the finnhub daily candle dataframe with the remaining non-biz calendar days.
    Fills volume with zero and all prices with most recent close, i.e. reasonable "no-biz" data.
    """
    all_dates = pd.DataFrame(pd.date_range(min(df['Date']), max(df['Date'])))
    all_dates.columns = ['Date']
    all_dates['Date'] = all_dates['Date'].apply(lambda t: t.date())
    df = all_dates.merge(df, on='Date', how='outer')
    # close takes the value of prev day's close
    df['Close'] = list(accumulate(df['Close'],
                                  lambda acc, new: acc if pd.isna(new) else new))
    df['Adj Close'] = list(accumulate(df['Adj Close'],
                                      lambda acc, new: acc if pd.isna(new) else new))
    # open takes the day's close, which is the prev day's close
    df['Open'] = np.where(df['Open'].isna(), df['Close'], df['Open'])
    # high takes the day's close, which is the prev day's close
    df['High'] = np.where(df['High'].isna(), df['Close'], df['High'])
    # low takes the day's close, which is the prev day's close
    df['Low'] = np.where(df['Low'].isna(), df['Close'], df['Low'])
    # Volume is simply 0
    df['Volume'] = np.where(df['Volume'].isna(), 0, df['Volume'])
    return df
