# -*- coding: utf-8 -*-
"""Functions from market data"""

__author__ = "Miguel Martin"
__version__ = "1"

import numpy as np
from pyquanttrade.engine.utils import (
    max_drawdown_ratio,
    max_drawdown_value,
    safe_div,
    safe_min,
    safe_sum,
    safe_mean,
)
from pyquanttrade.engine.test_summary import TestSummary
from pyquanttrade.engine.stats.daily_stats import DailyStats
from pyquanttrade.engine.stats.summary_stats import SystemSummaryStats
from pyquanttrade.engine.stats.trade_stats import TradeSummaryStats
from pyquanttrade.engine.trade import TradeList


class TestResult:
    def __init__(self, data_sim, ticker, capital):
        self.data = DailyStats(data_sim, ticker, capital)
        self.capital = capital

    def add_ticker(self, data_sim, ticker, capital):
        self.data.add_ticker(data_sim, ticker, capital)   

    def update(self, i, trade_list, ticker):
        self.data.update(i,trade_list, ticker)

    def describe(self, baseline=False):
        self.data.generate_all_stats()

        summary_stats = SystemSummaryStats(self.data)
        trade_summary_stats = {ticker:TradeSummaryStats(self.data.trade_list.clone(ticker), 
                                                        self.data.long_ticker[ticker], 
                                                        self.data.short_ticker[ticker], 
                                                        self.data.global_ticker[ticker], 
                                                        self.data.tickers_capital[ticker]) for ticker in self.data.tickers}
        
        trade_summary_stats['all'] = TradeSummaryStats(self.data.trade_list, self.data.long_all, self.data.short_all, self.data.global_all, np.sum(list(self.data.tickers_capital.values())))
        
        trade_summary_table = {t:v.toDataFrame() for (t,v) in  trade_summary_stats.items()}
        return TestSummary(summary_stats.ticker_stats, trade_summary_table)


