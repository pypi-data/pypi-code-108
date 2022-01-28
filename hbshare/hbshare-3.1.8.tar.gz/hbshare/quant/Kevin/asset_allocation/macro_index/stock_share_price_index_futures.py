"""
基差相关数据
"""
import pandas as pd
from datetime import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class StockSharePriceIndex:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_share_price_index_futures'

    def get_share_price_index_futures_data(self):
        # ZZ500
        res = w.wsd('000905.SH', 'close', self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch index data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            data = pd.DataFrame(res.Data[0], index=res.Times, columns=res.Codes)
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        index_data = data.copy()
        # index futures
        index_list = ['IC00.CFE', 'IC01.CFE', 'IC02.CFE', 'IC03.CFE']
        res = w.wsd(','.join(index_list), 'settle', self.start_date, self.end_date, '')
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch index_futures data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        future_data = data.copy()

        data = pd.merge(index_data, future_data, on='trade_date')
        data.rename(columns={'000905.SH': 'ZZ500', 'IC00.CFE': 'IC00', 'IC01.CFE': 'IC01',
                             'IC02.CFE': 'IC02', 'IC03.CFE': 'IC03'}, inplace=True)

        return data

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_share_price_index_futures_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            delete_duplicate_records(sql_script)
            WriteToDB().write_to_db(data, self.table_name)
        else:
            data = self.get_share_price_index_futures_data()
            sql_script = """
                    create table mac_share_price_index_futures(
                    id int auto_increment primary key,
                    trade_date date not null unique,
                    ZZ500 decimal(7, 2),
                    IC00 decimal(7, 2),
                    IC01 decimal(7, 2),
                    IC02 decimal(7, 2),
                    IC03 decimal(7, 2)) 
                """
            create_table(self.table_name, sql_script)
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    StockSharePriceIndex('2021-12-31', '2021-12-31', is_increment=1).get_construct_result()

