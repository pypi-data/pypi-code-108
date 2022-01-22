import os
from pathlib import Path
import datetime as dt

from unittest import TestCase

from kessho.portfolio.tools import Forex, PortfolioManager


class ForexTest(TestCase):

    def test_forex(self):

        usd = 'USD'
        chf = 'CHF'

        forex = Forex( ['USD', 'CHF'])
        self.assertIsNotNone(forex.forex)

        usd_chf = forex.rates_for(usd, chf)
        self.assertFalse(usd_chf.isna()['1USD=CHF'].all())
        self.assertGreater(len(usd_chf), 0)

        usd_chf_1 = forex.rate_for(usd, chf, dt.date(2021, 1, 1))
        usd_chf_2 = 1/ forex.rate_for(chf, usd, dt.date(2021, 1, 1))

        self.assertAlmostEqual(usd_chf_1, usd_chf_2, places=3)


class PortfolioManagerTest(TestCase):

    def setUp(self):
        self.tx_file = Path(os.getcwd()) / 'fixtures' / 'transactions.csv'

    def test_portfolio_manager(self):
        pm = PortfolioManager(initial_amount=100, from_=dt.date(2021, 4, 1),
                              tx_file=self.tx_file)
        self.assertTrue(pm is not None)

