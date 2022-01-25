"""
股票指数截面波动率指标
"""
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB


class StockCrossSectionVol:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_stock_cross_section_vol'
        self._init_api_params()

    def _init_api_params(self):
        self.url = 'http://fdc-query.intelnal.howbuy.com/query/data/commonapi?dataTrack=xxxxx'
        self.headers = {'Content-Type': 'application/json'}
        self.post_body = {"database": "readonly"}

    def fetch_data_batch(self, sql_script):
        post_body = self.post_body.copy()
        post_body['sql'] = sql_script
        post_body["ifByPage"] = False
        res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
        n = res['pages']
        all_data = []
        for i in range(1, n + 1):
            post_body["ifByPage"] = True
            post_body['pageNum'] = i
            res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
            all_data.append(pd.DataFrame(res['data']))
        all_data = pd.concat(all_data)

        return all_data

    def get_cross_section_vol(self):
        pre_dt = datetime.strptime(self.start_date, '%Y-%m-%d') - timedelta(days=60)
        pre_date = pre_dt.strftime('%Y%m%d')
        end_date = self.end_date.replace('-', '')

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            pre_date, end_date)
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
        actual_trading_day_list = [x for x in trading_day_list if x >= self.start_date.replace('-', '')]
        month_end_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()
        # 指数成分
        period_bm_cons = []
        index_list = ['000300', '000905', '000852']
        for date in month_end_list:
            bm_cons = []
            for benchmark_id in index_list:
                sql_script = "SELECT a.EndDate, a.Weight, c.SecuCode " \
                             "FROM hsjy_gg.LC_IndexComponentsWeight a, hsjy_gg.SecuMain b, hsjy_gg.SecuMain c " \
                             "WHERE a.indexCode = b.innerCode and b.SecuCode = '{}' and " \
                             "to_char(a.EndDate, 'yyyymmdd') = '{}' and b.SecuCategory = 4 " \
                             "and a.InnerCode = c.InnerCode".format(benchmark_id, date)
                post_body = self.post_body
                post_body['sql'] = sql_script
                res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
                if pd.DataFrame(res['data']).empty:
                    weight_df = pd.DataFrame(columns=['SECUCODE', 'trade_date', 'benchmark_id'])
                else:
                    weight_df = pd.DataFrame(res['data'])[['SECUCODE']]
                    weight_df['trade_date'] = date
                    weight_df['benchmark_id'] = benchmark_id
                bm_cons.append(weight_df)
            bm_cons = pd.concat(bm_cons)
            period_bm_cons.append(bm_cons)
        period_bm_cons = pd.concat(period_bm_cons)
        period_bm_cons['benchmark_id'] = period_bm_cons['benchmark_id'].replace({"000300": 1, "000905": 2, "000852": 3})
        pivot_df = pd.pivot_table(
            period_bm_cons, index='trade_date', columns='SECUCODE', values='benchmark_id').fillna(4.).sort_index()
        bm_df = pivot_df.reindex(trading_day_list).fillna(method='ffill').reindex(actual_trading_day_list)
        # 行情
        sql_script = "SELECT SYMBOL, TDATE, PCHG, VOTURNOVER FROM finchina.CHDQUOTE WHERE" \
                     " TDATE >= {} and TDATE <= {}".format(actual_trading_day_list[0], actual_trading_day_list[-1])
        mkt_info = self.fetch_data_batch(sql_script)
        mkt_info = mkt_info[(mkt_info['VOTURNOVER'] > 0) & (mkt_info['PCHG'].abs() <= 20)]
        mkt_info['TDATE'] = mkt_info['TDATE'].map(str)
        res = []
        for date in actual_trading_day_list:
            tdf = mkt_info[mkt_info['TDATE'] == date].set_index('SYMBOL')['PCHG'] / 100.
            tdf = tdf.to_frame('ret').merge(
                bm_df.loc[date].to_frame('sign'), left_index=True, right_index=True, how='left').fillna(4.)
            cs_vol = tdf.groupby('sign')['ret'].std().to_frame(date).T
            res.append(cs_vol)

        res = pd.concat(res).rename(columns={1.0: "HS300", 2.0: "ZZ500", 3.0: "ZZ1000", 4.0: "OTHER"})
        res.index.name = 'trade_date'
        res.reset_index(inplace=True)

        return res

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_cross_section_vol()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_stock_cross_section_vol(
                id int auto_increment primary key,
                trade_date date not null unique,
                HS300 decimal(5, 4),
                ZZ500 decimal(5, 4),
                ZZ1000 decimal(5, 4),
                OTHER decimal(5, 4)) 
            """
            create_table(self.table_name, sql_script)
            data = self.get_cross_section_vol()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    StockCrossSectionVol('2021-09-01', '2021-10-28', is_increment=1).get_construct_result()