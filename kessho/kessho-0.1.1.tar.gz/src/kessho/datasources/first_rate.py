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

    def __init__(self, filename: Path, process: bool = False, start=0, end=-1):
        """
        :param filename: Path to the csv file
        :param process: set to True to immediately compute additional feature columns
        """
        assert filename.exists(), f'Data folder {filename.as_posix()} does not exist'
        self.filename = filename
        self.raw = self.read_csv()
        self.raw = self.raw[start:end]

        if process:
            self.df = self.clean_date_and_day()
            self.calc_prev_and_current_day_close()
            self.create_additional_datetime_features()
            self.groupby_trading_hour()
            self.flatten_trading_hours()

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

        # Replace original volume by relative logarithmic Volume
        grouped['lVol'] = np.log(grouped['Volume'] + 1)  # + 1 is for numerical stability
        v_max = grouped['lVol'].max()
        grouped['Volume'] = grouped['lVol'] / v_max
        grouped = grouped.reset_index()
        del grouped['lVol']

        shifted = grouped.shift(1)[['Close']].rename(columns={'Close': 'Prev Hour Close'})
        grouped = pd.concat([grouped, shifted], axis=1)
        grouped['log(Change)'] = round(100.0 * np.log(grouped['Close'] / grouped['Prev Hour Close']), 4)

        del grouped['Prev Hour Close']
        self.df = grouped
        return grouped

    def flatten_trading_hours(self):
        df = self.df
        rows = []
        for day in df['Day'].unique():

            df_day = df[df['Day'] == day]

            row = {
                col + f' {th}': df_day[df_day['Trading Hour'] == th][col].iloc[0]
                for th in df_day['Trading Hour']
                for col in ['Open', 'Close', 'Low', 'High', 'log(Change)', 'Vola (m)', 'Volume']
            }
            row['Paused Days'] = df_day['Paused Days'].iloc[0]
            row['Weekday'] = df_day['Weekday'].iloc[0]
            row['Day Close'] = df_day['Day Close'].iloc[0]
            row['Trend 1d'] = np.log(df_day['Day Close'].iloc[0] / df_day['Prev Close'].iloc[0])
            row['Day'] = df_day['Day'].iloc[0]
            rows.append(row)

        grouped = pd.DataFrame.from_records(rows)

        # Deal with missing records
        for i in range(9):
            # no change, no volume, no volatility
            grouped[f'log(Change) {i}'] = np.where(grouped[f'log(Change) {i}'].isna(), 0, grouped[f'log(Change) {i}'])
            grouped[f'Volume {i}'] = np.where(grouped[f'Volume {i}'].isna(), 0, grouped[f'Volume {i}'])
            grouped[f'Vola (m) {i}'] = np.where(grouped[f'Vola (m) {i}'].isna(), 0, grouped[f'Vola (m) {i}'])

            # Every price figure just remains at the previous close
            grouped[f'Close {i}'] = list(accumulate(grouped[f'Close {i}'],
                                                    lambda acc, new: acc if np.isnan(new) else new))
            grouped[f'Open {i}'] = np.where(grouped[f'Open {i}'].isna(), grouped[f'Close {i}'], grouped[f'Open {i}'])
            grouped[f'High {i}'] = np.where(grouped[f'High {i}'].isna(), grouped[f'Close {i}'], grouped[f'High {i}'])
            grouped[f'Low {i}'] = np.where(grouped[f'Low {i}'].isna(), grouped[f'Close {i}'], grouped[f'Low {i}'])

        self.df = grouped

        return self.df

    def compute_trading_hour_history_tensors(self, n_weeks: int,
                                             first_date: dt.date = None, last_date: dt.date = None):
        """
        Computes the n_weeks (x 7 days)) x 9 (trading hours) x 3 (features) np.arrays from the processed data
        Features are gain, volatility and volume
        :return: a generator for 3-dimensional feature arrays, each representing the current history of trading action.
        """
        cols_ndx9 = (['Day']
                     + [f'log(Change) {index}' for index in range(9)]
                     + [f'Vola (m) {index}' for index in range(9)]
                     + [f'Volume {index}' for index in range(9)])
        ndx9 = self.df[cols_ndx9]

        all_dates = pd.date_range(ndx9['Day'].min(), ndx9['Day'].max())

        all_dates = pd.DataFrame(all_dates)
        all_dates.columns = ['Day']
        all_dates['Day'] = all_dates['Day'].apply(lambda d: d.date())
        ndx9 = all_dates.merge(ndx9, on='Day', how='outer').copy().fillna(0.0)

        if first_date:
            ndx9 = ndx9[ndx9['Day'] >= first_date]
        if last_date:
            ndx9 = ndx9[ndx9['Day'] <= last_date]

        num_tensors = len(ndx9) - n_weeks * 7 + 1

        def days():
            for i in range(num_tensors):
                yield ndx9['Day'].iloc[i + 7 * n_weeks - 1]

        def features():
            for i in range(num_tensors):
                img_lc = ndx9[i:i + 7 * n_weeks][[f'log(Change) {i}' for i in range(9)]].copy()
                img_vy = ndx9[i:i + 7 * n_weeks][[f'Vola (m) {i}' for i in range(9)]].copy()
                img_vo = ndx9[i:i + 7 * n_weeks][[f'Volume {i}' for i in range(9)]].copy()
                yield np.stack([img_lc.to_numpy(), img_vy.to_numpy(), img_vo.to_numpy()], axis=0)

        return days(), features()
