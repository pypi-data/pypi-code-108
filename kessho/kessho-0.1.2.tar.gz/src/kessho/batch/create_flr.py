"""
    Create Label TFRecords for given name or all of given thfp files
"""

import argparse
from pathlib import Path
import tensorflow as tf
import datetime as dt
import dateutil.parser as dateparser
import kessho.datasources.first_rate as fr
from kessho.datasources import finnhub
import pandas as pd
import numpy as np
from typing import List
import os
from itertools import accumulate

def create_flr(argv=None):
    
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--symbol',
        dest='symbol',
        required=False,
        help='A symbol for the name to be labeled. If provided, must provide date range, too')
    
    arg_parser.add_argument(
        '--from',
        dest='from_day',
        required=False,
        help='If symbol is provided, first day of quote query')
    
    arg_parser.add_argument(
        '--to',
        dest='to_day',
        required=False,
        help='If symbol is provided, last day of quote query')
    
    arg_parser.add_argument(
        '--thfp-dir',
        dest='thfp_path',
        required=False,
        default='.',
        help='The directory where the THFP data can be found. If provided, will generate labels for every THFP file found there')
    
    arg_parser.add_argument(
        '--outdir',
        dest='labels_path',
        required=True,
        default='.',
        help='The directory where to write the resulting TFRecord files containing the labels'
    )
   
    
    args, other_args = arg_parser.parse_known_args(argv)    
    
    thfp_path = Path(args.thfp_path)
    assert thfp_path.exists(), f'{thfp_path} does not exist.'
    
    labels_path = Path(args.labels_path)
    assert labels_path.exists(), f'{labels_path} does not exist.'

    for f in list(thfp_path.glob('*.tfrecord')):
        symbol, _, from_, to_ = f.name.split('.')[0].split('_')
        start = dateparser.isoparse(from_)
        end = dateparser.isoparse(to_)
        
        compute_labels(symbol, start, end, labels_path)

        
            
def compute_labels(symbol: str, start: dt.date, end: dt.date, labels_path: Path):
    

    print(f'Creating labels for {symbol} from {start.date()} to {end.date()}')

    fh = finnhub.FinnhubResource(api_key=os.environ['FINNHUB_API'])
    df = fh.get_data(symbol=symbol, columns=['t', 'c'], aliases=['Date', 'Close'], 
                     first_day=start, last_day=end, all_calendar_days=True)

    ema_rema(df, periods=[3, 7, 14, 30, 90], smooth=2.0, source_column='Close', inplace=True, rema=False)
    df = compute_future_log_returns(df, source_column='Close', steps=[3, 7, 14, 30, 90])    
    
    first_day = min(df['Date'])
    last_day = max(df['Date'])
    
    labels = compute_label_tensors(df)    

    ds = tf.data.Dataset.from_generator(
        lambda: labels, output_types=tf.float16
    ).map(
        lambda r: tf.cast(r, dtype=tf.float16)
    ).map(tf.io.serialize_tensor)

    file_name = f'{symbol}_FLR_{first_day}_{last_day}.tfrecord'
    writer = tf.data.experimental.TFRecordWriter(str(labels_path / file_name))
    writer.write(ds)

    
def compute_label_tensors(df):
    for row in df[['log_r+1', 'log_r+3', 'log_r+7', 'log_r+14', 'log_r+30', 'log_r+90']].to_numpy():
        yield row    
    
    
def compute_future_log_returns(df: pd.DataFrame, source_column: str, steps: List[int], dropna=True):
    """
    compute log returns with regards to future dates comparing 'source_column' with column target_format.format(step) for each step from the 'steps' list
    
    """    
    # Sufficient smoothing: The prediction target is the ema with the prev-shorter period.
    target_format = 'ema_{}'  

    
    # start with predicting the next day
    df[f'log_r+1'] = np.log(df[source_column].shift(-1)/df[source_column])

    prev = source_column
    for s in steps:
        df[f'log_r+{s}'] = np.log(df[prev].shift(-s)/df[source_column])
        prev = target_format.format(s)
    if dropna:
        df.dropna(inplace=True)
    return df    
    
    
def ema_rema(df, source_column='Close', smooth=2.0, periods=None, inplace: bool = False, rema: bool = False) -> pd.DataFrame:
    """
    """
    # business weeks=5days by default
    periods=periods or [5 * p for p in [1,2,3,5,8,13,21,34]]
    pairs = zip(periods[:-1], periods[1:])
    if not inplace:
        df = df.copy()

    for period in periods:
        df[f'ema_{period}'] = list(accumulate(df[source_column],
                                                    lambda x,y: round(
                                                     x * (1.- smooth / (1. + period)) +
                                                     y * smooth/ (1. + period), 3)))


    if rema:
        for pair in pairs:
            df[f'rema_{pair[0]}'] = round(df[f'ema_{pair[0]}'] / df[f'ema_{pair[1]}'], 3) - 1.
    
    return df    
    
if __name__ == '__main__':
    create_flr()