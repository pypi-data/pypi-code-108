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

    def test_insert_order_shfe_anyprice(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://q7.htfutures.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_shfe_anyprice.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha131313")
        utils.RD = random.Random(4)
        # 测试
        api = TqApi(account=account, auth="tianqin,tianqin", _md_url=md_url, _td_url=td_url)
        self.assertRaises(Exception, api.insert_order, "SHFE.au2112", "BUY", "OPEN", 1)
        api.close()

    def test_insert_order_shfe_limit_fok(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://q7.htfutures.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_shfe_limit_fok.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha131313")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=md_url, _td_url=td_url) as api:
            order1 = api.insert_order("SHFE.au2112", "BUY", "OPEN", 2, limit_price=380, advanced="FOK", order_id="PYSDK_insert_SHFE_limit_FOK")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            self.assertEqual("PYSDK_insert_SHFE_limit_FOK", order1.order_id)
            self.assertEqual("", order1.exchange_order_id)
            self.assertEqual("SHFE", order1.exchange_id)
            self.assertEqual("au2112", order1.instrument_id)
            self.assertEqual("BUY", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(2, order1.volume_orign)
            self.assertEqual(2, order1.volume_left)
            self.assertEqual(380.0, order1.limit_price)
            self.assertEqual(1632890201063519797, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ALL", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("CTP:资金不足", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_SHFE_limit_FOK', 'exchange_order_id': '', 'exchange_id': 'SHFE', 'instrument_id': 'au2112', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 2, 'limit_price': 380.0, 'price_type': 'LIMIT', 'volume_condition': 'ALL', 'time_condition': 'IOC', 'insert_date_time': 1632890201063519797, 'last_msg': 'CTP:资金不足', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': True, 'trade_price': nan, 'seqno': 0, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_shfe_limit_fak(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://q7.htfutures.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_shfe_limit_fak.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha131313")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=md_url, _td_url=td_url) as api:
            order1 = api.insert_order("SHFE.au2112", "BUY", "OPEN", 2, limit_price=380, advanced="FAK", order_id="PYSDK_insert_SHFE_limit_FAK2")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            print(str(order1))
            self.assertEqual("PYSDK_insert_SHFE_limit_FAK2", order1.order_id)
            self.assertEqual("", order1.exchange_order_id)
            self.assertEqual("SHFE", order1.exchange_id)
            self.assertEqual("au2112", order1.instrument_id)
            self.assertEqual("BUY", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(2, order1.volume_orign)
            self.assertEqual(2, order1.volume_left)
            self.assertEqual(380.0, order1.limit_price)
            self.assertEqual(1632890216577815369, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ANY", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("CTP:资金不足", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_SHFE_limit_FAK2', 'exchange_order_id': '', 'exchange_id': 'SHFE', 'instrument_id': 'au2112', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 2, 'limit_price': 380.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'insert_date_time': 1632890216577815369, 'last_msg': 'CTP:资金不足', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': True, 'trade_price': nan, 'seqno': 0, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_dec_best(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://q7.htfutures.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_dec_best.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha131313")
        utils.RD = random.Random(4)
        # 测试
        api = TqApi(account=account, auth="tianqin,tianqin", _md_url=md_url, _td_url=td_url)
        self.assertRaises(Exception, api.insert_order, "DCE.m2201", "BUY", "OPEN", 1, limit_price="BEST", order_id="PYSDK_insert_DCE_BEST")
        api.close()

    def test_insert_order_dec_fivelevel(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://q7.htfutures.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_dec_fivelevel.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha131313")
        utils.RD = random.Random(4)
        # 测试
        api = TqApi(account=account, auth="tianqin,tianqin", _md_url=md_url, _td_url=td_url)
        self.assertRaises(Exception, api.insert_order, "DCE.m2201", "BUY", "OPEN", 1, limit_price="FIVELEVEL",
                                          order_id="PYSDK_insert_DCE_FIVELEVEL")
        api.close()

    def test_insert_order_dce_anyprice(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://q7.htfutures.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_dce_anyprice.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha131313")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=md_url, _td_url=td_url) as api:
            order1 = api.insert_order("DCE.m2201", "BUY", "OPEN", 1, order_id="PYSDK_insert_DCE_any")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            print(str(order1))
            self.assertEqual("PYSDK_insert_DCE_any", order1.order_id)
            self.assertEqual("", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2201", order1.instrument_id)
            self.assertEqual("BUY", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(1, order1.volume_orign)
            self.assertEqual(1, order1.volume_left)
            self.assertEqual(0.0, order1.limit_price)
            self.assertEqual(1632890507000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("ANY", order1.price_type)
            self.assertEqual("ANY", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("40045:已撤单报单被拒绝DCE:该合约当前是连续交易暂停", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_any', 'exchange_order_id': '', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 1, 'volume_left': 1, 'limit_price': 0.0, 'price_type': 'ANY', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'insert_date_time': 1632890507000000000, 'last_msg': '40045:已撤单报单被拒绝DCE:该合约当前是连续交易暂停', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': True, 'trade_price': nan, 'seqno': 4, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_dce_anyprice_fok(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://q7.htfutures.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_dce_anyprice_fok.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha131313")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=md_url, _td_url=td_url) as api:
            order1 = api.insert_order("DCE.m2201", "BUY", "OPEN", 2, advanced="FOK", order_id="PYSDK_insert_DCE_any_FOK")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            print(str(order1))
            self.assertEqual("PYSDK_insert_DCE_any_FOK", order1.order_id)
            self.assertEqual("", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2201", order1.instrument_id)
            self.assertEqual("BUY", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(2, order1.volume_orign)
            self.assertEqual(2, order1.volume_left)
            self.assertEqual(0.0, order1.limit_price)
            self.assertEqual(1632893536208012593, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("ANY", order1.price_type)
            self.assertEqual("ALL", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("CTP:资金不足", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_any_FOK', 'exchange_order_id': '', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 2, 'limit_price': 0.0, 'price_type': 'ANY', 'volume_condition': 'ALL', 'time_condition': 'IOC', 'insert_date_time': 1632893536208012593, 'last_msg': 'CTP:资金不足', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': True, 'trade_price': nan, 'seqno': 0, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_dce_limit_fak(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://q7.htfutures.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_dce_limit_fak.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha131313")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=md_url, _td_url=td_url) as api:
            order1 = api.insert_order("DCE.m2201", "SELL", "OPEN", 1, limit_price=3467, advanced="FAK", order_id="PYSDK_insert_DCE_limit_FAK")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            print(str(order1))
            self.assertEqual("PYSDK_insert_DCE_limit_FAK", order1.order_id)
            self.assertEqual("   149052977", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2201", order1.instrument_id)
            self.assertEqual("SELL", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(1, order1.volume_orign)
            self.assertEqual(1, order1.volume_left)
            self.assertEqual(3467.0, order1.limit_price)
            self.assertEqual(1632893427000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ANY", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("已撤单", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_limit_FAK', 'exchange_order_id': '   149052977', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'SELL', 'offset': 'OPEN', 'volume_orign': 1, 'volume_left': 1, 'limit_price': 3467.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'insert_date_time': 1632893427000000000, 'last_msg': '已撤单', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': nan, 'seqno': 8, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_dce_limit_fok(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://q7.htfutures.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_dce_limit_fok.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha131313")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=md_url, _td_url=td_url) as api:
            order1 = api.insert_order("DCE.m2201", "SELL", "OPEN", 2, limit_price=3474, advanced="FOK", order_id="PYSDK_insert_DCE_limit_FOK")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            print(order1)
            self.assertEqual("PYSDK_insert_DCE_limit_FOK", order1.order_id)
            self.assertEqual("", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2201", order1.instrument_id)
            self.assertEqual("SELL", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(2, order1.volume_orign)
            self.assertEqual(2, order1.volume_left)
            self.assertEqual(3474.0, order1.limit_price)
            self.assertEqual(1632893715789590774, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ALL", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("CTP:资金不足", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_limit_FOK', 'exchange_order_id': '', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'SELL', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 2, 'limit_price': 3474.0, 'price_type': 'LIMIT', 'volume_condition': 'ALL', 'time_condition': 'IOC', 'insert_date_time': 1632893715789590774, 'last_msg': 'CTP:资金不足', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': True, 'trade_price': nan, 'seqno': 0, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_dce_limit_fak1(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://q7.htfutures.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_dce_limit_fak1.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha131313")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=md_url, _td_url=td_url) as api:
            order1 = api.insert_order("DCE.m2201", "SELL", "OPEN", 1, limit_price=3474, advanced="FAK", order_id="PYSDK_insert_DCE_limit_FAK2")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            print(str(order1))
            self.assertEqual("PYSDK_insert_DCE_limit_FAK2", order1.order_id)
            self.assertEqual("   149819447", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2201", order1.instrument_id)
            self.assertEqual("SELL", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(1, order1.volume_orign)
            self.assertEqual(1, order1.volume_left)
            self.assertEqual(3474.0, order1.limit_price)
            self.assertEqual(1632893730000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ANY", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("已撤单", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_limit_FAK2', 'exchange_order_id': '   149819447', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'SELL', 'offset': 'OPEN', 'volume_orign': 1, 'volume_left': 1, 'limit_price': 3474.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'insert_date_time': 1632893730000000000, 'last_msg': '已撤单', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': nan, 'seqno': 14, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))

    def test_insert_order_dce_limit_fok1(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        td_url = "wss://q7.htfutures.com/trade"
        set_test_script(os.path.join(dir_path, "log_file", "test_insert_order_dce_limit_fok1.script.lzma"))
        # 测试
        account = TqAccount("H海通期货", "83011119", "sha131313")
        utils.RD = random.Random(4)
        with TqApi(account=account, auth="tianqin,tianqin", _md_url=md_url, _td_url=td_url) as api:
            order1 = api.insert_order("DCE.m2201", "SELL", "OPEN", 1, limit_price=3484, advanced="FOK", order_id="PYSDK_insert_DCE_limit_FOK1")
            while True:
                api.wait_update()
                if order1.status == "FINISHED":
                    break
            print(str(order1))
            self.assertEqual("PYSDK_insert_DCE_limit_FOK1", order1.order_id)
            self.assertEqual("   150391230", order1.exchange_order_id)
            self.assertEqual("DCE", order1.exchange_id)
            self.assertEqual("m2201", order1.instrument_id)
            self.assertEqual("SELL", order1.direction)
            self.assertEqual("OPEN", order1.offset)
            self.assertEqual(1, order1.volume_orign)
            self.assertEqual(0, order1.volume_left)
            self.assertEqual(3484.0, order1.limit_price)
            self.assertEqual(1632893927000000000, order1.insert_date_time)
            self.assertEqual("FINISHED", order1.status)
            self.assertEqual("LIMIT", order1.price_type)
            self.assertEqual("ALL", order1.volume_condition)
            self.assertEqual("IOC", order1.time_condition)
            self.assertEqual("全部成交", order1.last_msg)
            self.assertEqual(
                "{'order_id': 'PYSDK_insert_DCE_limit_FOK1', 'exchange_order_id': '   150391230', 'exchange_id': 'DCE', 'instrument_id': 'm2201', 'direction': 'SELL', 'offset': 'OPEN', 'volume_orign': 1, 'volume_left': 0, 'limit_price': 3484.0, 'price_type': 'LIMIT', 'volume_condition': 'ALL', 'time_condition': 'IOC', 'insert_date_time': 1632893927000000000, 'last_msg': '全部成交', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 3489.0, 'seqno': 22, 'user_id': '83011119', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
                str(order1))
