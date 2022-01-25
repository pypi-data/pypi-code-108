# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

Q_MAP = {
    'day': 250.0,
    'week': 52.0,
    'month': 12.0,
    'season': 4,
    'semi': 2,
    'year': 1
}


def norm_dist_draw(se_signal, n_draw):
    series = se_signal.copy()
    for i in range(n_draw):
        std = series.std()
        mean = series.mean()
        series[series < mean - 3 * std] = mean - 3 * std
        series[series > mean + 3 * std] = mean + 3 * std
    return series


def return_to_nav(nav_start_date, return_series):
    if return_series.empty:
        return pd.Series(index=[], data=[])
    nav_series = return_series.add(1.0).cumprod()
    nav_series.loc[nav_start_date] = 1.0
    return nav_series.sort_index()


def nav_to_return_patch(nav_series, daily_trading_date_list, trading_day_list):
    nav_series = nav_series.sort_index()

    if nav_series.empty:
        return nav_series
    fund_sub_daily_nav = nav_series.reindex(daily_trading_date_list).interpolate().dropna().sort_index()
    fund_sub_nav = fund_sub_daily_nav.reindex(trading_day_list).dropna().sort_index()

    return_series = fund_sub_nav.pct_change().dropna()
    daily_return_series = fund_sub_daily_nav.pct_change().dropna()
    return return_series, daily_return_series


def return_df_day_index_patch(fund_nav_dict, daily_trading_date_list, trading_day_list, is_norm=False):
    if fund_nav_dict is None:
        return pd.DataFrame(), pd.DataFrame()

    fund_return_dict = {}
    fund_daily_return_dict = {}

    for fund in fund_nav_dict.keys():
        fund_adj_nav = fund_nav_dict[fund]

        return_series, daily_return_series = nav_to_return_patch(
            fund_adj_nav, daily_trading_date_list, trading_day_list)

        if return_series.empty or daily_return_series.empty:
            continue

        if is_norm and len(return_series) > 1:
            return_series = norm_dist_draw(return_series, 1)
            daily_return_series = norm_dist_draw(daily_return_series, 1)

        fund_return_dict[fund] = return_series
        fund_daily_return_dict[fund] = daily_return_series

    return_df_day_index = pd.DataFrame.from_dict(fund_return_dict)
    daily_return_df_day_index = pd.DataFrame.from_dict(fund_daily_return_dict)
    return return_df_day_index, daily_return_df_day_index


def benchmark_return_series_computer(child_series, benchmark_return_df, quotedMargin_series=None, frequency='day'):
    q = Q_MAP[frequency]
    if benchmark_return_df.empty:
        return pd.Series(data=[])

    intersection_list = list(set(benchmark_return_df.columns) & set(child_series.index))
    benchmark_return_df = benchmark_return_df[intersection_list]
    child_series = child_series.ix[intersection_list]
    if quotedMargin_series is not None:
        quotedMargin_series = quotedMargin_series.ix[intersection_list]
        benchmark_return_series = benchmark_return_df.add(quotedMargin_series / q).dot(child_series)
    else:
        benchmark_return_series = benchmark_return_df.dot(child_series)
    return benchmark_return_series


def compute_geometric_annual_return_df(return_df, calc_q):
    t = return_df.shape[0]

    if t <= 0:
        return pd.DataFrame()

    holding_period_nav_series = return_df.fillna(0.).add(1.0).prod()
    tao = float(calc_q) / float(t)
    annual_return_series = holding_period_nav_series.pow(tao).subtract(1.0)
    return annual_return_series


def compute_arithmetic_annual_return_df(return_df, calc_q):
    mean_return = return_df.mean()
    annual_return_series = mean_return.multiply(calc_q)
    return annual_return_series


def compute_linking_annual_return_df(return_df, calc_q):
    t = return_df.shape[0]

    if t <= 0:
        return pd.DataFrame()

    holding_period_yield = return_df.fillna(0.).add(1.0).prod().subtract(1.0)
    tao = float(calc_q) / float(t)
    annual_return_series = holding_period_yield.multiply(tao)
    return annual_return_series


def compute_annual_return_df(return_df_day_index, calc_q, annual_type):
    if annual_type == 'arithmetic':
        annual_return = compute_arithmetic_annual_return_df(return_df=return_df_day_index, calc_q=calc_q)
    elif annual_type == 'linking':
        annual_return = compute_linking_annual_return_df(return_df=return_df_day_index, calc_q=calc_q)
    else:
        annual_return = compute_geometric_annual_return_df(return_df=return_df_day_index, calc_q=calc_q)
    return annual_return


def compute_geometric_annual_return(return_series, calc_q):
    t = len(return_series)

    if t <= 0:
        return np.NaN

    holding_period_nav = return_series.fillna(0.).add(1.0).prod()
    tao = float(calc_q) / float(t)
    return float((holding_period_nav ** tao) - 1.0)


def compute_arithmetic_annual_return(return_series, calc_q):
    mean_return = return_series.mean()
    return float(mean_return * calc_q)


def compute_linking_annual_return(return_series, calc_q):
    t = len(return_series)

    if t <= 0:
        return np.NaN

    holding_period_yield = return_series.fillna(0.).add(1.0).prod() - 1.0
    tao = float(calc_q) / float(t)
    return float(holding_period_yield * tao)


def compute_annual_return(return_series, calc_q, annual_type):
    if annual_type == 'arithmetic':
        annual_return = compute_arithmetic_annual_return(return_series=return_series, calc_q=calc_q)
    elif annual_type == 'linking':
        annual_return = compute_linking_annual_return(return_series=return_series, calc_q=calc_q)
    else:
        annual_return = compute_geometric_annual_return(return_series=return_series, calc_q=calc_q)
    return annual_return
