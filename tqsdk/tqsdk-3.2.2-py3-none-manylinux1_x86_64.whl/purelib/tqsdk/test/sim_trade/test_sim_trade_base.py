#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'mayanqiong'

import json
import unittest

from tqsdk.diff import _simple_merge_diff
from tqsdk.tradeable.sim.trade_future import SimTrade


class TestSimTradeBase(unittest.TestCase):
    """
    测试天勤模拟交易类 - 基本使用规则：

    1. 获取初始截面，可以设置初始资金
    2. 任何合约应该先更新行情，再下单
    """

    def test_trade_0(self):
        """初始账户截面"""
        sim_trade = SimTrade(account_key="abc", init_balance=10000.0)
        account_snapshot = sim_trade.init_snapshot()
        account = account_snapshot['trade']['abc']['accounts']['CNY']
        self.assertEqual(
            json.dumps(account, ensure_ascii=False),
            '{"currency": "CNY", "pre_balance": 10000.0, "static_balance": 10000.0, "balance": 10000.0, "available": 10000.0, "float_profit": 0.0, "position_profit": 0.0, "close_profit": 0.0, "frozen_margin": 0.0, "margin": 0.0, "frozen_commission": 0.0, "commission": 0.0, "frozen_premium": 0.0, "premium": 0.0, "deposit": 0.0, "withdraw": 0.0, "risk_ratio": 0.0, "market_value": 0.0, "ctp_balance": NaN, "ctp_available": NaN}'
        )

    def test_trade_1(self):
        """初始账户, 首先更新行情，"""
        sim_trade = SimTrade(account_key="abc", init_balance=10000.0)
        account_snapshot = sim_trade.init_snapshot()

        # 初次更新行情，一定会收到持仓和账户更新包
        diffs, orders_events = sim_trade.update_quotes("CZCE.MA105", {
            'quotes': {
                'CZCE.MA105': {
                    'ins_class': 'FUTURE', 'instrument_id': 'CZCE.MA105', 'datetime': '2021-03-16 10:05:22.000001',
                    'ask_price1': float('nan'), 'bid_price1': 2469.0, 'last_price': 2470.0,
                    'price_tick': 1.0, 'volume_multiple': 10.0, 'margin': 1718.5, 'commission': 2.0,
                    'trading_time': {
                        "day": [["09:00:00", "10:15:00"], ["10:30:00", "11:30:00"], ["13:30:00", "15:00:00"]],
                        "night": [["21:00:00", "23:00:00"]]
                    }
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
        position = account_snapshot['trade']['abc']['positions']['CZCE.MA105']
        self.assertEqual(
            json.dumps(position, ensure_ascii=False, sort_keys=True),
            '{"exchange_id": "CZCE", "float_profit": 0.0, "float_profit_long": 0.0, "float_profit_short": 0.0, "future_margin": 1718.5, "instrument_id": "MA105", "last_price": 2470.0, "margin": 0.0, "margin_long": 0.0, "margin_short": 0.0, "market_value": 0.0, "market_value_long": 0.0, "market_value_short": 0.0, "open_cost_long": 0.0, "open_cost_short": 0.0, "open_price_long": NaN, "open_price_short": NaN, "pos_long_his": 0, "pos_long_today": 0, "pos_short_his": 0, "pos_short_today": 0, "position_cost_long": 0.0, "position_cost_short": 0.0, "position_price_long": NaN, "position_price_short": NaN, "position_profit": 0.0, "position_profit_long": 0.0, "position_profit_short": 0.0, "underlying_last_price": NaN, "volume_long": 0, "volume_long_frozen": 0, "volume_long_frozen_his": 0, "volume_long_frozen_today": 0, "volume_long_his": 0, "volume_long_today": 0, "volume_short": 0, "volume_short_frozen": 0, "volume_short_frozen_his": 0, "volume_short_frozen_today": 0, "volume_short_his": 0, "volume_short_today": 0}'
        )

    def test_trade_2(self):
        """初始账户, 没有更新行情先下单，报错"""
        sim_trade = SimTrade(account_key="abc", init_balance=10000.0)
        account_snapshot = sim_trade.init_snapshot()

        # 直接下单抛错
        with self.assertRaises(Exception) as e:
            sim_trade.insert_order("CZCE.MA105", {
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
        self.assertEqual('未收到指定合约行情', str(e.exception))
