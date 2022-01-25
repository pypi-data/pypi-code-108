"""
通胀类指标
"""
import pandas as pd
from datetime import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class Inflation:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_inflation'

    def get_inflation_data(self):
        """
        通胀类数据：LME铜、CPI：当月同比、PPI：当月同比
        """
        index_list = ['M0000612', 'M0001227']
        name_dict = {"M0000612": "CPI_yoy", "M0001227": "PPI_yoy"}

        res = w.edb(','.join(index_list), self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch inflation data error: start_date = {}, end_date = {}".format(self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns=name_dict, inplace=True)
        inflation = data.copy()
        # CA.LME
        res = w.wsd("CA.LME", "close", self.start_date, self.end_date, "")
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch inflation data error: start_date = {}, end_date = {}".format(self.start_date, self.end_date))
        else:
            data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns=name_dict, inplace=True)

        data = pd.merge(inflation, data, on='trade_date', how='outer').sort_values(by='trade_date').rename(
            columns={"CA.LME": "LME"})
        data['LME'] = data['LME'].fillna(method='ffill')

        return data

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_inflation_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_inflation(
                id int auto_increment primary key,
                trade_date date not null unique,
                CPI_yoy decimal(4, 2),
                PPI_yoy decimal(4, 2),
                LME decimal(7, 2)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_inflation_data()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    Inflation('2005-01-01', '2021-04-23', is_increment=0).get_construct_result()
