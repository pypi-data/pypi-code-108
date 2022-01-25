"""
套利FOF回测模块
"""
import numpy as np
from MyUtil.data_loader import get_trading_day_list, get_fund_nav_from_sql
from MyUtil.util_func import cal_annual_return, cal_annual_volatility, cal_max_drawdown, cal_sharpe_ratio
import pandas as pd
import datetime


if __name__ == '__main__':
    s_date = '20200103'
    e_date = '20211126'

    f_dict = {
        "展弘稳进1号1期": "SE8723",
        "盛冠达股指套利3号": "SGS597",
        "稳博中睿6号": "SJB143"
    }

    date_list = get_trading_day_list(s_date, e_date, frequency='week')

    nav_df = get_fund_nav_from_sql(s_date, e_date, f_dict).reindex(date_list).fillna(method='ffill')

    mx_df = pd.read_excel('D:\\蒙玺竞起6号净值.xlsx', sheet_name=0)
    mx_df['trade_date'] = mx_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    mx_df.rename(columns={"nav": "蒙玺竞起6号"}, inplace=True)
    mx_df = mx_df.set_index('trade_date').reindex(date_list).dropna()

    nav_df = pd.concat([nav_df, mx_df], axis=1)
    return_df = nav_df.pct_change().fillna(0.)

    # 等权
    weight_df1 = pd.DataFrame(index=return_df.index, columns=return_df.columns)
    weight_df1.loc['20200103', :] = [1/3, 1/3, 1/3, 0]

    rbl_list = ['20201120']

    for i in range(1, len(return_df)):
        date = return_df.index[i]
        weight_df1.iloc[i, :] = weight_df1.iloc[i - 1, :] * (1 + return_df.iloc[i, :])
        if date in rbl_list:
            weight_df1.loc[date] = weight_df1.loc[date].mean()

    port_nav1 = weight_df1.sum(axis=1)

    # 额度加权
    weight_df2 = pd.DataFrame(index=return_df.index, columns=return_df.columns)
    weight_df2.loc['20200103', :] = [4/9, 1/9, 4/9, 0]
    weight_df2.loc['20201120', :] = [4/11, 1/11, 4/11, 2/11]

    rbl_list = ['20201120']

    for i in range(1, len(return_df)):
        date = return_df.index[i]
        weight_df2.iloc[i, :] = weight_df2.iloc[i - 1, :] * (1 + return_df.iloc[i, :])
        if date in rbl_list:
            weight_df2.loc[date] = [weight_df2.loc[date].sum() * x for x in [4/11, 1/11, 4/11, 2/11]]

    port_nav2 = weight_df2.sum(axis=1)

    # 净值
    port_nav = pd.concat([port_nav1.to_frame('等权组合'), port_nav2.to_frame('最大额度组合')], axis=1)
    # 累计收益率
    cum_return = port_nav.iloc[-1] - 1
    # 年化收益
    an_return = port_nav.pct_change().dropna(how='all').apply(cal_annual_return, axis=0)
    # 年化波动
    an_vol = port_nav.pct_change().dropna(how='all').apply(cal_annual_volatility, axis=0)
    # 最大回撤
    max_draw = port_nav.apply(cal_max_drawdown, axis=0)
    draw_series = port_nav.apply(lambda x: x / x.cummax() - 1)
    # sharpe
    sharpe = port_nav.pct_change().dropna(how='all').apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
    # # sortino
    down_std = port_nav.pct_change().dropna(how='all').apply(lambda x: x[x < 0].std() * np.sqrt(52), axis=0)
    sortino = an_return / down_std
    # calmar
    calmar = an_return / max_draw.abs()
    # 胜率
    win_ratio = port_nav.pct_change().dropna(how='all').apply(lambda x: x.gt(0).sum() / len(x), axis=0)
    # 平均损益比
    win_lose = port_nav.pct_change().dropna(how='all').apply(lambda x: x[x > 0].mean() / x[x < 0].abs().mean(), axis=0)
    # 年度累计
    ret_20 = port_nav.loc['20201231'] - 1
    ret_21 = port_nav.iloc[-1] / port_nav.loc['20201231'] - 1