#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import random

from tqsdk import TqApi, utils
from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk.test.test_chan_helper import set_test_script


class TestMdBasic(TQBaseTestcase):
    """
    测试TqApi行情相关函数基本功能, 以及TqApi与行情服务器交互是否符合设计预期

    注：
    1. 在本地运行测试用例前需设置运行环境变量(Environment variables), 保证api中dict及set等类型的数据序列在每次运行时元素顺序一致: PYTHONHASHSEED=32
    2. 若测试用例中调用了会使用uuid的功能函数时（如insert_order()会使用uuid生成order_id）,
        则：在生成script文件时及测试用例中都需设置 utils.RD = random.Random(x), 以保证两次生成的uuid一致, x取值范围为0-2^32
    3. 对盘中的测试用例（即非回测）：因为TqSim模拟交易 Order 的 insert_date_time 和 Trade 的 trade_date_time 不是固定值，所以改为判断范围。
        盘中时：self.assertAlmostEqual(1575292560005832000 / 1e9, order1.insert_date_time / 1e9, places=1)
        回测时：self.assertEqual(1575291600000000000, order1.insert_date_time)
    """

    def setUp(self):
        super(TestMdBasic, self).setUp()

    def tearDown(self):
        super(TestMdBasic, self).tearDown()

    # 获取行情测试
    def test_get_quote_normal(self):
        """
        获取行情报价
        """
        # 预设服务器端响应
        utils.RD = random.Random(4)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_md_basic_get_quote_normal.script.lzma"))
        # 获取行情
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        q = api.get_quote("SHFE.cu2111")
        self.assertEqual(q.datetime, "2021-09-29 09:50:51.000000")
        self.assertEqual(q.ask_price1, 68560.0)
        self.assertEqual(q.ask_volume1, 5)
        self.assertEqual(q.bid_price1, 68550.0)
        self.assertEqual(q.bid_volume1, 17)
        self.assertEqual(q.last_price, 68550.0)
        self.assertEqual(q.highest, 69210.0)
        self.assertEqual(q.lowest, 68300.0)
        self.assertEqual(q.open, 69110.0)
        self.assertNotEqual(q.close, q.close)  # q.close is nan
        self.assertEqual(q.average, 68714.205676)
        self.assertEqual(q.volume, 82907)
        self.assertEqual(q.amount, 28484443250.0)
        self.assertEqual(q.open_interest, 116892)
        self.assertNotEqual(q.settlement, q.settlement)
        self.assertEqual(q.upper_limit, 74770.0)
        self.assertEqual(q.lower_limit, 63700.0)
        self.assertEqual(q.pre_open_interest, 117870)
        self.assertEqual(q.pre_settlement, 69240.0)
        self.assertEqual(q.pre_close, 69230.0)
        self.assertEqual(q.price_tick, 10)
        self.assertEqual(q.price_decs, 0)
        self.assertEqual(q.volume_multiple, 5)
        self.assertEqual(q.max_limit_order_volume, 500)
        self.assertEqual(q.max_market_order_volume, 0)
        self.assertEqual(q.min_limit_order_volume, 0)
        self.assertEqual(q.min_market_order_volume, 0)
        self.assertEqual(q.underlying_symbol, "")
        self.assertTrue(q.strike_price != q.strike_price)  # 判定nan
        self.assertEqual(q.expired, False)
        self.assertEqual(q.ins_class, "FUTURE")
        # 这两个字段不是对用户承诺的字段，api 中调用 _symbols_to_quotes 只有 objs.quote 里说明的字段
        # self.assertEqual(q.margin, 18249.0)
        # self.assertEqual(q.commission, 13.035)
        self.assertEqual(repr(q.trading_time.day),
                         "[['09:00:00', '10:15:00'], ['10:30:00', '11:30:00'], ['13:30:00', '15:00:00']]")
        self.assertEqual(repr(q.trading_time.night), "[['21:00:00', '25:00:00']]")
        self.assertEqual(q.expire_datetime, 1636959600.0)
        self.assertEqual(q.delivery_month, 11)
        self.assertEqual(q.delivery_year, 2021)
        self.assertEqual(q.instrument_id, "SHFE.cu2111")
        self.assertEqual(q.ask_price2, 68570.0)
        self.assertEqual(q.ask_volume2, 19)
        self.assertEqual(q.ask_price3, 68580.0)
        self.assertEqual(q.ask_volume3, 17)
        self.assertEqual(q.ask_price4, 68590.0)
        self.assertEqual(q.ask_volume4, 7)
        self.assertEqual(q.ask_price5, 68600)
        self.assertEqual(q.ask_volume5, 13)
        self.assertEqual(q.bid_price2, 68540.0)
        self.assertEqual(q.bid_volume2, 54)
        self.assertEqual(q.bid_price3, 68530.0)
        self.assertEqual(q.bid_volume3, 23)
        self.assertEqual(q.bid_price4, 68520.0)
        self.assertEqual(q.bid_volume4, 33)
        self.assertEqual(q.bid_price5, 68510)
        self.assertEqual(q.bid_volume5, 3)
        # 其他取值方式
        self.assertEqual(q["pre_close"], 69230.0)
        self.assertEqual(q.get("pre_settlement"), 69240.0)
        self.assertEqual(q.get("highest"), 69210.0)
        self.assertEqual(q.get("lowest"), 68300.0)
        self.assertEqual(q["open"], 69110.0)
        self.assertNotEqual(q["close"], q["close"])
        # 报错测试
        self.assertRaises(Exception, api.get_quote, "SHFE.au2199")
        self.assertRaises(KeyError, q.__getitem__, "ask_price6")
        api.close()

    def test_get_kline_serial(self):
        """
        获取K线数据
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_md_basic_get_kline_serial.script.lzma"))
        # 测试: 获取K线数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        klines = api.get_kline_serial("SHFE.cu2111", 10)
        self.assertEqual(klines.iloc[-1].close, 68540.0)
        self.assertEqual(klines.iloc[-1].id, 584587)
        self.assertEqual(klines.iloc[-2].id, 584586)
        self.assertEqual(klines.iloc[-1].datetime, 1632880260000000000)
        self.assertEqual(klines.iloc[-1].open, 68560)
        self.assertEqual(klines.iloc[-1].volume, 35)
        self.assertEqual(klines.iloc[-1].open_oi, 116884)
        self.assertEqual(klines.iloc[-1].duration, 10)
        # 其他取值方式
        self.assertEqual(klines.duration.iloc[-1], 10)
        self.assertEqual(klines.iloc[-1]["duration"], 10)
        self.assertEqual(klines["duration"].iloc[-1], 10)
        # 报错测试
        self.assertRaises(Exception, api.get_kline_serial, "SHFE.au1999", 10)
        self.assertRaises(AttributeError, klines.iloc[-1].__getattribute__, "dur")
        self.assertRaises(KeyError, klines.iloc[-1].__getitem__, "dur")
        api.close()

    def test_get_tick_serial(self):
        """
        获取tick数据
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_md_basic_get_tick_serial.script.lzma"))
        # 测试: 获取tick数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        ticks = api.get_tick_serial("SHFE.cu2111")
        self.assertEqual(ticks.iloc[-1].id, 3412507)
        self.assertEqual(ticks.iloc[-1].datetime, 1632880274000000000)
        self.assertEqual(ticks.iloc[-1].last_price, 68560.0)
        self.assertEqual(ticks.iloc[-1].average, 68713.95901)
        self.assertEqual(ticks.iloc[-1].highest, 69210.0)
        self.assertEqual(ticks.iloc[-1].lowest, 68300.0)
        self.assertEqual(ticks.iloc[-1].ask_price1, 68570.0)
        self.assertEqual(ticks.iloc[-1].ask_volume1, 13)
        self.assertEqual(ticks.iloc[-1].bid_price1, 68560.0)
        self.assertEqual(ticks.iloc[-1].bid_volume1, 15)
        self.assertEqual(ticks.iloc[-1].volume, 83041)
        self.assertEqual(ticks.iloc[-1].amount, 28530379350)
        self.assertEqual(ticks.iloc[-1].open_interest, 116852)
        self.assertEqual(ticks.iloc[-1].duration, 0)
        # 其他调用方式
        self.assertEqual(ticks.open_interest.iloc[-1], 116852)
        self.assertEqual(ticks["open_interest"].iloc[-2], 116852)
        self.assertEqual(ticks.iloc[-1]["ask_price1"], 68570)
        # 报错测试
        self.assertRaises(Exception, api.get_tick_serial, "SHFE.au2199")
        self.assertRaises(AttributeError, ticks.iloc[-1].__getattribute__, "dur")
        self.assertRaises(KeyError, ticks.iloc[-1].__getitem__, "dur")
        api.close()

    def test_get_kline_serial_adj_type(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_md_basic_get_kline_serial_adj_type.script.lzma"))
        # 测试: 获取tick数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        klines1 = api.get_kline_serial("SSE.600853", 86400, adj_type=None)
        self.assertEqual(klines1.iloc[-100].id, 811)
        self.assertEqual(klines1.iloc[-100].datetime, 1620576000000000000)
        self.assertEqual(klines1.iloc[-100].open, 2.57)
        self.assertEqual(klines1.iloc[-100].high, 2.59)
        self.assertEqual(klines1.iloc[-100].low, 2.55)
        self.assertEqual(klines1.iloc[-100].close, 2.58)
        self.assertEqual(klines1.iloc[-100].volume, 5064793)
        self.assertEqual(klines1.iloc[-100].open_oi, 0)
        self.assertEqual(klines1.iloc[-100].duration, 86400)

        klines2 = api.get_kline_serial("SSE.600853", 86400, adj_type="FORWARD")
        self.assertEqual(klines2.iloc[-100].id, 811)
        self.assertEqual(klines2.iloc[-100].datetime, 1620576000000000000)
        self.assertAlmostEqual(klines2.iloc[-100].open, 2.57, places=4)
        self.assertAlmostEqual(klines2.iloc[-100].high, 2.59, places=4)
        self.assertAlmostEqual(klines2.iloc[-100].low, 2.55, places=4)
        self.assertAlmostEqual(klines2.iloc[-100].close, 2.58, places=4)
        self.assertEqual(klines2.iloc[-100].volume, 5064793)
        self.assertEqual(klines2.iloc[-100].open_oi, 0)
        self.assertEqual(klines2.iloc[-100].duration, 86400)

        klines3 = api.get_kline_serial("SSE.600853", 86400, adj_type="BACK")
        self.assertEqual(klines3.iloc[-1].id, 910)
        self.assertEqual(klines3.iloc[-1].datetime, 1632844800000000000)
        self.assertAlmostEqual(klines3.iloc[-1].open, 2.53, places=4)
        self.assertAlmostEqual(klines3.iloc[-1].high, 2.57, places=4)
        self.assertAlmostEqual(klines3.iloc[-1].low, 2.51, places=4)
        self.assertAlmostEqual(klines3.iloc[-1].close, 2.55, places=4)
        self.assertEqual(klines3.iloc[-1].volume, 1132181)
        self.assertEqual(klines3.iloc[-1].open_oi, 0)
        self.assertEqual(klines3.iloc[-1].duration, 86400)

        klines4 = api.get_kline_serial("SSE.600853", 3600, adj_type="FORWARD")
        self.assertEqual(klines4.iloc[-100].id, 4451)
        self.assertEqual(klines4.iloc[-100].datetime, 1630288800000000000)
        self.assertAlmostEqual(klines4.iloc[-100].open, 2.48, places=4)
        self.assertAlmostEqual(klines4.iloc[-100].high, 2.48, places=4)
        self.assertAlmostEqual(klines4.iloc[-100].low, 2.46, places=4)
        self.assertAlmostEqual(klines4.iloc[-100].close, 2.47, places=4)
        self.assertEqual(klines4.iloc[-100].volume, 2453676)
        self.assertEqual(klines4.iloc[-100].open_oi, 0)
        self.assertEqual(klines4.iloc[-100].duration, 3600)
        api.close()

    def test_get_tick_serial_adj_type(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_md_basic_get_tick_serial_adj_type.script.lzma"))

        # 测试: 获取tick数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        ticks = api.get_tick_serial("SSE.600853", adj_type=None)
        self.assertEqual(ticks.iloc[-199].id, 1394127)
        self.assertEqual(ticks.iloc[-199].datetime, 1632879649760000000)
        self.assertEqual(ticks.iloc[-199].last_price, 2.54)
        self.assertEqual(ticks.iloc[-199].average, 2.5349)
        self.assertEqual(ticks.iloc[-199].highest, 2.55)
        self.assertEqual(ticks.iloc[-199].lowest, 2.51)

        self.assertEqual(ticks.iloc[-199].ask_price1, 2.55)
        self.assertEqual(ticks.iloc[-199].ask_volume1, 97780)
        self.assertEqual(ticks.iloc[-199].bid_price1, 2.54)
        self.assertEqual(ticks.iloc[-199].bid_volume1, 20100)

        self.assertEqual(ticks.iloc[-199].ask_price2, 2.56)
        self.assertEqual(ticks.iloc[-199].ask_volume2, 27900)
        self.assertEqual(ticks.iloc[-199].bid_price2, 2.53)
        self.assertEqual(ticks.iloc[-199].bid_volume2, 61800)

        self.assertEqual(ticks.iloc[-199].ask_price3, 2.57)
        self.assertEqual(ticks.iloc[-199].ask_volume3, 43700)
        self.assertEqual(ticks.iloc[-199].bid_price3, 2.52)
        self.assertEqual(ticks.iloc[-199].bid_volume3, 349900)

        self.assertEqual(ticks.iloc[-199].ask_price4, 2.58)
        self.assertEqual(ticks.iloc[-199].ask_volume4, 64200)
        self.assertEqual(ticks.iloc[-199].bid_price4, 2.51)
        self.assertEqual(ticks.iloc[-199].bid_volume4, 46300)

        self.assertEqual(ticks.iloc[-199].ask_price5, 2.59)
        self.assertEqual(ticks.iloc[-199].ask_volume5, 101900)
        self.assertEqual(ticks.iloc[-199].bid_price5, 2.5)
        self.assertEqual(ticks.iloc[-199].bid_volume5, 103200)

        self.assertEqual(ticks.iloc[-199].volume, 656100)
        self.assertEqual(ticks.iloc[-199].amount, 1663145)
        api.close()
