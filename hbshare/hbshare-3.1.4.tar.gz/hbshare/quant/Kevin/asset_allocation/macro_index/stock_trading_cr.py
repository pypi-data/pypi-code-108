"""
股票市场集中度指标
"""
import pandas as pd
import requests
import json
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB


class TradingCRNCalculator:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_stock_trading_cr'
        self._init_api_params()

    def _init_api_params(self):
        self.url = 'http://fdc-query.intelnal.howbuy.com/query/data/commonapi?dataTrack=xxxxx'
        self.headers = {'Content-Type': 'application/json'}
        self.post_body = {"database": "readonly", "sql": None}

    def get_stock_trading_cr(self):
        # calendar
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            self.start_date.replace('-', ''), self.end_date.replace('-', ''))
        post_body = self.post_body
        post_body['sql'] = sql_script
        res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)
        trading_day_list = df[df['isOpen'] == 1]['calendarDate'].tolist()
        # calculate
        cr5_list, cr10_list, avg_mkt_list = [], [], []
        from tqdm import tqdm
        for date in tqdm(trading_day_list):
            sql_script = "SELECT SYMBOL, TDATE, VATURNOVER, TCAP FROM finchina.CHDQUOTE WHERE TDATE = {}".format(date)
            post_body = self.post_body
            post_body['sql'] = sql_script
            res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
            df = pd.DataFrame(res['data'])
            df = df[df['SYMBOL'].str[0].isin(['0', '3', '6'])]
            df.rename(columns={"SYMBOL": "ticker", "TDATE": "tradeDate", "TCAP": "marketValue",
                               "VATURNOVER": "turnoverValue"}, inplace=True)
            # 剔除停牌、没有成交额的数据
            df = df[df['turnoverValue'] > 0.]
            quantile_5, quantile_10 = df['turnoverValue'].quantile(0.95), df['turnoverValue'].quantile(0.90)
            cr5 = df[df['turnoverValue'] >= quantile_5]['turnoverValue'].sum() / df['turnoverValue'].sum()
            cr10 = df[df['turnoverValue'] >= quantile_10]['turnoverValue'].sum() / df['turnoverValue'].sum()
            cr5_list.append(cr5)
            cr10_list.append(cr10)

            avg_mkt = (df['turnoverValue'] * df['marketValue']).sum() / df['turnoverValue'].sum() / 1e+8
            avg_mkt_list.append(avg_mkt)

        results = pd.DataFrame(
            {"trade_date": trading_day_list, "cr5": cr5_list, "cr10": cr10_list, "avg_mkt": avg_mkt_list})
        # 上证综指走势
        sql_script = "SELECT JYRQ, SPJG FROM funddb.ZSJY WHERE ZQDM = '{}' and JYRQ >= {} and JYRQ <= {}".format(
            '000001', trading_day_list[0], trading_day_list[-1])
        post_body = self.post_body
        post_body['sql'] = sql_script
        res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
        df = pd.DataFrame(res['data']).rename(columns={"JYRQ": "trade_date", "SPJG": "close"})[['trade_date', 'close']]

        df = pd.merge(results, df, on='trade_date')

        return df

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_stock_trading_cr()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_stock_trading_cr(
                id int auto_increment primary key,
                trade_date date not null unique,
                cr5 decimal(5, 4),
                cr10 decimal(5, 4),
                avg_mkt decimal(7, 2),
                close decimal(7, 2)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_stock_trading_cr()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    TradingCRNCalculator('2007-01-04', '2021-04-23', is_increment=0).get_construct_result()