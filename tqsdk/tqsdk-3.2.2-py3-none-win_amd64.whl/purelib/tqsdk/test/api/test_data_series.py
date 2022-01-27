#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'mayanqiong'

import lzma
import os
import platform
import random
import sys
import unittest
from datetime import datetime, date

import pandas as pd
import pytest
from pandas._testing import assert_series_equal

from tqsdk import TqApi, utils
from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk.test.test_chan_helper import set_test_script


def assert_dataframe(downloaded_klines, data_series):
    symbol = data_series.iloc[-1].symbol
    for col in data_series.columns:
        if col == "datetime":
            assert_series_equal(data_series["datetime"], downloaded_klines["datetime_nano"], check_dtype=False,
                                check_names=False)
        elif col not in ["id", "duration", "symbol"]:
            assert_series_equal(data_series[col], downloaded_klines[f"{symbol}.{col}"], check_dtype=False,
                                check_names=False)
    return True


@pytest.mark.nonparalleltest
class TestDataSeries(TQBaseTestcase):
    """
    测试不同情况下 get_data_series 正确性，使用提前下载好的 csv 文件验证
    """
    def setUp(self):
        CACHE_DIR = os.path.join(os.path.expanduser('~'), ".tqsdk/data_series")
        if os.path.exists(CACHE_DIR):
            for f in os.listdir(CACHE_DIR):
                try:
                    os.remove(os.path.join(CACHE_DIR, f))
                except:
                    pass  # 忽略抛错
        super(TestDataSeries, self).setUp()

    def tearDown(self):
        super(TestDataSeries, self).tearDown()

    def test_get_data_series1(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_get_data_series1.script.lzma"))
        # 测试
        utils.RD = random.Random(4)

        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        symbol = "SHFE.cu1809"
        dur_sec = 60
        start = datetime(2018, 1, 1, 6, 0, 0)
        end = datetime(2018, 2, 1, 16, 0, 0)
        adj_type = None
        klines1 = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines1))

        start = datetime(2018, 3, 1, 6, 0, 0)
        end = datetime(2018, 4, 1, 16, 0, 0)
        klines2 = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines2))

        api.close()

    def test_get_data_series2(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_get_data_series2.script.lzma"))
        # 测试
        utils.RD = random.Random(4)

        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        symbol = "SHFE.cu1809"
        dur_sec = 60
        start = datetime(2018, 3, 1, 6, 0, 0)
        end = datetime(2018, 4, 1, 16, 0, 0)
        adj_type = None
        klines1 = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines1))

        start = datetime(2018, 1, 1, 6, 0, 0)
        end = datetime(2018, 5, 1, 16, 0, 0)
        klines2 = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines2))
        api.close()

    def test_get_data_series3(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_get_data_series3.script.lzma"))
        # 测试
        utils.RD = random.Random(4)

        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        symbol = "SSE.603871"
        dur_sec = 3600
        start = datetime(2018, 2, 10, 6, 0, 0)
        end = datetime(2020, 12, 30, 16, 0, 0)
        adj_type = None
        klines1 = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines1))
        api.close()

    def test_get_data_series4(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_get_data_series4.script.lzma"))
        # 测试
        utils.RD = random.Random(4)

        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        symbol = "SSE.603871"
        dur_sec = 3600
        start = datetime(2018, 2, 10, 6, 0, 0)
        end = datetime(2020, 12, 30, 16, 0, 0)
        adj_type = "F"
        klines1 = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end,
                                            adj_type=adj_type)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines1))

        adj_type = "B"
        klines2 = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end,
                                            adj_type=adj_type)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines2))

        api.close()

    def test_get_data_series5(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_get_data_series5.script.lzma"))
        # 测试
        utils.RD = random.Random(4)

        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        symbol = "SSE.603871"
        dur_sec = 86400
        start = datetime(2018, 2, 10, 6, 0, 0)
        end = datetime(2020, 12, 30, 16, 0, 0)
        adj_type = None
        klines = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end,
                                           adj_type=adj_type)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines))

        adj_type = "F"
        klines1 = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end,
                                            adj_type=adj_type)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines1))

        adj_type = "B"
        klines2 = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end,
                                            adj_type=adj_type)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines2))

        api.close()

    @unittest.skipIf(sys.platform.startswith("win") and platform.architecture()[0] == "32bit", "don't test on 32bit win")
    def test_get_data_series6(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_get_data_series6.script.lzma"))
        # 测试
        utils.RD = random.Random(4)

        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        symbol = "SHFE.cu1809"
        dur_sec = 0
        start = datetime(2018, 3, 1, 6, 0, 0)
        end = datetime(2018, 4, 1, 16, 0, 0)
        adj_type = None
        klines1 = api.get_tick_data_series(symbol=symbol, start_dt=start, end_dt=end)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines1))

        start = datetime(2018, 1, 1, 6, 0, 0)
        end = datetime(2018, 5, 1, 16, 0, 0)
        klines2 = api.get_tick_data_series(symbol=symbol, start_dt=start, end_dt=end)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%dT%H%M%S')}_{end.strftime('%Y%m%dT%H%M%S')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines2))

        api.close()

    def test_get_data_series7(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_get_data_series7.script.lzma"))
        # 测试
        utils.RD = random.Random(4)

        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        symbol = "SHFE.cu1809"
        dur_sec = 60
        start = date(2018, 3, 1)
        end = date(2018, 4, 1)
        adj_type = None
        klines1 = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines1))

        start = date(2018, 2, 10)
        end = date(2018, 4, 10)
        klines2 = api.get_kline_data_series(symbol=symbol, duration_seconds=dur_sec, start_dt=start, end_dt=end)
        target_klines = pd.read_csv(lzma.open(
            os.path.join(dir_path, "get_data_series_files", f"{symbol}_{dur_sec}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}_{adj_type}.csv.lzma"),
            "rt", encoding="utf-8"))
        self.assertTrue(assert_dataframe(target_klines, klines2))
        api.close()
