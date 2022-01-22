import datetime as dt
import os
from pathlib import Path
from unittest import TestCase

import pandas as pd

from kessho.datasources.forex import AbstractForex
from kessho.portfolio.efinance import PortfolioManager


class DummyForex(AbstractForex):

    def rates_for(self, cfrom: str, cto: str) -> pd.DataFrame:
        raise NotImplementedError("Use rate_for() instead.")

    def rate_for(self, cfrom: str, cto: str, date: dt.date) -> float:
        return 1.0


class EFinancePortfolioManagerTests(TestCase):

    def test_read_efinance_tx(self):
        tx_file = Path(os.getcwd()) / 'fixtures' / 'transactions-12062021.csv'
        df = PortfolioManager.read_efinance_tx(tx_file)
        symbols = set(df['Symbol'].unique()).difference(['CHF'])
        for symbol in symbols:
            bought = df[(df['Symbol'] == symbol) & (df['Activity'] == 'Kauf')]['Quantity'].sum()
            sold = df[(df['Symbol'] == symbol) & (df['Activity'] == 'Verkauf')]['Quantity'].sum()
            print(f"{symbol}: {bought - sold}")

    @staticmethod
    def _balance(df, symbol):
        bought = df[(df['Symbol'] == symbol) & (df['Activity'] == 'Kauf')]['Quantity'].sum()
        sold = df[(df['Symbol'] == symbol) & (df['Activity'] == 'Verkauf')]['Quantity'].sum()
        return bought - sold

    def test_create_instance(self):
        tx_file = Path(os.getcwd()) / 'fixtures' / 'transactions-12062021.csv'
        pm = PortfolioManager(tx_file, main_currency='CHF',
                              special_names={
                                  'LIS': ('LIS.V', 'CAD'),
                                  'TKY': ('TKY.BE', 'EUR')
                              })

        self.assertIn('USD', pm.accounts)
        self.assertIn('CHF', pm.accounts)
        self.assertIn('USD', pm.currencies)
        self.assertIn('CHF', pm.currencies)
        self.assertIn('EUR', pm.currencies)
        self.assertIn('CAD', pm.currencies)
        self.assertEqual(3, len(pm.forex.forex))

    def test_holdings_history(self):
        pm = self._pm()
        balance = self._balance(pm.trades, 'SXC')
        history = pm.compute_holdings_history('SXC')
        for symbol in pm.get_all_names():
            history = pm.compute_holdings_history(symbol)

    def test_get_all_names(self):
        pm = self._pm()
        names = pm.get_all_names(from_=dt.date(2021, 1, 1), to_=dt.date(2021, 6, 11))
        self.assertIn('GEO', names)
        names = pm.get_all_names(to_=dt.date(2021, 6, 11))
        self.assertIn('GEO', names)
        names = pm.get_all_names(from_=dt.date(2021, 1, 1))
        self.assertIn('GEO', names)

    @staticmethod
    def _pm():
        tx_file = Path(os.getcwd()) / 'fixtures' / 'transactions-since-April-2021.csv'
        pm = PortfolioManager(tx_file, main_currency='CHF',
                              special_names={
                                  'LIS': ('LIS.V', 'CAD')
                              }, forex=lambda _: DummyForex())
        return pm
