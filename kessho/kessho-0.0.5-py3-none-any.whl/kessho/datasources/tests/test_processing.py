import tempfile
from pathlib import Path
from unittest import TestCase
import tensorflow as tf
from kessho.datasources.processing import (compute_and_save_quandl_rema,
                                           compute_and_save_finnhub_rema,
                                           compute_and_save_yahoo_rema)
from kessho.datasources import quandlapi, finnhub, yahoo
import datetime as dt


class TestProcessing(TestCase):

    def test_quandl_rema(self):

        symbol = 'BULL'
        qursc = quandlapi.QuandlResource()
        df = qursc.get_data(symbol)
        originally_last_record = df.iloc[-1]

        rema_dir = Path(tempfile.mkdtemp())
        compute_and_save_quandl_rema(path=rema_dir, indicators=[symbol])

        file = list(rema_dir.glob('*'))[0]
        tfrds = tf.data.TFRecordDataset(str(file))
        tfrds = tfrds.map(lambda t: tf.io.parse_tensor(t, out_type=tf.float16))
        *_, last_record = iter(tfrds)

        self.assertAlmostEqual(last_record.numpy()[0], originally_last_record['Index'], delta=1e-2)

    def test_finnhub_rema(self):

        symbol = 'ITA'
        fhrsc = finnhub.FinnhubResource()
        df = fhrsc.get_data(symbol, columns=['t', 'c'], aliases=None,
                            first_day=dt.datetime(1900, 1, 1, 0), last_day=dt.datetime(2100, 1, 1, 0))
        originally_last_record = df.iloc[-1]

        rema_dir = Path(tempfile.mkdtemp())
        compute_and_save_finnhub_rema(path=rema_dir, indicators=[symbol])

        file = list(rema_dir.glob('*'))[0]
        tfrds = tf.data.TFRecordDataset(str(file))
        tfrds = tfrds.map(lambda t: tf.io.parse_tensor(t, out_type=tf.float16))
        *_, last_record = iter(tfrds)

        self.assertAlmostEqual(last_record.numpy()[0], originally_last_record['c'], delta=1)

    def test_yahoo_rema(self):

        symbol = '^TNX'
        yarsc = yahoo.YahooResource()
        df = yarsc.ohlcav(symbol, from_=dt.datetime(1900, 1, 1, 0), to_=dt.datetime(2100, 1, 1, 0))
        originally_last_record = df.iloc[-1]

        rema_dir = Path(tempfile.mkdtemp())
        compute_and_save_yahoo_rema(path=rema_dir, indicators=[symbol])

        file = list(rema_dir.glob('*'))[0]
        tfrds = tf.data.TFRecordDataset(str(file))
        tfrds = tfrds.map(lambda t: tf.io.parse_tensor(t, out_type=tf.float16))
        *_, last_record = iter(tfrds)

        self.assertAlmostEqual(last_record.numpy()[0], originally_last_record['Close'], delta=1e-2)
