"""
国债收益率指标
"""
import pandas as pd
from datetime import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class TreasuryYield:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_treasury_yield'

    def get_treasury_yield_data(self):
        """
        国债收益率数据：各期限国债收益率数据、美国十年期国债收益率数据
        """
        index_list = ['M1001645', 'M1001646', 'M1001647', 'M1001648', 'M1001650', 'M1001652', 'M1001654', 'M1001655',
                      'M1001656', 'M1001657', 'G0000891']
        name_dict = {"M1001645": "ytm_6m", "M1001646": "ytm_1y", "M1001647": "ytm_2y", "M1001648": "ytm_3y",
                     "M1001650": "ytm_5y", "M1001652": "ytm_7y", "M1001654": "ytm_10y", "M1001655": "ytm_15y",
                     "M1001656": "ytm_20y", "M1001657": "ytm_30y", "G0000891": "usa_ytm_10y"}
        res = w.edb(','.join(index_list), self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch treasury yield data error: start_date = {}, end_date = {}".format(self.start_date, self.end_date))
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
            data = self.get_treasury_yield_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_treasury_yield(
                id int auto_increment primary key,
                trade_date date not null unique,
                ytm_6m decimal(6, 4),
                ytm_1y decimal(6, 4),
                ytm_2y decimal(6, 4),
                ytm_3y decimal(6, 4),
                ytm_5y decimal(6, 4),
                ytm_7y decimal(6, 4),
                ytm_10y decimal(6, 4),
                ytm_15y decimal(6, 4),
                ytm_20y decimal(6, 4),
                ytm_30y decimal(6, 4),
                usa_ytm_10y decimal(4, 2)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_treasury_yield_data()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    TreasuryYield('2007-12-14', '2021-04-23', is_increment=0).get_construct_result()