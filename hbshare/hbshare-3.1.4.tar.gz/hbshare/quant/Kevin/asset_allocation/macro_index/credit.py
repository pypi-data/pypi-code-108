"""
信用类指标
"""
import pandas as pd
from datetime import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class Credit:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_credit'

    def get_credit_data(self):
        """
        信用类数据：信用利差(余额加权):产业债AAA、信用利差(余额加权):产业债AA+、信用利差(余额加权):产业债AA、
                 信用利差(余额加权):城投债AAA、信用利差(余额加权):城投债AA+、信用利差(余额加权):城投债AA、
                 实体经济部门杠杆率、居民部门杠杆率、非金融企业部门杠杆率、政府部门杠杆率、商业银行:杠杆率
        """
        index_list = ['M1010107', 'M1010108', 'M1010109', 'M1010358', 'M1010359', 'M1010360',
                      'M6404532', 'M6404533', 'M6404534', 'M6404535', 'M6194530']
        name_dict = {'M1010107': "credit_spread_indu_AAA", "M1010108": "credit_spread_indu_AA_plus",
                     "M1010109": "credit_spread_indu_AA", "M1010358": "credit_spread_urban_AAA",
                     "M1010359": "credit_spread_urban_AA_plus", "M1010360": "credit_spread_urban_AA",
                     "M6404532": "leverage_1", "M6404533": "leverage_2", "M6404534": "leverage_3",
                     "M6404535": "leverage_4", "M6194530": "leverage_5"}

        res = w.edb(','.join(index_list), self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch credit data error: start_date = {}, end_date = {}".format(self.start_date, self.end_date))
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
            data = self.get_credit_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_credit(
                id int auto_increment primary key,
                trade_date date not null unique,
                credit_spread_indu_AAA decimal(6, 2),
                credit_spread_indu_AA_plus decimal(6, 2),
                credit_spread_indu_AA decimal(6, 2),
                credit_spread_urban_AAA decimal(6, 2),
                credit_spread_urban_AA_plus decimal(6, 2),
                credit_spread_urban_AA decimal(6, 2),                
                leverage_1 decimal(6, 2),
                leverage_2 decimal(6, 2),
                leverage_3 decimal(6, 2),
                leverage_4 decimal(6, 2),
                leverage_5 decimal(6, 2)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_credit_data()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    Credit('2005-12-01', '2021-04-23', is_increment=0).get_construct_result()