"""
股票市场风格因子离散度
"""
import os
import pandas as pd
import hbshare as hbs
from datetime import datetime, timedelta
from hbshare.quant.Kevin.rm_associated.config import style_names, industry_names
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB

path = r'D:\kevin\risk_model_jy\RiskModel\data'


class StyleFactorSpread:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_stock_style_spread'
        self._load_calendar()

    def _load_calendar(self):
        pre_dt = datetime.strptime(self.start_date, '%Y-%m-%d') - timedelta(days=60)
        pre_date = pre_dt.strftime('%Y%m%d')
        end_date = self.end_date.replace('-', '')
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            pre_date, end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        self.calendar_df = df

    @staticmethod
    def cal_spread(series):
        bottom = series[series <= series.quantile(0.2)].median()
        top = series[series >= series.quantile(0.8)].median()
        spread = top - bottom

        return spread

    def get_factor_spread(self):
        trading_day_list = self.calendar_df[self.calendar_df['isMonthEnd'] == 1]['calendarDate'].tolist()
        init_spread_list = []
        for date in trading_day_list:
            # 本地的风格因子数据
            data_path = os.path.join(path, r'zzqz_sw\style_factor')
            style_factor = pd.read_csv(
                os.path.join(data_path, '{0}.csv'.format(date)), dtype={"ticker": str}).set_index(
                'ticker')
            industry = pd.melt(style_factor[industry_names.values()].reset_index(),
                               id_vars=['ticker'], var_name='industry', value_name='sign')
            industry = industry[industry['sign'] == 1]
            merged_df = style_factor[style_names].merge(
                industry.set_index('ticker')['industry'], left_index=True, right_index=True).reset_index(drop=True)
            t_spread = []
            for name in style_names:
                t_spread.append(merged_df.groupby('industry')[name].apply(lambda df: self.cal_spread(df)).mean())
            spread = pd.Series(index=style_names, data=t_spread).to_frame(date)
            init_spread_list.append(spread)

        spread_df = pd.concat(init_spread_list, axis=1).T.sort_index()
        spread_df.index.name = 'trade_date'
        spread_df.reset_index(inplace=True)

        return spread_df

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_factor_spread()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_stock_style_spread(
                id int auto_increment primary key,
                trade_date date not null unique,
                size decimal(4, 3),
                beta decimal(4, 3),
                momentum decimal(4, 3),
                earnyield decimal(4, 3),
                resvol decimal(4, 3),
                growth decimal(4, 3),
                btop decimal(4, 3),
                leverage decimal(4, 3),
                liquidity decimal(4, 3),
                sizenl decimal(4, 3))
            """
            create_table(self.table_name, sql_script)
            data = self.get_factor_spread()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    StyleFactorSpread('2010-01-01', '2021-05-17', is_increment=0).get_construct_result()