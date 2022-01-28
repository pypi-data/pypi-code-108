"""
Zep风格因子模块
"""
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import pyecharts.options as opts
from pyecharts.charts import Line, Bar
from pyecharts.globals import ThemeType
import hbshare as hbs
from hbshare.quant.Kevin.rm_associated.config import engine_params, style_names, industry_names


class RiskFactorReturn:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
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
        sql_script = "SELECT * FROM factor_return where TRADE_DATE >= {} and TRADE_DATE <= {}".format(self.start_date,
                                                                                                      self.end_date)
        engine = create_engine(engine_params)
        factor_return = pd.read_sql(sql_script, engine)
        factor_return['trade_date'] = factor_return['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        factor_return = pd.pivot_table(
            factor_return, index='trade_date', columns='factor_name', values='factor_ret').sort_index()
        factor_return = factor_return[style_names + list(industry_names.values()) + ['country']]

        self.factor_return = factor_return

    def generate_trendency_line(self, title):
        factor_return = self.factor_return.copy()
        factor_return = factor_return.cumsum()[style_names] * 100
        cum_line = Line(
            init_opts=opts.InitOpts(
                page_title=title,
                width='1200px',
                height='600px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title=title),
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
        ).add_xaxis(
            xaxis_data=factor_return.index.tolist()
        )

        for style_factor in style_names:
            cum_line.add_yaxis(
                series_name=style_factor,
                is_smooth=True,
                y_axis=factor_return[style_factor].round(4).tolist(),
                label_opts=opts.LabelOpts(is_show=False)
            )

        html_content = cum_line.render_embed()
        print("%html {}".format(html_content))

    def generate_period_cumret_bar(self, title):
        factor_return = self.factor_return.copy()
        factor_return = (factor_return.sum()[style_names] * 100).round(2)

        bar = Bar(
            init_opts=opts.InitOpts(
                page_title=title,
                width='1200px',
                height='600px',
                theme=ThemeType.LIGHT
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            legend_opts=opts.LegendOpts(legend_icon='roundRect', pos_top='5%'),
            tooltip_opts=opts.TooltipOpts(
                is_show=True, trigger="axis", axis_pointer_type="cross"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts={"interval": "0"},
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
        ).add_xaxis(
            xaxis_data=["市值", "Beta", "动量", "盈利", "波动率", "成长", "估值", "杠杆", "流动性", "非线性市值"]
        ).add_yaxis(
            series_name='因子累计收益',
            y_axis=factor_return.values.tolist(),
            bar_width="60%"
        )

        html_content = bar.render_embed()
        print("%html {}".format(html_content))

    def generate_period_industry_bar(self, title):
        factor_return = self.factor_return.copy()
        industry = dict([val, key] for key, val in industry_names.items())
        df = (factor_return.sum().loc[list(industry.keys())] * 100).round(2)
        df.index = [industry[x] for x in df.index]
        df.sort_values(ascending=False, inplace=True)

        bar = Bar(
            init_opts=opts.InitOpts(
                page_title=title,
                width='1200px',
                height='600px',
                theme=ThemeType.LIGHT
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            legend_opts=opts.LegendOpts(legend_icon='roundRect', pos_top='5%'),
            tooltip_opts=opts.TooltipOpts(
                is_show=True, trigger="axis", axis_pointer_type="cross"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts={"interval": "0", "rotate": "90"},
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
        ).add_xaxis(
            xaxis_data=df.index.tolist()
        ).add_yaxis(
            series_name='行业因子累计收益',
            y_axis=df.values.tolist(),
            bar_width="60%"
        )

        html_content = bar.render_embed()
        print("%html {}".format(html_content))