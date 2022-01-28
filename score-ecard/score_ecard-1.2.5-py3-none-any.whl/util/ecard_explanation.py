# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2022/1/7 15:46
Desc:
'''

import numpy as np
import pandas as pd
import matplotlib as mplt
from matplotlib import pyplot as pl
import seaborn as sns
from pyecharts.charts import Bar, Line, Page, Grid
from pyecharts import options as opts

def summary_explanation(score_card, max_display=15, title=None, row_width=12, row_height=0.6, save_path=None):
    '''
    模型结构解读【评分卡构建结构 to 评分】:
        1.模型的特征构成及重要度排序(topN)，颜色越深，重要度越高；
        2.各子图宽度表示特征对模型的贡献度，对最终得分的加成，最终得分可理解为个子score_相加；
        3.各子图散点密集程度分布情况表征因子对于不同风险区间的描述精度，亦可理解为把握度高低；
    :param score_card:
    :param max_display:
    :param title:
    :param row_width:
    :param row_height:
    :param save_path:
    :return:
    '''
    # data
    df_importance = get_importance(score_card)
    size_ = min(max_display, len(df_importance))
    data = score_card.merge(pd.DataFrame(df_importance[:size_], columns=['importance_']), how='inner', left_on='field_',
                            right_index=True
                            ).sort_values('importance_', ascending=False)

    # color
    g7_color = ['#5100ad', '#5100ad', '#8d4fe8', '#a577e9', '#b490ea', '#c3a8eb', '#c9bbdd', '#dad4e3']
    g7_colormap = mplt.colors.LinearSegmentedColormap.from_list('cmap', g7_color[::-1], 256)
    g7_color_palette = sns.color_palette("Purples", n_colors=int(size_ * 1.2))

    # violinplot
    custom_params = {"axes.spines.left": False, "axes.spines.right": False, "axes.spines.top": False}
    sns.set_theme(style="white", rc=custom_params, palette=None)
    sns.violinplot(data=data, x="score_", y="field_", palette=g7_color_palette[::-1],
                   inner="points", orient="h", scale="width")

    # chart_init
    fig = pl.gcf().set_size_inches(row_width, size_ * row_height + 1.5)
    pl.axvline(x=0, color="#999999", zorder=-1)
    pl.suptitle(title, x=0.09, y=0.92, fontsize=16, color='#5100ad')
    pl.ylabel('')
    # pl.rcParams['font.sans-serif']=['SimHei']
    # pl.rcParams['axes.unicode_minus']=False

    # colorbar
    m = mplt.cm.ScalarMappable(cmap=g7_colormap)
    m.set_array([0, 1])
    cb = pl.colorbar(m, ticks=[0, 1], aspect=1000)
    cb.set_ticklabels(['Low', 'High'])
    cb.set_label('Feature Importance', size=12, labelpad=0)
    cb.ax.tick_params(labelsize=11, length=0)
    cb.set_alpha(1)
    cb.outline.set_visible(False)
    bbox = cb.ax.get_window_extent().transformed(pl.gcf().dpi_scale_trans.inverted())
    cb.ax.set_aspect((bbox.height - 0.9) * 20)
    if save_path is not None:
        pl.savefig(save_path, bbox_inches='tight')
        pl.close()

def sample_explanation(score_card, max_display=15, title=None, row_width=12, row_height=0.5, save_path=None):
    '''
    样本结构成分-训练集样本构成【评分卡样本构成 for 样本分布】:
        1.模型的样本分布，颜色越深，样本集中度越高，对于模型的贡献权重越高；
        2.各子图宽度表示特征对模型的贡献度，对最终得分的加成，最终得分可理解为各子score_相加；
        3.各子图密集度较高区域(颜色较深)表征该因子对于风险评估的主要作用区间，即因子作用的主区域；
    :param score_card:
    :param max_display:
    :param title:
    :param row_width:
    :param row_height:
    :param save_path:
    :return:
    '''
    # data
    df_importance = get_importance(score_card)
    size_ = min(max_display, len(df_importance))
    df_importance = df_importance[:size_]
    data = score_card.merge(pd.DataFrame(df_importance, columns=['importance_']), how='inner', left_on='field_',
                            right_index=True
                            ).sort_values('importance_', ascending=False)

    # color
    g7_color = ['#5100ad', '#5100ad', '#8d4fe8', '#a577e9', '#b490ea', '#c3a8eb', '#c9bbdd', '#dad4e3']
    g7_colormap = mplt.colors.LinearSegmentedColormap.from_list('cmap', g7_color[::-1], 256)

    # chart_init
    fig = pl.gcf().set_size_inches(row_width, size_ * row_height + 1.5)
    pl.axvline(x=0, color="#999999", zorder=-1)
    pl.suptitle(title, x=0.09, y=0.92, fontsize=16, color='#5100ad')
    pl.xlabel('score_')
    ax = pl.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    # scatter
    yticks_idx = []
    yticks_name = []
    feature_order = df_importance.index[::-1]
    for pos, icol_ in enumerate(feature_order):
        raw_data = data[data.field_ == icol_]
        if 'size_' in raw_data.columns:
            raw_data['size_'] = (raw_data['size_'] / raw_data['size_'].sum()).apply(lambda x: int(np.ceil(x)))
            idata = raw_data.apply(lambda x: [x['score_'] for i in range(x['size_'])], axis=1).sum()
            idata = np.array(idata)
        else:
            idata = raw_data.score_.values
        x, y = data_adapter(idata, row_height)
        x_idx = np.argsort(abs(y))
        cweight = [dict(zip(x[x_idx], abs(y[x_idx]))).get(i, 1) for i in x]
        pl.scatter(x=x, y=pos + y, s=20, alpha=1, cmap=g7_colormap, c=cweight, rasterized=len(x) > 10000)
        yticks_idx.append(pos)
        yticks_name.append(icol_)
    pl.yticks(yticks_idx, yticks_name, fontsize=10)

    # colorbar
    m = mplt.cm.ScalarMappable(cmap=g7_colormap)
    m.set_array([0, 1])
    cb = pl.colorbar(m, ticks=[0, 1], aspect=1000)
    cb.set_ticklabels(['Low', 'High'])
    cb.set_label('Sample Weight', size=12, labelpad=0)
    cb.ax.tick_params(labelsize=11, length=0)
    cb.set_alpha(1)
    cb.outline.set_visible(False)
    bbox = cb.ax.get_window_extent().transformed(pl.gcf().dpi_scale_trans.inverted())
    cb.ax.set_aspect((bbox.height - 0.9) * 20)

    if save_path is not None:
        pl.savefig(save_path, bbox_inches='tight')
        pl.close()


def factor_trend(score_card, max_display=15, title='因子一致性分析', subtitle='风险走势', row_width=14, row_height=14,
                 save_path=None):
    '''
    因子一致性-单调趋同【因子对于模型的功效趋势一致，对模型的单调贡献度】:
        1.因子的关联性分析，颜色越深，因子风险的趋势正向一致，颜色越浅，因子风险的趋势逆相关，颜色居中，则无关联，分布模式不同；
        2.因子对于模型的作用加成一致性
    :param score_card:
    :param max_display:
    :param title:
    :param subtitle:
    :param row_width:
    :param row_height:
    :param save_path:
    :return:
    '''
    # data
    df_importance = get_importance(score_card)
    size_ = min(max_display, len(df_importance))
    df_importance = df_importance[:size_]
    _card = score_card.merge(pd.DataFrame(df_importance, columns=['importance_']), how='inner', left_on='field_',
                             right_index=True
                             ).sort_values('importance_', ascending=False)
    _card['score_ext'] = _card.apply(lambda x: np.array([x['score_'] for i in range(x['size_'])]), axis=1)
    df_data = _card.groupby('field_').apply(
        lambda x: np.array(x["score_ext"])[np.argsort(list(x["bins_"]))]
    ).apply(lambda x: [j for i in x for j in i])
    df_data = pd.DataFrame(df_data.values.tolist(), index=df_data.index).T
    df_data.dropna(axis=1, inplace=True)
    df_corr = df_data.corr()

    # color
    g7_color_palette = sns.color_palette("binary", n_colors=size_)[::-1]
    color_dict = dict(zip(df_importance.index, g7_color_palette))
    color_list = [color_dict.get(i) for i in df_data.columns]

    # clustermap
    g = sns.clustermap(df_corr, center=0, cmap="Purples",
                       row_colors=color_list,
                       dendrogram_ratio=(.1, .15),
                       cbar_pos=(.01, .32, .03, .2),
                       linewidths=.6, figsize=(row_width, row_height),
                       )
    g.ax_row_dendrogram.remove()
    g.figure.text(0.03, 1.0, title, fontsize=14, fontfamily='SimHei', fontweight='bold')
    g.figure.text(0.03, 0.98, subtitle, fontsize=12, fontfamily='SimHei')
    ax = g.ax_heatmap
    ax.set_xlabel("")
    ax.set_ylabel("")

    if save_path is not None:
        pl.savefig(save_path, bbox_inches='tight')
        pl.close()


def single_factor_report(df_top, df_bottom, title_name='特征1风险分布', subtitle_name='tezheng1', color_list=['#5100ad']):
    '''
    :param df_top: 因子评分分布
    :param df_bottom: 因子对应样本数分布
    :param title_name:
    :param subtitle_name:
    :return:
        grid = factor_report(df_top,df_bottom)
        grid.render("tmp.html")
    '''

    def plot_base_line(df: pd.DataFrame, title_name='', subtitle_name='', xaxis_name='', yaxis_name='',
                       is_show_label=False, _interval=20):
        if isinstance(df, pd.Series):
            df = pd.DataFrame(df)
        _data = df.copy()
        _data.index = [str(i) for i in _data.index]
        c1 = Line({'bg_color': 'white'})
        c1.add_xaxis(_data.index.tolist())
        for i, icol in enumerate(_data.columns):
            c1.add_yaxis('', _data[icol].values.tolist(), is_connect_nones=True)
        c1.set_series_opts(label_opts=opts.LabelOpts(is_show=is_show_label))
        c1.set_global_opts(
            title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            datazoom_opts=opts.DataZoomOpts(is_show=True, xaxis_index=[0, 1], range_start=0, range_end=100),
            xaxis_opts=opts.AxisOpts(name=xaxis_name),
            yaxis_opts=opts.AxisOpts(name=yaxis_name,
                                     type_="value",
                                     is_scale=True,
                                     axislabel_opts=opts.LabelOpts(formatter="{value}"),
                                     splitline_opts=opts.SplitLineOpts(is_show=True,
                                                                       linestyle_opts=opts.LineStyleOpts(opacity=0.4)),
                                     )
        )
        c1.set_colors(color_list)
        return c1

    def plot_base_bar(df: pd.DataFrame, title_name='', subtitle_name='', xaxis_name='', yaxis_name='',
                      is_show_label=None):
        if isinstance(df, pd.Series):
            df = pd.DataFrame(df)
        _data = df.copy()
        _data.index = [str(i) for i in _data.index]
        if is_show_label is None:
            is_show_label = True if len(_data) < 8 else False
        c1 = Bar({'bg_color': 'white'})
        c1.add_xaxis(_data.index.tolist())
        for i, icol in enumerate(_data.columns):
            c1.add_yaxis('', _data[icol].values.tolist())
        c1.set_series_opts(label_opts=opts.LabelOpts(is_show=is_show_label))
        c1.set_global_opts(
            title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            xaxis_opts=opts.AxisOpts(name=xaxis_name),
            yaxis_opts=opts.AxisOpts(name=yaxis_name, type_="value", split_number=3),
            datazoom_opts=opts.DataZoomOpts(is_show=True, xaxis_index=[0, 1], range_start=0, range_end=100)
        )
        return c1

    line1 = plot_base_line(df_top, title_name=title_name, subtitle_name=subtitle_name, yaxis_name='score_')
    bar1 = plot_base_bar(df_bottom, yaxis_name='size_')
    grid = (
        Grid(init_opts=opts.InitOpts(width="800px", height="500px"))
            .add(line1, grid_opts=opts.GridOpts(pos_bottom="40%", pos_top="13%"))
            .add(bar1, grid_opts=opts.GridOpts(pos_top="70%"))
    )
    return grid

def model_factor_report(score_card, title='ecard', max_display=999, save_path=None):
    '''
    评分卡模型因子报告：【因子的评分规则详情】
        1.模型对于因子的认知程度(是否过拟合，是否欠拟合)
        2.因子表征样本的情况(样本是否有偏)
    :param score_card:
    :param title:
    :param max_display:
    :param save_path:
    :return:
    '''
    # data
    df_importance = get_importance(score_card)
    size_ = min(max_display, len(df_importance))
    df_importance = df_importance[:size_]
    page = Page(interval=5,page_title=title)
    for i, icol in enumerate(df_importance.index):
        _card = score_card[score_card.field_ == icol].sort_values('bins_').set_index('bins_')
        df_top = _card.score_.round(2)
        if 'size_' in _card.columns:
            df_bottom = _card.size_.astype(int)
        else:
            df_bottom = (df_top * 0 + 1).astype(int)
        chart_i = single_factor_report(df_top, df_bottom, title_name="{}. {}".format(i + 1, icol), subtitle_name='')
        page.add(chart_i)

    if save_path is not None:
        page.render("{}.html".format(save_path))
    else:
        return page.render_notebook()

def get_importance(score_card):
    df_card_info = score_card.groupby("field_").agg(
        {'size_': [("weights", lambda x: list(x))],
         'score_': [("values", lambda x: list(x))]

         }).droplevel(0, 1)
    get_weighted_std = lambda value_,weight_: np.average((value_-np.average(value_, weights=weight_))**2, weights=weight_)
    importance_ = df_card_info.apply(lambda x: get_weighted_std(x["values"], x["weights"]), axis=1)
    importance_ = (importance_/importance_.sum()).apply(lambda x:round(x,6))
    importance_ = importance_[importance_>0].sort_values(ascending=False)
    return importance_

def data_adapter(idata, row_height=0.5):
    inds = np.arange(len(idata))
    np.random.shuffle(inds)
    idata = idata[inds]
    N = len(idata)
    nbins = 100
    quant = np.round(nbins * (idata - np.min(idata)) / (np.max(idata) - np.min(idata) + 1e-8))
    inds = np.argsort(quant + np.random.randn(N) * 1e-6)
    layer = 0
    last_bin = -1
    ys = np.zeros(N)
    for ind in inds:
        if quant[ind] != last_bin:
            layer = 0
        ys[ind] = np.ceil(layer / 2) * ((layer % 2) * 2 - 1)
        layer += 1
        last_bin = quant[ind]
    ys *= 0.9 * (row_height / np.max(ys + 1))
    return idata, ys
