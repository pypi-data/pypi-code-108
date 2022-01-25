#!/usr/bin/python
#coding:utf-8
import hbshare as hbs
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts.globals import ThemeType


class PrivateFundRAReturnCalculator:
    def __init__(self, fund_id_list, start_date, end_date):
        self.fund_id_list = fund_id_list
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    @staticmethod
    def _load_calendar(start_date, end_date):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            start_date, end_date)
        res = hbs.db_data_query('readonly', sql_script)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        return df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd']]

    def _load_fund_info(self):
        data = []
        for fund_id in self.fund_id_list:
            sql_script = "SELECT JJDM, JJJC, CLRQ, ZZRQ FROM funddb.jjxx1 WHERE JJDM = '{}'".format(fund_id)
            res = hbs.db_data_query('readonly', sql_script)
            df = pd.DataFrame(res['data'])
            data.append(df)
        data = pd.concat(data)

        return data

    def _load_fund_nav(self):
        data = []
        for fund_id in self.fund_id_list:
            sql_script = "SELECT a.jjdm fund_id, b.jzrq tradeDate, b.fqdwjz as adj_nav from " \
                         "fundapp.jjxx1 a, fundapp.smlj b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3') " \
                         "and a.jjdm = '{}' " \
                         "order by b.jzrq".format(fund_id)
            res = hbs.db_data_query('readonly', sql_script)
            df = pd.DataFrame(res['data'])
            data.append(df)
        data = pd.concat(data)

        return data

    @staticmethod
    def cal_ret(nav_series):
        period_nav = nav_series.copy().dropna()
        annual_return = (period_nav.iloc[-1] / period_nav.iloc[0]) ** (2/3) - 1
        return annual_return

    def _load_data(self):
        fund_nav = self._load_fund_nav()
        all_ret = []
        for fund_id in self.fund_id_list:
            df = fund_nav[fund_nav['FUND_ID'] == fund_id].set_index('TRADEDATE')['ADJ_NAV'].sort_index()
            range_start, range_end = df.index[0], df.index[-1]
            date_range = [x.strftime("%Y%m%d") for x in pd.date_range(range_start, range_end)]
            df = df.reindex(date_range)
            rolling_ret = df.rolling(548, min_periods=52).apply(lambda x: self.cal_ret(x))[548:]
            all_ret.append(rolling_ret)

        all_ret = pd.concat(all_ret, axis=1).dropna(how='any')
        fund_info = self._load_fund_info()
        all_ret.columns = fund_info['JJJC'].tolist()
        # reindex
        interval_start, interval_end = all_ret.index[0], all_ret.index[-1]
        calendar_df = self._load_calendar(interval_start, interval_end)
        weekend_list = calendar_df[
            (calendar_df['isWeekEnd'] == 1) & (calendar_df['isOpen'] == 1)]['calendarDate'].tolist()
        all_ret = all_ret.reindex(weekend_list)

        all_ret = all_ret[(all_ret.index >= self.start_date) & (all_ret.index <= self.end_date)]

        self.data = all_ret

    def draw_picture(self):
        df = self.data.copy()
        df *= 100

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="滚动18个月年化收益率走势"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                is_inverse=True,
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                min_='dataMin',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ],
        ).add_xaxis(
            xaxis_data=df.index.tolist()[::-1]
        )

        for fund_name in df.columns:
            line.add_yaxis(
                series_name=fund_name,
                y_axis=df[fund_name].round(2).tolist()[::-1],
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.5),
                label_opts=opts.LabelOpts(is_show=False)
            )

        return line


if __name__ == '__main__':
    results = PrivateFundRAReturnCalculator(
        ['P00107', 'SK8618', 'P00193'], start_date='20190220', end_date='20210301').draw_picture()
