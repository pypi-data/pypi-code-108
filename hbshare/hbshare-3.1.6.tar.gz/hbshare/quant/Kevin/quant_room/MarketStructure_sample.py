"""
市场结构的测试代码部分
"""
import pandas as pd
import numpy as np
import os
import statsmodels.api as sm
from hbshare.fe.common.util.data_loader import get_trading_day_list
from hbshare.quant.Kevin.quant_room.MarketStructure import MarketHist, get_market_turnover, get_style_factor, \
    AlphaSeries, MarketStructure
from tqdm import tqdm


data_path = "D:\\研究基地\\Analysis"


def run_daily_plot(start_date, end_date):
    date_list = get_trading_day_list(start_date, end_date)
    for date in tqdm(date_list):
        MarketHist(date, '000905').daily_plot()


def run_market_structure(start_date, end_date):
    date_list = get_trading_day_list(start_date, end_date)
    all_res = []
    for date in tqdm(date_list):
        res = MarketStructure(date, '000905').get_construct_result()
        all_res.append(res)

    structure_all = pd.concat(all_res)
    structure_all.to_csv(os.path.join(data_path, "market_structure.csv"))


def run_factor_test(start_date, end_date, mode="1"):
    if mode == "1":
        factor_df = get_market_turnover(start_date, end_date)
    elif mode == "2":
        factor_df = pd.read_csv('D:\\市场微观结构图\\market_factor_save\\win_ratio.csv', index_col=0)
        factor_df['trade_date'] = factor_df.index
        factor_df['trade_date'] = factor_df['trade_date'].apply(lambda x: str(x))
        factor_df = factor_df.set_index('trade_date')
    elif mode == "3":
        factor_df = get_style_factor(start_date, end_date)
        # vol_df = factor_df.rolling(5).std().loc[start_date:]
        # vol_df.rename(columns=lambda x: str(x) + "_vol", inplace=True)
        factor_df = factor_df.loc[start_date:][['size', 'btop', 'growth']]
        # factor_df = pd.concat([factor_df, vol_df], axis=1)
    else:
        factor_df = pd.read_csv('D:\\市场微观结构图\\market_factor_save\\ind_cr.csv', index_col=0)
        factor_df['trade_date'] = factor_df.index
        factor_df['trade_date'] = factor_df['trade_date'].apply(lambda x: str(x))
        factor_df = factor_df.set_index('trade_date')

    alpha_series = AlphaSeries(start_date, end_date).calculate()
    idx = factor_df.index.intersection(alpha_series.index)
    factor_df = factor_df.reindex(idx)
    alpha_excess = alpha_series.reindex(idx)
    factor_df['alpha_excess'] = alpha_excess

    corr_df = factor_df.apply(lambda x: x.rolling(250).corr(factor_df['alpha_excess']).dropna(), axis=0)

    return factor_df


def run_analysis(start_date, end_date):
    cs_vol_df = pd.read_csv('D:\\市场微观结构图\\market_factor_save\\cs_vol.csv', index_col=0)
    cs_vol_df['trade_date'] = cs_vol_df.index
    cs_vol_df['trade_date'] = cs_vol_df['trade_date'].map(str)
    cs_vol_df = cs_vol_df.set_index('trade_date')

    win_ratio_df = pd.read_csv('D:\\市场微观结构图\\market_factor_save\\win_ratio.csv', index_col=0)
    win_ratio_df['trade_date'] = win_ratio_df.index
    win_ratio_df['trade_date'] = win_ratio_df['trade_date'].apply(lambda x: str(x))
    win_ratio_df = win_ratio_df.set_index('trade_date')

    style_df = get_style_factor(start_date, end_date)
    style_df = style_df.loc[start_date:][['size', 'btop', 'growth']]

    ind_df = pd.read_csv('D:\\市场微观结构图\\market_factor_save\\ind_cr.csv', index_col=0)
    ind_df['trade_date'] = ind_df.index
    ind_df['trade_date'] = ind_df['trade_date'].apply(lambda x: str(x))
    ind_df = ind_df.set_index('trade_date')

    factor_df = cs_vol_df[['skew_300', 'skew_800', 'skew_1800']].merge(
        win_ratio_df[['win_ratio_all', 'lose_spread_all']], left_index=True, right_index=True).merge(
        style_df[['size']], left_index=True, right_index=True).merge(
        ind_df[['win_ratio_abs', 'win_ratio_relative']], left_index=True, right_index=True)

    alpha_excess = AlphaSeries(start_date, end_date).calculate()
    idx = factor_df.index.intersection(alpha_excess.index)
    factor_df = factor_df.reindex(idx)
    alpha_excess = alpha_excess.reindex(idx)
    factor_df['alpha_excess'] = alpha_excess


if __name__ == '__main__':
    # run_daily_plot('20211215', '20211215')
    # df = run_factor_test('20180101', '20211112', mode="4")
    # print(df)
    # run_market_structure('20200101', '20211108')
    run_analysis('20180101', '20211112')