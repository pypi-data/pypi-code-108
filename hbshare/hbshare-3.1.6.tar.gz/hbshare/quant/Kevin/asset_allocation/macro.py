import pandas as pd
import numpy as np
import requests
import json
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated import engine_params, index_name
from datetime import datetime
import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts.globals import ThemeType


class EconomyMacro:
    def __init__(self, start_date='20050131', end_date='20210226'):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM macro_economy where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.data = data[['trade_date', 'economy_increase', 'M1', 'M2', 'M1-M2', 'CPI', 'PPI']]

    def draw_picture_one(self):
        df = self.data[['trade_date', 'economy_increase']]
        line = Line(
            init_opts=opts.InitOpts(
                width='800px',
                height='500px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="经济增长",
            y_axis=df["economy_increase"].round(3).tolist(),
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_two(self):
        df = self.data[['trade_date', 'M1', 'M2', 'M1-M2']]
        line = Line(
            init_opts=opts.InitOpts(
                width='800px',
                height='500px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观流动性"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="M1",
            y_axis=df["M1"].round(3).tolist(),
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="M2",
            y_axis=df["M2"].round(3).tolist(),
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="M1-M2",
            y_axis=df["M1-M2"].round(3).tolist(),
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_three(self):
        df = self.data[['trade_date', 'CPI', 'PPI']]
        line = Line(
            init_opts=opts.InitOpts(
                width='800px',
                height='500px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="物价指数"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="CPI",
            y_axis=df["CPI"].round(3).tolist(),
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="PPI",
            y_axis=df["PPI"].round(3).tolist(),
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line


class MarketMacro:
    def __init__(self, start_date='20120201', end_date='20210323'):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM market_macro where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.data = data[['trade_date', 'wind_A', 'HS300', 'ZZ500']]

    def draw_picture(self):
        df = self.data.copy()
        line = Line(
            init_opts=opts.InitOpts(
                width='800px',
                height='500px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="市场宏观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="万得全A",
            y_axis=df["wind_A"].round(3).tolist(),
            is_symbol_show=False,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="沪深300",
            y_axis=df["HS300"].round(3).tolist(),
            is_symbol_show=False,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="中证500",
            y_axis=df["ZZ500"].round(3).tolist(),
            is_symbol_show=False,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line


class MarketMicro:
    def __init__(self, start_date='20050131', end_date='20210226'):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM market_micro where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.left_data = data[data['direction'] == 'left'].sort_values(
            by='trade_date')[['trade_date', 'wind_A', 'HS300', 'ZZ500']]

        self.right_data = data[data['direction'] == 'right'].sort_values(
            by='trade_date')[['trade_date', 'wind_A', 'HS300', 'ZZ500']]

    def draw_picture(self, direction):
        if direction == 'left':
            df = self.left_data.copy()
            tl = "市场微观左侧"
        else:
            df = self.right_data.copy()
            tl = "市场微观右侧"

        line = Line(
            init_opts=opts.InitOpts(
                width='800px',
                height='500px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title=tl),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="万得全A",
            y_axis=df["wind_A"].round(3).tolist(),
            is_symbol_show=False,
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="沪深300",
            y_axis=df["HS300"].round(3).tolist(),
            is_symbol_show=False,
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="中证500",
            y_axis=df["ZZ500"].round(3).tolist(),
            is_symbol_show=False,
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line


class MarketValuation:
    def __init__(self, start_date, end_date, window=3):
        self.start_date = start_date
        self.end_date = end_date
        self.window = window
        self.index_list = ['000016', '000300', '000905', '000852', '000985']
        self._init_api_params()
        self._load_data()

    def _init_api_params(self):
        self.url = 'http://fdc-query.intelnal.howbuy.com/query/data/commonapi?dataTrack=xxxxx'
        self.headers = {'Content-Type': 'application/json'}
        self.post_body = {"database": "readonly", "sql": None}

    def _load_data(self):
        # calendar
        start_dt = datetime.strptime(self.start_date, '%Y%m%d')
        begin_date = datetime(start_dt.year - self.window, start_dt.month, start_dt.day).strftime('%Y%m%d')
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            begin_date, self.end_date)
        post_body = self.post_body
        post_body['sql'] = sql_script
        res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)
        weekend_list = df[(df['isWeekEnd'] == 1) & (df['isOpen'] == 1)]['calendarDate'].tolist()
        # index data
        index_data = []
        for index_code in self.index_list:
            sql_script = "SELECT JYRQ as TRADEDATE, ZQDM as INDEXCODE, SYL as PE_TTM FROM funddb.ZSJY WHERE " \
                         "ZQDM = '{}' and JYRQ >= {} and " \
                         "JYRQ <= {}".format(index_code, begin_date, self.end_date)
            post_body = self.post_body
            post_body['sql'] = sql_script
            res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
            data = pd.DataFrame(res['data'])
            index_data.append(data)

        index_data = pd.concat(index_data)
        self.index_pe = pd.pivot_table(index_data, index='TRADEDATE', columns='INDEXCODE', values='PE_TTM').replace(
            0., np.NaN).reindex(weekend_list)

    def draw_picture(self):
        index_pe = self.index_pe.copy()
        func = lambda x: pd.Series(x).rank(pct=True).iloc[-1]
        n = self.window * 52

        rolling_pct = index_pe.rolling(window=n, center=False, min_periods=n).apply(func)

        df = rolling_pct.loc[self.start_date:].dropna(how='all').reset_index()
        df.rename(columns={"TRADEDATE": "trade_date"}, inplace=True)
        line = Line(
            init_opts=opts.InitOpts(
                width='800px',
                height='500px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="市场宏观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', type_="scroll"),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ],
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        )

        for name in self.index_list:
            line.add_yaxis(
                series_name=index_name[name],
                y_axis=df[name].round(3).tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.5),
                label_opts=opts.LabelOpts(is_show=False)
            )

        return line


class TradingCRNCalculator:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._init_api_params()

    def _init_api_params(self):
        self.url = 'http://fdc-query.intelnal.howbuy.com/query/data/commonapi?dataTrack=xxxxx'
        self.headers = {'Content-Type': 'application/json'}
        self.post_body = {"database": "readonly", "sql": None}
        self.engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(
            'admin', 'mysql', '192.168.223.152', '3306', 'riskmodel'))

    def get_construct_result(self):
        # calendar
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
        trading_day_list = df[df['isOpen'] == 1]['calendarDate'].tolist()
        # calculate
        cr5_list, cr10_list, avg_mkt_list = [], [], []
        for date in trading_day_list:
            sql_script = "SELECT SYMBOL, TDATE, VATURNOVER, TCAP FROM finchina.CHDQUOTE WHERE TDATE = {}".format(date)
            post_body = self.post_body
            post_body['sql'] = sql_script
            res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
            df = pd.DataFrame(res['data'])
            df = df[df['SYMBOL'].str[0].isin(['0', '3', '6'])]
            df.rename(columns={"SYMBOL": "ticker", "TDATE": "tradeDate", "TCAP": "marketValue",
                               "VATURNOVER": "turnoverValue"}, inplace=True)
            # 剔除停牌、没有成交额的数据
            df = df[df['turnoverValue'] > 0.]
            quantile_5, quantile_10 = df['turnoverValue'].quantile(0.95), df['turnoverValue'].quantile(0.90)
            cr5 = df[df['turnoverValue'] >= quantile_5]['turnoverValue'].sum() / df['turnoverValue'].sum()
            cr10 = df[df['turnoverValue'] >= quantile_10]['turnoverValue'].sum() / df['turnoverValue'].sum()
            cr5_list.append(cr5)
            cr10_list.append(cr10)

            avg_mkt = (df['turnoverValue'] * df['marketValue']).sum() / df['turnoverValue'].sum() / 1e+8
            avg_mkt_list.append(avg_mkt)

        results = pd.DataFrame(
            {"trade_date": trading_day_list, "cr5": cr5_list, "cr10": cr10_list, "avg_mkt": avg_mkt_list})
        # 上证综指走势
        sql_script = "SELECT JYRQ, SPJG FROM funddb.ZSJY WHERE ZQDM = '{}' and JYRQ >= {} and JYRQ <= {}".format(
            '000001', trading_day_list[0], trading_day_list[-1])
        post_body = self.post_body
        post_body['sql'] = sql_script
        res = requests.post(url=self.url, data=json.dumps(post_body), headers=self.headers).json()
        df = pd.DataFrame(res['data']).rename(columns={"JYRQ": "trade_date", "SPJG": "close"})[['trade_date', 'close']]

        results = pd.merge(results, df, on='trade_date')

        results.to_sql('turnover_structure', self.engine, index=False, if_exists='append')

    def _load_data(self):
        sql_script = "SELECT * FROM turnover_structure WHERE TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.data = data[['trade_date', 'cr5', 'cr10', 'avg_mkt', 'close']]

    def draw_cr_picture(self):
        self._load_data()
        df = self.data.copy()
        df['cr5'] *= 100
        df['cr10'] *= 100

        line = Line(
            init_opts=opts.InitOpts(
                width='800px',
                height='500px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="A股成交额集中度"),
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
            xaxis_data=df['trade_date'].tolist()[::-1]
        ).add_yaxis(
            series_name="前5%个股成交额集中度",
            y_axis=df["cr5"].round(1).tolist()[::-1],
            is_symbol_show=False,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="前10%个股成交额集中度",
            y_axis=df["cr10"].round(1).tolist()[::-1],
            is_symbol_show=False,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_avg_picture(self):
        self._load_data()
        df = self.data.copy()

        line = Line(
            init_opts=opts.InitOpts(
                width='800px',
                height='500px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="成交额加权市值"),
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
                axislabel_opts=opts.LabelOpts(formatter="{value} 亿")
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ],
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()[::-1]
        ).add_yaxis(
            series_name="成交额加权市值",
            y_axis=df["avg_mkt"].round(1).tolist()[::-1],
            is_symbol_show=False,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            label_opts=opts.LabelOpts(is_show=False)
        ).extend_axis(
            yaxis=opts.AxisOpts(
                type_="value",
                min_='dataMin',
                axistick_opts=opts.AxisTickOpts(is_show=True))
        )

        line2 = (
            Line()
            .add_xaxis(xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="上证综指",
                yaxis_index=1,
                y_axis=df["close"].round(1).tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.5),
                label_opts=opts.LabelOpts(is_show=False))
        )

        return line.overlap(line2)


if __name__ == '__main__':
    # EconomyMacro('20050131', '20210226').draw_picture_three()
    # MarketMacro('20120201', '20210323').draw_picture()
    # MarketMicro('20050131', '20210226').draw_picture(direction="right")
    # MarketValuation('20120224', '20210326').draw_picture()
    TradingCRNCalculator('20070104', '20210423').draw_cr_picture()
