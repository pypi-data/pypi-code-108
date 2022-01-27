#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import datetime
import os
import random
import sys
import unittest

from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk import TqApi, utils, TqBacktest, BacktestFinished
from tqsdk.test.test_chan_helper import set_test_script


class TestFuncQueryBacktest(TQBaseTestcase):
    """
    TqApi中功能函数的基本功能测试.

    注：
    1. 在本地运行测试用例前需设置运行环境变量(Environment variables), 保证api中dict及set等类型的数据序列在每次运行时元素顺序一致: PYTHONHASHSEED=32
    2. 若测试用例中调用了会使用uuid的功能函数时（如insert_order()会使用uuid生成order_id）,
        则：在生成script文件时及测试用例中都需设置 TqApi.RD = random.Random(x), 以保证两次生成的uuid一致, x取值范围为0-2^32
    3. 对盘中的测试用例（即非回测）：因为TqSim模拟交易 Order 的 insert_date_time 和 Trade 的 trade_date_time 不是固定值，所以改为判断范围。
        盘中时：self.assertAlmostEqual(1575292560005832000 / 1e9, order1.insert_date_time / 1e9, places=1)
        回测时：self.assertEqual(1575291600000000000, order1.insert_date_time)
    """

    def setUp(self):
        super(TestFuncQueryBacktest, self).setUp(md_url="wss://backtest.shinnytech.com/t/nfmd/front/mobile")

    def tearDown(self):
        super(TestFuncQueryBacktest, self).tearDown()

    def test_func_query_backtest(self):
        """
            is_changing() 测试
            注：本函数不是回测，重新生成测试用例script文件时更改为当前可交易的合约代码,在盘中生成,且_ins_url可能需修改。
        """

        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://backtest.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_func_query_backtest.script.lzma"))

        # 测试: 模拟账户下单
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url,
                    backtest=TqBacktest(datetime.datetime(2021, 5, 5, 21, 0, 0), datetime.datetime(2021, 7, 25, 18, 0, 0)))
        klines = api.get_kline_serial("SHFE.cu2109", duration_seconds=3600)  # 以小时线推进行情
        while datetime.datetime.fromtimestamp(klines.iloc[-1].datetime / 1e9) < datetime.datetime(2021, 5, 5):
            api.wait_update()
        ls = api.query_cont_quotes()
        ls.sort()
        self.assertEqual(ls, ['CFFEX.IC2105', 'CFFEX.IF2105', 'CFFEX.IH2105', 'CFFEX.T2106', 'CFFEX.TF2106', 'CFFEX.TS2106', 'CZCE.AP110', 'CZCE.CF109', 'CZCE.CJ109', 'CZCE.CY109', 'CZCE.FG109', 'CZCE.JR109', 'CZCE.LR109', 'CZCE.MA109', 'CZCE.OI109', 'CZCE.PF107', 'CZCE.PK110', 'CZCE.PM107', 'CZCE.RI109', 'CZCE.RM109', 'CZCE.RS107', 'CZCE.SA109', 'CZCE.SF109', 'CZCE.SM109', 'CZCE.SR109', 'CZCE.TA109', 'CZCE.UR107', 'CZCE.WH109', 'CZCE.ZC109', 'DCE.a2109', 'DCE.b2106', 'DCE.bb2105', 'DCE.c2109', 'DCE.cs2107', 'DCE.eb2106', 'DCE.eg2109', 'DCE.fb2106', 'DCE.i2109', 'DCE.j2109', 'DCE.jd2109', 'DCE.jm2109', 'DCE.l2109', 'DCE.lh2109', 'DCE.m2109', 'DCE.p2109', 'DCE.pg2106', 'DCE.pp2109', 'DCE.rr2107', 'DCE.v2109', 'DCE.y2109', 'INE.bc2106', 'INE.lu2108', 'INE.nr2107', 'INE.sc2106', 'SHFE.ag2106', 'SHFE.al2106', 'SHFE.au2106', 'SHFE.bu2106', 'SHFE.cu2106', 'SHFE.fu2109', 'SHFE.hc2110', 'SHFE.ni2106', 'SHFE.pb2106', 'SHFE.rb2110', 'SHFE.ru2109', 'SHFE.sn2106', 'SHFE.sp2106', 'SHFE.ss2106', 'SHFE.wr2110', 'SHFE.zn2106'])
        in_options, at_options, out_options = api.query_all_level_finance_options(underlying_symbol="SSE.510300",
                                                                                  underlying_price=4.87,
                                                                                  option_class="CALL",
                                                                                  nearbys=[0, 1])
        self.assertEqual(in_options + at_options + out_options,
              ['SSE.10002877', 'SSE.10002878', 'SSE.10003321', 'SSE.10003323', 'SSE.10002879', 'SSE.10003311',
               'SSE.10003313', 'SSE.10002880', 'SSE.10003247', 'SSE.10003249', 'SSE.10002881', 'SSE.10003179',
               'SSE.10003223', 'SSE.10002882', 'SSE.10003180', 'SSE.10003224', 'SSE.10002883', 'SSE.10003181',
               'SSE.10003225', 'SSE.10002884', 'SSE.10003182', 'SSE.10003226', 'SSE.10002885', 'SSE.10003183',
               'SSE.10003227', 'SSE.10002897', 'SSE.10003184', 'SSE.10003228', 'SSE.10002905', 'SSE.10003185',
               'SSE.10003229', 'SSE.10003035', 'SSE.10003186', 'SSE.10003230', 'SSE.10003099', 'SSE.10003187',
               'SSE.10003231', 'SSE.10003123', 'SSE.10003203', 'SSE.10003253']
              )
        df = api.query_symbol_info(in_options + at_options + out_options)
        while datetime.datetime.fromtimestamp(klines.iloc[-1].datetime / 1e9) < datetime.datetime(2021, 5, 20):
            api.wait_update()
        ls = api.query_cont_quotes()
        ls.sort()
        self.assertEqual(ls, ['CFFEX.IC2106', 'CFFEX.IF2106', 'CFFEX.IH2106', 'CFFEX.T2109', 'CFFEX.TF2109', 'CFFEX.TS2109', 'CZCE.AP110', 'CZCE.CF109', 'CZCE.CJ109', 'CZCE.CY109', 'CZCE.FG109', 'CZCE.JR109', 'CZCE.LR109', 'CZCE.MA109', 'CZCE.OI109', 'CZCE.PF109', 'CZCE.PK110', 'CZCE.PM107', 'CZCE.RI109', 'CZCE.RM109', 'CZCE.RS107', 'CZCE.SA109', 'CZCE.SF109', 'CZCE.SM109', 'CZCE.SR109', 'CZCE.TA109', 'CZCE.UR107', 'CZCE.WH109', 'CZCE.ZC109', 'DCE.a2109', 'DCE.b2107', 'DCE.bb2109', 'DCE.c2109', 'DCE.cs2107', 'DCE.eb2106', 'DCE.eg2109', 'DCE.fb2106', 'DCE.i2109', 'DCE.j2109', 'DCE.jd2109', 'DCE.jm2109', 'DCE.l2109', 'DCE.lh2109', 'DCE.m2109', 'DCE.p2109', 'DCE.pg2106', 'DCE.pp2109', 'DCE.rr2107', 'DCE.v2109', 'DCE.y2109', 'INE.bc2107', 'INE.lu2108', 'INE.nr2107', 'INE.sc2107', 'SHFE.ag2106', 'SHFE.al2107', 'SHFE.au2106', 'SHFE.bu2106', 'SHFE.cu2107', 'SHFE.fu2109', 'SHFE.hc2110', 'SHFE.ni2106', 'SHFE.pb2106', 'SHFE.rb2110', 'SHFE.ru2109', 'SHFE.sn2107', 'SHFE.sp2107', 'SHFE.ss2107', 'SHFE.wr2110', 'SHFE.zn2106'])
        in_options, at_options, out_options = api.query_all_level_finance_options(underlying_symbol="SSE.510300",
                                                                                  underlying_price=4.87,
                                                                                  option_class="CALL",
                                                                                  nearbys=[0, 1])
        self.assertEqual(in_options + at_options + out_options,
              ['SSE.10002877', 'SSE.10002878', 'SSE.10003321', 'SSE.10003323', 'SSE.10002879', 'SSE.10003311',
               'SSE.10003313', 'SSE.10002880', 'SSE.10003247', 'SSE.10003249', 'SSE.10002881', 'SSE.10003179',
               'SSE.10003223', 'SSE.10002882', 'SSE.10003180', 'SSE.10003224', 'SSE.10002883', 'SSE.10003181',
               'SSE.10003225', 'SSE.10002884', 'SSE.10003182', 'SSE.10003226', 'SSE.10002885', 'SSE.10003183',
               'SSE.10003227', 'SSE.10002897', 'SSE.10003184', 'SSE.10003228', 'SSE.10002905', 'SSE.10003185',
               'SSE.10003229', 'SSE.10003035', 'SSE.10003186', 'SSE.10003230', 'SSE.10003099', 'SSE.10003187',
               'SSE.10003231', 'SSE.10003123', 'SSE.10003203', 'SSE.10003253']
              )
        df = api.query_symbol_info(in_options + at_options + out_options)
        while datetime.datetime.fromtimestamp(klines.iloc[-1].datetime / 1e9) < datetime.datetime(2021, 6, 5):
            api.wait_update()

        ls = api.query_cont_quotes()
        ls.sort()
        self.assertEqual(ls, ['CFFEX.IC2106', 'CFFEX.IF2106', 'CFFEX.IH2106', 'CFFEX.T2109', 'CFFEX.TF2109', 'CFFEX.TS2109', 'CZCE.AP110', 'CZCE.CF109', 'CZCE.CJ109', 'CZCE.CY109', 'CZCE.FG109', 'CZCE.JR109', 'CZCE.LR109', 'CZCE.MA109', 'CZCE.OI109', 'CZCE.PF109', 'CZCE.PK110', 'CZCE.PM107', 'CZCE.RI109', 'CZCE.RM109', 'CZCE.RS107', 'CZCE.SA109', 'CZCE.SF109', 'CZCE.SM109', 'CZCE.SR109', 'CZCE.TA109', 'CZCE.UR107', 'CZCE.WH109', 'CZCE.ZC109', 'DCE.a2109', 'DCE.b2107', 'DCE.bb2109', 'DCE.c2109', 'DCE.cs2107', 'DCE.eb2107', 'DCE.eg2109', 'DCE.fb2109', 'DCE.i2109', 'DCE.j2109', 'DCE.jd2109', 'DCE.jm2109', 'DCE.l2109', 'DCE.lh2109', 'DCE.m2109', 'DCE.p2109', 'DCE.pg2107', 'DCE.pp2109', 'DCE.rr2108', 'DCE.v2109', 'DCE.y2109', 'INE.bc2108', 'INE.lu2109', 'INE.nr2108', 'INE.sc2107', 'SHFE.ag2112', 'SHFE.al2107', 'SHFE.au2112', 'SHFE.bu2109', 'SHFE.cu2107', 'SHFE.fu2109', 'SHFE.hc2110', 'SHFE.ni2107', 'SHFE.pb2107', 'SHFE.rb2110', 'SHFE.ru2109', 'SHFE.sn2107', 'SHFE.sp2107', 'SHFE.ss2107', 'SHFE.wr2110', 'SHFE.zn2107'])
        in_options, at_options, out_options = api.query_all_level_finance_options(underlying_symbol="SSE.510300",
                                                                                  underlying_price=4.87,
                                                                                  option_class="CALL",
                                                                                  nearbys=[0, 1])
        self.assertEqual(in_options + at_options + out_options,
                         ['SSE.10002877', 'SSE.10002878', 'SSE.10003321', 'SSE.10002879', 'SSE.10003311',
                          'SSE.10002880', 'SSE.10003247', 'SSE.10003433', 'SSE.10002881', 'SSE.10003179',
                          'SSE.10003434', 'SSE.10002882', 'SSE.10003180', 'SSE.10003435', 'SSE.10002883',
                          'SSE.10003181', 'SSE.10003436', 'SSE.10002884', 'SSE.10003182', 'SSE.10003437',
                          'SSE.10002885', 'SSE.10003183', 'SSE.10003438', 'SSE.10002897', 'SSE.10003184',
                          'SSE.10003439', 'SSE.10002905', 'SSE.10003185', 'SSE.10003440', 'SSE.10003035',
                          'SSE.10003186', 'SSE.10003441', 'SSE.10003099', 'SSE.10003187', 'SSE.10003123',
                          'SSE.10003203']
                         )
        df = api.query_symbol_info(in_options + at_options + out_options)
        while datetime.datetime.fromtimestamp(klines.iloc[-1].datetime / 1e9) < datetime.datetime(2021, 6, 20):
            api.wait_update()
        ls = api.query_cont_quotes()
        ls.sort()
        self.assertEqual(ls, ['CFFEX.IC2107', 'CFFEX.IF2107', 'CFFEX.IH2107', 'CFFEX.T2109', 'CFFEX.TF2109', 'CFFEX.TS2109', 'CZCE.AP110', 'CZCE.CF109', 'CZCE.CJ109', 'CZCE.CY109', 'CZCE.FG109', 'CZCE.JR109', 'CZCE.LR109', 'CZCE.MA109', 'CZCE.OI109', 'CZCE.PF109', 'CZCE.PK110', 'CZCE.PM107', 'CZCE.RI109', 'CZCE.RM109', 'CZCE.RS109', 'CZCE.SA109', 'CZCE.SF109', 'CZCE.SM109', 'CZCE.SR109', 'CZCE.TA109', 'CZCE.UR109', 'CZCE.WH109', 'CZCE.ZC109', 'DCE.a2109', 'DCE.b2108', 'DCE.bb2109', 'DCE.c2109', 'DCE.cs2107', 'DCE.eb2107', 'DCE.eg2109', 'DCE.fb2109', 'DCE.i2109', 'DCE.j2109', 'DCE.jd2109', 'DCE.jm2109', 'DCE.l2109', 'DCE.lh2109', 'DCE.m2109', 'DCE.p2109', 'DCE.pg2108', 'DCE.pp2109', 'DCE.rr2108', 'DCE.v2109', 'DCE.y2109', 'INE.bc2108', 'INE.lu2109', 'INE.nr2108', 'INE.sc2108', 'SHFE.ag2112', 'SHFE.al2107', 'SHFE.au2112', 'SHFE.bu2109', 'SHFE.cu2107', 'SHFE.fu2109', 'SHFE.hc2110', 'SHFE.ni2107', 'SHFE.pb2107', 'SHFE.rb2110', 'SHFE.ru2109', 'SHFE.sn2108', 'SHFE.sp2109', 'SHFE.ss2107', 'SHFE.wr2110', 'SHFE.zn2107'])
        in_options, at_options, out_options = api.query_all_level_finance_options(underlying_symbol="SSE.510300",
                                                                                  underlying_price=4.87,
                                                                                  option_class="CALL",
                                                                                  nearbys=[0, 1])
        self.assertEqual(in_options + at_options + out_options,
                         ['SSE.10002877', 'SSE.10002878', 'SSE.10003321', 'SSE.10002879', 'SSE.10003311',
                          'SSE.10003457', 'SSE.10002880', 'SSE.10003247', 'SSE.10003433', 'SSE.10002881',
                          'SSE.10003179', 'SSE.10003434', 'SSE.10002882', 'SSE.10003180', 'SSE.10003435',
                          'SSE.10002883', 'SSE.10003181', 'SSE.10003436', 'SSE.10002884', 'SSE.10003182',
                          'SSE.10003437', 'SSE.10002885', 'SSE.10003183', 'SSE.10003438', 'SSE.10002897',
                          'SSE.10003184', 'SSE.10003439', 'SSE.10002905', 'SSE.10003185', 'SSE.10003440',
                          'SSE.10003035', 'SSE.10003186', 'SSE.10003441', 'SSE.10003099', 'SSE.10003187',
                          'SSE.10003123', 'SSE.10003203']
                         )

        df = api.query_symbol_info(in_options + at_options + out_options)
        while datetime.datetime.fromtimestamp(klines.iloc[-1].datetime / 1e9) < datetime.datetime(2021, 7, 5):
            api.wait_update()

        ls = api.query_cont_quotes()
        ls.sort()
        self.assertEqual(ls, ['CFFEX.IC2107', 'CFFEX.IF2107', 'CFFEX.IH2107', 'CFFEX.T2109', 'CFFEX.TF2109', 'CFFEX.TS2109', 'CZCE.AP110', 'CZCE.CF109', 'CZCE.CJ109', 'CZCE.CY109', 'CZCE.FG109', 'CZCE.JR109', 'CZCE.LR109', 'CZCE.MA109', 'CZCE.OI109', 'CZCE.PF109', 'CZCE.PK110', 'CZCE.PM107', 'CZCE.RI109', 'CZCE.RM109', 'CZCE.RS109', 'CZCE.SA109', 'CZCE.SF109', 'CZCE.SM109', 'CZCE.SR109', 'CZCE.TA109', 'CZCE.UR109', 'CZCE.WH109', 'CZCE.ZC109', 'DCE.a2109', 'DCE.b2108', 'DCE.bb2109', 'DCE.c2109', 'DCE.cs2109', 'DCE.eb2108', 'DCE.eg2109', 'DCE.fb2109', 'DCE.i2109', 'DCE.j2109', 'DCE.jd2109', 'DCE.jm2109', 'DCE.l2109', 'DCE.lh2109', 'DCE.m2109', 'DCE.p2109', 'DCE.pg2108', 'DCE.pp2109', 'DCE.rr2109', 'DCE.v2109', 'DCE.y2109', 'INE.bc2109', 'INE.lu2109', 'INE.nr2109', 'INE.sc2108', 'SHFE.ag2112', 'SHFE.al2108', 'SHFE.au2112', 'SHFE.bu2109', 'SHFE.cu2108', 'SHFE.fu2109', 'SHFE.hc2110', 'SHFE.ni2108', 'SHFE.pb2108', 'SHFE.rb2110', 'SHFE.ru2109', 'SHFE.sn2108', 'SHFE.sp2109', 'SHFE.ss2108', 'SHFE.wr2110', 'SHFE.zn2108'])
        in_options, at_options, out_options = api.query_all_level_finance_options(underlying_symbol="SSE.510300",
                                                                                  underlying_price=4.87,
                                                                                  option_class="CALL",
                                                                                  nearbys=[0, 1])
        self.assertEqual(in_options + at_options + out_options,
                         ['SSE.10003457', 'SSE.10003499', 'SSE.10003433', 'SSE.10003479', 'SSE.10003434', 'SSE.10003480', 'SSE.10003435', 'SSE.10003481', 'SSE.10003436', 'SSE.10003482', 'SSE.10003437', 'SSE.10003483', 'SSE.10003438', 'SSE.10003484', 'SSE.10003439', 'SSE.10003485', 'SSE.10003440', 'SSE.10003486', 'SSE.10003441', 'SSE.10003487']
                         )

        df = api.query_symbol_info(in_options + at_options + out_options)
        while datetime.datetime.fromtimestamp(klines.iloc[-1].datetime / 1e9) < datetime.datetime(2021, 7, 20):
            api.wait_update()

        ls = api.query_cont_quotes()
        ls.sort()
        self.assertEqual(ls, ['CFFEX.IC2108', 'CFFEX.IF2108', 'CFFEX.IH2108', 'CFFEX.T2109', 'CFFEX.TF2109', 'CFFEX.TS2109', 'CZCE.AP110', 'CZCE.CF109', 'CZCE.CJ109', 'CZCE.CY109', 'CZCE.FG109', 'CZCE.JR109', 'CZCE.LR201', 'CZCE.MA109', 'CZCE.OI109', 'CZCE.PF109', 'CZCE.PK110', 'CZCE.PM109', 'CZCE.RI201', 'CZCE.RM109', 'CZCE.RS109', 'CZCE.SA109', 'CZCE.SF109', 'CZCE.SM109', 'CZCE.SR109', 'CZCE.TA109', 'CZCE.UR109', 'CZCE.WH109', 'CZCE.ZC109', 'DCE.a2109', 'DCE.b2109', 'DCE.bb2201', 'DCE.c2109', 'DCE.cs2109', 'DCE.eb2108', 'DCE.eg2109', 'DCE.fb2109', 'DCE.i2109', 'DCE.j2109', 'DCE.jd2109', 'DCE.jm2109', 'DCE.l2109', 'DCE.lh2109', 'DCE.m2109', 'DCE.p2109', 'DCE.pg2109', 'DCE.pp2109', 'DCE.rr2109', 'DCE.v2109', 'DCE.y2109', 'INE.bc2109', 'INE.lu2110', 'INE.nr2109', 'INE.sc2109', 'SHFE.ag2112', 'SHFE.al2108', 'SHFE.au2112', 'SHFE.bu2109', 'SHFE.cu2108', 'SHFE.fu2109', 'SHFE.hc2110', 'SHFE.ni2108', 'SHFE.pb2108', 'SHFE.rb2110', 'SHFE.ru2109', 'SHFE.sn2108', 'SHFE.sp2109', 'SHFE.ss2108', 'SHFE.wr2110', 'SHFE.zn2108'])
        in_options, at_options, out_options = api.query_all_level_finance_options(underlying_symbol="SSE.510300",
                                                                                  underlying_price=4.87,
                                                                                  option_class="CALL",
                                                                                  nearbys=[0, 1])
        self.assertEqual(in_options + at_options + out_options,
              ['SSE.10003457', 'SSE.10003499', 'SSE.10003433', 'SSE.10003479', 'SSE.10003434', 'SSE.10003480',
               'SSE.10003435', 'SSE.10003481', 'SSE.10003436', 'SSE.10003482', 'SSE.10003437', 'SSE.10003483',
               'SSE.10003438', 'SSE.10003484', 'SSE.10003439', 'SSE.10003485', 'SSE.10003440', 'SSE.10003486',
               'SSE.10003441', 'SSE.10003487']
              )

        df = api.query_symbol_info(in_options + at_options + out_options)
        try:
            while True:
                api.wait_update()
        except BacktestFinished:
            api.close()
