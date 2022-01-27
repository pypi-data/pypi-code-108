#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import random
import time

from tqsdk import TqApi, utils
from tqsdk.ta import MA
from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk.test.test_chan_helper import set_test_script


class TestWaitUpdateFunction(TQBaseTestcase):
    """
    功能函数 wait_update() 测试.

    注：
    1. 在本地运行测试用例前需设置运行环境变量(Environment variables), 保证api中dict及set等类型的数据序列在每次运行时元素顺序一致: PYTHONHASHSEED=32
    2. 若测试用例中调用了会使用uuid的功能函数时（如insert_order()会使用uuid生成order_id）,
        则：在生成script文件时及测试用例中都需设置 utils.RD = random.Random(x), 以保证两次生成的uuid一致, x取值范围为0-2^32
    3. 对盘中的测试用例（即非回测）：因为TqSim模拟交易 Order 的 insert_date_time 和 Trade 的 trade_date_time 不是固定值，所以改为判断范围。
        盘中时：self.assertAlmostEqual(1575292560005832000 / 1e9, order1.insert_date_time / 1e9, places=1)
        回测时：self.assertEqual(1575291600000000000, order1.insert_date_time)
    """

    def setUp(self):
        super(TestWaitUpdateFunction, self).setUp()

    def tearDown(self):
        super(TestWaitUpdateFunction, self).tearDown()

    def test_wait_update_1(self):
        """
        若未连接天勤时修改了K线字段,则不应发送set_chart_data指令到服务器 (即不能调用api.py中_process_serial_extra_array()); 否则导致与服务器断连
        related issue: #146
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_func_wait_update_1.script.lzma"))
        # 测试
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        klines = api.get_kline_serial("SHFE.cu2112", 10)
        klines["ma"] = MA(klines, 15)  # 测试语句
        deadline = time.time() + 10
        while api.wait_update(deadline=deadline):
            pass

        api.close()

# C:\vnstudio2\python.exe -m pytest -n 12 C:\Users\yanqiong\Documents\tqsdk-python-private\tqsdk\test\api --show-capture=no --log-level=ERROR --log-file=E:\logs\debug.log
