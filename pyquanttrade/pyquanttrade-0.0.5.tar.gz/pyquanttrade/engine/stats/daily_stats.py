# -*- coding: utf-8 -*-
"""Functions from market data"""

__author__ = "Miguel Martin"
__version__ = "1"

import pandas as pd
import numpy as np

from pyquanttrade.engine.utils import (
    max_drawdown_ratio,
    max_drawdown_value,
    safe_div,
    safe_min,
    safe_sum,
    safe_mean,
)

class DailyStats:
    def __init__(self, data_sim, ticker, capital):
        self.trade_list = None
        self.tickers = [ticker]
        self.tickers_capital = {}
        self.tickers_capital[ticker] = capital
        self.long_ticker = {}
        self.short_ticker = {}
        self.global_ticker = {}
        (l, s, t) = self._initDataframe(data_sim.index, ticker, data_sim, capital)
        self.long_ticker[ticker] = l
        self.short_ticker[ticker] = s
        self.global_ticker[ticker] = t

        self.long_all = None
        self.short_all = None
        self.global_all = None

        self.last_closed_profit = {}
        self.last_closed_inversion = {}
        self._last_trades_len = {}
        self.last_closed_profit[ticker] = {"long": 0.0, "short": 0.0, "all": 0.0}
        self.last_closed_inversion[ticker] = {"long": 0.0, "short": 0.0, "all": 0.0}
        self._last_trades_len[ticker] = {"long": 0.0, "short": 0.0, "all": 0.0}


    # Init dataframes stats values for a ticker data. 
    def _initDataframe(self, index_data, ticker, data_sim, capital):
        long_system_results = pd.DataFrame(index=index_data)
        short_system_results = pd.DataFrame(index=index_data)
        system_results = pd.DataFrame(index=index_data)

        # init  long trades
        shares = int(capital / data_sim.iloc[0]["close"])
        long_system_results["close"] = data_sim["close"]
        long_system_results["trade_profit"] = np.NaN
        long_system_results["trade_inversion"] = np.NaN
        long_system_results["trade_cum_inversion"] = np.NaN
        long_system_results["trade_cum_profit"] = np.NaN
        long_system_results["trade_close"] = np.NaN
        long_system_results["trade_sequence"] = np.NaN
        long_system_results["profit_sequence"] = 0.0
        long_system_results["Daily_cumulative"] = 1.0
        long_system_results["Daily_sequence"] = 1.0
        long_system_results["Daily_current_inversion"] = np.NaN
        long_system_results["last_closed_profit"] = np.NaN
        long_system_results["sum_open_price"] = np.NaN
        long_system_results["open_trades"] = 0.0
        long_system_results["Daily_capital"] = 0.0
        long_system_results["Daily_freeze"] = 0.0
        long_system_results["baseline"] = (
            long_system_results["close"] * shares
        )

        # init  short trades
        short_system_results["close"] = data_sim["close"]
        short_system_results["trade_profit"] = np.NaN
        short_system_results["trade_inversion"] = np.NaN
        short_system_results["trade_cum_inversion"] = np.NaN
        short_system_results["trade_cum_profit"] = np.NaN
        short_system_results["trade_close"] = np.NaN
        short_system_results["trade_sequence"] = np.NaN
        short_system_results["Daily_cumulative"] = 1.0
        short_system_results["Daily_sequence"] = 1.0
        short_system_results["open_trades"] = 0.0
        short_system_results["profit_sequence"] = 0.0
        short_system_results["Daily_current_inversion"] = np.NaN
        short_system_results["last_closed_profit"] = np.NaN
        short_system_results["sum_open_price"] = np.NaN
        short_system_results["Daily_capital"] = 0.0
        short_system_results["Daily_freeze"] = 0.0
        short_system_results["baseline"] = (
            short_system_results["close"] * shares
        )

        # init  All trades
        system_results["close"] = data_sim["close"]
        system_results["trade_profit"] = np.NaN
        system_results["trade_inversion"] = np.NaN
        system_results["trade_cum_inversion"] = np.NaN
        system_results["trade_cum_profit"] = np.NaN
        system_results["trade_close"] = np.NaN
        system_results["trade_sequence"] = np.NaN
        system_results["Daily_cumulative"] = 1.0
        system_results["Daily_sequence"] = 1.0
        system_results["open_trades"] = 0.0
        system_results["profit_sequence"] = 0.0
        system_results["Daily_current_inversion"] = np.NaN
        system_results["last_closed_profit"] = np.NaN
        system_results["sum_open_price"] = np.NaN
        system_results["Daily_capital"] = 0.0
        system_results["Daily_freeze"] = 0.0
        system_results["baseline"] = system_results["close"] * shares

        return (long_system_results, short_system_results, system_results)

    # Add new ticker for the stats
    def add_ticker(self, data_sim, ticker, capital):
        self.tickers += [ticker]
        self.tickers_capital[ticker] = capital
        (l, s, t) = self._initDataframe(data_sim.index, ticker, data_sim, capital)
        self.long_ticker[ticker] = l
        self.short_ticker[ticker] = s
        self.global_ticker[ticker] = t

        self.last_closed_profit[ticker] = {"long": 0.0, "short": 0.0, "all": 0.0}
        self.last_closed_inversion[ticker] = {"long": 0.0, "short": 0.0, "all": 0.0}
        self._last_trades_len[ticker] = {"long": 0.0, "short": 0.0, "all": 0.0}

    def _update(self, trade_type, i, row, trade_list, system_results, ticker):
        if trade_type == "all":
            trade_closed_len = (
                self._last_trades_len[ticker]["long"]
                + self._last_trades_len[ticker]["short"]
            )
        else:
            trade_closed_len = len(
                [
                    trade
                    for k, trade in trade_list.trades_closed.items()
                    if (trade.type == trade_type and trade.ticker == ticker)
                ]
            )

        if trade_closed_len > self._last_trades_len[ticker][trade_type]:

            self._last_trades_len[ticker][trade_type] = trade_closed_len
            total_closed_profit = trade_list.get_close_profit(trade_type, ticker)
            delta_closed_profit = (
                total_closed_profit - self.last_closed_profit[ticker][trade_type]
            )
            self.last_closed_profit[ticker][trade_type] = total_closed_profit

            total_closed_inversion = trade_list.get_close_trades_total_open(trade_type, ticker)
            
            delta_closed_inversion = (
                total_closed_inversion - self.last_closed_inversion[ticker][trade_type]
            )
            self.last_closed_inversion[ticker][trade_type] = total_closed_inversion

            system_results.loc[i, ["trade_profit"]] = delta_closed_profit
            system_results.loc[i, ["trade_inversion"]] = delta_closed_inversion
            system_results.loc[i, ["trade_cum_inversion"]] = total_closed_profit
            system_results.loc[i, ["trade_cum_profit"]] = total_closed_inversion

            system_results.loc[i, ["trade_close"]] = 1 + safe_div(
                delta_closed_profit, delta_closed_inversion
            )
            system_results.loc[i, ["trade_sequence"]] = 1 + safe_div(
                total_closed_profit, total_closed_inversion
            )

        current_inversion = trade_list.get_current_total_open(trade_type, ticker)
        system_results.loc[i, ["Daily_current_inversion"]] = current_inversion
        if current_inversion == 0:
            system_results.loc[i, ["Daily_sequence"]] = 1
        else:
            system_results.loc[i, ["Daily_sequence"]] = (
                1 + (trade_list.get_current_profit(row, trade_type, ticker)) / current_inversion
            )
            system_results.loc[i, ["profit_sequence"]] = trade_list.get_current_profit(
                row, trade_type, ticker
            )


        if trade_type == "all":
            len_open_trades = len(
                [trade for k, trade in trade_list.trades_opened.items() if trade.ticker == ticker]
            )
        else:
            len_open_trades = len(
                [
                    trade
                    for k, trade in trade_list.trades_opened.items()
                    if (trade.type == trade_type and trade.ticker == ticker)
                ]
            )

        if len_open_trades > 0:
            sum_open_price = trade_list.get_open_trades_total_open(trade_type, ticker)
            system_results.loc[i,["last_closed_profit"]] = self.last_closed_profit[ticker][trade_type]
            system_results.loc[i,["sum_open_price"]] = sum_open_price
            system_results.loc[i, ["Daily_cumulative"]] = (
                1
                + (
                    trade_list.get_current_profit(row, trade_type, ticker)
                    - self.last_closed_profit[ticker][trade_type]
                )
                / sum_open_price
            )
            system_results.loc[i, ["open_trades"]] = len_open_trades

        dayly_capital = self.tickers_capital[ticker] + trade_list.get_current_profit(row, trade_type, ticker)
        system_results.loc[i, ["Daily_capital"]] = dayly_capital
        system_results.loc[
            i, ["Daily_freeze"]
        ] = dayly_capital - trade_list.get_current_only_open(trade_type, ticker)

    def update(self, i, trade_list, ticker):
        self.trade_list = trade_list
        l = self.long_ticker[ticker]
        s = self.short_ticker[ticker]
        t = self.global_ticker[ticker]
        self._update("long", i, l.loc[i, "close"], trade_list, l, ticker)
        self._update("short", i, s.loc[i, "close"], trade_list, s, ticker)
        self._update("all", i, t.loc[i, "close"], trade_list, t, ticker)
    

    
    def generate_all_stats(self):
        self.long_all = self._join_all_tickers(list(self.long_ticker.values()))
        self.short_all = self._join_all_tickers(list(self.short_ticker.values()))
        self.global_all = self._join_all_tickers(list(self.global_ticker.values()))


    def _join_ticker_result(self, ticker_a_results, ticker_b_result):
        join_results = pd.DataFrame(index=ticker_a_results.index)
        join_results["close"] = ticker_a_results["close"] + ticker_b_result["close"]
        join_results["trade_profit"] = ticker_a_results["trade_profit"] + ticker_b_result["trade_profit"]
        join_results["trade_inversion"] = ticker_a_results["trade_inversion"] + ticker_b_result["trade_inversion"]
        join_results["trade_cum_inversion"] = ticker_a_results["trade_cum_inversion"] + ticker_b_result["trade_cum_inversion"]
        join_results["trade_cum_profit"] = ticker_a_results["trade_cum_profit"] + ticker_b_result["trade_cum_profit"]
        join_results["trade_close"] = join_results["trade_profit"].div(join_results["trade_inversion"]) + 1
        join_results["trade_sequence"] = join_results["trade_cum_profit"].div(join_results["trade_cum_inversion"]) + 1
        join_results["Daily_current_inversion"] = ticker_a_results["Daily_current_inversion"] + ticker_b_result["Daily_current_inversion"]
        join_results["profit_sequence"] = ticker_a_results["profit_sequence"] + ticker_b_result["profit_sequence"]
        join_results["Daily_sequence"] = join_results["profit_sequence"].div(join_results["Daily_current_inversion"]) + 1
        join_results["last_closed_profit"] = ticker_a_results["last_closed_profit"] + ticker_b_result["last_closed_profit"]
        join_results["sum_open_price"] = ticker_a_results["sum_open_price"] + ticker_b_result["sum_open_price"]
        join_results["Daily_cumulative"] = (ticker_a_results["profit_sequence"] - ticker_a_results["last_closed_profit"]).div(ticker_b_result["sum_open_price"]) + 1
        join_results["open_trades"] = ticker_a_results["open_trades"] + ticker_b_result["open_trades"]
        join_results["Daily_capital"] = ticker_a_results["Daily_capital"] + ticker_b_result["Daily_capital"]
        join_results["Daily_freeze"] = ticker_a_results["Daily_freeze"] + ticker_b_result["Daily_freeze"]
        join_results["baseline"] = ticker_a_results["baseline"] + ticker_b_result["baseline"]

        return join_results

    def _join_all_tickers(self, tickers):
        if len(tickers) == 1:
            return tickers[0]
            
        join = self._join_ticker_result(tickers[0], tickers[1])

        for t in tickers[2:]:
            join = self._join_ticker_result(join, t)
        return join

