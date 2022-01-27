#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import random

from tqsdk import TqApi, utils
from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk.test.test_chan_helper import set_test_script


class TestTsBasic(TQBaseTestcase):
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
        super(TestTsBasic, self).setUp()

    def tearDown(self):
        super(TestTsBasic, self).tearDown()

    # 获取行情测试
    def test_get_trading_status(self):
        """
        获取行情报价
        """
        # 预设服务器端响应
        utils.RD = random.Random(4)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_ts_basic_get_trading_status.script.lzma"))
        # 获取行情
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        ts = api.get_trading_status("SHFE.cu2112")
        print(ts)
        self.assertEqual(ts, {'symbol': 'SHFE.cu2112', 'trade_status': 'CONTINOUS'})
        api.close()
