"""
本地净值对比程序
"""
import pandas as pd
import numpy as np
from datetime import datetime
import hbshare as hbs
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
from hbshare.fe.common.util.data_loader import get_trading_day_list
from Arbitrage_backtest import cal_annual_return, cal_annual_volatility, cal_sharpe_ratio, cal_max_drawdown
import plotly
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go
import plotly.figure_factory as ff

plotly.offline.init_notebook_mode(connected=True)


class Neutral2Long:
    """
    中性净值剥离
    """
    def __init__(self, neutral_series, fund_name, hedge_ratio=1):
        self.neutral_series = neutral_series
        self.fund_name = fund_name
        self.hedge_ratio = hedge_ratio
        self._load_data()

    def _load_data(self):
        start_date, end_date = self.neutral_series.index[0], self.neutral_series.index[-1]

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            start_date, end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)
        trading_day_list = df[df['isWeekEnd'] == 1]['calendarDate'].tolist()

        sql_script = "SELECT * FROM mac_share_price_index_futures where trade_date >= {} and trade_date <= {}".format(
            start_date, end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.data = data[['trade_date', 'ZZ500', 'IC00', 'IC01']].set_index('trade_date').reindex(trading_day_list)

    @staticmethod
    def week_of_month(dt):
        """ Returns the week of the month for the specified date.
        """
        first_day = dt.replace(day=1)
        dom = dt.day
        adjusted_dom = dom + first_day.weekday()
        return int(np.ceil(adjusted_dom / 7.0))

    def get_construct_result(self):
        data = self.data.copy()
        df = pd.merge(self.neutral_series.to_frame('neutral_nav'), data, left_index=True, right_index=True).sort_index()
        df['index_return'] = df['ZZ500'].pct_change().fillna(0.)
        df['future_return'] = df['IC00'].pct_change().fillna(0.)
        df['trade_date'] = df.index
        df['week'] = df['trade_date'].apply(lambda x: self.week_of_month(datetime.strptime(x, '%Y%m%d')))
        df.loc[df['week'] == 3, 'roll_return'] = df['IC01'] / df['IC00'] - 1
        df['roll_return'] = df['roll_return'].fillna(0.)
        df['单日对冲成本'] = (df['index_return'] - df['future_return'] + df['roll_return']) * self.hedge_ratio
        df['nav_对冲成本'] = (1 + df['单日对冲成本']).cumprod()
        df['对冲前alpha'] = (df['neutral_nav'] - df['nav_对冲成本']) / self.hedge_ratio + 1
        # plus beta
        df['return'] = df['index_return'] + df['对冲前alpha'].pct_change().fillna(0.)
        df[self.fund_name] = (1 + df['return']).cumprod()

        return df[[self.fund_name]]


# 伯兄
# local_nav = pd.read_excel("D:\\研究基地\\A-机器学习类\\伯兄\\净值文件\\伯兄卢比孔-多头剥离.xlsx", sheet_name=0, index_col=0)
# local_nav['tradeDate'] = local_nav.index
# local_nav['tradeDate'] = local_nav['tradeDate'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
# local_nav.rename(columns={"对冲前alpha（100资金）": "伯兄500指增"}, inplace=True)
# local_nav = local_nav.set_index('tradeDate')['伯兄500指增'].sort_index()
# local_nav = Neutral2Long(local_nav, '伯兄500指增').get_construct_result()

# 概率
nav_pieces1 = pd.read_excel('D:\\研究基地\\A-机器学习类\\概率\\概率业绩数据_0903.xlsx', sheet_name=5)
nav_pieces1.rename(columns={"日期": "trade_date", "估算超额收益": "estimate_return"}, inplace=True)
nav_pieces1['trade_date'] = nav_pieces1['trade_date'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
nav_pieces1 = Neutral2Long(
    nav_pieces1.set_index('trade_date')['累计净值'], '概率500指增', hedge_ratio=0.8).get_construct_result()

sql_script_out = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
             "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
             "and a.jjzt not in ('3') " \
             "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
             "order by b.jzrq".format('SQT076', '20210625', '20211217')
res_out = hbs.db_data_query("highuser", sql_script_out, page_size=5000)
online_nav = pd.DataFrame(res_out['data']).set_index('TRADEDATE')['ADJ_NAV']
local_nav = pd.concat([nav_pieces1, online_nav], axis=1)
local_nav['return'] = local_nav['ADJ_NAV'].pct_change()
local_nav['tmp'] = local_nav['概率500指增']
start_point = local_nav['return'].first_valid_index()
for k in range(local_nav.index.tolist().index(start_point), len(local_nav)):
    local_nav.loc[local_nav.index.tolist()[k], 'tmp'] = local_nav.iloc[k - 1]['tmp'] * (1 + local_nav.iloc[k]['return'])
local_nav = local_nav[['tmp']].rename(columns={"tmp": "概率500指增"})


compare_dict = {"衍复指增三号": "SJH866",
                "启林500指增": "SGY379",
                "因诺聚配500指增": "SGX346",
                "天演中证500指增": "SJU836",
                "诚奇中证500增强": "SLS817",
                "灵均进取1号": "SW3470",
                "凡二英火5号": "SJM016",
                # "星阔广厦1号中证500指数增": "SNU706",
                "世纪前沿500指增": "SGP682",
                "赫富500指增一号": "SEP463",
                "九坤日享500指增": "ST9804"}


class LocalNavComparer:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        # calendar
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency='week')
        # nav_df
        nav_list = []
        for fund_name, fund_id in compare_dict.items():
            sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                         "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3') " \
                         "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                         "order by b.jzrq".format(fund_id, self.start_date, self.end_date)
            res = hbs.db_data_query("highuser", sql_script, page_size=5000)
            data = pd.DataFrame(res['data']).set_index('TRADEDATE')['ADJ_NAV']
            data.name = fund_name
            nav_list.append(data)
        nav_df = pd.concat(nav_list, axis=1).sort_index().reindex(trading_day_list).fillna(method='ffill', limit=1)
        nav_df = pd.merge(nav_df, local_nav, left_index=True, right_index=True, how='left').fillna(
            method='ffill', limit=1)
        nav_df = nav_df / nav_df.iloc[0]
        # benchmark
        benchmark_id = '000905'
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(benchmark_id, self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script)
        data = pd.DataFrame(res['data']).rename(columns={"TCLOSE": "benchmark"}).set_index('TRADEDATE')[['benchmark']]
        data = data.reindex(trading_day_list)

        assert (nav_df.shape[0] == data.shape[0])

        excess_return = nav_df.pct_change().fillna(0.).sub(data.pct_change()['benchmark'].squeeze().fillna(0.), axis=0)

        self.excess_df = (1 + excess_return.fillna(0.)).cumprod()

    @staticmethod
    def plotly_line(df, title_text, sava_path, figsize=(1200, 500)):
        fig_width, fig_height = figsize
        data = []
        for col in df.columns:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines"
            )
            data.append(trace)

        date_list = df.index.tolist()
        tick_vals = [i for i in range(0, len(df), 4)]
        tick_text = [date_list[i] for i in range(0, len(df), 4)]

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True, tickvals=tick_vals, ticktext=tick_text),
            template='plotly_white'
        )
        fig = go.Figure(data=data, layout=layout)

        plot_ly(fig, filename=sava_path, auto_open=False)

    def get_construct_result(self):
        # plot
        self.plotly_line(
            self.excess_df, "500指增产品对比", "D:\\量化产品跟踪\\新增净值走势对比\\净值曲线.html", figsize=(1500, 800))
        # calculate
        nav_df = self.excess_df.copy()
        portfolio_index_df = pd.DataFrame(
            index=nav_df.columns, columns=['超额年化收益', '超额年化波动', '最大回撤', 'Sharpe', '胜率', '平均损益比'])
        portfolio_index_df.loc[:, '超额年化收益'] = nav_df.pct_change().dropna(how='all').apply(cal_annual_return, axis=0)
        portfolio_index_df.loc[:, '超额年化波动'] = \
            nav_df.pct_change().dropna(how='all').apply(cal_annual_volatility, axis=0)
        portfolio_index_df.loc[:, '最大回撤'] = nav_df.apply(cal_max_drawdown, axis=0)
        portfolio_index_df.loc[:, 'Sharpe'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
        portfolio_index_df.loc[:, '胜率'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: x.gt(0).sum() / len(x), axis=0)
        portfolio_index_df.loc[:, '平均损益比'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: x[x > 0].mean() / x[x < 0].abs().mean(), axis=0)
        portfolio_index_df.index.name = '产品名称'
        portfolio_index_df.reset_index(inplace=True)
        # 格式处理
        portfolio_index_df['超额年化收益'] = portfolio_index_df['超额年化收益'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['超额年化波动'] = portfolio_index_df['超额年化波动'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['最大回撤'] = portfolio_index_df['最大回撤'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['Sharpe'] = portfolio_index_df['Sharpe'].round(2)
        portfolio_index_df['胜率'] = portfolio_index_df['胜率'].apply(lambda x: format(x, '.1%'))
        portfolio_index_df['平均损益比'] = portfolio_index_df['平均损益比'].round(2)

        fig = ff.create_table(portfolio_index_df)
        fig.layout.autosize = False
        fig.layout.width = 1000
        fig.layout.height = 400

        plot_ly(fig, filename="D:\\量化产品跟踪\\新增净值走势对比\\收益指标统计.html", auto_open=False)


if __name__ == '__main__':
    LocalNavComparer("20201218", "20211217").get_construct_result()