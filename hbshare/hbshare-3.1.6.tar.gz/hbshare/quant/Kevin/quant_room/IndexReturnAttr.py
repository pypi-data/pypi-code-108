"""
宽基指数的行业收益拆分
"""
import hbshare as hbs
import pandas as pd
import datetime
from hbshare.fe.common.util.config import industry_name

# from plotly.graph_objs import Scatter, Layout
import plotly
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go

plotly.offline.init_notebook_mode(connected=True)


class IndexSectorReturnAttr:
    def __init__(self, start_date, end_date, benchmark_id):
        self.start_date = start_date
        self.end_date = end_date
        self.benchmark_id = benchmark_id
        self._load_data()

    def _load_data(self):
        trading_day_list = self._load_calendar()
        benchmark_weight_series_dict = self._load_benchmark_weight(trading_day_list)
        security_return_series_dict = self._load_security_return_series_dict(benchmark_weight_series_dict)
        security_sector_series_dict = self._load_security_sector(benchmark_weight_series_dict)

        data_param = {"trading_day_list": trading_day_list,
                      "benchmark_weight_series_dict": benchmark_weight_series_dict,
                      "security_return_series_dict": security_return_series_dict,
                      "security_sector_series_dict": security_sector_series_dict}

        self.data_param = data_param

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

        trading_day_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list

    def _load_benchmark_weight(self, trading_day_list):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(
            self.benchmark_id)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[self.benchmark_id, 'INNERCODE']
        benchmark_weight_series_dict = dict()
        for date in trading_day_list:
            sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                         "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                         "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
            data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
            weight_df = data.rename(
                columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})
            benchmark_weight_series_dict[date] = weight_df.set_index(
                'consTickerSymbol')['weight'] / 100.

        return benchmark_weight_series_dict

    def _load_security_return_series_dict(self, benchmark_weight_series_dict):
        ticker_list = list(pd.DataFrame.from_dict(benchmark_weight_series_dict).index)

        all_data = []
        for trading_day in sorted(benchmark_weight_series_dict.keys()) + [self.end_date]:
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
        pct_chg = pivot_df.pct_change().shift(-1).dropna(how='all')
        # process
        security_return_series_dict = dict()
        for date in pct_chg.index.tolist():
            security_return_series_dict[date] = pct_chg.loc[date].dropna()

        return security_return_series_dict

    @staticmethod
    def _load_security_sector(benchmark_weight_series_dict):
        trading_day_list = sorted(benchmark_weight_series_dict.keys())

        ticker_list = list(pd.DataFrame.from_dict(benchmark_weight_series_dict).index)
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

    def get_construct_result(self):
        trading_day_list = self.data_param.get('trading_day_list')
        benchmark_weight_series_dict = self.data_param.get('benchmark_weight_series_dict')
        security_return_series_dict = self.data_param.get('security_return_series_dict')
        security_sector_series_dict = self.data_param.get('security_sector_series_dict')

        ind_attr_list = []
        for trading_day in trading_day_list:
            benchmark_weight_series = benchmark_weight_series_dict[trading_day]
            security_return_series = security_return_series_dict[trading_day]
            security_sector_series = security_sector_series_dict[trading_day]

            idx = benchmark_weight_series.index.intersection(security_return_series.index).intersection(
                security_sector_series.index)

            benchmark_weight_series = benchmark_weight_series.reindex(idx)
            security_return_series = security_return_series.reindex(idx)
            security_sector_series = security_sector_series.reindex(idx)

            df = benchmark_weight_series.to_frame('weight').merge(
                security_return_series.to_frame('return'), left_index=True, right_index=True).merge(
                security_sector_series.to_frame('industry'), left_index=True, right_index=True)

            ind_attr = df.groupby('industry').apply(lambda x: x['weight'].dot(x['return'])).to_frame(trading_day)

            ind_attr_list.append(ind_attr)

        attr_df = pd.concat(ind_attr_list, axis=1)
        period_ind_attr = (1 + attr_df.T).prod() - 1

        return period_ind_attr


if __name__ == '__main__':
    ind_attr1 = IndexSectorReturnAttr('20201220', '20211028', '000300').get_construct_result()
    ind_attr2 = IndexSectorReturnAttr('20201220', '20211028', '000905').get_construct_result()
    ind_attr3 = IndexSectorReturnAttr('20201220', '20211028', '000852').get_construct_result()

    ind_attr_all = ind_attr1.to_frame('沪深300').merge(
        ind_attr2.to_frame('中证500'), left_index=True, right_index=True, how='outer').merge(
        ind_attr3.to_frame('中证1000'), left_index=True, right_index=True, how='outer').fillna(0.).sort_values(by='中证500')

    trace0 = go.Bar(x=ind_attr_all.index, y=ind_attr_all['沪深300'], name='沪深300', marker=dict(color='rgb(216, 0, 18)'))
    trace1 = go.Bar(x=ind_attr_all.index, y=ind_attr_all['中证500'], name='中证500', marker=dict(color='rgb(60, 127, 175)'))
    trace2 = go.Bar(x=ind_attr_all.index, y=ind_attr_all['中证1000'], name='中证1000', marker=dict(color='rgb(102, 102, 102)'))

    data_py = [trace0, trace1, trace2]

    plot_ly(data_py, filename='D:\\市场微观结构图\\今年以来宽基指数的行业贡献.html')