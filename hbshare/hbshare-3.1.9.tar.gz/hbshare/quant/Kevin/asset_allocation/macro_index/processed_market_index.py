"""
处理过的市场指数数据，用于添加在月度指标右轴
"""
import pandas as pd
from datetime import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class MarketIndex:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_market_index'

    def get_market_index_data(self):
        """
        沪深300、中证500、中债财富总指数、南华商品指数
        """
        index_list = ["000300.SH", "000905.SH", "H11001.CSI", "NH0100.NHF"]
        res = w.wsd(','.join(index_list), "close", self.start_date, self.end_date)

        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch market index data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            # 对齐到自然月末
            start_date, end_date = data.index[0], data.index[-1]
            data = data.reindex(pd.date_range(start_date, end_date)).fillna(method='ffill').reindex(
                pd.date_range(start_date, end_date, freq='M')).round(2)
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns={"000300.SH": "HS300", "000905.SH": "ZZ500",
                                 "H11001.CSI": "bond_index", "NH0100.NHF": "future_index"}, inplace=True)

        return data

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_market_index_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                    create table mac_market_index(
                    id int auto_increment primary key,
                    trade_date date not null unique,
                    HS300 decimal(8, 2),
                    ZZ500 decimal(8, 2),
                    bond_index decimal(8, 2),
                    future_index decimal(8, 2)) 
                """
            create_table(self.table_name, sql_script)
            data = self.get_market_index_data()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    MarketIndex('2021-01-04', '2021-06-25', is_increment=1).get_construct_result()