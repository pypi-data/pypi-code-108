"""
汇率和价格指数
"""
import pandas as pd
from datetime import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class RatesAndPrice:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_rates_and_price'

    def get_rates_and_price_data(self):
        """
        汇率和价格指数类数据：有效联邦基金利率、人民币兑美元汇率、美元指数、中国大宗商品价格指数、中国:进出口金额:当月值、
        在岸人民币汇率、离岸人民币汇率
        """
        index_list = ['G1161292', 'M0000185', 'M0000271', 'S5042881', 'M0085847']
        name_dict = {'G1161292': "federal_funds_rate", 'M0000185': "exchange_rate_dollar",
                     'M0000271': "dollar_index", 'S5042881': "CCPI", "M0085847": "in_export_value"}

        res = w.edb(','.join(index_list), self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch rates and price data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns=name_dict, inplace=True)
        rates = data.copy()
        # USDCNY.IB-USDCNH.FX
        res = w.wsd("USDCNY.IB,USDCNH.FX", "close", self.start_date, self.end_date, "")
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch rates and price data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            data.rename(columns=name_dict, inplace=True)

        rates = pd.merge(rates, data, on='trade_date', how='outer').sort_values(by='trade_date').rename(
            columns={"USDCNY.IB": "USDCNY_IB", "USDCNH.FX": "USDCNH_FX"})

        return rates

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_rates_and_price_data()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                    create table mac_rates_and_price(
                    id int auto_increment primary key,
                    trade_date date not null unique,
                    federal_funds_rate decimal(4, 2),
                    exchange_rate_dollar decimal(6, 4),
                    dollar_index decimal(7, 4),
                    CCPI decimal(6, 2),
                    in_export_value decimal(10, 2),
                    USDCNY_IB decimal(6, 4),
                    USDCNH_FX decimal(6, 4)) 
                """
            create_table(self.table_name, sql_script)
            data = self.get_rates_and_price_data()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    RatesAndPrice('2005-01-01', '2021-06-10', is_increment=0).get_construct_result()