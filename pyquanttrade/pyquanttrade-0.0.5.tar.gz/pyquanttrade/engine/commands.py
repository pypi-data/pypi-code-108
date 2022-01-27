# -*- coding: utf-8 -*-
"""Functions from market data"""

# -*- coding: utf-8 -*-
"""Functions from market data"""

__author__ = "Miguel Martin"
__version__ = "1"

from pyquanttrade import market
from pyquanttrade.market import marketData
from pyquanttrade.engine.trade import TradeList
from pyquanttrade.engine.test_result import TestResult
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import logging

# TODO: end positions closes to compute final return
def backtest(
    policy,
    tickers,
    start_at,
    stop_at,
    capital=10000,
    commision=0,
    slippage_perc=0,
    level=logging.WARNING,
    time_buffer=250
):
    logging.basicConfig(level=level)
    if not isinstance(tickers, list):
        tickers = [tickers]

    trade_list = TradeList(level=level)
    first_day = (
        datetime.strptime(start_at, "%Y-%m-%d").date() - timedelta(days=time_buffer)
    ).isoformat()

    policies = {}
    data_sims = {}
    data_dict = {}
    policy_class = policy
    logging.info(policy_class)
    remaining_capital = {tick: capital for tick in tickers}
    for ticker in tickers:
        policies[ticker] = policy_class
        logging.info(policy_class.name)
        data = marketData.get_data(ticker, first_day, stop_at)
        data_sim = data.loc[data.index >= start_at]

        if not data_sims:
            result = TestResult(data_sim, ticker, capital)
        else:
            result.add_ticker(data_sim, ticker, capital)

        data_sims[ticker] = data_sim
        data_dict[ticker] = data

    def calculate_num_shares(capital, share_price):
        num_shares = int(capital / share_price)
        remaining = capital - num_shares * share_price
        return (num_shares, remaining)

    def execute_policy(policy, i, row, data, capital, ticker):
        last_day = data.iloc[data.index.get_loc(i) - 1]
        signals = policy.execute(
            str(last_day.name).split(" ")[0], data, trades=trade_list
        )
        remaining = capital
        for signal in signals:
            if signal == "Buy_long":

                logging.info(str(ticker) + " : " + str(i) + " -- " + signal)
                slip = slippage_perc * (row["high"] - row["low"])
                loss = policy_class.long_stop_loss
                trailling = policy_class.long_stop_loss_trailling
                shares, remaining = calculate_num_shares(remaining, row["open"])
                trade_list.open_trade(
                    ticker,
                    "long",
                    str(i),
                    row["open"],
                    shares,
                    loss,
                    trailling,
                    commision,
                    slip,
                )
                logging.info("num of shares buyed: " + str(shares))
                logging.info("cost of shares buyed: " + str(shares * row["open"]))

            if signal == "Close_long":

                logging.info(str(ticker) + " : " + str(i) + " -- " + signal)
                money = trade_list.close_open_trades(
                    ticker, "long", str(i), row["open"]
                )
                remaining += money

            if signal == "Sell_short":

                logging.info(str(ticker) + " : " + str(i) + " -- " + signal)
                slip = slippage_perc * (row["high"] - row["low"])
                loss = policy_class.short_stop_loss
                trailling = policy_class.short_stop_loss_trailling
                shares, remaining = calculate_num_shares(remaining, row["open"])
                trade_list.open_trade(
                    ticker,
                    "short",
                    str(i),
                    row["open"],
                    shares,
                    loss,
                    trailling,
                    commision,
                    slip,
                )

            if signal == "Close_short":

                logging.info(str(ticker) + " : " + str(i) + " -- " + signal)
                money = trade_list.close_open_trades(
                    ticker, "short", str(i), row["open"]
                )
                remaining += money
        return remaining

    for i, row in data_sims[tickers[0]].iterrows():
        for ticker in policies.keys():
            ticker_row = data_sims[ticker].loc[i]
            if i in data_sims[ticker].index:
                remaining_capital[ticker] = execute_policy(
                    policies[ticker],
                    i,
                    ticker_row,
                    data_dict[ticker],
                    remaining_capital[ticker], 
                    ticker
                )

        for ticker in policies.keys():
            money = trade_list.verify_stop_loss(
                str(i), ticker_row["low"], ticker_row["high"]
            )
            remaining_capital[ticker] += money

            result.update(i, trade_list, ticker)
    
    #Data returns only works with one ticker, for visualization purposes
    return result, data

def plot_activity_list(activity_list):
    
    fig = go.Figure()

    #Decoding signal list as separate lists
    activity_list['buy_long'] = None
    activity_list.loc[activity_list['signals']=='Buy_long','buy_long'] = activity_list.loc[activity_list['signals']=='Buy_long','close']
    activity_list['rebuy_long'] = None
    activity_list.loc[activity_list['signals']=='Rebuy_long','rebuy_long'] = activity_list.loc[activity_list['signals']=='Rebuy_long','close']
    activity_list['close_long'] = None
    activity_list.loc[activity_list['signals']=='Close_long','close_long'] = activity_list.loc[activity_list['signals']=='Close_long','close']
    activity_list['sell_short'] = None
    activity_list.loc[activity_list['signals']=='Sell_short','sell_short'] = activity_list.loc[activity_list['signals']=='Sell_short','close']
    activity_list['resell_short'] = None
    activity_list.loc[activity_list['signals']=='Resell_short','resell_short'] = activity_list.loc[activity_list['signals']=='Resell_short','close']
    activity_list['close_short'] = None
    activity_list.loc[activity_list['signals']=='Close_short','close_short'] = activity_list.loc[activity_list['signals']=='Close_short','close']

    fig.add_trace(go.Scatter(x=activity_list['close'].index, y=activity_list['close'], mode='lines', name='Price', line={'width':1,'color':'black'}))
    if not activity_list['buy_long'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['buy_long'].index, y=activity_list['buy_long'], mode='markers', name='Buy Long', marker ={'symbol':'arrow-up', 'size':9, 'color':'green'}))
    if not activity_list['rebuy_long'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['rebuy_long'].index, y=activity_list['rebuy_long'], mode='markers', name='ReBuy Long', marker ={'symbol':'triangle-ne', 'size':9, 'color':'green'}))
    if not activity_list['close_long'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['close_long'].index, y=activity_list['close_long'], mode='markers', name='Close Long', marker ={'symbol':'x', 'size':9, 'color':'green'}))
    if not activity_list['sell_short'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['sell_short'].index, y=activity_list['sell_short'], mode='markers', name='Sell Short', marker ={'symbol':'arrow-down', 'size':9, 'color':'red'}))
    if not activity_list['resell_short'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['resell_short'].index, y=activity_list['resell_short'], mode='markers', name='ReSell Short', marker ={'symbol':'triangle-se', 'size':9, 'color':'red'}))
    if not activity_list['close_short'].isnull().all(): 
        fig.add_trace(go.Scatter(x=activity_list['close_short'].index, y=activity_list['close_short'], mode='markers', name='Close Short', marker ={'symbol':'x', 'size':9, 'color':'red'}))
    
    return fig


def backtest_and_visualise(
    policy,
    ticker,
    start_at,
    stop_at,
    capital=10000,
    commision=0,
    slippage_perc=0,
    level=logging.WARNING,
    time_buffer=250,
):
    assert ticker is not list

    result, data = backtest(
        policy,
        ticker,
        start_at,
        stop_at,
        capital=10000,
        commision=0,
        slippage_perc=0,
        level=logging.WARNING,
        time_buffer=250)

    for _, trade in result.data.trade_list.trades_closed.items():
        if trade.type == 'long':
            data.loc[trade.open_day,'signals'] = 'Buy_long'
            data.loc[trade.close_day,'signals'] = 'Close_long'
        elif trade.type == 'short':
            data.loc[trade.open_day,'signals'] = 'Sell_short'
            data.loc[trade.close_day,'signals'] = 'Close_short'

    fig = plot_activity_list(data)

    for elem in policy.plot_functions:
        fig.add_trace(go.Scatter(x = data.index, y = data[elem], mode='lines', name=elem, line={'width':1}))

    return result, fig