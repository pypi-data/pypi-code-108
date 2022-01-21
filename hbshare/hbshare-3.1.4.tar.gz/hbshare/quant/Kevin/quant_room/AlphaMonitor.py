"""
超额收益观测体系
"""
import hbshare as hbs
import pandas as pd
import numpy as np
import datetime
from scipy import stats
import plotly
import plotly.graph_objs as go
from plotly.offline import plot as plot_ly
import plotly.figure_factory as ff


def plot_render(plot_dic, width=1200, height=600, **kwargs):
    kwargs['output_type'] = 'div'
    plot_str = plotly.offline.plot(plot_dic, **kwargs)
    print('%%angular <div style="height: %ipx; width: %spx"> %s </div>' % (height, width, plot_str))


class AlphaMonitor:
    def __init__(self, trade_date, benchmark_id='000905'):
        self.trade_date = trade_date
        self.benchmark_id = benchmark_id
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
        # 个股收益
        sql_script = "SELECT SYMBOL, SNAME, VOTURNOVER, PCHG FROM finchina.CHDQUOTE WHERE" \
                     " TDATE = {}".format(self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
        data = data[data['SYMBOL'].str[0].isin(['0', '3', '6'])]
        data = data[data['VOTURNOVER'] > 1e-8]
        data = data[~data['SNAME'].str.contains('ST')]
        data = data[~data['SNAME'].str.contains('N')]
        data = data[~data['SNAME'].str.contains('C')]
        market_df = data.rename(
            columns={"SYMBOL": "ticker", 'PCHG': "return"})[['ticker', 'return']].dropna()
        # 指数收益
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=30)).strftime('%Y%m%d')
        sql_script = "SELECT JYRQ as TRADEDATE, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(self.benchmark_id, pre_date, self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        data['index_return'] = data['TCLOSE'].pct_change()
        index_return = data.set_index('TRADEDATE').loc[self.trade_date, 'index_return']
        # 指数成分数据
        shift_date = self._load_shift_date(self.trade_date)
        benchmark_cp = self._load_benchmark_components(shift_date)
        market_df = pd.merge(market_df, benchmark_cp, on='ticker', how='left')
        market_df['benchmark_id'].fillna('other', inplace=True)
        # 风格收益数据
        sql_script = "SELECT * FROM st_ashare.r_st_barra_factor_return where " \
                     "TRADE_DATE >= '{}' and TRADE_DATE <= '{}'".format(pre_date, self.trade_date)
        res = hbs.db_data_query('alluser', sql_script)
        style_df = pd.DataFrame(res['data'])
        style_df = pd.pivot_table(
            style_df, index='trade_date', columns='factor_name', values='factor_ret').sort_index()
        style_df = style_df[['size', 'btop', 'growth']]
        # 申万二级行业数据
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=10)).strftime('%Y%m%d')
        sql_script = "SELECT * FROM st_market.t_st_zs_hyzsdmdyb where fljb = {} and hyhfbz = 3 and sfyx = 1".format('2')
        res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).rename(columns={"zsdm": "SYMBOL", "flmc": "INDEXSNAME"})
        map_dict = data.set_index('SYMBOL')['INDEXSNAME'].to_dict()
        industry_index = []
        for key, value in map_dict.items():
            sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE, " \
                         "LTSZ as NEG_MKV FROM funddb.ZSJY WHERE " \
                         "ZQDM = '{}' and JYRQ >= {} and " \
                         "JYRQ <= {}".format(key, pre_date, self.trade_date)
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            df = pd.DataFrame(res['data'])
            df['INDEXNAME'] = value
            industry_index.append(df)
        industry_index = pd.concat(industry_index)
        industry_index = pd.pivot_table(
            industry_index, index='TRADEDATE', columns='INDEXNAME', values='TCLOSE').sort_index()
        industry_return = industry_index.pct_change().dropna().loc[self.trade_date].sort_values()

        self.data_param = {
            "market_info": market_df,
            "index_return": index_return,
            "style_factor": style_df,
            "industry_return": industry_return
        }

    def _return_structure_plot(self, market_df, index_return):
        market_df = market_df[market_df['return'].abs() <= 10]
        # bins
        interval_range = pd.interval_range(-10, 10, 100, closed='left')
        count_df = pd.cut(market_df['return'], bins=interval_range).value_counts().sort_index().to_frame('num')
        count_df['num_cumsum'] = count_df['num'].cumsum()
        count_df['start'] = count_df.index
        count_df['start'] = count_df['start'].apply(lambda x: round(x.left, 1))
        count_df['color'] = '#55CBF2'
        # locate the index return
        index_return = index_return * 100.
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
        title_text = "【{}】{}收益率{}%, 跑赢指数的个股比例为{}%, 跑赢的中位数为{}%, 跑输的中位数为{}%".format(
            self.trade_date, map_dict[self.benchmark_id], round(index_return, 2),
            win_ratio, round(win_med, 2), round(lose_med, 2))

        layout = go.Layout(xaxis=dict(range=[-10, 10]), title=title_text, width=1200, height=600)
        data = go.Histogram(x=np.array(market_df['return']), xbins=dict(start=-10, end=10, size=0.2),
                            histfunc='count', histnorm='probability',
                            marker=dict(color=color_list, line=dict(color='white', width=1)))

        # figure = go.Figure(data=[data], layout=layout)
        # plot_ly(figure, filename='D:\\临时存储\\市场收益结构.html', auto_open=False)

        return data, layout

    @staticmethod
    def _market_skew_plot(market_df):
        group_labels = ['沪深300', '中证500', '中证1000']
        market_df = market_df[market_df['return'].abs() <= 10]
        data_list = [
            market_df[market_df['benchmark_id'] == x]['return'].tolist() for x in ['000300', '000905', '000852']]
        fig = ff.create_distplot(data_list,
                                 group_labels,
                                 show_hist=False,
                                 show_rug=False)

        fig.update_layout(title="宽基指数成分股收益率偏度",
                          xaxis_title='收益率(%)',
                          yaxis_title='density',
                          width=1200, height=600,
                          template='plotly_white',
                          showlegend=True,
                          legend=dict(
                              orientation="v",
                              y=1,
                              yanchor="top",
                              x=1.0,
                              xanchor="right"))

        # plot_ly(fig, filename='D:\\临时存储\\宽基指数偏度.html', auto_open=False)

        return fig.data, fig.layout

    @staticmethod
    def plotly_line(df, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize
        data = []
        for col in df.columns:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines+markers",
                line=dict(
                    shape='spline'
                )
            )
            data.append(trace)

        tick_vals = df.index.tolist()[::3]

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), tickformat=',.0%', showgrid=True),
            xaxis=dict(showgrid=True, tickvals=tick_vals),
            template='plotly_white'
        )

        # figure = go.Figure(data=data, layout=layout)
        # plot_ly(figure, filename='D:\\临时存储\\风格因子收益.html', auto_open=False)

        return data, layout

    @staticmethod
    def _industry_return_plot(df, index_return, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize
        trace = go.Bar(
            x=df.index.tolist(),
            y=df.round(4).values.tolist(),
            name='申万二级行业收益',
            marker=dict(color='rgb(60, 127, 175)')
        )
        data = [trace]
        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12),  tickformat=',.2%', showgrid=True),
            xaxis=dict(showgrid=True, showticklabels=False),
            template='plotly_white',
            legend=dict(orientation="h"),
            shapes=[
                {"type": "line",
                 "xref": "paper",
                 "x0": 0,
                 "x1": 1,
                 "name": "中证500指数收益",
                 "y0": index_return,
                 "y1": index_return,
                 "line": {'color': 'rgb(216, 0, 18)', 'width': 2, 'dash': 'dash'}}]
        )

        # figure = go.Figure(data=data, layout=layout)
        # plot_ly(figure, filename='D:\\临时存储\\行业收益分布.html', auto_open=False)

        return data, layout

    def run(self):
        data_param = self.data_param

        market_df, index_return = data_param['market_info'], data_param['index_return']
        data, layout = self._return_structure_plot(market_df, index_return)
        plot_render({"data": data, "layout": layout}, width=1200, height=600)

        data, layout = self._market_skew_plot(market_df)
        plot_render({"data": data, "layout": layout}, width=1200, height=600)

        style_df = data_param['style_factor'].cumsum()
        style_df.columns = [x.upper() for x in style_df.columns]
        data, layout = self.plotly_line(style_df, title_text="市场风格走势")
        plot_render({"data": data, "layout": layout}, width=1200, height=600)

        industry_return = data_param['industry_return']
        abs_ratio = industry_return.gt(0).sum() / industry_return.shape[0]
        relative_ratio = industry_return.gt(index_return).sum() / industry_return.shape[0]
        title = "申万二级行业收益：当日绝对上涨比例: {}%, 相对中证500胜率: {}%".format(
            np.round(100*abs_ratio, 2), np.round(100*relative_ratio))
        data, layout = self._industry_return_plot(industry_return, index_return, title)
        plot_render({"data": data, "layout": layout}, width=1200, height=600)


if __name__ == '__main__':
    AlphaMonitor('20220106').run()