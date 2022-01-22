"""
    Create REMA TFRecords for a given list of symbols from Yahoo and Finnhub
"""

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from typing import List
import os
from itertools import accumulate

import tensorflow as tf
import datetime as dt
import dateutil.parser as dateparser
from kessho.datasources import finnhub, yahoo, quandlapi
from kessho.features import semantics
from kessho.datasources.processing import (compute_and_save_yahoo_rema, 
                                          compute_and_save_finnhub_rema, 
                                          compute_and_save_quandl_rema)

def create_rema(argv=None):
    
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--yahoo',
        dest='yahoo_symbols',
        required=False,
        help='Comma-separated list of symbols to be sourced from Yahoo')
    
    arg_parser.add_argument(
        '--finnhub',
        dest='finnhub_symbols',
        required=False,
        help='Comma-separated list of symbols to be sourced from Finnhub')
    
    arg_parser.add_argument(
        '--quandl',
        dest='quandl_symbols',
        required=False,
        help='Comma-separated list of sources loaded from quandl')
    
    arg_parser.add_argument(
        '--outdir',
        dest='rema_path',
        required=True,
        default='.',
        help='The directory where to write the resulting TFRecord files containing the rema signals'
    )
       
    args, other_args = arg_parser.parse_known_args(argv)    
    
    rema_path = Path(args.rema_path)
    assert rema_path.exists(), f'{rema_path} does not exist.'

    yahoo_symbols = args.yahoo_symbols.split(',')
    finnhub_symbols = args.finnhub_symbols.split(',')
    quandl_symbols = args.quandl_symbols.split(',')

    compute_and_save_yahoo_rema(rema_path, yahoo_symbols)
    compute_and_save_finnhub_rema(rema_path, finnhub_symbols)
    compute_and_save_quandl_rema(rema_path, quandl_symbols)
    

                
if __name__ == '__main__':
    create_rema()
