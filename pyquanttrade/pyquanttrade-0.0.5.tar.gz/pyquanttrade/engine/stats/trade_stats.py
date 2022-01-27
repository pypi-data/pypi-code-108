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

class TradeSummaryStats:

    def __init__(self, trade_list, long_stats, short_stats, system_stats, capital):
        self.all_trades = {}
        self.long_trades = {}
        self.short_trades = {}

        # split long win, long lose, short win and short lose trades for further analysis.
        long_win_trades = [
            trade
            for k, trade in trade_list.trades_closed.items()
            if trade.profit >= 0
            if trade.type == "long"
        ]
        long_lose_trades = [
            trade
            for k, trade in trade_list.trades_closed.items()
            if trade.profit < 0
            if trade.type == "long"
        ]

        short_win_trades = [
            trade
            for k, trade in trade_list.trades_closed.items()
            if trade.profit >= 0
            if trade.type == "short"
        ]
        short_lose_trades = [
            trade
            for k, trade in trade_list.trades_closed.items()
            if trade.profit < 0
            if trade.type == "short"
        ]
        # Num of trades:
        len_long_trades = len(long_lose_trades) + len(long_win_trades)
        len_short_trades = len(short_lose_trades) + len(short_win_trades)
        len_all_trades = len_long_trades + len_short_trades
        self.all_trades['len trades'] = len_all_trades
        self.long_trades['len trades'] = len_long_trades
        self.short_trades['len trades'] = len_short_trades

        self.all_trades['Num of winning trades'] = len(long_win_trades) + len(short_win_trades)
        self.all_trades['Num of losing trades'] = len(long_lose_trades) + len(short_lose_trades)
        self.long_trades['Num of winning trades'] = len(long_win_trades)
        self.long_trades['Num of losing trades'] = len(long_lose_trades)
        self.short_trades['Num of winning trades'] = len(short_win_trades)
        self.short_trades['Num of losing trades'] = len(short_lose_trades)

        # Profit of Winners:
        profit_long_win_trades = np.sum([trade.profit for trade in long_win_trades])
        profit_short_win_trades = np.sum([trade.profit for trade in short_win_trades])
        profit_total_win_trades = profit_long_win_trades + profit_short_win_trades

        self.all_trades['profit win trades'] = profit_total_win_trades
        self.long_trades['profit win trades'] = profit_long_win_trades
        self.short_trades['profit win trades'] = profit_short_win_trades

        # Loss of Lossers:
        lose_long_lose_trades = -np.sum([trade.profit for trade in long_lose_trades])
        lose_short_lose_trades = -np.sum([trade.profit for trade in short_lose_trades])
        lose_total_lose_trades = lose_long_lose_trades + lose_short_lose_trades

        self.all_trades['lose loser trades'] = lose_total_lose_trades
        self.long_trades['lose loser trades'] = lose_long_lose_trades
        self.short_trades['lose loser trades'] = lose_short_lose_trades

        # Net profit:
        net_long = profit_long_win_trades - lose_long_lose_trades
        net_short = profit_short_win_trades - lose_short_lose_trades
        net_total = net_long + net_short

        self.all_trades['net profit'] = net_total
        self.long_trades['net profit'] = net_long
        self.short_trades['net profit'] = net_short

        # Initial Capital:
        self.all_trades['init capital'] = capital
        self.long_trades['init capital'] = capital
        self.short_trades['init capital'] = capital

        # Final Capital:

        self.all_trades['final capital'] = capital + net_total
        self.long_trades['final capital'] = capital + net_long
        self.short_trades['final capital'] = capital + net_short

        # Ratio Net profit:
        long_init_capital = capital
        short_init_capital = capital
        total_init_capital = capital

        ratio_net_long = safe_div(net_long, long_init_capital)
        ratio_net_short = safe_div(net_short, short_init_capital)
        ratio_net_total = safe_div(net_total, total_init_capital)

        self.all_trades['ratio net profit'] = 100 * ratio_net_total
        self.long_trades['ratio net profit'] = 100 * ratio_net_long
        self.short_trades['ratio net profit'] = 100 * ratio_net_short

        # Anualized Ratio Net profit:
        sim_years = system_stats.shape[0] / 250
        self.all_trades['anual ratio net profile'] = 100 * ((ratio_net_total + 1) ** (1 / sim_years) - 1)
        self.long_trades['anual ratio net profile'] = 100 * ((ratio_net_long + 1) ** (1 / sim_years) - 1)
        self.short_trades['anual ratio net profile'] = 100 * ((ratio_net_short + 1) ** (1 / sim_years) - 1)

        # Profit Factor:
        long_profit_factor = safe_div(profit_long_win_trades, lose_long_lose_trades)
        short_profit_factor = safe_div(profit_short_win_trades, lose_short_lose_trades)
        total_profi_factor = safe_div(profit_total_win_trades, lose_total_lose_trades)

        self.all_trades['profit factor'] = total_profi_factor
        self.long_trades['profit factor'] = long_profit_factor
        self.short_trades['profit factor'] = short_profit_factor

        # Percent Profitable:

        long_percent_profitable = safe_div(
            len(long_win_trades), len(long_win_trades + long_lose_trades)
        )
        short_percent_profitable = safe_div(
            len(short_win_trades), len(short_win_trades + short_lose_trades)
        )
        total_percent_profitable = safe_div(
            len(long_win_trades + short_win_trades),
            len(
                long_win_trades
                + short_win_trades
                + long_lose_trades
                + short_lose_trades
            ),
        )

        self.all_trades['% profitable'] = total_percent_profitable
        self.long_trades['% profitable'] = long_percent_profitable
        self.short_trades['% profitable'] = short_percent_profitable

        # Payoff Ratio:

        long_avg_win = safe_div(profit_long_win_trades, len(long_win_trades))
        short_avg_win = safe_div(profit_short_win_trades, len(short_win_trades))
        total_avg_win = safe_div(
            profit_total_win_trades, len(long_win_trades + short_win_trades)
        )

        long_avg_lose = safe_div(lose_long_lose_trades, len(long_lose_trades))
        short_avg_lose = safe_div(lose_short_lose_trades, len(short_lose_trades))
        total_avg_lose = safe_div(
            lose_total_lose_trades, len(long_lose_trades + short_lose_trades)
        )

        long_payoff_ratio = safe_div(long_avg_win, long_avg_lose)
        short_payoff_ratio = safe_div(short_avg_win, short_avg_lose)
        total_payoff_ratio = safe_div(total_avg_win, total_avg_lose)

        self.all_trades['payoff ratio'] = total_payoff_ratio
        self.long_trades['payoff ratio'] = long_payoff_ratio
        self.short_trades['payoff ratio'] = short_payoff_ratio

        # Maximum loss:

        long_max_loss = safe_min([trade.profit for trade in long_lose_trades])
        short_max_loss = safe_min([trade.profit for trade in short_lose_trades])
        total_max_loss = np.max([long_max_loss, short_max_loss])

        self.all_trades['max loss'] = total_max_loss
        self.long_trades['max loss'] = long_max_loss
        self.short_trades['max loss'] = short_max_loss

        # Maximum consecutive lossing trades:
        long_max_consecutives_lossing_trades = 0
        short_max_consecutives_lossing_trades = 0
        total_max_consecutives_lossing_trades = 0

        long_current_consecutives_lossing_trades = 0
        short_current_consecutives_lossing_trades = 0
        total_current_consecutives_lossing_trades = 0

        for k, trade in trade_list.trades_closed.items():
            if trade.type == "long" and trade.profit < 0:
                long_current_consecutives_lossing_trades += 1
                total_current_consecutives_lossing_trades += 1

            if trade.type == "short" and trade.profit < 0:
                short_current_consecutives_lossing_trades += 1
                total_current_consecutives_lossing_trades += 1

            if trade.type == "long" and trade.profit >= 0:
                if (
                    long_current_consecutives_lossing_trades
                    > long_max_consecutives_lossing_trades
                ):
                    long_max_consecutives_lossing_trades = (
                        long_current_consecutives_lossing_trades
                    )
                long_current_consecutives_lossing_trades = 0

                if (
                    total_current_consecutives_lossing_trades
                    > total_max_consecutives_lossing_trades
                ):
                    total_max_consecutives_lossing_trades = (
                        total_current_consecutives_lossing_trades
                    )
                total_current_consecutives_lossing_trades = 0

            if trade.type == "short" and trade.profit >= 0:
                if (
                    short_current_consecutives_lossing_trades
                    > short_max_consecutives_lossing_trades
                ):
                    short_max_consecutives_lossing_trades = (
                        short_current_consecutives_lossing_trades
                    )
                short_current_consecutives_lossing_trades = 0

                if (
                    total_current_consecutives_lossing_trades
                    > total_max_consecutives_lossing_trades
                ):
                    total_max_consecutives_lossing_trades = (
                        total_current_consecutives_lossing_trades
                    )
                total_current_consecutives_lossing_trades = 0

        if (
            long_current_consecutives_lossing_trades
            > long_max_consecutives_lossing_trades
        ):
            long_max_consecutives_lossing_trades = (
                long_current_consecutives_lossing_trades
            )

        if (
            short_current_consecutives_lossing_trades
            > short_max_consecutives_lossing_trades
        ):
            short_max_consecutives_lossing_trades = (
                short_current_consecutives_lossing_trades
            )

        if (
            total_current_consecutives_lossing_trades
            > total_max_consecutives_lossing_trades
        ):
            total_max_consecutives_lossing_trades = (
                total_current_consecutives_lossing_trades
            )

        self.all_trades['max consecutives lossing trades'] = total_max_consecutives_lossing_trades
        self.long_trades['max consecutives lossing trades'] = long_max_consecutives_lossing_trades
        self.short_trades['max consecutives lossing trades'] = short_max_consecutives_lossing_trades

        # exposure:

        long_exposure = safe_div(
            long_stats[long_stats["open_trades"] > 0][
                "open_trades"
            ].count(),
            long_stats["open_trades"].count(),
        )

        short_exposure = safe_div(
            short_stats[short_stats["open_trades"] > 0][
                "open_trades"
            ].count(),
            short_stats["open_trades"].count(),
        )

        global_exposure = safe_div(
            system_stats[system_stats["open_trades"] > 0][
                "open_trades"
            ].count(),
            system_stats["open_trades"].count(),
        )

        self.all_trades['exposure'] = global_exposure * 100
        self.long_trades['exposure'] = long_exposure * 100
        self.short_trades['exposure'] = short_exposure * 100

        # holding period:

        long_holding = safe_mean(
            [
                trade.num_days
                for k, trade in trade_list.trades_closed.items()
                if trade.type == "long"
            ]
        )
        short_holding = safe_mean(
            [
                trade.num_days
                for k, trade in trade_list.trades_closed.items()
                if trade.type == "short"
            ]
        )
        global_holding = safe_mean(
            [trade.num_days for k, trade in trade_list.trades_closed.items()]
        )

        self.all_trades['holding'] = global_holding
        self.long_trades['holding'] = long_holding
        self.short_trades['holding'] = short_holding

        # Length of the average winning trade to the average losing trade:

        long_wins_holding = safe_mean(
            [
                trade.num_days
                for k, trade in trade_list.trades_closed.items()
                if trade.type == "long" and trade.profit > 0
            ]
        )
        long_lose_holding = safe_mean(
            [
                trade.num_days
                for k, trade in trade_list.trades_closed.items()
                if trade.type == "long" and trade.profit <= 0
            ]
        )
        long_holding_ratio = safe_div(long_wins_holding, long_lose_holding)

        short_wins_holding = safe_mean(
            [
                trade.num_days
                for k, trade in trade_list.trades_closed.items()
                if trade.type == "short" and trade.profit > 0
            ]
        )
        short_lose_holding = safe_mean(
            [
                trade.num_days
                for k, trade in trade_list.trades_closed.items()
                if trade.type == "short" and trade.profit <= 0
            ]
        )
        short_holding_ratio = safe_div(short_wins_holding, short_lose_holding)

        global_wins_holding = safe_mean(
            [
                trade.num_days
                for k, trade in trade_list.trades_closed.items()
                if trade.profit > 0
            ]
        )
        global_lose_holding = safe_mean(
            [
                trade.num_days
                for k, trade in trade_list.trades_closed.items()
                if trade.profit <= 0
            ]
        )
        global_holding_ratio = safe_div(global_wins_holding, global_lose_holding)

        self.all_trades['holding ratio'] = global_holding_ratio
        self.long_trades['holding ratio'] = long_holding_ratio
        self.short_trades['holding ratio'] = short_holding_ratio

        # profit expectancy.

        l_trades = long_win_trades + long_lose_trades
        s_trades = short_win_trades + short_lose_trades
        g_trades = l_trades + s_trades

        long_expectancy = safe_mean([trade.profit for trade in l_trades])
        short_expectancy = safe_mean([trade.profit for trade in s_trades])
        global_expectancy = safe_mean([trade.profit for trade in g_trades])

        self.all_trades['expectancy'] = global_expectancy
        self.long_trades['expectancy'] = long_expectancy
        self.short_trades['expectancy'] = short_expectancy

        # maxDD

        l_max_drawn_down = max_drawdown_value(
            long_stats["profit_sequence"]
        )
        s_max_drawn_down = max_drawdown_value(
            short_stats["profit_sequence"]
        )
        g_max_drawn_down = max_drawdown_value(system_stats["profit_sequence"])

        self.all_trades['max draw drown']= g_max_drawn_down
        self.long_trades['max draw drown'] = l_max_drawn_down
        self.short_trades['max draw drown'] = s_max_drawn_down

        # Recovery ratio

        self.all_trades['recovery ratio'] = safe_div(net_total, g_max_drawn_down)
        self.long_trades['recovery ratio'] = safe_div(net_long, l_max_drawn_down)
        self.short_trades['recovery ratio'] = safe_div(net_short, s_max_drawn_down)

    def toDataFrame(self):
        idx = [
            "Num of trades",
            "Num of winning trades",
            "Num of losing trades",
            "Profit of Winners",
            "Loss of Lossers",
            "Net profit",
            "Initial capital",
            "Final Capital",
            "% Net profit",
            "Anualized % Net profit",
            "Profit Factor",
            "Percent Profitable",
            "Payoff Ratio",
            "Maximum loss",
            "Maximum consecutive lossing trades",
            " % exposure",
            "Holding period",
            "lengt of avg win / leng of avg lose",
            "Profit expectancy",
            "MaxDD",
            "Recovery Ratio",
        ]

        data = {
            "All trades": list(self.all_trades.values()),
            "Long trades": list(self.long_trades.values()),
            "Short trades": list(self.short_trades.values()),
        }

        all_trade_statistics = pd.DataFrame(data, index=idx)

        return all_trade_statistics.round(2)

