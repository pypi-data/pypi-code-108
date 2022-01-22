"""
    Support for reading data files from https://firstratedata.com/
    Computes gains, volatility and volume per trading hour
"""

import datetime as dt
import math
from itertools import accumulate
from pathlib import Path

import numpy as np
import pandas as pd


class MinuteCsv:

    def __init__(self, filename: Path, process: bool = False):
        """
        :param filename: Path to the csv file
        :param process: set to True to immediately compute additional feature columns
        """
        assert filename.exists(), f'Data folder {filename.as_posix()} does not exist'
        self.filename = filename
        self.raw = self.read_csv()

        if process:
            self.df = self.clean_date_and_day()
            self.calc_prev_and_current_day_close()
            self.create_additional_datetime_features()
            self.groupby_trading_hour()

    def read_csv(self) -> pd.DataFrame:
        """
        Reads a CSV file from the directory Columns are: 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'.
        computes trading-hour and trend features, if process is set to True
        :return: A pandas dataframe with the columns 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'
        """
        df = pd.read_csv(self.filename,
                         names=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], header=None)
        return df

    def clean_date_and_day(self) -> pd.DataFrame:
        df = self.raw.copy()
        # There are always duplicates
        df.drop_duplicates(inplace=True)
        # use python-typed date
        df['Date'] = df['Date'].map(lambda d: dt.datetime.strptime(d, '%Y-%m-%d %H:%M:%S'))
        # remove the 8pm formal closing record
        df = df[df['Date'].apply(lambda x: x.time() != dt.time(20, 0))]
        # extract day
        df['Day'] = df['Date'].map(lambda d: d.date())

        self.df = df
        return df

    def calc_prev_and_current_day_close(self) -> pd.DataFrame:
        """
        Note that day's close in this context is not the official closing price at 16:00, but the
        latest closing price on that day, which can be after-hours.
        """
        df = self.df
        # Prev Day actually means "prev. row's day"
        to_prev = df.shift(1)[['Day', 'Close']].rename(columns={'Day': 'Prev Day', 'Close': 'Prev Close'})
        df = pd.concat([df, to_prev], axis=1)
        df = df.dropna()
        df['Prev Close'] = df.apply(lambda row:
                                    row['Prev Close'] if row['Prev Day'] != row['Day'] else math.nan, axis=1)
        df['Prev Close'] = list(accumulate(df['Prev Close'], lambda x, y: x if np.isnan(y) else y))

        to_next = df.shift(-1)[['Day', 'Close']].rename(columns={'Day': 'Next Day', 'Close': 'Next Close'})
        df = pd.concat([df, to_next], axis=1)
        df['Day Close'] = df.apply(lambda row:
                                   row['Close'] if row['Next Day'] != row['Day'] else math.nan, axis=1)  # noqa
        del df['Next Close']
        del df['Next Day']

        df = df[::-1]
        df['Day Close'] = list(accumulate(df['Day Close'], lambda x, y: x if np.isnan(y) else y))
        df = df[::-1]
        df = df.dropna()

        self.df = df
        return df

    def create_additional_datetime_features(self) -> pd.DataFrame:
        """
        Trading hour: one of the 9 phases from 0=pre-market to 8=post-market
        """
        df = self.df
        cuts = [dt.time(h, m) for (h, m) in [
            (0, 0), (9, 30), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (16, 0)]]

        def trading_hour(ts):
            time = ts.time()
            for index, cut in enumerate(cuts[::-1]):
                if time >= cut:
                    return 8 - index

        df['Trading Hour'] = df['Date'].apply(trading_hour)
        df['Weekday'] = df['Day'].apply(dt.date.weekday)
        df['Paused Days'] = (df['Day'] - df['Prev Day']).apply(lambda x: x.days)

        self.df = df
        return df

    def groupby_trading_hour(self):

        df = self.df
        df['Price Range (m)'] = df['High'] - df['Low']

        grouped = df.groupby(['Day', 'Trading Hour']).agg({
            'Open': ['first'],
            'Close': ['last'],
            'Low': ['min'],
            'High': ['max'],
            'Volume': ['sum'],
            'Date': ['count'],
            'Day Close': ['first'],
            'Prev Close': ['first'],
            'Price Range (m)': ['max'],
            'Weekday': ['first'],
            'Paused Days': ['first']
            })

        grouped.columns = ['Open', 'Close', 'Low', 'High', 'Volume', 'Count', 'Day Close',
                           'Prev Close', 'Vola (m)', 'Weekday', 'Paused Days']

        grouped['Vola (m)'] = round(100 * grouped['Vola (m)'] / grouped['Prev Close'], 3)
        grouped = grouped.reset_index()

        shifted = grouped.shift(1)[['Close']].rename(columns={'Close': 'Prev Hour Close'})
        grouped = pd.concat([grouped, shifted], axis=1)
        grouped.dropna(inplace=True)
        grouped['log(Change)'] = round(100.0 * np.log(grouped['Close'] / grouped['Prev Hour Close']), 4)

        del grouped['Prev Hour Close']

        self.df = grouped
        return grouped
