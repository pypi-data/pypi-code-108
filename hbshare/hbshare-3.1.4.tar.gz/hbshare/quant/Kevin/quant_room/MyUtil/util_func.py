"""
辅助函数模块
"""
import numpy as np


def cal_annual_return(return_series):
    T = len(return_series)
    annual_return = (1 + return_series).prod() ** (52 / T) - 1

    return annual_return


def cal_annual_volatility(return_series):
    vol = return_series.std() * np.sqrt(52)

    return vol


def cal_max_drawdown(nav_series):
    drawdown_series = nav_series / (nav_series.cummax()) - 1

    return drawdown_series.min()


def cal_sharpe_ratio(return_series, rf):
    annual_return = cal_annual_return(return_series)
    vol = cal_annual_volatility(return_series)
    sharpe_ratio = (annual_return - rf) / vol

    return sharpe_ratio