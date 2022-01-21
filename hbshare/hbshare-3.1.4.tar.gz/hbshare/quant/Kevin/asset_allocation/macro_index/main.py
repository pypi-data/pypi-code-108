import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params, style_names
from hbshare.fe.common.util.config import factor_map_dict
from datetime import datetime
import pyecharts.options as opts
from pyecharts.charts import Line, Bar
from pyecharts.globals import ThemeType
import pywt
import hbshare as hbs
import requests
import json
from hbshare.fe.common.util.data_loader import get_trading_day_list


def series_denoising(data):
    db4 = pywt.Wavelet('db4')
    coeffs = pywt.wavedec(data, db4)
    coeffs[len(coeffs) - 1] *= 0
    coeffs[len(coeffs) - 2] *= 0
    meta = pywt.waverec(coeffs, db4)

    if len(meta) != data.shape[0]:
        meta = meta[:-1]

    return meta


def add_market_index(df, line, index_name):
    """
    为单轴折线图添加指数走势
    @param df: 数据
    @param line: 折线图
    @param index_name: HS300、ZZ500、bond_index、future_index
    @return:
    """
    start_date, end_date = df['trade_date'].tolist()[0], df['trade_date'].tolist()[-1]

    sql_script = "SELECT * FROM mac_market_index where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
        start_date, end_date)
    engine = create_engine(engine_params)
    market_index = pd.read_sql(sql_script, engine)[['trade_date', index_name]]
    market_index['trade_date'] = market_index['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

    df = pd.merge(df, market_index, on='trade_date')

    line.extend_axis(
        yaxis=opts.AxisOpts(
            type_="value",
            axistick_opts=opts.AxisTickOpts(is_show=True),
            splitline_opts=opts.SplitLineOpts(is_show=False))
    )

    name_dict = {"HS300": "沪深300", "ZZ500": "中证500", "bond_index": "中债全债", "future_index": "南华商品"}

    line2 = (
        Line()
        .add_xaxis(
            xaxis_data=df['trade_date'].tolist())
        .add_yaxis(
            series_name="{}指数走势(右轴)".format(name_dict[index_name]),
            is_smooth=True,
            y_axis=df[index_name].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            yaxis_index=1
        )
    )
    line.overlap(line2)

    return line


"======================================================宏观经济类========================================================"


class CurrencyIndex:
    """
    货币类指标
    """
    def __init__(self, start_date='20050131', end_date='20210331'):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_curr where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.monthly_data = data.set_index(
            'trade_date')[['M1_yoy', 'M2_yoy', 'short_term_loan_balance', 'long_term_loan_balance',
                           'social_finance_yoy', 'social_finance_scale',
                           'currency', 'curr_multiplier']].dropna(axis=0, how='all')
        self.daily_data = data.set_index(
            'trade_date')[['reverse_repo_7', 'LPR_1_year', 'LPR_5_year',
                           'long_term_loan_rate', 'deposit_reserve_ratio_s',
                           'deposit_reserve_ratio_l', 'pledged_repo_7']].dropna(axis=0, how='all')

        sql_script = "SELECT trade_date, GDP_current_price FROM mac_eco_increase"
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        self.gdp_data = data

    def draw_picture_M1_M2(self, compare_index=None):
        df = self.monthly_data[['M1_yoy', 'M2_yoy']]
        df['spread'] = df['M1_yoy'] - df['M2_yoy']
        # 小波去噪
        df['M1_de'] = series_denoising(df['M1_yoy'])
        df['M2_de'] = series_denoising(df['M2_yoy'])
        df['spread_de'] = series_denoising(df['spread'])

        df = df.round(2).reset_index()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观流动性"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='year-on-year (%)',
                name_location='middle',
                name_gap=45,
                min_=-20,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="M1",
            is_smooth=True,
            y_axis=df["M1_de"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="M2",
            is_smooth=True,
            y_axis=df["M2_de"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="M1-M2",
            is_smooth=True,
            y_axis=df["spread_de"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        if compare_index is not None:
            line = add_market_index(df, line, compare_index)

        return line

    def draw_picture_loan(self, compare_index=None):
        df = self.monthly_data[['short_term_loan_balance', 'long_term_loan_balance']]
        df = (100 * df.pct_change(periods=12).dropna()).round(2)
        df.reset_index(inplace=True)

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观流动性"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='year-on-year (%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="金融机构：短期贷款余额",
            is_smooth=True,
            y_axis=df["short_term_loan_balance"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="金融机构：长期贷款余额",
            is_smooth=True,
            y_axis=df["long_term_loan_balance"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        if compare_index is not None:
            line = add_market_index(df, line, compare_index)

        return line

    def draw_picture_social_lending(self):
        df = self.monthly_data[['social_finance_yoy', 'social_finance_scale']].dropna().reset_index()
        df = df[df['trade_date'] >= '20160131']
        df['trade_date'] = df['trade_date'].apply(lambda x: x[:4] + '-' + x[4:6])

        bar = (
            Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="单位：%",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="社融数据"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_top='5%'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="单位：万亿",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    # axislabel_opts={"interval": "0", "rotate": 90},
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
            ).add_yaxis(
                series_name='社会融资规模存量',
                y_axis=df['social_finance_scale'].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(opacity=0.3),
                # bar_width="50%",
                z=0
            )
        )

        line = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="社融存量同比",
                is_smooth=True,
                y_axis=df["social_finance_yoy"].tolist(),
                is_symbol_show=True,
                linestyle_opts=opts.LineStyleOpts(width=2),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )

        bar.overlap(line)

        return bar

    def draw_daily_currency_pic(self):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {} and " \
                     "SFYM = 1".format(self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        month_end_list = df['calendarDate'].tolist()

        df = self.daily_data.fillna(method='ffill').reindex(month_end_list).dropna(how='all').reset_index()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观流动性"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="7日逆回购利率",
            y_axis=df["reverse_repo_7"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            is_step=True,
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="LPR：1年",
            y_axis=df["LPR_1_year"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            is_step=True,
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="LPR：5年",
            y_axis=df["LPR_5_year"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            is_step=True,
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="中长期贷款利率：3至5年",
            y_axis=df["long_term_loan_rate"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            is_step=True,
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_deposit(self):
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {} and " \
                     "SFYM = 1".format(self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        month_end_list = df['calendarDate'].tolist()

        df = self.daily_data.fillna(method='ffill').reindex(month_end_list)[
            ['deposit_reserve_ratio_s', 'deposit_reserve_ratio_l']].dropna().reset_index()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观流动性"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="人民币存款准备金率：中小型存款类金融机构",
            y_axis=df["deposit_reserve_ratio_s"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="人民币存款准备金率：大型存款类金融机构",
            y_axis=df["deposit_reserve_ratio_l"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_money_gap(self):
        m2_yoy = self.monthly_data['M2_yoy'].reset_index()
        df = pd.merge(m2_yoy, self.gdp_data, on='trade_date').dropna()
        df['gdp_nominal'] = (df['GDP_current_price'].pct_change(periods=4) * 100).round(2)
        df = df.dropna()[['trade_date', 'M2_yoy', 'gdp_nominal']]

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观流动性"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='year-on-year (%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="M2同比增速",
            is_smooth=True,
            y_axis=df["M2_yoy"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="GDP名义增速",
            is_smooth=True,
            y_axis=df["gdp_nominal"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_curr_multiplier(self):
        df = self.monthly_data[['currency', 'curr_multiplier']].dropna().reset_index()
        df['trade_date'] = df['trade_date'].apply(lambda x: x[:4] + '-' + x[4:6])
        df['currency'] = df['currency'].round()

        bar = (
            Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="单位：倍",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="货币供给"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_top='5%'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="单位：亿",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    # axislabel_opts={"interval": "0", "rotate": 90},
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
            ).add_yaxis(
                series_name='基础货币余额',
                y_axis=df['currency'].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(opacity=0.3),
                # bar_width="50%",
                z=0
            )
        )

        line = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="货币乘数",
                is_smooth=True,
                y_axis=df["curr_multiplier"].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=2),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )

        bar.overlap(line)

        return bar

    def draw_picture_pledged_repo(self, frequency="week"):
        if frequency == "week":
            sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {} and " \
                         "SFZM = 1".format(self.start_date, self.end_date)
        elif frequency == "month":
            sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {} and " \
                         "SFYM = 1".format(self.start_date, self.end_date)
        else:
            sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
                self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        month_end_list = df['calendarDate'].tolist()

        df = self.daily_data.fillna(method='ffill').reindex(month_end_list)[
            ['pledged_repo_7']].dropna().reset_index()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观流动性"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name="单位：%",
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")],
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="银行间质押式回购加权利率:7天",
            y_axis=df["pledged_repo_7"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line


class CurrencyShiborIndex:
    """
    货币Shibor指标
    """
    def __init__(self, start_date='20200101', end_date='20210514', frequency='week'):
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_curr_shibor where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        # calendar
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {} and " \
                     "SFJJ = 0".format(self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        if self.frequency == 'day':
            trading_day_list = df['calendarDate'].tolist()
        else:
            trading_day_list = df[df['isWeekEnd'] == '1']['calendarDate'].tolist()

        data = data.set_index(
            'trade_date')[['SHIBOR_ON', 'SHIBOR_1W', 'SHIBOR_2W', 'SHIBOR_1M', 'SHIBOR_3M', 'SHIBOR_6M', 'SHIBOR_9M',
                           'SHIBOR_1Y']].reindex(trading_day_list).dropna()
        data.rename(columns={"SHIBOR_ON": "SHIBOR:隔夜", "SHIBOR_1W": "SHIBOR:1周", "SHIBOR_2W": "SHIBOR:2周",
                             "SHIBOR_1M": "SHIBOR:1个月", "SHIBOR_3M": "SHIBOR:3个月", "SHIBOR_6M": "SHIBOR:6个月",
                             "SHIBOR_9M": "SHIBOR:9个月", "SHIBOR_1Y": "SHIBOR:1年"}, inplace=True)

        self.data = data

    def draw_picture_shibor(self):
        df = self.data.reset_index()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="各期限SHIBOR走势"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='SHIBOR (%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")],
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        )

        select_true = ['SHIBOR:隔夜', 'SHIBOR:1周', 'SHIBOR:1个月']
        select_false = ['SHIBOR:2周', 'SHIBOR:3个月', 'SHIBOR:6个月', 'SHIBOR:9个月', 'SHIBOR:1年']
        for name in select_true:
            line.add_yaxis(
                series_name=name,
                is_smooth=True,
                y_axis=df[name].round(4).tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.5),
                is_selected=True,
                label_opts=opts.LabelOpts(is_show=False)
            )
        for name in select_false:
            line.add_yaxis(
                series_name=name,
                is_smooth=True,
                y_axis=df[name].round(4).tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.5),
                is_selected=False,
                label_opts=opts.LabelOpts(is_show=False)
            )

        return line


class CreditIndex:
    """
    信用类指标
    """
    def __init__(self, start_date='20050131', end_date='20210331', frequency='week'):
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_credit where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        # calendar
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {} and " \
                     "SFJJ = 0".format(self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        if self.frequency == 'month':
            trading_day_list = df[df['isMonthEnd'] == '1']['calendarDate'].tolist()
        else:
            trading_day_list = df[df['isWeekEnd'] == '1']['calendarDate'].tolist()
        # 产业债信用利差数据
        self.credit_spread_indu = \
            data.set_index('trade_date')[[
                'credit_spread_indu_AAA', 'credit_spread_indu_AA_plus', 'credit_spread_indu_AA']].reindex(
                trading_day_list).dropna()
        # 城投债信用利差数据
        self.credit_spread_urban = \
            data.set_index('trade_date')[[
                'credit_spread_urban_AAA', 'credit_spread_urban_AA_plus', 'credit_spread_urban_AA']].reindex(
                trading_day_list).dropna()
        # 杠杆率数据
        self.leverage_data = data.set_index('trade_date')[[
            'leverage_1', 'leverage_2', 'leverage_3', 'leverage_4']].dropna(how='all')

    def draw_picture_indu(self):
        df = self.credit_spread_indu.reset_index()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="产业债信用利差"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Credit Spread (bp)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")],
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="信用利差：产业债AAA",
            is_smooth=True,
            y_axis=df["credit_spread_indu_AAA"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="信用利差：产业债AA+",
            is_smooth=True,
            y_axis=df["credit_spread_indu_AA_plus"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="信用利差：产业债AA",
            is_smooth=True,
            y_axis=df["credit_spread_indu_AA"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_urban(self):
        df = self.credit_spread_urban.reset_index()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="城投债信用利差"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Credit Spread (bp)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")],
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="信用利差：城投债AAA",
            is_smooth=True,
            y_axis=df["credit_spread_urban_AAA"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="信用利差：城投债AA+",
            is_smooth=True,
            y_axis=df["credit_spread_urban_AA_plus"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="信用利差：城投债AA",
            is_smooth=True,
            y_axis=df["credit_spread_urban_AA"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_leverage(self):
        df = self.leverage_data.reset_index()
        df['trade_date'] = df['trade_date'].apply(lambda x: x[:4] + '-' + x[4:6])
        df['ratio_pct'] = df['leverage_1'].pct_change()
        df = df[1:]
        df['ratio_pct'] = (100 * df['ratio_pct']).round(2)

        bar = (
            Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="宏观杠杆率"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_top='5%'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axislabel_opts={"interval": "0", "rotate": 90},
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
            ).add_yaxis(
                series_name='居民部门杠杆率',
                stack="stack1",
                y_axis=df['leverage_2'].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                bar_width="50%",
                z=0
            ).add_yaxis(
                series_name='非金融企业部门杠杆率',
                stack="stack1",
                y_axis=df['leverage_3'].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                bar_width="50%",
                z=0
            ).add_yaxis(
                series_name='政府部门杠杆率',
                stack="stack1",
                y_axis=df['leverage_3'].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                bar_width="50%",
                z=0
            )
        )

        line = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="实体经济部门杠杆环比增速",
                is_smooth=True,
                y_axis=df["ratio_pct"].tolist(),
                is_symbol_show=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )

        bar.overlap(line)

        return bar


class InflationIndex:
    """
    通胀类指标
    """
    def __init__(self, start_date='20050131', end_date='20210331'):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_inflation where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.data = data[['trade_date', 'CPI_yoy', 'PPI_yoy', 'LME']].dropna()

    def draw_picture(self):
        df = self.data.copy()

        line1 = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="通胀数据"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
            ).add_yaxis(
                series_name="CPI：当月同比",
                y_axis=df["CPI_yoy"].tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            ).add_yaxis(
                series_name="PPI：当月同比",
                y_axis=df["PPI_yoy"].tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            )
        )

        line2 = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="LME铜",
                is_smooth=True,
                y_axis=df["LME"].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )
        line1.overlap(line2)

        return line1


class EconomyIncreaseIndex:
    """
    经济增长类指标
    """
    def __init__(self, start_date='20050131', end_date='20210331'):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_eco_increase where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.data = data

    def draw_picture_gdp(self):
        df = self.data[['trade_date', 'GDP_real', 'GDP_deflator']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='year-on-year (%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="GDP:不变价:当季同比",
            is_smooth=True,
            y_axis=df["GDP_real"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="GDP:平减指数:当季同比",
            is_smooth=True,
            y_axis=df["GDP_deflator"].tolist(),
            is_symbol_show=False,
            # linestyle_opts=opts.LineStyleOpts(width=2),
            areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_PMI(self):
        df = self.data[['trade_date', 'PMI']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='PMI Index',
                name_location='middle',
                name_gap=45,
                min_=30,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="制造业PMI",
            is_smooth=True,
            y_axis=df["PMI"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False),
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(y=50, name="枯荣线")])
        )

        return line

    def draw_picture_IVA(self, compare_index=None):
        df = self.data[['trade_date', 'IVA_yoy']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='IVA yoy',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="工业增加值：当月同比",
            is_smooth=True,
            y_axis=df["IVA_yoy"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        if compare_index is not None:
            line = add_market_index(df, line, compare_index)

        return line

    def draw_picture_elec(self, compare_index=None):
        df = self.data[['trade_date', 'generating_cap_yoy']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Generating Capacity (%)',
                name_location='middle',
                name_gap=45,
                # min_=30,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="发电量：当月同比",
            is_smooth=True,
            y_axis=df["generating_cap_yoy"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        if compare_index is not None:
            line = add_market_index(df, line, compare_index)

        return line

    def draw_picture_excavator(self, compare_index=None):
        df = self.data[['trade_date', 'excavator_yoy']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Generating Capacity (%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="挖掘机销量：当月同比",
            is_smooth=True,
            y_axis=df["excavator_yoy"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        if compare_index is not None:
            line = add_market_index(df, line, compare_index)

        return line

    def draw_picture_consumer_index(self, compare_index=None):
        df = self.data[['trade_date', 'Consumer_Index']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Consumer Index',
                name_location='middle',
                name_gap=45,
                min_=80,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="消费者信心指数",
            is_smooth=True,
            y_axis=df["Consumer_Index"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        if compare_index is not None:
            line = add_market_index(df, line, compare_index)

        return line

    def draw_picture_house_price_index(self):
        df = self.data[['trade_date', 'house_price_yoy', 'hundred_house_price_yoy']].dropna()

        line1 = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    max_=20,
                    min_=-15,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="宏观经济增长"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    max_=2,
                    min_=-1.5,
                    name='House Price Index',
                    name_location='middle',
                    name_gap=45,
                    name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
            ).add_yaxis(
             series_name="70个大中城市新建商品住宅价格指数：环比",
             is_smooth=True,
             y_axis=df["house_price_yoy"].tolist(),
             is_symbol_show=False,
             linestyle_opts=opts.LineStyleOpts(width=1.8),
             label_opts=opts.LabelOpts(is_show=False)
            )
        )

        line2 = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="百城住宅价格指数：同比(右轴)",
                is_smooth=True,
                y_axis=df['hundred_house_price_yoy'].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                yaxis_index=1
            )
        )
        line1.overlap(line2)

        return line1

    def draw_picture_house_investment(self):
        df = self.data[['trade_date', 'house_sell_yoy', 'house_investment_yoy']].dropna()

        line = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="宏观经济增长"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name='House Sell And Investment Index',
                    name_location='middle',
                    name_gap=45,
                    name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
            ).add_yaxis(
                series_name="商品房销售面积：累计同比",
                is_smooth=True,
                y_axis=df["house_sell_yoy"].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            ).add_yaxis(
                series_name="房地产开发投资完成额:住宅:累计同比",
                is_smooth=True,
                y_axis=df["house_investment_yoy"].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            )
        )

        return line

    def draw_picture_industry(self):
        df = self.data[['trade_date', 'ind_goods_cum_yoy', 'ind_income_cum_yoy']].dropna()

        line1 = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    max_=200,
                    min_=-50,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="宏观经济增长"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    max_=40,
                    min_=-10,
                    name='Industry Inventory Circle',
                    name_location='middle',
                    name_gap=45,
                    name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
            ).add_yaxis(
             series_name="工业企业:产成品存货:累计同比",
             is_smooth=True,
             y_axis=df["ind_goods_cum_yoy"].tolist(),
             is_symbol_show=False,
             linestyle_opts=opts.LineStyleOpts(width=1.8),
             label_opts=opts.LabelOpts(is_show=False)
            )
        )

        line2 = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="工业企业：利润总额：累计同比(右轴)",
                is_smooth=True,
                y_axis=df['ind_income_cum_yoy'].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                yaxis_index=1
            )
        )
        line1.overlap(line2)

        return line1

    def draw_picture_cu_rate(self):
        df = self.data[['trade_date', 'ind_cu_rate']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name="单位：%",
                min_=60,
                max_=85,
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            )
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="单季度工业产能利用率",
            is_smooth=True,
            y_axis=df["ind_cu_rate"].tolist(),
            is_symbol_show=True,
            symbol='rect',
            symbol_size=8,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=True)
        )

        return line

    def draw_picture_CCFI(self):
        df = self.data[['trade_date', 'CCFI']].dropna()
        df = df[df['trade_date'] >= '20100101']

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='CCFI',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="中国出口集装箱运价指数CCFI",
            is_smooth=True,
            y_axis=df["CCFI"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_FAI(self):
        df = self.data[['trade_date', 'FAI_cum_yoy', 'FAI_mf_cum_yoy', 'FAI_fm_cum_yoy', 'FAI_re_cum_yoy']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='FAI Cumulative yoy (%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="固定资产投资完成额",
            is_smooth=True,
            y_axis=df["FAI_cum_yoy"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="制造业",
            is_smooth=True,
            y_axis=df["FAI_mf_cum_yoy"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="基建",
            is_smooth=True,
            y_axis=df["FAI_fm_cum_yoy"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="房地产",
            is_smooth=True,
            y_axis=df["FAI_re_cum_yoy"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.5),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_unemployment(self):
        df = self.data[['trade_date', 'unemployment']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Unemployment Ratio (%)',
                name_location='middle',
                name_gap=45,
                min_=3,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="城镇调查失业率",
            is_smooth=True,
            y_axis=df["unemployment"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_OECD(self, compare_index=None):
        df = self.data[['trade_date', 'OECD_leading_indicator']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='OECD综合领先指标：中国',
                name_location='middle',
                name_gap=45,
                min_=80,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="OECD综合领先指标：中国",
            is_smooth=True,
            y_axis=df["OECD_leading_indicator"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        if compare_index is not None:
            line = add_market_index(df, line, compare_index)

        return line

    def draw_picture_jy_curr_index(self, compare_index=None):
        df = self.data[['trade_date', 'jy_curr_index']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='九鞅货币条件指数',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="九鞅货币条件指数",
            is_smooth=True,
            y_axis=df["jy_curr_index"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        if compare_index is not None:
            line = add_market_index(df, line, compare_index)

        return line

    def draw_picture_kq_index(self, compare_index=None):
        df = self.data[['trade_date', 'kq_index']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观经济增长"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='克强指数',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="克强指数",
            is_smooth=True,
            y_axis=df["kq_index"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        if compare_index is not None:
            line = add_market_index(df, line, compare_index)

        return line


class RatesAndPriceIndex:
    """
    汇率和价格类指标
    """
    def __init__(self, start_date='20050131', end_date='20210331'):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_rates_and_price where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.data = data

    def draw_picture_federal_funds_rates(self):
        df = self.data[['trade_date', 'federal_funds_rate']].dropna()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宏观利率"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Effective Federal Funds Rate (%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="有效联邦基金利率",
            is_smooth=True,
            y_axis=df["federal_funds_rate"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_CCPI(self):
        df = self.data[['trade_date', 'CCPI', 'dollar_index']].dropna()

        line1 = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    min_=40,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="CCPI vs 美元指数"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    min_=60,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside")
                ]
            ).add_yaxis(
                series_name="中国大宗商品价格指数",
                y_axis=df["CCPI"].tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            )
        )

        line2 = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="美元指数(右轴)",
                is_smooth=True,
                y_axis=df["dollar_index"].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )
        line1.overlap(line2)

        return line1

    def draw_picture_usd2cny(self):
        df = self.data[['trade_date', 'exchange_rate_dollar', 'CCPI']].dropna()[['trade_date', 'exchange_rate_dollar']]
        df = df[df['trade_date'] >= '20100101']

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="本币兑美元汇率"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Rates: USD-CNY',
                name_location='middle',
                name_gap=45,
                min_=6,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="中间价：美元兑人民币",
            is_smooth=True,
            y_axis=df["exchange_rate_dollar"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_rates_diff(self):
        df = self.data[['trade_date', 'CCPI', 'USDCNY_IB', 'USDCNH_FX']].dropna()
        df['diff'] = df['USDCNY_IB'] - df['USDCNH_FX']

        line1 = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).extend_axis(
            yaxis=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=False))
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="汇率价差"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                min_=6,
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ],
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="在岸人民币汇率",
            is_smooth=True,
            y_axis=df["USDCNY_IB"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name="离岸人民币汇率",
            is_smooth=True,
            y_axis=df["USDCNH_FX"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        line2 = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="汇率价差(在岸 - 离岸)",
                is_smooth=True,
                y_axis=df["diff"].round(4).tolist(),
                is_symbol_show=False,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )
        line1.overlap(line2)

        return line1

    def draw_picture_export(self):
        df = self.data[['trade_date', 'in_export_value']].dropna()
        df['yoy'] = df['in_export_value'].pct_change(periods=12)
        df['in_export_value'] /= 10000.
        df['trade_date'] = df['trade_date'].apply(lambda x: x[:4] + '-' + x[4:6])
        df['in_export_value'] = df['in_export_value'].round(2)
        df = df.dropna()
        df['yoy'] = (100 * df['yoy']).round(2)

        bar = (
            Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="单位：%",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="中国进出口金额"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_top='5%'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="单位：亿美元",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    # axislabel_opts={"interval": "0", "rotate": 90},
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside")
                ],
            ).add_yaxis(
                series_name='中国进出口金额：当月值',
                y_axis=df['in_export_value'].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(opacity=0.3),
                # bar_width="50%",
                z=0
            )
        )

        line = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="当月同比(右轴)",
                is_smooth=True,
                y_axis=df["yoy"].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=2),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )

        bar.overlap(line)

        return bar


"=====================================================股票市场宏微观======================================================"


class StockMarketPE:
    """
    股票市场估值分位
    """
    def __init__(self, window, index_list, start_date='20050131', end_date='20210331'):
        self.window = window
        self.index_list = index_list
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        pre_date = str(int(self.start_date[:4]) - self.window) + self.start_date[4:]

        sql_script = "SELECT * FROM mac_stock_pe_ttm where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            pre_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        # calendar
        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {} and " \
                     "SFJJ = 0".format(pre_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        trading_day_list = df[df['isWeekEnd'] == '1']['calendarDate'].tolist()

        self.data = data.set_index(
            'trade_date').reindex(trading_day_list)[
            ['SZZS', 'SZ50', 'HS300', 'ZZ500', 'ZZ1000']].dropna(axis=0, how='all')

    def draw_picture_pe_ttm(self):
        index_pe = self.data.copy()
        func = lambda x: pd.Series(x).rank(pct=True).iloc[-1]
        n = self.window * 52

        rolling_pct = index_pe.rolling(window=n, center=False, min_periods=n).apply(func)
        df = rolling_pct[rolling_pct.index >= self.start_date].dropna(how='all').reset_index()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场宏观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Market Valuation Quantile (%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
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

        index_name = {"SZ50": "上证50",
                      "HS300": "沪深300",
                      "ZZ500": "中证500",
                      "ZZ1000": "中证1000",
                      "SZZS": "上证指数"}

        for name in self.index_list:
            line.add_yaxis(
                series_name=index_name[name],
                y_axis=(100 * df[name]).round(1).tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.5),
                label_opts=opts.LabelOpts(is_show=False)
            )

        return line


class StockValuation:
    """
    股票市场PE及PB
    """
    def __init__(self, start_date, end_date, mode="PE"):
        self.start_date = start_date
        self.end_date = end_date
        self.mode = mode
        self._load_data()

    def _load_data(self):
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="month")
        if self.mode == "PE":
            # pe_ttm
            sql_script = "SELECT * FROM mac_stock_pe_ttm where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
                self.start_date, self.end_date)
            engine = create_engine(engine_params)
            pe_ttm = pd.read_sql(sql_script, engine)
            pe_ttm['trade_date'] = pe_ttm['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            pe_ttm = pe_ttm[pe_ttm['trade_date'].isin(trading_day_list)]
            self.data = pe_ttm.set_index('trade_date')[['HS300', 'ZZ500', 'ZZ1000']].dropna(subset=['HS300', 'ZZ500'])
        else:
            # eps_ttm
            sql_script = "SELECT * FROM mac_stock_eps_ttm where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
                self.start_date, self.end_date)
            engine = create_engine(engine_params)
            eps_ttm = pd.read_sql(sql_script, engine)
            eps_ttm['trade_date'] = eps_ttm['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            eps_ttm = eps_ttm[eps_ttm['trade_date'].isin(trading_day_list)]
            self.data = eps_ttm.set_index('trade_date')[['HS300', 'ZZ500', 'ZZ1000']].dropna(subset=['HS300', 'ZZ500'])

    def draw_picture(self):
        df = self.data.reset_index()
        df.rename(
            columns={"HS300": "沪深300", "ZZ500": "中证500", "ZZ1000": "中证1000"}, inplace=True)

        line1 = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="宽基指数{}走势".format(self.mode)),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
            ).add_yaxis(
                series_name="中证500",
                y_axis=df["中证500"].tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            ).add_yaxis(
                series_name="中证1000",
                y_axis=df["中证1000"].tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            )
        )

        line2 = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="沪深300(右轴)",
                is_smooth=True,
                y_axis=df["沪深300"].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )
        line1.overlap(line2)

        return line1


class StockValueRotation:
    """
    股票市场大小盘估值轮动
    """
    def __init__(self, start_date='20050101', end_date='20211130'):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency='month')
        # pe_ttm
        sql_script = "SELECT * FROM mac_stock_pe_ttm where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        pe_ttm = pd.read_sql(sql_script, engine)
        pe_ttm['trade_date'] = pe_ttm['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        pe_ttm = pe_ttm[pe_ttm['trade_date'].isin(trading_day_list)]
        pe_ttm = pe_ttm.set_index('trade_date')[['HS300', 'ZZ500', 'ZZ1000']].dropna(subset=['HS300', 'ZZ500'])
        # init_ratio = pe_ttm.iloc[0]['ZZ500'] / pe_ttm.iloc[0]['HS300']
        pe_ttm = pe_ttm.pct_change().dropna(how='all')
        pe_ttm.fillna(method='ffill', axis=1, inplace=True)
        pe_ttm = (1 + pe_ttm).cumprod()
        pe_ttm['pe_ratio'] = pe_ttm['ZZ1000'] / pe_ttm['HS300']
        # eps_ttm
        sql_script = "SELECT * FROM mac_stock_eps_ttm where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        eps_ttm = pd.read_sql(sql_script, engine)
        eps_ttm['trade_date'] = eps_ttm['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        eps_ttm = eps_ttm[eps_ttm['trade_date'].isin(trading_day_list)]
        eps_ttm = eps_ttm.set_index('trade_date')[['HS300', 'ZZ500', 'ZZ1000']].dropna(subset=['HS300', 'ZZ500'])
        # init_ratio = eps_ttm.iloc[0]['ZZ500'] / eps_ttm.iloc[0]['HS300']
        eps_ttm = eps_ttm.pct_change().dropna(how='all')
        eps_ttm.fillna(method='ffill', axis=1, inplace=True)
        eps_ttm = (1 + eps_ttm).cumprod()
        eps_ttm['eps_ratio'] = eps_ttm['ZZ1000'] / eps_ttm['HS300']
        # 指数
        sql_script = "SELECT JYRQ, ZQDM, SPJG FROM funddb.ZSJY where ZQDM in ('000300', '000905', '000852') and " \
                     "JYRQ in ({})".format(','.join(trading_day_list))
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        index_df = pd.DataFrame(res['data']).rename(columns={"JYRQ": "trade_date"})

        index_df = pd.pivot_table(index_df, index='trade_date', columns='ZQDM', values='SPJG').sort_index()
        index_df['ratio'] = index_df['000852'] / index_df['000300']

        data = pd.concat([pe_ttm['pe_ratio'], eps_ttm['eps_ratio'], index_df['ratio']], axis=1).sort_index()
        data.index.name = 'trade_date'
        self.data = data

    def draw_picture(self):
        df = self.data.reset_index()
        df.rename(
            columns={"pe_ratio": "小盘/大盘(PE)", "eps_ratio": "小盘/大盘(EPS)", "ratio": "小盘/大盘(指数)"}, inplace=True)

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场宏观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Market Valuation (%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
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

        for name in df.columns[1:]:
            line.add_yaxis(
                series_name=name,
                y_axis=df[name].round(3).tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            )

        return line


class StockBondRotation:
    def __init__(self, index_name, start_date='20080101'):
        self.index_name = index_name
        self.start_date = start_date
        self._load_data()

    def _load_data(self):
        # 宽基指数PE数据(TTM)
        sql_script = "SELECT trade_date, {} FROM mac_stock_pe_ttm where trade_date >= {}".format(
            self.index_name, self.start_date)
        engine = create_engine(engine_params)
        pe_data = pd.read_sql(sql_script, engine)
        # 国债收益率数据
        sql_script = "SELECT trade_date, ytm_10y FROM mac_treasury_yield where trade_date >= {}".format(self.start_date)
        treasury_data = pd.read_sql(sql_script, engine)

        data = pd.merge(pe_data, treasury_data, on='trade_date').dropna()
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        data['premium'] = 1.0 / data[self.index_name] - 0.01 * data['ytm_10y']

        self.data = data

    def draw_picture_premium(self):
        df = self.data.copy()

        df_mean, df_std = round(df['premium'].mean(), 4), round(df['premium'].std(), 4)

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场宏观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Stock Premium',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="指数估值风险溢价",
            is_smooth=True,
            y_axis=df["premium"].round(4).tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='溢价均值+STD',
            y_axis=[round(df_mean + df_std, 4)] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='溢价均值',
            y_axis=[df_mean] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='溢价均值-STD',
            y_axis=[round(df_mean - df_std, 4)] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line


class StockIndexDiff:
    def __init__(self, start_date='20080101'):
        self.start_date = start_date
        self._init_api_params()
        self._load_data()

    def _init_api_params(self):
        self.url = 'http://fdc-query.intelnal.howbuy.com/query/data/commonapi?dataTrack=xxxxx'
        self.headers = {'Content-Type': 'application/json'}
        self.post_body = {"database": "readonly", "sql": None}

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

    def _load_data(self):
        sql_script = "SELECT JYRQ, ZQDM, SPJG FROM funddb.ZSJY where " \
                     "ZQDM in ('000300', '000852') and JYRQ >= {}".format(self.start_date)
        index_data = self.fetch_data_batch(sql_script)
        index_data = pd.pivot_table(
            index_data, index='JYRQ', columns='ZQDM', values='SPJG').sort_index().pct_change().dropna()
        index_data.rename(columns={"000300": "HS300", "000852": "ZZ1000"}, inplace=True)

        index_data['HS300'] = (1 + index_data['HS300']).cumprod()
        index_data['ZZ1000'] = (1 + index_data['ZZ1000']).cumprod()
        index_data['diff'] = index_data['HS300'] - index_data['ZZ1000']

        self.index_data = index_data

    def draw_picture_index_diff(self):
        df = self.index_data.copy().reset_index()

        max_range_1 = int(df[['HS300', 'ZZ1000']].max().max()) + 1
        max_range_2 = int(df['diff'].abs().max()) + 1

        line1 = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['JYRQ'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    min_=-max_range_2,
                    max_=max_range_2,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="股票市场宏观"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    min_=2 - max_range_1,
                    max_=max_range_1,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside")]
            ).add_yaxis(
                series_name="沪深300",
                y_axis=df["HS300"].round(3).tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            ).add_yaxis(
                series_name="中证1000",
                y_axis=df["ZZ1000"].round(3).tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            )
        )

        line2 = (
            Line()
            .add_xaxis(
                xaxis_data=df['JYRQ'].tolist())
            .add_yaxis(
                series_name="大小盘剪刀差",
                is_smooth=True,
                y_axis=df["diff"].round(3).tolist(),
                is_symbol_show=False,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )
        line1.overlap(line2)

        return line1


class StockCashFlowIndex:
    def __init__(self, start_date='20200101'):
        self.start_date = start_date
        self._init_api_params()
        self._load_data()

    def _init_api_params(self):
        self.url = 'http://fdc-query.intelnal.howbuy.com/query/data/commonapi?dataTrack=xxxxx'
        self.headers = {'Content-Type': 'application/json'}
        self.post_body = {"database": "readonly", "sql": None}

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

    def _load_data(self):
        sql_script = "SELECT * FROM mac_stock_cash_flow where TRADE_DATE >= {}".format(self.start_date)
        engine = create_engine(engine_params)
        cash_flow_df = pd.read_sql(sql_script, engine)
        cash_flow_df['trade_date'] = cash_flow_df['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        cash_flow_df['net_purchases'] = cash_flow_df['sh_net_purchases'] + cash_flow_df['sz_net_purchases']
        cash_flow_df = cash_flow_df[['trade_date', 'margin', 'net_purchases']]

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and " \
                     "SFZM = 1".format(self.start_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        trading_day_list = df['calendarDate'].tolist()

        sql_script = "SELECT JYRQ, ZQDM, SPJG FROM funddb.ZSJY where " \
                     "ZQDM = '000001' and JYRQ >= {}".format(self.start_date)
        index_data = self.fetch_data_batch(sql_script)
        index_data.rename(columns={"JYRQ": "trade_date"}, inplace=True)

        data = pd.merge(cash_flow_df, index_data[['trade_date', 'SPJG']], on='trade_date').fillna(0.)
        data['cum_purchases'] = data['net_purchases'].cumsum()
        data = data[data['trade_date'].isin(trading_day_list)]
        data['margin_diff'] = data['margin'].diff()
        data['hk_diff'] = data['cum_purchases'].diff()

        self.data = data.dropna()

    def draw_picture_cash_flow(self):
        df = self.data.copy()

        max_point = (int(df['SPJG'].max() / 500) + 1) * 500
        min_point = (int(df['SPJG'].min() / 500) - 1) * 500

        line1 = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WALDEN))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="上证综指",
                    min_=min_point,
                    max_=max_point,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="股票市场宏观"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="资金流向：(单位：亿元)",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside")]
            ).add_yaxis(
                series_name="北向资金",
                y_axis=df["hk_diff"].round(2).tolist(),
                is_symbol_show=True,
                symbol='rect',
                symbol_size=6,
                linestyle_opts=opts.LineStyleOpts(width=1.5),
                label_opts=opts.LabelOpts(is_show=False)
            ).add_yaxis(
                series_name="两融资金",
                y_axis=df["margin_diff"].round(2).tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.5, type_='dashed'),
                label_opts=opts.LabelOpts(is_show=False)
            )
        )

        line2 = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="上证综指",
                y_axis=df["SPJG"].round(2).tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.5),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1)
        )
        line1.overlap(line2)

        return line1


class StockTradingIndex:
    def __init__(self, window=3):
        self.window = window
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_stock_trading"
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        self.vix_data = data[['trade_date', 'VIX']].dropna()

        amt_data = data[['trade_date', 'amt_sh', 'amt_sz', 'amt_300', 'amt_500', 'amt_1000', 'amt_other']]
        amt_data['amt_all'] = amt_data['amt_sh'] + amt_data['amt_sz']
        end_date = amt_data['trade_date'].max()
        pre_date = str(int(end_date[:4]) - self.window) + end_date[4:6] + '01'
        amt_data = amt_data[amt_data['trade_date'] >= pre_date]
        self.amt_data = amt_data.dropna()

        turn_data = data[['trade_date', 'turn_sh', 'turn_sz', 'turn_300', 'turn_500', 'turn_1000']]
        end_date = turn_data['trade_date'].max()
        pre_date = str(int(end_date[:4]) - self.window) + end_date[4:6] + '01'
        turn_data = turn_data[turn_data['trade_date'] >= pre_date]
        self.turn_data = turn_data

        flow_data = data[['trade_date', 'inflow_sh', 'inflow_sz']].dropna()
        end_date = flow_data['trade_date'].max()
        pre_date = str(int(end_date[:4]) - self.window) + end_date[4:6] + '01'
        self.flow_data = flow_data[flow_data['trade_date'] >= pre_date]

    def draw_picture_vix(self):
        df = self.vix_data.copy()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场微观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='VIX Index (%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(color='grey', font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="VIX指数",
            is_smooth=True,
            y_axis=df["VIX"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_amt(self, index_name):
        df = self.amt_data[['trade_date', 'amt_' + index_name]].copy()

        q1, med, q3 = df['amt_' + index_name].quantile(0.25), \
            df['amt_' + index_name].quantile(0.5), df['amt_' + index_name].quantile(0.75)

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场微观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='单位（亿元）',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="成交额",
            is_smooth=True,
            y_axis=df["amt_" + index_name].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='25%分位',
            y_axis=[q1] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='中位数',
            y_axis=[med] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='75%分位',
            y_axis=[q3] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_turn(self, index_name):
        df = self.turn_data[['trade_date', 'turn_' + index_name]].copy()

        q1, med, q3 = df['turn_' + index_name].quantile(0.25), \
            df['turn_' + index_name].quantile(0.5), df['turn_' + index_name].quantile(0.75)

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场微观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='单位：%',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="换手率",
            is_smooth=True,
            y_axis=df["turn_" + index_name].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='25%分位',
            y_axis=[q1] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='中位数',
            y_axis=[med] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='75%分位',
            y_axis=[q3] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_amt_summary(self):
        df = self.amt_data[['trade_date', 'amt_300', 'amt_500', 'amt_1000']].copy()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宽基指数成交额"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='单位（亿元）',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="沪深300",
            is_smooth=True,
            y_axis=df["amt_300"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='中证500',
            is_smooth=True,
            y_axis=df["amt_500"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='中证1000',
            is_smooth=True,
            y_axis=df["amt_1000"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_turn_summary(self):
        df = self.turn_data[['trade_date', 'turn_300', 'turn_500', 'turn_1000']].copy()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宽基指数换手率"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='单位: %',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ],
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="沪深300",
            is_smooth=True,
            y_axis=df["turn_300"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='中证500',
            is_smooth=True,
            y_axis=df["turn_500"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='中证1000',
            is_smooth=True,
            y_axis=df["turn_1000"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_turn_compare(self, index_name1, index_name2):
        df = self.turn_data[['trade_date', "turn_" + index_name1, "turn_" + index_name2]].copy()
        df['ratio'] = df["turn_" + index_name1] / df["turn_" + index_name2]

        name_dict = {"turn_300": "沪深300", "turn_500": "中证500", "turn_1000": "中证1000"}

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宽基指数换手率对比"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='单位: %',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ],
        ).extend_axis(
            yaxis=opts.AxisOpts(
                name="换手率比值",
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True))
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name=name_dict["turn_" + index_name1],
            is_smooth=True,
            y_axis=df["turn_" + index_name1].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name=name_dict["turn_" + index_name2],
            is_smooth=True,
            y_axis=df["turn_" + index_name2].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        line2 = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="换手率比值(右轴)",
                is_smooth=True,
                y_axis=df["ratio"].round(3).tolist(),
                is_symbol_show=False,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )

        line.overlap(line2)

        return line


class StockIndexTrading:
    def __init__(self, start_date='20150101'):
        self.start_date = start_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_stock_trading WHERE trade_date >= {}".format(self.start_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        amt_data = data[['trade_date', 'amt_300', 'amt_500', 'amt_1000', 'amt_other']].set_index('trade_date')

        self.amt_data = (100 * amt_data.div(amt_data.sum(axis=1), axis=0)).round(2)

    def draw_picture_index_summary(self, start_date):
        df = self.amt_data[self.amt_data.index >= start_date]
        x_data = df.index.tolist()

        line = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=x_data)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="指数成交额占比走势图"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_left="center", pos_top="5%", legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    max_=100,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                    axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside")],
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False,
                                         axistick_opts=opts.AxisTickOpts(is_show=True), ),
            )
        )

        map_dict = {"amt_300": "沪深300", "amt_500": "中证500", "amt_1000": "中证1000", "amt_other": "其他"}

        for col in df.columns.tolist():
            line.add_yaxis(
                series_name=map_dict[col],
                stack="总量",
                is_symbol_show=False,
                is_smooth=True,
                y_axis=df[col].tolist(),
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
            )

        return line

    def draw_picture_index_trendency(self, index_name, start_date='20150101'):
        df = self.amt_data['amt_' + index_name].reset_index()
        df = df[df['trade_date'] >= start_date]

        q1, med, q3 = df['amt_' + index_name].quantile(0.25), \
            df['amt_' + index_name].quantile(0.5), df['amt_' + index_name].quantile(0.75)

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宽基指数成交额占比走势图"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='单位（%）',
                min_=int(0.8 * df['amt_' + index_name].min()),
                max_=int(1.2 * df['amt_' + index_name].max()),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="成交额占比",
            is_smooth=True,
            y_axis=df["amt_" + index_name].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='25%分位',
            y_axis=[np.round(q1, 2)] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='中位数',
            y_axis=[np.round(med, 2)] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='75%分位',
            y_axis=[np.round(q3, 2)] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line


class StockCrossSectionVolIndex:
    def __init__(self, window=3):
        self.window = window
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_stock_cross_section_vol"
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        end_date = data['trade_date'].max()
        pre_date = str(int(end_date[:4]) - self.window) + end_date[4:6] + '01'
        data = data[data['trade_date'] >= pre_date]

        self.data = data

    def draw_picture_vol(self, index_name):
        df = self.data[['trade_date', index_name]].copy()
        df[index_name] = (df[index_name] * 100).round(2)

        q1, med, q3 = df[index_name].quantile(0.25), \
            df[index_name].quantile(0.5), df[index_name].quantile(0.75)

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场微观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='单位：%',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="截面波动率",
            is_smooth=True,
            y_axis=df[index_name].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='25%分位',
            y_axis=[q1] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='中位数',
            y_axis=[med] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='75%分位',
            y_axis=[q3] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_vol_summary(self):
        df = self.data[['trade_date', 'HS300', 'ZZ500', 'ZZ1000']].copy()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宽基指数截面波动率"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='单位: %',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name="沪深300",
            is_smooth=True,
            y_axis=df["HS300"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='中证500',
            is_smooth=True,
            y_axis=df["ZZ500"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='中证1000',
            is_smooth=True,
            y_axis=df["ZZ1000"].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line

    def draw_picture_vol_compare(self, index_name1, index_name2):
        df = self.data[['trade_date', index_name1, index_name2]].copy()
        df['ratio'] = df[index_name1] / df[index_name2]

        name_dict = {"HS300": "沪深300", "ZZ500": "中证500", "ZZ1000": "中证1000", "OTHER": "其他"}

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="宽基指数截面波动率对比"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='单位: %',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ],
        ).extend_axis(
            yaxis=opts.AxisOpts(
                name="波动率比值",
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True))
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name=name_dict[index_name1],
            is_smooth=True,
            y_axis=df[index_name1].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name=name_dict[index_name2],
            is_smooth=True,
            y_axis=df[index_name2].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        line2 = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="截面波动率比值(右轴)",
                is_smooth=True,
                y_axis=df["ratio"].round(3).tolist(),
                is_symbol_show=False,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )

        line.overlap(line2)

        return line


class StockTimeSeriesVolIndex:
    def __init__(self, window=3, days=20):
        self.window = window
        self.days = days
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_stock_time_series_vol"
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        end_date = data['trade_date'].max()
        pre_date = str(int(end_date[:4]) - self.window) + end_date[4:6] + '01'
        data = data[data['trade_date'] >= pre_date]

        if self.days == 20:
            data = data.set_index('trade_date').filter(regex="_20d").reset_index()
        else:
            data = data.set_index('trade_date').filter(regex='_5d').reset_index()

        self.data = data

    def draw_picture_vol(self, index_name):
        df = self.data[['trade_date', index_name + '_' + str(self.days) + 'd']].copy()
        df.rename(columns={index_name + '_' + str(self.days) + 'd': index_name}, inplace=True)
        df[index_name] = (df[index_name] * 100).round(2)

        q1, med, q3 = df[index_name].quantile(0.25), \
            df[index_name].quantile(0.5), df[index_name].quantile(0.75)

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场微观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='单位：%',
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=df['trade_date'].tolist()
        ).add_yaxis(
            series_name=str(self.days) + "日时序波动率",
            is_smooth=True,
            y_axis=df[index_name].tolist(),
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='25%分位',
            y_axis=[q1] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='中位数',
            y_axis=[med] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        ).add_yaxis(
            series_name='75%分位',
            y_axis=[q3] * df.shape[0],
            is_symbol_show=False,
            linestyle_opts=opts.LineStyleOpts(type_='dashed', width=1.8),
            label_opts=opts.LabelOpts(is_show=False)
        )

        return line


class StockTradingCrIndex:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_stock_trading_cr WHERE TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.data = data[['trade_date', 'cr5', 'cr10', 'avg_mkt', 'close']]

    def draw_cr_picture(self):
        df = self.data.copy()
        df['cr5'] *= 100
        df['cr10'] *= 100

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场微观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
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
        df = self.data.copy()

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场微观"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
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


class StockStyleFactor:
    """
    股票市场风格因子
    """
    def __init__(self, start_date, end_date, frequency='day'):
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency
        self._load_data()

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

    def _load_data(self):
        # sql_script = "SELECT * FROM factor_return where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
        #     self.start_date, self.end_date)
        # engine = create_engine(engine_params)
        # factor_return = pd.read_sql(sql_script, engine)
        # factor_return['trade_date'] = factor_return['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        sql_script = "SELECT * FROM st_ashare.r_st_barra_factor_return where " \
                     "TRADE_DATE >= '{}' and TRADE_DATE <= '{}'".format(self.start_date, self.end_date)
        factor_return = self.fetch_data_batch_hbs("alluser", sql_script)
        factor_return = pd.pivot_table(
            factor_return, index='trade_date', columns='factor_name', values='factor_ret').sort_index()
        factor_return = factor_return[style_names]

        self.factor_return = factor_return

    def draw_picture_cum_return(self):
        factor_return = self.factor_return.copy()
        factor_return = factor_return.cumsum()[style_names] * 100
        cum_line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场微观"),
            legend_opts=opts.LegendOpts(legend_icon='roundRect', pos_top='5%'),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                min_interval=0.1,
                name='Cumulative Performance(%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=factor_return.index.tolist()
        )

        for style_factor in style_names:
            cum_line.add_yaxis(
                series_name=factor_map_dict[style_factor],
                is_smooth=True,
                y_axis=factor_return[style_factor].round(4).tolist(),
                label_opts=opts.LabelOpts(is_show=False)
            )

        return cum_line


class StockStyleMomentum:
    """
    股票市场风格因子动量
    """
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_stock_style_momentum"
        engine = create_engine(engine_params)
        factor_momentum = pd.read_sql(sql_script, engine)
        factor_momentum['trade_date'] = factor_momentum['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.factor_momentum_all = factor_momentum.set_index('trade_date')[style_names]

        factor_momentum = factor_momentum[(factor_momentum['trade_date'] >= self.start_date) &
                                          (factor_momentum['trade_date'] <= self.end_date)]

        self.factor_momentum = factor_momentum.set_index('trade_date')[style_names]

    def draw_picture_factor_momentum(self):
        factor_momentum = self.factor_momentum.copy()
        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场微观"),
            legend_opts=opts.LegendOpts(legend_icon='roundRect', pos_top='5%'),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                # min_interval=0.1,
                name='Style Factor Momentum(%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=factor_momentum.index.tolist()
        )

        for style_factor in style_names:
            line.add_yaxis(
                series_name=factor_map_dict[style_factor],
                is_smooth=True,
                y_axis=factor_momentum[style_factor].round(3).tolist(),
                label_opts=opts.LabelOpts(is_show=False)
            )

        return line

    def draw_picture_quantile(self):
        factor_momentum = self.factor_momentum_all.copy()
        latest_mom = factor_momentum.iloc[-1]
        mom_quantile = factor_momentum.rank(pct=True).iloc[-1]
        df = pd.merge(latest_mom.to_frame('momentum'), mom_quantile.to_frame('mom_quantile'),
                      left_index=True, right_index=True)
        df *= 100.
        df['momentum'] = df['momentum'].round(1)
        df['mom_quantile'] = df['mom_quantile'].round(1)

        x_data = [factor_map_dict[x] for x in df.index.tolist()]
        momentum = df['momentum'].tolist()
        mom_quantile = df['mom_quantile'].tolist()

        momentum_limit = int(np.max(np.abs(momentum)) / 5 + 1) * 5
        mom_quantile_limit = int(np.max(np.abs(mom_quantile)) / 5 + 1) * 5

        bar = (
            Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=x_data)
            .add_yaxis(
                series_name='截面动量: {}'.format(factor_momentum.index[-1]),
                y_axis=momentum,
                label_opts=opts.LabelOpts(is_show=True, formatter="{c}%"))
            .extend_axis(
                yaxis=opts.AxisOpts(
                    name="动量所处历史分位",
                    type_="value",
                    min_=-mom_quantile_limit,
                    max_=mom_quantile_limit,
                    split_number=6,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                    axistick_opts=opts.AxisTickOpts(is_show=True)))
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="风格因子最新截面动量及所处历史分位"),
                tooltip_opts=opts.TooltipOpts(
                    is_show=True, trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_left="center", pos_top="bottom"),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axislabel_opts={"interval": "0"},
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="shadow")),
                yaxis_opts=opts.AxisOpts(
                    name="截面动量",
                    type_="value",
                    min_=-momentum_limit,
                    max_=momentum_limit,
                    # split_number=6,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                    axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                ))
        )

        bar2 = (
            Bar()
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(
                series_name="动量所处历史分位",
                yaxis_index=1,
                y_axis=mom_quantile,
                gap="0%",
                label_opts=opts.LabelOpts(is_show=True, formatter="{c}%"))
        )

        bar.overlap(bar2)

        return bar


class StockStyleSpread:
    """
    股票市场风格因子离散度
    """
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_stock_style_spread"
        engine = create_engine(engine_params)
        factor_spread = pd.read_sql(sql_script, engine)
        factor_spread['trade_date'] = factor_spread['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        factor_spread = factor_spread.set_index('trade_date')[style_names]
        factor_spread = (factor_spread - factor_spread.rolling(72).mean()) / factor_spread.rolling(72).std()
        factor_spread = factor_spread.dropna()

        self.factor_spread_all = factor_spread

        self.factor_spread = factor_spread[(factor_spread.index >= self.start_date) &
                                           (factor_spread.index <= self.end_date)]

    def draw_picture_factor_spread(self):
        factor_spread = self.factor_spread.copy()
        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.WESTEROS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="股票市场微观"),
            legend_opts=opts.LegendOpts(legend_icon='roundRect', pos_top='5%'),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                # min_interval=0.1,
                name='Style Factor Spread(%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")]
        ).add_xaxis(
            xaxis_data=factor_spread.index.tolist()
        )

        for style_factor in style_names:
            line.add_yaxis(
                series_name=factor_map_dict[style_factor],
                is_smooth=True,
                y_axis=factor_spread[style_factor].round(2).tolist(),
                label_opts=opts.LabelOpts(is_show=False)
            )

        return line

    def draw_picture_quantile(self):
        factor_spread = self.factor_spread_all.copy()
        latest_spread = factor_spread.iloc[-1]
        spread_quantile = factor_spread.rank(pct=True).iloc[-1]
        df = pd.merge(latest_spread.to_frame('spread'), spread_quantile.to_frame('spread_quantile'),
                      left_index=True, right_index=True)

        df['spread'] = df['spread'].round(2)
        df['spread_quantile'] = (100 * df['spread_quantile']).round(1)

        x_data = [factor_map_dict[x] for x in df.index.tolist()]
        spread = df['spread'].tolist()
        spread_quantile = df['spread_quantile'].tolist()

        spread_limit = int(np.max(np.abs(spread)) + 1)
        spread_quantile_limit = int(np.max(np.abs(spread_quantile)) / 5 + 1) * 5

        bar = (
            Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=x_data)
            .add_yaxis(
                series_name='截面离散度: {}'.format(factor_spread.index[-1]),
                y_axis=spread,
                label_opts=opts.LabelOpts(is_show=True))
            .extend_axis(
                yaxis=opts.AxisOpts(
                    name="离散度所处历史分位",
                    type_="value",
                    min_=-spread_quantile_limit,
                    max_=spread_quantile_limit,
                    split_number=6,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                    axistick_opts=opts.AxisTickOpts(is_show=True)))
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="风格因子最新截面离散度及所处历史分位"),
                tooltip_opts=opts.TooltipOpts(
                    is_show=True, trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_left="center", pos_top="bottom"),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axislabel_opts={"interval": "0"},
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="shadow")),
                yaxis_opts=opts.AxisOpts(
                    name="截面动量",
                    type_="value",
                    min_=-spread_limit,
                    max_=spread_limit,
                    # split_number=6,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True)
                ))
        )

        bar2 = (
            Bar()
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(
                series_name="离散度所处历史分位",
                yaxis_index=1,
                y_axis=spread_quantile,
                gap="0%",
                label_opts=opts.LabelOpts(is_show=True, formatter="{c}%"))
        )

        bar.overlap(bar2)

        return bar


"=====================================================债券市场宏微观======================================================"


class TreasurySpreadIndex:
    def __init__(self, start_date='20080104', end_date='20300101'):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_treasury_yield WHERE TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.data = data

    def draw_picture_treasury_spread(self):
        df = self.data[['trade_date', 'ytm_10y', 'usa_ytm_10y']].dropna()
        df['diff'] = df['ytm_10y'] - df['usa_ytm_10y']

        line = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="债券市场宏观"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="单位：%",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside")]
            ).add_yaxis(
                series_name="中国国债收益率：10年",
                y_axis=df["ytm_10y"].round(3).tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            ).add_yaxis(
                series_name="美国国债收益率：10年",
                y_axis=df["usa_ytm_10y"].round(3).tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            ).add_yaxis(
                series_name="中美国债利差：中国-美国",
                is_smooth=True,
                y_axis=df["diff"].round(3).tolist(),
                is_symbol_show=False,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False)
            )
        )

        return line

    def draw_picture_treasury_yield(self, date, compare_date=None):
        data = self.data[['trade_date', 'ytm_6m', 'ytm_1y', 'ytm_2y', 'ytm_3y', 'ytm_5y', 'ytm_7y',
                          'ytm_10y', 'ytm_15y', 'ytm_20y', 'ytm_30y']].set_index('trade_date')
        if compare_date is None:
            df = data.loc[date]
            df.index.name = 'duration'
            df = df.to_frame('yield').reset_index()
            df['duration'] = df['duration'].apply(lambda x: x.split('_')[-1].upper())

            line = (
                Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
                .add_xaxis(
                    xaxis_data=df['duration'].tolist())
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="债券市场微观"),
                    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                    legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                    yaxis_opts=opts.AxisOpts(
                        type_="value",
                        name="单位：%",
                        min_=1,
                        axistick_opts=opts.AxisTickOpts(is_show=True),
                        splitline_opts=opts.SplitLineOpts(is_show=True),
                    ),
                    xaxis_opts=opts.AxisOpts(
                        type_="category",
                        axistick_opts=opts.AxisTickOpts(is_show=True)),
                ).add_yaxis(
                    series_name="国债到期收益率",
                    y_axis=df['yield'].tolist(),
                    linestyle_opts=opts.LineStyleOpts(width=1.8),
                    label_opts=opts.LabelOpts(is_show=False)
                )
            )
        else:
            df = data.loc[[date, compare_date]].T.reset_index()
            df.rename(columns={"index": "duration"}, inplace=True)
            df['duration'] = df['duration'].apply(lambda x: x.split('_')[-1].upper())
            df['delta'] = (100 * (df[date] - df[compare_date])).round(2)

            max_limit = np.round(df['delta'].abs().max()) + 1

            line = (
                Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
                .add_xaxis(
                    xaxis_data=df['duration'].tolist())
                .extend_axis(
                    yaxis=opts.AxisOpts(
                        type_="value",
                        name="单位：BP",
                        min_=-max_limit,
                        max_=max_limit,
                        axistick_opts=opts.AxisTickOpts(is_show=True),
                        splitline_opts=opts.SplitLineOpts(is_show=False))
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="债券市场微观"),
                    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                    legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%'),
                    yaxis_opts=opts.AxisOpts(
                        type_="value",
                        name="单位：%",
                        min_=1,
                        axistick_opts=opts.AxisTickOpts(is_show=True),
                        splitline_opts=opts.SplitLineOpts(is_show=True),
                    ),
                    xaxis_opts=opts.AxisOpts(
                        type_="category",
                        axistick_opts=opts.AxisTickOpts(is_show=True)),
                ).add_yaxis(
                    series_name="国债到期收益率: {}".format(date),
                    y_axis=df[date].tolist(),
                    linestyle_opts=opts.LineStyleOpts(width=1.8),
                    label_opts=opts.LabelOpts(is_show=False)
                ).add_yaxis(
                    series_name="国债到期收益率: {}".format(compare_date),
                    y_axis=df[compare_date].tolist(),
                    linestyle_opts=opts.LineStyleOpts(width=1.8),
                    label_opts=opts.LabelOpts(is_show=False)
                )
            )

            bar = (
                Bar()
                .add_xaxis(
                    xaxis_data=df['duration'].tolist())
                .add_yaxis(
                    series_name='变动',
                    y_axis=df['delta'].tolist(),
                    label_opts=opts.LabelOpts(is_show=True),
                    bar_width="50%",
                    yaxis_index=1,
                    z=0,
                    color='orange'
                ))

            line.overlap(bar)

        return line

    def draw_picture_different_treasury(self):
        df = self.data[['trade_date', 'ytm_6m', 'ytm_1y', 'ytm_2y', 'ytm_3y', 'ytm_5y', 'ytm_10y']].set_index(
            'trade_date').dropna()

        line = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df.index.tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="债券市场宏观"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="单位：%",
                    min_=1,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside")]
            ))

        for col in df.columns.tolist():
            if col in ['ytm_1y', 'ytm_5y', 'ytm_10y']:
                line.add_yaxis(
                    series_name=col.upper(),
                    y_axis=df[col].round(3).tolist(),
                    is_symbol_show=False,
                    is_smooth=True,
                    linestyle_opts=opts.LineStyleOpts(width=1.8),
                    label_opts=opts.LabelOpts(is_show=False)
                )
            else:
                line.add_yaxis(
                    series_name=col.upper(),
                    y_axis=df[col].round(3).tolist(),
                    is_symbol_show=False,
                    is_smooth=True,
                    linestyle_opts=opts.LineStyleOpts(width=1.8),
                    label_opts=opts.LabelOpts(is_show=False),
                    is_selected=False
                )

        return line


class BondTradingIndex:
    def __init__(self, start_date='20210101', end_date='20210625'):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_bond_trading WHERE TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.data = data

    def draw_picture(self):
        df = self.data[['trade_date', 'R001', 'R007', 'bank_repo']].dropna()

        bar = (
            Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WALDEN))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="单位：亿元",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="隔夜回购成交量"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_top='5%'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="单位：亿元",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    # axislabel_opts={"rotate": 90},
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside")]
            ).add_yaxis(
                series_name='R001',
                stack="stack1",
                y_axis=df['R001'].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                bar_width="50%",
                z=0
            ).add_yaxis(
                series_name='R007',
                stack="stack1",
                y_axis=df['R007'].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                bar_width="50%",
                z=0
            )
        )

        line = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="质押式回购成交量",
                y_axis=df["bank_repo"].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=3),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )

        bar.overlap(line)

        return bar


"=====================================================期货市场宏微观======================================================"


class FutureMarketIndex:
    def __init__(self):
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_future_market_data"
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))

        self.price_data = pd.pivot_table(data, index='trade_date', columns='index_name', values='CLOSE').sort_index()
        self.volume_data = pd.pivot_table(data, index='trade_date', columns='index_name', values='VOLUME').sort_index()
        self.oi_data = pd.pivot_table(data, index='trade_date', columns='index_name', values='OI_INDEX').sort_index()

    def draw_picture_summary(self, start_date='20210401'):
        df = pd.merge(self.volume_data['CCFI.WI'].to_frame('volume'), self.oi_data['CCFI.WI'].to_frame('oi'),
                      left_index=True, right_index=True)
        df = df[df.index >= start_date]
        df = (df / 10000.).round(2).reset_index()

        bar = (
            Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="单位：万手",
                    min_=(df['oi'].min() // 500) * 500,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="商品市场成交量&持仓量"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_top='5%'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="单位：万手",
                    min_=(df['volume'].min() // 500) * 500,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    # axislabel_opts={"rotate": 90},
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
            ).add_yaxis(
                series_name='成交量',
                y_axis=df['volume'].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                bar_width="80%",
                z=0
            )
        )

        line = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="持仓量(右轴)",
                y_axis=df["oi"].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=2),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )

        bar.overlap(line)

        return bar

    def draw_picture_single_future(self, index_name, start_date='20210401'):
        df = pd.merge(self.volume_data[index_name].to_frame('volume'), self.oi_data[index_name].to_frame('oi'),
                      left_index=True, right_index=True)
        df = df[df.index >= start_date]
        df = (df / 10000.).round(2).reset_index()

        bar = (
            Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WALDEN))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="单位：万手",
                    min_=(df['oi'].min() // 50) * 50,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="单个商品成交量&持仓量"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_top='5%'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="单位：万手",
                    min_=(df['volume'].min() // 50) * 50,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    # axislabel_opts={"rotate": 90},
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
            ).add_yaxis(
                series_name='成交量',
                y_axis=df['volume'].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                bar_width="80%",
                z=0
            )
        )

        line = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="持仓量(右轴)",
                y_axis=df["oi"].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=2),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )

        bar.overlap(line)

        return bar

    def draw_picture_index(self, start_date='20200102'):
        df = self.price_data[self.price_data.index >= start_date]
        df = df.div(df.iloc[0]).round(4)
        df = df[[x for x in df.columns if x != 'CCFI.WI']]

        name_dict = {"APFI.WI": "农副产品", "CIFI.WI": "化工", "CRFI.WI": "谷物", "ENFI.WI": "能源", "JJRI.WI": "煤焦钢矿",
                     "NFFI.WI": "有色", "NMBM.WI": "非金属建材", "NMFI.WI": "贵金属",
                     "OOFI.WI": "油脂油料", "SOFI.WI": "软商品"}

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.MACARONS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="商品指数走势"),
            legend_opts=opts.LegendOpts(legend_icon='roundRect', pos_top='5%'),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                min_=0.5,
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")],
        ).add_xaxis(
            xaxis_data=df.index.tolist()
        )

        for name in df.columns:
            line.add_yaxis(
                series_name=name_dict[name],
                is_smooth=True,
                y_axis=df[name].round(4).tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(width=1.2),
            )

        return line

    def draw_picture_vol(self, start_date='20200102'):
        df = self.price_data.pct_change().dropna().rolling(20).std().dropna()
        df = df[df.index >= start_date]
        df = (100 * df).round(2)
        df = df[[x for x in df.columns if x != 'CCFI.WI']]

        name_dict = {"APFI.WI": "农副产品", "CIFI.WI": "化工", "CRFI.WI": "谷物", "ENFI.WI": "能源", "JJRI.WI": "煤焦钢矿",
                     "NFFI.WI": "有色", "NMBM.WI": "非金属建材", "NMFI.WI": "贵金属",
                     "OOFI.WI": "油脂油料", "SOFI.WI": "软商品"}

        line = Line(
            init_opts=opts.InitOpts(
                width='1200px',
                height='600px',
                theme=ThemeType.MACARONS
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="商品指数波动率走势"),
            legend_opts=opts.LegendOpts(legend_icon='roundRect', pos_top='5%'),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axistick_opts=opts.AxisTickOpts(is_show=True, is_align_with_label=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")],
        ).add_xaxis(
            xaxis_data=df.index.tolist()
        )

        for name in df.columns:
            line.add_yaxis(
                series_name=name_dict[name],
                is_smooth=True,
                y_axis=df[name].round(4).tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(width=1.2),
            )

        return line


class FuturePriceSpread:
    def __init__(self, start_date='20150101'):
        self.start_date = start_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM mac_future_price WHERE TRADE_DATE >= {}".format(self.start_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data = data.set_index('trade_date')
        # 价差公式
        data['spread_a'] = data['RB.SHF'] - 1.55 * data['I.DCE'] - 0.45 * data['J.DCE']
        data['spread_b'] = 1.55 * data['I.DCE'] - 0.45 * data['J.DCE']
        data['spread_0'] = data['HC.SHF'] - data['RB.SHF']
        data['spread_1'] = data['JM.DCE'] - data['J.DCE']
        data['spread_2'] = 0.2 * data['Y.DCE'] - 0.8 * data['M.DCE']
        data['spread_3'] = data['Y.DCE'] - data['P.DCE']
        data['spread_4'] = 3 * data['MA.CZC'] - data['PP.DCE']
        data['spread_5'] = data['CU.SHF'] - data['ZN.SHF']
        data = data.filter(regex="spread_*")

        self.name_list = ["热卷螺纹价差", "焦煤焦炭价差", "豆油豆粕价差", "豆油棕榈油价差", "甲醇聚丙烯价差", "铜锌价差"]
        self.data = data

    def draw_picture_one(self):
        df = self.data[['spread_1', 'spread_2']].reset_index()

        line1 = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="商品期货价差"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside")
                ]
            ).add_yaxis(
                series_name="螺纹铁矿焦炭价差",
                y_axis=df["spread_1"].tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False)
            )
        )

        line2 = (
            Line()
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .add_yaxis(
                series_name="铁矿焦炭价差(右轴)",
                is_smooth=True,
                y_axis=df["spread_2"].tolist(),
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(width=1.8),
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index=1
            )
        )
        line1.overlap(line2)

        return line1

    def draw_picture_common(self, col_name):
        col = "spread_" + str(self.name_list.index(col_name))
        df = self.data[[col]].reset_index()

        line = (
            Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
            .add_xaxis(
                xaxis_data=df['trade_date'].tolist())
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=False))
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="商品期货价差"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                legend_opts=opts.LegendOpts(pos_right="center", pos_top='5%', legend_icon='circle'),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_show=True)),
                datazoom_opts=[
                    opts.DataZoomOpts(range_start=0, range_end=100),
                    opts.DataZoomOpts(type_="inside")
                ]
            ).add_yaxis(
                series_name=col_name,
                y_axis=df[col].tolist(),
                is_symbol_show=False,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=2),
                label_opts=opts.LabelOpts(is_show=False)
            )
        )

        return line


if __name__ == '__main__':
    # pic = CurrencyIndex(end_date='20210801').draw_picture_M1_M2(compare_index='HS300')
    # CurrencyShiborIndex(start_date='20210101', end_date='20210517').draw_picture_shibor()
    # CreditIndex(frequency='week').draw_picture_indu()
    # InflationIndex().draw_picture()
    # EconomyIncreaseIndex(end_date='20210517').draw_picture_excavator(compare_index='HS300')
    # RatesAndPriceIndex(end_date='20210610').draw_picture_export()
    # StockMarketPE(window=5, index_list=['HS300', 'ZZ500'], start_date='20140101').draw_picture_pe_ttm()
    StockValuation(start_date='20050101', end_date='20211213', mode='EPS').draw_picture()
    # StockValueRotation().draw_picture()
    # pic = StockBondRotation(index_name='HS300', start_date='20150101').draw_picture_premium()
    # pic = StockIndexDiff(start_date='20190101').draw_picture_index_diff()
    # pic = StockCashFlowIndex(start_date='20200101').draw_picture_cash_flow()
    # pic = StockTradingIndex().draw_picture_amt_summary()
    # pic = StockIndexTrading().draw_picture_index_trendency('300', '20190101')
    # StockCrossSectionVolIndex().draw_picture_vol_compare('HS300', 'OTHER')
    # StockTimeSeriesVolIndex().draw_picture_vol('HS300')
    # pic = StockTradingCrIndex('20190101', '20210423').draw_cr_picture()
    # pic = StockStyleFactor('20210501', '20210826').draw_picture_cum_return()
    # StockStyleMomentum('20200101', '20210517').draw_picture_quantile()
    # StockStyleSpread('20200101', '20210517').draw_picture_quantile()
    # TreasurySpreadIndex('20200101', '20210517').draw_picture_different_treasury()
    # pic = BondTradingIndex('20200123', '20200615').draw_picture()
    # FutureMarketIndex().draw_picture_vol(start_date='20200102')
    # FutureMarketIndex().draw_picture_single_future(index_name='NMBM.WI')

    # pic.render('D:\\kevin\\123.html')
