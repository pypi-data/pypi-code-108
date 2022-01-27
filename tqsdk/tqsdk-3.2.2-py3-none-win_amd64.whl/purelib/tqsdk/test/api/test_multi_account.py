#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import random
import unittest

import pytest

from tqsdk import TqApi, TqAccount, TqSim, TqKq, utils, TqChan
from tqsdk import TqMultiAccount, TargetPosTask
from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk.test.test_chan_helper import set_test_script


class TestMultiAccount(TQBaseTestcase):
    """
    simnow 不可用，使用 TqKq 和 TqSim 测试多账户，下次录脚本可以换回 simnow 代替实盘账户
    """
    def setUp(self):
        super(TestMultiAccount, self).setUp()

    def tearDown(self):
        super(TestMultiAccount, self).tearDown()

    def test_one_account_insert_order(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://otg-sim.shinnytech.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_with_multi_account_tqkq1.script.lzma"))
        account1 = TqAccount("快期模拟", "147716", "123456", td_url=td_url)
        account_list = TqMultiAccount([account1])
        utils.RD = random.Random(4)
        api = TqApi(account=account_list, auth="tianqin,tianqin", _md_url=md_url)
        # 下单
        order1 = api.insert_order(symbol="DCE.m2201", direction="BUY", offset="OPEN", volume=5, limit_price=3549, account=account1, order_id="test_multi_6")
        while order1.status != "FINISHED":
            api.wait_update()
        api.close()


    """
    多账户测试场景一: 同时登陆3个实盘账户(TqAccount × 3)
    分别进行登录、下单和撤单操作, 预期持仓、资金、委托和成交数据符合预期
    """
    def test_multi_account_insert_order(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://otg-sim.shinnytech.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_with_multi_account_tqkq3.script.lzma"))
        account1 = TqAccount("快期模拟", "147716", "123456", td_url=td_url)
        account2 = TqAccount("快期模拟", "172289", "123456", td_url=td_url)
        account3 = TqAccount("快期模拟", "103988", "123456", td_url=td_url)
        account_list = TqMultiAccount([account1, account2, account3])
        utils.RD = random.Random(4)
        api = TqApi(account=account_list, auth="tianqin,tianqin", _md_url=md_url)

        # 下单
        order1 = api.insert_order(symbol="DCE.m2201", direction="BUY", offset="OPEN", volume=5, limit_price=3549,
                                  account=account1, order_id="test_multi_3_1_1")
        order2 = api.insert_order(symbol="DCE.m2201", direction="BUY", offset="OPEN", volume=10, limit_price=3540,
                                  account=account2, order_id="test_multi_3_2_1")
        order3 = api.insert_order(symbol="DCE.m2209", direction="BUY", offset="OPEN", volume=15, limit_price=3250,
                                  account=account1, order_id="test_multi_3_1_2")
        order4 = api.insert_order(symbol="DCE.m2209", direction="BUY", offset="OPEN", volume=20, limit_price=3240,
                                  account=account2, order_id="test_multi_3_2_2")
        api.cancel_order(order3, account=account1)
        api.cancel_order(order4, account=account2)
        while order1.status != "FINISHED" or order2.status != "FINISHED" or order3.status != "FINISHED" or order4.status != "FINISHED":
            api.wait_update()

        # 查询资产
        act1 = api.get_account(account1)
        act2 = api.get_account(account2)
        act3 = api.get_account(account3)
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 994506.11, 'static_balance': 994506.11, 'balance': 989103.61, 'available': 489213.61, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -5395.0, 'position_profit': -5395.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 499890.0, 'frozen_commission': 0.0, 'commission': 7.5, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.5053970028478614, 'market_value': 0.0, 'user_id': '147716'}",
            str(act1)
        )
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 1076733.015, 'static_balance': 1076733.015, 'balance': 1080268.015, 'available': 195029.0149999999, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': 3550.0, 'position_profit': 3550.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 885239.0, 'frozen_commission': 0.0, 'commission': 15.0, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.8194623812869254, 'market_value': 0.0, 'user_id': '172289'}",
            str(act2)
        )
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 995858.1495000002, 'static_balance': 995858.1495000002, 'balance': 997008.1495000002, 'available': 912971.2495000002, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': 1150.0, 'position_profit': 1150.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 84036.9, 'frozen_commission': 0.0, 'commission': 0.0, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.08428908032712122, 'market_value': 0.0, 'user_id': '103988'}",
            str(act3)
        )
        # 查询持仓
        pos1 = api.get_position("DCE.m2201", account=account1)
        pos2 = api.get_position(account=account2)["DCE.m2201"]
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2201', 'pos_long_his': 22, 'pos_long_today': 5, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 27, 'volume_long_his': 0, 'volume_long': 27, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 3499.814814814815, 'open_price_short': nan, 'open_cost_long': 944950.0, 'open_cost_short': nan, 'position_price_long': 3499.814814814815, 'position_price_short': nan, 'position_cost_long': 944950.0, 'position_cost_short': nan, 'float_profit_long': -4270.0, 'float_profit_short': nan, 'float_profit': -4270.0, 'position_profit_long': -4270.0, 'position_profit_short': nan, 'position_profit': -4270.0, 'margin_long': 47493.0, 'margin_short': nan, 'margin': 47493.0, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'pos': 27, 'pos_long': 27, 'pos_short': 0, 'user_id': '147716', 'volume_long_yd': 22, 'volume_short_yd': 0, 'last_price': 3484.0}",
            str(pos1)
        )
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2201', 'pos_long_his': 90, 'pos_long_today': 10, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 100, 'volume_long_his': 0, 'volume_long': 100, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 3504.3, 'open_price_short': nan, 'open_cost_long': 3504300.0, 'open_cost_short': nan, 'position_price_long': 3504.3, 'position_price_short': nan, 'position_cost_long': 3504300.0, 'position_cost_short': nan, 'float_profit_long': -20300.0, 'float_profit_short': nan, 'float_profit': -20300.0, 'position_profit_long': -20300.0, 'position_profit_short': nan, 'position_profit': -20300.0, 'margin_long': 175900.0, 'margin_short': nan, 'margin': 175900.0, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'pos': 100, 'pos_long': 100, 'pos_short': 0, 'user_id': '172289', 'volume_long_yd': 90, 'volume_short_yd': 0, 'last_price': 3484.0}",
            str(pos2)
        )
        # 查询委托
        ord1 = api.get_order(order_id=order1.order_id, account=account1)
        ord2 = api.get_order(account=account2)['test_multi_3_2_1']
        self.assertEqual(
            "{'order_id': 'test_multi_3_1_1', 'exchange_order_id': 'test_multi_3_1_1', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 5, 'volume_left': 0, 'limit_price': 3549.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1632840974079340791, 'last_msg': '', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 3485.0, 'seqno': 3, 'user_id': '147716', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(ord1)
        )
        self.assertEqual(
            "{'order_id': 'test_multi_3_2_1', 'exchange_order_id': 'test_multi_3_2_1', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 10, 'volume_left': 0, 'limit_price': 3540.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1632840974078454853, 'last_msg': '', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 3485.0, 'seqno': 3, 'user_id': '172289', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(ord2)
        )

        # 撤单结果校验
        self.assertEqual(
            "{'order_id': 'test_multi_3_1_2', 'exchange_order_id': 'test_multi_3_1_2', 'exchange_id': 'DCE', 'instrument_id': 'm2209', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 15, 'volume_left': 15, 'limit_price': 3250.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1632840974096539180, 'last_msg': '', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': nan, 'seqno': 6, 'user_id': '147716', 'frozen_margin': 26385.0, 'frozen_premium': 0.0, 'frozen_commission': 22.5}",
            str(order3)
        )
        self.assertEqual(
            "{'order_id': 'test_multi_3_2_2', 'exchange_order_id': 'test_multi_3_2_2', 'exchange_id': 'DCE', 'instrument_id': 'm2209', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 20, 'volume_left': 20, 'limit_price': 3240.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1632840974095823322, 'last_msg': '', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': nan, 'seqno': 6, 'user_id': '172289', 'frozen_margin': 35180.0, 'frozen_premium': 0.0, 'frozen_commission': 30.0}",
            str(order4)
        )

        # 查询成交
        trd1 = api.get_trade(account=account1)['11c6bdc683ef4e0bab7388b0679316cc']
        trd2 = api.get_trade(account=account2)['0b32cdeeab1a4a4fa50ea2a78a3cabad']
        self.assertEqual(
            "{'order_id': 'test_multi_3_1_1', 'trade_id': '11c6bdc683ef4e0bab7388b0679316cc', 'exchange_trade_id': '11c6bdc683ef4e0bab7388b0679316cc', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'BUY', 'offset': 'OPEN', 'price': 3485.0, 'volume': 5, 'trade_date_time': 1632840974079419678, 'seqno': 1, 'user_id': '147716', 'commission': 7.5}",
            str(trd1)
        )
        self.assertEqual(
            "{'order_id': 'test_multi_3_2_1', 'trade_id': '0b32cdeeab1a4a4fa50ea2a78a3cabad', 'exchange_trade_id': '0b32cdeeab1a4a4fa50ea2a78a3cabad', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'BUY', 'offset': 'OPEN', 'price': 3485.0, 'volume': 10, 'trade_date_time': 1632840974078537448, 'seqno': 1, 'user_id': '172289', 'commission': 15.0}",
            str(trd2)
        )
        api.close()

    """
    多账户测试场景二: 同时登录 TqAccount + TqSim + TqKq 
    分别进行登录、下单和撤单操作, 预期持仓、资金、委托和成交数据符合预期
    """
    def test_multi_account_with_diff_type_account(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://otg-sim.shinnytech.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_multi_account_with_diff_type_account.script.lzma"))

        # 测试
        account1 = TqAccount("快期模拟", "103988", "123456", td_url=td_url)
        account2 = TqSim(account_id="sim1")
        account3 = TqKq(td_url=td_url)
        account_list = TqMultiAccount([account1, account2, account3])
        # 测试
        utils.RD = random.Random(8)
        api = TqApi(account=account_list, _md_url=md_url, auth="tianqin,tianqin")
        # 下单
        order1 = api.insert_order(symbol="SHFE.cu2111", direction="BUY", offset="OPEN", volume=1, limit_price=69300,
                                  account=account1)
        order2 = api.insert_order(symbol="SHFE.cu2111", direction="BUY", offset="OPEN", volume=10, limit_price=69250,
                                  account=account2)
        order3 = api.insert_order(symbol="DCE.c2201", direction="BUY", offset="OPEN", volume=10, account=account3)
        order4 = api.insert_order(symbol="DCE.i2201", direction="BUY", offset="OPEN", volume=15, limit_price=660,
                                  account=account1)
        order5 = api.insert_order(symbol="DCE.i2201", direction="BUY", offset="OPEN", volume=20, limit_price=662,
                                  account=account2)
        api.cancel_order(order4, account=account1)
        api.cancel_order(order5, account=account2)
        while order1.status != "FINISHED" or order2.status != "FINISHED" or order3.status != "FINISHED" or order4.status != "FINISHED" or order5.status != "FINISHED":
            api.wait_update()
        # 查询委托
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_6694f229359b154881a0d5b3ffc6e35c', 'exchange_order_id': 'PYSDK_insert_6694f229359b154881a0d5b3ffc6e35c', 'exchange_id': 'SHFE', 'instrument_id': 'cu2111', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 1, 'volume_left': 0, 'limit_price': 69300.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1632841004344431972, 'last_msg': '', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 68660.0, 'seqno': 3, 'user_id': '103988', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(order1)
        )
        self.assertAlmostEqual(1632841003509611000 / 1e9, order2['insert_date_time'] / 1e9, places=0)
        del order2['insert_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_92b850ad7eb72f8263f65da874007cb4', 'exchange_order_id': 'PYSDK_insert_92b850ad7eb72f8263f65da874007cb4', 'exchange_id': 'SHFE', 'instrument_id': 'cu2111', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 10, 'volume_left': 0, 'limit_price': 69250.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 69250.0, 'user_id': 'sim1', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order2)
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_67164890d49d0ac1e5b8063831360a40', 'exchange_order_id': 'PYSDK_insert_67164890d49d0ac1e5b8063831360a40', 'exchange_id': 'DCE', 'instrument_id': 'c2201', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 10, 'volume_left': 0, 'limit_price': 0.0, 'price_type': 'ANY', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'insert_date_time': 1632841004368435578, 'last_msg': '', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 2477.0, 'seqno': 3, 'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(order3)
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_852a5fba444adf42b37f5722051e2670', 'exchange_order_id': 'PYSDK_insert_852a5fba444adf42b37f5722051e2670', 'exchange_id': 'DCE', 'instrument_id': 'i2201', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 15, 'volume_left': 15, 'limit_price': 660.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1632841004386554064, 'last_msg': '', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': nan, 'seqno': 6, 'user_id': '103988', 'frozen_margin': 81540.0, 'frozen_premium': 0.0, 'frozen_commission': 101.925}",
            str(order4)
        )
        self.assertAlmostEqual(1632841003794509000 / 1e9, order5['insert_date_time'] / 1e9, places=0)
        del order5['insert_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_a9b7e3ea1d1d784fb9db434b610b1631', 'exchange_order_id': 'PYSDK_insert_a9b7e3ea1d1d784fb9db434b610b1631', 'exchange_id': 'DCE', 'instrument_id': 'i2201', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 20, 'volume_left': 20, 'limit_price': 662.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '已撤单', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': nan, 'user_id': 'sim1', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order5)
        )

        # 查询持仓
        pos1 = api.get_position("SHFE.cu2111", account=account1)
        pos2 = api.get_position("DCE.i2201", account=account1)
        self.assertEqual(
            "{'exchange_id': 'SHFE', 'instrument_id': 'cu2111', 'pos_long_his': 1, 'pos_long_today': 1, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 1, 'volume_long_his': 1, 'volume_long': 2, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 68910.0, 'open_price_short': nan, 'open_cost_long': 689100.0, 'open_cost_short': nan, 'position_price_long': 68910.0, 'position_price_short': nan, 'position_cost_long': 689100.0, 'position_cost_short': nan, 'float_profit_long': -2600.0, 'float_profit_short': nan, 'float_profit': -2600.0, 'position_profit_long': -2600.0, 'position_profit_short': nan, 'position_profit': -2600.0, 'margin_long': 62315.99999999999, 'margin_short': nan, 'margin': 62315.99999999999, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'pos': 2, 'pos_long': 2, 'pos_short': 0, 'user_id': '103988', 'volume_long_yd': 1, 'volume_short_yd': 0, 'last_price': 68650.0}",
            str(pos1)
        )
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'i2201', 'pos_long_his': 0, 'pos_long_today': 0, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': nan, 'open_price_short': nan, 'open_cost_long': nan, 'open_cost_short': nan, 'position_price_long': nan, 'position_price_short': nan, 'position_cost_long': nan, 'position_cost_short': nan, 'float_profit_long': nan, 'float_profit_short': nan, 'float_profit': nan, 'position_profit_long': nan, 'position_profit_short': nan, 'position_profit': nan, 'margin_long': nan, 'margin_short': nan, 'margin': nan, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'pos': 0, 'pos_long': 0, 'pos_short': 0, 'user_id': '103988', 'volume_long_yd': 0, 'volume_short_yd': 0, 'last_price': 686.5}",
            str(pos2)
        )

        sim_pos1 = api.get_position("SHFE.cu2111", account=account2)
        sim_pos2 = api.get_position("DCE.i2201", account=account2)
        self.assertEqual(
            "{'exchange_id': 'SHFE', 'instrument_id': 'cu2111', 'pos_long_his': 0, 'pos_long_today': 10, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 10, 'volume_long_his': 0, 'volume_long': 10, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 69250.0, 'open_price_short': nan, 'open_cost_long': 3462500.0, 'open_cost_short': 0.0, 'position_price_long': 69250.0, 'position_price_short': nan, 'position_cost_long': 3462500.0, 'position_cost_short': 0.0, 'float_profit_long': -30000.0, 'float_profit_short': 0.0, 'float_profit': -30000.0, 'position_profit_long': -30000.0, 'position_profit_short': 0.0, 'position_profit': -30000.0, 'margin_long': 311580.0, 'margin_short': 0.0, 'margin': 311580.0, 'market_value_long': 0.0, 'market_value_short': 0.0, 'market_value': 0.0, 'pos': 10, 'pos_long': 10, 'pos_short': 0, 'last_price': 68650.0, 'underlying_last_price': nan, 'future_margin': 31158.0}",
            str(sim_pos1)
        )
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'i2201', 'pos_long_his': 0, 'pos_long_today': 0, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': nan, 'open_price_short': nan, 'open_cost_long': nan, 'open_cost_short': nan, 'position_price_long': nan, 'position_price_short': nan, 'position_cost_long': nan, 'position_cost_short': nan, 'float_profit_long': nan, 'float_profit_short': nan, 'float_profit': nan, 'position_profit_long': nan, 'position_profit_short': nan, 'position_profit': nan, 'margin_long': nan, 'margin_short': nan, 'margin': nan, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'pos': 0, 'pos_long': 0, 'pos_short': 0}",
            str(sim_pos2)
        )

        pos3 = api.get_position("DCE.c2201", account=account3)
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'c2201', 'pos_long_his': 10, 'pos_long_today': 10, 'pos_short_his': 4, 'pos_short_today': 0, 'volume_long_today': 20, 'volume_long_his': 0, 'volume_long': 20, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 4, 'volume_short_his': 0, 'volume_short': 4, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 2474.0, 'open_price_short': 2464.0, 'open_cost_long': 494800.0, 'open_cost_short': 98560.0, 'position_price_long': 2474.0, 'position_price_short': 2464.0, 'position_cost_long': 494800.0, 'position_cost_short': 98560.0, 'float_profit_long': 600.0, 'float_profit_short': -520.0, 'float_profit': 80.0, 'position_profit_long': 600.0, 'position_profit_short': -520.0, 'position_profit': 80.0, 'margin_long': 24800.0, 'margin_short': 4960.0, 'margin': 29760.0, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'pos': 16, 'pos_long': 20, 'pos_short': 4, 'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625', 'volume_long_yd': 10, 'volume_short_yd': 4, 'last_price': 2477.0}",
            str(pos3)
        )

        # 查询成交
        trd1 = api.get_trade(account=account1)
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_6694f229359b154881a0d5b3ffc6e35c', 'trade_id': 'bca45536c24f4cee860aa7309537c77a', 'exchange_trade_id': 'bca45536c24f4cee860aa7309537c77a', 'exchange_id': 'SHFE', 'instrument_id': 'cu2111', 'direction': 'BUY', 'offset': 'OPEN', 'price': 68660.0, 'volume': 1, 'trade_date_time': 1632841004344516208, 'seqno': 1, 'user_id': '103988', 'commission': 17.310000000000002}",
            str(trd1['bca45536c24f4cee860aa7309537c77a'])
        )
        trd1.pop('bca45536c24f4cee860aa7309537c77a')

        trd2 = api.get_trade(account=account2)['PYSDK_insert_92b850ad7eb72f8263f65da874007cb4|10']
        self.assertAlmostEqual(1632841003510141000/1e9, trd2['trade_date_time']/1e9, places=0)
        del trd2['trade_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_92b850ad7eb72f8263f65da874007cb4', 'trade_id': 'PYSDK_insert_92b850ad7eb72f8263f65da874007cb4|10', 'exchange_trade_id': 'PYSDK_insert_92b850ad7eb72f8263f65da874007cb4|10', 'exchange_id': 'SHFE', 'instrument_id': 'cu2111', 'direction': 'BUY', 'offset': 'OPEN', 'price': 69250.0, 'volume': 10, 'user_id': 'sim1', 'commission': 173.1}",
            str(trd2)
        )

        trd3 = api.get_trade(account=account3)
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_67164890d49d0ac1e5b8063831360a40', 'trade_id': '61a4f85338fd4455ad1d174f52e07340', 'exchange_trade_id': '61a4f85338fd4455ad1d174f52e07340', 'exchange_id': 'DCE', 'instrument_id': 'c2201', 'direction': 'BUY', 'offset': 'OPEN', 'price': 2477.0, 'volume': 10, 'trade_date_time': 1632841004368526027, 'seqno': 1, 'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625', 'commission': 12.0}",
            str(trd3['61a4f85338fd4455ad1d174f52e07340'])
        )
        api.close()

    """
    多账户测试场景三: 同时登录模拟账户 TqSim × 3
    分别进行登录、下单和撤单操作, 预期持仓、资金、委托和成交数据符合预期
    """
    def test_multi_account_with_3_tqsim(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://otg-sim.shinnytech.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_multi_account_with_3_tqsim.script.lzma"))

        account1, account2, account3 = TqSim(account_id="sim1"), TqSim(account_id="sim2"), TqSim()
        account_list = TqMultiAccount([account1, account2, account3])
        # 测试
        utils.RD = random.Random(4)
        api = TqApi(account=account_list, _md_url=md_url, auth="tianqin,tianqin")
        # 下单
        order1 = api.insert_order(symbol="DCE.m2201", direction="BUY", offset="OPEN", volume=5, limit_price=3549,
                                  account=account1)
        order2 = api.insert_order(symbol="DCE.m2201", direction="BUY", offset="OPEN", volume=10, limit_price=3540,
                                  account=account2)
        order3 = api.insert_order(symbol="DCE.m2209", direction="BUY", offset="OPEN", volume=15, limit_price=3250,
                                  account=account3)
        order4 = api.insert_order(symbol="DCE.m2209", direction="BUY", offset="OPEN", volume=20, limit_price=3240,
                                  account=account2)
        api.cancel_order(order3, account=account3)
        api.cancel_order(order4, account=account2)

        while order1.status != "FINISHED" or order2.status != "FINISHED" or order3.status != "FINISHED" or order4.status != "FINISHED":
            api.wait_update()

        # 查询资产
        act1 = api.get_account(account1)
        act2 = api.get_account(account2)
        act3 = api.get_account(account3)
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 10000000.0, 'static_balance': 10000000.0, 'balance': 9996742.5, 'available': 9987947.5, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -3250.0, 'position_profit': -3250.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 8795.0, 'frozen_commission': 0.0, 'commission': 7.5, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0008797865904818494, 'market_value': 0.0}",
            str(act1)
        )
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 10000000.0, 'static_balance': 10000000.0, 'balance': 9994385.0, 'available': 9976795.0, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -5600.0, 'position_profit': -5600.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 17590.0, 'frozen_commission': 0.0, 'commission': 15.0, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0017599882333930502, 'market_value': 0.0}",
            str(act2)
        )
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 10000000.0, 'static_balance': 10000000.0, 'balance': 10000000.0, 'available': 10000000.0, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 0.0, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0, 'market_value': 0.0}",
            str(act3)
        )

        # 查询持仓
        pos1 = api.get_position("DCE.m2201", account=account1)
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2201', 'pos_long_his': 0, 'pos_long_today': 5, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 5, 'volume_long_his': 0, 'volume_long': 5, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 3549.0, 'open_price_short': nan, 'open_cost_long': 177450.0, 'open_cost_short': 0.0, 'position_price_long': 3549.0, 'position_price_short': nan, 'position_cost_long': 177450.0, 'position_cost_short': 0.0, 'float_profit_long': -3250.0, 'float_profit_short': 0.0, 'float_profit': -3250.0, 'position_profit_long': -3250.0, 'position_profit_short': 0.0, 'position_profit': -3250.0, 'margin_long': 8795.0, 'margin_short': 0.0, 'margin': 8795.0, 'market_value_long': 0.0, 'market_value_short': 0.0, 'market_value': 0.0, 'pos': 5, 'pos_long': 5, 'pos_short': 0, 'last_price': 3484.0, 'underlying_last_price': nan, 'future_margin': 1759.0}",
            str(pos1)
        )

        pos2_1 = api.get_position("DCE.m2201", account=account2)
        pos2_2 = api.get_position("DCE.m2209", account=account2)
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2201', 'pos_long_his': 0, 'pos_long_today': 10, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 10, 'volume_long_his': 0, 'volume_long': 10, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 3540.0, 'open_price_short': nan, 'open_cost_long': 354000.0, 'open_cost_short': 0.0, 'position_price_long': 3540.0, 'position_price_short': nan, 'position_cost_long': 354000.0, 'position_cost_short': 0.0, 'float_profit_long': -5600.0, 'float_profit_short': 0.0, 'float_profit': -5600.0, 'position_profit_long': -5600.0, 'position_profit_short': 0.0, 'position_profit': -5600.0, 'margin_long': 17590.0, 'margin_short': 0.0, 'margin': 17590.0, 'market_value_long': 0.0, 'market_value_short': 0.0, 'market_value': 0.0, 'pos': 10, 'pos_long': 10, 'pos_short': 0, 'last_price': 3484.0, 'underlying_last_price': nan, 'future_margin': 1759.0}",
            str(pos2_1)
        )
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2209', 'pos_long_his': 0, 'pos_long_today': 0, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': nan, 'open_price_short': nan, 'open_cost_long': nan, 'open_cost_short': nan, 'position_price_long': nan, 'position_price_short': nan, 'position_cost_long': nan, 'position_cost_short': nan, 'float_profit_long': nan, 'float_profit_short': nan, 'float_profit': nan, 'position_profit_long': nan, 'position_profit_short': nan, 'position_profit': nan, 'margin_long': nan, 'margin_short': nan, 'margin': nan, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'pos': 0, 'pos_long': 0, 'pos_short': 0}",
            str(pos2_2)
        )

        pos3 = api.get_position("DCE.m2209", account=account3)
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2209', 'pos_long_his': 0, 'pos_long_today': 0, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': nan, 'open_price_short': nan, 'open_cost_long': nan, 'open_cost_short': nan, 'position_price_long': nan, 'position_price_short': nan, 'position_cost_long': nan, 'position_cost_short': nan, 'float_profit_long': nan, 'float_profit_short': nan, 'float_profit': nan, 'position_profit_long': nan, 'position_profit_short': nan, 'position_profit': nan, 'margin_long': nan, 'margin_short': nan, 'margin': nan, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'pos': 0, 'pos_long': 0, 'pos_short': 0}",
            str(pos3)
        )

        # 查询委托
        self.assertAlmostEqual(1632841022779756000/1e9, order1['insert_date_time']/1e9, places=0)
        self.assertAlmostEqual(1632841022775295000/1e9, order2['insert_date_time']/1e9, places=0)
        self.assertAlmostEqual(1632841022857769000/1e9, order3['insert_date_time']/1e9, places=0)
        self.assertAlmostEqual(1632841022864010000/1e9, order4['insert_date_time']/1e9, places=0)
        del order1['insert_date_time']
        del order2['insert_date_time']
        del order3['insert_date_time']
        del order4['insert_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'exchange_order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 5, 'volume_left': 0, 'limit_price': 3549.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 3549.0, 'user_id': 'sim1', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order1)
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 10, 'volume_left': 0, 'limit_price': 3540.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 3540.0, 'user_id': 'sim2', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order2)
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258', 'exchange_order_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258', 'exchange_id': 'DCE', 'instrument_id': 'm2209', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 15, 'volume_left': 15, 'limit_price': 3250.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '已撤单', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': nan, 'user_id': 'TQSIM', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order3)
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_43000de01b2ed40ed3addccb2c33be0a', 'exchange_order_id': 'PYSDK_insert_43000de01b2ed40ed3addccb2c33be0a', 'exchange_id': 'DCE', 'instrument_id': 'm2209', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 20, 'volume_left': 20, 'limit_price': 3240.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '已撤单', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': nan, 'user_id': 'sim2', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order4)
        )

        # 查询成交
        trd1 = api.get_trade(account=account1)['PYSDK_insert_1710cf5327ac435a7a97c643656412a9|5']
        self.assertAlmostEqual(1632841022779892000/1e9, trd1['trade_date_time']/1e9, places=0)
        del trd1['trade_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|5', 'exchange_trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|5', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'BUY', 'offset': 'OPEN', 'price': 3549.0, 'volume': 5, 'user_id': 'sim1', 'commission': 7.5}",
            str(trd1)
        )

        trd2 = api.get_trade(account=account2)['PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|10']
        self.assertAlmostEqual(1632841022775686000/1e9, trd2['trade_date_time']/1e9, places=0)
        del trd2['trade_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|10', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|10', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'BUY', 'offset': 'OPEN', 'price': 3540.0, 'volume': 10, 'user_id': 'sim2', 'commission': 15.0}",
            str(trd2)
        )

        trd3 = api.get_trade(account=account3)
        self.assertEqual(trd3, {})  # 已撤单 没有成交
        api.close()

    """
    调仓测试
    账户1 DCE.m2105 多仓 40 手, 目标仓位 30 , 需要平仓 10 手多仓
    账户2 DCE.i2101 多仓 85 手, 目标仓位 80 , 需要平仓 5 手多仓
    账户3 SHFE.rb2012 多仓 2 手, 目标仓位 5 , 需要开仓 3 手多仓
    """
    def test_multi_account_with_lib(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://otg-sim.shinnytech.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_multi_account_with_lib.script.lzma"))

        account1 = TqAccount("快期模拟", "147716", "123456", td_url=td_url)
        account2 = TqAccount("快期模拟", "172289", "123456", td_url=td_url)
        account3 = TqAccount("快期模拟", "103988", "123456", td_url=td_url)
        account_list = TqMultiAccount([account1, account2, account3])

        utils.RD = random.Random(5)
        api = TqApi(account=account_list, auth="tianqin,tianqin", _md_url=md_url)
        symbol1 = "DCE.m2201"
        symbol2 = "DCE.i2201"
        symbol3 = "SHFE.rb2201"
        position1 = api.get_position(symbol1, account=account1)
        position2 = api.get_position(symbol2, account=account2)
        position3 = api.get_position(symbol3, account=account3)
        self.assertEqual(position1.pos, 32)
        self.assertEqual(position2.pos, 32)
        self.assertEqual(position3.pos, 12)
        target_pos1 = TargetPosTask(api, symbol1, account=account1)
        target_pos2 = TargetPosTask(api, symbol2, account=account2)
        target_pos3 = TargetPosTask(api, symbol3, account=account3)
        target_pos1.set_target_volume(22)
        target_pos2.set_target_volume(32)
        target_pos3.set_target_volume(12)
        while position1.volume_long != 22 or position2.volume_long != 32 or position3.volume_long != 12:
            api.wait_update()

        # 预期持仓数量
        self.assertEqual(position1.pos, 22)
        self.assertEqual(position2.pos, 32)
        self.assertEqual(position3.pos, 12)
        # 预期委托
        ord1 = api.get_order(account=account1)
        ord2 = api.get_order(account=account2)
        ord3 = api.get_order(account=account3)
        self.assertEqual(
            "{'order_id': 'PYSDK_target_3fd4235992edcf451a1afe878b33e968', 'exchange_order_id': 'PYSDK_target_3fd4235992edcf451a1afe878b33e968', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'SELL', 'offset': 'CLOSE', 'volume_orign': 10, 'volume_left': 0, 'limit_price': 3484.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1632841034991107055, 'last_msg': '', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 3484.0, 'seqno': 12, 'user_id': '147716', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(ord1['PYSDK_target_3fd4235992edcf451a1afe878b33e968'])
        )
        self.assertEqual(
            ['test_multi_3_2_1', 'test_multi_3_2_2'], list(ord2.keys())
        )
        self.assertEqual(
            ['PYSDK_insert_6694f229359b154881a0d5b3ffc6e35c', 'PYSDK_insert_852a5fba444adf42b37f5722051e2670'], list(ord3.keys())
        )
        api.close()
