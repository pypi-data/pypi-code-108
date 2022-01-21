# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import math


def accumulate_timing_risk(annualized_exante_period_timing_series):
    return annualized_exante_period_timing_series.mean()


def accumulate_management_risk(annualized_exante_period_management_df_dict):
    trading_day_list = sorted(annualized_exante_period_management_df_dict.keys())
    annualized_exante_period_management_df = pd.DataFrame(
        annualized_exante_period_management_df_dict[trading_day_list[0]])
    for trading_day in trading_day_list[1:]:
        annualized_exante_period_management_df += annualized_exante_period_management_df_dict[trading_day]
    annualized_exante_period_management_df /= len(trading_day_list)

    return annualized_exante_period_management_df


def compute_attr_linking_coef(period_return_df):
    R_p_t = period_return_df['portfolio']
    R_b_t = period_return_df['benchmark']
    R_p = np.prod(R_p_t.add(1.0)) - 1.0
    R_b = np.prod(R_b_t.add(1.0)) - 1.0
    k = (np.log(1.0 + R_p) - np.log(1.0 + R_b)) / (R_p - R_b)
    R_p_t_arr = R_p_t.values
    R_b_t_arr = R_b_t.values
    k_t = (np.log((1.0 + R_p_t_arr).tolist()) - np.log((1.0 + R_b_t_arr).tolist())) / (R_p_t_arr - R_b_t_arr)
    beta_arr = np.nan_to_num(k_t / k if k != 0.0 else [0.0] * len(k_t))
    beta_series = pd.Series(index=period_return_df.index, data=beta_arr)
    beta_series.index.name = 'date'

    return beta_series


def accumulate_style_factor_return(q, total_return_df, annualized_realized_period_style_factor_series_dict):
    trade_date_list = sorted(annualized_realized_period_style_factor_series_dict.keys())
    first_trade_date = trade_date_list[0]
    unannualized_realized_accumulated_style_factor_series_dict = dict()
    first_annualized_realized_period_style_factor_series = \
        annualized_realized_period_style_factor_series_dict[first_trade_date]
    unannualized_realized_accumulated_style_factor_series_dict[first_trade_date] = \
        first_annualized_realized_period_style_factor_series / q
    total_return_dict = total_return_df.to_dict()
    R_T_P = total_return_dict[first_trade_date]['portfolio'] / q
    R_T_B = total_return_dict[first_trade_date]['benchmark'] / q
    C_T = (R_T_P - R_T_B) / (np.log(1 + R_T_P) - np.log(1 + R_T_B))
    X_t = first_annualized_realized_period_style_factor_series
    for i in range(1, len(trade_date_list)):
        X_pre_t = X_t / q * i
        X_pre_t_divide_C_T = X_pre_t.divide(C_T).fillna(0.)
        trading_day = trade_date_list[i]
        annualized_realized_period_style_factor_series_t = \
            annualized_realized_period_style_factor_series_dict[trading_day]
        r_sector_t_series = annualized_realized_period_style_factor_series_t.divide(q)
        r_p_t = total_return_dict[trading_day]['portfolio'] / q
        r_b_t = total_return_dict[trading_day]['benchmark'] / q
        r_A_t = r_p_t - r_b_t
        if r_A_t == 0:
            unannualized_realized_accumulated_style_factor_series_dict[trading_day] = X_pre_t
            continue
        alpha_t = r_sector_t_series.divide(r_A_t)
        R_T_P = (1 + R_T_P) * (1 + r_p_t) - 1  # R_T+1_P
        R_T_B = (1 + R_T_B) * (1 + r_b_t) - 1  # R_T+1_B
        C_T = (R_T_P - R_T_B) / (np.log(1 + R_T_P) - np.log(1 + R_T_B))  # C_T+1
        X_t = (X_pre_t_divide_C_T * C_T + C_T * np.log((1 + r_p_t) / (1 + r_b_t)) * alpha_t) * q / (i + 1)
        unannualized_realized_accumulated_style_factor_series_dict[trading_day] = X_t / q * (i + 1)

    return unannualized_realized_accumulated_style_factor_series_dict


def accumulate_specific_return(q, total_return_df, annualized_realized_period_specific_return_series):
    trade_date_list = sorted(annualized_realized_period_specific_return_series.index)
    first_trade_date = trade_date_list[0]
    unannualized_realized_accumulated_specific_return_series = pd.Series(index=trade_date_list)
    unannualized_realized_accumulated_specific_return_series[first_trade_date] = \
        annualized_realized_period_specific_return_series[first_trade_date] / q
    total_return_dict = total_return_df.to_dict()
    R_T_P = total_return_dict[first_trade_date]['portfolio'] / q
    R_T_B = total_return_dict[first_trade_date]['benchmark'] / q
    C_T = (R_T_P - R_T_B) / (np.log(1 + R_T_P) - np.log(1 + R_T_B))
    X_t = annualized_realized_period_specific_return_series[first_trade_date]
    for i in range(1, len(trade_date_list)):
        X_pre_t = X_t / q * i
        X_pre_t_divide_C_T = X_pre_t / C_T
        if np.isnan(X_pre_t_divide_C_T):
            X_pre_t_divide_C_T = 0.
        trading_day = trade_date_list[i]
        annualized_realized_period_specific_return_t = annualized_realized_period_specific_return_series[trading_day]
        r_p_t = total_return_dict[trading_day]['portfolio'] / q
        r_b_t = total_return_dict[trading_day]['benchmark'] / q
        r_A_t = r_p_t - r_b_t
        if r_A_t == 0:
            unannualized_realized_accumulated_specific_return_series[trading_day] = X_pre_t
            continue
        alpha_t = annualized_realized_period_specific_return_t / q / r_A_t
        R_T_P = (1 + R_T_P) * (1 + r_p_t) - 1  # R_T+1_P
        R_T_B = (1 + R_T_B) * (1 + r_b_t) - 1  # R_T+1_B
        C_T = (R_T_P - R_T_B) / (np.log(1 + R_T_P) - np.log(1 + R_T_B))  # C_T+1
        X_t = (X_pre_t_divide_C_T * C_T + C_T * np.log((1 + r_p_t) / (1 + r_b_t)) * alpha_t) * q / (i + 1)
        unannualized_realized_accumulated_specific_return_series[trading_day] = X_t / q * (i + 1)

    return unannualized_realized_accumulated_specific_return_series


def accumulate_style_factor_risk(annualized_exante_period_style_factor_series_dict):
    trading_day_list = sorted(annualized_exante_period_style_factor_series_dict.keys())
    annualized_exante_accumulated_style_factor_series = \
        pd.Series(annualized_exante_period_style_factor_series_dict[trading_day_list[0]])
    for trading_day in trading_day_list[1:]:
        annualized_exante_accumulated_style_factor_series += \
            annualized_exante_period_style_factor_series_dict[trading_day]
    annualized_exante_accumulated_style_factor_series /= len(trading_day_list)
    annualized_exante_accumulated_style_factor_series.name = 'style_factor_annualized_exante_risk'
    return annualized_exante_accumulated_style_factor_series


def accumulate_timing_return(total_return_df, realized_period_timing_series):
    trading_day_list = sorted(total_return_df.columns.unique().tolist())
    first_trading_day = trading_day_list[0]
    realized_accumulated_timing_series = pd.Series(index=realized_period_timing_series.index)
    realized_accumulated_timing_series[first_trading_day] = realized_period_timing_series[first_trading_day]

    total_return_dict = total_return_df.to_dict()
    R_T_P = total_return_dict[first_trading_day]['portfolio']
    R_T_B = total_return_dict[first_trading_day]['benchmark']
    C_T = (R_T_P - R_T_B) / (np.log(1 + R_T_P) - np.log(1 + R_T_B))
    if math.isnan(C_T):
        C_T = 0.
    X_t = realized_period_timing_series[first_trading_day]
    for i in range(1, len(trading_day_list)):
        X_pre_t = X_t * i
        X_pre_t_divide_C_T = X_pre_t / C_T if C_T != 0 else 0.

        trading_day = trading_day_list[i]
        timing_t = realized_period_timing_series[trading_day]
        r_p_t = total_return_dict[trading_day]['portfolio']
        r_b_t = total_return_dict[trading_day]['benchmark']
        r_A_t = r_p_t - r_b_t
        alpha_t = timing_t / r_A_t
        if np.isnan(alpha_t):
            alpha_t = 0.
        R_T_P = (1 + R_T_P) * (1 + r_p_t) - 1  # R_T+1_P
        R_T_B = (1 + R_T_B) * (1 + r_b_t) - 1  # R_T+1_B
        C_T = (R_T_P - R_T_B) / (np.log(1 + R_T_P) - np.log(1 + R_T_B))  # C_T+1
        X_t = ((X_pre_t_divide_C_T * C_T) + (C_T * np.log((1 + r_p_t) / (1 + r_b_t)) * alpha_t)) / (i + 1)
        realized_accumulated_timing_series[trading_day] = X_t * (i + 1)

    return realized_accumulated_timing_series


def accumulate_management_return(total_return_df, realized_period_management_df_dict):
    trading_day_list = sorted(realized_period_management_df_dict.keys())
    first_trading_day = trading_day_list[0]
    first_realized_period_management_df = realized_period_management_df_dict[first_trading_day]
    realized_accumulated_management_df_dict = dict()
    realized_accumulated_management_df_dict[first_trading_day] = first_realized_period_management_df

    total_return_dict = total_return_df.to_dict()
    R_T_P = total_return_dict[first_trading_day]['portfolio']
    R_T_B = total_return_dict[first_trading_day]['benchmark']
    C_T = (R_T_P - R_T_B) / (np.log(1 + R_T_P) - np.log(1 + R_T_B))
    if math.isnan(C_T):
        C_T = 0.
    X_t = first_realized_period_management_df
    for i in range(1, len(trading_day_list)):
        X_pre_t = X_t * i
        X_pre_t_divide_C_T = (X_pre_t / C_T).fillna(0.)

        trading_day = trading_day_list[i]
        r_p_t = total_return_dict[trading_day]['portfolio']
        r_b_t = total_return_dict[trading_day]['benchmark']
        r_A_t = r_p_t - r_b_t
        alpha_t = realized_period_management_df_dict[trading_day].divide(r_A_t).fillna(0.)
        R_T_P = (1 + R_T_P) * (1 + r_p_t) - 1  # R_T+1_P
        R_T_B = (1 + R_T_B) * (1 + r_b_t) - 1  # R_T+1_B
        C_T = (R_T_P - R_T_B) / (np.log(1 + R_T_P) - np.log(1 + R_T_B))  # C_T+1
        # if np.isnan(alpha_t):
        #     alpha_t = 0.
        X_t = (X_pre_t_divide_C_T.multiply(C_T)).add(
            C_T * np.log((1 + r_p_t) / (1 + r_b_t)) * alpha_t) / (i + 1)
        realized_accumulated_management_df_dict[trading_day] = X_t * (i + 1)

    return realized_accumulated_management_df_dict
