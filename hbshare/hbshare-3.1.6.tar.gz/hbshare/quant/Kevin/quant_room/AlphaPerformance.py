"""
Alpha标的表现统计
"""
import pandas as pd
import hbshare as hbs
import datetime
import plotly
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go

plotly.offline.init_notebook_mode(connected=True)


alpha_dict = {
    "hs300": {"明汯稳健增长": "SK5676",
              "幻方300指增欣享一号": "SNL044"},
    "zz500": {"明汯价值成长": "SEE194",
              "启林500指增": "SGY379",
              "黑翼500指增": "SEM323",
              # "幻方500指增": "SN1691",
              "衍复指增三号": "SJH866",
              "天演启航量化500指增": "SQP881",
              "诚奇睿盈500指增": "SQK764",
              "量锐62号": "SGR954",
              "橡木秋实": "SEU546",
              "因诺聚配500指增": "SGX346",
              "赫富500指增一号": "SEP463",
              "中邮永安易股墨丘利二号": "SJE527",
              "量派500指增8号": "SNJ513",
              # "铭量500增强1号": "SLY644",
              "星阔广厦1号": "SNU706"
              },
    "zz1000": {"衍复臻选1000指增": "SNP701",
               "明汯量化中小盘": "SGG585"},
    # "zz1000": {"YF": "SJM688",
    #            "QL": "SJT863",
    #            "MH": "SGG585",
    #            "YN": "SGY044",
    #            "JK": "SCP381"},
    "500_neutral": {"启林盈润1号": "SER285",
                    "卓识利民": "SCL316",
                    "衍复中性三号": "SJH864",
                    "天演广全": "SLC213",
                    "诚奇睿盈对冲尊享": "SNR622",
                    "橡木欣荣": "SEZ550",
                    # "幻方量化专享2号": "SLK497",
                    "赫富对冲四号": "SEW735",
                    "易股鑫源八号": "SS0450",
                    # "量派睿核10号": "SNP300",
                    "星阔云起1号": "SNU704"},
    "cb": {"悬铃A号": "SCH558",
           "百奕传家一号": "SJS027",
           "仟富来开元12号": "SJC879",
           "星辰之艾方多策略4号": "SX5536",
           "安值福慧量化1号": "SCP765"}
}


class AlphaPerformance:
    def __init__(self, start_date, end_date, fund_info_dict):
        self.start_date = start_date
        self.end_date = end_date
        self.fund_info_dict = fund_info_dict
        self._load_data()

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

        trading_day_list = df[df['isWeekEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list

    def _load_data(self):
        nav_series_dict = dict()

        for strategy_type, id_dict in self.fund_info_dict.items():
            nav_list = []
            for fund_name, fund_id in id_dict.items():
                sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                             "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                             "and a.jjzt not in ('3') " \
                             "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                             "order by b.jzrq".format(fund_id, self.start_date, self.end_date)
                res = hbs.db_data_query("highuser", sql_script, page_size=5000)
                data = pd.DataFrame(res['data']).set_index('TRADEDATE')['ADJ_NAV']
                data.name = fund_name
                nav_list.append(data)

            nav_df = pd.concat(nav_list, axis=1)
            nav_series_dict[strategy_type] = nav_df.sort_index()

        self.nav_series_dict = nav_series_dict

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

        plot_ly(fig, filename=sava_path)

    def get_construct_result(self):
        trading_day_list = self._load_calendar()

        # 300指增
        nav_df = self.nav_series_dict['hs300'].reindex(trading_day_list).dropna(how='all')
        return_df = nav_df.fillna(method='ffill').pct_change().fillna(0.)
        adj_nav_df = (1 + return_df).cumprod()
        self.plotly_line(adj_nav_df, "300指增产品走势图", "D:\\量化产品跟踪\\量化池产品净值走势\\300指增走势.html")
        # 500指增
        nav_df = self.nav_series_dict['zz500'].reindex(trading_day_list).dropna(how='all')
        return_df = nav_df.fillna(method='ffill').pct_change()
        for i in range(len(return_df.columns)):
            col = return_df.columns[i]
            return_df.iloc[return_df.index.tolist().index(return_df[col].first_valid_index()) - 1, i] = 0.
        adj_nav_df = (1 + return_df).cumprod()
        self.plotly_line(adj_nav_df, "500指增产品走势图", "D:\\量化产品跟踪\\量化池产品净值走势\\500指增走势.html",
                         figsize=(1500, 800))
        # 1000指增
        nav_df = self.nav_series_dict['zz1000'].reindex(trading_day_list).dropna(how='all')
        return_df = nav_df.fillna(method='ffill').pct_change().dropna()
        adj_nav_df = (1 + return_df).cumprod()
        self.plotly_line(adj_nav_df, "1000指增产品走势图", "D:\\量化产品跟踪\\量化池产品净值走势\\1000指增走势.html",
                         figsize=(1500, 800))
        # 500中性
        nav_df = self.nav_series_dict['500_neutral'].reindex(trading_day_list).dropna(how='all')
        return_df = nav_df.fillna(method='ffill').pct_change()
        for i in range(len(return_df.columns)):
            col = return_df.columns[i]
            return_df.iloc[return_df.index.tolist().index(return_df[col].first_valid_index()) - 1, i] = 0.
        adj_nav_df = (1 + return_df).cumprod()
        self.plotly_line(adj_nav_df, "500中性产品走势图", "D:\\量化产品跟踪\\量化池产品净值走势\\500中性走势.html",
                         figsize=(1500, 800))
        # 可转债
        nav_df = self.nav_series_dict['cb'].reindex(trading_day_list).dropna(how='all')
        return_df = nav_df.fillna(method='ffill').pct_change()
        for i in range(len(return_df.columns)):
            col = return_df.columns[i]
            return_df.iloc[return_df.index.tolist().index(return_df[col].first_valid_index()) - 1, i] = 0.
        adj_nav_df = (1 + return_df).cumprod()
        self.plotly_line(adj_nav_df, "可转债产品走势图", "D:\\量化产品跟踪\\量化池产品净值走势\\可转债走势.html",
                         figsize=(1500, 800))


if __name__ == '__main__':
    AlphaPerformance('20200904', '20211203', alpha_dict).get_construct_result()