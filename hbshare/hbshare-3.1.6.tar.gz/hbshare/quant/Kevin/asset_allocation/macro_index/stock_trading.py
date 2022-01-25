"""
股票市场成交及换手数据
"""
import pandas as pd
from datetime import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class StockTrading:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_stock_trading'

    def get_stock_trading_data(self):
        """
        股票市场交易类数据
        """
        # VIX指数
        res = w.wsd("VIX.GI", "close", self.start_date, self.end_date, "")
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch VIX data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        vix_index = data.copy()
        # 成交额数据：两市、300、500、1000及其他
        res = w.wsd("000001.SH,399001.SZ,000300.SH,000905.SH,000852.SH", "amt", self.start_date, self.end_date, "")
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch amt data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns={"000001.SH": "amt_sh", "399001.SZ": "amt_sz", "000300.SH": "amt_300",
                                 "000905.SH": "amt_500", "000852.SH": "amt_1000"}, inplace=True)
            data.eval("amt_other = amt_sh + amt_sz - amt_300 - amt_500 - amt_1000", inplace=True)
            data = (data.set_index('trade_date') / 1e+8).reset_index()
        amt = data.copy()
        # 换手率数据：两市、300、500、1000
        res = w.wsd("000001.SH,399001.SZ,000300.SH,000905.SH,000852.SH", "turn", self.start_date, self.end_date, "")
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch turn data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns={"000001.SH": "turn_sh", "399001.SZ": "turn_sz", "000300.SH": "turn_300",
                                 "000905.SH": "turn_500", "000852.SH": "turn_1000"}, inplace=True)
        turn = data.copy()
        # 主力资金流入数据
        res = w.wsd("000001.SH,399001.SZ", "mfd_inflow_m", self.start_date, self.end_date, "unit=1")
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch inflow data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns={"000001.SH": "inflow_sh", "399001.SZ": "inflow_sz"}, inplace=True)
            data['inflow_sh'] /= 1e+8
            data['inflow_sz'] /= 1e+8
        flow = data.copy()
        all_data = vix_index.merge(amt, on='trade_date', how='outer').merge(turn, on='trade_date', how='outer').merge(
            flow, on='trade_date', how='outer').rename(columns={"VIX.GI": "VIX"})

        return all_data

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_stock_trading_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            delete_duplicate_records(sql_script)
            WriteToDB().write_to_db(data, self.table_name)
        else:
            data = self.get_stock_trading_data()
            sql_script = """
                    create table mac_stock_trading(
                    id int auto_increment primary key,
                    trade_date date not null unique,
                    VIX decimal(5, 2),
                    amt_sh decimal(7, 2),
                    amt_sz decimal(7, 2),
                    amt_300 decimal(7, 2),
                    amt_500 decimal(7, 2),
                    amt_1000 decimal(7, 2),
                    amt_other decimal(7, 2),
                    turn_sh decimal(4, 2),
                    turn_sz decimal(4, 2),
                    turn_300 decimal(4, 2),
                    turn_500 decimal(4, 2),
                    turn_1000 decimal(4, 2),
                    inflow_sh decimal(6, 2),
                    inflow_sz decimal(6, 2)) 
                """
            create_table(self.table_name, sql_script)
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    StockTrading('2021-06-06', '2021-09-06', is_increment=1).get_construct_result()