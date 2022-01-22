import datetime as dt
import os
from pathlib import Path
from unittest import TestCase

from kessho.portfolio.time_series import create_time_series
from kessho.portfolio.tools import read_tx_efinance2, create_quotes_cache


class EFinanceTxFileTests(TestCase):

    def setUp(self):
        self.tx_file = Path(os.getcwd()) / 'fixtures' / 'transactions.csv'

    def test_read_tx_efincance2(self):

        transactions = read_tx_efinance2(self.tx_file)
        self.assertTrue(len(transactions) > 0)

    def test_portfolio_manager(self):
        transactions = read_tx_efinance2(self.tx_file)

        all_pos = ['GME', 'AMD', 'WMT', 'TSM', 'TKY', 'ALGN', 'NVDA', 'SWKS', 'AMAT', 'MTW']
        first_day = dt.date(2019, 10, 1)
        last_day = dt.date(2019, 10, 31)

        res = create_time_series(transactions, all_pos,
                                 first_day=first_day,
                                 last_day=last_day)

        self.assertTrue(res is not None)

