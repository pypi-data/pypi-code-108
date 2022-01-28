"""
S&P Access China Analysis
"""
import pandas as pd
import hbshare as hbs
import os
from hbshare.fe.common.util.config import style_name, industry_name
from hbshare.fe.common.util.config import factor_map_dict
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go
from WindPy import w

w.start()


class AccessChinaAnalysis:
    def __init__(self, trade_date, benchmark_id):
        self.trade_date = trade_date
        self.benchmark_id = benchmark_id
        self._load_data()

    def _load_portfolio_weight_series(self):
        # data set
        res = w.wset("sectorconstituent", "date={};sectorid=1000025141000000".format(self.trade_date))
        if res.ErrorCode != 0:
            data_set = pd.DataFrame()
            print("Fetching sectorconstituent data error!")
        else:
            data_set = pd.DataFrame(res.Data, index=res.Fields, columns=res.Codes).T
        # use wsd for quota exceed
        code_list = data_set['wind_code'].tolist()
        res = w.wsd(','.join(code_list), "mkt_freeshares", self.trade_date, self.trade_date, "unit=1")
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("Fetching mkt_freeshares data error!")
        else:
            data = pd.DataFrame(res.Data, index=res.Fields, columns=res.Codes).T

        data = pd.merge(data_set, data, left_on='wind_code', right_index=True)
        data['ticker'] = data['wind_code'].apply(lambda x: x.split('.')[0])
        data['weight'] = data['MKT_FREESHARES'] / data['MKT_FREESHARES'].sum()

        return data.set_index('ticker')['weight']

    def _load_benchmark_weight_series(self, ticker=None):
        if ticker is None:
            ticker = self.benchmark_id
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(
            ticker)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[ticker, 'INNERCODE']

        sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})

        return weight_df.set_index('consTickerSymbol')['weight'] / 100.

    def _load_style_exposure(self):
        sql_script = "SELECT * FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}'".format(self.trade_date)
        res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        exposure_df = pd.DataFrame(res['data']).set_index('ticker')
        ind_names = [x.lower() for x in industry_name['sw'].values()]
        exposure_df = exposure_df[style_name + ind_names]

        return exposure_df

    def _load_data(self):
        portfolio_weight_series = self._load_portfolio_weight_series()
        benchmark_weight_series = self._load_benchmark_weight_series()
        # 300 & 500
        benchmark_weight_300 = self._load_benchmark_weight_series('000300')
        benchmark_weight_500 = self._load_benchmark_weight_series('000905')
        style_exposure_df = self._load_style_exposure()

        self.data_param = {
            "portfolio_weight_series": portfolio_weight_series,
            "benchmark_weight_series": benchmark_weight_series,
            "benchmark_weight_300": benchmark_weight_300,
            "benchmark_weight_500": benchmark_weight_500,
            "style_exposure_df": style_exposure_df
        }

    @staticmethod
    def plotly_style_bar(df, title_text, figsize=(1200, 800), legend_x=0.30):
        fig_width, fig_height = figsize
        cols = df.columns.tolist()
        color_list = ['rgb(49, 130, 189)', 'rgb(204, 204, 204)', 'rgb(216, 0, 18)']
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
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            legend=dict(orientation="h", x=legend_x),
            template='plotly_white'
        )

        fig = go.Figure(data=data, layout=layout)

        return fig

    def get_construct_result(self):
        portfolio_weight_series = self.data_param.get('portfolio_weight_series')
        benchmark_weight_series = self.data_param.get('benchmark_weight_series')
        style_exposure_df = self.data_param.get('style_exposure_df')
        # benchmark_weight_300 = self.data_param.get('benchmark_weight_300')
        # benchmark_weight_500 = self.data_param.get('benchmark_weight_500')

        # 板块分布
        weight_df = portfolio_weight_series.reset_index().rename(columns={"wind_code": "ticker"})
        weight_df.loc[weight_df['ticker'].str.startswith('0'), 'sector'] = '深市'
        weight_df.loc[weight_df['ticker'].str.startswith('60'), 'sector'] = '沪市'
        weight_df.loc[weight_df['ticker'].str.startswith('30'), 'sector'] = '创业板'
        weight_df.loc[weight_df['ticker'].str.startswith('688'), 'sector'] = '科创板'
        sector_distribution = weight_df.groupby('sector')['weight'].sum()

        # 风格及行业分布
        idx = portfolio_weight_series.index.union(benchmark_weight_series.index).intersection(
            style_exposure_df.index)

        portfolio_weight_series = portfolio_weight_series.reindex(idx).fillna(0.)
        benchmark_weight_series = benchmark_weight_series.reindex(idx).fillna(0.)
        style_exposure_df = style_exposure_df.reindex(idx).astype(float)
        portfolio_expo = style_exposure_df.T.dot(portfolio_weight_series)
        benchmark_expo = style_exposure_df.T.dot(benchmark_weight_series)
        style_expo = pd.concat([portfolio_expo.to_frame('port'), benchmark_expo.to_frame('bm')], axis=1)
        style_expo['active'] = style_expo['port'] - style_expo['bm']

        reverse_ind = dict([(value.lower(), key) for (key, value) in industry_name['sw'].items()])
        benchmark_id_map = {"000300": "沪深300", "000905": "中证500", "000906": "中证800", "000852": "中证1000"}

        if not os.path.exists('D:\\市场微观结构图\\S&P_Access_China\\{}'.format(self.trade_date)):
            os.mkdir('D:\\市场微观结构图\\S&P_Access_China\\{}'.format(self.trade_date))

        style_df = style_expo[['port', 'bm', 'active']].rename(
            columns={"port": "S&P Access China", "bm": benchmark_id_map[self.benchmark_id], "active": "主动暴露"}).loc[
            style_name]
        style_df.index = style_df.index.map(factor_map_dict)
        fig = self.plotly_style_bar(style_df, "横截面持仓风格暴露")
        plot_ly(fig, filename="D:\\市场微观结构图\\S&P_Access_China\\{}\\风格暴露.html".format(self.trade_date))

        # 行业
        ind_df = style_expo[['port', 'bm', 'active']].rename(
            columns={"port": "S&P Access China", "bm": benchmark_id_map[self.benchmark_id],
                     "active": "主动暴露"}).iloc[10:]
        ind_df.index = [reverse_ind[x] for x in ind_df.index]
        fig = self.plotly_style_bar(ind_df, "横截面持仓行业暴露", figsize=(1500, 700), legend_x=0.35)
        plot_ly(fig, filename="D:\\市场微观结构图\\S&P_Access_China\\{}\\行业暴露.html".format(self.trade_date))

        results = {"style_df": style_df, "ind_df": ind_df, "sector_distribution": sector_distribution}

        return results


if __name__ == '__main__':
    AccessChinaAnalysis('20210831', '000906').get_construct_result()