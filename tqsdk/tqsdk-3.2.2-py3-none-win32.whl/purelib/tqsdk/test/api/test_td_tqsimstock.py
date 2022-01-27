#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'mayanqiong'


import os
import datetime
import random

from tqsdk import TqApi, TqBacktest, BacktestFinished, TqSimStock, utils
from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk.test.test_chan_helper import set_test_script


class TestTdBacktestTqsimstock(TQBaseTestcase):
    """
    回测时的交易测试.

    注：
    1. 在本地运行测试用例前需设置运行环境变量(Environment variables), 保证api中dict及set等类型的数据序列在每次运行时元素顺序一致: PYTHONHASHSEED=32
    2. 若测试用例中调用了会使用uuid的功能函数时（如insert_order()会使用uuid生成order_id）,
        则：在生成script文件时及测试用例中都需设置 utils.RD = random.Random(x), 以保证两次生成的uuid一致, x取值范围为0-2^32
    3. 对盘中的测试用例（即非回测）：因为TqSim模拟交易 Order 的 insert_date_time 和 Trade 的 trade_date_time 不是固定值，所以改为判断范围。
        盘中时：self.assertAlmostEqual(1575292560005832000 / 1e9, order1.insert_date_time / 1e9, places=1)
        回测时：self.assertEqual(1575291600000000000, order1.insert_date_time)
    """

    def setUp(self):
        super(TestTdBacktestTqsimstock, self).setUp()

    def tearDown(self):
        super(TestTdBacktestTqsimstock, self).tearDown()

    def test_tqsimstock(self):
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://backtest.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_backtest_tqsimstock.script.lzma"))
        utils.RD = random.Random(4)
        simstock = TqSimStock()
        api = TqApi(
            account=simstock,
            backtest=TqBacktest(start_dt=datetime.datetime(2021, 7, 12), end_dt=datetime.datetime(2021, 7, 22)),
            auth="tianqin,tianqin", _md_url=md_url
        )
        symbol = 'SSE.603666'
        quote = api.get_quote(symbol)
        account = simstock.get_account()
        position = simstock.get_position(symbol)
        print(account)
        self.assertEqual(
            "{'user_id': 'TQSIM_STOCK', 'currency': 'CNY', 'market_value': 0.0, 'asset': 10000000.0, 'asset_his': 10000000.0, 'available': 10000000.0, 'available_his': 10000000.0, 'cost': 0.0, 'drawable': 10000000.0, 'deposit': 0.0, 'withdraw': 0.0, 'buy_frozen_balance': 0.0, 'buy_frozen_fee': 0.0, 'buy_balance_today': 0.0, 'buy_fee_today': 0.0, 'sell_balance_today': 0.0, 'sell_fee_today': 0.0, 'hold_profit': 0.0, 'float_profit_today': 0.0, 'real_profit_today': 0.0, 'profit_today': 0.0, 'profit_rate_today': 0.0, 'dividend_balance_today': 0.0, 'market_value_his': 0.0, 'cost_his': 0.0}",
            str(account)
        )
        try:
            while datetime.datetime.strptime(quote.datetime, "%Y-%m-%d %H:%M:%S.%f") < datetime.datetime(2021, 7, 12, 10, 30):
                api.wait_update()
            order1 = api.insert_order("SSE.603666", direction="BUY", volume=600)
            api.wait_update()
            print("order1", "=" * 100)
            self.assertEqual(order1.order_id, 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258')
            self.assertEqual(order1.volume_orign, 600)
            self.assertEqual(order1.volume_left, 0)
            self.assertEqual(order1.status, "FINISHED")
            self.assertEqual(position.volume, 600)
            self.assertEqual(account.available, 9945266.32)

            while datetime.datetime.strptime(quote.datetime, "%Y-%m-%d %H:%M:%S.%f") < datetime.datetime(2021, 7, 14, 9, 50):
                api.wait_update()
            order2 = api.insert_order("SSE.603666", direction="BUY", volume=200, limit_price=quote.bid_price1)
            api.wait_update()
            print("order2", "=" * 100)
            self.assertEqual(order2.volume_orign, 200)
            self.assertEqual(order2.volume_left, 200)
            self.assertEqual(order2.status, "ALIVE")
            self.assertEqual(position.volume, 600)

            api.cancel_order(order2)
            api.wait_update()
            self.assertEqual(order2.volume_orign, 200)
            self.assertEqual(order2.volume_left, 200)
            self.assertEqual(order2.status, "FINISHED")
            self.assertEqual(position.volume, 600)

            while datetime.datetime.strptime(quote.datetime, "%Y-%m-%d %H:%M:%S.%f") < datetime.datetime(2021, 7, 15,
                                                                                                         10, 30):
                api.wait_update()
            order3 = api.insert_order("SSE.603666", direction="BUY", volume=200, limit_price=quote.ask_price1)
            api.wait_update()
            print("order3", "=" * 100)
            self.assertEqual(order3.volume_orign, 200)
            self.assertEqual(order3.volume_left, 0)
            self.assertEqual(order3.status, "FINISHED")
            self.assertEqual(position.volume, 800)

            order4 = api.insert_order("SSE.603666", direction="SELL", volume=800)
            api.wait_update()
            print("order4", "=" * 100)
            self.assertEqual(order4.volume_orign, 800)
            self.assertEqual(order4.volume_left, 800)
            self.assertEqual(order4.status, "FINISHED")
            self.assertEqual(position.volume, 800)

            order5 = api.insert_order("SSE.603666", direction="SELL", volume=200)
            api.wait_update()
            print("order5", "=" * 100)
            self.assertEqual(order5.volume_orign, 200)
            self.assertEqual(order5.volume_left, 0)
            self.assertEqual(order5.status, "FINISHED")
            self.assertEqual(position.volume, 600)

            while datetime.datetime.strptime(quote.datetime, "%Y-%m-%d %H:%M:%S.%f") < datetime.datetime(2021, 7, 16, 9,
                                                                                                         30):
                api.wait_update()
            print("after settle", "=" * 100)
            self.assertEqual(account.dividend_balance_today, 222.0)
            self.assertEqual(account.available_his, 9945234.19)
            self.assertEqual(account.available, 9945678.19)
            self.assertEqual(position.volume, 840)
            self.assertEqual(position.shared_volume_today, 240.0)
            self.assertEqual(position.devidend_balance_today, 222.0)

            order6 = api.insert_order("SSE.603666", direction="BUY", volume=200)
            api.wait_update()
            print("order6", "=" * 100)
            self.assertEqual(order6.volume_orign, 200)
            self.assertEqual(order6.volume_left, 0)
            self.assertEqual(order6.status, "FINISHED")
            self.assertEqual(position.volume, 1040)

            while datetime.datetime.strptime(quote.datetime, "%Y-%m-%d %H:%M:%S.%f") < datetime.datetime(2021, 7, 19,
                                                                                                         10, 30):
                api.wait_update()
            order7 = api.insert_order("SSE.603666", direction="BUY", volume=200)
            api.wait_update()
            print("order7", "=" * 100)
            self.assertEqual(order7.volume_orign, 200)
            self.assertEqual(order7.volume_left, 0)
            self.assertEqual(order7.status, "FINISHED")
            self.assertEqual(position.volume, 1240)

            while datetime.datetime.strptime(quote.datetime, "%Y-%m-%d %H:%M:%S.%f") < datetime.datetime(2021, 7, 20,
                                                                                                         10, 30):
                api.wait_update()
            order8 = api.insert_order("SSE.603666", direction="SELL", volume=600)
            api.wait_update()
            print("order8", "=" * 100)
            self.assertEqual(order8.volume_orign, 600)
            self.assertEqual(order8.volume_left, 0)
            self.assertEqual(order8.status, "FINISHED")
            self.assertEqual(position.volume, 640)

            while True:
                api.wait_update()
        except BacktestFinished:
            api.close()
            print(account)
            print(position)

