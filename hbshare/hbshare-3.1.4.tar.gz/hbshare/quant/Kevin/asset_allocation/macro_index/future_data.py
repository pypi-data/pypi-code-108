"""
期货市场数据
"""
import pandas as pd
from datetime import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class FutureMarketIndex:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_future_market_data'

    def get_future_market_data(self):
        """
        Wind商品指数数据
        """
        index_list = ['NMBM.WI', 'NMFI.WI', 'OOFI.WI', 'SOFI.WI', 'NFFI.WI',
                      'JJRI.WI', 'ENFI.WI', 'CIFI.WI', 'CRFI.WI', 'APFI.WI',
                      'CCFI.WI']
        all_data = []
        for index_name in index_list:
            res = w.wsd(index_name, "close,volume,oi_index", self.start_date, self.end_date, "")
            if res.ErrorCode != 0:
                data = pd.DataFrame()
                print("fetch future index data error: start_date = {}, end_date = {}".format(
                    self.start_date, self.end_date))
            else:
                data = pd.DataFrame(res.Data, index=res.Fields, columns=res.Times).T
                data.index.name = 'trade_date'
                data.reset_index(inplace=True)
                data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
                data['index_name'] = index_name

            all_data.append(data)
        all_data = pd.concat(all_data)

        return all_data

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_future_market_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_future_market_data(
                id int auto_increment primary key,
                trade_date date not null,
                index_name char(20),
                CLOSE decimal(6, 2),
                VOLUME decimal(9, 0),
                OI_INDEX decimal(9, 0)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_future_market_data()
            WriteToDB().write_to_db(data, self.table_name)


class FuturePrice:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_future_price'

    def get_future_price_data(self):
        """
        常见期货行情数据
        """
        index_list = ['CU.SHF', 'HC.SHF', 'I.DCE', 'J.DCE', 'JM.DCE', 'M.DCE',
                      'MA.CZC', 'P.DCE', 'PP.DCE', 'RB.SHF', 'Y.DCE', 'ZN.SHF']
        res = w.wsd(','.join(index_list), "close", self.start_date, self.end_date, "")
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch future index data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        return data

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_future_price_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_future_price(
                id int auto_increment primary key,
                trade_date date not null unique,
                CU.SHF decimal(6, 0),
                HC.SHF decimal(6, 0),
                I.DCE decimal(6, 0),
                J.DCE decimal(6, 0),
                JM.DCE decimal(6, 0),
                M.DCE decimal(6, 0),
                MA.CZC decimal(6, 0),
                P.DCE decimal(6, 0),
                PP.SHF decimal(6, 0),
                RB.SHF decimal(6, 0),
                Y.DCE decimal(6, 0),
                ZN.SHF decimal(6, 0)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_future_price_data()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    FutureMarketIndex('2020-01-01', '2021-06-29', is_increment=1).get_construct_result()
    # FuturePrice('2015-01-05', '2021-06-29', is_increment=0).get_construct_result()