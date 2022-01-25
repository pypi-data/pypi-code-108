#!/usr/bin/python
#coding:utf-8
import numpy as np
import pyecharts.options as opts
from pyecharts.charts import Bar, Line, HeatMap, Timeline
from pyecharts.globals import ThemeType


def draw_summary_bar(df):
    colors = ['#5793f3', '#d14a61']

    x_data = df.index.tolist()
    factor_exposure = df['factor_exposure'].tolist()
    return_attr = df['return_attr'].tolist()

    exposure_limit = int(np.max(np.abs(factor_exposure)) + 1)
    return_limit = int(np.max(np.abs(return_attr)) / 5 + 1) * 5

    bar = (
        Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
        .add_xaxis(
            xaxis_data=x_data)
        .add_yaxis(
            series_name='因子暴露',
            y_axis=factor_exposure,
            label_opts=opts.LabelOpts(is_show=False),
            color=colors[0])
        .extend_axis(
            yaxis=opts.AxisOpts(
                name="收益贡献",
                type_="value",
                min_=-return_limit,
                max_=return_limit,
                split_number=6,
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                axistick_opts=opts.AxisTickOpts(is_show=True)))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="风格暴露及收益贡献"),
            tooltip_opts=opts.TooltipOpts(
                is_show=True, trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_left="center", pos_top="bottom"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axislabel_opts={"interval": "0"},
                axistick_opts=opts.AxisTickOpts(is_show=True),
                axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="shadow")),
            yaxis_opts=opts.AxisOpts(
                name="因子暴露",
                type_="value",
                min_=-exposure_limit,
                max_=exposure_limit,
                split_number=6,
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ))
    )

    bar2 = (
        Bar()
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="收益贡献",
            yaxis_index=1,
            y_axis=return_attr,
            label_opts=opts.LabelOpts(is_show=False))
    )

    return bar.overlap(bar2)


def draw_summary_bar_style(df):
    colors = ['#5793f3', '#d14a61']

    x_data = df.index.tolist()
    factor_exposure = df['factor_exposure'].tolist()
    return_attr = df['return_attr'].tolist()

    exposure_limit = int(np.max(np.abs(factor_exposure)) + 1)
    return_limit = int(np.max(np.abs(return_attr)) / 5 + 1) * 5

    bar = (
        Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
        .add_xaxis(
            xaxis_data=x_data)
        .add_yaxis(
            series_name='因子暴露',
            y_axis=factor_exposure,
            label_opts=opts.LabelOpts(is_show=False),
            color=colors[0])
        .extend_axis(
            yaxis=opts.AxisOpts(
                name="收益贡献",
                type_="value",
                min_=-return_limit,
                max_=return_limit,
                split_number=6,
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                axistick_opts=opts.AxisTickOpts(is_show=True)))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="风格暴露及收益贡献"),
            tooltip_opts=opts.TooltipOpts(
                is_show=True, trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_left="center", pos_top="bottom"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axislabel_opts={"interval": "0"},
                axistick_opts=opts.AxisTickOpts(is_show=True),
                axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="shadow")),
            yaxis_opts=opts.AxisOpts(
                name="因子暴露",
                type_="value",
                min_=-exposure_limit,
                max_=exposure_limit,
                split_number=6,
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ))
    )

    bar2 = (
        Bar()
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="收益贡献",
            yaxis_index=1,
            y_axis=return_attr,
            label_opts=opts.LabelOpts(is_show=False))
    )

    return bar.overlap(bar2)


def draw_area_line(df, title):
    x_data = df.index.tolist()

    line = (
        Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
        .add_xaxis(
            xaxis_data=x_data)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_left="center", pos_top="bottom", legend_icon='rect'),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                max_=100,
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False,
                                     axistick_opts=opts.AxisTickOpts(is_show=True),),
        )
    )

    for style_factor in df.columns.tolist():
        line.add_yaxis(
            series_name=style_factor,
            stack="总量",
            y_axis=df[style_factor].tolist(),
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )

    return line


def draw_area_bar(df, title):
    x_data = df.index.tolist()

    bar = (
        Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.WESTEROS))
        .add_xaxis(
            xaxis_data=x_data)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_left="center", pos_top="bottom"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", axistick_opts=opts.AxisTickOpts(is_show=True)),
        )
    )

    for style_factor in df.columns.tolist():
        bar.add_yaxis(
            series_name=style_factor,
            stack="stack1",
            y_axis=df[style_factor].tolist(),
            label_opts=opts.LabelOpts(is_show=False),
            bar_width="60%"
        )

    return bar


def draw_heatmap(df, title, min_value=-4, max_value=4):
    value = [[i, j, df.values[i, j]] for i in range(df.shape[0]) for j in range(df.shape[1])]

    picture = (
        HeatMap(init_opts=opts.InitOpts(width='1200px', height='600px'))
        .add_xaxis(df.index.tolist())
        .add_yaxis(
            "风格暴露",
            df.columns.tolist(),
            value=value,
            label_opts=opts.LabelOpts(is_show=True, position='inside')
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            visualmap_opts=opts.VisualMapOpts(min_=min_value, max_=max_value, orient="horizontal", pos_left="center")
        )
    )

    return picture


def draw_brinson_area_bar(df):
    x_data = [x[:4] + '-' + x[4:6] for x in df.index.tolist()]

    max_return = np.ceil(df.abs().max().max() * 1.2)

    bar = (
        Bar(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.MACARONS))
        .add_xaxis(
            xaxis_data=x_data)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Brinson时序归因图"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_left="center", pos_top="bottom"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                max_=max_return,
                min_=-max_return,
                axistick_opts=opts.AxisTickOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", axistick_opts=opts.AxisTickOpts(is_show=True)),
        ).extend_axis(
            yaxis=opts.AxisOpts(
                type_="value",
                max_=max_return,
                min_=-max_return,
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                axistick_opts=opts.AxisTickOpts(is_show=True)))
    )

    name_dict = {"asset_allo": "大类资产配置收益", "sector_allo": "行业配置收益",
                 "equity_selection": "行业选股收益", "trading": "交易收益"}

    for name in df.columns[1:].tolist():
        bar.add_yaxis(
            series_name=name_dict[name],
            stack="stack1",
            y_axis=df[name].tolist(),
            label_opts=opts.LabelOpts(is_show=False),
            bar_width="60%",
            z=0
        )

    line = (
        Line()
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="超额收益",
            yaxis_index=1,
            y_axis=df['active_return'],
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=True))
    )

    return bar.overlap(line)


def draw_heatmap_brinson(df):
    value = [[i, j, df.values[i, j]] for i in range(df.shape[0]) for j in range(df.shape[1])]

    value_max = df.max().max()
    value_min = df.min().min()

    picture = (
        HeatMap(init_opts=opts.InitOpts(width='1000px', height='800px'))
        .add_xaxis(df.index.tolist())
        .add_yaxis(
            "行业配置收益",
            df.columns.tolist(),
            value=value,
            label_opts=opts.LabelOpts(is_show=True, position='inside')
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="行业配置收益时序图"),
            visualmap_opts=opts.VisualMapOpts(min_=value_min, max_=value_max, orient="horizontal", pos_left="center")
        )
    )

    return picture


def draw_weight_compare_brinson(df):
    x_data = [x[:4] + '-' + x[4:6] for x in df.index.tolist()]

    line = (
        Line(init_opts=opts.InitOpts(width='1200px', height='600px', theme=ThemeType.MACARONS))
        .add_xaxis(
            xaxis_data=x_data)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="组合权益权重走势"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_left="center", pos_top="bottom"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                min_=60,
                axistick_opts=opts.AxisTickOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            )
        ).add_yaxis(
            series_name='基金权益权重',
            y_axis=df['portfolio_weight'].tolist(),
            label_opts=opts.LabelOpts(is_show=True),
            linestyle_opts=opts.LineStyleOpts(width=2)
        ).add_yaxis(
            series_name='基准权益权重',
            y_axis=df['benchmark_weight'].tolist(),
            label_opts=opts.LabelOpts(is_show=True),
            linestyle_opts=opts.LineStyleOpts(width=2)
        )
    )

    return line


def draw_active_exposure_series(df, title):
    bar = Bar(
        init_opts=opts.InitOpts(
            page_title=title,
            width='1200px',
            height='600px',
            theme=ThemeType.WESTEROS
        )
    ).set_global_opts(
        title_opts=opts.TitleOpts(title=title),
        legend_opts=opts.LegendOpts(legend_icon='pin', pos_top='5%'),
        xaxis_opts=opts.AxisOpts(
            type_="category",
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
        xaxis_data=df.index.tolist()
    )

    for name in df.columns:
        bar.add_yaxis(
            series_name=name,
            y_axis=df[name].round(3).tolist(),
            label_opts=opts.LabelOpts(is_show=False),
            gap="0%"
        )

    return bar


def draw_timeline_bar(df, min_height=600):
    num = int(df.gt(0.01).sum(axis=1).mean())
    tl = Timeline(init_opts=opts.InitOpts(width='1200px', height='{}px'.format(max(25 * num, min_height))))

    for i in df.index.tolist():
        tmp = df.loc[i].dropna()
        tmp = tmp[tmp >= 0.01].sort_values()
        bar = (
            Bar()
            .add_xaxis(tmp.index.tolist())
            .add_yaxis(
                "持仓权重",
                (tmp * 100).round(2).values.tolist(),
                itemstyle_opts=opts.ItemStyleOpts(color="#37a2da"),
                label_opts=opts.LabelOpts(is_show=False))
            .reversal_axis()
            .set_global_opts(
                title_opts=opts.TitleOpts("截面持股权重 (时间点: {})".format(i)),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                    splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.3)))
            )
        )
        tl.add(bar, "{}年{}月".format(i[:4], i[4:6]))

    return tl