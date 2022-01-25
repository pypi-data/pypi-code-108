"""
债券交易指标
"""
import pandas as pd
from datetime import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class BondTrading:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_bond_trading'

    def get_bond_trading_data(self):
        """
        R001成交量、R007成交量、质押式回购成交量
        """
        index_list = ['M0330244', 'M0330245', 'M0041739']
        name_dict = {"M0330244": "R001", "M0330245": "R007", "M0041739": "bank_repo"}
        res = w.edb(','.join(index_list), self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch bond trading data error: start_date = {}, end_date = {}".format(self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns=name_dict, inplace=True)

        return data

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_bond_trading_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_bond_trading(
                id int auto_increment primary key,
                trade_date date not null unique,
                R001 decimal(8, 2),
                R007 decimal(8, 2),
                bank_repo decimal(8, 2))
            """
            create_table(self.table_name, sql_script)
            data = self.get_bond_trading_data()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    BondTrading('2010-01-01', '2021-06-25', is_increment=0).get_construct_result()