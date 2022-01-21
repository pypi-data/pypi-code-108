import pandas as pd
import numpy as np
import datetime
import requests
import json
import hbshare as hbs
from hbshare.fe.common.util.config import style_name, industry_name
from sqlalchemy import create_engine

sql_params = {
    "ip": "192.168.223.152",
    "user": "readonly",
    "pass": "c24mg2e6",
    "port": "3306",
    "database": "daily_data"
}
engine_params = "mysql+pymysql://{}:{}@{}:{}/{}".format(sql_params['user'], sql_params['pass'],
                                                        sql_params['ip'],
                                                        sql_params['port'], sql_params['database'])


def get_trading_day_list(start_date, end_date, frequency='day'):
    sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
        start_date, end_date)
    res = hbs.db_data_query('readonly', sql_script, page_size=5000)
    df = pd.DataFrame(res['data']).rename(
        columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                 "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
    df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
    df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
    df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

    calendar_df = df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd']]

    if frequency == "day":
        trading_day_list = calendar_df[calendar_df['isOpen'] == 1]['calendarDate'].tolist()
    elif frequency == "week":
        trading_day_list = calendar_df[calendar_df['isWeekEnd'] == 1]['calendarDate'].tolist()
    elif frequency == 'month':
        trading_day_list = calendar_df[calendar_df['isMonthEnd'] == 1]['calendarDate'].tolist()
    else:
        trading_day_list = calendar_df['calendarDate'].tolist()

    return trading_day_list


class NavAttributionLoader:
    def __init__(self, fund_id, fund_type, start_date, end_date, factor_type, benchmark_id):
        self.fund_id = fund_id
        self.fund_type = fund_type
        self.start_date = start_date
        self.end_date = end_date
        self.factor_type = factor_type
        self.benchmark_id = benchmark_id
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

    @staticmethod
    def fetch_data_batch_hbs(user_name, sql_script):
        total_res = hbs.db_data_query(user_name, sql_script, is_pagination=False)
        n = total_res['pages']
        all_data = []
        for i in range(1, n + 1):
            res = hbs.db_data_query(
                user_name, sql_script, page_num=i, is_pagination=True, page_size=total_res['pageSize'])
            all_data.append(pd.DataFrame(res['data']))
        all_data = pd.concat(all_data)

        return all_data

    def _load_calendar(self):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            self.start_date, self.end_date)
        post_body = self.post_body
        post_body['sql'] = sql_script
        res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)
        df['month'] = df['calendarDate'].apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d').month)
        df['isQuarterEnd'] = np.where((df['isMonthEnd'] == 1) & (df['month'].isin([3, 6, 9, 12])), 1, 0)
        df['isQuarterEnd'] = df['isQuarterEnd'].astype(int)

        return df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd', 'isQuarterEnd']]

    def _load_fund_data(self):
        if self.fund_type == 'mutual':
            sql_script = "SELECT a.jjdm fund_id, b.jzrq tradeDate, b.hbcl accumulate_return from " \
                         "funddb.jjxx1 a, funddb.jjhb b where a.cpfl = '2' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3', 'c') " \
                         "and a.m_opt_type <> '03' and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                         "order by b.jzrq".format(self.fund_id, self.start_date, self.end_date)
            post_body = self.post_body
            post_body['sql'] = sql_script
            res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
            data = pd.DataFrame(res['data'])
            data['ADJ_NAV'] = 0.01 * data['ACCUMULATE_RETURN'] + 1
        else:
            sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                         "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3') " \
                         "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                         "order by b.jzrq".format(self.fund_id, self.start_date, self.end_date)
            res = hbs.db_data_query("highuser", sql_script, page_size=5000)
            data = pd.DataFrame(res['data'])

        data.rename(columns={"FUND_ID": "fund_id", "TRADEDATE": "tradeDate", "ADJ_NAV": "adj_nav"}, inplace=True)

        return data.set_index('tradeDate')['adj_nav']

    def _load_bond_index(self):
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE " \
                     "ZQDM = 'H11001' and JYRQ >= {} and JYRQ <= {}".format(self.start_date, self.end_date)
        post_body = self.post_body
        post_body['sql'] = sql_script
        res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
        data = pd.DataFrame(res['data'])
        data.rename(columns={"TCLOSE": "中证全债"}, inplace=True)

        return data.set_index('TRADEDATE')[['中证全债']]

    def _load_factor_data(self):
        factor_type = self.factor_type
        bond_index = self._load_bond_index()
        if factor_type == "style_allo":
            # index_names = ['大盘价值', '大盘成长', '中盘价值', '中盘成长', '小盘价值', '小盘成长']
            index_codes = ['399373', '399372', '399375', '399374', '399377', '399376']
            sql_script = "SELECT jyrq as TRADEDATE, zqmc as INDEXNAME, spjg as TCLOSE from " \
                         "st_market.t_st_zs_hqql WHERE " \
                         "ZQDM in ({}) and JYRQ >= {} and " \
                         "JYRQ <= {}".format(','.join("'{0}'".format(x) for x in index_codes),
                                             self.start_date, self.end_date)
            factor_data = self.fetch_data_batch_hbs('alluser', sql_script)
            factor_data = factor_data.rename(
                columns={"INDEXNAME": "factor_name", "TRADEDATE": "trade_date"})
            # factor_data = pd.DataFrame(hbs.db_data_query('alluser', sql_script, page_size=5000)['data']).rename(
            #     columns={"INDEXNAME": "factor_name", "TRADEDATE": "trade_date"})
            factor_data['trade_date'] = factor_data['trade_date'].map(str)
            factor_data = pd.pivot_table(
                factor_data, index='trade_date', columns='factor_name', values='TCLOSE').sort_index()
            factor_data = pd.merge(factor_data, bond_index, left_index=True, right_index=True)
        elif factor_type == "style":
            # sql_script = "SELECT * FROM factor_return where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            #     self.start_date, self.end_date)
            # engine = create_engine(engine_params)
            # factor_data = pd.read_sql(sql_script, engine)
            # factor_data['trade_date'] = \
            #     factor_data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
            # factor_data = pd.pivot_table(
            #     factor_data, index='trade_date', columns='factor_name', values='factor_ret').sort_index()[style_name]
            # factor_data = (1 + factor_data).cumprod()
            sql_script = "SELECT * FROM st_ashare.r_st_barra_factor_return where " \
                         "TRADE_DATE >= '{}' and TRADE_DATE <= '{}'".format(self.start_date, self.end_date)
            factor_data = self.fetch_data_batch_hbs("alluser", sql_script)
            factor_data = pd.pivot_table(
                factor_data, index='trade_date', columns='factor_name', values='factor_ret').sort_index()[style_name]
            factor_data = (1 + factor_data).cumprod()
        elif factor_type == "sector":
            # sql_script = "SELECT * FROM sector_return where TRADEDATE >= {} and TRADEDATE <= {}".format(
            #     self.start_date, self.end_date)
            # engine = create_engine(engine_params)
            # factor_data = pd.read_sql(sql_script, engine)
            # factor_data['TRADEDATE'] = \
            #     factor_data['TRADEDATE'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
            # factor_data.rename(columns={"TRADEDATE": "trade_date", "BIGFINANCE": "大金融",
            #                             "CONSUMING": "消费", "CYCLE": "周期", "MANUFACTURE": "制造"}, inplace=True)
            # factor_data = factor_data.set_index('trade_date').sort_index()
            # del factor_data['id']
            # factor_data = (1 + factor_data).cumprod()
            # factor_data = pd.merge(factor_data, bond_index, left_index=True, right_index=True)
            sql_script = "SELECT * FROM st_market.r_st_sector_factor where " \
                         "trade_date >= {} and trade_date <= {}".format(self.start_date, self.end_date)
            factor_data = self.fetch_data_batch_hbs('alluser', sql_script)
            factor_data = factor_data[['trade_date', 'bigfinance', 'consuming', 'tmt', 'cycle', 'manufacture']]
            factor_data.rename(columns={"bigfinance": "大金融", "consuming": "消费", "tmt": "TMT",
                                        "cycle": "周期", "manufacture": "制造"}, inplace=True)
            factor_data = factor_data.set_index('trade_date').sort_index()
            factor_data = (1 + factor_data).cumprod()
            factor_data = pd.merge(factor_data, bond_index, left_index=True, right_index=True)
        else:
            factor_data = pd.DataFrame()

        return factor_data

    def _load_benchmark_data(self):
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(self.benchmark_id, self.start_date, self.end_date)
        post_body = self.post_body
        post_body['sql'] = sql_script
        res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
        data = pd.DataFrame(res['data'])
        data.rename(columns={"TCLOSE": "benchmark"}, inplace=True)

        return data.set_index('TRADEDATE')[['benchmark']]

    def load(self):
        calendar_df = self._load_calendar()
        fund_adj_nav = self._load_fund_data()
        factor_data = self._load_factor_data()
        benchmark_series = self._load_benchmark_data()

        data = {"calendar_df": calendar_df,
                "fund_nav_series": fund_adj_nav,
                "factor_data": factor_data,
                "benchmark_series": benchmark_series}

        return data


class CtaNavAttributionLoader:
    def __init__(self, fund_id, start_date, end_date, style_factors):
        self.fund_id = fund_id
        self.start_date = start_date
        self.end_date = end_date
        self.style_factors = style_factors
        self._pre_date_process()

    def _pre_date_process(self):
        start_dt = datetime.datetime.strptime(self.start_date, '%Y%m%d')
        self.pre_date = (start_dt - datetime.timedelta(days=300)).strftime('%Y%m%d')

    def _load_calendar(self):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            self.pre_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        self.calendar_df = df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd']]

        trading_day_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list

    @staticmethod
    def fetch_data_batch(user_name, sql_script):
        total_res = hbs.db_data_query(user_name, sql_script, is_pagination=False)
        n = total_res['pages']
        all_data = []
        for i in range(1, n + 1):
            res = hbs.db_data_query(
                user_name, sql_script, page_num=i, is_pagination=True, page_size=total_res['pageSize'])
            all_data.append(pd.DataFrame(res['data']))
        all_data = pd.concat(all_data)

        return all_data

    def _load_fund_data(self):
        sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                     "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                     "and a.jjzt not in ('3') " \
                     "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                     "order by b.jzrq".format(self.fund_id, self.start_date, self.end_date)
        res = hbs.db_data_query("highuser", sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).rename(
            columns={"FUND_ID": "fund_id", "TRADEDATE": "tradeDate", "ADJ_NAV": "adj_nav"})

        return data.set_index('tradeDate')['adj_nav']

    def _load_factor_data(self):
        sql_script = "SELECT * FROM cta_index where TDATE >= {} and TDATE <= {}".format(
            self.pre_date, self.end_date)
        engine = create_engine(engine_params)
        factor_data = pd.read_sql(sql_script, engine).rename(columns={"TDATE": "TRADEDATE"})
        factor_data['TRADEDATE'] = \
            factor_data['TRADEDATE'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        factor_data = pd.pivot_table(
            factor_data, index='TRADEDATE', columns='FACTOR', values='CLOSE').sort_index()[self.style_factors]

        return factor_data

    def load(self):
        trading_day_list = self._load_calendar()
        fund_adj_nav = self._load_fund_data()
        factor_data = self._load_factor_data()

        data = {
            "trading_day_list": trading_day_list,
            "fund_nav_series": fund_adj_nav,
            "factor_data": factor_data}

        return data


class SectorIndexCalculatorLoader:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def load(self):
        start_dt = datetime.datetime.strptime(self.start_date, '%Y%m%d')
        pre_date = (start_dt - datetime.timedelta(days=30)).strftime('%Y%m%d')

        sql_script = "SELECT * FROM st_market.t_st_zs_hyzsdmdyb where fljb = {} and hyhfbz = 3 and sfyx = 1".format('1')
        res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).rename(columns={"zsdm": "SYMBOL", "flmc": "INDEXSNAME"})
        map_dict = data.set_index('SYMBOL')['INDEXSNAME'].to_dict()
        industry_index = []
        for key, value in map_dict.items():
            sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE, " \
                         "LTSZ as NEG_MKV FROM funddb.ZSJY WHERE " \
                         "ZQDM = '{}' and JYRQ >= {} and " \
                         "JYRQ <= {}".format(key, pre_date, self.end_date)
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            df = pd.DataFrame(res['data'])
            df['INDEXNAME'] = value
            industry_index.append(df)
        industry_index = pd.concat(industry_index)

        return industry_index


class EquityBrinsonAttributionLoader:
    def __init__(self, fund_id, benchmark_id, start_date, end_date):
        self.fund_id = fund_id
        self.benchmark_id = benchmark_id
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def fetch_data_batch(user_name, sql_script):
        total_res = hbs.db_data_query(user_name, sql_script, is_pagination=False)
        n = total_res['pages']
        all_data = []
        for i in range(1, n + 1):
            res = hbs.db_data_query(
                user_name, sql_script, page_num=i, is_pagination=True, page_size=total_res['pageSize'])
            all_data.append(pd.DataFrame(res['data']))
        all_data = pd.concat(all_data)

        return all_data

    def _load_calendar(self):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        self.calendar_df = df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd']]

        df = df[df['isMonthEnd'] == 1].copy()
        trading_day_list = [x for x in sorted(df['calendarDate'].unique()) if x[4:6] in ['06', '12']]

        return trading_day_list

    def _load_portfolio_weight(self):
        sql_script = "SELECT JJDM, JSRQ, ZQDM, ZJBL FROM funddb.GPZH WHERE JJDM = '{}' and GGRQ >= {} " \
                     "and GGRQ <= {}".format(self.fund_id, self.start_date, self.end_date)
        data = self.fetch_data_batch('readonly', sql_script)
        # res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        if data.empty:
            portfolio_weight_series_dict = None
        else:
            data = data.rename(columns={"JSRQ": "endDate", "ZQDM": "ticker", "ZJBL": "weight"})
            # date_list = [x for x in sorted(data['endDate'].unique()) if x[4:6] not in ['03', '09']]
            date_list = [x for x in sorted(data['endDate'].unique()) if x[4:] in ['0630', '1231']]
            trading_day_list = [
                self.calendar_df[(self.calendar_df['calendarDate'] <= x) & (self.calendar_df['isOpen'] == 1)]
                ['calendarDate'].unique()[-1] for x in date_list]
            map_dict = dict(zip(date_list, trading_day_list))
            data['endDate'] = data['endDate'].replace(map_dict)

            portfolio_weight_series_dict = {}
            for date in trading_day_list:
                portfolio_weight_series_dict[date] = \
                    (data[data['endDate'] == date].set_index('ticker')['weight'] / 100.).dropna()

        return portfolio_weight_series_dict

    def _load_benchmark_weight(self, portfolio_weight_series_dict, equity_ratio_series):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(
            self.benchmark_id)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[self.benchmark_id, 'INNERCODE']
        trading_day_list = sorted(portfolio_weight_series_dict.keys())
        benchmark_weight_series_dict = dict()
        for date in trading_day_list:
            sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                         "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                         "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
            data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
            weight_df = data.rename(
                columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})
            benchmark_weight_series_dict[date] = weight_df.set_index(
                'consTickerSymbol')['weight'] / 100. * equity_ratio_series.loc[date]

        return benchmark_weight_series_dict

    @staticmethod
    def _load_security_period_return(portfolio_weight_series_dict, benchmark_weight_series_dict, trading_day_list):
        portfolio_ticker_list = list(pd.DataFrame.from_dict(portfolio_weight_series_dict).index)
        benchmark_ticker_list = list(pd.DataFrame.from_dict(benchmark_weight_series_dict).index)
        ticker_list = sorted(list(set(portfolio_ticker_list).union(set(benchmark_ticker_list))))

        all_data = []
        for trading_day in trading_day_list:
            sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode " \
                         "and rownum=1) SecuCode, b.TradingDay, b.BackwardPrice FROM hsjy_gg.QT_PerformanceData b " \
                         "where b.TradingDay = to_date('{}', 'yyyymmdd')".format(trading_day)
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            data_main = pd.DataFrame(res['data'])

            sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode " \
                         "and rownum=1) SecuCode, b.TradingDay, b.BackwardPrice FROM " \
                         "hsjy_gg.LC_STIBPerformanceData b " \
                         "where b.TradingDay = to_date('{}', 'yyyymmdd')".format(trading_day)
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            data_stib = pd.DataFrame(res['data'])

            all_data.append(pd.concat([data_main, data_stib]))

        data = pd.concat(all_data)
        data.rename(
            columns={"SECUCODE": "ticker", "BACKWARDPRICE": "adj_price", "TRADINGDAY": "trade_date"}, inplace=True)
        data = data[data['ticker'].isin(ticker_list)]
        data['trade_date'] = data['trade_date'].apply(
            lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d'))
        pivot_df = pd.pivot_table(data, index='trade_date', columns='ticker', values='adj_price').sort_index()
        pct_chg = pivot_df.pct_change().dropna(how='all')
        # process
        security_return_series_dict = dict()
        for date in pct_chg.index.tolist():
            security_return_series_dict[date] = pct_chg.loc[date].dropna()

        return security_return_series_dict

    def _load_security_return(self, portfolio_weight_series_dict, benchmark_weight_series_dict):
        df = self.calendar_df[self.calendar_df['isMonthEnd'] == 1].copy()
        trading_day_list = [x for x in sorted(df['calendarDate'].unique()) if x[4:6] in ['06', '12']]
        start_date, end_date = trading_day_list[0], trading_day_list[-1]

        portfolio_ticker_list = list(pd.DataFrame.from_dict(portfolio_weight_series_dict).index)
        benchmark_ticker_list = list(pd.DataFrame.from_dict(benchmark_weight_series_dict).index)
        ticker_list = sorted(list(set(portfolio_ticker_list).union(set(benchmark_ticker_list))))

        n = 100
        sec_return = []
        group_ticker_list = [ticker_list[i: i + n] for i in range(0, len(ticker_list), n)]
        for group_ticker in group_ticker_list:
            sql_script = "SELECT SYMBOL, TDATE, PCHG FROM finchina.CHDQUOTE WHERE" \
                         " SYMBOL in ({}) and TDATE >= {} and TDATE <= {}".format(
                          ','.join("'{0}'".format(x) for x in group_ticker), start_date, end_date)
            data = self.fetch_data_batch('readonly', sql_script)
            sec_return.append(data)
        sec_return = pd.concat(sec_return)
        sec_return['TDATE'] = sec_return['TDATE'].astype(str)
        # process
        security_return_series_dict = dict()
        for i in range(len(trading_day_list) - 1):
            trading_day, next_trading_day = trading_day_list[i], trading_day_list[i + 1]
            period_return = sec_return[(sec_return['TDATE'] > trading_day) & (sec_return['TDATE'] <= next_trading_day)]
            period_return = pd.pivot_table(period_return, index='TDATE', columns='SYMBOL', values='PCHG').sort_index()
            period_return = period_return.fillna(0.) / 100.
            security_return_series_dict[next_trading_day] = (1 + period_return).prod() - 1

        return security_return_series_dict

    @staticmethod
    def _load_security_sector(portfolio_weight_series_dict, benchmark_weight_series_dict):
        trading_day_list = sorted(portfolio_weight_series_dict.keys())

        portfolio_ticker_list = list(pd.DataFrame.from_dict(portfolio_weight_series_dict).index)
        benchmark_ticker_list = list(pd.DataFrame.from_dict(benchmark_weight_series_dict).index)
        ticker_list = sorted(list(set(portfolio_ticker_list).union(set(benchmark_ticker_list))))
        n = 300
        group_ticker_list = [ticker_list[i: i + n] for i in range(0, len(ticker_list), n)]
        cols_list = ['ticker'] + [x.lower() for x in industry_name['sw'].values()]

        security_sector_series_dict = dict()
        for date in trading_day_list:
            all_data = []
            for group_ticker in group_ticker_list:
                sql_script = "SELECT {} FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}' and " \
                             "ticker in ({})".format(','.join(cols_list), date,
                                                     ','.join("'{0}'".format(x) for x in group_ticker))
                res = hbs.db_data_query('alluser', sql_script, page_size=5000)
                data = pd.DataFrame(res['data'])
                all_data.append(data)

            factor_exposure = pd.concat(all_data).set_index('ticker')
            reverse_ind = dict([(value.lower(), key) for (key, value) in industry_name['sw'].items()])
            ind_exposure = factor_exposure[reverse_ind.keys()].rename(columns=reverse_ind)
            ind_exposure = ind_exposure.reset_index().melt(
                id_vars=['ticker'], value_vars=list(reverse_ind.values()), var_name='industryName1', value_name='sign')
            ind_exposure = ind_exposure[ind_exposure['sign'] == '1']
            security_sector_series_dict[date] = ind_exposure.set_index(
                'ticker').reindex(ticker_list)['industryName1'].dropna()

        return security_sector_series_dict

    def _load_nav_based_return(self, trading_day_list):
        nav_based_return_dict = dict()
        for i in range(len(trading_day_list) - 1):
            trading_day, next_trading_day = trading_day_list[i], trading_day_list[i + 1]
            sql_script = "SELECT a.jjdm fund_id, b.jzrq tradeDate, b.hbcl accumulate_return from " \
                         "funddb.jjxx1 a, funddb.jjhb b where a.cpfl = '2' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3', 'c') " \
                         "and a.m_opt_type <> '03' and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                         "order by b.jzrq".format(self.fund_id, trading_day, next_trading_day)
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            portfolio_nav_df = pd.DataFrame(res['data'])
            if portfolio_nav_df.empty:
                continue
            portfolio_nav_df['ADJ_NAV'] = 0.01 * portfolio_nav_df['ACCUMULATE_RETURN'] + 1
            portfolio_nav_df.rename(columns={"ADJ_NAV": "portfolio"}, inplace=True)

            sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY " \
                         "WHERE ZQDM = '{}' and JYRQ >= {} and " \
                         "JYRQ <= {}".format(self.benchmark_id, trading_day, next_trading_day)
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            equity_benchmark_nav_df = pd.DataFrame(res['data'])
            equity_benchmark_nav_df.rename(columns={"TCLOSE": "equity_bm"}, inplace=True)

            sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY " \
                         "WHERE ZQDM = '{}' and JYRQ >= {} and " \
                         "JYRQ <= {}".format('H11001', trading_day, next_trading_day)
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            bond_benchmark_nav_df = pd.DataFrame(res['data'])
            bond_benchmark_nav_df.rename(columns={"TCLOSE": "bond_bm"}, inplace=True)

            nav_df = portfolio_nav_df[['TRADEDATE', 'portfolio']].merge(
                equity_benchmark_nav_df[['TRADEDATE', 'equity_bm']], on='TRADEDATE').merge(
                bond_benchmark_nav_df[['TRADEDATE', 'bond_bm']], on='TRADEDATE')

            nav_based_return_dict[next_trading_day] = \
                (nav_df.set_index('TRADEDATE').pct_change().dropna() + 1).prod() - 1

        return nav_based_return_dict

    def _load_portfolio_equity_ratio(self, N=12):
        sql_script = "SELECT JJDM, JSRQ, GPBL FROM funddb.ZCPZ WHERE JJDM = '{}'".format(self.fund_id)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).rename(
            columns={"JSRQ": "endDate", "GPBL": "equity_ratio"})[['JJDM', 'endDate', 'equity_ratio']].dropna()
        data['equity_ratio'] /= 100.
        data['avg_ratio'] = data['equity_ratio'].rolling(N, min_periods=1).mean()
        data = data[(data['endDate'] >= self.start_date) & (data['endDate'] <= self.end_date)]

        date_list = [x for x in sorted(data['endDate'].unique()) if x[4:6] not in ['03', '09']]
        trading_day_list = [
            self.calendar_df[(self.calendar_df['calendarDate'] <= x) & (self.calendar_df['isOpen'] == 1)]
            ['calendarDate'].unique()[-1] for x in date_list]
        map_dict = dict(zip(date_list, trading_day_list))
        data['endDate'] = data['endDate'].replace(map_dict)
        data = data[data['endDate'].isin(trading_day_list)]

        return data.set_index('endDate')['avg_ratio']

    def load(self):
        trading_day_list = self._load_calendar()
        if len(trading_day_list) < 2:
            return
        portfolio_weight_series_dict = self._load_portfolio_weight()
        if not portfolio_weight_series_dict:
            return
        # tdl adjust
        weight_start_date = sorted(portfolio_weight_series_dict.keys())[0]
        trading_day_list = [x for x in trading_day_list if x >= weight_start_date]

        equity_ratio_series = self._load_portfolio_equity_ratio()
        benchmark_weight_series_dict = self._load_benchmark_weight(portfolio_weight_series_dict, equity_ratio_series)
        security_sector_series_dict = self._load_security_sector(
            portfolio_weight_series_dict, benchmark_weight_series_dict)

        security_return_series_dict = self._load_security_period_return(
            portfolio_weight_series_dict, benchmark_weight_series_dict, trading_day_list)
        nav_based_return_dict = self._load_nav_based_return(trading_day_list)

        data_param = {
            "trading_day_list": trading_day_list,
            "portfolio_weight_series_dict": portfolio_weight_series_dict,
            "benchmark_weight_series_dict": benchmark_weight_series_dict,
            "security_sector_series_dict": security_sector_series_dict,
            "security_return_series_dict": security_return_series_dict,
            "nav_based_return_dict": nav_based_return_dict}

        return data_param


class HoldingAttributionLoader:
    """
    先前的持仓Loader
    """
    def __init__(self, fund_id, benchmark_id, start_date, end_date, mode='style'):
        self.fund_id = fund_id
        self.benchmark_id = benchmark_id
        self.start_date = start_date
        self.end_date = end_date
        self.mode = mode

    @staticmethod
    def fetch_data_batch(user_name, sql_script):
        total_res = hbs.db_data_query(user_name, sql_script, is_pagination=False)
        n = total_res['pages']
        all_data = []
        for i in range(1, n + 1):
            res = hbs.db_data_query(
                user_name, sql_script, page_num=i, is_pagination=True, page_size=total_res['pageSize'])
            all_data.append(pd.DataFrame(res['data']))
        all_data = pd.concat(all_data)

        return all_data

    def _load_calendar(self):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        self.calendar_df = df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd']]

    def _load_portfolio_weight(self):
        sql_script = "SELECT JJDM, JSRQ, ZQDM, ZJBL FROM funddb.GPZH WHERE JJDM = '{}' and GGRQ >= {} " \
                     "and GGRQ <= {}".format(self.fund_id, self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).rename(
            columns={"JSRQ": "endDate", "ZQDM": "ticker", "ZJBL": "weight"})
        date_list = [x for x in sorted(data['endDate'].unique()) if x[4:6] not in ['03', '09']]
        trading_day_list = [
            self.calendar_df[(self.calendar_df['calendarDate'] <= x) & (self.calendar_df['isOpen'] == 1)]
            ['calendarDate'].unique()[-1] for x in date_list]
        map_dict = dict(zip(date_list, trading_day_list))
        data['endDate'] = data['endDate'].replace(map_dict)

        portfolio_weight_series_dict = {}
        for date in trading_day_list:
            portfolio_weight_series_dict[date] = data[data['endDate'] == date].set_index('ticker')['weight'] / 100.

        return trading_day_list, portfolio_weight_series_dict

    @staticmethod
    def _load_risk_model_data(trading_day_list):
        risk_model_dict = dict()
        risk_model_dict['schema'] = {"industry_field": sorted(pd.Series(industry_name['sw']).values.tolist()),
                                     "style_field": style_name + ['country']}
        factor_order = style_name + risk_model_dict['schema']['industry_field'] + ['country']
        data = dict()
        for date in trading_day_list[:-1]:
            sql_script = "SELECT * FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}'".format(date)
            res = hbs.db_data_query('alluser', sql_script, page_size=5000)
            factor_exposure = pd.DataFrame(res['data']).set_index('ticker')
            exclude = ['credt_etl', 'moddt_etl', 'id', 'trade_date', 'm_opt_type']
            cols = sorted([x for x in factor_exposure.columns if x not in exclude])
            map_dict = {x.lower(): x for x in risk_model_dict['schema']['industry_field']}
            factor_exposure = factor_exposure[cols].rename(columns=map_dict)[factor_order]

            sql_script = "SELECT * FROM st_ashare.r_st_barra_factor_cov where TRADE_DATE = '{}'".format(date)
            res = hbs.db_data_query('alluser', sql_script, page_size=5000)
            factor_covariance = pd.DataFrame(res['data']).set_index('factor_name')
            factor_covariance = factor_covariance[cols].rename(columns=map_dict).reindex(factor_order)[factor_order]

            sql_script = "SELECT * FROM st_ashare.r_st_barra_s_risk where TRADE_DATE = '{}'".format(date)
            res = hbs.db_data_query('alluser', sql_script, page_size=5000)
            srisk = pd.DataFrame(res['data']).set_index('ticker')['s_ret']

            data[date] = {"exposure": factor_exposure, "factor_covariance": factor_covariance, "specific_risk": srisk}

        risk_model_dict['data'] = data

        return risk_model_dict

    def _load_factor_return(self, trading_day_list):
        factor_return_series_dict = dict()
        for i in range(len(trading_day_list) - 1):
            trading_day, next_trading_day = trading_day_list[i], trading_day_list[i + 1]
            sql_script = "SELECT * FROM st_ashare.r_st_barra_factor_return where " \
                         "TRADE_DATE > '{}' and TRADE_DATE <= {}".format(trading_day, next_trading_day)
            data = self.fetch_data_batch('alluser', sql_script)
            factor_return = pd.pivot_table(
                data, index='trade_date', columns='factor_name', values='factor_ret').sort_index()
            factor_return_series_dict[next_trading_day] = (1 + factor_return).prod() - 1

        return factor_return_series_dict

    def _load_benchmark_weight(self, trading_day_list):
        benchmark_weight_series_dict = dict()
        for date in trading_day_list:
            sql_script = "SELECT a.EndDate, a.Weight, c.SecuCode " \
                         "FROM hsjy_gg.LC_IndexComponentsWeight a, hsjy_gg.SecuMain b, hsjy_gg.SecuMain c " \
                         "WHERE a.indexCode = b.innerCode and b.SecuCode = '{}' and " \
                         "to_char(a.EndDate, 'yyyymmdd') = '{}' and b.SecuCategory = 4 " \
                         "and a.InnerCode = c.InnerCode".format(self.benchmark_id, date)
            data = self.fetch_data_batch('readonly', sql_script)
            weight_df = data.rename(
                columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})
            benchmark_weight_series_dict[date] = weight_df.set_index('consTickerSymbol')['weight'] / 100.

        return benchmark_weight_series_dict

    def _load_security_return(self, portfolio_weight_series_dict, benchmark_weight_series_dict):
        trading_day_list = sorted(portfolio_weight_series_dict.keys())
        start_date, end_date = trading_day_list[0], trading_day_list[-1]

        portfolio_ticker_list = list(pd.DataFrame.from_dict(portfolio_weight_series_dict).index)
        benchmark_ticker_list = list(pd.DataFrame.from_dict(benchmark_weight_series_dict).index)
        ticker_list = sorted(list(set(portfolio_ticker_list).union(set(benchmark_ticker_list))))

        n = 100
        sec_return = []
        group_ticker_list = [ticker_list[i: i + n] for i in range(0, len(ticker_list), n)]
        for group_ticker in group_ticker_list:
            sql_script = "SELECT SYMBOL, TDATE, PCHG FROM finchina.CHDQUOTE WHERE" \
                         " SYMBOL in ({}) and TDATE >= {} and TDATE <= {}".format(
                          ','.join("'{0}'".format(x) for x in group_ticker), start_date, end_date)
            data = self.fetch_data_batch('readonly', sql_script)
            sec_return.append(data)
        sec_return = pd.concat(sec_return)
        sec_return['TDATE'] = sec_return['TDATE'].astype(str)
        # process
        security_return_series_dict = dict()
        for i in range(len(trading_day_list) - 1):
            trading_day, next_trading_day = trading_day_list[i], trading_day_list[i + 1]
            period_return = sec_return[(sec_return['TDATE'] > trading_day) & (sec_return['TDATE'] <= next_trading_day)]
            period_return = pd.pivot_table(period_return, index='TDATE', columns='SYMBOL', values='PCHG').sort_index()
            period_return = period_return.fillna(0.) / 100.
            security_return_series_dict[next_trading_day] = (1 + period_return).prod() - 1

        return security_return_series_dict

    @staticmethod
    def _load_security_sector(portfolio_weight_series_dict, benchmark_weight_series_dict):
        trading_day_list = sorted(portfolio_weight_series_dict.keys())

        portfolio_ticker_list = list(pd.DataFrame.from_dict(portfolio_weight_series_dict).index)
        benchmark_ticker_list = list(pd.DataFrame.from_dict(benchmark_weight_series_dict).index)
        ticker_list = sorted(list(set(portfolio_ticker_list).union(set(benchmark_ticker_list))))

        security_sector_series_dict = dict()
        for date in trading_day_list:
            sql_script = "SELECT * FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}'".format(date)
            res = hbs.db_data_query('alluser', sql_script, page_size=5000)
            factor_exposure = pd.DataFrame(res['data']).set_index('ticker')
            reverse_ind = dict([(value.lower(), key) for (key, value) in industry_name['sw'].items()])
            ind_exposure = factor_exposure[reverse_ind.keys()].rename(columns=reverse_ind)
            ind_exposure = ind_exposure.reset_index().melt(
                id_vars=['ticker'], value_vars=list(reverse_ind.values()), var_name='industryName1', value_name='sign')
            ind_exposure = ind_exposure[ind_exposure['sign'] == '1']
            security_sector_series_dict[date] = ind_exposure.set_index(
                'ticker').reindex(ticker_list)['industryName1'].dropna()

        return security_sector_series_dict

    def _load_nav_active_return(self, trading_day_list):
        nav_active_return_dict = dict()
        for i in range(len(trading_day_list) - 1):
            trading_day, next_trading_day = trading_day_list[i], trading_day_list[i + 1]
            sql_script = "SELECT a.jjdm fund_id, b.jzrq tradeDate, b.hbcl accumulate_return from " \
                         "funddb.jjxx1 a, funddb.jjhb b where a.cpfl = '2' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3', 'c') " \
                         "and a.m_opt_type <> '03' and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                         "order by b.jzrq".format(self.fund_id, trading_day, next_trading_day)
            nav_df = self.fetch_data_batch('readonly', sql_script)
            nav_df['ADJ_NAV'] = 0.01 * nav_df['ACCUMULATE_RETURN'] + 1

            sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                         "and JYRQ >= {} and JYRQ <= {}".format(self.benchmark_id, trading_day, next_trading_day)
            benchmark_nav_df = self.fetch_data_batch('readonly', sql_script)

            nav_df = pd.merge(
                nav_df[['TRADEDATE', 'ADJ_NAV']], benchmark_nav_df[['TRADEDATE', 'TCLOSE']], on='TRADEDATE').rename(
                columns={"ADJ_NAV": "portfolio", "TCLOSE": "benchmark"})

            nav_active_return_dict[next_trading_day] = \
                (nav_df.set_index('TRADEDATE').pct_change().dropna() + 1).prod() - 1

        return nav_active_return_dict

    def load(self):
        self._load_calendar()
        trading_day_list, portfolio_weight_series_dict = self._load_portfolio_weight()
        benchmark_weight_series_dict = self._load_benchmark_weight(trading_day_list)
        security_return_series_dict = self._load_security_return(
            portfolio_weight_series_dict, benchmark_weight_series_dict)
        if self.mode == "style":
            factor_return_series_dict = self._load_factor_return(trading_day_list)
            risk_model_dict = self._load_risk_model_data(trading_day_list)
            security_sector_series_dict = None
            nav_active_return_dict = None
        else:
            factor_return_series_dict = None
            risk_model_dict = None
            security_sector_series_dict = self._load_security_sector(
                portfolio_weight_series_dict, benchmark_weight_series_dict)
            nav_active_return_dict = self._load_nav_active_return(trading_day_list)

        data_param = {
            "trading_day_list": trading_day_list,
            "portfolio_weight_series_dict": portfolio_weight_series_dict,
            "risk_model_dict": risk_model_dict,
            "benchmark_weight_series_dict": benchmark_weight_series_dict,
            "security_return_series_dict": security_return_series_dict,
            "factor_return_series_dict": factor_return_series_dict,
            "security_sector_series_dict": security_sector_series_dict,
            "nav_active_return_dict": nav_active_return_dict}

        return data_param


class MorningStarBoxStyleLoader:
    def __init__(self, trade_date, mode):
        self.trade_date = trade_date
        self.mode = mode

    @staticmethod
    def fetch_data_batch(user_name, sql_script):
        total_res = hbs.db_data_query(user_name, sql_script, is_pagination=False)
        n = total_res['pages']
        all_data = []
        for i in range(1, n + 1):
            res = hbs.db_data_query(
                user_name, sql_script, page_num=i, is_pagination=True, page_size=total_res['pageSize'])
            all_data.append(pd.DataFrame(res['data']))
        all_data = pd.concat(all_data)

        return all_data

    def _load_associated_date(self):
        pre_date = str(int(self.trade_date[:4]) - 2) + '0101'
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
           pre_date, self.trade_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)
        df = df[df['isMonthEnd'] == 1]

        if self.mode == "main":  # quarter
            df['pre_end'] = df['calendarDate'].shift(1)
            quotation_date = df.set_index('calendarDate').loc[self.trade_date, 'pre_end']
            report_date = \
                quotation_date[:4] + '0331' if self.trade_date[4:6] in ["04", "07"] else quotation_date[:4] + "0930"
        else:
            df['shift_2'] = df['calendarDate'].shift(2)
            df['shift_4'] = df['calendarDate'].shift(4)
            if self.trade_date[4:6] == "08":
                quotation_date = df.set_index('calendarDate').loc[self.trade_date, 'shift_2']
                report_date = quotation_date[:6] + '30'
            else:
                quotation_date = df.set_index('calendarDate').loc[self.trade_date, 'shift_4']
                report_date = quotation_date[:6] + '31'

        return quotation_date, report_date

    def _load_valuation_data(self, date):
        """
        估值数据
        """
        # 主板
        sql_script = "SELECT TotalMV, NegotiableMV, PE, PB, PCFTTM, DividendRatio, SecuCode FROM " \
                     "(SELECT b.TotalMV, b.NegotiableMV, b.PE, b.PB, b.PCFTTM, b.DividendRatio, a.SecuCode, " \
                     "row_number() over(partition by a.InnerCode order by a.InnerCode) rn FROM " \
                     "hsjy_gg.LC_DIndicesForValuation b join hsjy_gg.SecuMain a on a.InnerCode = b.InnerCode and " \
                     "a.SecuMarket in (83, 90) and a.SecuCategory = 1 WHERE b.TradingDay = to_date('{}', 'yyyymmdd')) " \
                     "WHERE rn = 1".format(date)
        data_main = self.fetch_data_batch('readonly', sql_script)
        data_main.rename(columns={"SECUCODE": "ticker", "TOTALMV": "marketValue",
                                  "NEGOTIABLEMV": "negMarketValue", "PCFTTM": "PCF"}, inplace=True)
        # 科创板
        sql_script = "SELECT TotalMV, NegotiableMV, PETTM, PB, PCFTTM, DividendRatio, SecuCode FROM " \
                     "(SELECT b.TotalMV, b.NegotiableMV, b.PETTM, b.PB, b.PCFTTM, b.DividendRatio, a.SecuCode, " \
                     "row_number() over(partition by a.InnerCode order by a.InnerCode) rn FROM " \
                     "hsjy_gg.LC_STIBDIndiForValue b join hsjy_gg.SecuMain a on a.InnerCode = b.InnerCode and " \
                     "a.SecuMarket in (83, 90) and a.SecuCategory = 1 WHERE b.TradingDay = to_date('{}', 'yyyymmdd')) " \
                     "WHERE rn = 1".format(date)
        res = hbs.db_data_query('readonly', sql_script)
        data_stib = pd.DataFrame(res['data'])
        data_stib.rename(
            columns={"SECUCODE": "ticker", "TOTALMV": "marketValue",
                     "NEGOTIABLEMV": "negMarketValue", "PETTM": "PE", "PCFTTM": "PCF"}, inplace=True)

        data = pd.concat([data_main, data_stib])
        del data['ROW_ID']
        data = data.dropna(subset=['ticker'])

        return data.set_index('ticker')

    def _load_growth_data(self):
        """
        成长数据
        """
        last_fiscal_year = int(self.trade_date[:4])
        last_fiscal_year = last_fiscal_year - 1 if self.trade_date[4:6] == '01' else last_fiscal_year
        fiscal_year_list = [str(x) + '1231' for x in np.arange(last_fiscal_year - 3, last_fiscal_year)]

        sql_script = "SELECT SYMBOL, COMPCODE FROM finchina.TQ_OA_STCODE WHERE SETYPE in (101, 108)"
        s_code = self.fetch_data_batch('readonly', sql_script)
        ticker_list = s_code['COMPCODE'].unique()
        n = 300
        group_ticker_list = [ticker_list[i: i + n] for i in range(0, len(ticker_list), n)]
        # 利润表
        data = []
        for group_ticker in group_ticker_list:
            # sql_script = "SELECT COMPCODE, ENDDATE, PUBLISHDATE, BIZINCO, NETPROFIT FROM " \
            #              "finchina.TQ_FIN_PROINCSTATEMENTNEW WHERE REPORTTYPE in (1, 3) and " \
            #              "ENDDATE in ({}) and PUBLISHDATE <= '{}' and " \
            #              "COMPCODE in ({})".format(','.join(fiscal_year_list), self.trade_date,
            #                                        ','.join("'{0}'".format(x) for x in group_ticker))
            sql_script = "SELECT COMPCODE, ENDDATE, PUBLISHDATE, BIZINCO, NETPROFIT FROM " \
                         "finchina.TQ_FIN_PROINCSTATEMENTNEW WHERE REPORTTYPE in (1, 3) and " \
                         "ENDDATE in ({}) and " \
                         "COMPCODE in ({})".format(','.join(fiscal_year_list),
                                                   ','.join("'{0}'".format(x) for x in group_ticker))
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            data.append(pd.DataFrame(res['data']))

        data = pd.concat(data).sort_values(by=['COMPCODE', 'ENDDATE', 'PUBLISHDATE'])
        data.drop_duplicates(subset=['COMPCODE', 'ENDDATE'], keep='last', inplace=True)
        revenue_data = data[['COMPCODE', 'ENDDATE', 'BIZINCO', 'NETPROFIT']]
        # 资产负债表
        data = []
        for group_ticker in group_ticker_list:
            # sql_script = "SELECT COMPCODE, ENDDATE, PUBLISHDATE, TOTASSET FROM " \
            #              "finchina.TQ_FIN_PROBALSHEETNEW WHERE REPORTTYPE in (1, 3) and " \
            #              "ENDDATE in ({}) and PUBLISHDATE <= '{}' and " \
            #              "COMPCODE in ({})".format(','.join(fiscal_year_list), self.trade_date,
            #                                        ','.join("'{0}'".format(x) for x in group_ticker))
            sql_script = "SELECT COMPCODE, ENDDATE, PUBLISHDATE, TOTASSET FROM " \
                         "finchina.TQ_FIN_PROBALSHEETNEW WHERE REPORTTYPE in (1, 3) and " \
                         "ENDDATE in ({}) and " \
                         "COMPCODE in ({})".format(','.join(fiscal_year_list),
                                                   ','.join("'{0}'".format(x) for x in group_ticker))
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            data.append(pd.DataFrame(res['data']))
        data = pd.concat(data).sort_values(by=['COMPCODE', 'ENDDATE', 'PUBLISHDATE'])
        data.drop_duplicates(subset=['COMPCODE', 'ENDDATE'], keep='last', inplace=True)
        asset_data = data[['COMPCODE', 'ENDDATE', 'TOTASSET']]

        fin_data = pd.merge(revenue_data, asset_data, on=['COMPCODE', 'ENDDATE']).dropna()
        fin_data = pd.merge(fin_data, s_code[['SYMBOL', 'COMPCODE']], on='COMPCODE').rename(
            columns={"SYMBOL": "ticker", "ENDDATE": "endDate", "BIZINCO": "revenue",
                     "NETPROFIT": "net_profit", "TOTASSET": "t_asset"})

        tmp = fin_data['ticker'].value_counts()
        tmp = tmp[tmp == 3]
        fin_data = fin_data[fin_data['ticker'].isin(tmp.index)]

        return fin_data[['ticker', 'endDate', 'revenue', 'net_profit', 't_asset']]

    def _load_fund_holding_data(self, date):
        sql_script = "select jjdm, clrq, zzrq, (select count(1) from st_fund.t_st_gm_rhb r where r.jjdm = a.jjdm) " \
                     "hb_count from st_fund.t_st_gm_jjxx a " \
                     "where a.Jjfl in ('1','3') and m_opt_type <> '03' and clrq is not null " \
                     "order by clrq asc"
        data = self.fetch_data_batch('funduser', sql_script)
        data['clrq'] = data['clrq'].map(str)
        data['zzrq'] = data['zzrq'].fillna('20991231')

        # 成立满一年
        begin_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d') - datetime.timedelta(days=365)
        begin_date = datetime.datetime.strftime(begin_dt, '%Y%m%d')
        fund_id_list = data[(data['clrq'] < begin_date) & (data['zzrq'] > self.trade_date)]['jjdm'].tolist()

        n = 50
        fund_holding = []
        group_fund_id_list = [fund_id_list[i: i + n] for i in range(0, len(fund_id_list), n)]
        for group_id in group_fund_id_list:
            sql_script = "SELECT JJDM, ZQDM, JSRQ, GGRQ, ZJBL FROM funddb.GPZH WHERE JJDM in ({}) and JSRQ = {} and " \
                         "GGRQ <= {}".format(','.join("'{0}'".format(x) for x in group_id), date, self.trade_date)
            df = self.fetch_data_batch('readonly', sql_script)
            fund_holding.append(df)

        fund_holding = pd.concat(fund_holding)
        # holding num >= 10
        count_df = fund_holding['JJDM'].value_counts()
        count_df = count_df[count_df >= 10]
        fund_holding = fund_holding[fund_holding['JJDM'].isin(count_df.index)]
        fund_holding.rename(columns={"JJDM": "fund_id", "ZQDM": "ticker", "ZJBL": "weight"}, inplace=True)
        fund_holding['weight'] /= 100.

        return fund_holding[['fund_id', 'ticker', 'weight']]

    def load(self):
        quotation_date, report_date = self._load_associated_date()
        equity_value = self._load_valuation_data(quotation_date)
        equity_growth = self._load_growth_data()
        fund_holding_df = self._load_fund_holding_data(report_date)

        return {
            "quotation_date": quotation_date,
            "report_date": report_date,
            "equity_value": equity_value,
            "equity_growth": equity_growth,
            "fund_holding": fund_holding_df
        }


def get_nav_data_from_mysql(fund_name, fof_name):
    sql_script = "SELECT jjdm as fund_id, jjmc as fund_name, khmc as fof_name, " \
                 "jzrq as trade_date, jjjz, ljjz, xnjz, khzcfe FROM ac_fof.t_ac_fof_xfc where " \
                 "jjmc = '{}' and khmc = '{}' order by jzrq".format(fund_name, fof_name)
    res = hbs.db_data_query('alluser', sql_script)
    data = pd.DataFrame(res['data'])

    return data
