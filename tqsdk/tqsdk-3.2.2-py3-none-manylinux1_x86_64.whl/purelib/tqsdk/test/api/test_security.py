#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import os
import random
import unittest, pytest
from tqsdk import TqApi, TqAccount, utils, TargetPosTask
from tqsdk.test.base_testcase import TQBaseTestcase


@pytest.mark.skip(reason="temporarily remove 股票环境不可用")
class TestSecurity(TQBaseTestcase):
    """
    测试股票交易业务
    """
    def setUp(self):
        super(TestSecurity, self).setUp()

    def tearDown(self):
        super(TestSecurity, self).tearDown()

    def test_insert_order(self):
        """测试股票买入下单"""
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_security_insert_order_buy.script.lzma"))
        self.td_mock.run(os.path.join(dir_path, "log_file", "test_security_insert_order_buy.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        td_url = f"ws://127.0.0.1:{self.td_mock.port}/"

        utils.RD = random.Random(27)
        account = TqAccount(broker_id="oes_xc", account_id="123456", password="123456", account_type="SPOT")
        api = TqApi(account=account, auth="tianqin,tianqin", _td_url=td_url, _md_url=md_url)
        order = api.insert_order(symbol="SZSE.000002", direction="BUY", volume=100, limit_price=28.00)
        while order.status != "FINISHED":
            api.wait_update()

        #校验委托信
        self.assertEqual(order.user_id, '123456')
        self.assertEqual(order.account_id, '1888000703')
        self.assertEqual(order.exchange_id, 'SZSE')
        self.assertEqual(order.instrument_id, '000002')
        self.assertEqual(order.direction, 'BUY')
        self.assertEqual(order.volume_orign, 100)
        self.assertEqual(order.price_type, 'LIMIT')
        self.assertEqual(order.limit_price, 28.0)
        self.assertEqual(order.volume_left, 0)
        self.assertEqual(order.cum_balance, 2800.0)
        self.assertEqual(order.cum_fee, 5.056)
        # 校验成交信息
        trades = api.get_trade()
        trade = trades['82']
        self.assertEqual(trade.user_id, '123456')
        self.assertEqual(trade.balance, 2800.0)
        self.assertEqual(trade.account_id, '1888000703')
        self.assertEqual(trade.client_seq_no, 4)
        self.assertEqual(trade.cum_balance, 2800.0)
        self.assertEqual(trade.cum_fee, 5.056)
        self.assertEqual(trade.cum_interest, 0.0)
        self.assertEqual(trade.cum_volume, 100)
        self.assertEqual(trade.direction, 'BUY')
        self.assertEqual(trade.exchange_id, 'SZSE')
        self.assertEqual(trade.instrument_id, '000002')
        self.assertEqual(trade.inv_account_id, '0188800703')
        self.assertEqual(trade.price_type, 'LIMIT')
        self.assertEqual(trade.limit_price, 28.0)
        self.assertEqual(trade.price, 28.0)
        self.assertEqual(trade.volume, 100)
        self.assertEqual(trade.volume_orign, 100)
        # 持仓数据校验
        position = api.get_position("SZSE.000002")
        self.assertEqual(position.user_id, '123456')
        self.assertEqual(position.cost, 24438529.36)
        self.assertEqual(position.cost_price, 24.4312)
        self.assertEqual(position.float_profit, 3889966.6399999997)
        self.assertEqual(position.account_id, '1888000703')
        self.assertEqual(position.volume, 1000300)
        # 资金账户校验
        account = api.get_account()
        self.assertEqual(account.user_id, '123456')
        self.assertEqual(account.float_profit, 30799966.640000008)

        api.close()

    def test_insert_order_sell(self):
        """测试股票卖出下单"""
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_security_insert_order_sell.script.lzma"))
        self.td_mock.run(os.path.join(dir_path, "log_file", "test_security_insert_order_sell.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        td_url = f"ws://127.0.0.1:{self.td_mock.port}/"

        """测试股票卖出操作"""
        utils.RD = random.Random(28)
        account = TqAccount(broker_id="oes_xc", account_id="123456", password="123456", account_type="SPOT")
        api = TqApi(account=account, auth="tianqin,tianqin", _td_url=td_url, _md_url=md_url)
        order = api.insert_order(symbol="SSE.600000", direction="SELL", volume=500, limit_price=9.45)
        while order.status != "FINISHED":
            api.wait_update()

        #校验委托信
        self.assertEqual(order.user_id, '123456')
        self.assertEqual(order.account_id, '1888000703')
        self.assertEqual(order.exchange_id, 'SSE')
        self.assertEqual(order.instrument_id, '600000')
        self.assertEqual(order.direction, 'SELL')
        self.assertEqual(order.volume_orign, 500)
        self.assertEqual(order.price_type, 'LIMIT')
        self.assertEqual(order.limit_price, 9.45)
        self.assertEqual(order.volume_left, 0)
        self.assertEqual(order.cum_balance, 4725.0)
        self.assertEqual(order.cum_fee, 9.8195)
        # 校验成交信息
        trades = api.get_trade()
        trade = trades['85']
        self.assertEqual(trade.user_id, '123456')
        self.assertEqual(trade.balance, 4725.0)
        self.assertEqual(trade.account_id, '1888000703')
        self.assertEqual(trade.client_seq_no, 5)
        self.assertEqual(trade.cum_balance, 4725.0)
        self.assertEqual(trade.cum_fee, 9.8195)
        self.assertEqual(trade.cum_interest, 0.0)
        self.assertEqual(trade.cum_volume, 500)
        self.assertEqual(trade.direction, 'SELL')
        self.assertEqual(trade.exchange_id, 'SSE')
        self.assertEqual(trade.instrument_id, '600000')
        self.assertEqual(trade.inv_account_id, 'A188800703')
        self.assertEqual(trade.price_type, 'LIMIT')
        self.assertEqual(trade.limit_price, 9.45)
        self.assertEqual(trade.price, 9.45)
        self.assertEqual(trade.volume, 500)
        self.assertEqual(trade.volume_orign, 500)
        # 持仓数据校验
        position = api.get_position("SSE.600000")
        self.assertEqual(position.user_id, '123456')
        self.assertEqual(position.cost, 13265264.05)
        self.assertEqual(position.cost_price, 13.2719)
        self.assertEqual(position.float_profit, -3790004.0500000003)
        self.assertEqual(position.volume, 999500)
        self.assertEqual(position.last_price, 9.48)
        # 资金账户校验
        account = api.get_account()
        self.assertEqual(account.user_id, '123456')
        self.assertEqual(account.float_profit, 29822043.35)

        api.close()

    def test_insert_order_cancel(self):
        """撤单测试"""
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_security_insert_order_cancel.script.lzma"))
        self.td_mock.run(os.path.join(dir_path, "log_file", "test_security_insert_order_cancel.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        td_url = f"ws://127.0.0.1:{self.td_mock.port}/"

        utils.RD = random.Random(34)
        account = TqAccount(broker_id="oes_xc", account_id="123456", password="123456", account_type="SPOT")
        api = TqApi(account=account, auth="tianqin,tianqin", _td_url=td_url, _md_url=md_url)
        order = api.insert_order(symbol="SZSE.000002", direction="BUY", volume=1000, limit_price=25.30)
        api.cancel_order(order)
        while order.status != "FINISHED":
            api.wait_update()
        #校验委托信
        self.assertEqual(order.order_id, '14')
        self.assertEqual(order.account_id, '1888000703')
        self.assertEqual(order.exchange_id, 'SZSE')
        self.assertEqual(order.instrument_id, '000002')
        self.assertEqual(order.direction, 'BUY')
        self.assertEqual(order.volume_orign, 1000)
        self.assertEqual(order.volume_left, 600)
        self.assertEqual(order.volume_canceled, 600)
        self.assertEqual(order.cum_volume, 400)
        self.assertEqual(order.price_type, 'LIMIT')
        self.assertEqual(order.limit_price, 25.3)
        self.assertEqual(order.cum_balance, 10120.0)
        self.assertEqual(order.cum_fee, 5.2024)
        # 校验成交信息
        trades = api.get_trade()
        trade = trades['117']
        self.assertEqual(trade.user_id, '123456')
        self.assertEqual(trade.balance, 10120.0)
        self.assertEqual(trade.client_seq_no, 14)
        self.assertEqual(trade.cum_balance, 10120.0)
        self.assertEqual(trade.cum_fee, 5.2024)
        self.assertEqual(trade.cum_volume, 400)
        self.assertEqual(trade.direction, 'BUY')
        self.assertEqual(trade.exchange_id, 'SZSE')
        self.assertEqual(trade.instrument_id, '000002')
        self.assertEqual(trade.inv_account_id, '0188800703')
        self.assertEqual(trade.price_type, 'LIMIT')
        self.assertEqual(trade.limit_price, 25.3)
        self.assertEqual(trade.price, 25.3)
        self.assertEqual(trade.volume, 400)
        self.assertEqual(trade.volume_orign, 1000)
        api.close()

    def test_insert_order2(self):
        """测试股票OTG BUG修复-[BE-1041]"""
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_security_insert_order_buy2.script.lzma"))
        self.td_mock.run(os.path.join(dir_path, "log_file", "test_security_insert_order_buy2.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        td_url = f"ws://127.0.0.1:{self.td_mock.port}/"

        utils.RD = random.Random(30)
        account = TqAccount(broker_id="oes_xc", account_id="123456", password="123456", account_type="SPOT")
        api = TqApi(account=account, auth="tianqin,tianqin", _td_url=td_url, _md_url=md_url)
        order = api.insert_order(symbol="SZSE.000002", direction="BUY", volume=100, limit_price=28.00)
        while order.status != "FINISHED":
            api.wait_update()

        #校验委托
        self.assertEqual(order.order_id, '15')
        self.assertEqual(order.exchange_id, 'SZSE')
        self.assertEqual(order.instrument_id, '000002')
        self.assertEqual(order.direction, 'BUY')
        self.assertEqual(order.volume_orign, 100)
        self.assertEqual(order.price_type, 'LIMIT')
        self.assertEqual(order.limit_price, 28.0)
        self.assertEqual(order.volume_left, 0)
        self.assertEqual(order.cum_balance, 2772.0)
        self.assertEqual(order.cum_fee, 5.0554)
        # 校验成交信息
        trades = api.get_trade()
        trade = trades['158']
        self.assertEqual(trade.balance, 2772.0)
        self.assertEqual(trade.account_id, '1888000703')
        self.assertEqual(trade.client_seq_no, '15')
        # 持仓数据校验
        position = api.get_position("SZSE.000002")
        self.assertEqual(position.today_buy_volume, 246200)
        api.close()
