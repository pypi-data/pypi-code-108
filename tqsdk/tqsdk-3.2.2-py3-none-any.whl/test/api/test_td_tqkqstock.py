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


from tqsdk import TqApi, TqAccount, utils, TqKqStock
from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk.test.test_chan_helper import set_test_script


class TestTdStockTrade(TQBaseTestcase):
    """
    快期股票模拟，insert_order 测试
    """

    def setUp(self):
        super(TestTdStockTrade, self).setUp()

    def tearDown(self):
        super(TestTdStockTrade, self).tearDown()

    def test_insert_order_tqkqstock_any(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "ws://otg-sim-securities.shinnytech.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_tqkqstock_any.script.lzma"))
        # 测试
        utils.RD = random.Random(4)
        acc = TqKqStock(td_url=td_url)
        api = TqApi(account=acc, auth="tianqin,tianqin", _md_url=md_url)
        order = api.insert_order("SSE.688529", volume=200, direction="BUY")  # 市价单
        while order.status == 'ALIVE':
            api.wait_update()
            print(order)
        self.assertEqual(
            {'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625-sim-securities', 'order_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231', 'exchange_order_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231', 'exchange_id': 'SSE', 'instrument_id': '688529', 'direction': 'BUY', 'volume_orign': 200, 'volume_left': 0, 'price_type': 'ANY', 'limit_price': 30.98, 'frozen_fee': 5.0, 'insert_date_time': 1636695304272475203, 'status': 'FINISHED', 'last_msg': '', 'seqno': 2, 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 30.98},
            order
        )
        account = api.get_account(acc)
        self.assertEqual(
            "{'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625-sim-securities', 'currency': 'CNY', 'market_value': 6196.0, 'asset': 999995.0, 'asset_his': 0.0, 'available': 993799.0, 'available_his': 0.0, 'cost': 6201.0, 'drawable': 993799.0, 'deposit': 1000000.0, 'withdraw': 0.0, 'buy_frozen_balance': 0.0, 'buy_frozen_fee': 0.0, 'buy_balance_today': 6196.0, 'buy_fee_today': 5.0, 'sell_balance_today': 0.0, 'sell_fee_today': 0.0, 'hold_profit': -5.0, 'float_profit_today': -4.999999999999716, 'real_profit_today': 0.0, 'profit_today': -4.999999999999716, 'profit_rate_today': -0.0008063215610384963, 'dividend_balance_today': 0.0}",
            str(account)
        )
        pos = api.get_position("SSE.688529")
        self.assertEqual(
            "{'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625-sim-securities', 'exchange_id': 'SSE', 'instrument_id': '688529', 'create_date': '20211112', 'cost': 6201.0, 'cost_his': 0.0, 'volume': 200, 'volume_his': 0, 'last_price': 30.98, 'buy_volume_today': 200, 'buy_balance_today': 6196.0, 'buy_fee_today': 5.0, 'sell_volume_today': 0, 'sell_balance_today': 0.0, 'sell_fee_today': 0.0, 'buy_volume_his': 0, 'buy_balance_his': 0.0, 'buy_fee_his': 0.0, 'sell_volume_his': 0, 'sell_balance_his': 0.0, 'sell_fee_his': 0.0, 'shared_volume_today': 0, 'devidend_balance_today': 0.0, 'market_value': 6196.0, 'market_value_his': 0.0, 'float_profit_today': -4.999999999999716, 'real_profit_today': 0.0, 'real_profit_his': nan, 'profit_today': -4.999999999999716, 'profit_rate_today': -0.0008063215610384963, 'hold_profit': -5.0, 'real_profit_total': 0.0, 'profit_total': -5.0, 'profit_rate_total': -0.0008063215610385422, 'real_profit_total_his': 0.0}",
            str(pos)
        )
        self.assertEqual(
            "{'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625-sim-securities', 'trade_id': '4fbae481aed641e2acbbcf72696f45bd', 'exchange_id': 'SSE', 'instrument_id': '688529', 'order_id': 'PYSDK_insert_8ca5996666ceab360512bd1311072231', 'exchange_order_id': '', 'direction': 'BUY', 'volume': 200, 'price': 30.98, 'balance': 6196.0, 'fee': 5.0, 'trade_date_time': 1636695304272619932, 'seqno': 1, 'exchange_trade_id': '4fbae481aed641e2acbbcf72696f45bd'}",
            str(order.trade_records['4fbae481aed641e2acbbcf72696f45bd'])
        )
        api.close()

    def test_insert_order_tqkqstock_limit(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "ws://otg-sim-securities.shinnytech.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_tqkqstock_limit.script.lzma"))
        # 测试
        utils.RD = random.Random(4)
        acc = TqKqStock(td_url=td_url)
        api = TqApi(account=acc, auth="tianqin,tianqin", _md_url=md_url)

        quote = api.get_quote("SSE.688529")
        order = api.insert_order("SSE.688529", volume=200, direction="BUY", limit_price=quote.ask_price1)
        while order.status == 'ALIVE':
            api.wait_update()
        self.assertEqual(
            "{'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625-sim-securities', 'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_id': 'SSE', 'instrument_id': '688529', 'direction': 'BUY', 'volume_orign': 200, 'volume_left': 0, 'price_type': 'LIMIT', 'limit_price': 31.03, 'frozen_fee': 5.0, 'insert_date_time': 1636695427475108871, 'status': 'FINISHED', 'last_msg': '', 'seqno': 4, 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 31.03}",
            str(order)
        )

        order = api.insert_order("SSE.688529", volume=200, direction="BUY", limit_price=quote.bid_price2)
        api.wait_update()
        self.assertEqual(
            "{'user_id': '', 'order_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258', 'exchange_order_id': '', 'exchange_id': 'SSE', 'instrument_id': '688529', 'direction': 'BUY', 'volume_orign': 200, 'volume_left': 200, 'price_type': 'LIMIT', 'limit_price': 30.98, 'frozen_fee': nan, 'insert_date_time': 0, 'status': 'ALIVE', 'last_msg': ''}",
            str(order)
        )
        api.cancel_order(order)
        self.assertEqual(
            "{'user_id': '', 'order_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258', 'exchange_order_id': '', 'exchange_id': 'SSE', 'instrument_id': '688529', 'direction': 'BUY', 'volume_orign': 200, 'volume_left': 200, 'price_type': 'LIMIT', 'limit_price': 30.98, 'frozen_fee': nan, 'insert_date_time': 0, 'status': 'ALIVE', 'last_msg': ''}",
            str(order)
        )
        while order.status == 'ALIVE':
            api.wait_update()
        self.assertEqual(
            "{'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625-sim-securities', 'order_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258', 'exchange_order_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258', 'exchange_id': 'SSE', 'instrument_id': '688529', 'direction': 'BUY', 'volume_orign': 200, 'volume_left': 200, 'price_type': 'LIMIT', 'limit_price': 30.98, 'frozen_fee': 5.0, 'insert_date_time': 1636695427503733214, 'status': 'FINISHED', 'last_msg': '', 'seqno': 5, 'is_dead': True, 'is_online': False, 'is_error': False}",
            str(order)
        )

        self.assertEqual(
            "{'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625-sim-securities', 'currency': 'CNY', 'market_value': 12400.0, 'asset': 999988.0, 'asset_his': 0.0, 'available': 987588.0, 'available_his': 0.0, 'cost': 12412.0, 'drawable': 987588.0, 'deposit': 1000000.0, 'withdraw': 0.0, 'buy_frozen_balance': 0.0, 'buy_frozen_fee': 0.0, 'buy_balance_today': 12402.0, 'buy_fee_today': 10.0, 'sell_balance_today': 0.0, 'sell_fee_today': 0.0, 'hold_profit': -12.0, 'float_profit_today': -12.000000000000455, 'real_profit_today': 0.0, 'profit_today': -12.000000000000455, 'profit_rate_today': -0.0009668063164679709, 'dividend_balance_today': 0.0}",
            str(api.get_account(acc))
        )
        self.assertEqual(
            "{'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625-sim-securities', 'exchange_id': 'SSE', 'instrument_id': '688529', 'create_date': '20211112', 'cost': 12412.0, 'cost_his': 0.0, 'volume': 400, 'volume_his': 0, 'last_price': 31.0, 'buy_volume_today': 400, 'buy_balance_today': 12402.0, 'buy_fee_today': 10.0, 'sell_volume_today': 0, 'sell_balance_today': 0.0, 'sell_fee_today': 0.0, 'buy_volume_his': 0, 'buy_balance_his': 0.0, 'buy_fee_his': 0.0, 'sell_volume_his': 0, 'sell_balance_his': 0.0, 'sell_fee_his': 0.0, 'shared_volume_today': 0, 'devidend_balance_today': 0.0, 'market_value': 12400.0, 'market_value_his': 0.0, 'float_profit_today': -12.000000000000455, 'real_profit_today': 0.0, 'real_profit_his': nan, 'profit_today': -12.000000000000455, 'profit_rate_today': -0.0009668063164679709, 'hold_profit': -12.0, 'real_profit_total': 0.0, 'profit_total': -12.0, 'profit_rate_total': -0.0009668063164679343, 'real_profit_total_his': 0.0}",
            str(api.get_position("SSE.688529"))
        )
        api.close()
