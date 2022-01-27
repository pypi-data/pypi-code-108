#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import random

from tqsdk import TqApi, utils
from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk.test.test_chan_helper import set_test_script


class TestTdBasic(TQBaseTestcase):
    """
    测试TqApi交易相关函数基本功能, 以及TqApi与交易服务器交互是否符合设计预期

    注：
    1. 在本地运行测试用例前需设置运行环境变量(Environment variables), 保证api中dict及set等类型的数据序列在每次运行时元素顺序一致: PYTHONHASHSEED=32
    2. 若测试用例中调用了会使用uuid的功能函数时（如insert_order()会使用uuid生成order_id）,
        则：在生成script文件时及测试用例中都需设置 utils.RD = random.Random(x), 以保证两次生成的uuid一致, x取值范围为0-2^32
    3. 对盘中的测试用例（即非回测）：因为TqSim模拟交易 Order 的 insert_date_time 和 Trade 的 trade_date_time 不是固定值，所以改为判断范围。
        盘中时：self.assertAlmostEqual(1575292560005832000 / 1e9, order1.insert_date_time / 1e9, places=1)
        回测时：self.assertEqual(1575291600000000000, order1.insert_date_time)
    """

    def setUp(self):
        super(TestTdBasic, self).setUp()

    def tearDown(self):
        super(TestTdBasic, self).tearDown()

    # 模拟交易测试

    # @unittest.skip("无条件跳过")
    def test_insert_order(self):
        """
        下单
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_insert_order_simulate.script.lzma"))
        # 测试: 模拟账户下单
        # 非回测, 则需在盘中生成测试脚本: 测试脚本重新生成后，数据根据实际情况有变化,因此需要修改assert语句的内容
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("DCE.jd2201", "BUY", "OPEN", 1)
        order2 = api.insert_order("SHFE.cu2111", "BUY", "OPEN", 2, limit_price=68900)
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()
        self.assertEqual(order1.order_id, "PYSDK_insert_1710cf5327ac435a7a97c643656412a9")
        self.assertEqual(order1.direction, "BUY")
        self.assertEqual(order1.offset, "OPEN")
        self.assertEqual(order1.volume_orign, 1)
        self.assertEqual(order1.volume_left, 0)
        self.assertNotEqual(order1.limit_price, order1.limit_price)  # 判断nan
        self.assertEqual(order1.price_type, "ANY")
        self.assertEqual(order1.volume_condition, "ANY")
        self.assertEqual(order1.time_condition, "IOC")
        self.assertAlmostEqual(1632883558336758000 / 1e9, order1.insert_date_time / 1e9, places=0)
        self.assertEqual(order1.status, "FINISHED")
        for k, v in order1.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1632883558339413000 / 1e9, v.trade_date_time / 1e9, places=0)
            del v.trade_date_time
            self.assertEqual(
                {'order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|1', 'exchange_trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|1', 'exchange_id': 'DCE', 'instrument_id': 'jd2201', 'direction': 'BUY', 'offset': 'OPEN', 'price': 4357.0, 'volume': 1, 'user_id': 'TQSIM', 'commission': 6.5115},
                v)
        self.assertEqual(order2.order_id, "PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09")
        self.assertEqual(order2.direction, "BUY")
        self.assertEqual(order2.offset, "OPEN")
        self.assertEqual(order2.volume_orign, 2)
        self.assertEqual(order2.volume_left, 0)
        self.assertEqual(order2.limit_price, 68900.0)
        self.assertEqual(order2.price_type, "LIMIT")
        self.assertEqual(order2.volume_condition, "ANY")
        self.assertEqual(order2.time_condition, "GFD")
        self.assertAlmostEqual(1632883559007560000 / 1e9, order2.insert_date_time / 1e9, places=0)
        self.assertEqual(order2.status, "FINISHED")
        for k, v in order2.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1632883559007850000 / 1e9, v.trade_date_time / 1e9, places=0)
            del v.trade_date_time
            self.assertEqual(
                {'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_id': 'SHFE', 'instrument_id': 'cu2111', 'direction': 'BUY', 'offset': 'OPEN', 'price': 68900.0, 'volume': 2, 'user_id': 'TQSIM', 'commission': 34.62},
                v)
            api.close()

    def test_insert_order_fok(self):
        """
        下单
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_insert_order_fok_simulate.script.lzma"))
        # 测试: 模拟账户下单
        # 非回测, 则需在盘中生成测试脚本: 测试脚本重新生成后，数据根据实际情况有变化,因此需要修改assert语句的内容
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("SHFE.au2112", "BUY", "OPEN", 2, limit_price=374, advanced="FOK")
        order2 = api.insert_order("SHFE.cu2112", "BUY", "OPEN", 2, limit_price=68800, advanced="FOK")
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()
        self.assertEqual(order1.order_id, "PYSDK_insert_1710cf5327ac435a7a97c643656412a9")
        self.assertEqual(order1.direction, "BUY")
        self.assertEqual(order1.offset, "OPEN")
        self.assertEqual(order1.volume_orign, 2)
        self.assertEqual(order1.volume_left, 0)
        self.assertEqual(order1.limit_price, 374.0)  # 判断nan
        self.assertEqual(order1.price_type, "LIMIT")
        self.assertEqual(order1.volume_condition, "ALL")
        self.assertEqual(order1.time_condition, "IOC")
        self.assertEqual(order1.last_msg, "全部成交")
        self.assertAlmostEqual(1632883568008631000 / 1e9, order1.insert_date_time / 1e9, places=0)
        self.assertEqual(order1.status, "FINISHED")
        self.assertEqual(len(order1.trade_records.items()), 1)  # 没有成交记录

        self.assertEqual(order2.order_id, "PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09")
        self.assertEqual(order2.direction, "BUY")
        self.assertEqual(order2.offset, "OPEN")
        self.assertEqual(order2.volume_orign, 2)
        self.assertEqual(order2.volume_left, 0)
        self.assertEqual(order2.limit_price, 68800.0)
        self.assertEqual(order2.price_type, "LIMIT")
        self.assertEqual(order2.volume_condition, "ALL")
        self.assertEqual(order2.time_condition, "IOC")
        self.assertEqual(order2.last_msg, "全部成交")
        self.assertAlmostEqual(1632883570506217000 / 1e9, order2.insert_date_time / 1e9, places=0)
        self.assertEqual(order2.status, "FINISHED")
        for k, v in order1.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1632883568008873000 / 1e9, v.trade_date_time / 1e9, places=0)
            del v.trade_date_time
            self.assertEqual(
                {'order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|2', 'exchange_trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|2', 'exchange_id': 'SHFE', 'instrument_id': 'au2112', 'direction': 'BUY', 'offset': 'OPEN', 'price': 374.0, 'volume': 2, 'user_id': 'TQSIM', 'commission': 20.0},
                v)
        api.close()

    def test_insert_order_fak(self):
        """
        下单
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_insert_order_fak_simulate.script.lzma"))
        # 测试: 模拟账户下单
        # 非回测, 则需在盘中生成测试脚本: 测试脚本重新生成后，数据根据实际情况有变化,因此需要修改assert语句的内容

        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("SHFE.au2112", "BUY", "OPEN", 2, limit_price=374, advanced="FAK")
        order2 = api.insert_order("SHFE.cu2112", "BUY", "OPEN", 2, limit_price=68800, advanced="FAK")
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()
        print(order1)
        print(order2)
        print(order2.trade_records.items())
        self.assertEqual(order1.order_id, "PYSDK_insert_1710cf5327ac435a7a97c643656412a9")
        self.assertEqual(order1.direction, "BUY")
        self.assertEqual(order1.offset, "OPEN")
        self.assertEqual(order1.volume_orign, 2)
        self.assertEqual(order1.volume_left, 0)
        self.assertEqual(order1.limit_price, 374.0)  # 判断nan
        self.assertEqual(order1.price_type, "LIMIT")
        self.assertEqual(order1.volume_condition, "ANY")
        self.assertEqual(order1.time_condition, "IOC")
        self.assertEqual(order1.last_msg, "全部成交")
        self.assertAlmostEqual(1632883590509573000 / 1e9, order1.insert_date_time / 1e9, places=0)
        self.assertEqual(order1.status, "FINISHED")
        self.assertEqual(len(order1.trade_records.items()), 1)  # 没有成交记录

        self.assertEqual(order2.order_id, "PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09")
        self.assertEqual(order2.direction, "BUY")
        self.assertEqual(order2.offset, "OPEN")
        self.assertEqual(order2.volume_orign, 2)
        self.assertEqual(order2.volume_left, 0)
        self.assertEqual(order2.limit_price, 68800.0)
        self.assertEqual(order2.price_type, "LIMIT")
        self.assertEqual(order2.volume_condition, "ANY")
        self.assertEqual(order2.time_condition, "IOC")
        self.assertEqual(order2.last_msg, "全部成交")
        self.assertAlmostEqual(1632883592506680000 / 1e9, order2.insert_date_time / 1e9, places=0)
        self.assertEqual(order2.status, "FINISHED")
        for k, v in order2.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1632883592506805000 / 1e9, v.trade_date_time / 1e9, places=0)
            del v.trade_date_time
            self.assertEqual(
                v, {'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_id': 'SHFE', 'instrument_id': 'cu2112', 'direction': 'BUY', 'offset': 'OPEN', 'price': 68800.0, 'volume': 2, 'user_id': 'TQSIM', 'commission': 34.555}
            )
        api.close()

    def test_cancel_order(self):
        """
        撤单

        注：本函数不是回测，重新在盘中生成测试用例script文件时更改为当前可交易的合约代码,且_ins_url可能需修改。
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_cancel_order_simulate.script.lzma"))
        # 测试: 模拟账户
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("DCE.jd2201", "BUY", "OPEN", 1, limit_price=4310)
        order2 = api.insert_order("SHFE.cu2112", "BUY", "OPEN", 2, limit_price=66900)
        api.wait_update()
        self.assertEqual("ALIVE", order1.status)
        self.assertEqual("ALIVE", order2.status)
        api.cancel_order(order1)
        api.cancel_order(order2.order_id)
        while order1.status != "FINISHED" or order2.status != "FINISHED":
            api.wait_update()
        self.assertEqual("FINISHED", order1.status)
        self.assertEqual("FINISHED", order2.status)
        self.assertNotEqual(order1.volume_left, 0)
        self.assertNotEqual(order2.volume_left, 0)
        api.close()

    def test_get_account(self):
        """
        获取账户资金信息
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_get_account_simulate.script.lzma"))
        # 测试: 获取数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order = api.insert_order("DCE.jd2201", "BUY", "OPEN", 1, limit_price=4460)
        while order.status == "ALIVE":
            api.wait_update()
        account = api.get_account()
        print(str(account))
        # 测试脚本重新生成后，数据根据实际情况有变化
        self.assertEqual(
            str(account),
            "{'currency': 'CNY', 'pre_balance': 10000000.0, 'static_balance': 10000000.0, 'balance': 9998923.4885, 'available': 9995884.788500002, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -1070.0, 'position_profit': -1070.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 3038.7, 'frozen_commission': 0.0, 'commission': 6.5115, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.00030390271547680914, 'market_value': 0.0}")
        self.assertEqual(account.currency, "CNY")
        self.assertEqual(account.pre_balance, 10000000.0)
        self.assertEqual(9998923.4885, account.balance)
        self.assertEqual(6.5115, account["commission"])
        self.assertEqual(3038.7, account["margin"])
        self.assertEqual(-1070.0, account.position_profit)
        api.close()

    def test_get_position(self):
        """
        获取持仓
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_get_position_simulate.script.lzma"))
        # 测试: 获取数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("DCE.jd2201", "BUY", "OPEN", 1, limit_price=4460)
        order2 = api.insert_order("DCE.jd2201", "BUY", "OPEN", 3)
        order3 = api.insert_order("DCE.jd2201", "SELL", "OPEN", 3)
        while order1.status == "ALIVE" or order2.status == "ALIVE" or order3.status == "ALIVE":
            api.wait_update()
        position = api.get_position("DCE.jd2201")
        print(str(position))
        # 测试脚本重新生成后，数据根据实际情况有变化
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'jd2201', 'pos_long_his': 0, 'pos_long_today': 4, 'pos_short_his': 0, 'pos_short_today': 3, 'volume_long_today': 4, 'volume_long_his': 0, 'volume_long': 4, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 3, 'volume_short_his': 0, 'volume_short': 3, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 4380.5, 'open_price_short': 4353.0, 'open_cost_long': 175220.0, 'open_cost_short': 130590.0, 'position_price_long': 4380.5, 'position_price_short': 4353.0, 'position_cost_long': 175220.0, 'position_cost_short': 130590.0, 'float_profit_long': -1100.0, 'float_profit_short': 0.0, 'float_profit': -1100.0, 'position_profit_long': -1100.0, 'position_profit_short': 0.0, 'position_profit': -1100.0, 'margin_long': 12154.8, 'margin_short': 9116.099999999999, 'margin': 21270.899999999998, 'market_value_long': 0.0, 'market_value_short': 0.0, 'market_value': 0.0, 'pos': 1, 'pos_long': 4, 'pos_short': 3, 'last_price': 4353.0, 'underlying_last_price': nan, 'future_margin': 3038.7}",
            str(position))
        self.assertEqual(1, position.pos)
        self.assertEqual(4, position.pos_long)
        self.assertEqual(3, position.pos_short)
        self.assertEqual(position.exchange_id, "DCE")
        self.assertEqual(position.instrument_id, "jd2201")
        self.assertEqual(position.pos_long_his, 0)
        self.assertEqual(position.pos_long_today, 4)
        self.assertEqual(position.pos_short_his, 0)
        self.assertEqual(position.pos_short_today, 3)
        self.assertEqual(position.volume_long_today, 4)
        self.assertEqual(position.volume_long_his, 0)
        self.assertEqual(position.volume_long, 4)
        self.assertEqual(position.volume_long_frozen_today, 0)
        self.assertEqual(position.volume_long_frozen_his, 0)
        self.assertEqual(position.volume_long_frozen, 0)
        self.assertEqual(position.volume_short_today, 3)
        self.assertEqual(position.volume_short_his, 0)
        self.assertEqual(position.volume_short, 3)
        self.assertEqual(position.volume_short_frozen_today, 0)
        self.assertEqual(position.volume_short_frozen_his, 0)
        self.assertEqual(position.volume_short_frozen, 0)
        self.assertEqual(position.open_price_long, 4380.5)
        self.assertEqual(position.open_price_short, 4353.0)
        self.assertEqual(position.open_cost_long, 175220.0)
        self.assertEqual(position.open_cost_short, 130590.0)
        self.assertEqual(position.position_price_long, 4380.5)
        self.assertEqual(position.position_price_short, 4353.0)
        self.assertEqual(position.position_cost_long, 175220.0)
        self.assertEqual(position.position_cost_short, 130590.0)
        self.assertEqual(position.float_profit_long, -1100.0)
        self.assertEqual(position.float_profit_short, 0.0)
        self.assertEqual(position.float_profit, -1100.0)
        self.assertEqual(position.position_profit_long, -1100.0)
        self.assertEqual(position.position_profit_short, 0.0)
        self.assertEqual(position.position_profit, -1100.0)
        self.assertEqual(position.margin_long, 12154.8)
        self.assertEqual(position.margin_short, 9116.099999999999)
        self.assertEqual(position.margin, 21270.899999999998)
        self.assertEqual(position.market_value_long, 0.0)
        self.assertEqual(position.market_value_short, 0.0)
        self.assertEqual(position.market_value, 0.0)
        self.assertEqual(position.last_price, 4353.0)
        self.assertEqual(position.future_margin, 3038.7)
        # 其他取值方式测试
        self.assertEqual(position["pos_long_today"], 4)
        self.assertEqual(position["pos_short_today"], 3)
        self.assertEqual(position["volume_long_his"], 0)
        self.assertEqual(position["volume_long"], 4)
        api.close()

    def test_get_trade(self):
        """
        获取成交记录
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_get_trade_simulate.script.lzma"))
        # 测试: 模拟账户
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("DCE.jd2201", "BUY", "OPEN", 1)
        order2 = api.insert_order("SHFE.cu2112", "BUY", "OPEN", 2, limit_price=68800)
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()
        trade1 = api.get_trade("PYSDK_insert_1710cf5327ac435a7a97c643656412a9|1")
        trade2 = api.get_trade("PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2")
        print(trade1)
        print(trade2)
        self.assertAlmostEqual(1632883657824019000 / 1e9, trade1.trade_date_time / 1e9, places=0)
        self.assertAlmostEqual(1632883657836105000 / 1e9, trade2.trade_date_time / 1e9, places=0)
        del trade1["trade_date_time"]
        del trade2["trade_date_time"]
        self.assertEqual(
            str(trade1),
            "{'order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|1', 'exchange_trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|1', 'exchange_id': 'DCE', 'instrument_id': 'jd2201', 'direction': 'BUY', 'offset': 'OPEN', 'price': 4355.0, 'volume': 1, 'user_id': 'TQSIM', 'commission': 6.5115}")
        self.assertEqual(
            str(trade2),
            "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_id': 'SHFE', 'instrument_id': 'cu2112', 'direction': 'BUY', 'offset': 'OPEN', 'price': 68800.0, 'volume': 2, 'user_id': 'TQSIM', 'commission': 34.555}")
        self.assertEqual(trade1.direction, "BUY")
        self.assertEqual(trade1.offset, "OPEN")
        self.assertEqual(trade1.price, 4355.0)
        self.assertEqual(trade1.volume, 1)
        self.assertEqual(trade1.commission, 6.5115)

        self.assertEqual(trade2.direction, "BUY")
        self.assertEqual(trade2.offset, "OPEN")
        self.assertEqual(trade2.price, 68800.0)
        self.assertEqual(trade2.volume, 2)
        self.assertEqual(trade2.commission, 34.555)
        api.close()

    def test_get_order(self):
        """
        获取委托单信息
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_get_order_simulate.script.lzma"))
        # 测试: 模拟账户下单
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("DCE.jd2201", "BUY", "OPEN", 1)
        order2 = api.insert_order("SHFE.cu2112", "SELL", "OPEN", 2, limit_price=67800)
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()
        get_order1 = api.get_order(order1.order_id)
        get_order2 = api.get_order(order2.order_id)
        self.assertEqual(get_order1.order_id, "PYSDK_insert_1710cf5327ac435a7a97c643656412a9")
        self.assertEqual(get_order1.direction, "BUY")
        self.assertEqual(get_order1.offset, "OPEN")
        self.assertEqual(get_order1.volume_orign, 1)
        self.assertEqual(get_order1.volume_left, 0)
        self.assertNotEqual(get_order1.limit_price, get_order1.limit_price)  # 判断nan
        self.assertEqual(get_order1.price_type, "ANY")
        self.assertEqual(get_order1.volume_condition, "ANY")
        self.assertEqual(get_order1.time_condition, "IOC")
        # 因为TqSim模拟交易的 insert_date_time 不是固定值，所以改为判断范围（前后100毫秒）
        self.assertAlmostEqual(1632883666824046000 / 1e9, get_order1.insert_date_time / 1e9, places=0)
        self.assertEqual(get_order1.last_msg, "全部成交")
        self.assertEqual(get_order1.status, "FINISHED")
        self.assertEqual(get_order1.frozen_margin, 0)

        self.assertEqual(get_order2.order_id, "PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09")
        self.assertEqual(get_order2.direction, "SELL")
        self.assertEqual(get_order2.offset, "OPEN")
        self.assertEqual(get_order2.volume_orign, 2)
        self.assertEqual(get_order2.volume_left, 0)
        self.assertEqual(get_order2.limit_price, 67800.0)
        self.assertEqual(get_order2.price_type, "LIMIT")
        self.assertEqual(get_order2.volume_condition, "ANY")
        self.assertEqual(get_order2.time_condition, "GFD")
        self.assertAlmostEqual(1632883670505757000 / 1e9, get_order2["insert_date_time"] / 1e9, places=0)
        self.assertEqual(get_order2["last_msg"], "全部成交")
        self.assertEqual(get_order2["status"], "FINISHED")
        self.assertEqual(get_order2.frozen_margin, 0)

        del get_order1["insert_date_time"]
        del get_order2["insert_date_time"]
        self.assertEqual(
            str(get_order1),
            "{'order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'exchange_order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'exchange_id': 'DCE', 'instrument_id': 'jd2201', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 1, 'volume_left': 0, 'limit_price': nan, 'price_type': 'ANY', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'last_msg': '全部成交', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 4356.0, 'user_id': 'TQSIM', 'frozen_margin': 0.0, 'frozen_premium': 0.0}"
        )
        self.assertEqual(
            str(get_order2),
            "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_id': 'SHFE', 'instrument_id': 'cu2112', 'direction': 'SELL', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 0, 'limit_price': 67800.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 67800.0, 'user_id': 'TQSIM', 'frozen_margin': 0.0, 'frozen_premium': 0.0}"
        )
        api.close()

    # 期权模拟交易盘中测试

    def test_insert_order_option(self):
        """
            期权下单
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_insert_order_simulate_option.script.lzma"))
        # 测试: 模拟账户下单
        # 非回测, 则需在盘中生成测试脚本: 测试脚本重新生成后，数据根据实际情况有变化,因此需要修改assert语句的内容
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("SHFE.cu2111C69000", "BUY", "OPEN", 1, limit_price=1800)
        order2 = api.insert_order("CZCE.SR201C5700", "SELL", "OPEN", 2, limit_price=140)
        order3 = api.insert_order("DCE.m2111-P-2800", "BUY", "OPEN", 3, limit_price=113)
        while order1.status == "ALIVE" or order2.status == "ALIVE" or order3.status == "ALIVE":
            api.wait_update()
        self.assertEqual(order1.order_id, "PYSDK_insert_1710cf5327ac435a7a97c643656412a9")
        self.assertAlmostEqual(1632885810534386000 / 1e9, order1['insert_date_time'] / 1e9, places=0)
        del order1['insert_date_time']
        self.assertEqual(
            str(order1),
            "{'order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'exchange_order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'exchange_id': 'SHFE', 'instrument_id': 'cu2111C69000', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 1, 'volume_left': 0, 'limit_price': 1800.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 1800.0, 'user_id': 'TQSIM', 'frozen_margin': 0.0, 'frozen_premium': 0.0}"
        )
        for k, v in order1.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1632885810532095000 / 1e9, v.trade_date_time / 1e9, places=0)
            del v.trade_date_time
            self.assertEqual(
                v,
                {'order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9',
                 'trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|1',
                 'exchange_trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|1', 'exchange_id': 'SHFE',
                 'instrument_id': 'cu2111C69000', 'direction': 'BUY', 'offset': 'OPEN', 'price': 1800.0, 'volume': 1,
                 'user_id': 'TQSIM', 'commission': 10}
            )

        self.assertEqual(order2.order_id, "PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09")
        self.assertAlmostEqual(1632885810552631000 / 1e9, order2['insert_date_time'] / 1e9, places=0)
        del order2['insert_date_time']
        self.assertEqual(
            str(order2),
            "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_id': 'CZCE', 'instrument_id': 'SR201C5700', 'direction': 'SELL', 'offset': 'OPEN', 'volume_orign': 2, 'volume_left': 0, 'limit_price': 140.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 140.0, 'user_id': 'TQSIM', 'frozen_margin': 0.0, 'frozen_premium': 0.0}"
        )

        for k, v in order2.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1632885810554931000 / 1e9, v.trade_date_time / 1e9, places=0)
            del v.trade_date_time
            self.assertEqual(
                v,
                {'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09',
                 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2',
                 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|2', 'exchange_id': 'CZCE',
                 'instrument_id': 'SR201C5700', 'direction': 'SELL', 'offset': 'OPEN', 'price': 140.0, 'volume': 2,
                 'user_id': 'TQSIM', 'commission': 20}
            )

        self.assertEqual(order3.order_id, "PYSDK_insert_c79d679346d4ac7a5c3902b38963dc6e")
        self.assertAlmostEqual(1632885810562177000 / 1e9, order3['insert_date_time'] / 1e9, places=0)
        del order3['insert_date_time']
        self.assertEqual(
            str(order3),
            "{'order_id': 'PYSDK_insert_c79d679346d4ac7a5c3902b38963dc6e', 'exchange_order_id': 'PYSDK_insert_c79d679346d4ac7a5c3902b38963dc6e', 'exchange_id': 'DCE', 'instrument_id': 'm2111-P-2800', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 3, 'volume_left': 0, 'limit_price': 113.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'is_dead': True, 'is_online': False, 'is_error': False, 'trade_price': 113.0, 'user_id': 'TQSIM', 'frozen_margin': 0.0, 'frozen_premium': 0.0}"
        )
        for k, v in order3.trade_records.items():  # 模拟交易为一次性全部成交，因此只有一条成交记录
            self.assertAlmostEqual(1632885810557608000 / 1e9, v.trade_date_time / 1e9, places=0)
            del v.trade_date_time
            self.assertEqual(
                v,
                {'order_id': 'PYSDK_insert_c79d679346d4ac7a5c3902b38963dc6e',
                 'trade_id': 'PYSDK_insert_c79d679346d4ac7a5c3902b38963dc6e|3',
                 'exchange_trade_id': 'PYSDK_insert_c79d679346d4ac7a5c3902b38963dc6e|3', 'exchange_id': 'DCE',
                 'instrument_id': 'm2111-P-2800', 'direction': 'BUY', 'offset': 'OPEN', 'price': 113.0, 'volume': 3,
                 'user_id': 'TQSIM', 'commission': 30}
            )
        api.close()

    def test_cancel_order_option(self):
        """
            撤单
            注：本函数不是回测，重新盘中生成测试用例script文件时更改为当前可交易的合约代码,且_ins_url可能需修改。
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_cancel_order_simulate_option.script.lzma"))
        # 测试: 模拟账户
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("DCE.m2111-P-2800", "BUY", "OPEN", 1, limit_price=60)
        order2 = api.insert_order("SHFE.cu2111C69000", "BUY", "OPEN", 2, limit_price=1200)
        api.wait_update()
        self.assertEqual("ALIVE", order1.status)
        api.cancel_order(order1)
        api.cancel_order(order2.order_id)
        while order1.status != "FINISHED" or order2.status != "FINISHED":
            api.wait_update()
        self.assertEqual("FINISHED", order1.status)
        self.assertEqual("FINISHED", order2.status)
        self.assertEqual(order1.volume_left, 0)
        self.assertNotEqual(order2.volume_left, 0)
        api.close()

    def test_get_account_option(self):
        """
            获取账户资金信息
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_get_account_simulate_option.script.lzma"))
        # 测试: 获取数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("CZCE.SR201C5700", "SELL", "OPEN", 2, limit_price=120)
        order2 = api.insert_order("DCE.m2201-P-3500", "BUY", "OPEN", 3, limit_price=123)
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()
        account = api.get_account()
        # 测试脚本重新生成后，数据根据实际情况有变化
        print(str(account))
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 10000000.0, 'static_balance': 10000000.0, 'balance': 9998875.0, 'available': 9981607.6, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -1075.0, 'position_profit': 0.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 17052.4, 'frozen_commission': 0.0, 'commission': 50.0, 'frozen_premium': 0.0, 'premium': -1290.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.001705431861084372, 'market_value': 215.0}",
            str(account)
        )
        self.assertEqual(account.currency, "CNY")
        self.assertEqual(account.pre_balance, 10000000.0)
        self.assertEqual(account.balance, 9998875.0)
        self.assertEqual(account["commission"], 50.0)
        self.assertEqual(account["margin"], 17052.4)
        self.assertEqual(account.position_profit, 0.0)
        self.assertEqual(account.available, 9981607.6)
        self.assertNotEqual(account.ctp_balance, account.ctp_balance)  # nan
        self.assertEqual(account.float_profit, -1075.0)
        self.assertEqual(account.margin, 17052.4)
        self.assertEqual(account.commission, 50.0)
        self.assertEqual(account.premium, -1290.0)
        self.assertEqual(account.risk_ratio, 0.001705431861084372)
        self.assertEqual(account.market_value, 215.0)
        api.close()

    def test_get_position_option(self):
        """
            获取持仓
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_get_position_simulate_option.script.lzma"))
        # 测试: 获取数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("CZCE.SR201C5700", "BUY", "OPEN", 2, limit_price=310)
        order2 = api.insert_order("CZCE.SR201C5700", "BUY", "OPEN", 3, limit_price=310)
        order3 = api.insert_order("CZCE.SR201C5700", "SELL", "OPEN", 3, limit_price=120)
        order4 = api.insert_order("CZCE.SR201C5700", "SELL", "OPEN", 3)  # 只有郑商所支持期权市价单
        self.assertRaises(Exception, api.insert_order, "DCE.m2201-P-3500", "BUY", "OPEN", 1)# 只有郑商所支持期权市价单

        while order1.status == "ALIVE" or order2.status == "ALIVE" or order3.status == "ALIVE" or order4.status == "ALIVE":
            api.wait_update()
        self.assertEqual(order4.volume_left, 0)
        position = api.get_position("CZCE.SR201C5700")
        position2 = api.get_position("DCE.m2201-P-3500")
        self.assertEqual(0, position2.pos_long)
        self.assertEqual(0, position2.pos_short)

        # 测试脚本重新生成后，数据根据实际情况有变化
        self.assertEqual(
            "{'exchange_id': 'CZCE', 'instrument_id': 'SR201C5700', 'pos_long_his': 0, 'pos_long_today': 5, 'pos_short_his': 0, 'pos_short_today': 6, 'volume_long_today': 5, 'volume_long_his': 0, 'volume_long': 5, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 6, 'volume_short_his': 0, 'volume_short': 6, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 310.0, 'open_price_short': 125.25, 'open_cost_long': 15500.0, 'open_cost_short': 7515.0, 'position_price_long': 310.0, 'position_price_short': 125.25, 'position_cost_long': 15500.0, 'position_cost_short': 7515.0, 'float_profit_long': -7375.0, 'float_profit_short': -2235.0, 'float_profit': -9610.0, 'position_profit_long': 0.0, 'position_profit_short': 0.0, 'position_profit': 0.0, 'margin_long': 0.0, 'margin_short': 51157.200000000004, 'margin': 51157.200000000004, 'market_value_long': 8125.0, 'market_value_short': -9750.0, 'market_value': -1625.0, 'pos': -1, 'pos_long': 5, 'pos_short': 6, 'last_price': 162.5, 'underlying_last_price': 5751.0, 'future_margin': nan}",
            str(position)
        )
        self.assertEqual(-1, position.pos)
        self.assertEqual(5, position.pos_long)
        self.assertEqual(6, position.pos_short)
        self.assertEqual(position.exchange_id, "CZCE")
        self.assertEqual(position.instrument_id, "SR201C5700")
        self.assertEqual(position.pos_long_his, 0)
        self.assertEqual(position.pos_long_today, 5)
        self.assertEqual(position.pos_short_his, 0)
        self.assertEqual(position.pos_short_today, 6)
        self.assertEqual(position.volume_long_today, 5)
        self.assertEqual(position.volume_long_his, 0)
        self.assertEqual(position.volume_long, 5)
        self.assertEqual(position.volume_long_frozen_today, 0)
        self.assertEqual(position.volume_long_frozen_his, 0)
        self.assertEqual(position.volume_long_frozen, 0)
        self.assertEqual(position.volume_short_today, 6)
        self.assertEqual(position.volume_short_his, 0)
        self.assertEqual(position.volume_short, 6)
        self.assertEqual(position.volume_short_frozen_today, 0)
        self.assertEqual(position.volume_short_frozen_his, 0)
        self.assertEqual(position.volume_short_frozen, 0)
        self.assertEqual(position.open_price_long, 310.0)
        self.assertEqual(position.open_price_short, 125.25)
        self.assertEqual(position.open_cost_long, 15500.0)
        self.assertEqual(position.open_cost_short, 7515.0)
        self.assertEqual(position.position_price_long, 310.0)
        self.assertEqual(position.position_price_short, 125.25)
        self.assertEqual(position.position_cost_long, 15500.0)
        self.assertEqual(position.position_cost_short, 7515.0)
        self.assertEqual(position.float_profit_long, -7375.0)
        self.assertEqual(position.float_profit_short, -2235.0)
        self.assertEqual(position.float_profit, -9610.0)
        self.assertEqual(position.position_profit_long, 0.0)
        self.assertEqual(position.position_profit_short, 0.0)
        self.assertEqual(position.position_profit, 0.0)
        self.assertEqual(position.margin_long, 0.0)
        self.assertEqual(position.margin_short, 51157.200000000004)
        self.assertEqual(position.margin, 51157.200000000004)
        self.assertEqual(position.market_value_long, 8125.0)
        self.assertEqual(position.market_value_short, -9750.0)
        self.assertEqual(position.market_value, -1625.0)
        self.assertEqual(position.last_price, 162.5)
        self.assertEqual(position.underlying_last_price, 5751.0)

        # 其他取值方式测试
        self.assertEqual(position["pos_long_today"], 5)
        self.assertEqual(position["pos_short_today"], 6)
        self.assertEqual(position["volume_long_his"], 0)
        self.assertEqual(position["volume_long"], 5)
        api.close()

    def test_get_trade_option(self):
        """
            获取成交记录
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        md_url = "wss://api.shinnytech.com/t/nfmd/front/mobile"
        set_test_script(os.path.join(dir_path, "log_file", "test_td_basic_get_trade_simulate_option.script.lzma"))
        # 测试: 模拟账户
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        order1 = api.insert_order("CZCE.SR201C5700", "SELL", "OPEN", 2, limit_price=120)
        order2 = api.insert_order("DCE.m2201-P-3500", "BUY", "OPEN", 3, limit_price=123)
        while order1.status == "ALIVE" or order2.status == "ALIVE":
            api.wait_update()
        trade1 = api.get_trade("PYSDK_insert_1710cf5327ac435a7a97c643656412a9|2")
        trade2 = api.get_trade("PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|3")
        print(str(trade1))
        print(str(trade2))
        self.assertAlmostEqual(1632886199010616000 / 1e9, trade1.trade_date_time / 1e9, places=0)
        self.assertAlmostEqual(1632886199813992000 / 1e9, trade2.trade_date_time / 1e9, places=0)
        del trade1["trade_date_time"]
        del trade2["trade_date_time"]
        self.assertEqual(
            str(trade1),
            "{'order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|2', 'exchange_trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|2', 'exchange_id': 'CZCE', 'instrument_id': 'SR201C5700', 'direction': 'SELL', 'offset': 'OPEN', 'price': 120.0, 'volume': 2, 'user_id': 'TQSIM', 'commission': 20}")
        self.assertEqual(
            str(trade2),
            "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|3', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|3', 'exchange_id': 'DCE', 'instrument_id': 'm2201-P-3500', 'direction': 'BUY', 'offset': 'OPEN', 'price': 123.0, 'volume': 3, 'user_id': 'TQSIM', 'commission': 30}")
        self.assertEqual(trade1.direction, "SELL")
        self.assertEqual(trade1.offset, "OPEN")
        self.assertEqual(trade1.price, 120.0)
        self.assertEqual(trade1.volume, 2)
        self.assertEqual(trade1.commission, 20)

        self.assertEqual(trade2.direction, "BUY")
        self.assertEqual(trade2.offset, "OPEN")
        self.assertEqual(trade2.price, 123.0)
        self.assertEqual(trade2.volume, 3)
        self.assertEqual(trade2.commission, 30)
        api.close()
