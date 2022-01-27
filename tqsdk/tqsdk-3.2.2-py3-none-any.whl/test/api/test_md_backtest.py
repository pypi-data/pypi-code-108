#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'limin'

import json
import os
import sys
import unittest
import random
from contextlib import closing
from datetime import datetime
from tqsdk import TqApi, TqBacktest, BacktestFinished, utils, TqChan
from tqsdk.ta import OPTION_IMPV
from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk.test.test_chan_helper import set_test_script


class TestMdBacktest(TQBaseTestcase):
    '''
     行情回测测试
    '''

    def setUp(self):
        super(TestMdBacktest, self).setUp()

    def tearDown(self):
        super(TestMdBacktest, self).tearDown()

    def test_get_quote_backtest(self):
        """
        回测获取行情报价
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://backtest.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_md_backtest_get_quote.script.lzma"))
        # 测试
        try:
            utils.RD = random.Random(4)
            api = TqApi(backtest=TqBacktest(datetime(2020, 6, 2), datetime(2020, 6, 3)),
                        auth="tianqin,tianqin", _md_url=md_url)
            with closing(api):
                quote = api.get_quote("SHFE.cu2009")
                quote_data = {k: v for k, v in quote.items()}
                quote_data["trading_time"] = {k: v for k, v in quote_data["trading_time"].items()}
                self.assertEqual(
                    json.dumps(quote_data, sort_keys=True),
                    '{"amount": NaN, "ask_price1": 44640.0, "ask_price2": NaN, "ask_price3": NaN, "ask_price4": NaN, "ask_price5": NaN, "ask_volume1": 1, "ask_volume2": 0, "ask_volume3": 0, "ask_volume4": 0, "ask_volume5": 0, "average": NaN, "bid_price1": 44620.0, "bid_price2": NaN, "bid_price3": NaN, "bid_price4": NaN, "bid_price5": NaN, "bid_volume1": 1, "bid_volume2": 0, "bid_volume3": 0, "bid_volume4": 0, "bid_volume5": 0, "cash_dividend_ratio": [], "close": NaN, "commission": 13.035, "datetime": "2020-06-02 00:00:00.000000", "delivery_month": 9, "delivery_year": 2020, "exchange_id": "SHFE", "exercise_month": 0, "exercise_type": "", "exercise_year": 0, "expire_datetime": 1600153200.0, "expire_rest_days": 105, "expired": true, "highest": NaN, "ins_class": "FUTURE", "instrument_id": "SHFE.cu2009", "instrument_name": "", "iopv": NaN, "last_exercise_datetime": NaN, "last_price": 44630.0, "lower_limit": NaN, "lowest": NaN, "margin": 18249.0, "max_limit_order_volume": 500, "max_market_order_volume": 0, "min_limit_order_volume": 0, "min_market_order_volume": 0, "open": NaN, "open_interest": 53079, "option_class": "", "pre_close": NaN, "pre_open_interest": 0, "pre_settlement": NaN, "price_decs": 0, "price_tick": 10, "product_id": "cu", "public_float_share_quantity": 0, "settlement": NaN, "stock_dividend_ratio": [], "strike_price": NaN, "trading_time": {"day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]], "night": [["21:00:00", "25:00:00"]]}, "underlying_symbol": "", "upper_limit": NaN, "volume": 0, "volume_multiple": 5}'
                )# 其他取值方式
                self.assertNotEqual(quote["pre_close"], quote.pre_close)
                self.assertNotEqual(quote.get("pre_settlement"), quote.pre_settlement)
                self.assertNotEqual(quote.get("highest"), quote.highest)
                self.assertNotEqual(quote.get("lowest"), quote.lowest)
                self.assertNotEqual(quote["open"], quote.open)
                self.assertNotEqual(quote["close"], quote.close)
        except BacktestFinished:
            api.close()
            print("backtest finished")

    def test_get_kline_serial_update(self):
        """
        获取K线数据, 行情应该随着 api.wait_update 一直更新时间
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://backtest.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_md_backtest_get_kline_serial_update.script.lzma"))

        # 测试: 获取K线数据
        utils.RD = random.Random(4)
        api = TqApi(backtest=TqBacktest(datetime(2020, 6, 2), datetime(2020, 6, 3)),
                    auth="tianqin,tianqin", _md_url=md_url)

        quote = api.get_quote("SHFE.rb2009")
        df = api.get_kline_serial("SHFE.rb2009", 1, 10)

        self.assertEqual(quote["datetime"], "2020-06-01 22:59:59.999999")
        self.assertEqual(df["datetime"].iloc[-1], 1.591023599e+18)

        api.wait_update()
        df['ema5'] = df['close'].rolling(5, min_periods=1).mean()
        df.loc[df["ema5"] > 2.5, 'duo'] = 1
        self.assertEqual(quote["datetime"], "2020-06-02 09:00:00.000000")
        self.assertEqual(df["datetime"].iloc[-1], 1.5910596e+18)

        api.wait_update()
        df['ema5'] = df['close'].rolling(5, min_periods=1).mean()
        df.loc[df["ema5"] > 2.5, 'duo'] = 1
        self.assertEqual(quote["datetime"], "2020-06-02 09:00:00.999999")
        self.assertEqual(df["datetime"].iloc[-1], 1.5910596e+18)

        api.wait_update()
        df['ema5'] = df['close'].rolling(5, min_periods=1).mean()
        df.loc[df["ema5"] > 2.5, 'duo'] = 1
        self.assertEqual(quote["datetime"], "2020-06-02 09:00:01.000000")
        self.assertEqual(df["datetime"].iloc[-1], 1.591059601e+18)

        api.close()

    def test_get_kline_serial_mutli_symbol_update(self):
        """
        获取K线数据, 行情应该随着 api.wait_update 一直更新时间
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://backtest.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_md_backtest_get_kline_serial_mutil_symbol_update.script.lzma"))

        # 测试: 获取K线数据
        utils.RD = random.Random(4)
        api = TqApi(backtest=TqBacktest(datetime(2020, 2, 2), datetime(2020, 4, 3)),
                    auth="tianqin,tianqin", _md_url=md_url)

        quote = api.get_quote("SHFE.cu2006C50000")
        klines = api.get_kline_serial(["SHFE.cu2006C50000", "SHFE.cu2006"], 24 * 60 * 60, 20)

        while quote.datetime < "2020-02-03 09:00:00.000000":
            api.wait_update()
        impv = OPTION_IMPV(klines, quote, 0.025)
        self.assertEqual("2020-02-03 09:00:00.000000", quote.datetime)
        self.assertEqual('7.90037,8.14295,8.29614,8.72528,8.83839,8.94612,7.84119,8.62895,9.64177,8.80140,10.06843,10.37674,11.49183,10.08550,10.13223,8.17235,9.41323,9.54246,9.88586,13.95591',
                         ','.join([f"{i:.5f}" for i in list(impv["impv"] * 100)]))

        while quote.datetime < "2020-02-04 09:00:00.000000":
            api.wait_update()
        impv = OPTION_IMPV(klines, quote, 0.025)
        self.assertEqual("2020-02-04 09:00:00.000000", quote.datetime)
        self.assertEqual('8.14295,8.29614,8.72528,8.83839,8.94612,7.84119,8.62895,9.64177,8.80140,10.06843,10.37674,11.49183,10.08550,10.13223,8.17235,9.41323,9.54246,9.88586,13.17991,13.47967',
                         ','.join([f"{i:.5f}" for i in list(impv["impv"] * 100)]))

        while quote.datetime < "2020-02-05 09:00:00.000000":
            api.wait_update()
        impv = OPTION_IMPV(klines, quote, 0.025)
        self.assertEqual("2020-02-05 09:00:00.000000", quote.datetime)
        self.assertEqual('8.29614,8.72528,8.83839,8.94612,7.84119,8.62895,9.64177,8.80140,10.06843,10.37674,11.49183,10.08550,10.13223,8.17235,9.41323,9.54246,9.88586,13.17991,12.84848,13.46791',
                         ','.join([f"{i:.5f}" for i in list(impv["impv"] * 100)]))

        while quote.datetime < "2020-02-06 09:00:00.000000":
            api.wait_update()
        impv = OPTION_IMPV(klines, quote, 0.025)
        self.assertEqual("2020-02-06 09:00:00.000000", quote.datetime)
        self.assertAlmostEqual('8.72528,8.83839,8.94612,7.84119,8.62895,9.64177,8.80140,10.06843,10.37674,11.49183,10.08550,10.13223,8.17235,9.41323,9.54246,9.88586,13.17991,12.84848,12.60985,12.30410',
                         ','.join([f"{i:.5f}" for i in list(impv["impv"] * 100)]))

        while quote.datetime < "2020-02-07 09:00:00.000000":
            api.wait_update()
        impv = OPTION_IMPV(klines, quote, 0.025)
        self.assertEqual("2020-02-07 09:00:00.000000", quote.datetime)
        self.assertEqual('8.83839,8.94612,7.84119,8.62895,9.64177,8.80140,10.06843,10.37674,11.49183,10.08550,10.13223,8.17235,9.41323,9.54246,9.88586,13.17991,12.84848,12.60985,12.36215,12.31351',
                         ','.join([f"{i:.5f}" for i in list(impv["impv"] * 100)]))

        while quote.datetime < "2020-02-10 09:00:00.000000":
            api.wait_update()
        impv = OPTION_IMPV(klines, quote, 0.025)
        self.assertEqual("2020-02-10 09:00:00.000000", quote.datetime)
        self.assertAlmostEqual('8.94612,7.84119,8.62895,9.64177,8.80140,10.06843,10.37674,11.49183,10.08550,10.13223,8.17235,9.41323,9.54246,9.88586,13.17991,12.84848,12.60985,12.36215,12.56515,13.28526',
                         ','.join([f"{i:.5f}" for i in list(impv["impv"] * 100)]))

        while quote.datetime < "2020-02-11 09:00:00.000000":
            api.wait_update()
        impv = OPTION_IMPV(klines, quote, 0.025)
        self.assertEqual("2020-02-11 09:00:00.000000", quote.datetime)
        self.assertEqual('7.84119,8.62895,9.64177,8.80140,10.06843,10.37674,11.49183,10.08550,10.13223,8.17235,9.41323,9.54246,9.88586,13.17991,12.84848,12.60985,12.36215,12.56515,13.18500,13.06567',
                         ','.join([f"{i:.5f}" for i in list(impv["impv"] * 100)]))

        while quote.datetime < "2020-02-12 09:00:00.000000":
            api.wait_update()
        impv = OPTION_IMPV(klines, quote, 0.025)
        self.assertEqual("2020-02-12 09:00:00.000000", quote.datetime)
        self.assertEqual('8.62895,9.64177,8.80140,10.06843,10.37674,11.49183,10.08550,10.13223,8.17235,9.41323,9.54246,9.88586,13.17991,12.84848,12.60985,12.36215,12.56515,13.18500,13.04029,11.11245',
                         ','.join([f"{i:.5f}" for i in list(impv["impv"] * 100)]))

        api.close()
