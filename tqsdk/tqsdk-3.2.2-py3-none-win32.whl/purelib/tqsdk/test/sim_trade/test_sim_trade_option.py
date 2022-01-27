#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'mayanqiong'

import unittest

import numpy as np

from tqsdk.diff import _simple_merge_diff
from tqsdk.tradeable.sim.trade_future import SimTrade


class TestSimTradeOption(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期权交易
    1.买开-> 2.行情更新 -> 3.结算 -> 4.行情更新 -> 5.卖平
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        # 更新初始行情
        self.sim_trade.update_quotes("DCE.m2105-C-3100", {
            'quotes': {
                'DCE.m2105-C-3100': {
                    'ins_class': 'OPTION', 'instrument_id': 'DCE.m2105-C-3100',
                    'datetime': '2020-12-10 21:00:59.999999',
                    'option_class': 'CALL', 'underlying_symbol': 'DCE.m2105', 'strike_price': 3100.0,
                    'ask_price1': 128.5, 'bid_price1': 127.5, 'last_price': 128.0,
                    'price_tick': 0.5, 'volume_multiple': 10.0,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "23:00:00"]]
                    },

                },
                'DCE.m2105': {
                    'ins_class': 'FUTURE', 'instrument_id': 'DCE.m2105', 'datetime': '2020-12-10 21:00:59.999999',
                    'ask_price1': 3145.0, 'bid_price1': 3143.0, 'last_price': 3144.0,
                    'price_tick': 1.0, 'volume_multiple': 10.0, 'margin': 1598.0, 'commission': 1.5,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "23:00:00"]]
                    }
                }
            }
        })

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_option(self):
        self.trade_option_1()
        self.trade_option_2()
        self.trade_option_3()
        self.trade_option_4()
        self.trade_option_5()

    def trade_option_1(self):
        """买开"""
        diffs, orders_events = self.sim_trade.insert_order("DCE.m2105-C-3100", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
            'exchange_id': 'DCE',
            'instrument_id': 'm2105-C-3100',
            'direction': 'BUY',
            'offset': 'OPEN',
            'volume': 1,
            'price_type': 'LIMIT',
            'limit_price': 128.5,
            'time_condition': 'GFD',
            'volume_condition': 'ANY'
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 2)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        np.testing.assert_equal(
            self.account_snapshot['trade']['abc']['accounts']['CNY'],
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999985.0,
             'available': 998705.0, 'float_profit': -5.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 10.0, 'frozen_premium': 0.0,
             'premium': -1285.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0, 'market_value': 1280.0,
             'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        print(self.account_snapshot['trade']['abc']['positions']['DCE.m2105-C-3100'])
        np.testing.assert_equal(
            self.account_snapshot['trade']['abc']['positions']['DCE.m2105-C-3100'],
            {'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100', 'pos_long_his': 0, 'pos_long_today': 1,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 1, 'volume_long_his': 0, 'volume_long': 1,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 128.5, 'open_price_short': float('nan'),
             'open_cost_long': 1285.0, 'open_cost_short': 0.0, 'position_price_long': 128.5,
             'position_price_short': float('nan'), 'position_cost_long': 1285.0, 'position_cost_short': 0.0,
             'float_profit_long': -5.0, 'float_profit_short': 0.0, 'float_profit': -5.0, 'position_profit_long': 0.0,
             'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0, 'margin_short': 0.0,
             'margin': 0.0, 'last_price': 128.0, 'underlying_last_price': 3144.0, 'market_value_long': 1280.0,
             'market_value_short': 0.0, 'market_value': 1280.0, 'future_margin': float('nan')}
        )
        self.assertEqual(
            self.account_snapshot['trade']['abc']['orders'],
            {
                'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d': {
                    'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                    'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100',
                    'direction': 'BUY', 'offset': 'OPEN',
                    'price_type': 'LIMIT', 'limit_price': 128.5,
                    'time_condition': 'GFD', 'volume_condition': 'ANY',
                    'exchange_order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                    'volume_orign': 1, 'volume_left': 0,
                    'frozen_margin': 0.0, 'frozen_premium': 0.0,
                    'last_msg': '全部成交', 'status': 'FINISHED',
                    'insert_date_time': 1607605259999999000
                }
            }
        )
        self.assertEqual(
            self.account_snapshot['trade']['abc']['trades'],
            {'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|1': {
                'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                'trade_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|1',
                'exchange_trade_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|1',
                'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100',
                'direction': 'BUY', 'offset': 'OPEN', 'price': 128.5,
                'volume': 1, 'trade_date_time': 1607605259999999000,
                'commission': 10}}
        )

        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d', 'exchange_id': 'DCE',
             'instrument_id': 'm2105-C-3100', 'direction': 'BUY', 'offset': 'OPEN', 'price_type': 'LIMIT',
             'limit_price': 128.5, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d', 'volume_orign': 1, 'volume_left': 1,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1607605259999999000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d', 'exchange_id': 'DCE',
             'instrument_id': 'm2105-C-3100', 'direction': 'BUY', 'offset': 'OPEN', 'price_type': 'LIMIT',
             'limit_price': 128.5, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d', 'volume_orign': 1, 'volume_left': 0,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1607605259999999000}
        )

    def trade_option_2(self):
        """期权价格升高"""
        diffs, orders_events = self.sim_trade.update_quotes("DCE.m2105-C-3100", {
            'quotes': {
                'DCE.m2105-C-3100': {
                    'datetime': '2020-12-10 21:02:00.000000', 'ask_price1': 133.5, 'bid_price1': 132.5,
                    'last_price': 133.0
                }
            }
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        position = self.account_snapshot['trade']['abc']['positions']['DCE.m2105-C-3100']
        np.testing.assert_equal(
            position,
            {'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100', 'pos_long_his': 0, 'pos_long_today': 1,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 1, 'volume_long_his': 0, 'volume_long': 1,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 128.5, 'open_cost_long': 1285.0,
             'open_cost_short': 0.0, 'position_price_long': 128.5, 'position_cost_long': 1285.0,
             'position_cost_short': 0.0, 'float_profit_long': 45.0, 'float_profit_short': 0.0, 'float_profit': 45.0,
             'position_profit_long': 0.0, 'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0,
             'margin_short': 0.0, 'margin': 0.0, 'last_price': 133.0, 'underlying_last_price': 3144.0,
             'market_value_long': 1330.0, 'market_value_short': 0.0, 'market_value': 1330.0, 'open_price_short': float('nan'),
             'position_price_short': float('nan'), 'future_margin': float('nan')}
        )
        np.testing.assert_equal(
            self.account_snapshot['trade']['abc']['accounts']['CNY'],
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 1000035.0,
             'available': 998705.0, 'float_profit': 45.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 10.0, 'frozen_premium': 0.0,
             'premium': -1285.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0, 'market_value': 1330.0,
             'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )

    def trade_option_3(self):
        """结算"""
        diffs, orders_events, trade_log = self.sim_trade.settle()
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        position = self.account_snapshot['trade']['abc']['positions']['DCE.m2105-C-3100']
        np.testing.assert_equal(
            position,
            {'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100', 'pos_long_his': 1, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 1, 'volume_long': 1,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 128.5, 'open_cost_long': 1285.0,
             'open_cost_short': 0.0, 'position_price_long': 133.0, 'position_cost_long': 1330.0,
             'position_cost_short': 0.0, 'float_profit_long': 45.0, 'float_profit_short': 0.0, 'float_profit': 45.0,
             'position_profit_long': 0.0, 'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0,
             'margin_short': 0.0, 'margin': 0.0, 'last_price': 133.0, 'underlying_last_price': 3144.0,
             'market_value_long': 1330.0, 'market_value_short': 0.0, 'market_value': 1330.0, 'open_price_short': float('nan'),
             'position_price_short': 133.0, 'future_margin': float('nan')}
        )
        np.testing.assert_equal(
            self.account_snapshot['trade']['abc']['accounts']['CNY'],
            {'currency': 'CNY', 'pre_balance': 998705.0, 'static_balance': 998705.0, 'balance': 1000035.0,
             'available': 998705.0, 'float_profit': 45.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 0.0, 'frozen_premium': 0.0,
             'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0, 'market_value': 1330.0,
             'ctp_balance': float('nan'), 'ctp_available': float('nan')
             }
        )

    def trade_option_4(self):
        """更新行情"""
        diffs, orders_events = self.sim_trade.update_quotes("DCE.m2105-C-3100", {
            'quotes': {
                'DCE.m2105-C-3100': {
                    'datetime': '2020-12-14 09:00:00.000000',
                    'ask_price1': 110.5, 'bid_price1': 109.5, 'last_price': 110.0
                }
            }
        })
        self.assertEqual(len(diffs), 2)
        self.assertEqual(len(orders_events), 0)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        position = self.account_snapshot['trade']['abc']['positions']['DCE.m2105-C-3100']
        np.testing.assert_equal(
            position,
            {'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100', 'pos_long_his': 1, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 1, 'volume_long': 1,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 128.5, 'open_cost_long': 1285.0,
             'open_cost_short': 0.0, 'position_price_long': 133.0, 'position_cost_long': 1330.0,
             'position_cost_short': 0.0, 'float_profit_long': -185.0, 'float_profit_short': 0.0, 'float_profit': -185.0,
             'position_profit_long': 0.0, 'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0,
             'margin_short': 0.0, 'margin': 0.0, 'last_price': 110.0, 'underlying_last_price': 3144.0,
             'market_value_long': 1100.0, 'market_value_short': 0.0, 'market_value': 1100.0,
             'open_price_short': float('nan'), 'position_price_short': float('nan'), 'future_margin': float('nan')
             }
        )
        np.testing.assert_equal(
            self.account_snapshot['trade']['abc']['accounts']['CNY'],
            {'currency': 'CNY', 'pre_balance': 998705.0, 'static_balance': 998705.0, 'balance': 999805.0,
             'available': 998705.0, 'float_profit': -185.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 0.0, 'frozen_premium': 0.0,
             'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0, 'market_value': 1100.0,
             'ctp_balance': float('nan'), 'ctp_available': float('nan')
             }
        )

    def trade_option_5(self):
        """平仓"""
        diffs, orders_events = self.sim_trade.insert_order('DCE.m2105-C-3100', {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216',
            'exchange_id': 'DCE',
            'instrument_id': 'm2105-C-3100',
            'direction': 'SELL',
            'offset': 'CLOSE',
            'volume': 1,
            'price_type': 'LIMIT',
            'limit_price': 109.5,
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

        self.assertEqual(
            orders,  # 之前的 orders 没有删除
            {'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d': {'user_id': 'TQSIM',
                                                               'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                                                               'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100',
                                                               'direction': 'BUY', 'offset': 'OPEN',
                                                               'price_type': 'LIMIT', 'limit_price': 128.5,
                                                               'time_condition': 'GFD', 'volume_condition': 'ANY',
                                                               'exchange_order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                                                               'volume_orign': 1, 'volume_left': 0,
                                                               'frozen_margin': 0.0, 'frozen_premium': 0.0,
                                                               'last_msg': '全部成交', 'status': 'FINISHED',
                                                               'insert_date_time': 1607605259999999000},
             'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216': {'user_id': 'TQSIM',
                                                               'order_id': 'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216',
                                                               'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100',
                                                               'direction': 'SELL', 'offset': 'CLOSE',
                                                               'price_type': 'LIMIT', 'limit_price': 109.5,
                                                               'time_condition': 'GFD', 'volume_condition': 'ANY',
                                                               'exchange_order_id': 'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216',
                                                               'volume_orign': 1, 'volume_left': 0,
                                                               'frozen_margin': 0.0, 'frozen_premium': 0.0,
                                                               'last_msg': '全部成交', 'status': 'FINISHED',
                                                               'insert_date_time': 1607907600000000000}}
        )
        self.assertEqual(
            trades,
            {'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|1': {'user_id': 'TQSIM',
                                                                 'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                                                                 'trade_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|1',
                                                                 'exchange_trade_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|1',
                                                                 'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100',
                                                                 'direction': 'BUY', 'offset': 'OPEN', 'price': 128.5,
                                                                 'volume': 1, 'trade_date_time': 1607605259999999000,
                                                                 'commission': 10},
             'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216|1': {'user_id': 'TQSIM',
                                                                 'order_id': 'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216',
                                                                 'trade_id': 'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216|1',
                                                                 'exchange_trade_id': 'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216|1',
                                                                 'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100',
                                                                 'direction': 'SELL', 'offset': 'CLOSE', 'price': 109.5,
                                                                 'volume': 1, 'trade_date_time': 1607907600000000000,
                                                                 'commission': 10}}
        )
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 998705.0, 'static_balance': 998705.0, 'balance': 999790.0,
             'available': 999790.0, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 10.0, 'frozen_premium': 0.0,
             'premium': 1095.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0, 'market_value': 0.0,
             'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['DCE.m2105-C-3100'],
            {'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': float('nan'), 'open_cost_long': 0.0,
             'open_cost_short': 0.0, 'position_price_long': float('nan'), 'position_cost_long': 0.0, 'position_cost_short': 0.0,
             'float_profit_long': 0.0, 'float_profit_short': 0.0, 'float_profit': 0.0, 'position_profit_long': 0.0,
             'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0, 'margin_short': 0.0,
             'margin': 0.0, 'last_price': 110.0, 'underlying_last_price': 3144.0, 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': float('nan'),
             'open_price_short': float('nan'), 'position_price_short': float('nan')}
        )

        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216', 'exchange_id': 'DCE',
             'instrument_id': 'm2105-C-3100', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 109.5, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216', 'volume_orign': 1, 'volume_left': 1,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1607907600000000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216', 'exchange_id': 'DCE',
             'instrument_id': 'm2105-C-3100', 'direction': 'SELL', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 109.5, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_a001d29a067663a34ec4cb82adfb4216', 'volume_orign': 1, 'volume_left': 0,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1607907600000000000}
        )


class TestSimTradeOption2(unittest.TestCase):
    """
    测试天勤模拟交易类 - 期权交易
    1.卖开挂单 -> 2.行情更新，成交 -> 3.价格更新,资金变化 -> 4.买平
    """

    def setUp(self):
        self.sim_trade = SimTrade(account_key='abc', init_balance=1000000.0)
        self.account_snapshot = self.sim_trade.init_snapshot()
        # 更新初始行情
        self.sim_trade.update_quotes("DCE.m2105-C-3100", {
            'quotes': {
                'DCE.m2105-C-3100': {
                    'ins_class': 'OPTION', 'instrument_id': 'DCE.m2105-C-3100',
                    'datetime': '2020-12-10 21:00:59.999999',
                    'option_class': 'CALL', 'underlying_symbol': 'DCE.m2105', 'strike_price': 3100.0,
                    'ask_price1': 128.5, 'bid_price1': 127.5, 'last_price': 128.0,
                    'price_tick': 0.5, 'volume_multiple': 10.0,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "23:00:00"]]
                    },

                },
                'DCE.m2105': {
                    'ins_class': 'FUTURE', 'instrument_id': 'DCE.m2105', 'datetime': '2020-12-10 21:00:59.999999',
                    'ask_price1': 3145.0, 'bid_price1': 3143.0, 'last_price': 3144.0,
                    'price_tick': 1.0, 'volume_multiple': 10.0, 'margin': 1598.0, 'commission': 1.5,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "23:00:00"]]
                    }
                }
            }
        })

    def tearDown(self):
        self.sim_trade = None
        self.account_snapshot = None

    def test_trade_option(self):
        self.trade_option_1()
        self.trade_option_2()
        self.trade_option_3()
        self.trade_option_4()

    def trade_option_1(self):
        """卖开挂单"""
        diffs, orders_events = self.sim_trade.insert_order("DCE.m2105-C-3100", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
            'exchange_id': 'DCE',
            'instrument_id': 'm2105-C-3100',
            'direction': 'SELL',
            'offset': 'OPEN',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 128.5,
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
        self.assertEqual(
            orders,
            {'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d': {'user_id': 'TQSIM',
                                                               'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                                                               'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100',
                                                               'direction': 'SELL', 'offset': 'OPEN',
                                                               'price_type': 'LIMIT', 'limit_price': 128.5,
                                                               'time_condition': 'GFD', 'volume_condition': 'ANY',
                                                               'exchange_order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                                                               'volume_orign': 2, 'volume_left': 2,
                                                               'frozen_margin': 0.0, 'frozen_premium': 0.0,
                                                               'last_msg': '报单成功', 'status': 'ALIVE',
                                                               'insert_date_time': 1607605259999999000}}
        )
        self.assertEqual(trades, {})
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 1000000.0,
             'available': 989894.4, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 10105.599999999999, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 0.0,
             'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0,
             'market_value': 0.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        self.assertEqual(positions, {})
        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d', 'exchange_id': 'DCE',
             'instrument_id': 'm2105-C-3100', 'direction': 'SELL', 'offset': 'OPEN', 'price_type': 'LIMIT',
             'limit_price': 128.5, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1607605259999999000}
        )

    def trade_option_2(self):
        """行情更新，成交"""
        diffs, orders_events = self.sim_trade.update_quotes("DCE.m2105-C-3100", {
            'quotes': {
                'DCE.m2105-C-3100': {
                    'datetime': '2020-12-10 21:01:59.999999',
                    'ask_price1': 129.5, 'bid_price1': 128.5, 'last_price': 129.0
                }
            }
        })
        self.assertEqual(len(diffs), 6)
        self.assertEqual(len(orders_events), 1)
        for diff in diffs:
            _simple_merge_diff(self.account_snapshot, diff)

        orders = self.account_snapshot['trade']['abc']['orders']
        trades = self.account_snapshot['trade']['abc']['trades']
        account = self.account_snapshot['trade']['abc']['accounts']['CNY']
        positions = self.account_snapshot['trade']['abc']['positions']
        self.assertEqual(
            orders,
            {'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d': {'user_id': 'TQSIM',
                                                               'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                                                               'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100',
                                                               'direction': 'SELL', 'offset': 'OPEN',
                                                               'price_type': 'LIMIT', 'limit_price': 128.5,
                                                               'time_condition': 'GFD', 'volume_condition': 'ANY',
                                                               'exchange_order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                                                               'volume_orign': 2, 'volume_left': 0,
                                                               'frozen_margin': 0.0, 'frozen_premium': 0.0,
                                                               'last_msg': '全部成交', 'status': 'FINISHED',
                                                               'insert_date_time': 1607605259999999000}}
        )
        self.assertEqual(
            trades,
            {'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|2': {'user_id': 'TQSIM',
                                                                 'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                                                                 'trade_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|2',
                                                                 'exchange_trade_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|2',
                                                                 'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100',
                                                                 'direction': 'SELL', 'offset': 'OPEN', 'price': 128.5,
                                                                 'volume': 2, 'trade_date_time': 1607605319999999000,
                                                                 'commission': 20}}
        )
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999970.0,
             'available': 992424.4, 'float_profit': -10.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 10125.599999999999, 'frozen_commission': 0.0, 'commission': 20.0,
             'frozen_premium': 0.0, 'premium': 2570.0, 'deposit': 0.0, 'withdraw': 0.0,
             'risk_ratio': 0.010125903777113312, 'market_value': -2580.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['DCE.m2105-C-3100'],
            {'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 2, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 2, 'volume_short_his': 0, 'volume_short': 2, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': float('nan'), 'open_price_short': 128.5,
             'open_cost_long': 0.0, 'open_cost_short': 2570.0, 'position_price_long': float('nan'),
             'position_price_short': 128.5, 'position_cost_long': 0.0, 'position_cost_short': 2570.0,
             'float_profit_long': 0.0, 'float_profit_short': -10.0, 'float_profit': -10.0, 'position_profit_long': 0.0,
             'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0,
             'margin_short': 10125.599999999999, 'margin': 10125.599999999999, 'last_price': 129.0,
             'underlying_last_price': 3144.0, 'market_value_long': 0.0, 'market_value_short': -2580.0,
             'market_value': -2580.0, 'future_margin': float('nan')}
        )

    def trade_option_3(self):
        """期权价格升高，资金变化"""
        diffs, orders_events = self.sim_trade.update_quotes("DCE.m2105-C-3100", {
            'quotes': {
                'DCE.m2105-C-3100': {
                    'datetime': '2020-12-10 21:02:00.000000', 'ask_price1': 133.5, 'bid_price1': 132.5, 'last_price': 133.0
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
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999890.0,
             'available': 992344.4, 'float_profit': -90.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 10205.599999999999, 'frozen_commission': 0.0, 'commission': 20.0,
             'frozen_premium': 0.0, 'premium': 2570.0, 'deposit': 0.0, 'withdraw': 0.0,
             'risk_ratio': 0.010206722739501344, 'market_value': -2660.0, 'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['DCE.m2105-C-3100'],
            {'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 2, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 2, 'volume_short_his': 0, 'volume_short': 2, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_short': 128.5, 'open_cost_long': 0.0,
             'open_cost_short': 2570.0, 'position_price_short': 128.5, 'position_cost_long': 0.0,
             'position_cost_short': 2570.0, 'float_profit_long': 0.0, 'float_profit_short': -90.0,
             'float_profit': -90.0, 'position_profit_long': 0.0, 'position_profit_short': 0.0, 'position_profit': 0.0,
             'margin_long': 0.0, 'margin_short': 10205.599999999999, 'margin': 10205.599999999999, 'last_price': 133.0,
             'underlying_last_price': 3144.0, 'market_value_long': 0.0, 'market_value_short': -2660.0,
             'market_value': -2660.0, 'future_margin': float('nan'), 'open_price_long': float('nan'),
             'position_price_long': float('nan')}
        )

    def trade_option_4(self):
        """买平"""
        diffs, orders_events = self.sim_trade.insert_order("DCE.m2105-C-3100", {
            'aid': 'insert_order',
            'user_id': 'TQSIM',
            'order_id': 'PYSDK_insert_buy_close',
            'exchange_id': 'DCE',
            'instrument_id': 'm2105-C-3100',
            'direction': 'BUY',
            'offset': 'CLOSE',
            'volume': 2,
            'price_type': 'LIMIT',
            'limit_price': 133.5,
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
        self.assertEqual(
            orders,
            {'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d': {'user_id': 'TQSIM',
                                                               'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                                                               'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100',
                                                               'direction': 'SELL', 'offset': 'OPEN',
                                                               'price_type': 'LIMIT', 'limit_price': 128.5,
                                                               'time_condition': 'GFD', 'volume_condition': 'ANY',
                                                               'exchange_order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                                                               'volume_orign': 2, 'volume_left': 0,
                                                               'frozen_margin': 0.0, 'frozen_premium': 0.0,
                                                               'last_msg': '全部成交', 'status': 'FINISHED',
                                                               'insert_date_time': 1607605259999999000},
             'PYSDK_insert_buy_close': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close', 'exchange_id': 'DCE',
                                        'instrument_id': 'm2105-C-3100', 'direction': 'BUY', 'offset': 'CLOSE',
                                        'price_type': 'LIMIT', 'limit_price': 133.5, 'time_condition': 'GFD',
                                        'volume_condition': 'ANY', 'exchange_order_id': 'PYSDK_insert_buy_close',
                                        'volume_orign': 2, 'volume_left': 0, 'frozen_margin': 0.0,
                                        'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
                                        'insert_date_time': 1607605320000000000}}
        )
        self.assertEqual(
            trades,
            {'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|2': {'user_id': 'TQSIM',
                                                                 'order_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d',
                                                                 'trade_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|2',
                                                                 'exchange_trade_id': 'PYSDK_insert_7da557c0cbd696b042dad5c5c0e5b27d|2',
                                                                 'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100',
                                                                 'direction': 'SELL', 'offset': 'OPEN', 'price': 128.5,
                                                                 'volume': 2, 'trade_date_time': 1607605319999999000,
                                                                 'commission': 20},
             'PYSDK_insert_buy_close|2': {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close',
                                          'trade_id': 'PYSDK_insert_buy_close|2',
                                          'exchange_trade_id': 'PYSDK_insert_buy_close|2', 'exchange_id': 'DCE',
                                          'instrument_id': 'm2105-C-3100', 'direction': 'BUY', 'offset': 'CLOSE',
                                          'price': 133.5, 'volume': 2, 'trade_date_time': 1607605320000000000,
                                          'commission': 20}}

        )
        np.testing.assert_equal(
            account,
            {'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999860.0,
             'available': 999860.0, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0,
             'frozen_margin': 0.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 40.0, 'frozen_premium': 0.0,
             'premium': -100.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0, 'market_value': 0.0,
             'ctp_balance': float('nan'), 'ctp_available': float('nan')}
        )
        np.testing.assert_equal(
            positions['DCE.m2105-C-3100'],
            {'exchange_id': 'DCE', 'instrument_id': 'm2105-C-3100', 'pos_long_his': 0, 'pos_long_today': 0,
             'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 0, 'volume_long_his': 0, 'volume_long': 0,
             'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0,
             'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0,
             'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_short': float('nan'), 'open_cost_long': 0.0,
             'open_cost_short': 0.0, 'position_price_short': float('nan'), 'position_cost_long': 0.0, 'position_cost_short': 0.0,
             'float_profit_long': 0.0, 'float_profit_short': 0.0, 'float_profit': 0.0, 'position_profit_long': 0.0,
             'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0, 'margin_short': 0.0,
             'margin': 0.0, 'last_price': 133.0, 'underlying_last_price': 3144.0, 'market_value_long': 0.0,
             'market_value_short': 0.0, 'market_value': 0.0, 'future_margin': float('nan'),
             'open_price_long': float('nan'), 'position_price_long': float('nan')}
        )

        self.assertEqual(
            orders_events[0],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close', 'exchange_id': 'DCE',
             'instrument_id': 'm2105-C-3100', 'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 133.5, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_buy_close', 'volume_orign': 2, 'volume_left': 2,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '报单成功', 'status': 'ALIVE',
             'insert_date_time': 1607605320000000000}
        )
        self.assertEqual(
            orders_events[1],
            {'user_id': 'TQSIM', 'order_id': 'PYSDK_insert_buy_close', 'exchange_id': 'DCE',
             'instrument_id': 'm2105-C-3100', 'direction': 'BUY', 'offset': 'CLOSE', 'price_type': 'LIMIT',
             'limit_price': 133.5, 'time_condition': 'GFD', 'volume_condition': 'ANY',
             'exchange_order_id': 'PYSDK_insert_buy_close', 'volume_orign': 2, 'volume_left': 0,
             'frozen_margin': 0.0, 'frozen_premium': 0.0, 'last_msg': '全部成交', 'status': 'FINISHED',
             'insert_date_time': 1607605320000000000}
        )

