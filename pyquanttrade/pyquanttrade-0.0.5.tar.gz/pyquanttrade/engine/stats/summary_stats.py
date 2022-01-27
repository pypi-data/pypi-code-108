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

class SystemSummaryStats:

    def __init__(self, data_stats):
        self.ticker_stats = {ticker:self._get_system_table_stats(data_stats.long_ticker[ticker], data_stats.short_ticker[ticker], data_stats.global_ticker[ticker], data_stats.tickers_capital[ticker]) for ticker in data_stats.tickers}
        all_capital = np.sum(list(data_stats.tickers_capital.values()))
        self.ticker_stats['all'] = self._get_system_table_stats(data_stats.long_all, data_stats.short_all, data_stats.global_all, all_capital)
    
    def  _generate_system_stats(self, system_results, capital):

        sim_years = system_results.shape[0] / 250
        profit = (
            system_results["Daily_capital"].tail(1)[0] - capital
        ) / capital
        global_results = [100 * profit]

        anual_net_profit_ratio = 100 * ((profit + 1) ** (1 / sim_years) - 1)
        global_results += [anual_net_profit_ratio]

        max_drawn_down = 100 * (max_drawdown_ratio(system_results["Daily_capital"]))
        global_results += [max_drawn_down]

        if max_drawn_down == 0:
            ajusted_annual_return = 0.0
        else:
            ajusted_annual_return = 100 * (anual_net_profit_ratio / max_drawn_down)
        global_results += [ajusted_annual_return]

        return global_results
    
    
    def _get_system_table_stats(self, long, short, system, capital):

        idx = [
            "Net profit%",
            "Annual Return %",
            "Max DrawDown",
            "Risk Adjusted Return %",
        ]


        data = {
            "All trades": self._generate_system_stats(system, capital),
            "Long trades": self._generate_system_stats(long, capital),
            "Short trades": self._generate_system_stats(short, capital),
        }

        return pd.DataFrame(data, index=idx).round(2)
    


