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


class Forex:
    """
    Wrapper that scrapes from currency-converter.org.uk
    """

    def __init__(self, currencies):

        self.forex = {}
        self.lookup = {}
        for cfrom in currencies:
            for cto in currencies:
                if cfrom != cto:
                    key = f'1{cfrom}={cto}'
                    url = ('https://www.currency-converter.org.uk/currency-rates' +
                           '/historical/table/%s-%s.html' % (cfrom, cto))
                    page = requests.get(url)
                    soup = BeautifulSoup(page.content, features="html.parser")

                    rows = soup.find(text='Friday').parent.parent.parent.findChildren('tr')[1:-1]

                    rates = [[row.findChildren('td')[1].text,
                              float(row.findChildren('td')[3].text.split(" ")[0])] for row in rows]

                    fx = pd.DataFrame(rates, columns=['Date', key])
                    fx.Date = pd.to_datetime(fx.Date, format="%d/%m/%Y").map(lambda d: d.date())
                    self.lookup[key] = dict(fx[['Date', key]].to_records(index=False))
                    fx.set_index('Date', inplace=True)
                    self.forex[key] = fx

    def rates_for(self, cfrom: str, cto: str) -> pd.DataFrame:
        return self.forex[f'1{cfrom}={cto}']

    def rate_for(self, cfrom: str, cto: str, date: dt.date) -> float:
        return self.lookup[f'1{cfrom}={cto}'][date]


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


def read_tx_efinance2(filename: Union[str, Path]):
    """
    Read Swiss Post e-finance transaction log, aggregate split trades
    """

    df = pd.read_csv(filename, encoding='iso8859_2', delimiter=';')

    # set currency as symbol for inflow/outflow
    #
    df['is_inout'] = ((df['Transaktionen'] == 'Auszahlung') |
                      (df['Transaktionen'] == 'Einzahlung') |
                      (df['Transaktionen'] == 'Jahresgebühr') |
                      (df['Transaktionen'] == 'Zins') |
                      (df['Transaktionen'] == 'Kosten für titel') |
                      (df['Transaktionen'] == 'Forex-Gutschrift') |
                      (df['Transaktionen'] == 'Forex-Belastung') |
                      (df['Transaktionen'] == 'Fx-Belastung Comp.') |
                      (df['Transaktionen'] == 'Fx-Gutschrift Comp.') |
                      (df['Transaktionen'] == 'Spesen Steuerauszug') |
                      (df['Transaktionen'] == 'Zins') |
                      (df['Transaktionen'] == 'Berichtigung Börsengeb.') |
                      (df['Transaktionen'] == 'Bonusprogramm') |
                      (df['Transaktionen'] == 'Dividende'))

    df['Symbol'] = np.where(df['is_inout'], df['Währung'], df['Symbol'])
    df.drop(columns=['Name', 'Auftrag #', 'ISIN', 'is_inout'], inplace=True)

    # type mapping
    #
    df['Date'] = df.Datum.map(lambda s: dt.datetime.strptime(s, '%d-%m-%Y %H:%M:%S').date())
    df['Nettobetrag'] = df['Nettobetrag'].map(lambda x: _float(str(x).replace("'", "")))
    df['Kosten'] = df['Kosten'].map(lambda x: _float(str(x).replace("'", "")))
    df['Anzahl'] = df['Anzahl'].map(lambda x: _float(str(x).replace("'", "")))
    df['Stückpreis'] = df['Stückpreis'].map(lambda x: _float(str(x).replace("'", "")))
    df['Nettobetrag in der Währung des Kontos'] = df['Nettobetrag in der Währung des Kontos'].map(
        lambda x: _float(str(x).replace("'", "")))
    df['Saldo'] = df['Saldo'].map(lambda x: _float(str(x).replace("'", "")))

    # aggregate by date, symbol, activity
    #
    trades = df.groupby(['Date', 'Symbol', 'Transaktionen']).agg(
        {'Nettobetrag': 'sum',
         'Anzahl': 'sum',
         'Kosten': 'sum',
         'Währung Nettobetrag': 'first',
         'Nettobetrag in der Währung des Kontos': 'sum',
         'Saldo': ['min', 'max', 'first'],
         'Währung': 'first'}).reset_index().copy()

    # clean up faulty records.
    #
    trades = trades[trades['Symbol'] != 'ZUEHLKE TECHNOL'].copy()

    # Rename the automatically created column names
    #
    trades['Net'] = trades[('Nettobetrag', 'sum')]
    trades.drop(columns=[('Nettobetrag', 'sum')], inplace=True)

    trades['Currency of Net'] = trades[('Währung Nettobetrag', 'first')]
    trades.drop(columns=[('Währung Nettobetrag', 'first')], inplace=True)

    trades['Cost'] = trades[('Kosten', 'sum')]
    trades.drop(columns=[('Kosten', 'sum')], inplace=True)

    trades['Quantity'] = trades[('Anzahl', 'sum')]
    trades.drop(columns=[('Anzahl', 'sum')], inplace=True)

    trades['Avg Price'] = np.abs(trades[('Nettobetrag in der Währung des Kontos', 'sum')] / trades['Quantity'])

    trades['Rel Cost'] = np.abs(100.0 * trades['Cost'] / trades[('Nettobetrag in der Währung des Kontos', 'sum')])

    trades['Net Amt on Acct'] = trades[('Nettobetrag in der Währung des Kontos', 'sum')]
    trades.drop(columns=[('Nettobetrag in der Währung des Kontos', 'sum')], inplace=True)

    trades['Acct'] = trades[('Währung', 'first')]
    trades.drop(columns=[('Währung', 'first')], inplace=True)

    trades['Total'] = np.where(trades['Transaktionen'] == 'Kauf',
                               trades[('Saldo', 'min')],
                               np.where(trades['Transaktionen'] == 'Verkauf',
                                        trades[('Saldo', 'max')],
                                        trades[('Saldo', 'first')]))

    trades.drop(columns=[('Saldo', 'min'), ('Saldo', 'max'), ('Saldo', 'first')], inplace=True)

    trades.rename(columns={'Transaktionen': 'Activity'}, inplace=True)

    # Re-establish a proper index (after clean up)
    #
    trades.columns = trades.columns.droplevel(level=1)

    trades.reset_index(inplace=True)

    trades.drop(columns=['index'], inplace=True)

    sort_and_check(trades)

    return trades


def sort_and_check(trades):
    """
    Sort the trades, such that the previous total plus the next sum of nets yields the next total.
    Note that this is impossible for interleaving trades. Still, it's good to do this whenever possible
    to have some kind of plausibility check.
    """

    for account in ['CHF', 'USD']:
        trades_acct = trades[trades['Acct'] == account]
        prev_total = 0.0
        for date in trades_acct['Date'].unique():
            probe = trades_acct[trades_acct['Date'] == date]
            indices = [t[0] for t in probe.iterrows()]
            if len(probe) > 1:
                # print(f'There are {len(probe)} records for {date}. Checking for swaps between {indices}')

                for k in range(len(probe) - 1):

                    lead = indices[k]
                    # print(f'Looking at head {lead}')

                    if np.round(prev_total + trades['Net Amt on Acct'].iloc[lead], 2) == np.round(
                            trades['Total'].iloc[lead], 2):
                        # print(f"Head {lead} is good. Continuing")
                        prev_total = trades['Total'].iloc[lead]
                        continue

                    # print("The head doesn't link to the prev. Trying to find a record to swap for head")
                    for index in indices[k + 1:]:

                        if np.round(prev_total + trades['Net Amt on Acct'].iloc[index], 2) == np.round(
                                trades['Total'].iloc[index], 2):
                            # print(f'--> swapping {lead} with {index}')
                            swap = trades.iloc[lead]
                            trades.iloc[lead] = trades.iloc[index]
                            trades.iloc[index] = swap

                            # The new lead defines the new total
                            prev_total = trades['Total'].iloc[lead]
                            # print(f"Total now {prev_total}")
                            break

                # Check the last for the day
                prev_total = trades['Total'].iloc[indices[-2]]
                if np.round(prev_total + trades['Net Amt on Acct'].iloc[indices[-1]], 2) != np.round(
                        trades['Total'].iloc[indices[-1]], 2):
                    print(
                        f"Warning: Record nr. {indices[-1]} on account {account} "
                        f"doesn't fit to prev total {prev_total} - interleaving trades?")

                prev_total = trades['Total'].iloc[indices[-1]]

            else:
                prev_total = probe['Total'].iloc[0]


def create_quotes_cache(positions: List[str], first_day: dt.date, last_day: dt.date, col='Close') -> dict:

    replacements = {'TKY': 'TKY.F'}

    cache = {}
    for pos in positions:
        symbol = replacements.get(pos) or pos
        quotes = yahoo.ohlcav(symbol, first_day, last_day + dt.timedelta(days=1))[['Date', col]]
        cache[pos] = dict(quotes.to_records(index=False))

    return cache
