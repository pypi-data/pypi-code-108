import collections
import datetime
import datetime as dt
import logging
from pathlib import Path
from typing import Union, List

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

from kessho.datasources.yahoo import YahooResource

yahoo = YahooResource()

logger = logging.getLogger(__name__)



def _float(x: str) -> float:
    try:
        return float(x)
    except ValueError:
        return 0.0


def map_symbol(symbol):
    """
    Some stocks have different symbols in ZH than in NY
    """
    choice = {
        'TKY': 'TKY.BE',
        'LIS': 'LIS.V',
    }
    return choice.get(symbol) or symbol


def read_tx_efinance(filename: Union[str, Path], from_=None, to_=None):
    df = pd.read_csv(filename, encoding='iso8859_2', delimiter=';')

    to_ = to_ or dt.date.today()

    df.Nettobetrag = df.Nettobetrag.map(lambda x: _float(str(x).replace("'", "")))

    df.Symbol = df.Symbol.map(map_symbol)

    df.Stückpreis = df.Stückpreis.map(lambda x: _float(str(x).replace("'", "")))  # noqa
    df.Saldo = df.Saldo.map(lambda x: _float(str(x).replace("'", "")))
    del df['ISIN']
    del df["Auftrag #"]

    df.Name.replace(np.nan, "-", inplace=True, regex=True)
    df['Time'] = pd.to_datetime(df.Datum, format='%d-%m-%Y %H:%M:%S')
    df = df.sort_values(by='Time')
    df.Datum = pd.to_datetime(df.Datum.map(lambda x: x.split(" ")[0]), format='%d-%m-%Y').map(lambda x: x.date())
    df.rename(columns={'Datum': 'Date', "Nettobetrag in der Währung des Kontos": 'True_Net'}, inplace=True)
    df.True_Net = df.True_Net.map(lambda x: _float(str(x).replace("'", "")))
    df.drop(['Aufgelaufene Zinsen', 'Name'], axis=1, inplace=True)
    # df.set_index('Date', inplace=True)
    df = df[from_ <= df['Date']] if from_ else df
    df = df[df['Date'] <= to_]
    return df


def merge_by_date_index(df1, df2, how='inner'):
    df = pd.merge(df1, df2, left_on='Date',
                  right_on='Date', how=how)
    del df['Date']
    df.rename(columns={'key_0': 'Date'}, inplace=True)
    return df


def next_day(date):
    return datetime.datetime.fromordinal(date.toordinal() + 1)


def general_credit_or_debit(new_record, transaction):
    currency = transaction.Währung
    new_record[currency] = round(new_record[currency] + transaction.True_Net, 2)


def in_out_flow(new_record, transaction, forex):
    currency = transaction.Währung
    if currency != 'CHF':
        rate = forex.rate_for(currency, 'CHF', transaction.Date)
    else:
        rate = 1.0

    new_record[currency] = round(new_record[currency] + transaction.True_Net, 2)
    new_record['Giro'] = round(new_record['Giro'] - transaction.True_Net * rate, 2)


def trade_equity(new_record, transaction):
    symbol = transaction.Symbol
    num_shares = transaction.Anzahl
    curr = transaction.Währung

    new_record[curr] = round(new_record[curr] + transaction.True_Net, 2)
    if transaction.True_Net < 0:
        new_record[symbol] += num_shares
    else:
        new_record[symbol] -= num_shares


def trade_forex(new_record, transaction):
    curr = transaction.Währung

    new_record[curr] = round(new_record[curr] + transaction.True_Net, 2)


class PortfolioManager:

    def __init__(self, initial_amount, from_: dt.date = None, to_: dt.date = None, tx_file=None, tx_df=None):

        self.prices = {}

        to_ = to_ or dt.date.today()
        from_ = from_ or dt.date(1960, 1, 1)

        txdf = read_tx_efinance(tx_file, from_=from_, to_=to_) if tx_df is None else tx_df

        assert txdf is not None, "Either tx_file or tx_df need be provided"

        symbols = [map_symbol(symbol) for symbol in txdf.Symbol.dropna().unique()]

        print("Getting price data from yahoo...")

        symbols_with_data = []
        for symbol in symbols:

            symbol = map_symbol(symbol)

            # if symbol not in special_prices:
            try:
                df1 = yahoo.ohlcav(symbol, from_, to_)
                df1 = df1[['Date', 'Low', 'High', 'Adj Close']]
                self.prices[symbol] = dict(df1[['Date', 'Adj Close']].to_records(index=False))
                df1.columns = ['Date', f'{symbol} Low', f'{symbol} High', f'{symbol} Close']
                df1['Date'] = pd.to_datetime(df1['Date']).map(lambda d: d.date())
                txdf = pd.merge(txdf, df1, left_on='Date', right_on='Date', how='outer')
                symbols_with_data.append(symbol)
            except ValueError as e:
                logger.warning(f"Can't get price data for {symbol}")
                print(e)

        print("Done.")
        self.symbols = symbols_with_data

        self.txdf = txdf[txdf.Transaktionen.notna()]

        logger.info("Getting forex data for USD/CHF")
        self.forex = Forex(['USD', 'CHF'])

        self.actions = {'Kauf': trade_equity,
                        'Verkauf': trade_equity,
                        'Einzahlung': in_out_flow,
                        'Auszahlung': in_out_flow,
                        'Fx-Belastung Comp.': trade_forex,
                        'Fx-Gutschrift Comp.': trade_forex,
                        'Forex-Belastung': trade_forex,
                        'Forex-Gutschrift': trade_forex,
                        'Berichtigung Börsengeb.': general_credit_or_debit,
                        'Jahresgebühr': general_credit_or_debit,
                        'Zins': general_credit_or_debit,
                        'Titeleingang': None,
                        'Titelausgang': None}

        # first portfolio record one day before the first transaction
        start_date = min(self.txdf.Date)-dt.timedelta(days=1)

        self.portfolio_history = self.calc_portfolio_history(start_date, initial_amounts={'CHF': initial_amount})

    def initial_portfolio(self, initial_amounts):
        einzahlungen = self.txdf.Nettobetrag[self.txdf.Transaktionen == 'Einzahlung'].sum()
        auszahlungen = self.txdf.Nettobetrag[self.txdf.Transaktionen == 'Auszahlung'].sum()
        snapshot = {key: 0. for key in (['Giro', 'CHF', 'USD'] + list(self.symbols))}
        snapshot['CHF'] = initial_amounts['CHF']
        snapshot['networth'] = round(initial_amounts['CHF'] + einzahlungen + auszahlungen, 2)
        snapshot['Giro'] = round(einzahlungen + auszahlungen, 2)
        return snapshot

    def share_price(self, symbol: str, date: dt.date):
        return self.prices[symbol][date]

    def calc_networth(self, date, pr):

        usd_chf = self.forex.rate_for('USD', 'CHF', date)

        networth = (
                pr['Giro'] + pr['CHF'] +
                np.sum([self.share_price(symbol, date) * pr[symbol] * usd_chf
                        for symbol in self.symbols]) +
                pr['USD'] * usd_chf
        )
        networth = round(networth, 2)
        return networth

    def calc_portfolio_history(self, start_date, initial_amounts):
        portfolio_history = collections.OrderedDict()
        portfolio_history[start_date] = self.initial_portfolio(initial_amounts)
        # txdf must be time-ordered!
        previous_record = list(portfolio_history.values())[0]
        last_date = start_date
        for index, transaction in self.txdf.iterrows():

            record_date = transaction.Date

            if record_date != last_date:
                new_record = previous_record.copy()
            else:
                new_record = previous_record

            self.process(new_record, transaction)
            portfolio_history[record_date] = new_record

            last_date = record_date
            previous_record = new_record

        return portfolio_history

    def process(self, new_record, tx):
        record_date = tx.Date
        tx_type = tx.Transaktionen

        execute_booking = self.actions.get(tx_type)
        if execute_booking:
            execute_booking(new_record, tx, forex=self.forex)
            networth = self.calc_networth(record_date, new_record)
            new_record['networth'] = networth



