"""
指增策略 - 市场结构
"""
import pandas as pd
import hbshare as hbs
import numpy as np
from scipy import stats
import statsmodels.api as sm
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params, style_names
import datetime
import plotly.graph_objs as go
from plotly.offline import plot as plot_ly
from statsmodels.stats.weightstats import DescrStatsW
from hbshare.fe.common.util.data_loader import get_trading_day_list


class MarketHist:
    """
    市场收益率Histogram
    """
    def __init__(self, trade_date, benchmark_id):
        self.trade_date = trade_date
        self.benchmark_id = benchmark_id
        self._load_data()

    def _load_data(self):
        # A股行情
        sql_script = "SELECT SYMBOL, SNAME, VOTURNOVER, PCHG, MCAP, TCAP FROM finchina.CHDQUOTE WHERE" \
                     " TDATE = {}".format(self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
        data = data[data['SYMBOL'].str[0].isin(['0', '3', '6'])]
        data = data[data['VOTURNOVER'] > 1e-8]
        data = data[~data['SNAME'].str.contains('ST')]
        data = data[~data['SNAME'].str.contains('N')]
        data = data[~data['SNAME'].str.contains('C')]
        market_df = data.rename(
            columns={"SYMBOL": "ticker", 'PCHG': "return", "TCAP": "marketValue"})[
            ['ticker', 'return', 'marketValue']].dropna()
        # 指数收益率
        start_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (start_dt - datetime.timedelta(days=30)).strftime('%Y%m%d')
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(self.benchmark_id, pre_date, self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        data['index_return'] = data['TCLOSE'].pct_change()
        index_return = data.set_index('TRADEDATE').loc[self.trade_date, 'index_return']

        self.market_df = market_df
        self.index_return = index_return

    def daily_plot(self):
        market_df = self.market_df.copy()
        market_df = market_df[market_df['return'].abs() <= 10]
        # bins
        interval_range = pd.interval_range(-10, 10, 100, closed='left')
        count_df = pd.cut(market_df['return'], bins=interval_range).value_counts().sort_index().to_frame('num')
        count_df['num_cumsum'] = count_df['num'].cumsum()
        count_df['start'] = count_df.index
        count_df['start'] = count_df['start'].apply(lambda x: round(x.left, 1))
        count_df['color'] = '#55CBF2'
        # locate the index return
        index_return = self.index_return * 100.
        lower = round(np.floor(index_return / 0.2) * 0.2, 2)
        count_df.loc[count_df['start'] == lower, 'color'] = '#ff2d51'
        # quantile
        win_ratio = round(100 - stats.percentileofscore(np.array(market_df['return']), index_return), 1)
        win_med = market_df[market_df['return'] >= index_return]['return'].median()
        lose_med = market_df[market_df['return'] < index_return]['return'].median()
        # locate the lower med
        lower = round(np.floor(lose_med / 0.2) * 0.2, 2)
        count_df.loc[count_df['start'] == lower, 'color'] = '#ffa400'
        # # locate the upper med
        lower = round(np.floor(win_med / 0.2) * 0.2, 2)
        count_df.loc[count_df['start'] == lower, 'color'] = '#ffa400'

        color_list = count_df[count_df['num_cumsum'] > 0]['color'].tolist()

        # text
        map_dict = {"000905": "中证500", "000852": "中证1000", "000300": "沪深300"}
        title_text = "【{}】市场个股收益率结构, {}收益率{}%, 跑赢指数的个股比例为{}%, 跑赢的中位数为{}%, 跑输的中位数为{}%".format(
            self.trade_date, map_dict[self.benchmark_id], round(index_return, 2),
            win_ratio, round(win_med, 2), round(lose_med, 2))

        L = go.Layout(xaxis=dict(range=[-10, 10]), title=title_text, width=1440, height=800)
        D = go.Histogram(x=np.array(market_df['return']), xbins=dict(start=-10, end=10, size=0.2),
                         histfunc='count', histnorm='probability',
                         marker=dict(color=color_list, line=dict(color='white', width=1)))
        F = go.Figure(data=[D], layout=L)
        plot_ly(F, filename='D:\\市场微观结构图\\个股收益率结构\\{}.html'.format(self.trade_date), auto_open=False)


class AlphaSeries:
    def __init__(self, start_date, end_date, benchmark_id='000905'):
        self.start_date = start_date
        self.end_date = end_date
        self.benchmark_id = benchmark_id

    def calculate(self):
        nav_series_list = []
        for name, fund_id in alpha_dict.items():
            sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                         "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3') " \
                         "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                         "order by b.jzrq".format(fund_id, self.start_date, self.end_date)
            res = hbs.db_data_query("highuser", sql_script, page_size=5000)
            data = pd.DataFrame(res['data']).set_index('TRADEDATE')['ADJ_NAV']
            data.name = name
            nav_series_list.append(data)
        nav_df = pd.concat(nav_series_list, axis=1).sort_index()
        # 衍复前期的剔除掉
        nav_df.loc[:"20200219", "衍复指增三号"] = np.NaN
        # 处理: 单独只有衍复有的去掉
        nav_df = nav_df.dropna(subset=nav_df.columns[1:], how='all', axis=0)

        trading_day_list = get_trading_day_list(nav_df.index[0], nav_df.index[-1])
        nav_df = nav_df.reindex(trading_day_list).dropna(how='all', axis=0)

        for col in nav_df.columns:
            nav_df[col] = nav_df[col] / nav_df[col].shift(1) - 1
        nav_df.dropna(axis=0, how='all', inplace=True)
        mean_alpha = nav_df.mean(axis=1)  # 策略日度平均收益

        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(self.benchmark_id, self.start_date, self.end_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        data['index_return'] = data['TCLOSE'].pct_change()
        index_return = data.set_index('TRADEDATE')['index_return'].dropna()

        idx = mean_alpha.index.intersection(index_return.index)
        excess_return = mean_alpha.reindex(idx) - index_return.reindex(idx)
        # excess_return = mean_alpha.reindex(idx)

        return excess_return


def get_market_turnover(start_date, end_date):
    """
    市场成交额数据
    """
    sql_script = "SELECT trade_date, amt_sh, amt_sz, amt_300, amt_500, amt_1000 FROM mac_stock_trading where " \
                 "trade_date >= {} and trade_date <= {}".format(start_date, end_date)
    engine = create_engine(engine_params)
    data = pd.read_sql(sql_script, engine)
    data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    data['amt_A'] = data['amt_sh'] + data['amt_sz']
    data['amt_other'] = data['amt_A'] - data['amt_300'] - data['amt_500'] - data['amt_1000']

    return data.set_index('trade_date')[['amt_A', 'amt_300', 'amt_500', 'amt_1000', 'amt_other']]


def get_style_factor(start_date, end_date):
    """
    风格因子收益率
    """
    trade_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    pre_date = (trade_dt - datetime.timedelta(days=30)).strftime('%Y%m%d')
    sql_script = "SELECT * FROM factor_return where trade_date >= {} and trade_date <= {}".format(pre_date, end_date)
    engine = create_engine(engine_params)
    data = pd.read_sql(sql_script, engine)
    data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    data = pd.pivot_table(
        data, index='trade_date', columns='factor_name', values='factor_ret').sort_index()[style_names]

    return data


class MarketSpread:
    def __init__(self, trade_date):
        self.trade_date = trade_date
        self._load_data()

    @staticmethod
    def _load_shift_date(date):
        trade_dt = datetime.datetime.strptime(date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=100)).strftime('%Y%m%d')

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            pre_date, date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        trading_day_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list[-1]

    @staticmethod
    def _load_benchmark_components(date):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and " \
                     "SecuCode in ('000300', '000905', '000852')"
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code_series = index_info.set_index('SECUCODE')['INNERCODE']

        weight = []
        for benchmark_id in ['000300', '000905', '000852']:
            inner_code = inner_code_series.loc[benchmark_id]
            sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                         "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                         "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
            data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
            weight_df = data.rename(
                columns={"SECUCODE": "ticker", "ENDDATE": "effDate", "WEIGHT": "weight"})
            weight_df['benchmark_id'] = benchmark_id
            weight.append(weight_df[['ticker', 'benchmark_id']])

        return pd.concat(weight)

    def _load_data(self):
        # A股行情
        sql_script = "SELECT SYMBOL, SNAME, VATURNOVER, PCHG, MCAP, TCAP FROM finchina.CHDQUOTE WHERE" \
                     " TDATE = {}".format(self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
        data = data[data['SYMBOL'].str[0].isin(['0', '3', '6'])]
        data = data[data['VATURNOVER'] > 1e-8]
        data = data[~data['SNAME'].str.contains('ST')]
        data = data[~data['SNAME'].str.contains('N')]
        data = data[~data['SNAME'].str.contains('C')]
        # 剔除新股
        list_status = pd.read_csv('D:\\kevin\\risk_model_jy\\RiskModel\\data\\common_data\\list_status.csv',
                                  index_col=0, dtype={"listDate": str})
        list_status['ticker'] = list_status['ticker'].apply(lambda x: str(x).zfill(6))
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=90)).strftime('%Y%m%d')
        list_status = list_status[list_status['listDate'] <= pre_date]
        data = data[data['SYMBOL'].isin(list_status['ticker'].tolist())]
        # data = data[data['PCHG'].abs() <= 10.1]
        market_df = data.rename(
            columns={"SYMBOL": "ticker", 'PCHG': "return", "TCAP": "marketValue", "MCAP": "floatM"})[
            ['ticker', 'return', 'marketValue', 'floatM']].dropna()

        shift_date = self._load_shift_date(self.trade_date)
        benchmark_cp = self._load_benchmark_components(shift_date)

        market_df = pd.merge(market_df, benchmark_cp, on='ticker', how='left')
        market_df['benchmark_id'].fillna('other', inplace=True)

        # 指数收益率
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format('000905', pre_date, self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        data['index_return'] = data['TCLOSE'].pct_change()
        index_return = data.set_index('TRADEDATE').loc[self.trade_date, 'index_return']

        self.market_df = market_df
        self.index_return = index_return

    @staticmethod
    def _cs_calculate(df):
        ret_series = df['return']
        return [ret_series.std(), ret_series.skew(), ret_series.kurt()]

    def calculate_cross_section_vol(self):
        market_df = self.market_df.copy()
        cs_vol = pd.DataFrame(columns=['std', 'skew', 'kurt'])
        # universe cut
        cut_dict = {
            "300": ["000300"],
            "500": ["000905"],
            "1000": ["000852"],
            "other": ["other"],
            "800": ["000300", "000905"],
            "not_800": ["000852", "other"],
            "1800": ["000300", "000905", "000852"],
            "not_300": ["000905", "000852", "other"],
            "Market_A": ["000300", "000905", "000852", "other"]
        }
        for key, value in cut_dict.items():
            tmp = market_df[market_df['benchmark_id'].isin(value)]
            cs_vol.loc[key] = self._cs_calculate(tmp)
        cs_vol.index.name = 'universe'
        cs_vol = pd.melt(cs_vol.reset_index(), id_vars=['universe'], var_name='type', value_name='value')
        cs_vol['factor_name'] = cs_vol['type'] + '_' + cs_vol['universe']
        cs_vol = cs_vol.set_index('factor_name')['value'].to_frame(self.trade_date)

        return cs_vol

    @staticmethod
    def _calculate(df, index_return):
        win_ratio = 100 - stats.percentileofscore(np.array(df['return']), index_return)
        win_med = df[df['return'] >= index_return]['return'].median()
        lose_med = df[df['return'] < index_return]['return'].median()

        return win_ratio, win_med, lose_med

    def calculate_win_ratio_factor(self):
        market_df = self.market_df.copy()
        index_return = self.index_return * 100.

        # 300 + 500
        win_ratio_df = pd.DataFrame(
            index=[self.trade_date], columns=['win_ratio_800', 'win_spread_800', 'lose_spread_800'])
        tmp_df = market_df[market_df['benchmark_id'].isin(['000300', '000905'])]
        win_ratio, win_med, lose_med = self._calculate(tmp_df, index_return)
        win_ratio_df.loc[self.trade_date] = [win_ratio, win_med - index_return, index_return - lose_med]
        df1 = win_ratio_df.copy()
        # 300 + 500 + 1000
        win_ratio_df = pd.DataFrame(
            index=[self.trade_date], columns=['win_ratio_1800', 'win_spread_1800', 'lose_spread_1800'])
        tmp_df = market_df[~market_df['benchmark_id'].isin(['other'])]
        win_ratio, win_med, lose_med = self._calculate(tmp_df, index_return)
        win_ratio_df.loc[self.trade_date] = [win_ratio, win_med - index_return, index_return - lose_med]
        df2 = win_ratio_df.copy()
        # all market
        win_ratio_df = pd.DataFrame(
            index=[self.trade_date], columns=['win_ratio_all', 'win_spread_all', 'lose_spread_all'])
        win_ratio, win_med, lose_med = self._calculate(market_df, index_return)
        win_ratio_df.loc[self.trade_date] = [win_ratio, win_med - index_return, index_return - lose_med]
        df3 = win_ratio_df.copy()

        win_ratio_df = pd.concat([df1, df2, df3], axis=1).T

        return win_ratio_df


class IndustryCr:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def _load_industry_data(self):
        start_dt = datetime.datetime.strptime(self.start_date, '%Y%m%d')
        pre_date = (start_dt - datetime.timedelta(days=50)).strftime('%Y%m%d')

        sql_script = "SELECT * FROM st_market.t_st_zs_hyzsdmdyb where fljb = {} and hyhfbz = 2".format('2')
        res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).rename(columns={"zsdm": "SYMBOL", "flmc": "INDEXSNAME"})
        map_dict = data.set_index('SYMBOL')['INDEXSNAME'].to_dict()
        # 二级行业的微调
        map_dict.pop('399707')
        map_dict['801193'] = "券商"
        industry_data = []
        for key, value in map_dict.items():
            sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE, ZSZ as MKV " \
                         "FROM funddb.ZSJY WHERE " \
                         "ZQDM = '{}' and JYRQ >= {} and " \
                         "JYRQ <= {}".format(key, pre_date, self.end_date)
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            df = pd.DataFrame(res['data'])
            df['INDEXNAME'] = value
            industry_data.append(df)
        industry_data = pd.concat(industry_data)

        industry_index = pd.pivot_table(
            industry_data, index='TRADEDATE', columns='INDEXNAME', values='TCLOSE').sort_index()
        industry_return = industry_index.pct_change().dropna().loc[self.start_date:]

        industry_mkv = pd.pivot_table(
            industry_data, index='TRADEDATE', columns='INDEXNAME', values='MKV').sort_index()
        industry_mkv = industry_mkv.reindex(industry_return.index).fillna(method='ffill')

        return industry_return, industry_mkv

    def _load_benchmark_return(self):
        start_dt = datetime.datetime.strptime(self.start_date, '%Y%m%d')
        pre_date = (start_dt - datetime.timedelta(days=50)).strftime('%Y%m%d')
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format('000905', pre_date, self.end_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        data['index_return'] = data['TCLOSE'].pct_change()
        index_return = data.set_index('TRADEDATE').loc[self.start_date:, 'index_return']

        return index_return

    def calculate(self):
        industry_return, industry_mkv = self._load_industry_data()
        index_return = self._load_benchmark_return()

        industry_factor = pd.DataFrame(index=industry_return.index)

        # 行业绝对胜率
        win_ratio_abs = industry_return.gt(0).sum(axis=1) / industry_return.shape[1]
        industry_factor['win_ratio_abs'] = win_ratio_abs
        # 行业相对中证500胜率
        win_ratio_relative = (industry_return.sub(index_return, axis=0)).gt(0).sum(axis=1) / industry_return.shape[1]
        industry_factor['win_ratio_relative'] = win_ratio_relative
        # 行业收益的波动率
        industry_factor['ind_std'] = industry_return.std(axis=1)
        # 行业收益的偏度
        industry_factor['ind_skew'] = industry_return.skew(axis=1)
        # 峰度
        industry_factor['ind_kurt'] = industry_return.kurt(axis=1)
        # 行业收益贡献: 标准差/偏度/峰度/spread
        assert (industry_return.shape == industry_mkv.shape)
        industry_ratio = industry_mkv.divide(industry_mkv.sum(axis=1), axis=0)
        industry_attr = industry_return.multiply(industry_ratio)
        industry_factor['ind_attr_std'] = industry_attr.std(axis=1)
        industry_factor['ind_attr_skew'] = industry_attr.skew(axis=1)
        industry_factor['ind_attr_kurt'] = industry_attr.kurt(axis=1)

        industry_factor['ind_spread'] = industry_return.apply(
            lambda x: sm.OLS(x.sort_values().values, sm.add_constant(
                np.arange(industry_return.shape[1]))).fit().params[1], axis=1)

        return industry_factor


class MarketStructure:
    def __init__(self, trade_date, benchmark_id):
        self.trade_date = trade_date
        self.benchmark_id = benchmark_id
        self._load_data()

    def _load_market_info(self):
        # A股行情
        sql_script = "SELECT SYMBOL, SNAME, VOTURNOVER, PCHG, MCAP, TCAP FROM finchina.CHDQUOTE WHERE" \
                     " TDATE = {}".format(self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
        data = data[data['SYMBOL'].str[0].isin(['0', '3', '6'])]
        data = data[data['VOTURNOVER'] > 1e-8]
        data = data[~data['SNAME'].str.contains('ST')]
        data = data[~data['SNAME'].str.contains('N')]
        data = data[~data['SNAME'].str.contains('C')]
        # 剔除新股
        list_status = pd.read_csv('D:\\kevin\\risk_model_jy\\RiskModel\\data\\common_data\\list_status.csv',
                                  index_col=0, dtype={"listDate": str})
        list_status['ticker'] = list_status['ticker'].apply(lambda x: str(x).zfill(6))
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=90)).strftime('%Y%m%d')
        list_status = list_status[list_status['listDate'] <= pre_date]
        data = data[data['SYMBOL'].isin(list_status['ticker'].tolist())]

        data = data[data['PCHG'].abs() <= 10.1]

        market_df = data.rename(
            columns={"SYMBOL": "ticker", 'PCHG': "return", "TCAP": "marketValue", "MCAP": "floatM"})[
            ['ticker', 'return', 'marketValue', 'floatM']].dropna()
        # 指数收益率
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(self.benchmark_id, pre_date, self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        data['index_return'] = data['TCLOSE'].pct_change()
        index_return = data.set_index('TRADEDATE').loc[self.trade_date, 'index_return']

        return market_df, index_return

    def _load_style_factor_return(self):
        sql_script = "SELECT * FROM st_ashare.r_st_barra_factor_return where TRADE_DATE = '{}'".format(self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('alluser', sql_script)['data'])
        size_return = data.set_index('factor_name').loc['size', 'factor_ret']

        return size_return

    def _load_industry_data(self):
        start_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (start_dt - datetime.timedelta(days=50)).strftime('%Y%m%d')

        sql_script = "SELECT * FROM st_market.t_st_zs_hyzsdmdyb where fljb = {} and hyhfbz = 2".format('1')
        res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).rename(columns={"zsdm": "SYMBOL", "flmc": "INDEXSNAME"})
        map_dict = data.set_index('SYMBOL')['INDEXSNAME'].to_dict()
        industry_index = []
        for key, value in map_dict.items():
            sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE, LTSZ as NEG_MKV " \
                         "FROM funddb.ZSJY WHERE " \
                         "ZQDM = '{}' and JYRQ >= {} and " \
                         "JYRQ <= {}".format(key, pre_date, self.trade_date)
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            df = pd.DataFrame(res['data'])
            df['INDEXNAME'] = value
            industry_index.append(df)
        industry_index = pd.concat(industry_index)

        return industry_index

    def _load_data(self):
        market_df, index_return = self._load_market_info()
        size_return = self._load_style_factor_return()
        industry_index = self._load_industry_data()

        self.data_param = {
            "market_df": market_df,
            "index_return": index_return,
            "size_return": size_return,
            "industry_index": industry_index
        }

    def get_construct_result(self):
        data_param = self.data_param.copy()

        structure_df = pd.DataFrame(index=[self.trade_date], columns=[
            'cs_vol', 'cs_vol_w', 'skew', 'kurt', 'win_ratio', 'win_med', 'lose_med', 'size_return', 'ind_cr'])

        market_df = data_param['market_df']
        index_return = data_param['index_return'] * 100.
        structure_df.loc[self.trade_date, 'cs_vol'] = market_df['return'].std() / 100.
        structure_df.loc[self.trade_date, 'cs_vol_w'] = \
            DescrStatsW(np.array(market_df['return']), weights=np.array(market_df['floatM']), ddof=1).std / 100.
        structure_df.loc[self.trade_date, 'skew'] = market_df['return'].skew()
        structure_df.loc[self.trade_date, 'kurt'] = market_df['return'].kurt()
        win_ratio = round(100 - stats.percentileofscore(np.array(market_df['return']), index_return), 1)
        win_med = market_df[market_df['return'] >= index_return]['return'].median() - index_return
        lose_med = market_df[market_df['return'] < index_return]['return'].median() - index_return
        structure_df.loc[self.trade_date, 'win_ratio'] = win_ratio
        structure_df.loc[self.trade_date, 'win_med'] = win_med
        structure_df.loc[self.trade_date, 'lose_med'] = lose_med
        size_return = data_param['size_return']
        structure_df.loc[self.trade_date, 'size_return'] = size_return

        industry_index = data_param['industry_index']
        tmp = pd.pivot_table(
            industry_index, index='TRADEDATE', columns='INDEXNAME', values='TCLOSE').sort_index()
        industry_return = tmp.pct_change().dropna().loc[self.trade_date]
        structure_df.loc[self.trade_date, 'ind_cr'] = industry_return.gt(0).sum() / len(industry_return)

        return structure_df


alpha_dict = {
    "衍复指增三号": "SJH866",
    "九坤日享中证500指数增强1号": "ST9804",
    "因诺聚配中证500指数增强": "SGX346",
    "启林中证500指数增强1号": "SGY379"
}


if __name__ == '__main__':
    # MarketSpread('20211117').calculate_cross_section_vol()
    # sdate = '20180101'
    sdate = '20211101'
    edate = '20211112'

    # from tqdm import tqdm
    # date_list = get_trading_day_list(sdate, edate)
    # cs_vol_list = []
    # win_ratio_list = []
    # for t_date in tqdm(date_list):
    #     market_spread = MarketSpread(t_date)
    #     res1 = market_spread.calculate_cross_section_vol()
    #     res2 = market_spread.calculate_win_ratio_factor()
    #     cs_vol_list.append(res1)
    #     win_ratio_list.append(res2)
    #
    # factor1 = pd.concat(cs_vol_list, axis=1).T
    # factor2 = pd.concat(win_ratio_list, axis=1).T
    #
    # factor1.to_csv('D:\\市场微观结构图\\market_factor_save\\cs_vol.csv')
    # factor2.to_csv('D:\\市场微观结构图\\market_factor_save\\win_ratio.csv')

    # ind_factor = IndustryCr(sdate, edate).calculate()
    # ind_factor.to_csv('D:\\市场微观结构图\\market_factor_save\\ind_cr.csv')

    market_structure = MarketStructure()