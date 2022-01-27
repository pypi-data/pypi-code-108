#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'mayanqiong'

import json
import unittest

from tqsdk.diff import _simple_merge_diff
from tqsdk.tradeable.sim.trade_stock import SimTradeStock


class TestSimTradeStock1(unittest.TestCase):
    """
    简单测试：
    1. 初始截面
    2. 更新行情
    3. 未收到行情下单
    """

    def test_trade_0(self):
        """初始账户截面"""
        sim_trade = SimTradeStock(account_key="abc", init_balance=10000.0)
        account_snapshot = sim_trade.init_snapshot()
        account = account_snapshot['trade']['abc']['accounts']['CNY']
        print(json.dumps(account, ensure_ascii=False))
        self.assertEqual(
            '{"user_id": "", "currency": "CNY", "market_value_his": 0.0, "asset_his": 10000.0, "cost_his": 0.0, "deposit": 0.0, "withdraw": 0.0, "dividend_balance_today": 0.0, "available_his": 10000.0, "market_value": 0.0, "asset": 10000.0, "available": 10000.0, "drawable": 10000.0, "buy_frozen_balance": 0.0, "buy_frozen_fee": 0.0, "buy_balance_today": 0.0, "buy_fee_today": 0.0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "cost": 0.0, "hold_profit": 0.0, "float_profit_today": 0.0, "real_profit_today": 0.0, "profit_today": 0.0, "profit_rate_today": 0.0}',
            json.dumps(account, ensure_ascii=False)
        )

    def test_trade_1(self):
        """初始账户, 首先更新行情，"""
        sim_trade = SimTradeStock(account_key="abc", init_balance=10000.0)
        account_snapshot = sim_trade.init_snapshot()

        # 初次更新行情，一定会收到持仓和账户更新包
        diffs, orders_events = sim_trade.update_quotes("SSE.603666", {
            'quotes': {
                'SSE.603666': {
                    'datetime': '2021-11-23 13:49:43.510000', 'ins_class': 'STOCK', 'instrument_id': 'SSE.603666',
                    'instrument_name': '亿嘉和', 'exchange_id': 'SSE', 'expired': False,
                    'trading_time': {"day": [["09:30:00", "11:30:00"], ["13:00:00", "15:00:00"]], "night": []},
                    'ask_price1': 75.8, 'ask_volume1': 19700, 'bid_price1': 75.79, 'bid_volume1': 1600,
                    'last_price': 75.79, 'highest': 76.8, 'lowest': 73.73, 'open': 74.9,
                    'average': 74.95, 'volume': 2748961, 'amount': 206025211.0, 'open_interest': 0,
                    'upper_limit': 83.37, 'lower_limit': 68.21, 'price_tick': 0.01, 'price_decs': 2,
                    'volume_multiple': 100.0, 'max_limit_order_volume': 0, 'max_market_order_volume': 0, 'min_limit_order_volume': 0, 'min_market_order_volume': 0,
                    'stock_dividend_ratio': ['20181102,0.400000', '20200624,0.400000', '20210716,0.400000'],
                    'cash_dividend_ratio': ['20181102,0.140000', '20190628,0.462000', '20200624,0.260000', '20210716,0.370000']
                }
            }
        })
        account = account_snapshot['trade']['abc']['accounts']['CNY']
        account_str = json.dumps(account, ensure_ascii=False)  # 初始账户信息

        self.assertEqual(len(diffs), 2)  # 一定会收到持仓和账户更新包
        self.assertEqual([], orders_events)
        for diff in diffs:
            _simple_merge_diff(account_snapshot, diff)

        self.assertEqual(json.dumps(account, ensure_ascii=False), account_str)  # 账户信息没变，收到默认的持仓
        position = account_snapshot['trade']['abc']['positions']['SSE.603666']
        print(json.dumps(position, ensure_ascii=False, sort_keys=True))
        self.assertEqual(
            '{"buy_balance_his": 0.0, "buy_balance_today": 0.0, "buy_fee_his": 0.0, "buy_fee_today": 0.0, "buy_float_profit_today": 0.0, "buy_volume_his": 0, "buy_volume_today": 0, "cost": 0.0, "cost_his": 0.0, "create_date": "", "devidend_balance_today": 0.0, "exchange_id": "SSE", "float_profit_today": 0.0, "hold_profit": 0.0, "instrument_id": "603666", "last_price": 75.79, "market_value": 0.0, "market_value_his": 0.0, "profit_rate_today": 0.0, "profit_rate_total": 0.0, "profit_today": 0.0, "profit_total": 0.0, "real_profit_his": 0.0, "real_profit_today": 0.0, "real_profit_total": 0.0, "sell_balance_his": 0.0, "sell_balance_today": 0.0, "sell_fee_his": 0.0, "sell_fee_today": 0.0, "sell_float_profit_today": 0.0, "sell_volume_frozen": 0, "sell_volume_his": 0, "sell_volume_today": 0, "shared_volume_today": 0, "user_id": "", "volume": 0, "volume_his": 0}',
            json.dumps(position, ensure_ascii=False, sort_keys=True)
        )

    def test_trade_2(self):
        """初始账户, 没有更新行情先下单，报错"""
        sim_trade = SimTradeStock(account_key="abc", init_balance=10000.0)
        account_snapshot = sim_trade.init_snapshot()
        # 直接下单抛错
        with self.assertRaises(Exception) as e:
            sim_trade.insert_order("SSE.603666", {
                'aid': 'insert_order',
                'user_id': 'TQSIM',
                'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
                'exchange_id': 'SSE',
                'instrument_id': '603666',
                'direction': 'BUY',
                'volume': 100,
                'price_type': 'ANY'
            })
        self.assertEqual('未收到指定合约行情', str(e.exception))


class TestSimTradeStock2(unittest.TestCase):
    """
    简单测试：
    1. 下市价单
    2. 平仓手数不足, 限价单
    3. 限价单, 行情更新,  成交
    4. 下单 200 手未成交, 下单 600 手未成交, 结算
    5. 下单 200 手未成交, 下单 600 手未成交, 撤单
    """

    def setUp(self) -> None:
        self.sim_trade = SimTradeStock(account_key="abc", account_id="TQSIM", init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        account_str = json.dumps(account, ensure_ascii=False)  # 初始账户信息
        self.assertEqual(
            '{"user_id": "TQSIM", "currency": "CNY", "market_value_his": 0.0, "asset_his": 1000000.0, "cost_his": 0.0, "deposit": 0.0, "withdraw": 0.0, "dividend_balance_today": 0.0, "available_his": 1000000.0, "market_value": 0.0, "asset": 1000000.0, "available": 1000000.0, "drawable": 1000000.0, "buy_frozen_balance": 0.0, "buy_frozen_fee": 0.0, "buy_balance_today": 0.0, "buy_fee_today": 0.0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "cost": 0.0, "hold_profit": 0.0, "float_profit_today": 0.0, "real_profit_today": 0.0, "profit_today": 0.0, "profit_rate_today": 0.0}',
            account_str
        )
        diffs, orders_events = self.sim_trade.update_quotes("SSE.603666", {
            'quotes': {
                'SSE.603666': {
                    'datetime': '2021-11-23 13:49:43.510000', 'ins_class': 'STOCK', 'instrument_id': 'SSE.603666',
                    'instrument_name': '亿嘉和', 'exchange_id': 'SSE', 'expired': False,
                    'trading_time': {"day": [["09:30:00", "11:30:00"], ["13:00:00", "15:00:00"]], "night": []},
                    'ask_price1': 75.8, 'ask_volume1': 19700, 'bid_price1': 75.79, 'bid_volume1': 1600,
                    'last_price': 75.79, 'highest': 76.8, 'lowest': 73.73, 'open': 74.9,
                    'average': 74.95, 'volume': 2748961, 'amount': 206025211.0, 'open_interest': 0,
                    'upper_limit': 83.37, 'lower_limit': 68.21, 'price_tick': 0.01, 'price_decs': 2,
                    'volume_multiple': 100.0, 'max_limit_order_volume': 0, 'max_market_order_volume': 0,
                    'min_limit_order_volume': 0, 'min_market_order_volume': 0,
                    'stock_dividend_ratio': ['20181102,0.400000', '20200624,0.400000', '20210716,0.400000'],
                    'cash_dividend_ratio': ['20181102,0.140000', '20190628,0.462000', '20200624,0.260000',
                                            '20210716,0.370000']
                }
            }
        })
        self.assertEqual(len(diffs), 2)  # 一定会收到持仓和账户更新包
        self.assertEqual([], orders_events)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        self.assertEqual(json.dumps(account, ensure_ascii=False), account_str)  # 账户信息没变，收到默认的持仓
        position = self.account_snapshot['trade']['abc']['positions']['SSE.603666']
        self.assertEqual(
            {"buy_balance_his": 0.0, "buy_balance_today": 0.0, "buy_fee_his": 0.0, "buy_fee_today": 0.0,
             "buy_float_profit_today": 0.0, "buy_volume_his": 0, "buy_volume_today": 0, "cost": 0.0, "cost_his": 0.0,
             "create_date": "", "devidend_balance_today": 0.0, "exchange_id": "SSE", "float_profit_today": 0.0,
             "hold_profit": 0.0, "instrument_id": "603666", "last_price": 75.79, "market_value": 0.0,
             "market_value_his": 0.0, "profit_rate_today": 0.0, "profit_rate_total": 0.0, "profit_today": 0.0,
             "profit_total": 0.0, "real_profit_his": 0.0, "real_profit_today": 0.0, "real_profit_total": 0.0,
             "sell_balance_his": 0.0, "sell_balance_today": 0.0, "sell_fee_his": 0.0, "sell_fee_today": 0.0,
             "sell_float_profit_today": 0.0, "sell_volume_frozen": 0, "sell_volume_his": 0, "sell_volume_today": 0,
             "shared_volume_today": 0, "user_id": "TQSIM", "volume": 0, "volume_his": 0},
            position
        )

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_1(self):
        """市价单"""
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 200,
            'price_type': 'ANY'
        })
        self.assertEqual(6, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            '{"user_id": "TQSIM", "currency": "CNY", "market_value_his": 0.0, "asset_his": 1000000.0, "cost_his": 0.0, "deposit": 0.0, "withdraw": 0.0, "dividend_balance_today": 0.0, "available_his": 1000000.0, "market_value": 15158.000000000002, "asset": 999993.0, "available": 984835.0, "drawable": 984835.0, "buy_frozen_balance": 0.0, "buy_frozen_fee": 0.0, "buy_balance_today": 15160.0, "buy_fee_today": 5.0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "cost": 15165.0, "hold_profit": -6.999999999998181, "float_profit_today": -6.999999999999318, "real_profit_today": 0.0, "profit_today": -6.999999999999318, "profit_rate_today": -0.00046158918562474896}',
            json.dumps(account)
        )
        self.assertEqual(
            '{"user_id": "TQSIM", "exchange_id": "SSE", "instrument_id": "603666", "create_date": "2021-11-23", "volume_his": 0, "cost_his": 0.0, "market_value_his": 0.0, "real_profit_his": 0.0, "shared_volume_today": 0, "devidend_balance_today": 0.0, "buy_volume_his": 0, "buy_balance_his": 0.0, "buy_fee_his": 0.0, "sell_volume_his": 0, "sell_balance_his": 0.0, "sell_fee_his": 0.0, "buy_volume_today": 200, "buy_balance_today": 15160.0, "buy_fee_today": 5.0, "sell_volume_today": 0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "last_price": 75.79, "sell_volume_frozen": 0, "sell_float_profit_today": 0.0, "buy_float_profit_today": -6.999999999999318, "cost": 15165.0, "volume": 200, "market_value": 15158.000000000002, "float_profit_today": -6.999999999999318, "real_profit_today": 0.0, "profit_today": -6.999999999999318, "profit_rate_today": -0.00046158918562474896, "hold_profit": -6.999999999998181, "real_profit_total": 0.0, "profit_total": -6.999999999998181, "profit_rate_total": -0.000461589185624674, "buy_avg_price": 75.825}',
            json.dumps(positions["SSE.603666"])
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'exchange_id': 'SSE', 'instrument_id': '603666', 'direction': 'BUY', 'price_type': 'ANY', 'exchange_order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'volume_orign': 200, 'volume_left': 0, 'frozen_balance': 0.0, 'frozen_fee': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED', 'insert_date_time': 1637646583510000000},
            orders['PYSDK_insert_42de71a44009a3420164af39b87a7870']
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'trade_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870|200', 'exchange_trade_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870|200', 'exchange_id': 'SSE', 'instrument_id': '603666', 'direction': 'BUY', 'price': 75.8, 'volume': 200, 'trade_date_time': 1637646583510000000, 'fee': 5.0},
            trades['PYSDK_insert_42de71a44009a3420164af39b87a7870|200']
        )

        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_aaaa',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'SELL',
            'volume': 200,
            'price_type': 'LIMIT',
            'limit_price': 98.5
        })
        self.assertEqual(2, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            '{"user_id": "TQSIM", "currency": "CNY", "market_value_his": 0.0, "asset_his": 1000000.0, "cost_his": 0.0, "deposit": 0.0, "withdraw": 0.0, "dividend_balance_today": 0.0, "available_his": 1000000.0, "market_value": 15158.000000000002, "asset": 999993.0, "available": 984835.0, "drawable": 984835.0, "buy_frozen_balance": 0.0, "buy_frozen_fee": 0.0, "buy_balance_today": 15160.0, "buy_fee_today": 5.0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "cost": 15165.0, "hold_profit": -6.999999999998181, "float_profit_today": -6.999999999999318, "real_profit_today": 0.0, "profit_today": -6.999999999999318, "profit_rate_today": -0.00046158918562474896}',
            json.dumps(account)
        )
        self.assertEqual(
            '{"user_id": "TQSIM", "exchange_id": "SSE", "instrument_id": "603666", "create_date": "2021-11-23", "volume_his": 0, "cost_his": 0.0, "market_value_his": 0.0, "real_profit_his": 0.0, "shared_volume_today": 0, "devidend_balance_today": 0.0, "buy_volume_his": 0, "buy_balance_his": 0.0, "buy_fee_his": 0.0, "sell_volume_his": 0, "sell_balance_his": 0.0, "sell_fee_his": 0.0, "buy_volume_today": 200, "buy_balance_today": 15160.0, "buy_fee_today": 5.0, "sell_volume_today": 0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "last_price": 75.79, "sell_volume_frozen": 0, "sell_float_profit_today": 0.0, "buy_float_profit_today": -6.999999999999318, "cost": 15165.0, "volume": 200, "market_value": 15158.000000000002, "float_profit_today": -6.999999999999318, "real_profit_today": 0.0, "profit_today": -6.999999999999318, "profit_rate_today": -0.00046158918562474896, "hold_profit": -6.999999999998181, "real_profit_total": 0.0, "profit_total": -6.999999999998181, "profit_rate_total": -0.000461589185624674, "buy_avg_price": 75.825}',
            json.dumps(positions["SSE.603666"])
        )
        self.assertEqual(
            {'direction': 'SELL', 'exchange_id': 'SSE', 'exchange_order_id': 'PYSDK_insert_aaaa',
             'frozen_balance': 0.0, 'frozen_fee': 0.0, 'insert_date_time': 1637646583510000000,
             'instrument_id': '603666', 'last_msg': '平仓手数不足', 'limit_price': 98.5, 'order_id': 'PYSDK_insert_aaaa',
             'price_type': 'LIMIT', 'status': 'FINISHED', 'user_id': 'TQSIM', 'volume_left': 200, 'volume_orign': 200},
            orders['PYSDK_insert_aaaa']
        )
        self.assertEqual(1, len(trades))

    def test_trade_2(self):
        """平仓手数不足, 限价单"""
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'SELL',
            'volume': 200,
            'price_type': 'LIMIT',
            'limit_price': 98.5
        })
        self.assertEqual(2, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            '{"user_id": "TQSIM", "currency": "CNY", "market_value_his": 0.0, "asset_his": 1000000.0, "cost_his": 0.0, "deposit": 0.0, "withdraw": 0.0, "dividend_balance_today": 0.0, "available_his": 1000000.0, "market_value": 0.0, "asset": 1000000.0, "available": 1000000.0, "drawable": 1000000.0, "buy_frozen_balance": 0.0, "buy_frozen_fee": 0.0, "buy_balance_today": 0.0, "buy_fee_today": 0.0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "cost": 0.0, "hold_profit": 0.0, "float_profit_today": 0.0, "real_profit_today": 0.0, "profit_today": 0.0, "profit_rate_today": 0.0}',
            json.dumps(account)
        )
        self.assertEqual(
            '{"user_id": "TQSIM", "exchange_id": "SSE", "instrument_id": "603666", "create_date": "", "volume_his": 0, "cost_his": 0.0, "market_value_his": 0.0, "real_profit_his": 0.0, "shared_volume_today": 0, "devidend_balance_today": 0.0, "buy_volume_his": 0, "buy_balance_his": 0.0, "buy_fee_his": 0.0, "sell_volume_his": 0, "sell_balance_his": 0.0, "sell_fee_his": 0.0, "buy_volume_today": 0, "buy_balance_today": 0.0, "buy_fee_today": 0.0, "sell_volume_today": 0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "last_price": 75.79, "sell_volume_frozen": 0, "sell_float_profit_today": 0.0, "buy_float_profit_today": 0.0, "cost": 0.0, "volume": 0, "market_value": 0.0, "float_profit_today": 0.0, "real_profit_today": 0.0, "profit_today": 0.0, "profit_rate_today": 0.0, "hold_profit": 0.0, "real_profit_total": 0.0, "profit_total": 0.0, "profit_rate_total": 0.0}',
            json.dumps(positions["SSE.603666"])
        )
        self.assertEqual(
            {'direction': 'SELL', 'exchange_id': 'SSE', 'exchange_order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
             'frozen_balance': 0.0, 'frozen_fee': 0.0, 'insert_date_time': 1637646583510000000, 'instrument_id': '603666',
             'last_msg': '平仓手数不足', 'limit_price': 98.5, 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
             'price_type': 'LIMIT', 'status': 'FINISHED', 'user_id': 'TQSIM', 'volume_left': 200, 'volume_orign': 200},
            orders['PYSDK_insert_42de71a44009a3420164af39b87a7870']
        )
        self.assertEqual({}, trades)

        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 200,
            'price_type': 'LIMIT',
            'limit_price': 78.5
        })
        self.assertEqual(6, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        self.assertEqual(
            '{"user_id": "TQSIM", "currency": "CNY", "market_value_his": 0.0, "asset_his": 1000000.0, "cost_his": 0.0, "deposit": 0.0, "withdraw": 0.0, "dividend_balance_today": 0.0, "available_his": 1000000.0, "market_value": 15158.000000000002, "asset": 999453.0, "available": 984295.0, "drawable": 984295.0, "buy_frozen_balance": 0.0, "buy_frozen_fee": 0.0, "buy_balance_today": 15700.0, "buy_fee_today": 5.0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "cost": 15705.0, "hold_profit": -546.9999999999982, "float_profit_today": -546.9999999999999, "real_profit_today": 0.0, "profit_today": -546.9999999999999, "profit_rate_today": -0.03482967207895574}',
            json.dumps(account)
        )
        self.assertEqual(
            '{"user_id": "TQSIM", "exchange_id": "SSE", "instrument_id": "603666", "create_date": "2021-11-23", "volume_his": 0, "cost_his": 0.0, "market_value_his": 0.0, "real_profit_his": 0.0, "shared_volume_today": 0, "devidend_balance_today": 0.0, "buy_volume_his": 0, "buy_balance_his": 0.0, "buy_fee_his": 0.0, "sell_volume_his": 0, "sell_balance_his": 0.0, "sell_fee_his": 0.0, "buy_volume_today": 200, "buy_balance_today": 15700.0, "buy_fee_today": 5.0, "sell_volume_today": 0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "last_price": 75.79, "sell_volume_frozen": 0, "sell_float_profit_today": 0.0, "buy_float_profit_today": -546.9999999999999, "cost": 15705.0, "volume": 200, "market_value": 15158.000000000002, "float_profit_today": -546.9999999999999, "real_profit_today": 0.0, "profit_today": -546.9999999999999, "profit_rate_today": -0.03482967207895574, "hold_profit": -546.9999999999982, "real_profit_total": 0.0, "profit_total": -546.9999999999982, "profit_rate_total": -0.03482967207895563, "buy_avg_price": 78.525}',
            json.dumps(positions["SSE.603666"])
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'exchange_id': 'SSE',
             'instrument_id': '603666', 'direction': 'BUY', 'price_type': 'LIMIT', 'limit_price': 78.5,
             'exchange_order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'volume_orign': 200,
             'volume_left': 0, 'frozen_balance': 0.0, 'frozen_fee': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1637646583510000000},
            orders['PYSDK_insert_42de71a44009a3420164af39b87a7870']
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
             'trade_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870|200',
             'exchange_trade_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870|200', 'exchange_id': 'SSE',
             'instrument_id': '603666', 'direction': 'BUY', 'price': 78.5, 'volume': 200,
             'trade_date_time': 1637646583510000000, 'fee': 5.0},
            trades['PYSDK_insert_42de71a44009a3420164af39b87a7870|200']
        )

    def test_trade_3(self):
        """限价单  行情更新  成交"""
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 200,
            'price_type': 'LIMIT',
            'limit_price': 75.7
        })
        self.assertEqual(2, len(diffs))
        self.assertEqual(1, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            '{"user_id": "TQSIM", "currency": "CNY", "market_value_his": 0.0, "asset_his": 1000000.0, "cost_his": 0.0, "deposit": 0.0, "withdraw": 0.0, "dividend_balance_today": 0.0, "available_his": 1000000.0, "market_value": 0.0, "asset": 1000000.0, "available": 984855.0, "drawable": 984855.0, "buy_frozen_balance": 15140.0, "buy_frozen_fee": 5.0, "buy_balance_today": 0.0, "buy_fee_today": 0.0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "cost": 0.0, "hold_profit": 0.0, "float_profit_today": 0.0, "real_profit_today": 0.0, "profit_today": 0.0, "profit_rate_today": 0.0}',
            json.dumps(account)
        )
        self.assertEqual(
            '{"user_id": "TQSIM", "exchange_id": "SSE", "instrument_id": "603666", "create_date": "", "volume_his": 0, "cost_his": 0.0, "market_value_his": 0.0, "real_profit_his": 0.0, "shared_volume_today": 0, "devidend_balance_today": 0.0, "buy_volume_his": 0, "buy_balance_his": 0.0, "buy_fee_his": 0.0, "sell_volume_his": 0, "sell_balance_his": 0.0, "sell_fee_his": 0.0, "buy_volume_today": 0, "buy_balance_today": 0.0, "buy_fee_today": 0.0, "sell_volume_today": 0, "sell_balance_today": 0.0, "sell_fee_today": 0.0, "last_price": 75.79, "sell_volume_frozen": 0, "sell_float_profit_today": 0.0, "buy_float_profit_today": 0.0, "cost": 0.0, "volume": 0, "market_value": 0.0, "float_profit_today": 0.0, "real_profit_today": 0.0, "profit_today": 0.0, "profit_rate_today": 0.0, "hold_profit": 0.0, "real_profit_total": 0.0, "profit_total": 0.0, "profit_rate_total": 0.0}',
            json.dumps(positions["SSE.603666"])
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'exchange_id': 'SSE',
             'instrument_id': '603666', 'direction': 'BUY', 'price_type': 'LIMIT', 'limit_price': 75.7,
             'exchange_order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'volume_orign': 200,
             'volume_left': 200, 'frozen_balance': 0.0, 'frozen_fee': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1637646583510000000},
            orders['PYSDK_insert_42de71a44009a3420164af39b87a7870']
        )
        self.assertEqual({}, trades)

        # 行情更新
        diffs, orders_events = self.sim_trade.update_quotes("SSE.603666", {
            'quotes': {
                'SSE.603666': {
                    'datetime': '2021-11-23 13:49:44.510000',
                    'ask_price1': 75.7, 'last_price': 75.69, 'bid_price1': 75.69
                }
            }
        })
        self.assertEqual(6, len(diffs))
        self.assertEqual(1, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        self.assertEqual(
            {
             'asset': 999993.0,
             'asset_his': 1000000.0,
             'available': 984855.0,
             'available_his': 1000000.0,
             'buy_balance_today': 15140.0,
             'buy_fee_today': 5.0,
             'buy_frozen_balance': 0.0,
             'buy_frozen_fee': 0.0,
             'cost': 15145.0,
             'cost_his': 0.0,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 0.0,
             'drawable': 984855.0,
             'float_profit_today': 6.0000000000030695,
             'hold_profit': -7.0,
             'market_value': 15138.0,
             'market_value_his': 0.0,
             'profit_rate_today': 0.000396170353252101,
             'profit_today': 6.0000000000030695,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account
        )
        self.assertEqual(
            {'buy_avg_price': 75.725,
             'buy_balance_his': 0.0,
             'buy_balance_today': 15140.0,
             'buy_fee_his': 0.0,
             'buy_fee_today': 5.0,
             'buy_float_profit_today': 6.0000000000030695,
             'buy_volume_his': 0,
             'buy_volume_today': 200,
             'cost': 15145.0,
             'cost_his': 0.0,
             'create_date': '2021-11-23',
             'devidend_balance_today': 0.0,
             'exchange_id': 'SSE',
             'float_profit_today': 6.0000000000030695,
             'hold_profit': -7.0,
             'instrument_id': '603666',
             'last_price': 75.69,
             'market_value': 15138.0,
             'market_value_his': 0.0,
             'profit_rate_today': 0.000396170353252101,
             'profit_rate_total': -0.00046219874546054804,
             'profit_today': 6.0000000000030695,
             'profit_total': -7.0,
             'real_profit_his': 0.0,
             'real_profit_today': 0.0,
             'real_profit_total': 0.0,
             'sell_balance_his': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_his': 0.0,
             'sell_fee_today': 0.0,
             'sell_float_profit_today': 0.0,
             'sell_volume_frozen': 0,
             'sell_volume_his': 0,
             'sell_volume_today': 0,
             'shared_volume_today': 0,
             'user_id': 'TQSIM',
             'volume': 200,
             'volume_his': 0},
            positions["SSE.603666"]
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'exchange_id': 'SSE',
             'instrument_id': '603666', 'direction': 'BUY', 'price_type': 'LIMIT', 'limit_price': 75.7,
             'exchange_order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870', 'volume_orign': 200,
             'volume_left': 0, 'frozen_balance': 0.0, 'frozen_fee': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1637646583510000000},
            orders['PYSDK_insert_42de71a44009a3420164af39b87a7870']
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870',
             'trade_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870|200',
             'exchange_trade_id': 'PYSDK_insert_42de71a44009a3420164af39b87a7870|200', 'exchange_id': 'SSE',
             'instrument_id': '603666', 'direction': 'BUY', 'price': 75.7, 'volume': 200,
             'trade_date_time': 1637646584510000000, 'fee': 5.0},
            trades['PYSDK_insert_42de71a44009a3420164af39b87a7870|200']
        )

    def test_trade_4(self) -> None:
        # 下单 200 手未成交
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_aaaa',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 200,
            'price_type': 'LIMIT',
            'limit_price': 75.7
        })
        self.assertEqual(2, len(diffs))
        self.assertEqual(1, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        # 下单 600 手成交
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_bbbb',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 600,
            'price_type': 'ANY'
        })
        self.assertEqual(6, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            {
             'asset': 999982.63,
             'asset_his': 1000000.0,
             'available': 939363.63,
             'available_his': 1000000.0,
             'buy_balance_today': 45480.0,
             'buy_fee_today': 11.370000000000001,
             'buy_frozen_balance': 15140.0,
             'buy_frozen_fee': 5.0,
             'cost': 45491.37,
             'cost_his': 0.0,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 0.0,
             'drawable': 939363.63,
             'float_profit_today': -17.36999999999682,
             'hold_profit': -17.369999999995343,
             'market_value': 45474.00000000001,
             'market_value_his': 0.0,
             'profit_rate_today': -0.0003818306637060352,
             'profit_today': -17.36999999999682,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'exchange_id': 'SSE', 'instrument_id': '603666', 'create_date': '2021-11-23',
             'volume_his': 0, 'cost_his': 0.0, 'market_value_his': 0.0, 'real_profit_his': 0.0,
             'shared_volume_today': 0, 'devidend_balance_today': 0.0, 'buy_volume_his': 0, 'buy_balance_his': 0.0,
             'buy_fee_his': 0.0, 'sell_volume_his': 0, 'sell_balance_his': 0.0, 'sell_fee_his': 0.0,
             'buy_volume_today': 600, 'buy_balance_today': 45480.0, 'buy_fee_today': 11.370000000000001,
             'sell_volume_today': 0, 'sell_balance_today': 0.0, 'sell_fee_today': 0.0, 'last_price': 75.79,
             'sell_volume_frozen': 0, 'sell_float_profit_today': 0.0, 'buy_float_profit_today': -17.36999999999682,
             'cost': 45491.37, 'volume': 600, 'market_value': 45474.00000000001,
             'float_profit_today': -17.36999999999682, 'real_profit_today': 0.0, 'profit_today': -17.36999999999682,
             'profit_rate_today': -0.0003818306637060352, 'hold_profit': -17.369999999995343, 'real_profit_total': 0.0,
             'profit_total': -17.369999999995343, 'profit_rate_total': -0.00038183066370600275,
             'buy_avg_price': 75.81895},
            positions["SSE.603666"]
        )
        self.assertEqual(
            {'direction': 'BUY',
             'exchange_id': 'SSE',
             'exchange_order_id': 'PYSDK_insert_aaaa',
             'frozen_balance': 0.0,
             'frozen_fee': 0.0,
             'insert_date_time': 1637646583510000000,
             'instrument_id': '603666',
             'last_msg': '报单成功',
             'limit_price': 75.7,
             'order_id': 'PYSDK_insert_aaaa',
             'price_type': 'LIMIT',
             'status': 'ALIVE',
             'user_id': 'TQSIM',
             'volume_left': 200,
             'volume_orign': 200},
            orders['PYSDK_insert_aaaa']
        )
        self.assertEqual(
            {'direction': 'BUY',
             'exchange_id': 'SSE',
             'exchange_order_id': 'PYSDK_insert_bbbb',
             'frozen_balance': 0.0,
             'frozen_fee': 0.0,
             'insert_date_time': 1637646583510000000,
             'instrument_id': '603666',
             'last_msg': '全部成交',
             'order_id': 'PYSDK_insert_bbbb',
             'price_type': 'ANY',
             'status': 'FINISHED',
             'user_id': 'TQSIM',
             'volume_left': 0,
             'volume_orign': 600},
            orders['PYSDK_insert_bbbb']
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_bbbb', 'trade_id': 'PYSDK_insert_bbbb|600',
             'exchange_trade_id': 'PYSDK_insert_bbbb|600', 'exchange_id': 'SSE', 'instrument_id': '603666',
             'direction': 'BUY', 'price': 75.8, 'volume': 600, 'trade_date_time': 1637646583510000000,
             'fee': 11.370000000000001},
            trades['PYSDK_insert_bbbb|600']
        )

        # 结算
        diffs, orders_events, trade_log = self.sim_trade.settle()
        self.assertEqual(len(diffs), 3)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        self.assertEqual(
            {
             'asset': 999982.63,
             'asset_his': 999982.63,
             'available': 954508.63,
             'available_his': 954508.63,
             'buy_balance_today': 0.0,
             'buy_fee_today': 0.0,
             'buy_frozen_balance': 0.0,
             'buy_frozen_fee': 0.0,
             'cost': 45491.37,
             'cost_his': 45491.37,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 0.0,
             'drawable': 954508.63,
             'float_profit_today': 0.0,
             'hold_profit': 0.0,
             'market_value': 45474.00000000001,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': 0.0,
             'profit_today': 0.0,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'exchange_id': 'SSE', 'instrument_id': '603666', 'create_date': '2021-11-23',
             'volume_his': 600, 'cost_his': 45491.37, 'market_value_his': 45474.00000000001, 'real_profit_his': 0.0,
             'shared_volume_today': 0, 'devidend_balance_today': 0.0, 'buy_volume_his': 600, 'buy_balance_his': 45480.0,
             'buy_fee_his': 11.370000000000001, 'sell_volume_his': 0, 'sell_balance_his': 0.0, 'sell_fee_his': 0.0,
             'buy_volume_today': 0, 'buy_balance_today': 0.0, 'buy_fee_today': 0.0, 'sell_volume_today': 0,
             'sell_balance_today': 0.0, 'sell_fee_today': 0.0, 'last_price': 75.79, 'sell_volume_frozen': 0,
             'sell_float_profit_today': 0.0, 'buy_float_profit_today': 0.0, 'cost': 45491.37, 'volume': 600,
             'market_value': 45474.00000000001, 'float_profit_today': 0.0, 'real_profit_today': 0.0,
             'profit_today': 0.0, 'profit_rate_today': 0.0, 'hold_profit': 0.0, 'real_profit_total': 0.0,
             'profit_total': -17.369999999995343, 'profit_rate_total': -0.00038183066370600275, 'buy_avg_price': 0.0},
            positions["SSE.603666"]
        )
        self.assertEqual(
            {'direction': 'BUY',
             'exchange_id': 'SSE',
             'exchange_order_id': 'PYSDK_insert_aaaa',
             'frozen_balance': 0.0,
             'frozen_fee': 0.0,
             'insert_date_time': 1637646583510000000,
             'instrument_id': '603666',
             'last_msg': '交易日结束，自动撤销当日有效的委托单（GFD）',
             'limit_price': 75.7,
             'order_id': 'PYSDK_insert_aaaa',
             'price_type': 'LIMIT',
             'status': 'FINISHED',
             'user_id': 'TQSIM',
             'volume_left': 200,
             'volume_orign': 200},
            orders['PYSDK_insert_aaaa']
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_bbbb', 'trade_id': 'PYSDK_insert_bbbb|600',
             'exchange_trade_id': 'PYSDK_insert_bbbb|600', 'exchange_id': 'SSE', 'instrument_id': '603666',
             'direction': 'BUY', 'price': 75.8, 'volume': 600, 'trade_date_time': 1637646583510000000,
             'fee': 11.370000000000001},
            trades['PYSDK_insert_bbbb|600']
        )

    def test_trade_5(self) -> None:
        # 下单 200 手未成交, 撤单
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_aaaa',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 200,
            'price_type': 'LIMIT',
            'limit_price': 75.7
        })
        self.assertEqual(2, len(diffs))
        self.assertEqual(1, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            {
             'asset': 1000000.0,
             'asset_his': 1000000.0,
             'available': 984855.0,
             'available_his': 1000000.0,
             'buy_balance_today': 0.0,
             'buy_fee_today': 0.0,
             'buy_frozen_balance': 15140.0,
             'buy_frozen_fee': 5.0,
             'cost': 0.0,
             'cost_his': 0.0,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 0.0,
             'drawable': 984855.0,
             'float_profit_today': 0.0,
             'hold_profit': 0.0,
             'market_value': 0.0,
             'market_value_his': 0.0,
             'profit_rate_today': 0.0,
             'profit_today': 0.0,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account
        )
        self.assertEqual(
            {'buy_balance_his': 0.0,
             'buy_balance_today': 0.0,
             'buy_fee_his': 0.0,
             'buy_fee_today': 0.0,
             'buy_float_profit_today': 0.0,
             'buy_volume_his': 0,
             'buy_volume_today': 0,
             'cost': 0.0,
             'cost_his': 0.0,
             'create_date': '',
             'devidend_balance_today': 0.0,
             'exchange_id': 'SSE',
             'float_profit_today': 0.0,
             'hold_profit': 0.0,
             'instrument_id': '603666',
             'last_price': 75.79,
             'market_value': 0.0,
             'market_value_his': 0.0,
             'profit_rate_today': 0.0,
             'profit_rate_total': 0.0,
             'profit_today': 0.0,
             'profit_total': 0.0,
             'real_profit_his': 0.0,
             'real_profit_today': 0.0,
             'real_profit_total': 0.0,
             'sell_balance_his': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_his': 0.0,
             'sell_fee_today': 0.0,
             'sell_float_profit_today': 0.0,
             'sell_volume_frozen': 0,
             'sell_volume_his': 0,
             'sell_volume_today': 0,
             'shared_volume_today': 0,
             'user_id': 'TQSIM',
             'volume': 0,
             'volume_his': 0},
            positions["SSE.603666"]
        )
        self.assertEqual(
            {'direction': 'BUY',
             'exchange_id': 'SSE',
             'exchange_order_id': 'PYSDK_insert_aaaa',
             'frozen_balance': 0.0,
             'frozen_fee': 0.0,
             'insert_date_time': 1637646583510000000,
             'instrument_id': '603666',
             'last_msg': '报单成功',
             'limit_price': 75.7,
             'order_id': 'PYSDK_insert_aaaa',
             'price_type': 'LIMIT',
             'status': 'ALIVE',
             'user_id': 'TQSIM',
             'volume_left': 200,
             'volume_orign': 200},
            orders['PYSDK_insert_aaaa']
        )
        self.assertEqual({}, trades)
        # 下单 600 手成交
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_bbbb',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 600,
            'price_type': 'ANY'
        })
        self.assertEqual(6, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        self.assertEqual(
            {
             'asset': 999982.63,
             'asset_his': 1000000.0,
             'available': 939363.63,
             'available_his': 1000000.0,
             'buy_balance_today': 45480.0,
             'buy_fee_today': 11.370000000000001,
             'buy_frozen_balance': 15140.0,
             'buy_frozen_fee': 5.0,
             'cost': 45491.37,
             'cost_his': 0.0,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 0.0,
             'drawable': 939363.63,
             'float_profit_today': -17.36999999999682,
             'hold_profit': -17.369999999995343,
             'market_value': 45474.00000000001,
             'market_value_his': 0.0,
             'profit_rate_today': -0.0003818306637060352,
             'profit_today': -17.36999999999682,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'exchange_id': 'SSE', 'instrument_id': '603666', 'create_date': '2021-11-23',
             'volume_his': 0, 'cost_his': 0.0, 'market_value_his': 0.0, 'real_profit_his': 0.0,
             'shared_volume_today': 0, 'devidend_balance_today': 0.0, 'buy_volume_his': 0, 'buy_balance_his': 0.0,
             'buy_fee_his': 0.0, 'sell_volume_his': 0, 'sell_balance_his': 0.0, 'sell_fee_his': 0.0,
             'buy_volume_today': 600, 'buy_balance_today': 45480.0, 'buy_fee_today': 11.370000000000001,
             'sell_volume_today': 0, 'sell_balance_today': 0.0, 'sell_fee_today': 0.0, 'last_price': 75.79,
             'sell_volume_frozen': 0, 'sell_float_profit_today': 0.0, 'buy_float_profit_today': -17.36999999999682,
             'cost': 45491.37, 'volume': 600, 'market_value': 45474.00000000001,
             'float_profit_today': -17.36999999999682, 'real_profit_today': 0.0, 'profit_today': -17.36999999999682,
             'profit_rate_today': -0.0003818306637060352, 'hold_profit': -17.369999999995343, 'real_profit_total': 0.0,
             'profit_total': -17.369999999995343, 'profit_rate_total': -0.00038183066370600275,
             'buy_avg_price': 75.81895},
            positions["SSE.603666"]
        )
        self.assertEqual(
            {'direction': 'BUY',
             'exchange_id': 'SSE',
             'exchange_order_id': 'PYSDK_insert_aaaa',
             'frozen_balance': 0.0,
             'frozen_fee': 0.0,
             'insert_date_time': 1637646583510000000,
             'instrument_id': '603666',
             'last_msg': '报单成功',
             'limit_price': 75.7,
             'order_id': 'PYSDK_insert_aaaa',
             'price_type': 'LIMIT',
             'status': 'ALIVE',
             'user_id': 'TQSIM',
             'volume_left': 200,
             'volume_orign': 200},
            orders['PYSDK_insert_aaaa']
        )
        self.assertEqual(
            {'direction': 'BUY',
             'exchange_id': 'SSE',
             'exchange_order_id': 'PYSDK_insert_bbbb',
             'frozen_balance': 0.0,
             'frozen_fee': 0.0,
             'insert_date_time': 1637646583510000000,
             'instrument_id': '603666',
             'last_msg': '全部成交',
             'order_id': 'PYSDK_insert_bbbb',
             'price_type': 'ANY',
             'status': 'FINISHED',
             'user_id': 'TQSIM',
             'volume_left': 0,
             'volume_orign': 600},
            orders['PYSDK_insert_bbbb']
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_bbbb', 'trade_id': 'PYSDK_insert_bbbb|600',
             'exchange_trade_id': 'PYSDK_insert_bbbb|600', 'exchange_id': 'SSE', 'instrument_id': '603666',
             'direction': 'BUY', 'price': 75.8, 'volume': 600, 'trade_date_time': 1637646583510000000,
             'fee': 11.370000000000001},
            trades['PYSDK_insert_bbbb|600']
        )

        # 撤单
        diffs, orders_events = self.sim_trade.cancel_order("SSE.603666", {
            "aid": "cancel_order",
            "order_id": "PYSDK_insert_aaaa"
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        self.assertEqual(
            {
             'asset': 999982.63,
             'asset_his': 1000000.0,
             'available': 954508.63,
             'available_his': 1000000.0,
             'buy_balance_today': 45480.0,
             'buy_fee_today': 11.370000000000001,
             'buy_frozen_balance': 0.0,
             'buy_frozen_fee': 0.0,
             'cost': 45491.37,
             'cost_his': 0.0,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 0.0,
             'drawable': 954508.63,
             'float_profit_today': -17.36999999999682,
             'hold_profit': -17.369999999995343,
             'market_value': 45474.00000000001,
             'market_value_his': 0.0,
             'profit_rate_today': -0.0003818306637060352,
             'profit_today': -17.36999999999682,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account
        )
        self.assertEqual(
            {'buy_avg_price': 75.81895,
             'buy_balance_his': 0.0,
             'buy_balance_today': 45480.0,
             'buy_fee_his': 0.0,
             'buy_fee_today': 11.370000000000001,
             'buy_float_profit_today': -17.36999999999682,
             'buy_volume_his': 0,
             'buy_volume_today': 600,
             'cost': 45491.37,
             'cost_his': 0.0,
             'create_date': '2021-11-23',
             'devidend_balance_today': 0.0,
             'exchange_id': 'SSE',
             'float_profit_today': -17.36999999999682,
             'hold_profit': -17.369999999995343,
             'instrument_id': '603666',
             'last_price': 75.79,
             'market_value': 45474.00000000001,
             'market_value_his': 0.0,
             'profit_rate_today': -0.0003818306637060352,
             'profit_rate_total': -0.00038183066370600275,
             'profit_today': -17.36999999999682,
             'profit_total': -17.369999999995343,
             'real_profit_his': 0.0,
             'real_profit_today': 0.0,
             'real_profit_total': 0.0,
             'sell_balance_his': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_his': 0.0,
             'sell_fee_today': 0.0,
             'sell_float_profit_today': 0.0,
             'sell_volume_frozen': 0,
             'sell_volume_his': 0,
             'sell_volume_today': 0,
             'shared_volume_today': 0,
             'user_id': 'TQSIM',
             'volume': 600,
             'volume_his': 0},
            positions["SSE.603666"]
        )
        self.assertEqual(
            {'direction': 'BUY',
             'exchange_id': 'SSE',
             'exchange_order_id': 'PYSDK_insert_aaaa',
             'frozen_balance': 0.0,
             'frozen_fee': 0.0,
             'insert_date_time': 1637646583510000000,
             'instrument_id': '603666',
             'last_msg': '已撤单',
             'limit_price': 75.7,
             'order_id': 'PYSDK_insert_aaaa',
             'price_type': 'LIMIT',
             'status': 'FINISHED',
             'user_id': 'TQSIM',
             'volume_left': 200,
             'volume_orign': 200},
            orders['PYSDK_insert_aaaa']
        )
        diffs, orders_events = self.sim_trade.cancel_order("SSE.603666", {
            "aid": "cancel_order",
            "order_id": "PYSDK_insert_bbbb"
        })
        self.assertEqual(len(diffs), 0)
        self.assertEqual(len(orders_events), 0)


class TestSimTradeStock3(unittest.TestCase):
    """
    测试天勤模拟股票交易类
    setUp: 下单，结算
    行情更新 -> 卖平 (不在交易时间段) -> 卖平 (手数不足)
    行情更新 -> 买开 -> 卖平
    """

    def setUp(self) -> None:
        # 构造初始持仓
        self.sim_trade = SimTradeStock(account_key="abc", account_id="TQSIM", init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        diffs, orders_events = self.sim_trade.update_quotes("SSE.603666", {
            'quotes': {
                'SSE.603666': {
                    'datetime': '2021-11-23 13:49:43.510000', 'ins_class': 'STOCK', 'instrument_id': 'SSE.603666',
                    'instrument_name': '亿嘉和', 'exchange_id': 'SSE', 'expired': False,
                    'trading_time': {"day": [["09:30:00", "11:30:00"], ["13:00:00", "15:00:00"]], "night": []},
                    'ask_price1': 75.8, 'ask_volume1': 19700, 'bid_price1': 75.79, 'bid_volume1': 1600,
                    'last_price': 75.79, 'highest': 76.8, 'lowest': 73.73, 'open': 74.9,
                    'average': 74.95, 'volume': 2748961, 'amount': 206025211.0, 'open_interest': 0,
                    'upper_limit': 83.37, 'lower_limit': 68.21, 'price_tick': 0.01, 'price_decs': 2,
                    'volume_multiple': 100.0, 'max_limit_order_volume': 0, 'max_market_order_volume': 0,
                    'min_limit_order_volume': 0, 'min_market_order_volume': 0,
                    'stock_dividend_ratio': ['20181102,0.400000', '20200624,0.400000', '20210716,0.400000'],
                    'cash_dividend_ratio': ['20181102,0.140000', '20190628,0.462000', '20200624,0.260000',
                                            '20210716,0.370000']
                }
            }
        })
        self.assertEqual(len(diffs), 2)  # 一定会收到持仓和账户更新包
        self.assertEqual([], orders_events)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        # 下单 200 手未成交
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_aaaa',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 200,
            'price_type': 'LIMIT',
            'limit_price': 75.7
        })
        self.assertEqual(2, len(diffs))
        self.assertEqual(1, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        # 下单 600 手成交
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_bbbb',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 600,
            'price_type': 'ANY'
        })
        self.assertEqual(6, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        # 结算
        diffs, orders_events, trade_log = self.sim_trade.settle()
        self.assertEqual(len(diffs), 3)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            {
             'asset': 999982.63,
             'asset_his': 999982.63,
             'available': 954508.63,
             'available_his': 954508.63,
             'buy_balance_today': 0.0,
             'buy_fee_today': 0.0,
             'buy_frozen_balance': 0.0,
             'buy_frozen_fee': 0.0,
             'cost': 45491.37,
             'cost_his': 45491.37,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 0.0,
             'drawable': 954508.63,
             'float_profit_today': 0.0,
             'hold_profit': 0.0,
             'market_value': 45474.00000000001,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': 0.0,
             'profit_today': 0.0,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'exchange_id': 'SSE', 'instrument_id': '603666', 'create_date': '2021-11-23',
             'volume_his': 600, 'cost_his': 45491.37, 'market_value_his': 45474.00000000001, 'real_profit_his': 0.0,
             'shared_volume_today': 0, 'devidend_balance_today': 0.0, 'buy_volume_his': 600, 'buy_balance_his': 45480.0,
             'buy_fee_his': 11.370000000000001, 'sell_volume_his': 0, 'sell_balance_his': 0.0, 'sell_fee_his': 0.0,
             'buy_volume_today': 0, 'buy_balance_today': 0.0, 'buy_fee_today': 0.0, 'sell_volume_today': 0,
             'sell_balance_today': 0.0, 'sell_fee_today': 0.0, 'last_price': 75.79, 'sell_volume_frozen': 0,
             'sell_float_profit_today': 0.0, 'buy_float_profit_today': 0.0, 'cost': 45491.37, 'volume': 600,
             'market_value': 45474.00000000001, 'float_profit_today': 0.0, 'real_profit_today': 0.0,
             'profit_today': 0.0, 'profit_rate_today': 0.0, 'hold_profit': 0.0, 'real_profit_total': 0.0,
             'profit_total': -17.369999999995343, 'profit_rate_total': -0.00038183066370600275, 'buy_avg_price': 0.0},
            positions["SSE.603666"]
        )

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_stock_1(self):
        """行情更新"""
        diffs, orders_events = self.sim_trade.update_quotes("SSE.603666", {
            'quotes': {
                'SSE.603666': {
                    'datetime': '2021-11-24 09:10:00.510000',
                    'ask_price1': 75.7, 'last_price': 75.69, 'bid_price1': 75.69
                }
            }
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            {
             'asset': 999922.63,
             'asset_his': 999982.63,
             'available': 954508.63,
             'available_his': 954508.63,
             'buy_balance_today': 0.0,
             'buy_fee_today': 0.0,
             'buy_frozen_balance': 0.0,
             'buy_frozen_fee': 0.0,
             'cost': 45491.37,
             'cost_his': 45491.37,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 0.0,
             'drawable': 954508.63,
             'float_profit_today': -60.000000000005116,
             'hold_profit': -77.37000000000262,
             'market_value': 45414.0,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': -0.0013189314808502164,
             'profit_today': -60.000000000005116,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account
        )
        self.assertEqual(
            {'buy_avg_price': 0.0,
             'buy_balance_his': 45480.0,
             'buy_balance_today': 0.0,
             'buy_fee_his': 11.370000000000001,
             'buy_fee_today': 0.0,
             'buy_float_profit_today': 0.0,
             'buy_volume_his': 600,
             'buy_volume_today': 0,
             'cost': 45491.37,
             'cost_his': 45491.37,
             'create_date': '2021-11-23',
             'devidend_balance_today': 0.0,
             'exchange_id': 'SSE',
             'float_profit_today': -60.000000000005116,
             'hold_profit': -60.000000000007276,
             'instrument_id': '603666',
             'last_price': 75.69,
             'market_value': 45414.0,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': -0.0013189314808502164,
             'profit_rate_total': -0.0017007621445562667,
             'profit_today': -60.000000000005116,
             'profit_total': -77.37000000000262,
             'real_profit_his': 0.0,
             'real_profit_today': 0.0,
             'real_profit_total': 0.0,
             'sell_balance_his': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_his': 0.0,
             'sell_fee_today': 0.0,
             'sell_float_profit_today': -60.000000000005116,
             'sell_volume_frozen': 0,
             'sell_volume_his': 0,
             'sell_volume_today': 0,
             'shared_volume_today': 0,
             'user_id': 'TQSIM',
             'volume': 600,
             'volume_his': 600},
            positions["SSE.603666"]
        )

        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_1',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'SELL',
            'volume': 800,
            'price_type': 'LIMIT',
            'limit_price': 76.7
        })
        self.assertEqual(2, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_1', 'exchange_id': 'SSE', 'instrument_id': '603666',
             'direction': 'SELL', 'price_type': 'LIMIT', 'limit_price': 76.7, 'exchange_order_id': 'PYSDK_insert_1',
             'volume_orign': 800, 'volume_left': 800, 'frozen_balance': 0.0, 'frozen_fee': 0.0, 'last_msg': '报单成功',
             'status': 'ALIVE', 'insert_date_time': 1637716200510000000},
            orders_events[0]
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_1', 'exchange_id': 'SSE', 'instrument_id': '603666',
             'direction': 'SELL', 'price_type': 'LIMIT', 'limit_price': 76.7, 'exchange_order_id': 'PYSDK_insert_1',
             'volume_orign': 800, 'volume_left': 800, 'frozen_balance': 0.0, 'frozen_fee': 0.0,
             'last_msg': '下单失败, 不在可交易时间段内', 'status': 'FINISHED', 'insert_date_time': 1637716200510000000},
            orders_events[1]
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_1', 'exchange_id': 'SSE', 'instrument_id': '603666', 'direction': 'SELL', 'price_type': 'LIMIT', 'limit_price': 76.7, 'exchange_order_id': 'PYSDK_insert_1', 'volume_orign': 800, 'volume_left': 800, 'frozen_balance': 0.0, 'frozen_fee': 0.0, 'last_msg': '下单失败, 不在可交易时间段内', 'status': 'FINISHED', 'insert_date_time': 1637716200510000000},
            orders['PYSDK_insert_1']
        )

        # 更新行情，时间推进
        diffs, orders_events = self.sim_trade.update_quotes("SSE.603666", {
            'quotes': {
                'SSE.603666': {
                    'datetime': '2021-11-24 09:30:02.510000',
                    'ask_price1': 75.7, 'last_price': 75.69, 'bid_price1': 75.69
                }
            }
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_2',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'SELL',
            'volume': 800,
            'price_type': 'LIMIT',
            'limit_price': 76.7
        })
        self.assertEqual(2, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_2', 'exchange_id': 'SSE', 'instrument_id': '603666',
             'direction': 'SELL', 'price_type': 'LIMIT', 'limit_price': 76.7, 'exchange_order_id': 'PYSDK_insert_2',
             'volume_orign': 800, 'volume_left': 800, 'frozen_balance': 0.0, 'frozen_fee': 0.0, 'last_msg': '报单成功',
             'status': 'ALIVE', 'insert_date_time': 1637717402510000000},
            orders_events[0]
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_2', 'exchange_id': 'SSE', 'instrument_id': '603666',
             'direction': 'SELL', 'price_type': 'LIMIT', 'limit_price': 76.7, 'exchange_order_id': 'PYSDK_insert_2',
             'volume_orign': 800, 'volume_left': 800, 'frozen_balance': 0.0, 'frozen_fee': 0.0, 'last_msg': '平仓手数不足',
             'status': 'FINISHED', 'insert_date_time': 1637717402510000000},
            orders_events[1]
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_2', 'exchange_id': 'SSE', 'instrument_id': '603666',
             'direction': 'SELL', 'price_type': 'LIMIT', 'limit_price': 76.7, 'exchange_order_id': 'PYSDK_insert_2',
             'volume_orign': 800, 'volume_left': 800, 'frozen_balance': 0.0, 'frozen_fee': 0.0, 'last_msg': '平仓手数不足',
             'status': 'FINISHED', 'insert_date_time': 1637717402510000000},
            orders['PYSDK_insert_2']
        )

    def test_trade_stock_2(self):
        diffs, orders_events = self.sim_trade.update_quotes("SSE.603666", {
            'quotes': {
                'SSE.603666': {
                    'datetime': '2021-11-24 09:30:00.510000',
                    'ask_price1': 76.0, 'last_price': 75.9, 'bid_price1': 75.89
                }
            }
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            {'asset': 1000048.63,
             'asset_his': 999982.63,
             'available': 954508.63,
             'available_his': 954508.63,
             'buy_balance_today': 0.0,
             'buy_fee_today': 0.0,
             'buy_frozen_balance': 0.0,
             'buy_frozen_fee': 0.0,
             'cost': 45491.37,
             'cost_his': 45491.37,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 0.0,
             'drawable': 954508.63,
             'float_profit_today': 65.99999999999966,
             'hold_profit': 48.62999999999738,
             'market_value': 45540.0,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': 0.001450824628935107,
             'profit_today': 65.99999999999966,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account
        )
        self.assertEqual(
            {'buy_avg_price': 0.0,
             'buy_balance_his': 45480.0,
             'buy_balance_today': 0.0,
             'buy_fee_his': 11.370000000000001,
             'buy_fee_today': 0.0,
             'buy_float_profit_today': 0.0,
             'buy_volume_his': 600,
             'buy_volume_today': 0,
             'cost': 45491.37,
             'cost_his': 45491.37,
             'create_date': '2021-11-23',
             'devidend_balance_today': 0.0,
             'exchange_id': 'SSE',
             'float_profit_today': 65.99999999999966,
             'hold_profit': 65.99999999999272,
             'instrument_id': '603666',
             'last_price': 75.9,
             'market_value': 45540.0,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': 0.001450824628935107,
             'profit_rate_total': 0.0010689939652289517,
             'profit_today': 65.99999999999966,
             'profit_total': 48.62999999999738,
             'real_profit_his': 0.0,
             'real_profit_today': 0.0,
             'real_profit_total': 0.0,
             'sell_balance_his': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_his': 0.0,
             'sell_fee_today': 0.0,
             'sell_float_profit_today': 65.99999999999966,
             'sell_volume_frozen': 0,
             'sell_volume_his': 0,
             'sell_volume_today': 0,
             'shared_volume_today': 0,
             'user_id': 'TQSIM',
             'volume': 600,
             'volume_his': 600},
            positions["SSE.603666"]
        )

        # 下单
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_1',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 300,
            'price_type': 'LIMIT',
            'limit_price': 76.2
        })
        self.assertEqual(6, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        self.assertEqual(
            {
             'asset': 999952.915,
             'asset_his': 999982.63,
             'available': 931642.915,
             'available_his': 954508.63,
             'buy_balance_today': 22860.0,
             'buy_fee_today': 5.715,
             'buy_frozen_balance': 0.0,
             'buy_frozen_fee': 0.0,
             'cost': 68357.085,
             'cost_his': 45491.37,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 0.0,
             'drawable': 931642.915,
             'float_profit_today': -29.71499999999736,
             'hold_profit': -47.0850000000064,
             'market_value': 68310.0,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': -0.0004347025622873965,
             'profit_today': -29.71499999999736,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account
        )
        self.assertEqual(
            {'buy_avg_price': 76.21905,
             'buy_balance_his': 45480.0,
             'buy_balance_today': 22860.0,
             'buy_fee_his': 11.370000000000001,
             'buy_fee_today': 5.715,
             'buy_float_profit_today': -95.71499999999702,
             'buy_volume_his': 600,
             'buy_volume_today': 300,
             'cost': 68357.085,
             'cost_his': 45491.37,
             'create_date': '2021-11-23',
             'devidend_balance_today': 0.0,
             'exchange_id': 'SSE',
             'float_profit_today': -29.71499999999736,
             'hold_profit': -29.71500000000742,
             'instrument_id': '603666',
             'last_price': 75.9,
             'market_value': 68310.0,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': -0.0004347025622873965,
             'profit_rate_total': -0.0006888093604342953,
             'profit_today': -29.71499999999736,
             'profit_total': -47.085000000002765,
             'real_profit_his': 0.0,
             'real_profit_today': 0.0,
             'real_profit_total': 0.0,
             'sell_balance_his': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_his': 0.0,
             'sell_fee_today': 0.0,
             'sell_float_profit_today': 65.99999999999966,
             'sell_volume_frozen': 0,
             'sell_volume_his': 0,
             'sell_volume_today': 0,
             'shared_volume_today': 0,
             'user_id': 'TQSIM',
             'volume': 900,
             'volume_his': 600},
            positions["SSE.603666"]
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_1', 'exchange_id': 'SSE', 'instrument_id': '603666',
             'direction': 'BUY', 'price_type': 'LIMIT', 'limit_price': 76.2, 'exchange_order_id': 'PYSDK_insert_1',
             'volume_orign': 300, 'volume_left': 0, 'frozen_balance': 0.0, 'frozen_fee': 0.0, 'last_msg': '全部成交',
             'status': 'FINISHED', 'insert_date_time': 1637717400510000000},
            orders['PYSDK_insert_1']
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_1', 'trade_id': 'PYSDK_insert_1|300',
             'exchange_trade_id': 'PYSDK_insert_1|300', 'exchange_id': 'SSE', 'instrument_id': '603666',
             'direction': 'BUY', 'price': 76.2, 'volume': 300, 'trade_date_time': 1637717400510000000, 'fee': 5.715},
            trades['PYSDK_insert_1|300']
        )

        # 下单
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_1',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'SELL',
            'volume': 400,
            'price_type': 'ANY'
        })
        self.assertEqual(6, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        self.assertEqual(
            {'user_id': 'TQSIM',  'currency': 'CNY', 'market_value_his': 45474.00000000001,
             'asset_his': 999982.63, 'cost_his': 45491.37, 'deposit': 0.0, 'withdraw': 0.0,
             'dividend_balance_today': 0.0, 'available_his': 954508.63, 'market_value': 37950.0,
             'asset': 999910.9700000001, 'available': 961960.9700000001, 'drawable': 954508.63,
             'buy_frozen_balance': 0.0, 'buy_frozen_fee': 0.0, 'buy_balance_today': 22860.0, 'buy_fee_today': 5.715,
             'sell_balance_today': 30356.0, 'sell_fee_today': 37.945, 'cost': 38029.505000000005,
             'hold_profit': -79.50500000000466, 'float_profit_today': -7.714999999997474,
             'real_profit_today': 43.99999999999977, 'profit_today': 36.2850000000023,
             'profit_rate_today': 0.0009541275911953704},
            account
        )
        self.assertEqual(
            {'buy_avg_price': 76.21905,
             'buy_balance_his': 45480.0,
             'buy_balance_today': 22860.0,
             'buy_fee_his': 11.370000000000001,
             'buy_fee_today': 5.715,
             'buy_float_profit_today': -95.71499999999702,
             'buy_volume_his': 600,
             'buy_volume_today': 300,
             'cost': 38029.505000000005,
             'cost_his': 45491.37,
             'create_date': '2021-11-23',
             'devidend_balance_today': 0.0,
             'exchange_id': 'SSE',
             'float_profit_today': -7.714999999997474,
             'hold_profit': -62.13500000000931,
             'instrument_id': '603666',
             'last_price': 75.9,
             'market_value': 37950.0,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': 0.0009541275911953704,
             'profit_rate_total': -0.0009336172006447331,
             'profit_today': 36.2850000000023,
             'profit_total': -35.505000000004884,
             'real_profit_his': 0.0,
             'real_profit_today': 43.99999999999977,
             'real_profit_total': 43.99999999999977,
             'sell_balance_his': 0.0,
             'sell_balance_today': 30356.0,
             'sell_fee_his': 0.0,
             'sell_fee_today': 37.945,
             'sell_float_profit_today': 87.99999999999955,
             'sell_volume_frozen': 0,
             'sell_volume_his': 0,
             'sell_volume_today': 400,
             'shared_volume_today': 0,
             'user_id': 'TQSIM',
             'volume': 500,
             'volume_his': 600},
            positions["SSE.603666"]
        )
        self.assertEqual(
            {'direction': 'SELL',
             'exchange_id': 'SSE',
             'exchange_order_id': 'PYSDK_insert_1',
             'frozen_balance': 0.0,
             'frozen_fee': 0.0,
             'insert_date_time': 1637717400510000000,
             'instrument_id': '603666',
             'last_msg': '全部成交',
             'limit_price': 76.2,
             'order_id': 'PYSDK_insert_1',
             'price_type': 'ANY',
             'status': 'FINISHED',
             'user_id': 'TQSIM',
             'volume_left': 0,
             'volume_orign': 400},
            orders['PYSDK_insert_1']
        )
        self.assertEqual(
            {'direction': 'SELL',
             'exchange_id': 'SSE',
             'exchange_trade_id': 'PYSDK_insert_1|400',
             'fee': 37.945,
             'instrument_id': '603666',
             'order_id': 'PYSDK_insert_1',
             'price': 75.89,
             'trade_date_time': 1637717400510000000,
             'trade_id': 'PYSDK_insert_1|400',
             'user_id': 'TQSIM',
             'volume': 400},
            trades['PYSDK_insert_1|400']
        )


class TestSimTradeStock4(unittest.TestCase):
    """
    测试天勤模拟股票交易类
    setUp: 下单
    结算(送股，分红) -> 行情更新 -> 卖平
    """

    def setUp(self) -> None:
        # 构造初始持仓
        self.sim_trade = SimTradeStock(account_key="abc", account_id="TQSIM", init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        diffs, orders_events = self.sim_trade.update_quotes("SSE.603666", {
            'quotes': {
                'SSE.603666': {
                    'datetime': '2021-07-15 13:49:43.510000', 'ins_class': 'STOCK', 'instrument_id': 'SSE.603666',
                    'instrument_name': '亿嘉和', 'exchange_id': 'SSE', 'expired': False,
                    'trading_time': {"day": [["09:30:00", "11:30:00"], ["13:00:00", "15:00:00"]], "night": []},
                    'ask_price1': 75.8, 'ask_volume1': 19700, 'bid_price1': 75.79, 'bid_volume1': 1600,
                    'last_price': 75.79, 'highest': 76.8, 'lowest': 73.73, 'open': 74.9,
                    'average': 74.95, 'volume': 2748961, 'amount': 206025211.0, 'open_interest': 0,
                    'upper_limit': 83.37, 'lower_limit': 68.21, 'price_tick': 0.01, 'price_decs': 2,
                    'volume_multiple': 100.0, 'max_limit_order_volume': 0, 'max_market_order_volume': 0,
                    'min_limit_order_volume': 0, 'min_market_order_volume': 0,
                    'stock_dividend_ratio': ['20181102,0.400000', '20200624,0.400000', '20210716,0.400000'],
                    'cash_dividend_ratio': ['20181102,0.140000', '20190628,0.462000', '20200624,0.260000', '20210716,0.370000']
                }
            }
        })
        self.assertEqual(len(diffs), 2)  # 一定会收到持仓和账户更新包
        self.assertEqual([], orders_events)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        # 下单 200 手未成交
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_aaaa',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 200,
            'price_type': 'LIMIT',
            'limit_price': 75.7
        })
        self.assertEqual(2, len(diffs))
        self.assertEqual(1, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        # 下单 600 手成交
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_bbbb',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'BUY',
            'volume': 600,
            'price_type': 'ANY'
        })
        self.assertEqual(6, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            {
             'asset': 999982.63,
             'asset_his': 1000000.0,
             'available': 939363.63,
             'available_his': 1000000.0,
             'buy_balance_today': 45480.0,
             'buy_fee_today': 11.370000000000001,
             'buy_frozen_balance': 15140.0,
             'buy_frozen_fee': 5.0,
             'cost': 45491.37,
             'cost_his': 0.0,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 0.0,
             'drawable': 939363.63,
             'float_profit_today': -17.36999999999682,
             'hold_profit': -17.369999999995343,
             'market_value': 45474.00000000001,
             'market_value_his': 0.0,
             'profit_rate_today': -0.0003818306637060352,
             'profit_today': -17.36999999999682,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account)
        self.assertEqual(
            {'buy_avg_price': 75.81895,
             'buy_balance_his': 0.0,
             'buy_balance_today': 45480.0,
             'buy_fee_his': 0.0,
             'buy_fee_today': 11.370000000000001,
             'buy_float_profit_today': -17.36999999999682,
             'buy_volume_his': 0,
             'buy_volume_today': 600,
             'cost': 45491.37,
             'cost_his': 0.0,
             'create_date': '2021-07-15',
             'devidend_balance_today': 0.0,
             'exchange_id': 'SSE',
             'float_profit_today': -17.36999999999682,
             'hold_profit': -17.369999999995343,
             'instrument_id': '603666',
             'last_price': 75.79,
             'market_value': 45474.00000000001,
             'market_value_his': 0.0,
             'profit_rate_today': -0.0003818306637060352,
             'profit_rate_total': -0.00038183066370600275,
             'profit_today': -17.36999999999682,
             'profit_total': -17.369999999995343,
             'real_profit_his': 0.0,
             'real_profit_today': 0.0,
             'real_profit_total': 0.0,
             'sell_balance_his': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_his': 0.0,
             'sell_fee_today': 0.0,
             'sell_float_profit_today': 0.0,
             'sell_volume_frozen': 0,
             'sell_volume_his': 0,
             'sell_volume_today': 0,
             'shared_volume_today': 0,
             'user_id': 'TQSIM',
             'volume': 600,
             'volume_his': 0},
            positions["SSE.603666"])

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_stock(self):
        self.trade_stock_1()
        self.trade_stock_2()

    def trade_stock_1(self):
        """结算"""
        diffs, orders_events, trade_log = self.sim_trade.settle()
        self.assertEqual(len(diffs), 3)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            {
             'asset': 1000204.63,
             'asset_his': 999982.63,
             'available': 954952.63,
             'available_his': 954508.63,
             'buy_balance_today': 0.0,
             'buy_fee_today': 0.0,
             'buy_frozen_balance': 0.0,
             'buy_frozen_fee': 0.0,
             'cost': 45491.37,
             'cost_his': 45491.37,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 222.0,
             'drawable': 954952.63,
             'float_profit_today': 0.0,
             'hold_profit': 0.0,
             'market_value': 45252.00000000001,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': 0.0,
             'profit_today': 0.0,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0}
            ,
            account
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'exchange_id': 'SSE', 'instrument_id': '603666', 'create_date': '2021-07-15',
             'volume_his': 600, 'cost_his': 45491.37, 'market_value_his': 45474.00000000001, 'real_profit_his': 0.0,
             'shared_volume_today': 240.0, 'devidend_balance_today': 222.0, 'buy_volume_his': 600,
             'buy_balance_his': 45480.0, 'buy_fee_his': 11.370000000000001, 'sell_volume_his': 0,
             'sell_balance_his': 0.0, 'sell_fee_his': 0.0, 'buy_volume_today': 0, 'buy_balance_today': 0.0,
             'buy_fee_today': 0.0, 'sell_volume_today': 0, 'sell_balance_today': 0.0, 'sell_fee_today': 0.0,
             'last_price': 53.87142857142858, 'sell_volume_frozen': 0, 'sell_float_profit_today': 0.0,
             'buy_float_profit_today': 0.0, 'cost': 45491.37, 'volume': 840.0, 'market_value': 45252.00000000001,
             'float_profit_today': 0.0, 'real_profit_today': 0.0, 'profit_today': 0.0, 'profit_rate_today': 0.0,
             'hold_profit': 0.0, 'real_profit_total': 0.0, 'profit_total': -17.369999999995343,
             'profit_rate_total': -0.00038183066370600275, 'buy_avg_price': 0.0},
            positions["SSE.603666"]
        )

    def trade_stock_2(self):
        # 更新行情
        diffs, orders_events = self.sim_trade.update_quotes("SSE.603666", {
            'quotes': {
                'SSE.603666': {
                    'datetime': '2021-07-16 9:39:43.510000',
                    'ask_price1': 77.8, 'bid_price1': 77.9, 'last_price': 77.9
                }
            }
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            {'asset': 1020388.63,
             'asset_his': 999982.63,
             'available': 954952.63,
             'available_his': 954508.63,
             'buy_balance_today': 0.0,
             'buy_fee_today': 0.0,
             'buy_frozen_balance': 0.0,
             'buy_frozen_fee': 0.0,
             'cost': 45491.37,
             'cost_his': 45491.37,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 222.0,
             'drawable': 954508.63,
             'float_profit_today': 33113.142857142855,
             'hold_profit': 19944.630000000005,
             'market_value': 65436.00000000001,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': 0.7278994424028745,
             'profit_today': 33113.142857142855,
             'real_profit_today': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_today': 0.0,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account)
        self.assertEqual(
            {'buy_avg_price': 0.0,
             'buy_balance_his': 45480.0,
             'buy_balance_today': 0.0,
             'buy_fee_his': 11.370000000000001,
             'buy_fee_today': 0.0,
             'buy_float_profit_today': 18696.0,
             'buy_volume_his': 600,
             'buy_volume_today': 0,
             'cost': 45491.37,
             'cost_his': 45491.37,
             'create_date': '2021-07-15',
             'devidend_balance_today': 222.0,
             'exchange_id': 'SSE',
             'float_profit_today': 33113.142857142855,
             'hold_profit': 20184.0,
             'instrument_id': '603666',
             'last_price': 77.9,
             'market_value': 65436.00000000001,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': 0.7278994424028745,
             'profit_rate_total': 0.443306719494269,
             'profit_today': 33113.142857142855,
             'profit_total': 20166.630000000005,
             'real_profit_his': 0.0,
             'real_profit_today': 0.0,
             'real_profit_total': 0.0,
             'sell_balance_his': 0.0,
             'sell_balance_today': 0.0,
             'sell_fee_his': 0.0,
             'sell_fee_today': 0.0,
             'sell_float_profit_today': 14417.142857142855,
             'sell_volume_frozen': 0,
             'sell_volume_his': 0,
             'sell_volume_today': 0,
             'shared_volume_today': 240.0,
             'user_id': 'TQSIM',
             'volume': 840.0,
             'volume_his': 600},
            positions['SSE.603666']
        )

        # 下单 200 手未成交
        diffs, orders_events = self.sim_trade.insert_order("SSE.603666", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_2',
            'exchange_id': 'SSE',
            'instrument_id': '603666',
            'direction': 'SELL',
            'volume': 200,
            'price_type': 'LIMIT',
            'limit_price': 75.7
        })
        self.assertEqual(6, len(diffs))
        self.assertEqual(2, len(orders_events))
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        self.assertEqual(
            {'asset': 1019928.49,
             'asset_his': 999982.63,
             'available': 970072.49,
             'available_his': 954508.63,
             'buy_balance_today': 0.0,
             'buy_fee_today': 0.0,
             'buy_frozen_balance': 0.0,
             'buy_frozen_fee': 0.0,
             'cost': 30327.58,
             'cost_his': 45491.37,
             'currency': 'CNY',
             'deposit': 0.0,
             'dividend_balance_today': 222.0,
             'drawable': 954508.63,
             'float_profit_today': 42724.57142857143,
             'hold_profit': 19528.420000000006,
             'market_value': 49856.00000000001,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': 1.567229753059285,
             'profit_today': 47530.28571428571,
             'real_profit_today': 4805.714285714284,
             'sell_balance_today': 15140.0,
             'sell_fee_today': 20.14,
             'user_id': 'TQSIM',
             'withdraw': 0.0},
            account
        )
        self.assertEqual(
            {'buy_avg_price': 0.0,
             'buy_balance_his': 45480.0,
             'buy_balance_today': 0.0,
             'buy_fee_his': 11.370000000000001,
             'buy_fee_today': 0.0,
             'buy_float_profit_today': 18696.0,
             'buy_volume_his': 600,
             'buy_volume_today': 0,
             'cost': 30327.58,
             'cost_his': 45491.37,
             'create_date': '2021-07-15',
             'devidend_balance_today': 222.0,
             'exchange_id': 'SSE',
             'float_profit_today': 42724.57142857143,
             'hold_profit': 19767.79,
             'instrument_id': '603666',
             'last_price': 77.9,
             'market_value': 49856.00000000001,
             'market_value_his': 45474.00000000001,
             'profit_rate_today': 1.567229753059285,
             'profit_rate_total': 0.8096964639352789,
             'profit_today': 47530.28571428571,
             'profit_total': 24556.134285714288,
             'real_profit_his': 0.0,
             'real_profit_today': 4805.714285714284,
             'real_profit_total': 4805.714285714284,
             'sell_balance_his': 0.0,
             'sell_balance_today': 15140.0,
             'sell_fee_his': 0.0,
             'sell_fee_today': 20.14,
             'sell_float_profit_today': 24028.571428571428,
             'sell_volume_frozen': 0,
             'sell_volume_his': 0,
             'sell_volume_today': 200,
             'shared_volume_today': 240.0,
             'user_id': 'TQSIM',
             'volume': 640.0,
             'volume_his': 600},
            positions["SSE.603666"]
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_2', 'exchange_id': 'SSE', 'instrument_id': '603666', 'direction': 'SELL', 'price_type': 'LIMIT', 'limit_price': 75.7, 'exchange_order_id': 'PYSDK_insert_2', 'volume_orign': 200, 'volume_left': 0, 'frozen_balance': 0.0, 'frozen_fee': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED', 'insert_date_time': 1626399583510000000},
            orders['PYSDK_insert_2']
        )
        self.assertEqual(
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_2', 'trade_id': 'PYSDK_insert_2|200', 'exchange_trade_id': 'PYSDK_insert_2|200', 'exchange_id': 'SSE', 'instrument_id': '603666', 'direction': 'SELL', 'price': 75.7, 'volume': 200, 'trade_date_time': 1626399583510000000, 'fee': 20.14},
            trades['PYSDK_insert_2|200']
        )

