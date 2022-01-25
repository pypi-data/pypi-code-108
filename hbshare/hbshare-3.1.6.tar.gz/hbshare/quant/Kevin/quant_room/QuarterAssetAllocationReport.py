"""
季度资产报告辅助程序
"""
import pandas as pd
from datetime import datetime
import os
import plotly
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go

plotly.offline.init_notebook_mode(connected=True)


class QuarterAssetAllocationReport:
    def __init__(self, start_date, end_date, data_path, file_name):
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = data_path
        self.file_name = file_name
        self._load_data()

    def _load_data(self):
        data_with_header = pd.read_excel(
            os.path.join(self.data_path, r"{}".format(self.file_name)), sheet_name='原始净值')
        data = pd.read_excel(os.path.join(self.data_path, r"{}".format(self.file_name)), sheet_name='原始净值', header=1)
        data['t_date'] = data['t_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        data.index = data['t_date']
        cols = data_with_header.columns.tolist()
        # 月末日期
        df = data[['t_date']].sort_index()
        df['month'] = df['t_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d').month)
        df['next_month'] = df['month'].shift(-1).fillna(0.).astype(int)
        df = df[(df['month'] != df['next_month']) & (df['t_date'] >= self.start_date)]
        trading_day_list = sorted(df['t_date'].tolist())
        # type
        data_param = dict()
        type_list = [x for x in cols if not x.startswith('Unnamed')]
        for i in range(len(type_list) - 1):
            typ = type_list[i]
            s_index, e_index = cols.index(type_list[i]), cols.index(type_list[i + 1])
            data_slice = data[data.columns[s_index: e_index]]
            if typ in ['量价（500）', '机器学习', '基本面']:
                data_slice['benchmark'] = data['中证500']
            elif typ in ['量价（300）']:
                data_slice['benchmark'] = data['沪深300']
            elif typ in ['量价（1000）']:
                data_slice['benchmark'] = data['中证1000']
            else:
                 pass
            data_slice = data_slice[data_slice.index >= self.start_date].reindex(trading_day_list)
            data_param[type_list[i]] = data_slice
        # 指数
        index_df = data[['沪深300', '中证500', '中证1000']].reindex(trading_day_list)

        self.trading_day_list = trading_day_list
        self.data_param = data_param
        self.index_df = index_df

    def calculate_excess_return(self):
        data_lj = self.data_param['量价（500）']
        data_ml = self.data_param['机器学习']
        data_fd = self.data_param['基本面']

        return_lj = data_lj.pct_change(limit=1).dropna(axis=0, how='all')
        return_lj['average'] = return_lj[return_lj.columns[:-1]].mean(axis=1)
        return_lj['ave_excess'] = return_lj['average'] - return_lj['benchmark']

        return_fd = data_fd.pct_change(limit=1).dropna(axis=0, how='all')
        return_fd['average'] = return_fd[return_fd.columns[:-1]].mean(axis=1)
        return_fd['ave_excess'] = return_fd['average'] - return_fd['benchmark']

        return_ml = data_ml.pct_change(limit=1).dropna(axis=0, how='all')
        return_ml['average'] = return_ml[return_ml.columns[:-1]].mean(axis=1)
        return_ml['ave_excess'] = return_ml['average'] - return_ml['benchmark']

        compare_df = return_lj['ave_excess'].to_frame('量价类').merge(
            return_fd['ave_excess'].to_frame('基本面'), left_index=True, right_index=True).merge(
            return_ml['ave_excess'].to_frame('机器学习'), left_index=True, right_index=True)

        return compare_df

    def calculate_index_return(self):
        index_df = self.index_df.copy()
        return_df = index_df.pct_change().dropna(axis=0, how='all')

        return return_df

    def calculate_market_vol(self):
        # 直接从本地取
        path = 'D:\\kevin\\risk_model_jy\\RiskModel\\data\\common_data\\chg_pct'
        filenames = os.listdir(path)
        filenames = [x for x in filenames if (
                    not x.split('.')[0] < self.start_date and x.split('.')[0] <= self.end_date)]
        date_list = []
        vol_list = []
        for name in filenames:
            date_list.append(name.split('.')[0])
            df = pd.read_csv(os.path.join(path, name)).dropna()
            df = df[(df['dailyReturnReinv'] >= -0.2) & (df['dailyReturnReinv'] <= 0.2)]
            vol_list.append(df['dailyReturnReinv'].std())

        vol_df = pd.DataFrame({"date": date_list, "vol": vol_list})

        return vol_df


def plotly_bar(df, title_text, save_path):
    cols = df.columns.tolist()
    color_list = ['rgb(216, 0, 18)', 'rgb(60, 127, 175)', 'rgb(35, 35, 35)']
    data = []
    for i in range(len(cols)):
        col = cols[i]
        trace = go.Bar(
            x=df.index.tolist(),
            y=df[col],
            name=col,
            marker=dict(color=color_list[i])
        )
        data.append(trace)

    layout = go.Layout(
        title=dict(text=title_text, x=0.07, y=0.85),
        autosize=False, width=1200, height=500,
        yaxis=dict(tickfont=dict(size=12), tickformat=',.1%', showgrid=True),
        xaxis=dict(showgrid=True),
        legend=dict(orientation="h", x=0.35),
        template='plotly_white'
    )
    fig = go.Figure(data=data, layout=layout)

    plot_ly(fig, filename=save_path, auto_open=False)


def plotly_line(df, day_list, title_text, save_path):
    trace = go.Scatter(
        x=df['date'],
        y=df['vol'],
        mode="lines",
        marker=dict(color='rgb(35, 35, 35)')
    )

    data = [trace]

    tick_vals = [df['date'].tolist().index(x) for x in day_list]
    tick_text = [x[:6] for x in day_list]

    layout = go.Layout(
        title=dict(text=title_text, x=0.07, y=0.85),
        autosize=False, width=1200, height=400,
        yaxis=dict(tickfont=dict(size=12), tickformat=',.1%', showgrid=True),
        xaxis=dict(showgrid=True, tickvals=tick_vals, ticktext=tick_text),
        template='plotly_white'
    )

    fig = go.Figure(data=data, layout=layout)

    plot_ly(fig, filename=save_path, auto_open=False)


if __name__ == '__main__':
    allo_rep = QuarterAssetAllocationReport(
        start_date='20201230', end_date='20211231',
        data_path='D:\\量化产品跟踪\\指数增强', file_name='指增-20211231.xlsx')

    excess_df = allo_rep.calculate_excess_return()
    excess_df['date'] = excess_df.index
    excess_df['date'] = excess_df['date'].apply(lambda x: x[:6])
    excess_df = excess_df.set_index('date')[['机器学习', '基本面', '量价类']]
    plotly_bar(excess_df, "股票量化策略超额表现", "D:\\市场微观结构图\\股票量化策略超额表现.html")

    index_return_df = allo_rep.calculate_index_return()
    index_return_df['date'] = index_return_df.index
    index_return_df['date'] = index_return_df['date'].apply(lambda x: x[:6])
    index_return_df = index_return_df.set_index('date')
    plotly_bar(index_return_df, "指数表现", "D:\\市场微观结构图\\指数表现.html")

    market_vol = allo_rep.calculate_market_vol()
    plotly_line(market_vol, allo_rep.trading_day_list, "市场横截面波动率", "D:\\市场微观结构图\\市场横截面波动率.html")
