"""
股票指数时序波动率指标
"""
import pandas as pd
from datetime import datetime, timedelta
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class StockTimeSeriesVol:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_stock_time_series_vol'

    def get_time_series_vol(self):
        """
        股票市场指数行情数据：包含沪深300、中证500、中证1000、万得全A
        """
        index_list = ['000300.SH', '000905.SH', '000852.SH', '881001.WI']
        pre_dt = datetime.strptime(self.start_date, '%Y-%m-%d') - timedelta(days=50)
        pre_date = pre_dt.strftime('%Y-%m-%d')
        res = w.wsd(','.join(index_list), 'close', pre_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch pe_ttm data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        index_return = data.set_index('trade_date').pct_change().dropna()
        # 5日
        tmp = index_return.rolling(5).std()
        vol_5 = tmp[tmp.index >= self.start_date.replace('-', '')]
        vol_5.rename(columns={"000300.SH": "HS300_5d", "000905.SH": "ZZ500_5d",
                              "000852.SH": "ZZ1000_5d", "881001.WI": "WindA_5d"}, inplace=True)
        # 20日
        tmp = index_return.rolling(20).std()
        vol_20 = tmp[tmp.index >= self.start_date.replace('-', '')]
        vol_20.rename(columns={"000300.SH": "HS300_20d", "000905.SH": "ZZ500_20d",
                               "000852.SH": "ZZ1000_20d", "881001.WI": "WindA_20d"}, inplace=True)
        df = pd.merge(vol_5, vol_20, left_index=True, right_index=True).reset_index()

        return df

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_time_series_vol()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_stock_time_series_vol(
                id int auto_increment primary key,
                trade_date date not null unique,
                HS300_5d decimal(5, 4),
                ZZ500_5d decimal(5, 4),
                ZZ1000_5d decimal(5, 4),
                WindA_5d decimal(5, 4),
                HS300_20d decimal(5, 4),
                ZZ500_20d decimal(5, 4),
                ZZ1000_20d decimal(5, 4),
                WindA_20d decimal(5, 4)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_time_series_vol()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    StockTimeSeriesVol('2021-04-23', '2021-04-23', is_increment=1).get_construct_result()