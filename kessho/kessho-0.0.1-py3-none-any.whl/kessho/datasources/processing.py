import datetime as dt
import os
from pathlib import Path
from typing import List
import pandas as pd
import tensorflow as tf

from kessho.datasources import yahoo, finnhub, quandlapi
from kessho.features import semantics


def compute_and_save_yahoo_rema(path: Path, indicators: List[str]):
    yarsc = yahoo.YahooResource()

    for symbol in indicators:
        # Make sure we get all data
        df = yarsc.ohlcav(symbol, dt.datetime(1900, 1, 1, 0), dt.datetime(2100, 1, 1, 0))

        write_to_tfrecord(df, path, symbol, source_column='Close')


def compute_and_save_finnhub_rema(path: Path, indicators: List[str]):
    fhrsc = finnhub.FinnhubResource()

    for symbol in indicators:
        # Make sure we get all data
        df = fhrsc.get_data(symbol=symbol, columns=['t', 'c'], aliases=['Date', 'Close'],
                            first_day=dt.datetime(1900, 1, 1, 0), last_day=dt.datetime(2100, 1, 1, 0))

        write_to_tfrecord(df, path, symbol, source_column='Close')


def compute_and_save_quandl_rema(path: Path, indicators: List[str]):
    qursc = quandlapi.QuandlResource()

    for symbol in indicators:
        df = qursc.get_data(symbol)
        write_to_tfrecord(df, path, symbol, source_column='Index')


def write_to_tfrecord(df: pd.DataFrame, path: Path, symbol: str, source_column: str):
    rema_cols = [source_column] + [f'rema_{source_column}_{k}' for k in [1, 2, 5, 8, 13, 21]]

    first_day, last_day = min(df['Date']), max(df['Date'])
    df = semantics.ema_rema(df, column=source_column, rema=True)
    data = df[rema_cols].to_numpy()
    ds = tf.data.Dataset.from_tensor_slices(data)
    ds = ds.map(lambda r: tf.cast(r, dtype=tf.float16))
    ds = ds.map(tf.io.serialize_tensor)
    symbol = symbol.replace('^', '')
    file_name = f'{symbol}_REMA_{first_day}_{last_day}.tfrecord'
    print(f"Writing trend data for  {symbol} to {file_name}")
    writer = tf.data.experimental.TFRecordWriter(str(path / file_name))
    writer.write(ds)
