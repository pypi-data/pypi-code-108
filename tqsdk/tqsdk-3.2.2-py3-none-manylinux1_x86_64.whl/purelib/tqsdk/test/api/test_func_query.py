#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import random
import sys
import unittest

from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk import TqApi, utils
from tqsdk.test.test_chan_helper import set_test_script


class TestFuncQuery(TQBaseTestcase):
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
        super(TestFuncQuery, self).setUp(md_url="wss://api.shinnytech.com/t/nfmd/front/mobile")

    def tearDown(self):
        super(TestFuncQuery, self).tearDown()

    def test_func_query(self):
        """
            is_changing() 测试
            注：本函数不是回测，重新生成测试用例script文件时更改为当前可交易的合约代码,在盘中生成,且_ins_url可能需修改。
        """

        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_func_query.script.lzma"))
        # 测试: 模拟账户下单
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        ls = api.query_quotes(ins_class="FUTURE", exchange_id="SHFE", product_id="rb", expired=False)
        self.assertEqual(
            ls,
            ['SHFE.rb2208', 'SHFE.rb2206', 'SHFE.rb2201', 'SHFE.rb2202', 'SHFE.rb2207', 'SHFE.rb2210', 'SHFE.rb2209',
             'SHFE.rb2204', 'SHFE.rb2205', 'SHFE.rb2203', 'SHFE.rb2111', 'SHFE.rb2112']
        )
        ls_cont = api.query_cont_quotes(exchange_id="DCE")
        self.assertEqual(
            ls_cont,
            ['DCE.pp2201', 'DCE.c2201', 'DCE.jm2201', 'DCE.rr2201', 'DCE.eg2201', 'DCE.bb2201', 'DCE.lh2201',
             'DCE.p2201', 'DCE.j2201', 'DCE.fb2201', 'DCE.y2201', 'DCE.a2201', 'DCE.eb2112', 'DCE.jd2201', 'DCE.l2201',
             'DCE.b2201', 'DCE.cs2201', 'DCE.i2201', 'DCE.m2201', 'DCE.v2201', 'DCE.pg2112']
        )
        in_options, at_options, out_options = api.query_all_level_options(underlying_symbol="DCE.m2109",
                                                                          underlying_price=2620, option_class="PUT")
        self.assertEqual(in_options, ['DCE.m2109-P-4150', 'DCE.m2109-P-4100', 'DCE.m2109-P-4050', 'DCE.m2109-P-4000', 'DCE.m2109-P-3950', 'DCE.m2109-P-3900', 'DCE.m2109-P-3850', 'DCE.m2109-P-3800', 'DCE.m2109-P-3750', 'DCE.m2109-P-3700', 'DCE.m2109-P-3650', 'DCE.m2109-P-3600', 'DCE.m2109-P-3550', 'DCE.m2109-P-3500', 'DCE.m2109-P-3450', 'DCE.m2109-P-3400', 'DCE.m2109-P-3350', 'DCE.m2109-P-3300', 'DCE.m2109-P-3250', 'DCE.m2109-P-3200', 'DCE.m2109-P-3150', 'DCE.m2109-P-3100', 'DCE.m2109-P-3050', 'DCE.m2109-P-3000', 'DCE.m2109-P-2950', 'DCE.m2109-P-2900', 'DCE.m2109-P-2850', 'DCE.m2109-P-2800', 'DCE.m2109-P-2750', 'DCE.m2109-P-2700', 'DCE.m2109-P-2650'])
        self.assertEqual(at_options, ['DCE.m2109-P-2600'])
        self.assertEqual(out_options, ['DCE.m2109-P-2550', 'DCE.m2109-P-2500'])
        in_options, at_options, out_options = api.query_all_level_finance_options(underlying_symbol="SSE.510300",
                                                                                  underlying_price=4.87,
                                                                                  option_class="CALL",
                                                                                  nearbys=[0, 1])
        self.assertEqual(in_options, ['SSE.10003527', 'SSE.10003641', 'SSE.10003528', 'SSE.10003642', 'SSE.10003411', 'SSE.10003643', 'SSE.10003391', 'SSE.10003644', 'SSE.10003392'])
        self.assertEqual(at_options, ['SSE.10003645'])
        self.assertEqual(out_options,  ['SSE.10003393', 'SSE.10003646', 'SSE.10003394', 'SSE.10003647', 'SSE.10003395', 'SSE.10003648', 'SSE.10003396', 'SSE.10003649', 'SSE.10003397', 'SSE.10003659', 'SSE.10003398', 'SSE.10003399'])
        df = api.query_symbol_info(in_options + at_options + out_options)

        print(df)
        api.close()

    def test_func_query_async(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_func_query_async.script.lzma"))

        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)

        async def t1(api):
            in_options, at_options, out_options = await api.query_all_level_options("SHFE.au2112", 365.0, "CALL")
            self.assertEqual(in_options, ['SHFE.au2112C324', 'SHFE.au2112C328', 'SHFE.au2112C332', 'SHFE.au2112C336', 'SHFE.au2112C340', 'SHFE.au2112C344', 'SHFE.au2112C348', 'SHFE.au2112C352', 'SHFE.au2112C356', 'SHFE.au2112C360'])
            self.assertEqual(at_options, ['SHFE.au2112C364'])
            self.assertEqual(out_options, ['SHFE.au2112C368', 'SHFE.au2112C372', 'SHFE.au2112C376', 'SHFE.au2112C380', 'SHFE.au2112C384', 'SHFE.au2112C388', 'SHFE.au2112C392', 'SHFE.au2112C396', 'SHFE.au2112C400', 'SHFE.au2112C408', 'SHFE.au2112C416', 'SHFE.au2112C424', 'SHFE.au2112C432', 'SHFE.au2112C440'])
            in_options, at_options, out_options = await api.query_all_level_finance_options("SSE.510300", 4.60, "CALL",
                                                                                            nearbys=1)
            self.assertEqual(in_options, ['SSE.10003527', 'SSE.10003528'])
            self.assertEqual(at_options, ['SSE.10003411'])
            self.assertEqual(out_options, ['SSE.10003391', 'SSE.10003392', 'SSE.10003393', 'SSE.10003394', 'SSE.10003395', 'SSE.10003396', 'SSE.10003397', 'SSE.10003398', 'SSE.10003399'])
            df = await api.query_symbol_info(in_options + at_options + out_options)
            print(df.to_string())

            ls = await api.query_quotes(ins_class="FUTURE", exchange_id="SHFE", expired=False, has_night=False)
            self.assertEqual(ls,
                             ['SHFE.wr2209', 'SHFE.wr2205', 'SHFE.wr2210', 'SHFE.wr2202', 'SHFE.wr2201', 'SHFE.wr2204',
                              'SHFE.wr2206', 'SHFE.wr2207', 'SHFE.wr2112', 'SHFE.wr2203', 'SHFE.wr2208', 'SHFE.wr2111'])
            ls = await api.query_cont_quotes(exchange_id="SHFE")
            self.assertEqual(ls,
                             ['SHFE.hc2201', 'SHFE.sn2112', 'SHFE.ag2112', 'SHFE.zn2112', 'SHFE.bu2112', 'SHFE.rb2201',
                              'SHFE.ss2112', 'SHFE.au2112', 'SHFE.sp2112', 'SHFE.ni2112', 'SHFE.pb2112', 'SHFE.ru2201',
                              'SHFE.wr2202', 'SHFE.al2112', 'SHFE.cu2112', 'SHFE.fu2201'])
            df = await api.query_symbol_info(ls)
            print(df.to_string())

            ls = await api.query_options(underlying_symbol="SHFE.cu2112")
            self.assertEqual(ls, ['SHFE.cu2112P80000', 'SHFE.cu2112P65000', 'SHFE.cu2112P64000', 'SHFE.cu2112C84000', 'SHFE.cu2112P76000', 'SHFE.cu2112C76000', 'SHFE.cu2112C61000', 'SHFE.cu2112P74000', 'SHFE.cu2112C72000', 'SHFE.cu2112C71000', 'SHFE.cu2112C79000', 'SHFE.cu2112C64000', 'SHFE.cu2112C70000', 'SHFE.cu2112P82000', 'SHFE.cu2112C66000', 'SHFE.cu2112C69000', 'SHFE.cu2112C62000', 'SHFE.cu2112P77000', 'SHFE.cu2112P63000', 'SHFE.cu2112P66000', 'SHFE.cu2112P69000', 'SHFE.cu2112C67000', 'SHFE.cu2112P62000', 'SHFE.cu2112C74000', 'SHFE.cu2112P67000', 'SHFE.cu2112C75000', 'SHFE.cu2112P72000', 'SHFE.cu2112P71000', 'SHFE.cu2112C68000', 'SHFE.cu2112P84000', 'SHFE.cu2112C73000', 'SHFE.cu2112P75000', 'SHFE.cu2112P79000', 'SHFE.cu2112P70000', 'SHFE.cu2112P61000', 'SHFE.cu2112C63000', 'SHFE.cu2112C77000', 'SHFE.cu2112C82000', 'SHFE.cu2112C78000', 'SHFE.cu2112C80000', 'SHFE.cu2112P68000', 'SHFE.cu2112C65000', 'SHFE.cu2112P73000', 'SHFE.cu2112P78000'])
            ls = await api.query_atm_options(underlying_symbol="SHFE.cu2112", underlying_price=20000, price_level=0,
                                             option_class="CALL")
            self.assertEqual(ls, ['SHFE.cu2112C61000'])

        task1 = api.create_task(t1(api))

        while not task1.done():
            api.wait_update(_task=task1)
        api.close()
