"""
股票市场风格因子动量
"""
import os
import pandas as pd
import hbshare as hbs
from datetime import datetime, timedelta
from hbshare.quant.Kevin.rm_associated.config import style_names
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB

path = r'D:\kevin\risk_model_jy\RiskModel\data'


class StyleFactorMomentum:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name = 'mac_stock_style_momentum'
        self._load_calendar()

    def _load_calendar(self):
        pre_dt = datetime.strptime(self.start_date, '%Y-%m-%d') - timedelta(days=400)
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

    def get_factor_momentum(self):
        month_end_list = self.calendar_df[self.calendar_df['isMonthEnd'] == 1]['calendarDate'].tolist()
        trading_day_list = self.calendar_df[self.calendar_df['isOpen'] == 1]['calendarDate'].tolist()
        rank_ic_list = []
        for i in range(1, len(month_end_list)):
            m_end = month_end_list[i]
            pre_end = month_end_list[i - 1]
            period_date = [x for x in trading_day_list if pre_end < x <= m_end]
            # 本地取风格因子数据
            data_path = os.path.join(path, r'zzqz_sw\style_factor')
            style_factor = pd.read_csv(
                os.path.join(data_path, '{0}.csv'.format(pre_end)), dtype={"ticker": str}).set_index(
                'ticker')[style_names]
            # 本地行情数据
            data_path = os.path.join(path, r'common_data\chg_pct')
            period_info = []
            for date in period_date:
                chg_pct = pd.read_csv(
                    os.path.join(data_path, '{}.csv'.format(date)), dtype={"tradeDate": str, "ticker": str})
                period_info.append(chg_pct)

            period_info = pd.concat(period_info)
            pivot_df = pd.pivot_table(
                period_info, index='tradeDate', columns='ticker', values='dailyReturnReinv').fillna(0.).sort_index()
            period_ret = (1 + pivot_df).prod() - 1

            rank_ic = style_factor.apply(lambda x: x.corr(period_ret, method='spearman'), axis=0).to_frame(m_end).T
            rank_ic_list.append(rank_ic)

        ic_df = pd.concat(rank_ic_list)
        res = ic_df.rolling(12).mean().dropna().round(3)
        res.index.name = 'trade_date'
        res.reset_index(inplace=True)

        return res

    def get_construct_result(self):
        if self.is_increment == 1:
            data = self.get_factor_momentum()
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name, ','.join(data['trade_date'].tolist()))
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table mac_stock_style_momentum(
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
            data = self.get_factor_momentum()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    # StyleFactorMomentum('2021-04-17', '2021-05-17', is_increment=1).get_construct_result()
    StyleFactorMomentum('2010-01-01', '2021-05-17', is_increment=0).get_construct_result()