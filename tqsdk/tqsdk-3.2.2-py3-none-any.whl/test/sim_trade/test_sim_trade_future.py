#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'mayanqiong'

import unittest

import numpy as np

from tqsdk.diff import _simple_merge_diff
from tqsdk.tradeable.sim.trade_future import SimTrade


class TestSimTradeFuture(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期货交易
    1. 市价单, 立即成交
    2. 市价单, 涨停价，市价指令剩余撤销
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        # 更新初始行情
        self.sim_trade.update_quotes("CZCE.MA105", {
            'quotes': {
                'CZCE.MA105': {
                    'datetime': '2021-03-17 13:33:54.600000', 'ask_price1': 2470.0, 'bid_price1': 2469.0,
                    'last_price': 2470.0, 'price_tick': 1.0, 'volume_multiple': 10.0, 'ins_class': 'FUTURE',
                    'instrument_id': 'CZCE.MA105', 'margin': 1718.5, 'commission': 2.0,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "23:00:00"]]}
                }
            }
        })

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_future_1(self):
        """市价单, 立即成交"""
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'BUY',
            'offset': 'OPEN',
            'volume': 3,
            'price_type': 'ANY',
            'time_condition': 'IOC',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {"currency": "CNY", "pre_balance": 1000000.0, "static_balance": 1000000.0, "balance": 999994.0,
             "available": 994838.5, "float_profit": 0.0, "position_profit": 0.0, "close_profit": 0.0,
             "frozen_margin": 0.0, "margin": 5155.5, "frozen_commission": 0.0, "commission": 6.0, "frozen_premium": 0.0,
             "premium": 0.0, "deposit": 0.0, "withdraw": 0.0, "risk_ratio": 0.005155530933185599, "market_value": 0.0,
             "ctp_balance": float('nan'), "ctp_available": float('nan')}
        )

        trades = self.account_snapshot['trade']['abc']['trades']
        self.assertEqual(
            trades,
            {
                "PYSDK_insert_42de71a44009a3420164af39b87a7870|3": {
                    "user_id": "TQSIM",
                    "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870",
                    "trade_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870|3",
                    "exchange_trade_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870|3",
                    "exchange_id": "CZCE", "instrument_id": "MA105",
                    "direction": "BUY", "offset": "OPEN", "price": 2470.0,
                    "volume": 3, "trade_date_time": 1615959234600000000,
                    "commission": 6.0
                }
            }
        )

        orders = self.account_snapshot['trade']['abc']['orders']
        self.assertEqual(
            orders,
            {
                "PYSDK_insert_42de71a44009a3420164af39b87a7870": {
                    "user_id": "TQSIM", "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870",
                    "exchange_id": "CZCE", "instrument_id": "MA105", "direction": "BUY", "offset": "OPEN",
                    "price_type": "ANY", "time_condition": "IOC", "volume_condition": "ANY",
                    "exchange_order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870",
                    "volume_orign": 3, "volume_left": 0, "frozen_margin": 0.0, "frozen_premium": 0.0,
                    "last_msg": "全部成交", "status": "FINISHED", "insert_date_time": 1615959234600000000
                }
            }
        )

        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            positions["CZCE.MA105"],
            {
                "exchange_id": "CZCE", "instrument_id": "MA105",
                "pos_long_his": 0, "pos_long_today": 3, "pos_short_his": 0, "pos_short_today": 0,
                "volume_long_today": 3, "volume_long_his": 0, "volume_long": 3,
                "volume_long_frozen_today": 0, "volume_long_frozen_his": 0, "volume_long_frozen": 0,
                "volume_short_today": 0, "volume_short_his": 0, "volume_short": 0,
                "volume_short_frozen_today": 0, "volume_short_frozen_his": 0, "volume_short_frozen": 0,
                "open_price_long": 2470.0, "open_price_short": float('nan'),
                "open_cost_long": 74100.0, "open_cost_short": 0.0,
                "position_price_long": 2470.0, "position_price_short": float('nan'),
                "position_cost_long": 74100.0, "position_cost_short": 0.0,
                "float_profit_long": 0.0, "float_profit_short": 0.0, "float_profit": 0.0,
                "position_profit_long": 0.0, "position_profit_short": 0.0, "position_profit": 0.0,
                "margin_long": 5155.5, "margin_short": 0.0, "margin": 5155.5,
                "last_price": 2470.0, "underlying_last_price": float('nan'),
                "market_value_long": 0.0, "market_value_short": 0.0, "market_value": 0.0, 'future_margin': 1718.5
            }
        )

        # 下单成功 order
        self.assertEqual(
            orders_events[0],
            {
                "user_id": "TQSIM", "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "exchange_id": "CZCE",
                "instrument_id": "MA105", "direction": "BUY", "offset": "OPEN", "price_type": "ANY",
                "time_condition": "IOC", "volume_condition": "ANY",
                "exchange_order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870",
                "volume_orign": 3, "volume_left": 3, "frozen_margin": 0.0,
                "frozen_premium": 0.0, "last_msg": "报单成功", "status": "ALIVE", "insert_date_time": 1615959234600000000
            }
        )
        # 全部成交 order
        self.assertEqual(
            orders_events[1],
            {
                "user_id": "TQSIM", "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "exchange_id": "CZCE",
                "instrument_id": "MA105", "direction": "BUY", "offset": "OPEN", "price_type": "ANY",
                "time_condition": "IOC", "volume_condition": "ANY",
                "exchange_order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870",
                "volume_orign": 3, "volume_left": 0, "frozen_margin": 0.0, "frozen_premium": 0.0,
                "last_msg": "全部成交", "status": "FINISHED", "insert_date_time": 1615959234600000000
            }
        )

    def test_trade_future_2(self):
        """市价单, 涨停价，市价指令剩余撤销"""
        diffs, orders_events = self.sim_trade.update_quotes("CZCE.MA105", {
            'quotes': {
                'CZCE.MA105': {'ask_price1': float('nan')}
            }
        })
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'BUY',
            'offset': 'OPEN',
            'volume': 3,
            'price_type': 'ANY',
            'time_condition': 'IOC',
            'volume_condition': 'ANY'
        })
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {"currency": "CNY", "pre_balance": 1000000.0, "static_balance": 1000000.0, "balance": 1000000.0,
             "available": 1000000.0, "float_profit": 0.0, "position_profit": 0.0, "close_profit": 0.0,
             "frozen_margin": 0.0, "margin": 0.0, "frozen_commission": 0.0, "commission": 0.0, "frozen_premium": 0.0,
             "premium": 0.0, "deposit": 0.0, "withdraw": 0.0, "risk_ratio": 0.0, "market_value": 0.0,
             "ctp_balance": float('nan'), "ctp_available": float('nan')}
        )
        self.assertEqual(len(orders_events), 2)
        self.assertEqual(
            orders_events[0],
            {"user_id": "TQSIM", "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "exchange_id": "CZCE",
             "instrument_id": "MA105", "direction": "BUY", "offset": "OPEN", "price_type": "ANY",
             "time_condition": "IOC", "volume_condition": "ANY",
             "exchange_order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "volume_orign": 3, "volume_left": 3,
             "frozen_margin": 0.0, "frozen_premium": 0.0, "last_msg": "报单成功", "status": "ALIVE",
             "insert_date_time": 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {"user_id": "TQSIM", "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "exchange_id": "CZCE",
             "instrument_id": "MA105", "direction": "BUY", "offset": "OPEN", "price_type": "ANY",
             "time_condition": "IOC", "volume_condition": "ANY",
             "exchange_order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "volume_orign": 3, "volume_left": 3,
             "frozen_margin": 0.0, "frozen_premium": 0.0, "last_msg": "市价指令剩余撤销", "status": "FINISHED",
             "insert_date_time": 1615959234600000000}
        )


class TestSimTradeFuture1(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期货交易
    1. 开仓资金不足
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        self.sim_trade.update_quotes("CFFEX.T2106", {
            'quotes': {
                'CFFEX.T2106': {
                    'datetime': '2021-03-17 13:33:54.600000', 'ask_price1': 96.95, 'bid_price1': 96.945,
                    'last_price': 96.945, 'price_tick': 0.005, 'volume_multiple': 10000.0, 'ins_class': 'FUTURE',
                    'instrument_id': 'CFFEX.T2106', 'margin': 19365.0, 'commission': 3.0,
                    'trading_time': {"day": [["09:30:00", "11:30:00"], ["13:00:00", "15:15:00"]], "night": []}
                }
            }
        })

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_future_1(self):
        diffs, orders_events = self.sim_trade.insert_order("CFFEX.T2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
            'exchange_id': 'CFFEX',
            'instrument_id': 'T2106',
            'direction': 'SELL',
            'offset': 'OPEN',
            'volume': 1000,
            'price_type': 'LIMIT',
            'limit_price': 96.95,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {"currency": "CNY", "pre_balance": 1000000.0, "static_balance": 1000000.0, "balance": 1000000.0,
             "available": 1000000.0, "float_profit": 0.0, "position_profit": 0.0, "close_profit": 0.0,
             "frozen_margin": 0.0, "margin": 0.0, "frozen_commission": 0.0, "commission": 0.0, "frozen_premium": 0.0,
             "premium": 0.0, "deposit": 0.0, "withdraw": 0.0, "risk_ratio": 0.0, "market_value": 0.0,
             "ctp_balance": float('nan'), "ctp_available": float('nan')}
        )
        self.assertEqual(
            orders_events[0],
            {"user_id": "TQSIM", "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "exchange_id": "CFFEX",
             "instrument_id": "T2106", "direction": "SELL", "offset": "OPEN", "price_type": "LIMIT",
             "limit_price": 96.95, "time_condition": "GFD", "volume_condition": "ANY",
             "exchange_order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "volume_orign": 1000,
             "volume_left": 1000, "frozen_margin": 0.0, "frozen_premium": 0.0, "last_msg": "报单成功", "status": "ALIVE",
             "insert_date_time": 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {"user_id": "TQSIM", "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "exchange_id": "CFFEX",
             "instrument_id": "T2106", "direction": "SELL", "offset": "OPEN", "price_type": "LIMIT",
             "limit_price": 96.95, "time_condition": "GFD", "volume_condition": "ANY",
             "exchange_order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "volume_orign": 1000,
             "volume_left": 1000, "frozen_margin": 0.0, "frozen_premium": 0.0, "last_msg": "开仓资金不足",
             "status": "FINISHED", "insert_date_time": 1615959234600000000}
        )


class TestSimTradeFuture2(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期货交易
    1. 不支持的合约类型
    2. 不在可交易时间段内
    3. 指数下单
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        self.sim_trade.update_quotes("KQ.m@CFFEX.T", {
            'quotes': {
                'KQ.i@CFFEX.T': {
                    'datetime': '2021-03-17 13:33:54.600000', 'ask_price1': float('nan'), 'bid_price1': float('nan'),
                    'last_price': 96.945, 'price_tick': 0.005, 'volume_multiple': 10000.0, 'ins_class': 'FUTURE_INDEX',
                    'instrument_id': 'KQ.i@CFFEX.T', 'margin': 19365.0, 'commission': 3.0,
                    'trading_time': {"day": [["09:30:00", "11:30:00"], ["13:00:00", "15:15:00"]], "night": []}
                },
                'KQ.m@CFFEX.T': {
                    'datetime': '2021-03-17 13:33:54.600000', 'ask_price1': 96.95, 'bid_price1': 96.945,
                    'last_price': 96.945, 'price_tick': 0.005, 'volume_multiple': 10000.0, 'ins_class': 'FUTURE_CONT',
                    'instrument_id': 'KQ.m@CFFEX.T',
                    'trading_time': {"day": [["09:30:00", "11:30:00"], ["13:00:00", "15:15:00"]], "night": []}
                }
            }
        })

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_future_1(self):
        """不支持的合约类型，TqSim 目前不支持组合，股票，etf期权模拟交易"""
        diffs, orders_events = self.sim_trade.insert_order("KQ.m@CFFEX.T", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_cont',
            'exchange_id': 'KQ',
            'instrument_id': 'm@CFFEX.T',
            'direction': 'SELL',
            'offset': 'OPEN',
            'volume': 1000,
            'price_type': 'LIMIT',
            'limit_price': 96.95,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {"currency": "CNY", "pre_balance": 1000000.0, "static_balance": 1000000.0, "balance": 1000000.0,
             "available": 1000000.0, "float_profit": 0.0, "position_profit": 0.0, "close_profit": 0.0,
             "frozen_margin": 0.0, "margin": 0.0, "frozen_commission": 0.0, "commission": 0.0,
             "frozen_premium": 0.0,
             "premium": 0.0, "deposit": 0.0, "withdraw": 0.0, "risk_ratio": 0.0, "market_value": 0.0,
             "ctp_balance": float('nan'), "ctp_available": float('nan')}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_cont', 'exchange_id': 'KQ', 'instrument_id': 'm@CFFEX.T',
             'direction': 'SELL', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 96.95,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_cont',
             'volume_orign': 1000, 'volume_left': 1000, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功',
             'status': 'ALIVE', 'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_cont', 'exchange_id': 'KQ', 'instrument_id': 'm@CFFEX.T',
             'direction': 'SELL', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 96.95,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_cont',
             'volume_orign': 1000, 'volume_left': 1000, 'frozen_margin': 0.0, 'frozen_premium': 0.0,
             'last_msg': '不支持的合约类型，TqSim 目前不支持组合，股票，etf期权模拟交易', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def test_trade_future_2(self):
        """不在可交易时间段内"""
        diffs, orders_events = self.sim_trade.insert_order("KQ.i@CFFEX.T", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_index',
            'exchange_id': 'KQ',
            'instrument_id': 'i@CFFEX.T',
            'direction': 'BUY',
            'offset': 'OPEN',
            'volume': 10,
            'price_type': 'LIMIT',
            'limit_price': 96.93,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 1000000.0,
             'available': 806350.0, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 193650.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 0.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0,
             'market_value': 0.0, "ctp_balance": float('nan'), "ctp_available": float('nan')}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_index', 'exchange_id': 'KQ', 'instrument_id': 'i@CFFEX.T',
             'direction': 'BUY', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 96.93, 'time_condition': 'GFD',
             'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_index', 'volume_orign': 10,
             'volume_left': 10, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )

        diffs, orders_events = self.sim_trade.update_quotes("SHFE.ni2106", {
            "quotes": {
                'SHFE.ni2106': {
                    'datetime': '2021-03-17 21:00:00.500000', 'ask_price1': 120730.0, 'bid_price1': 120720.0,
                    'last_price': 120720.0, 'price_tick': 10.0, 'volume_multiple': 1.0, 'ins_class': 'FUTURE',
                    'instrument_id': 'SHFE.ni2106', 'margin': 9708.8, 'commission': 6.0,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "25:00:00"]]
                    }
                }
            }
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        diffs, orders_events = self.sim_trade.insert_order("KQ.i@CFFEX.T", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_index',
            'exchange_id': 'KQ',
            'instrument_id': 'i@CFFEX.T',
            'direction': 'BUY',
            'offset': 'OPEN',
            'volume': 10,
            'price_type': 'LIMIT',
            'limit_price': 96.95,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 1000000.0,
             'available': 806350.0, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 193650.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 0.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0,
             'market_value': 0.0, "ctp_balance": float('nan'), "ctp_available": float('nan')}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_index', 'exchange_id': 'KQ', 'instrument_id': 'i@CFFEX.T',
             'direction': 'BUY', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 96.95, 'time_condition': 'GFD',
             'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_index', 'volume_orign': 10,
             'volume_left': 10, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615986000500000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_index', 'exchange_id': 'KQ', 'instrument_id': 'i@CFFEX.T',
             'direction': 'BUY', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 96.95, 'time_condition': 'GFD',
             'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_index', 'volume_orign': 10,
             'volume_left': 10, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '下单失败, 不在可交易时间段内',
             'status': 'FINISHED', 'insert_date_time': 1615986000500000000}
        )

    def test_trade_future_3(self):
        """指数下单"""
        diffs, orders_events = self.sim_trade.insert_order("KQ.i@CFFEX.T", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_index',
            'exchange_id': 'KQ',
            'instrument_id': 'i@CFFEX.T',
            'direction': 'BUY',
            'offset': 'OPEN',
            'volume': 10,
            'price_type': 'LIMIT',
            'limit_price': 96.93,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 1000000.0,
             'available': 806350.0, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 193650.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 0.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0,
             'market_value': 0.0, "ctp_balance": float('nan'), "ctp_available": float('nan')}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_index', 'exchange_id': 'KQ',
             'instrument_id': 'i@CFFEX.T',
             'direction': 'BUY', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 96.93,
             'time_condition': 'GFD',
             'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_index', 'volume_orign': 10,
             'volume_left': 10, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )


class TestSimTradeFuture3(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期货交易 限价单
    1. 买开（挂单）
    2. 更新价格，没有成交
    3. 更新价格，成交
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        self.sim_trade.update_quotes("CZCE.MA105", {
            'quotes': {
                'CZCE.MA105': {
                    'datetime': '2021-03-17 13:33:54.600000', 'ask_price1': 2470.0, 'bid_price1': 2469.0,
                    'last_price': 2470.0, 'price_tick': 1.0, 'volume_multiple': 10.0, 'ins_class': 'FUTURE',
                    'instrument_id': 'CZCE.MA105', 'margin': 1718.5, 'commission': 2.0,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "23:00:00"]]}
                }
            }
        })

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_future(self):
        self.trade_future_1()
        self.trade_future_2()
        self.trade_future_3()

    def trade_future_1(self):
        """买开"""
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'BUY',
            'offset': 'OPEN',
            'volume': 3,
            'price_type': 'LIMIT',
            'limit_price': 2469.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {"currency": "CNY", "pre_balance": 1000000.0, "static_balance": 1000000.0, "balance": 1000000.0,
             "available": 994844.5, "float_profit": 0.0, "position_profit": 0.0, "close_profit": 0.0,
             "frozen_margin": 5155.5, "margin": 0.0, "frozen_commission": 0.0, "commission": 0.0, "frozen_premium": 0.0,
             "premium": 0.0, "deposit": 0.0, "withdraw": 0.0, "risk_ratio": 0.0, "market_value": 0.0,
             "ctp_balance": float('nan'), "ctp_available": float('nan')}
        )

        self.assertEqual(
            orders_events[0],
            {"user_id": "TQSIM", "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "exchange_id": "CZCE",
             "instrument_id": "MA105", "direction": "BUY", "offset": "OPEN", "price_type": "LIMIT",
             "limit_price": 2469.0, "time_condition": "GFD", "volume_condition": "ANY",
             "exchange_order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "volume_orign": 3, "volume_left": 3,
             "frozen_margin": 0.0, "frozen_premium": 0.0, "last_msg": "报单成功", "status": "ALIVE",
             "insert_date_time": 1615959234600000000}
        )

    def trade_future_2(self):
        """更新价格，没有成交"""
        diffs, orders_events = self.sim_trade.update_quotes("CZCE.MA105", {
            'quotes': {
                'CZCE.MA105': {
                    'datetime': '2021-03-16 10:05:24.000001',
                    'ask_price1': 2470.0, 'bid_price1': 2468.0, 'last_price': 2469.0,
                }
            }
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual([], orders_events)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

    def trade_future_3(self):
        """更新价格，成交"""
        diffs, orders_events = self.sim_trade.update_quotes("CZCE.MA105", {
            'quotes': {
                'CZCE.MA105': {
                    'datetime': '2021-03-16 10:05:25.000001',
                    'ask_price1': 2469.0, 'bid_price1': 2467.0, 'last_price': 2468.0,
                }
            }
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {"currency": "CNY", "pre_balance": 1000000.0, "static_balance": 1000000.0, "balance": 999964.0,
             "available": 994808.5, "float_profit": -30.0, "position_profit": -30.0, "close_profit": 0.0,
             "frozen_margin": 0.0, "margin": 5155.5, "frozen_commission": 0.0, "commission": 6.0, "frozen_premium": 0.0,
             "premium": 0.0, "deposit": 0.0, "withdraw": 0.0, "risk_ratio": 0.005155685604681768, "market_value": 0.0,
             "ctp_balance": float('nan'), "ctp_available": float('nan')}
        )
        trades = self.account_snapshot['trade']['abc']['trades']
        self.assertEqual(
            trades,
            {"PYSDK_insert_42de71a44009a3420164af39b87a7870|3": {"user_id": "TQSIM",
                                                                 "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870",
                                                                 "trade_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870|3",
                                                                 "exchange_trade_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870|3",
                                                                 "exchange_id": "CZCE", "instrument_id": "MA105",
                                                                 "direction": "BUY", "offset": "OPEN", "price": 2469.0,
                                                                 "volume": 3, "trade_date_time": 1615959234600000000,
                                                                 "commission": 6.0}}
        )
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            positions["CZCE.MA105"],
            {"exchange_id": "CZCE", "instrument_id": "MA105", "pos_long_his": 0, "pos_long_today": 3,
             "pos_short_his": 0, "pos_short_today": 0, "volume_long_today": 3, "volume_long_his": 0, "volume_long": 3,
             "volume_long_frozen_today": 0, "volume_long_frozen_his": 0, "volume_long_frozen": 0,
             "volume_short_today": 0, "volume_short_his": 0, "volume_short": 0, "volume_short_frozen_today": 0,
             "volume_short_frozen_his": 0, "volume_short_frozen": 0, "open_price_long": 2469.0,
             "open_price_short": float('nan'), "open_cost_long": 74070.0, "open_cost_short": 0.0,
             "position_price_long": 2469.0, "position_price_short": float('nan'), "position_cost_long": 74070.0,
             "position_cost_short": 0.0, "float_profit_long": -30.0, "float_profit_short": 0.0, "float_profit": -30.0,
             "position_profit_long": -30.0, "position_profit_short": 0.0, "position_profit": -30.0,
             "margin_long": 5155.5, "margin_short": 0.0, "margin": 5155.5, "last_price": 2468.0,
             "underlying_last_price": float('nan'), "market_value_long": 0.0, "market_value_short": 0.0,
             "market_value": 0.0, 'future_margin': 1718.5}
        )
        orders = self.account_snapshot['trade']['abc']['orders']
        self.assertEqual(
            orders,
            {
                "PYSDK_insert_42de71a44009a3420164af39b87a7870": {
                    "user_id": "TQSIM",
                    "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870",
                    "exchange_id": "CZCE",
                    "instrument_id": "MA105",
                    "direction": "BUY",
                    "offset": "OPEN",
                    "price_type": "LIMIT",
                    "limit_price": 2469.0,
                    "time_condition": "GFD",
                    "volume_condition": "ANY",
                    "exchange_order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870",
                    "volume_orign": 3,
                    "volume_left": 0,
                    "frozen_margin": 0.0,
                    "frozen_premium": 0.0,
                    "last_msg": "全部成交",
                    "status": "FINISHED",
                    "insert_date_time": 1615959234600000000
                }
            })
        self.assertEqual(
            orders_events[0],
            {"user_id": "TQSIM", "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "exchange_id": "CZCE",
             "instrument_id": "MA105", "direction": "BUY", "offset": "OPEN", "price_type": "LIMIT",
             "limit_price": 2469.0, "time_condition": "GFD", "volume_condition": "ANY",
             "exchange_order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870", "volume_orign": 3, "volume_left": 0,
             "frozen_margin": 0.0, "frozen_premium": 0.0, "last_msg": "全部成交", "status": "FINISHED",
             "insert_date_time": 1615959234600000000}
        )


class TestSimTradeFuture4(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期货交易
    限价单买开（挂单）
    1. 主动撤单
    2. 结算自动撤单
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        self.sim_trade.update_quotes("CZCE.MA105", {
            'quotes': {
                'CZCE.MA105': {
                    'datetime': '2021-03-17 13:33:54.600000', 'ask_price1': 2470.0, 'bid_price1': 2469.0,
                    'last_price': 2470.0, 'price_tick': 1.0, 'volume_multiple': 10.0, 'ins_class': 'FUTURE',
                    'instrument_id': 'CZCE.MA105', 'margin': 1718.5, 'commission': 2.0,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "23:00:00"]]}
                }
            }
        })
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'SELL',
            'offset': 'OPEN',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 2472.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_future_1(self):
        """撤单"""
        diffs, orders_events = self.sim_trade.cancel_order("CZCE.MA105", {
            "aid": "cancel_order",
            "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870"
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {
                "currency": "CNY",
                "pre_balance": 1000000.0,
                "static_balance": 1000000.0,
                "balance": 1000000.0,
                "available": 1000000.0,
                "float_profit": 0.0,
                "position_profit": 0.0,
                "close_profit": 0.0,
                "frozen_margin": 0.0,
                "margin": 0.0,
                "frozen_commission": 0.0,
                "commission": 0.0,
                "frozen_premium": 0.0,
                "premium": 0.0,
                "deposit": 0.0,
                "withdraw": 0.0,
                "risk_ratio": 0.0,
                "market_value": 0.0,
                "ctp_balance": float('nan'),
                "ctp_available": float('nan')
            }
        )
        self.assertEqual(
            orders_events[0],
            {
                "user_id": "TQSIM",
                "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870",
                "exchange_id": "CZCE",
                "instrument_id": "MA105",
                "direction": "SELL",
                "offset": "OPEN",
                "price_type": "LIMIT",
                "limit_price": 2472.0,
                "time_condition": "GFD",
                "volume_condition": "ANY",
                "exchange_order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870",
                "volume_orign": 2,
                "volume_left": 2,
                "frozen_margin": 0.0,
                "frozen_premium": 0.0,
                "last_msg": "已撤单",
                "status": "FINISHED",
                "insert_date_time": 1615959234600000000
            }
        )

    def test_trade_future_2(self):
        """结算（自动撤单）"""
        diffs, orders_events = self.sim_trade.update_quotes("CZCE.MA105", {
            "quotes": {
                "CZCE.MA105": {
                    'datetime': '2021-03-16 14:59:59.000001', 'ask_price1': 2468.0, 'bid_price1': 2466.0,
                    'last_price': 2467.0
                }
            }
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual([], orders_events)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        diffs, orders_events, trade_log = self.sim_trade.settle()
        self.assertEqual(len(diffs), 3)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 1000000.0,
             'available': 1000000.0, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 0.0, 'frozen_premium': 0.0,
             'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0, 'market_value': 0.0,
             'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            positions['CZCE.MA105'],
            {'exchange_id': 'CZCE', 'instrument_id': 'MA105', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': float('nan'),
             'open_price_short': float('nan'),
             'open_cost_long': 0.0, 'open_cost_short': 0.0, 'position_price_long': 2467.0,
             'position_price_short': 2467.0, 'position_cost_long': 0.0, 'position_cost_short': 0.0,
             'float_profit_long': 0.0, 'float_profit_short': 0.0, 'float_profit': 0.0, 'position_profit_long': 0,
             'position_profit_short': 0, 'position_profit': 0, 'margin_long': 0.0, 'margin_short': 0.0, 'margin': 0.0,
             'last_price': 2467.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 1718.5}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105', 'direction': 'SELL', 'offset': 'OPEN', 'price_type': 'LIMIT',
             'limit_price': 2472.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '交易日结束，自动撤销当日有效的委托单（GFD）',
             'status': 'FINISHED', 'insert_date_time': 1615959234600000000}
        )


class TestSimTradeFuture5(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期货交易 （卖开 10 手）
    1. 平仓5手，冻结
    2. 平仓10手，平仓手数不足
    3. 更新价格，5 手平仓成交
    4. 下单 IOC ，未成交
    5. 结算
    6. 平仓 2 手
    7. IOC, 平仓成交
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        self.sim_trade.update_quotes("DCE.jd2105", {
            'quotes': {
                'DCE.jd2105': {
                    'datetime': '2021-03-17 13:33:54.600000', 'ask_price1': 4360.0, 'bid_price1': 4359.0,
                    'last_price': 4359.0, 'price_tick': 1.0, 'volume_multiple': 10.0, 'ins_class': 'FUTURE',
                    'instrument_id': 'DCE.jd2105', 'margin': 3062.5, 'commission': 6.5625,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": []
                    }
                }
            }
        })
        # 卖开 10 手
        self.account_snapshot['trade']['abc']['positions']
        diffs, orders_events = self.sim_trade.insert_order("DCE.jd2105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'sell_open_10',
            'exchange_id': 'DCE',
            'instrument_id': 'jd2105',
            'direction': 'SELL',
            'offset': 'OPEN',
            'volume': 10,
            'price_type': 'LIMIT',
            'limit_price': 4359.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_future(self):
        self.trade_future_1()
        self.trade_future_2()
        self.trade_future_3()
        self.trade_future_4()
        self.trade_future_5()
        self.trade_future_6()
        self.trade_future_7()

    def trade_future_1(self):
        """平仓5手，冻结"""
        diffs, orders_events = self.sim_trade.insert_order("DCE.jd2105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'buy_close_5',
            'exchange_id': 'DCE',
            'instrument_id': 'jd2105',
            'direction': 'BUY',
            'offset': 'CLOSE',
            'volume': 5,
            'price_type': 'LIMIT',
            'limit_price': 4358.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999934.375,
             'available': 969309.375, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 30625.0, 'frozen_commission': 0.0, 'commission': 65.625,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.030627009897524524,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['DCE.jd2105'],
            {'exchange_id': 'DCE', 'instrument_id': 'jd2105', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 10, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 10, 'volume_short_his': 0, 'volume_short': 10, 'volume_short_frozen_today': 5,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 5, 'open_price_long': float('nan'),
             'open_price_short': 4359.0,
             'open_cost_long': 0.0, 'open_cost_short': 435900.0, 'position_price_long': float('nan'),
             'position_price_short': 4359.0, 'position_cost_long': 0.0, 'position_cost_short': 435900.0,
             'float_profit_long': 0.0, 'float_profit_short': 0.0, 'float_profit': 0.0, 'position_profit_long': 0.0,
             'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0, 'margin_short': 30625.0,
             'margin': 30625.0, 'last_price': 4359.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 3062.5}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_5', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 4358.0,
             'time_condition': 'GFD',
             'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_5', 'volume_orign': 5, 'volume_left': 5,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_2(self):
        """平仓10手，平仓手数不足"""
        diffs, orders_events = self.sim_trade.insert_order("DCE.jd2105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'buy_close_10',
            'exchange_id': 'DCE',
            'instrument_id': 'jd2105',
            'direction': 'BUY',
            'offset': 'CLOSE',
            'volume': 10,
            'price_type': 'LIMIT',
            'limit_price': 4360.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999934.375,
             'available': 969309.375, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 30625.0, 'frozen_commission': 0.0, 'commission': 65.625,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.030627009897524524,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['DCE.jd2105'],
            {'exchange_id': 'DCE', 'instrument_id': 'jd2105', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 10, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 10, 'volume_short_his': 0, 'volume_short': 10, 'volume_short_frozen_today': 5,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 5, 'open_price_long': float('nan'),
             'open_price_short': 4359.0,
             'open_cost_long': 0.0, 'open_cost_short': 435900.0, 'position_price_long': float('nan'),
             'position_price_short': 4359.0, 'position_cost_long': 0.0, 'position_cost_short': 435900.0,
             'float_profit_long': 0.0, 'float_profit_short': 0.0, 'float_profit': 0.0, 'position_profit_long': 0.0,
             'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0, 'margin_short': 30625.0,
             'margin': 30625.0, 'last_price': 4359.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 3062.5}
        )

        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_10', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 4360.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_10',
             'volume_orign': 10, 'volume_left': 10, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功',
             'status': 'ALIVE', 'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_10', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 4360.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_10',
             'volume_orign': 10, 'volume_left': 10, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '平仓手数不足',
             'status': 'FINISHED', 'insert_date_time': 1615959234600000000}
        )

    def trade_future_3(self):
        """更新价格，成交"""
        diffs, orders_events = self.sim_trade.update_quotes("DCE.jd2105", {
            'quotes': {
                'DCE.jd2105': {
                    'datetime': '2021-03-16 10:05:25.000001',
                    'ask_price1': 4358.0, 'bid_price1': 4357.0, 'last_price': 4357.0,
                }
            }
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 1000051.5625,
             'available': 984739.0625, 'float_profit': 100.0, 'position_profit': 100.0, 'close_profit': 50.0,
             'frozen_margin': 0.0, 'margin': 15312.5, 'frozen_commission': 0.0, 'commission': 98.4375,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.015311710489927863,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['DCE.jd2105'],
            {'exchange_id': 'DCE', 'instrument_id': 'jd2105', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 5, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 5, 'volume_short_his': 0, 'volume_short': 5, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': float('nan'),
             'open_price_short': 4359.0,
             'open_cost_long': 0.0, 'open_cost_short': 217950.0, 'position_price_long': float('nan'),
             'position_price_short': 4359.0, 'position_cost_long': 0.0, 'position_cost_short': 217950.0,
             'float_profit_long': 0.0, 'float_profit_short': 100.0, 'float_profit': 100.0, 'position_profit_long': 0.0,
             'position_profit_short': 100.0, 'position_profit': 100.0, 'margin_long': 0.0, 'margin_short': 15312.5,
             'margin': 15312.5, 'last_price': 4357.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 3062.5}
        )
        self.assertEqual(
            orders,
            {'sell_open_10': {'user_id': 'TQSIM', 'order_id': 'sell_open_10', 'exchange_id': 'DCE',
                              'instrument_id': 'jd2105', 'direction': 'SELL', 'offset': 'OPEN', 'price_type': 'LIMIT',
                              'limit_price': 4359.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
                              'exchange_order_id': 'sell_open_10', 'volume_orign': 10, 'volume_left': 0,
                              'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
                              'insert_date_time': 1615959234600000000},
             'buy_close_5': {'user_id': 'TQSIM', 'order_id': 'buy_close_5', 'exchange_id': 'DCE',
                             'instrument_id': 'jd2105', 'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT',
                             'limit_price': 4358.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
                             'exchange_order_id': 'buy_close_5', 'volume_orign': 5, 'volume_left': 0,
                             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
                             'insert_date_time': 1615959234600000000},
             'buy_close_10': {'user_id': 'TQSIM', 'order_id': 'buy_close_10', 'exchange_id': 'DCE',
                              'instrument_id': 'jd2105', 'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT',
                              'limit_price': 4360.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
                              'exchange_order_id': 'buy_close_10', 'volume_orign': 10, 'volume_left': 10,
                              'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '平仓手数不足', 'status': 'FINISHED',
                              'insert_date_time': 1615959234600000000}}
        )
        self.assertEqual(
            trades,
            {'sell_open_10|10': {'user_id': 'TQSIM', 'order_id': 'sell_open_10', 'trade_id': 'sell_open_10|10',
                                 'exchange_trade_id': 'sell_open_10|10', 'exchange_id': 'DCE',
                                 'instrument_id': 'jd2105', 'direction': 'SELL', 'offset': 'OPEN', 'price': 4359.0,
                                 'volume': 10, 'trade_date_time': 1615959234600000000, 'commission': 65.625},
             'buy_close_5|5': {'user_id': 'TQSIM', 'order_id': 'buy_close_5', 'trade_id': 'buy_close_5|5',
                               'exchange_trade_id': 'buy_close_5|5', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
                               'direction': 'BUY', 'offset': 'CLOSE', 'price': 4358.0, 'volume': 5,
                               'trade_date_time': 1615959234600000000, 'commission': 32.8125}}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_5', 'exchange_id': 'DCE',
             'instrument_id': 'jd2105', 'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 4358.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'buy_close_5', 'volume_orign': 5, 'volume_left': 0,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_4(self):
        """下单 FAK ，未成交"""
        diffs, orders_events = self.sim_trade.insert_order("DCE.jd2105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'buy_close_10',
            'exchange_id': 'DCE',
            'instrument_id': 'jd2105',
            'direction': 'BUY',
            'offset': 'CLOSE',
            'volume': 5,
            'price_type': 'LIMIT',
            'limit_price': 4356.0,
            'time_condition': 'IOC',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 4)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 1000051.5625,
             'available': 984739.0625, 'float_profit': 100.0, 'position_profit': 100.0, 'close_profit': 50.0,
             'frozen_margin': 0.0, 'margin': 15312.5, 'frozen_commission': 0.0, 'commission': 98.4375,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.015311710489927863,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            positions['DCE.jd2105'],
            {'exchange_id': 'DCE', 'instrument_id': 'jd2105', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 5, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 5, 'volume_short_his': 0, 'volume_short': 5, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': float('nan'),
             'open_price_short': 4359.0,
             'open_cost_long': 0.0, 'open_cost_short': 217950.0, 'position_price_long': float('nan'),
             'position_price_short': 4359.0, 'position_cost_long': 0.0, 'position_cost_short': 217950.0,
             'float_profit_long': 0.0, 'float_profit_short': 100.0, 'float_profit': 100.0, 'position_profit_long': 0.0,
             'position_profit_short': 100.0, 'position_profit': 100.0, 'margin_long': 0.0, 'margin_short': 15312.5,
             'margin': 15312.5, 'last_price': 4357.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 3062.5}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_10', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 4356.0,
             'time_condition': 'IOC', 'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_10', 'volume_orign': 5,
             'volume_left': 5, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_10', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 4356.0,
             'time_condition': 'IOC', 'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_10', 'volume_orign': 5,
             'volume_left': 5, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '已撤单报单已提交',
             'status': 'FINISHED', 'insert_date_time': 1615959234600000000}
        )

    def trade_future_5(self):
        """结算"""
        diffs, orders_events, trade_log = self.sim_trade.settle()
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000051.5625, 'static_balance': 1000051.5625, 'balance': 1000051.5625,
             'available': 984739.0625, 'float_profit': 100.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 15312.5, 'frozen_commission': 0.0, 'commission': 0.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.015311710489927863,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['DCE.jd2105'],
            {'exchange_id': 'DCE', 'instrument_id': 'jd2105', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 5, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 5, 'volume_short': 5, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': float('nan'),
             'open_price_short': 4359.0,
             'open_cost_long': 0.0, 'open_cost_short': 217950.0, 'position_price_long': 4357.0,
             'position_price_short': 4357.0, 'position_cost_long': 0.0, 'position_cost_short': 217850.0,
             'float_profit_long': 0.0, 'float_profit_short': 100.0, 'float_profit': 100.0, 'position_profit_long': 0.0,
             'position_profit_short': 0, 'position_profit': 0, 'margin_long': 0.0, 'margin_short': 15312.5,
             'margin': 15312.5, 'last_price': 4357.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 3062.5}
        )

    def trade_future_6(self):
        """平仓2手"""
        diffs, orders_events = self.sim_trade.insert_order("DCE.jd2105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'buy_close_2',
            'exchange_id': 'DCE',
            'instrument_id': 'jd2105',
            'direction': 'BUY',
            'offset': 'CLOSE',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 4358.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000051.5625, 'static_balance': 1000051.5625, 'balance': 1000018.4375,
             'available': 990830.9375, 'float_profit': 60.0, 'position_profit': 0.0, 'close_profit': -20.0,
             'frozen_margin': 0.0, 'margin': 9187.5, 'frozen_commission': 0.0, 'commission': 13.125,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.009187330608591905,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            positions['DCE.jd2105'],
            {'exchange_id': 'DCE', 'instrument_id': 'jd2105', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 3, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 3, 'volume_short': 3, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': float('nan'),
             'open_price_short': 4359.0,
             'open_cost_long': 0.0, 'open_cost_short': 130770.0, 'position_price_long': float('nan'),
             'position_price_short': 4357.0, 'position_cost_long': 0.0, 'position_cost_short': 130710.0,
             'float_profit_long': 0.0, 'float_profit_short': 60.0, 'float_profit': 60.0, 'position_profit_long': 0.0,
             'position_profit_short': 0, 'position_profit': 0, 'margin_long': 0.0, 'margin_short': 9187.5,
             'margin': 9187.5, 'last_price': 4357.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 3062.5}
        )
        trades = self.account_snapshot['trade']['abc']['trades']
        self.assertEqual(
            trades,
            {'sell_open_10|10': {'user_id': 'TQSIM', 'order_id': 'sell_open_10', 'trade_id': 'sell_open_10|10',
                                 'exchange_trade_id': 'sell_open_10|10', 'exchange_id': 'DCE',
                                 'instrument_id': 'jd2105', 'direction': 'SELL', 'offset': 'OPEN', 'price': 4359.0,
                                 'volume': 10, 'trade_date_time': 1615959234600000000, 'commission': 65.625},
             'buy_close_5|5': {'user_id': 'TQSIM', 'order_id': 'buy_close_5', 'trade_id': 'buy_close_5|5',
                               'exchange_trade_id': 'buy_close_5|5', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
                               'direction': 'BUY', 'offset': 'CLOSE', 'price': 4358.0, 'volume': 5,
                               'trade_date_time': 1615959234600000000, 'commission': 32.8125},
             'buy_close_2|2': {'user_id': 'TQSIM', 'order_id': 'buy_close_2', 'trade_id': 'buy_close_2|2',
                               'exchange_trade_id': 'buy_close_2|2', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
                               'direction': 'BUY', 'offset': 'CLOSE', 'price': 4358.0, 'volume': 2,
                               'trade_date_time': 1615959234600000000, 'commission': 13.125}}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_2', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 4358.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_2', 'volume_orign': 2,
             'volume_left': 2, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_2', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 4358.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_2', 'volume_orign': 2,
             'volume_left': 0, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_7(self):
        """平仓成交 IOC"""
        diffs, orders_events = self.sim_trade.insert_order("DCE.jd2105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'buy_close_IOC',
            'exchange_id': 'DCE',
            'instrument_id': 'jd2105',
            'direction': 'BUY',
            'offset': 'CLOSE',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 4350.0,
            'time_condition': 'IOC',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 4)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000051.5625, 'static_balance': 1000051.5625, 'balance': 1000018.4375,
             'available': 990830.9375, 'float_profit': 60.0, 'position_profit': 0.0, 'close_profit': -20.0,
             'frozen_margin': 0.0, 'margin': 9187.5, 'frozen_commission': 0.0, 'commission': 13.125,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.009187330608591905,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            positions['DCE.jd2105'],
            {'exchange_id': 'DCE', 'instrument_id': 'jd2105', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 3, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 3, 'volume_short': 3, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': float('nan'),
             'open_price_short': 4359.0,
             'open_cost_long': 0.0, 'open_cost_short': 130770.0, 'position_price_long': float('nan'),
             'position_price_short': 4357.0, 'position_cost_long': 0.0, 'position_cost_short': 130710.0,
             'float_profit_long': 0.0, 'float_profit_short': 60.0, 'float_profit': 60.0, 'position_profit_long': 0.0,
             'position_profit_short': 0, 'position_profit': 0, 'margin_long': 0.0, 'margin_short': 9187.5,
             'margin': 9187.5, 'last_price': 4357.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 3062.5}
        )
        trades = self.account_snapshot['trade']['abc']['trades']
        self.assertEqual(
            trades,
            {'sell_open_10|10': {'user_id': 'TQSIM', 'order_id': 'sell_open_10', 'trade_id': 'sell_open_10|10',
                                 'exchange_trade_id': 'sell_open_10|10', 'exchange_id': 'DCE',
                                 'instrument_id': 'jd2105', 'direction': 'SELL', 'offset': 'OPEN', 'price': 4359.0,
                                 'volume': 10, 'trade_date_time': 1615959234600000000, 'commission': 65.625},
             'buy_close_5|5': {'user_id': 'TQSIM', 'order_id': 'buy_close_5', 'trade_id': 'buy_close_5|5',
                               'exchange_trade_id': 'buy_close_5|5', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
                               'direction': 'BUY', 'offset': 'CLOSE', 'price': 4358.0, 'volume': 5,
                               'trade_date_time': 1615959234600000000, 'commission': 32.8125},
             'buy_close_2|2': {'user_id': 'TQSIM', 'order_id': 'buy_close_2', 'trade_id': 'buy_close_2|2',
                               'exchange_trade_id': 'buy_close_2|2', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
                               'direction': 'BUY', 'offset': 'CLOSE', 'price': 4358.0, 'volume': 2,
                               'trade_date_time': 1615959234600000000, 'commission': 13.125}}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_IOC', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 4350.0,
             'time_condition': 'IOC', 'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_IOC',
             'volume_orign': 2, 'volume_left': 2, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功',
             'status': 'ALIVE', 'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_IOC', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 4350.0,
             'time_condition': 'IOC', 'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_IOC',
             'volume_orign': 2, 'volume_left': 2, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '已撤单报单已提交',
             'status': 'FINISHED', 'insert_date_time': 1615959234600000000}
        )


class TestSimTradeFuture6(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期货交易 （买开 10 手）
    1. 卖平（15手数不足）
    2. 更新价格
    3. 结算 (昨10)
    4. 平仓（10 IOC 未成交）
    5. 平仓（5挂单）
    6. 平仓（2成交）只平今
    7. 加仓 10 (持仓为 8 + 10)
    8. 平仓（5成交）(持仓为 3 + 10) 只平昨
    9. 平仓（5成交）(持仓为 0 + 8) 平昨今
    10. 撤单(已成交的单)
    11. 撤单(未成交的单)
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        self.sim_trade.update_quotes("CZCE.MA105", {
            'quotes': {
                'CZCE.MA105': {
                    'datetime': '2021-03-17 13:33:54.600000', 'ask_price1': 2470.0, 'bid_price1': 2469.0,
                    'last_price': 2470.0, 'price_tick': 1.0, 'volume_multiple': 10.0, 'ins_class': 'FUTURE',
                    'instrument_id': 'CZCE.MA105', 'margin': 1718.5, 'commission': 2.0,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "23:00:00"]]}
                }
            }
        })
        # 买开 10 手
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_buy_open',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'BUY',
            'offset': 'OPEN',
            'volume': 10,
            'price_type': 'LIMIT',
            'limit_price': 2470.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_future(self):
        self.trade_future_1()
        self.trade_future_2()
        self.trade_future_3()
        self.trade_future_4()
        self.trade_future_5()
        self.trade_future_6()
        self.trade_future_7()
        self.trade_future_8()
        self.trade_future_9()
        self.trade_future_10()
        self.trade_future_11()

    def trade_future_1(self):
        """卖平（15手数不足）"""
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'SELL',
            'offset': 'CLOSE',
            'volume': 15,
            'price_type': 'LIMIT',
            'limit_price': 2470.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 2470.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'volume_orign': 15,
             'volume_left': 15, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 2470.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'volume_orign': 15,
             'volume_left': 15, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '平仓手数不足', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_2(self):
        """更新价格"""
        diffs, orders_events = self.sim_trade.update_quotes("CZCE.MA105", {
            'quotes': {
                'CZCE.MA105': {
                    'datetime': '2021-03-16 10:05:25.000001',
                    'ask_price1': 2469.0, 'bid_price1': 2467.0, 'last_price': 2468.0,
                }
            }
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999780.0,
             'available': 982595.0, 'float_profit': -200.0, 'position_profit': -200.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 17185.0, 'frozen_commission': 0.0, 'commission': 20.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.017188781531937026,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions["CZCE.MA105"],
            {'exchange_id': 'CZCE', 'instrument_id': 'MA105', 'pos_long_his': 0, 'pos_long_today': 10,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 10, 'volume_long_his': 0, 'volume_long': 10,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 2470.0,
             'open_price_short': float('nan'),
             'open_cost_long': 247000.0, 'open_cost_short': 0.0, 'position_price_long': 2470.0,
             'position_price_short': float('nan'), 'position_cost_long': 247000.0, 'position_cost_short': 0.0,
             'float_profit_long': -200.0, 'float_profit_short': 0.0, 'float_profit': -200.0,
             'position_profit_long': -200.0, 'position_profit_short': 0.0, 'position_profit': -200.0,
             'margin_long': 17185.0, 'margin_short': 0.0, 'margin': 17185.0, 'last_price': 2468.0,
             'underlying_last_price': float('nan'), 'market_value_long': 0.0, 'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 1718.5}
        )

    def trade_future_3(self):
        """结算"""
        
        diffs, orders_events, trade_log = self.sim_trade.settle()
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999780.0, 'static_balance': 999780.0, 'balance': 999780.0,
             'available': 982595.0, 'float_profit': -200.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 17185.0, 'frozen_commission': 0.0, 'commission': 0.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.017188781531937026,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions["CZCE.MA105"],
            {'exchange_id': 'CZCE', 'instrument_id': 'MA105', 'pos_long_his': 10, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 10, 'volume_long': 10,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 2470.0,
             'open_price_short': float('nan'),
             'open_cost_long': 247000.0, 'open_cost_short': 0.0, 'position_price_long': 2468.0,
             'position_price_short': 2468.0, 'position_cost_long': 246800.0, 'position_cost_short': 0.0,
             'float_profit_long': -200.0, 'float_profit_short': 0.0, 'float_profit': -200.0, 'position_profit_long': 0,
             'position_profit_short': 0.0, 'position_profit': 0, 'margin_long': 17185.0, 'margin_short': 0.0,
             'margin': 17185.0, 'last_price': 2468.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 1718.5}
        )

    def trade_future_4(self):
        """平仓（10 IOC）"""
        
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_pending_sell_close',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'SELL',
            'offset': 'CLOSE',
            'volume': 10,
            'price_type': 'LIMIT',
            'limit_price': 2470.0,
            'time_condition': 'IOC',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 4)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999780.0, 'static_balance': 999780.0, 'balance': 999780.0,
             'available': 982595.0, 'float_profit': -200.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 17185.0, 'frozen_commission': 0.0, 'commission': 0.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.017188781531937026,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions["CZCE.MA105"],
            {'exchange_id': 'CZCE', 'instrument_id': 'MA105', 'pos_long_his': 10, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 10, 'volume_long': 10,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 2470.0,
             'open_price_short': float('nan'),
             'open_cost_long': 247000.0, 'open_cost_short': 0.0, 'position_price_long': 2468.0,
             'position_price_short': 2468.0, 'position_cost_long': 246800.0, 'position_cost_short': 0.0,
             'float_profit_long': -200.0, 'float_profit_short': 0.0, 'float_profit': -200.0, 'position_profit_long': 0,
             'position_profit_short': 0.0, 'position_profit': 0, 'margin_long': 17185.0, 'margin_short': 0.0,
             'margin': 17185.0, 'last_price': 2468.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 1718.5}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_pending_sell_close', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 2470.0, 'time_condition': 'IOC', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_pending_sell_close', 'volume_orign': 10, 'volume_left': 10,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_pending_sell_close', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 2470.0, 'time_condition': 'IOC', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_pending_sell_close', 'volume_orign': 10, 'volume_left': 10,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '已撤单报单已提交', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_5(self):
        """平仓（5挂单）"""
        
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_pending_sell_close',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'SELL',
            'offset': 'CLOSE',
            'volume': 5,
            'price_type': 'LIMIT',
            'limit_price': 2470.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999780.0, 'static_balance': 999780.0, 'balance': 999780.0,
             'available': 982595.0, 'float_profit': -200.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 17185.0, 'frozen_commission': 0.0, 'commission': 0.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.017188781531937026,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions["CZCE.MA105"],
            {'exchange_id': 'CZCE', 'instrument_id': 'MA105', 'pos_long_his': 10, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 10, 'volume_long': 10,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 5, 'volume_long_frozen': 5,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 2470.0,
             'open_price_short': float('nan'),
             'open_cost_long': 247000.0, 'open_cost_short': 0.0, 'position_price_long': 2468.0,
             'position_price_short': 2468.0, 'position_cost_long': 246800.0, 'position_cost_short': 0.0,
             'float_profit_long': -200.0, 'float_profit_short': 0.0, 'float_profit': -200.0, 'position_profit_long': 0,
             'position_profit_short': 0.0, 'position_profit': 0, 'margin_long': 17185.0, 'margin_short': 0.0,
             'margin': 17185.0, 'last_price': 2468.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 1718.5}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_pending_sell_close', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 2470.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_pending_sell_close', 'volume_orign': 5, 'volume_left': 5,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_6(self):
        """平仓（2成交）"""
        
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'SELL',
            'offset': 'CLOSE',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 2467.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999780.0, 'static_balance': 999780.0, 'balance': 999756.0,
             'available': 986008.0, 'float_profit': -160.0, 'position_profit': 0.0, 'close_profit': -20.0,
             'frozen_margin': 0.0, 'margin': 13748.0, 'frozen_commission': 0.0, 'commission': 4.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.01375135533070069,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions["CZCE.MA105"],
            {'exchange_id': 'CZCE', 'instrument_id': 'MA105', 'pos_long_his': 8, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 8, 'volume_long': 8,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 5, 'volume_long_frozen': 5,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 2470.0,
             'open_price_short': float('nan'),
             'open_cost_long': 197600.0, 'open_cost_short': 0.0, 'position_price_long': 2468.0,
             'position_price_short': float('nan'), 'position_cost_long': 197440.0, 'position_cost_short': 0.0,
             'float_profit_long': -160.0, 'float_profit_short': 0.0, 'float_profit': -160.0, 'position_profit_long': 0,
             'position_profit_short': 0.0, 'position_profit': 0, 'margin_long': 13748.0, 'margin_short': 0.0,
             'margin': 13748.0, 'last_price': 2468.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 1718.5}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 2467.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 2467.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'volume_orign': 2, 'volume_left': 0,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_7(self):
        """加仓 10"""
        
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_buy_open1',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'BUY',
            'offset': 'OPEN',
            'volume': 10,
            'price_type': 'LIMIT',
            'limit_price': 2470.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999780.0, 'static_balance': 999780.0, 'balance': 999536.0,
             'available': 968603.0, 'float_profit': -360.0, 'position_profit': -200.0, 'close_profit': -20.0,
             'frozen_margin': 0.0, 'margin': 30933.0, 'frozen_commission': 0.0, 'commission': 24.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.030947359574842726,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['CZCE.MA105'],
            {'exchange_id': 'CZCE', 'instrument_id': 'MA105', 'pos_long_his': 8, 'pos_long_today': 10,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 10, 'volume_long_his': 8, 'volume_long': 18,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 5, 'volume_long_frozen': 5,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 2470.0,
             'open_price_short': float('nan'),
             'open_cost_long': 444600.0, 'open_cost_short': 0.0, 'position_price_long': 2469.111111111111,
             'position_price_short': float('nan'), 'position_cost_long': 444440.0, 'position_cost_short': 0.0,
             'float_profit_long': -360.0, 'float_profit_short': 0.0, 'float_profit': -360.0,
             'position_profit_long': -200.0, 'position_profit_short': 0.0, 'position_profit': -200.0,
             'margin_long': 30933.0, 'margin_short': 0.0, 'margin': 30933.0, 'last_price': 2468.0,
             'underlying_last_price': float('nan'), 'market_value_long': 0.0, 'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 1718.5}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_open1', 'exchange_id': 'CZCE', 'instrument_id': 'MA105',
             'direction': 'BUY', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 2470.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_buy_open1',
             'volume_orign': 10, 'volume_left': 10, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功',
             'status': 'ALIVE', 'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_open1', 'exchange_id': 'CZCE', 'instrument_id': 'MA105',
             'direction': 'BUY', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 2470.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_buy_open1',
             'volume_orign': 10, 'volume_left': 0, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交',
             'status': 'FINISHED', 'insert_date_time': 1615959234600000000}
        )

    def trade_future_8(self):
        """平仓 5"""
        
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_sell_close1',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'SELL',
            'offset': 'CLOSE',
            'volume': 5,
            'price_type': 'LIMIT',
            'limit_price': 2467.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999780.0, 'static_balance': 999780.0, 'balance': 999476.0,
             'available': 977135.5, 'float_profit': -260.0, 'position_profit': -144.44444444444446,
             'close_profit': -125.55555555554292, 'frozen_margin': 0.0, 'margin': 22340.5, 'frozen_commission': 0.0,
             'commission': 34.0, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0,
             'risk_ratio': 0.022352212559381114, 'market_value': 0.0, 'ctp_balance': float('nan'),
             'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['CZCE.MA105'],
            {'exchange_id': 'CZCE', 'instrument_id': 'MA105', 'pos_long_his': 3, 'pos_long_today': 10,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 10, 'volume_long_his': 3, 'volume_long': 13,
             'volume_long_frozen_today': 2, 'volume_long_frozen_his': 3, 'volume_long_frozen': 5,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 2470.0,
             'open_price_short': float('nan'),
             'open_cost_long': 321100.0, 'open_cost_short': 0.0, 'position_price_long': 2469.111111111111,
             'position_price_short': float('nan'), 'position_cost_long': 320984.44444444444, 'position_cost_short': 0.0,
             'float_profit_long': -260.0, 'float_profit_short': 0.0, 'float_profit': -260.0,
             'position_profit_long': -144.44444444444446, 'position_profit_short': 0.0,
             'position_profit': -144.44444444444446, 'margin_long': 22340.5, 'margin_short': 0.0, 'margin': 22340.5,
             'last_price': 2468.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 1718.5}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_close1', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105',
             'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 2467.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_sell_close1',
             'volume_orign': 5, 'volume_left': 5, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功',
             'status': 'ALIVE', 'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_close1', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105',
             'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 2467.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_sell_close1',
             'volume_orign': 5, 'volume_left': 0, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交',
             'status': 'FINISHED', 'insert_date_time': 1615959234600000000}
        )

    def trade_future_9(self):
        """平仓 5"""
        
        diffs, orders_events = self.sim_trade.insert_order("CZCE.MA105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_sell_close2',
            'exchange_id': 'CZCE',
            'instrument_id': 'MA105',
            'direction': 'SELL',
            'offset': 'CLOSE',
            'volume': 5,
            'price_type': 'LIMIT',
            'limit_price': 2467.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999780.0, 'static_balance': 999780.0, 'balance': 999416.0,
             'available': 985668.0, 'float_profit': -160.0, 'position_profit': -88.88888888888889,
             'close_profit': -231.11111111108585, 'frozen_margin': 0.0, 'margin': 13748.0, 'frozen_commission': 0.0,
             'commission': 44.0, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0,
             'risk_ratio': 0.013756033523577769, 'market_value': 0.0, 'ctp_balance': float('nan'),
             'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['CZCE.MA105'],
            {'exchange_id': 'CZCE', 'instrument_id': 'MA105', 'pos_long_his': 0, 'pos_long_today': 8,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 8, 'volume_long_his': 0, 'volume_long': 8,
             'volume_long_frozen_today': 5, 'volume_long_frozen_his': 0, 'volume_long_frozen': 5,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 2470.0,
             'open_price_short': float('nan'),
             'open_cost_long': 197600.0, 'open_cost_short': 0.0, 'position_price_long': 2469.111111111111,
             'position_price_short': float('nan'), 'position_cost_long': 197528.88888888888, 'position_cost_short': 0.0,
             'float_profit_long': -160.0, 'float_profit_short': 0.0, 'float_profit': -160.0,
             'position_profit_long': -88.88888888888889, 'position_profit_short': 0.0,
             'position_profit': -88.88888888888889, 'margin_long': 13748.0, 'margin_short': 0.0, 'margin': 13748.0,
             'last_price': 2468.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 1718.5}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_close2', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105',
             'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 2467.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_sell_close2',
             'volume_orign': 5, 'volume_left': 5, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功',
             'status': 'ALIVE', 'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_close2', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105',
             'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 2467.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_sell_close2',
             'volume_orign': 5, 'volume_left': 0, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交',
             'status': 'FINISHED', 'insert_date_time': 1615959234600000000}
        )

    def trade_future_10(self):
        """撤单(已成交的)"""
        diffs, orders_events = self.sim_trade.cancel_order("CZCE.MA105", {
            "aid": "cancel_order",
            "order_id": "PYSDK_insert_42de71a44009a3420164af39b87a7870"
        })
        self.assertEqual(len(diffs), 0)
        self.assertEqual(len(orders_events), 0)

    def trade_future_11(self):
        """撤单"""
        diffs, orders_events = self.sim_trade.cancel_order("CZCE.MA105", {
            "aid": "cancel_order",
            "order_id": "PYSDK_insert_pending_sell_close"
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999780.0, 'static_balance': 999780.0, 'balance': 999416.0,
             'available': 985668.0, 'float_profit': -160.0, 'position_profit': -88.88888888888889,
             'close_profit': -231.11111111108585, 'frozen_margin': 0.0, 'margin': 13748.0, 'frozen_commission': 0.0,
             'commission': 44.0, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0,
             'risk_ratio': 0.013756033523577769, 'market_value': 0.0, 'ctp_balance': float('nan'),
             'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['CZCE.MA105'],
            {'exchange_id': 'CZCE', 'instrument_id': 'MA105', 'pos_long_his': 0, 'pos_long_today': 8,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 8, 'volume_long_his': 0, 'volume_long': 8,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 2470.0,
             'open_price_short': float('nan'),
             'open_cost_long': 197600.0, 'open_cost_short': 0.0, 'position_price_long': 2469.111111111111,
             'position_price_short': float('nan'), 'position_cost_long': 197528.88888888888, 'position_cost_short': 0.0,
             'float_profit_long': -160.0, 'float_profit_short': 0.0, 'float_profit': -160.0,
             'position_profit_long': -88.88888888888889, 'position_profit_short': 0.0,
             'position_profit': -88.88888888888889, 'margin_long': 13748.0, 'margin_short': 0.0, 'margin': 13748.0,
             'last_price': 2468.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 1718.5}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_pending_sell_close', 'exchange_id': 'CZCE',
             'instrument_id': 'MA105', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 2470.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_pending_sell_close', 'volume_orign': 5, 'volume_left': 5,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '已撤单', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )


class TestSimTradeFuture7(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期货交易 SHFE （买开 10 手）
    限价单 卖平/卖平今/买平/买平今 (平仓手数不足)
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        self.sim_trade.update_quotes("SHFE.ni2106", {
            'quotes': {
                'SHFE.ni2106': {
                    'datetime': '2021-03-17 13:33:54.600000', 'ask_price1': 120730.0, 'bid_price1': 120720.0,
                    'last_price': 120720.0, 'price_tick': 10.0, 'volume_multiple': 1.0, 'ins_class': 'FUTURE',
                    'instrument_id': 'SHFE.ni2106', 'margin': 9708.8, 'commission': 6.0,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "25:00:00"]]
                    }
                }
            }
        })

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_future_shfe_1(self):
        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_sell_close',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'SELL',
            'offset': 'CLOSE',
            'volume': 3,
            'price_type': 'LIMIT',
            'limit_price': 120730.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_close', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106',
             'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 120730.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_sell_close',
             'volume_orign': 3,
             'volume_left': 3, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_close', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106',
             'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 120730.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_sell_close',
             'volume_orign': 3,
             'volume_left': 3, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '平昨仓手数不足', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def test_trade_future_shfe_2(self):
        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_sell_closetoday',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'SELL',
            'offset': 'CLOSETODAY',
            'volume': 3,
            'price_type': 'LIMIT',
            'limit_price': 120730.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 2)
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_closetoday', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106',
             'direction': 'SELL', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT', 'limit_price': 120730.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_sell_closetoday',
             'volume_orign': 3,
             'volume_left': 3, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_closetoday', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106',
             'direction': 'SELL', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT', 'limit_price': 120730.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_sell_closetoday',
             'volume_orign': 3,
             'volume_left': 3, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '平今仓手数不足', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def test_trade_future_shfe_3(self):
        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_buy_close',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'BUY',
            'offset': 'CLOSE',
            'volume': 3,
            'price_type': 'LIMIT',
            'limit_price': 120730.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 2)
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close', 'exchange_id': 'SHFE', 'instrument_id': 'ni2106',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 120730.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_buy_close',
             'volume_orign': 3,
             'volume_left': 3, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close', 'exchange_id': 'SHFE', 'instrument_id': 'ni2106',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 120730.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_buy_close',
             'volume_orign': 3,
             'volume_left': 3, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '平昨仓手数不足', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def test_trade_future_shfe_4(self):
        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_buy_closetoday',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'BUY',
            'offset': 'CLOSETODAY',
            'volume': 3,
            'price_type': 'LIMIT',
            'limit_price': 120730.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 2)
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_closetoday', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106',
             'direction': 'BUY', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT', 'limit_price': 120730.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_buy_closetoday',
             'volume_orign': 3,
             'volume_left': 3, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_closetoday', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106',
             'direction': 'BUY', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT', 'limit_price': 120730.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_buy_closetoday',
             'volume_orign': 3,
             'volume_left': 3, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '平今仓手数不足', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )


class TestSimTradeFuture8(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期货交易 SHFE
    1. 买开 10
    2. 卖平今 2
    3. 卖开 10
    4. 买平今 3 (多今 8 ｜ 空今 7)
    5. 买平今 2 挂单
    6. 卖平今 2 挂单
    7. 撤单
    8. 撤单
    9. 行情更新
    10. 结算 -> (多 8,0 ｜ 空 7,0)
    11. 卖平昨 2手 IOC 立即撤单
    12. 买平昨 2手 IOC 立即撤单
    13. 买平昨 2手 IOC 成交 (多 8,0 ｜ 空 5,0)
    14. 卖平昨 2手 IOC 成交 (多 6,0 ｜ 空 5,0)
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        self.sim_trade.update_quotes("SHFE.ni2106", {
            'quotes': {
                'SHFE.ni2106': {
                    'datetime': '2021-03-17 13:33:54.600000', 'ask_price1': 120730.0, 'bid_price1': 120720.0,
                    'last_price': 120720.0, 'price_tick': 10.0, 'volume_multiple': 1.0, 'ins_class': 'FUTURE',
                    'instrument_id': 'SHFE.ni2106', 'margin': 9708.8, 'commission': 6.0,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "25:00:00"]]
                    }
                }
            }
        })

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_future(self):
        self.trade_future_1()
        self.trade_future_2()
        self.trade_future_3()
        self.trade_future_4()
        self.trade_future_5()
        self.trade_future_6()
        self.trade_future_7()
        self.trade_future_8()
        self.trade_future_9()
        self.trade_future_10()
        self.trade_future_11()
        self.trade_future_12()
        self.trade_future_13()
        self.trade_future_14()

    def trade_future_1(self):
        """买开 10"""
        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_buy_open',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'BUY',
            'offset': 'OPEN',
            'volume': 10,
            'price_type': 'LIMIT',
            'limit_price': 120730.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999840.0,
             'available': 902752.0, 'float_profit': -100.0, 'position_profit': -100.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 97088.0, 'frozen_commission': 0.0, 'commission': 60.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.09710353656585054,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 0, 'pos_long_today': 10,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 10, 'volume_long_his': 0, 'volume_long': 10,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 120730.0,
             'open_price_short': float('nan'), 'open_cost_long': 1207300.0, 'open_cost_short': 0.0,
             'position_price_long': 120730.0, 'position_price_short': float('nan'), 'position_cost_long': 1207300.0,
             'position_cost_short': 0.0, 'float_profit_long': -100.0, 'float_profit_short': 0.0, 'float_profit': -100.0,
             'position_profit_long': -100.0, 'position_profit_short': 0.0, 'position_profit': -100.0,
             'margin_long': 97088.0, 'margin_short': 0.0, 'margin': 97088.0, 'last_price': 120720.0,
             'underlying_last_price': float('nan'), 'market_value_long': 0.0, 'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )
        self.assertEqual(
            trades,
            {'PYSDK_insert_buy_open|10': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_open',
                                          'trade_id': 'PYSDK_insert_buy_open|10',
                                          'exchange_trade_id': 'PYSDK_insert_buy_open|10', 'exchange_id': 'SHFE',
                                          'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'OPEN',
                                          'price': 120730.0, 'volume': 10, 'trade_date_time': 1615959234600000000,
                                          'commission': 60.0}}
        )

        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_open', 'exchange_id': 'SHFE', 'instrument_id': 'ni2106',
             'direction': 'BUY', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 120730.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_buy_open',
             'volume_orign': 10, 'volume_left': 10, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功',
             'status': 'ALIVE', 'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_open', 'exchange_id': 'SHFE', 'instrument_id': 'ni2106',
             'direction': 'BUY', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 120730.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_buy_open',
             'volume_orign': 10, 'volume_left': 0, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交',
             'status': 'FINISHED', 'insert_date_time': 1615959234600000000}
        )

    def trade_future_2(self):
        """卖平今 2"""
        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_sell_closetoday',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'SELL',
            'offset': 'CLOSETODAY',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 120720.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999828.0,
             'available': 922157.6, 'float_profit': -80.0, 'position_profit': -80.0, 'close_profit': -20.0,
             'frozen_margin': 0.0, 'margin': 77670.4, 'frozen_commission': 0.0, 'commission': 72.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0776837616069964,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 0, 'pos_long_today': 8,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 8, 'volume_long_his': 0, 'volume_long': 8,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 120730.0,
             'open_price_short': float('nan'), 'open_cost_long': 965840.0, 'open_cost_short': 0.0,
             'position_price_long': 120730.0, 'position_price_short': float('nan'), 'position_cost_long': 965840.0,
             'position_cost_short': 0.0, 'float_profit_long': -80.0, 'float_profit_short': 0.0, 'float_profit': -80.0,
             'position_profit_long': -80.0, 'position_profit_short': 0.0, 'position_profit': -80.0,
             'margin_long': 77670.4, 'margin_short': 0.0, 'margin': 77670.4, 'last_price': 120720.0,
             'underlying_last_price': float('nan'), 'market_value_long': 0.0, 'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )
        self.assertEqual(
            trades,
            {'PYSDK_insert_buy_open|10': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_open',
                                          'trade_id': 'PYSDK_insert_buy_open|10',
                                          'exchange_trade_id': 'PYSDK_insert_buy_open|10', 'exchange_id': 'SHFE',
                                          'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'OPEN',
                                          'price': 120730.0, 'volume': 10, 'trade_date_time': 1615959234600000000,
                                          'commission': 60.0},
             'PYSDK_insert_sell_closetoday|2': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_closetoday',
                                                'trade_id': 'PYSDK_insert_sell_closetoday|2',
                                                'exchange_trade_id': 'PYSDK_insert_sell_closetoday|2',
                                                'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'direction': 'SELL',
                                                'offset': 'CLOSETODAY', 'price': 120720.0, 'volume': 2,
                                                'trade_date_time': 1615959234600000000, 'commission': 12.0}}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_closetoday', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT',
             'limit_price': 120720.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_sell_closetoday', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_closetoday', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT',
             'limit_price': 120720.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_sell_closetoday', 'volume_orign': 2, 'volume_left': 0,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_3(self):
        """卖开 10"""
        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_sell_open',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'SELL',
            'offset': 'OPEN',
            'volume': 10,
            'price_type': 'LIMIT',
            'limit_price': 120720.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999768.0,
             'available': 825009.6, 'float_profit': -80.0, 'position_profit': -80.0, 'close_profit': -20.0,
             'frozen_margin': 0.0, 'margin': 174758.4, 'frozen_commission': 0.0, 'commission': 132.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.17479895335717885,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 0, 'pos_long_today': 8,
             'pos_short_his': 0, 'pos_short_today': 10, 'volume_long_today': 8, 'volume_long_his': 0, 'volume_long': 8,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 10, 'volume_short_his': 0, 'volume_short': 10, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 120730.0,
             'open_price_short': 120720.0, 'open_cost_long': 965840.0, 'open_cost_short': 1207200.0,
             'position_price_long': 120730.0, 'position_price_short': 120720.0, 'position_cost_long': 965840.0,
             'position_cost_short': 1207200.0, 'float_profit_long': -80.0, 'float_profit_short': 0.0,
             'float_profit': -80.0, 'position_profit_long': -80.0, 'position_profit_short': 0.0,
             'position_profit': -80.0, 'margin_long': 77670.4, 'margin_short': 97088.0, 'margin': 174758.4,
             'last_price': 120720.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )
        self.assertEqual(
            trades,
            {'PYSDK_insert_buy_open|10': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_open',
                                          'trade_id': 'PYSDK_insert_buy_open|10',
                                          'exchange_trade_id': 'PYSDK_insert_buy_open|10', 'exchange_id': 'SHFE',
                                          'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'OPEN',
                                          'price': 120730.0, 'volume': 10, 'trade_date_time': 1615959234600000000,
                                          'commission': 60.0},
             'PYSDK_insert_sell_closetoday|2': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_closetoday',
                                                'trade_id': 'PYSDK_insert_sell_closetoday|2',
                                                'exchange_trade_id': 'PYSDK_insert_sell_closetoday|2',
                                                'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'direction': 'SELL',
                                                'offset': 'CLOSETODAY', 'price': 120720.0, 'volume': 2,
                                                'trade_date_time': 1615959234600000000, 'commission': 12.0},
             'PYSDK_insert_sell_open|10': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_open',
                                           'trade_id': 'PYSDK_insert_sell_open|10',
                                           'exchange_trade_id': 'PYSDK_insert_sell_open|10', 'exchange_id': 'SHFE',
                                           'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'OPEN',
                                           'price': 120720.0, 'volume': 10, 'trade_date_time': 1615959234600000000,
                                           'commission': 60.0}}
        )

        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_open', 'exchange_id': 'SHFE', 'instrument_id': 'ni2106',
             'direction': 'SELL', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 120720.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_sell_open',
             'volume_orign': 10, 'volume_left': 10, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功',
             'status': 'ALIVE', 'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_open', 'exchange_id': 'SHFE', 'instrument_id': 'ni2106',
             'direction': 'SELL', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 120720.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_sell_open',
             'volume_orign': 10, 'volume_left': 0, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交',
             'status': 'FINISHED', 'insert_date_time': 1615959234600000000}
        )

    def trade_future_4(self):
        """买平今 3"""
        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_buy_closetoday',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'BUY',
            'offset': 'CLOSETODAY',
            'volume': 3,
            'price_type': 'LIMIT',
            'limit_price': 120730.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999720.0,
             'available': 854088.0, 'float_profit': -80.0, 'position_profit': -80.0, 'close_profit': -50.0,
             'frozen_margin': 0.0, 'margin': 145632.0, 'frozen_commission': 0.0, 'commission': 150.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.1456727883807466,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 0, 'pos_long_today': 8,
             'pos_short_his': 0, 'pos_short_today': 7, 'volume_long_today': 8, 'volume_long_his': 0, 'volume_long': 8,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 7, 'volume_short_his': 0, 'volume_short': 7, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 120730.0,
             'open_price_short': 120720.0, 'open_cost_long': 965840.0, 'open_cost_short': 845040.0,
             'position_price_long': 120730.0, 'position_price_short': 120720.0, 'position_cost_long': 965840.0,
             'position_cost_short': 845040.0, 'float_profit_long': -80.0, 'float_profit_short': 0.0,
             'float_profit': -80.0, 'position_profit_long': -80.0, 'position_profit_short': 0.0,
             'position_profit': -80.0, 'margin_long': 77670.4, 'margin_short': 67961.6, 'margin': 145632.0,
             'last_price': 120720.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )
        self.assertEqual(
            trades,
            {'PYSDK_insert_buy_open|10': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_open',
                                          'trade_id': 'PYSDK_insert_buy_open|10',
                                          'exchange_trade_id': 'PYSDK_insert_buy_open|10', 'exchange_id': 'SHFE',
                                          'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'OPEN',
                                          'price': 120730.0, 'volume': 10, 'trade_date_time': 1615959234600000000,
                                          'commission': 60.0},
             'PYSDK_insert_sell_closetoday|2': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_closetoday',
                                                'trade_id': 'PYSDK_insert_sell_closetoday|2',
                                                'exchange_trade_id': 'PYSDK_insert_sell_closetoday|2',
                                                'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'direction': 'SELL',
                                                'offset': 'CLOSETODAY', 'price': 120720.0, 'volume': 2,
                                                'trade_date_time': 1615959234600000000, 'commission': 12.0},
             'PYSDK_insert_sell_open|10': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_open',
                                           'trade_id': 'PYSDK_insert_sell_open|10',
                                           'exchange_trade_id': 'PYSDK_insert_sell_open|10', 'exchange_id': 'SHFE',
                                           'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'OPEN',
                                           'price': 120720.0, 'volume': 10, 'trade_date_time': 1615959234600000000,
                                           'commission': 60.0},
             'PYSDK_insert_buy_closetoday|3': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_closetoday',
                                               'trade_id': 'PYSDK_insert_buy_closetoday|3',
                                               'exchange_trade_id': 'PYSDK_insert_buy_closetoday|3',
                                               'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'direction': 'BUY',
                                               'offset': 'CLOSETODAY', 'price': 120730.0, 'volume': 3,
                                               'trade_date_time': 1615959234600000000, 'commission': 18.0}}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_closetoday', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT',
             'limit_price': 120730.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_buy_closetoday', 'volume_orign': 3, 'volume_left': 3,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_closetoday', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT',
             'limit_price': 120730.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_buy_closetoday', 'volume_orign': 3, 'volume_left': 0,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_5(self):
        """买平今 2 挂单"""

        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_buy_closetoday1',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'BUY',
            'offset': 'CLOSETODAY',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 120720.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999720.0,
             'available': 854088.0, 'float_profit': -80.0, 'position_profit': -80.0, 'close_profit': -50.0,
             'frozen_margin': 0.0, 'margin': 145632.0, 'frozen_commission': 0.0, 'commission': 150.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.1456727883807466,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 0, 'pos_long_today': 8,
             'pos_short_his': 0, 'pos_short_today': 7, 'volume_long_today': 8, 'volume_long_his': 0, 'volume_long': 8,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 7, 'volume_short_his': 0, 'volume_short': 7, 'volume_short_frozen_today': 2,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 2, 'open_price_long': 120730.0,
             'open_price_short': 120720.0, 'open_cost_long': 965840.0, 'open_cost_short': 845040.0,
             'position_price_long': 120730.0, 'position_price_short': 120720.0, 'position_cost_long': 965840.0,
             'position_cost_short': 845040.0, 'float_profit_long': -80.0, 'float_profit_short': 0.0,
             'float_profit': -80.0, 'position_profit_long': -80.0, 'position_profit_short': 0.0,
             'position_profit': -80.0, 'margin_long': 77670.4, 'margin_short': 67961.6, 'margin': 145632.0,
             'last_price': 120720.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_closetoday1', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT',
             'limit_price': 120720.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_buy_closetoday1', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_6(self):
        """卖平今 2 挂单"""

        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_sell_closetoday1',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'SELL',
            'offset': 'CLOSETODAY',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 120740.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999720.0,
             'available': 854088.0, 'float_profit': -80.0, 'position_profit': -80.0, 'close_profit': -50.0,
             'frozen_margin': 0.0, 'margin': 145632.0, 'frozen_commission': 0.0, 'commission': 150.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.1456727883807466,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 0, 'pos_long_today': 8,
             'pos_short_his': 0, 'pos_short_today': 7, 'volume_long_today': 8, 'volume_long_his': 0, 'volume_long': 8,
             'volume_long_frozen_today': 2, 'volume_long_frozen_his': 0, 'volume_long_frozen': 2,
             'volume_short_today': 7, 'volume_short_his': 0, 'volume_short': 7, 'volume_short_frozen_today': 2,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 2, 'open_price_long': 120730.0,
             'open_price_short': 120720.0, 'open_cost_long': 965840.0, 'open_cost_short': 845040.0,
             'position_price_long': 120730.0, 'position_price_short': 120720.0, 'position_cost_long': 965840.0,
             'position_cost_short': 845040.0, 'float_profit_long': -80.0, 'float_profit_short': 0.0,
             'float_profit': -80.0, 'position_profit_long': -80.0, 'position_profit_short': 0.0,
             'position_profit': -80.0, 'margin_long': 77670.4, 'margin_short': 67961.6, 'margin': 145632.0,
             'last_price': 120720.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_closetoday1', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT',
             'limit_price': 120740.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_sell_closetoday1', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_7(self):
        """撤单"""

        diffs, orders_events = self.sim_trade.cancel_order("SHFE.ni2106", {
            "aid": "cancel_order",
            "order_id": "PYSDK_insert_sell_closetoday1"
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_closetoday1', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT',
             'limit_price': 120740.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_sell_closetoday1', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '已撤单', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_8(self):
        """撤单"""

        diffs, orders_events = self.sim_trade.cancel_order("SHFE.ni2106", {
            "aid": "cancel_order",
            "order_id": "PYSDK_insert_buy_closetoday1"
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999720.0,
             'available': 854088.0, 'float_profit': -80.0, 'position_profit': -80.0, 'close_profit': -50.0,
             'frozen_margin': 0.0, 'margin': 145632.0, 'frozen_commission': 0.0, 'commission': 150.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.1456727883807466,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 0, 'pos_long_today': 8,
             'pos_short_his': 0, 'pos_short_today': 7, 'volume_long_today': 8, 'volume_long_his': 0, 'volume_long': 8,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 7, 'volume_short_his': 0, 'volume_short': 7, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 120730.0,
             'open_price_short': 120720.0, 'open_cost_long': 965840.0, 'open_cost_short': 845040.0,
             'position_price_long': 120730.0, 'position_price_short': 120720.0, 'position_cost_long': 965840.0,
             'position_cost_short': 845040.0, 'float_profit_long': -80.0, 'float_profit_short': 0.0,
             'float_profit': -80.0, 'position_profit_long': -80.0, 'position_profit_short': 0.0,
             'position_profit': -80.0, 'margin_long': 77670.4, 'margin_short': 67961.6, 'margin': 145632.0,
             'last_price': 120720.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_closetoday1', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'CLOSETODAY', 'price_type': 'LIMIT',
             'limit_price': 120720.0, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_buy_closetoday1', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '已撤单', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_9(self):
        """行情更新"""

        diffs, orders_events = self.sim_trade.update_quotes(
            "SHFE.ni2106", {
                "quotes": {
                    "SHFE.ni2106": {
                        'datetime': '2021-03-17 14:59:59.500000', 'ask_price1': 120700.0, 'bid_price1': 120690.0,
                        'last_price': 120690.0,
                    }
                }
            })
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

    def trade_future_10(self):
        """结算"""

        diffs, orders_events, trade_log = self.sim_trade.settle()
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999690.0, 'static_balance': 999690.0, 'balance': 999690.0,
             'available': 854058.0, 'float_profit': -110.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 145632.0, 'frozen_commission': 0.0, 'commission': 0.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.14567715991957506,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 8, 'pos_long_today': 0,
             'pos_short_his': 7, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 8, 'volume_long': 8,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 7, 'volume_short': 7, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 120730.0,
             'open_price_short': 120720.0, 'open_cost_long': 965840.0, 'open_cost_short': 845040.0,
             'position_price_long': 120690.0, 'position_price_short': 120690.0, 'position_cost_long': 965520.0,
             'position_cost_short': 844830.0, 'float_profit_long': -320.0, 'float_profit_short': 210.0,
             'float_profit': -110.0, 'position_profit_long': 0, 'position_profit_short': 0.0, 'position_profit': 0,
             'margin_long': 77670.4, 'margin_short': 67961.59999999999, 'margin': 145632.0, 'last_price': 120690.0,
             'underlying_last_price': float('nan'), 'market_value_long': 0.0, 'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )

    def trade_future_11(self):
        """卖平昨 2手 IOC 立即撤单"""

        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_sell_close_fok',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'SELL',
            'offset': 'CLOSE',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 120740.0,
            'time_condition': 'IOC',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 4)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999690.0, 'static_balance': 999690.0, 'balance': 999690.0,
             'available': 854058.0, 'float_profit': -110.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 145632.0, 'frozen_commission': 0.0, 'commission': 0.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.14567715991957506,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 8, 'pos_long_today': 0,
             'pos_short_his': 7, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 8, 'volume_long': 8,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 7, 'volume_short': 7, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 120730.0,
             'open_price_short': 120720.0, 'open_cost_long': 965840.0, 'open_cost_short': 845040.0,
             'position_price_long': 120690.0, 'position_price_short': 120690.0, 'position_cost_long': 965520.0,
             'position_cost_short': 844830.0, 'float_profit_long': -320.0, 'float_profit_short': 210.0,
             'float_profit': -110.0, 'position_profit_long': 0, 'position_profit_short': 0.0, 'position_profit': 0,
             'margin_long': 77670.4, 'margin_short': 67961.59999999999, 'margin': 145632.0, 'last_price': 120690.0,
             'underlying_last_price': float('nan'), 'market_value_long': 0.0, 'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_close_fok', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 120740.0, 'time_condition': 'IOC', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_sell_close_fok', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615964399500000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_close_fok', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 120740.0, 'time_condition': 'IOC', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_sell_close_fok', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '已撤单报单已提交', 'status': 'FINISHED',
             'insert_date_time': 1615964399500000000}
        )

    def trade_future_12(self):
        """买平昨 2手 IOC 立即撤单"""


        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_buy_close_fok',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'BUY',
            'offset': 'CLOSE',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 120640.0,
            'time_condition': 'IOC',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 4)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999690.0, 'static_balance': 999690.0, 'balance': 999690.0,
             'available': 854058.0, 'float_profit': -110.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 145632.0, 'frozen_commission': 0.0, 'commission': 0.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.14567715991957506,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 8, 'pos_long_today': 0,
             'pos_short_his': 7, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 8, 'volume_long': 8,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 7, 'volume_short': 7, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 120730.0,
             'open_price_short': 120720.0, 'open_cost_long': 965840.0, 'open_cost_short': 845040.0,
             'position_price_long': 120690.0, 'position_price_short': 120690.0, 'position_cost_long': 965520.0,
             'position_cost_short': 844830.0, 'float_profit_long': -320.0, 'float_profit_short': 210.0,
             'float_profit': -110.0, 'position_profit_long': 0, 'position_profit_short': 0.0, 'position_profit': 0,
             'margin_long': 77670.4, 'margin_short': 67961.59999999999, 'margin': 145632.0, 'last_price': 120690.0,
             'underlying_last_price': float('nan'), 'market_value_long': 0.0, 'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close_fok', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 120640.0, 'time_condition': 'IOC', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_buy_close_fok', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615964399500000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close_fok', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 120640.0, 'time_condition': 'IOC', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_buy_close_fok', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '已撤单报单已提交', 'status': 'FINISHED',
             'insert_date_time': 1615964399500000000}
        )

    def trade_future_13(self):
        """买平昨 2手 成交"""
        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_buy_close_fok',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'BUY',
            'offset': 'CLOSE',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 120700.0,
            'time_condition': 'IOC',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        trades = self.account_snapshot['trade']['abc']['trades']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999690.0, 'static_balance': 999690.0, 'balance': 999658.0,
             'available': 873443.6, 'float_profit': -170.0, 'position_profit': 0.0, 'close_profit': -20.0,
             'frozen_margin': 0.0, 'margin': 126214.4, 'frozen_commission': 0.0, 'commission': 12.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.1262575800923916,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 8, 'pos_long_today': 0,
             'pos_short_his': 5, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 8, 'volume_long': 8,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 5, 'volume_short': 5, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 120730.0,
             'open_price_short': 120720.0, 'open_cost_long': 965840.0, 'open_cost_short': 603600.0,
             'position_price_long': 120690.0, 'position_price_short': 120690.0, 'position_cost_long': 965520.0,
             'position_cost_short': 603450.0, 'float_profit_long': -320.0, 'float_profit_short': 150.0,
             'float_profit': -170.0, 'position_profit_long': 0, 'position_profit_short': 0.0, 'position_profit': 0,
             'margin_long': 77670.4, 'margin_short': 48543.99999999999, 'margin': 126214.4, 'last_price': 120690.0,
             'underlying_last_price': float('nan'), 'market_value_long': 0.0, 'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )
        self.assertEqual(
            trades,
            {'PYSDK_insert_buy_open|10': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_open',
                                          'trade_id': 'PYSDK_insert_buy_open|10',
                                          'exchange_trade_id': 'PYSDK_insert_buy_open|10', 'exchange_id': 'SHFE',
                                          'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'OPEN',
                                          'price': 120730.0, 'volume': 10, 'trade_date_time': 1615959234600000000,
                                          'commission': 60.0},
             'PYSDK_insert_sell_closetoday|2': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_closetoday',
                                                'trade_id': 'PYSDK_insert_sell_closetoday|2',
                                                'exchange_trade_id': 'PYSDK_insert_sell_closetoday|2',
                                                'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'direction': 'SELL',
                                                'offset': 'CLOSETODAY', 'price': 120720.0, 'volume': 2,
                                                'trade_date_time': 1615959234600000000, 'commission': 12.0},
             'PYSDK_insert_sell_open|10': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_open',
                                           'trade_id': 'PYSDK_insert_sell_open|10',
                                           'exchange_trade_id': 'PYSDK_insert_sell_open|10', 'exchange_id': 'SHFE',
                                           'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'OPEN',
                                           'price': 120720.0, 'volume': 10, 'trade_date_time': 1615959234600000000,
                                           'commission': 60.0},
             'PYSDK_insert_buy_closetoday|3': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_closetoday',
                                               'trade_id': 'PYSDK_insert_buy_closetoday|3',
                                               'exchange_trade_id': 'PYSDK_insert_buy_closetoday|3',
                                               'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'direction': 'BUY',
                                               'offset': 'CLOSETODAY', 'price': 120730.0, 'volume': 3,
                                               'trade_date_time': 1615959234600000000, 'commission': 18.0},
             'PYSDK_insert_buy_close_fok|2': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close_fok',
                                              'trade_id': 'PYSDK_insert_buy_close_fok|2',
                                              'exchange_trade_id': 'PYSDK_insert_buy_close_fok|2',
                                              'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'direction': 'BUY',
                                              'offset': 'CLOSE', 'price': 120700.0, 'volume': 2,
                                              'trade_date_time': 1615964399500000000, 'commission': 12.0}}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close_fok', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 120700.0, 'time_condition': 'IOC', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_buy_close_fok', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615964399500000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close_fok', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 120700.0, 'time_condition': 'IOC', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_buy_close_fok', 'volume_orign': 2, 'volume_left': 0,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1615964399500000000}
        )

    def trade_future_14(self):
        """卖平昨 2手 成交"""
        diffs, orders_events = self.sim_trade.insert_order("SHFE.ni2106", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_sell_close_fok',
            'exchange_id': 'SHFE',
            'instrument_id': 'ni2106',
            'direction': 'SELL',
            'offset': 'CLOSE',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 120690.0,
            'time_condition': 'IOC',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        trades = self.account_snapshot['trade']['abc']['trades']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 999690.0, 'static_balance': 999690.0, 'balance': 999646.0,
             'available': 892849.2, 'float_profit': -90.0, 'position_profit': 0.0, 'close_profit': -20.0,
             'frozen_margin': 0.0, 'margin': 106796.79999999999, 'frozen_commission': 0.0, 'commission': 24.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.10683461945528716,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['SHFE.ni2106'],
            {'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'pos_long_his': 6, 'pos_long_today': 0,
             'pos_short_his': 5, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 6, 'volume_long': 6,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 5, 'volume_short': 5, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 120730.0,
             'open_price_short': 120720.0, 'open_cost_long': 724380.0, 'open_cost_short': 603600.0,
             'position_price_long': 120690.0, 'position_price_short': 120690.0, 'position_cost_long': 724140.0,
             'position_cost_short': 603450.0, 'float_profit_long': -240.0, 'float_profit_short': 150.0,
             'float_profit': -90.0, 'position_profit_long': 0, 'position_profit_short': 0.0, 'position_profit': 0,
             'margin_long': 58252.799999999996, 'margin_short': 48543.99999999999, 'margin': 106796.79999999999,
             'last_price': 120690.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0,
             'market_value': 0.0, 'future_margin': 9708.8}
        )
        self.assertEqual(
            trades,
            {'PYSDK_insert_buy_open|10': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_open',
                                          'trade_id': 'PYSDK_insert_buy_open|10',
                                          'exchange_trade_id': 'PYSDK_insert_buy_open|10', 'exchange_id': 'SHFE',
                                          'instrument_id': 'ni2106', 'direction': 'BUY', 'offset': 'OPEN',
                                          'price': 120730.0, 'volume': 10, 'trade_date_time': 1615959234600000000,
                                          'commission': 60.0},
             'PYSDK_insert_sell_closetoday|2': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_closetoday',
                                                'trade_id': 'PYSDK_insert_sell_closetoday|2',
                                                'exchange_trade_id': 'PYSDK_insert_sell_closetoday|2',
                                                'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'direction': 'SELL',
                                                'offset': 'CLOSETODAY', 'price': 120720.0, 'volume': 2,
                                                'trade_date_time': 1615959234600000000, 'commission': 12.0},
             'PYSDK_insert_sell_open|10': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_open',
                                           'trade_id': 'PYSDK_insert_sell_open|10',
                                           'exchange_trade_id': 'PYSDK_insert_sell_open|10', 'exchange_id': 'SHFE',
                                           'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'OPEN',
                                           'price': 120720.0, 'volume': 10, 'trade_date_time': 1615959234600000000,
                                           'commission': 60.0},
             'PYSDK_insert_buy_closetoday|3': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_closetoday',
                                               'trade_id': 'PYSDK_insert_buy_closetoday|3',
                                               'exchange_trade_id': 'PYSDK_insert_buy_closetoday|3',
                                               'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'direction': 'BUY',
                                               'offset': 'CLOSETODAY', 'price': 120730.0, 'volume': 3,
                                               'trade_date_time': 1615959234600000000, 'commission': 18.0},
             'PYSDK_insert_buy_close_fok|2': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close_fok',
                                              'trade_id': 'PYSDK_insert_buy_close_fok|2',
                                              'exchange_trade_id': 'PYSDK_insert_buy_close_fok|2',
                                              'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'direction': 'BUY',
                                              'offset': 'CLOSE', 'price': 120700.0, 'volume': 2,
                                              'trade_date_time': 1615964399500000000, 'commission': 12.0},
             'PYSDK_insert_sell_close_fok|2': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_close_fok',
                                               'trade_id': 'PYSDK_insert_sell_close_fok|2',
                                               'exchange_trade_id': 'PYSDK_insert_sell_close_fok|2',
                                               'exchange_id': 'SHFE', 'instrument_id': 'ni2106', 'direction': 'SELL',
                                               'offset': 'CLOSE', 'price': 120690.0, 'volume': 2,
                                               'trade_date_time': 1615964399500000000, 'commission': 12.0}}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_close_fok', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 120690.0, 'time_condition': 'IOC', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_sell_close_fok', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615964399500000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_sell_close_fok', 'exchange_id': 'SHFE',
             'instrument_id': 'ni2106', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 120690.0, 'time_condition': 'IOC', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_sell_close_fok', 'volume_orign': 2, 'volume_left': 0,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1615964399500000000}
        )


class TestSimTradeFuture9(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期货交易 （卖开 10 手成交）
    1. 买开 5 手，冻结
    2. 修改保证金/手续费（10手持仓保证金变化，冻结保证金不变）
    3. 买平 5 手
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        self.sim_trade.update_quotes("DCE.jd2105", {
            'quotes': {
                'DCE.jd2105': {
                    'datetime': '2021-03-17 13:33:54.600000', 'ask_price1': 4360.0, 'bid_price1': 4359.0,
                    'last_price': 4359.0, 'price_tick': 1.0, 'volume_multiple': 10.0, 'ins_class': 'FUTURE',
                    'instrument_id': 'DCE.jd2105', 'margin': 3062.5, 'commission': 6.5625,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": []
                    }
                }
            }
        })
        # 卖开 10 手
        self.account_snapshot['trade']['abc']['positions']
        diffs, orders_events = self.sim_trade.insert_order("DCE.jd2105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'sell_open_10',
            'exchange_id': 'DCE',
            'instrument_id': 'jd2105',
            'direction': 'SELL',
            'offset': 'OPEN',
            'volume': 10,
            'price_type': 'LIMIT',
            'limit_price': 4359.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_future(self):
        self.trade_future_1()
        self.trade_future_2()
        self.trade_future_3()

    def trade_future_1(self):
        """买开5手，冻结"""
        diffs, orders_events = self.sim_trade.insert_order("DCE.jd2105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'buy_close_5',
            'exchange_id': 'DCE',
            'instrument_id': 'jd2105',
            'direction': 'BUY',
            'offset': 'OPEN',
            'volume': 5,
            'price_type': 'LIMIT',
            'limit_price': 4358.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999934.375,
             'available': 953996.875, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 15312.5, 'margin': 30625.0, 'frozen_commission': 0.0, 'commission': 65.625,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.030627009897524524,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['DCE.jd2105'],
            {'exchange_id': 'DCE', 'instrument_id': 'jd2105', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 10, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 10, 'volume_short_his': 0, 'volume_short': 10, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': float('nan'), 'open_price_short': 4359.0,
             'open_cost_long': 0.0, 'open_cost_short': 435900.0, 'position_price_long': float('nan'),
             'position_price_short': 4359.0, 'position_cost_long': 0.0, 'position_cost_short': 435900.0,
             'float_profit_long': 0.0, 'float_profit_short': 0.0, 'float_profit': 0.0, 'position_profit_long': 0.0,
             'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0, 'margin_short': 30625.0,
             'margin': 30625.0, 'last_price': 4359.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 3062.5}
        )
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_5', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'OPEN', 'price_type': 'LIMIT', 'limit_price': 4358.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_5', 'volume_orign': 5,
             'volume_left': 5, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )

    def trade_future_2(self):
        """修改保证金/手续费"""
        diffs, orders_events = self.sim_trade.update_quotes("DCE.jd2105", {
            'quotes': {
                'DCE.jd2105': {'margin': 5000.0, 'commission': 10.0}
            }
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999934.375,
             'available': 934621.875, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 15312.5, 'margin': 50000.0, 'frozen_commission': 0.0, 'commission': 65.625,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.05000328146534616,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['DCE.jd2105'],
            {'exchange_id': 'DCE', 'instrument_id': 'jd2105', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 10, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 10, 'volume_short_his': 0, 'volume_short': 10, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': float('nan'), 'open_price_short': 4359.0,
             'open_cost_long': 0.0, 'open_cost_short': 435900.0, 'position_price_long': float('nan'),
             'position_price_short': 4359.0, 'position_cost_long': 0.0, 'position_cost_short': 435900.0,
             'float_profit_long': 0.0, 'float_profit_short': 0.0, 'float_profit': 0.0, 'position_profit_long': 0.0,
             'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0, 'margin_short': 50000.0,
             'margin': 50000.0, 'last_price': 4359.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 5000.0}
        )

    def trade_future_3(self):
        """买平 5 手"""
        diffs, orders_events = self.sim_trade.insert_order("DCE.jd2105", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'buy_close_5',
            'exchange_id': 'DCE',
            'instrument_id': 'jd2105',
            'direction': 'BUY',
            'offset': 'CLOSE',
            'volume': 5,
            'price_type': 'LIMIT',
            'limit_price': 4360.0,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999834.375,
             'available': 959521.875, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': -50.0,
             'frozen_margin': 15312.5, 'margin': 25000.0, 'frozen_commission': 0.0, 'commission': 115.625,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.02500414131090462,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['DCE.jd2105'],
            {'exchange_id': 'DCE', 'instrument_id': 'jd2105', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 5, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 5, 'volume_short_his': 0, 'volume_short': 5, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': float('nan'), 'open_price_short': 4359.0,
             'open_cost_long': 0.0, 'open_cost_short': 217950.0, 'position_price_long': float('nan'),
             'position_price_short': 4359.0, 'position_cost_long': 0.0, 'position_cost_short': 217950.0,
             'float_profit_long': 0.0, 'float_profit_short': 0.0, 'float_profit': 0.0, 'position_profit_long': 0.0,
             'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0, 'margin_short': 25000.0,
             'margin': 25000.0, 'last_price': 4359.0, 'underlying_last_price': float('nan'), 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': 5000.0}
        )
        
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_5', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 4360.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_5', 'volume_orign': 5,
             'volume_left': 5, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1615959234600000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'buy_close_5', 'exchange_id': 'DCE', 'instrument_id': 'jd2105',
             'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT', 'limit_price': 4360.0,
             'time_condition': 'GFD', 'volume_condition': 'ANY', 'exchange_order_id': 'buy_close_5', 'volume_orign': 5,
             'volume_left': 0, 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1615959234600000000}
        )
