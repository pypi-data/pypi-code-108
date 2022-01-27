#!usr/bin/env python3
#-*- coding:utf-8 -*-
"""
@author: yanqiong
@file: test_td_trade.py
@create_on: 2020/6/12
@description: 
"""
import os
import random


from tqsdk import TqApi, TqAccount, utils
from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk.test.test_chan_helper import set_test_script


class TestTdTrade(TQBaseTestcase):
    """
    实盘账户下，insert_order 各种情况测试
    """

    def setUp(self):
        super(TestTdTrade, self).setUp()

    def tearDown(self):
        super(TestTdTrade, self).tearDown()

    def test_risk_rule(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "ws://106.15.80.213:37480/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_risk.script.lzma"))
        # 测试
        account = TqAccount("N南华期货_ETF", "90101636", "nh123456")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _td_url=td_url, _md_url=md_url) as api:
            options = api.query_options("SSE.510300", "CALL", 2021, 12, expired=False)
            symbol = options[0]
            quote = api.get_quote(symbol)
            api.set_risk_management_rule("SSE", True)
            risk_data = api.get_risk_management_data(symbol=symbol)
            print(risk_data)
            # 该合约没有 risk_data，从未下过单
            self.assertEqual(risk_data.user_id, "")
            self.assertEqual(risk_data.exchange_id, "")
            self.assertEqual(risk_data.instrument_id, "")
            self.assertNotEqual(risk_data.self_trade.highest_buy_price, risk_data.self_trade.highest_buy_price)
            self.assertNotEqual(risk_data.self_trade.lowest_sell_price, risk_data.self_trade.lowest_sell_price)
            self.assertEqual(risk_data.self_trade.self_trade_count, 0)
            self.assertEqual(risk_data.self_trade.rejected_count, 0)
            self.assertEqual(risk_data.frequent_cancellation.insert_order_count, 0)
            self.assertEqual(risk_data.frequent_cancellation.cancel_order_count, 0)
            self.assertNotEqual(risk_data.frequent_cancellation.cancel_order_percent, risk_data.frequent_cancellation.cancel_order_percent)
            self.assertEqual(risk_data.frequent_cancellation.rejected_count, 0)
            self.assertEqual(risk_data.trade_position_ratio.trade_units, 0)
            self.assertEqual(risk_data.trade_position_ratio.net_position_units, 0)
            self.assertNotEqual(risk_data.trade_position_ratio.trade_position_ratio, risk_data.trade_position_ratio.trade_position_ratio)
            self.assertEqual(risk_data.trade_position_ratio.rejected_count, 0)

            order = api.insert_order(symbol=symbol, direction="BUY", offset="OPEN", limit_price=quote.ask_price1, volume=2, order_id="PYSDK_insert_risk")
            while True:
                api.wait_update()
                if order.status == "FINISHED":
                    break
            print(risk_data)
            self.assertEqual(risk_data.user_id, "90101636")
            self.assertEqual(risk_data.exchange_id, "SSE")
            self.assertEqual(risk_data.instrument_id, "10003411")
            self.assertNotEqual(risk_data.self_trade.highest_buy_price, risk_data.self_trade.highest_buy_price)
            self.assertNotEqual(risk_data.self_trade.lowest_sell_price, risk_data.self_trade.lowest_sell_price)
            self.assertEqual(risk_data.self_trade.self_trade_count, 0)
            self.assertEqual(risk_data.self_trade.rejected_count, 0)
            self.assertEqual(risk_data.frequent_cancellation.insert_order_count, 1)
            self.assertEqual(risk_data.frequent_cancellation.cancel_order_count, 0)
            self.assertEqual(risk_data.frequent_cancellation.cancel_order_percent, 0)
            self.assertEqual(risk_data.frequent_cancellation.rejected_count, 0)
            self.assertEqual(risk_data.trade_position_ratio.trade_units, 0)
            self.assertEqual(risk_data.trade_position_ratio.net_position_units, 0)
            self.assertNotEqual(risk_data.trade_position_ratio.trade_position_ratio, risk_data.trade_position_ratio.trade_position_ratio)
            self.assertEqual(risk_data.trade_position_ratio.rejected_count, 0)
