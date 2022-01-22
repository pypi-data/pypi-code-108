import datetime as dt
from pathlib import Path
from typing import Union, List, Dict, Tuple
import logging

import numpy as np
import pandas as pd
from pydantic import BaseModel

from kessho.datasources.forex import Forex
from kessho.datasources.yahoo import YahooResource

logger = logging.getLogger(__name__)


class HoldingPeriod(BaseModel):

    symbol: str
    qty: int

    value_sell: float
    date_sell: dt.date

    value_buy: float
    date_buy: dt.date

    currency: str
    cost: float
    cdgr: float
    pl: float
    pl_rel: float


class TxRecord(BaseModel):
    symbol: str
    tx: str
    cost: float
    curr: str
    qty: int
    price: float
    date: dt.date
    time: dt.time


class PortfolioManager:

    def __init__(self, file_name: Union[str, Path], main_currency: str,
                 special_names: Dict[str, Tuple[str, str]] = None, forex=None, as_of=None):

        self.ACTIONS = {
            'Kauf': self.buy,
            'Verkauf': self.sell,
            'Jahresgebühr': self.other_fee,
            'Einzahlung': self.inout,
            'Auszahlung': self.inout,
            'Zins': self.other_fee,
            'Fx-Belastung Comp.': self.forex,
            'Fx-Gutschrift Comp.': self.forex,
            'Forex-Belastung': self.forex,
            'Forex-Gutschrift': self.forex,
            'Berichtigung Börsengeb.': self.other_fee,
            'Dividende': self.dividend,
            'Bonusprogramm': self.other_fee,
            'Kosten für titel': self.other_fee,
            'Spesen Steuerauszug': self.other_fee,
        }
        self.as_of = as_of or dt.date.today()

        self.yahoo = YahooResource()
        self.filename = file_name
        self.main_currency = main_currency
        self.special_names = special_names
        self.trades = self.read_efinance_tx(self.filename)
        self.accounts = list(self.trades.Acct.unique())
        self.currencies = list(self.trades['Currency of Net'].unique())
        currency_pairs = [(c, main_currency) for c in self.currencies if c != main_currency]
        self.forex = forex(currency_pairs) if forex else Forex(currency_pairs)
        self.ts = self.create_time_series(self.trades, special_cases=self.special_names)
        self.compute_portfolio_value()

    def get_all_names(self, from_: dt.date = None, to_: dt.date = None):

        trades = self.trades[self.trades['Date'] >= from_] if from_ else self.trades
        trades = trades[trades['Date'] <= to_] if to_ else trades
        symbols = set(trades['Symbol'].unique())
        currencies = set(trades['Currency of Net'].unique())
        return symbols.difference(currencies)

    def compute_portfolio_value(self):
        cols = [c.split('_')[1] for c in self.ts.columns if 'Q_' in c]

        def eod_value(r, special_names):
            to_chf = {
                curr: self.forex.rate_for(curr, 'CHF', r['Date'])
                for curr in self.currencies if curr != self.main_currency
            }
            value = sum([r[f'P_{c}'] * r[f'Q_{c}'] for c in cols if c not in self.special_names])
            value *= to_chf['USD']

            converted_amounts = sum([r[f'P_{name}'] * r[f'Q_{name}'] * to_chf[currency]
                                     for name, (alias, currency) in special_names.items()
                                     if currency in self.currencies])

            value += converted_amounts + r['Base Acct']

            return value + r[self.main_currency] + sum([r[acct] * to_chf[acct]
                                                        for acct in self.accounts if acct != self.main_currency])

        self.ts['Portfolio'] = self.ts.apply(lambda r: eod_value(r, self.special_names), axis=1)

    #
    #  Read the TX file
    #
    @staticmethod
    def read_efinance_tx(filename: Union[str, Path]) -> pd.DataFrame:
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
        df.drop(columns=['Name', 'ISIN', 'is_inout'], inplace=True)

        # type mapping
        #
        df['Date'] = df.Datum.map(lambda s: dt.datetime.strptime(s, '%d-%m-%Y %H:%M:%S').date())
        df['Time'] = df.Datum.map(lambda s: dt.datetime.strptime(s, '%d-%m-%Y %H:%M:%S').time())
        df['Nettobetrag'] = df['Nettobetrag'].map(lambda x: _float(str(x).replace("'", "")))
        df['Kosten'] = df['Kosten'].map(lambda x: _float(str(x).replace("'", "")))
        df['Anzahl'] = df['Anzahl'].map(lambda x: _float(str(x).replace("'", "")))
        df['Stückpreis'] = df['Stückpreis'].map(lambda x: _float(str(x).replace("'", "")))

        # Apply split adjustments to records prior to the split, because quotes will be adjusted retro-actively.
        splits = {'SOXL': (dt.date(2021, 3, 2), 15.0)}
        for symbol, split in splits.items():
            date, factor = split
            df['Anzahl'] = np.where((df['Date'] < date) & (df['Symbol'] == symbol),
                                    df['Anzahl'] * factor, df['Anzahl'])
            df['Stückpreis'] = np.where((df['Date'] < date) & (df['Symbol'] == symbol),
                                        df['Stückpreis'] / factor, df['Stückpreis'])

        df['Nettobetrag in der Währung des Kontos'] = df['Nettobetrag in der Währung des Kontos'].map(
            lambda x: _float(str(x).replace("'", "")))
        df['Saldo'] = df['Saldo'].map(lambda x: _float(str(x).replace("'", "")))

        # aggregate by date, symbol, activity
        #
        trades = df.groupby(['Date', 'Symbol', 'Transaktionen', 'Auftrag #']).agg(
            {'Nettobetrag': 'sum',
             'Anzahl': 'sum',
             'Kosten': 'sum',
             'Time': 'first',
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

        PortfolioManager.sort_and_check(trades)

        return trades

    #
    #    Sort and verfiy intermediate totals
    #
    @staticmethod
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

    #
    #   Cache the quotes once for the entire time series
    #
    def create_quotes_cache(self, positions: List[str], first_day: dt.date, last_day: dt.date,
                            col='Close', special=None) -> dict:
        """
        :param positions: A list of symbols to look up prices for.
        :param first_day: The first day to look up prices for.
        :param last_day: The last day to look up prices for.
        :param col: the column of the yahoo table to use. Defaults to 'Close'.
        :param special: a map: {symbol_orig: (symbol_yahoo, currency)} to deal with special cases like eg.
            TKY being represented by the symbol TKY.F on yahoo. And if the currency reported from yahoo is not USD,
            then this is also specified here.
        """
        special = special or dict()

        cache = {}
        for pos in positions:
            symbol, currency = special.get(pos) or (pos, 'USD')
            quotes = self.yahoo.ohlcav(symbol, first_day, last_day + dt.timedelta(days=1))[['Date', col]]
            cache[pos] = dict(quotes.to_records(index=False))

        return cache

    #
    #    Create a continuous time series from the events
    #
    def create_time_series(self, txdf: pd.DataFrame, positions: List[str] = None,
                           first_day=None, last_day=None,
                           special_cases: Dict[str, Tuple[str, str]] = None) -> pd.DataFrame:
        """
        :param txdf: pandas dataframe of transactions
        :param positions: specify to only create timeseries of a subset of involved names.
        :param first_day: first day of the desired timeseries
        :param last_day: last day of the desired timeseries
        :param special_cases: a dictionary like {'TKY', ('TKY.F', 'EUR')} to look up symbol and curr for names listed
        on non-US exchanges.
        """
        positions = positions or list(txdf.Symbol.unique())
        first_day = first_day or min(txdf.Date)
        last_day = last_day or dt.date.today() - dt.timedelta(days=1)

        records = []
        accounts = list(txdf.Acct.unique())
        for c in accounts:
            if c in positions:
                positions.remove(c)

        prices = self.create_quotes_cache(positions, first_day, last_day, special=special_cases)

        initial_base = (sum(txdf.iloc[np.where(txdf['Activity'] == 'Einzahlung')]['Net']) +
                        sum(txdf.iloc[np.where(txdf['Activity'] == 'Auszahlung')]['Net']))

        cols = accounts + [f'P_{pos}' for pos in positions] + [f'Q_{pos}' for pos in positions]
        record = {c: 0.0 for c in cols}
        record['Tx Fee'] = 0.0
        record['Base Acct'] = round(initial_base, 2)
        record['Dividend'] = 0.0
        record['Other Fees'] = 0.0
        record['Tx Fees'] = 0.0

        logs = []
        for day in pd.date_range(first_day, last_day):
            day = day.date()
            record = record.copy()
            record['In-Out'] = 0.0
            for pos in positions:
                try:
                    record[f'P_{pos}'] = np.round(prices[pos][day], 2)
                except KeyError:
                    # A key error may mean that the symbol is not being traded on that day. Maybe it's not IPO'd yet.
                    record[f'P_{pos}'] = 0.0
            record['Date'] = day
            records.append(record)
            trades = txdf[txdf['Date'] == day]

            for _, tx in trades.iterrows():
                action = self.ACTIONS.get(tx.Activity) or self.warn
                logs.append(action(tx, record))

        return pd.DataFrame.from_records(records)

    #
    #   Holding periods and their returns for success analysis
    #
    def compute_holdings_history(self, symbol: str) -> pd.DataFrame:

        finished = False
        holding_periods = []
        records = self.prepare_for_symbol(symbol)

        while not finished:  # Continue while there are non-zero 'Sell' records

            finished = True
            balance = 0
            r_out = None

            for r in records:

                if r.qty > 0.0:
                    if r.qty == 25200:
                        print('hello')
                    # The first of a possible sequence of sell actions
                    if r.tx == 'Verkauf':
                        if balance == 0:
                            finished = False
                            balance += r.qty
                            r_out = r
                        continue  # skip any subsequent

                    # Now we need to find sufficient purchases to substantiate the sale
                    if r.tx == 'Kauf' and balance > 0:
                        r_in = r
                        qty = min(r_out.qty, r_in.qty)

                        # Here, we strongly assume that buying and selling use the same currency
                        hp = self.extract_holding_period(symbol, qty, r.curr, r_in, r_out)

                        holding_periods.append(hp)
                        balance -= qty
                        if balance == 0:
                            break  # the sale is sufficiently substantiated, start from the beginning
                        else:
                            continue

            if balance:
                logger.warning("Can't sell what you didn't buy before...;-(")
                logger.warning("Are your sure your tx file is complete?")
                finished = True

        # There may be lots we haven't sold yet, each one of those will be evaluated as if selling now
        remainder = [r for r in records if r.qty > 0 and r.tx == 'Kauf']
        for r_in in remainder:

            prices = self.yahoo.ohlcav(symbol, from_=self.as_of - dt.timedelta(days=5), to_=self.as_of)
            price = prices.iloc[-1]['Close']
            r_out = TxRecord(symbol=symbol, cost=r_in.cost, curr=r_in.curr, qty=r_in.qty, price=price,
                             date=self.as_of, time=r_in.time, tx='Verkauf')

            # Here, we strongly assume that buying and selling use the same currency
            hp = self.extract_holding_period(symbol, r_in.qty, r_in.curr, r_in, r_out)
            holding_periods.append(hp)

        ret = pd.DataFrame.from_records([dict(hp) for hp in holding_periods])

        # sort by buy decision date, which is usually more relevant
        return ret if len(ret) == 0 else ret.sort_values(by='date_buy', ascending=True)

    @staticmethod
    def extract_holding_period(symbol: str, qty: int, curr: str, r_buy: TxRecord, r_sell: TxRecord):

        days = (r_sell.date - r_buy.date).days
        sell_amt = qty * r_sell.price
        buy_amt = qty * r_buy.price
        sell_cost = r_sell.cost * qty / r_sell.qty
        buy_cost = r_buy.cost * qty / r_buy.qty
        cost = sell_cost + buy_cost

        holding_period = HoldingPeriod(
            symbol=symbol,
            qty=qty,
            currency=curr,

            value_sell=round(sell_amt, 2),
            date_sell=r_sell.date,

            value_buy=buy_amt,
            date_buy=r_buy.date,

            cost=cost,
            cdgr=round(np.log((sell_amt - cost) / buy_amt) * 1.0 / (days + 1) * 100., 2),
            pl=round(sell_amt - buy_amt - cost, 2),
            pl_rel=round(100*np.log(sell_amt / buy_amt), 2))

        r_buy.qty -= qty
        r_sell.qty -= qty

        return holding_period

    def prepare_for_symbol(self, symbol: str) -> List[TxRecord]:
        transactions = self.trades
        trades = transactions[(transactions['Activity'] == 'Kauf') | (transactions['Activity'] == 'Verkauf')]
        records = trades[trades['Symbol'] == symbol].copy()
        records.sort_index(ascending=False, inplace=True)
        records.rename(columns={'Net Amt on Acct': 'Amount', 'Avg Price': 'Price'},
                       inplace=True)
        return [TxRecord(symbol=symbol, cost=round(r.Cost, 2), curr=r.Acct,
                         qty=r.Quantity, price=round(r.Price, 2),
                         date=r.Date, time=r.Time, tx=r.Activity)
                for r in records.itertuples()]

    #
    #   For debugging purposes
    #
    @staticmethod
    def log_record(activity, amt, total, prev, curr, *keys):
        records = [{'Activity': 'Previous', 'Amount': 0.0, 'Total': np.nan},
                   {'Activity': activity, 'Amount': amt, 'Total': total}]
        for n, row in enumerate([prev, curr]):
            records[n].update({key: row[key] for key in keys})
            records[n]['Date'] = row['Date']
        df = pd.DataFrame.from_records(records)
        return df

    def buy(self, tx, record):
        prev_record = record.copy()
        symbol = tx.Symbol
        acct = tx.Acct
        qty = tx.Quantity
        net = tx['Net Amt on Acct']
        total = tx['Total']

        from_curr = tx['Currency of Net']
        to_curr = self.main_currency
        fx_rate = self.forex.rate_for(from_curr, to_curr, tx['Date'])

        record[f'Q_{symbol}'] = np.round(record[f'Q_{symbol}'] + qty, 2)
        record[acct] = np.round(record[acct] + net, 2)
        record['Tx Fee'] = np.round(record['Tx Fee'] + tx.Cost * fx_rate, 2)
        return self.log_record('buy', net, total, prev_record, record, f'Q_{symbol}', acct, 'Tx Fee')

    def sell(self, tx, record):
        prev_record = record.copy()
        symbol = tx.Symbol
        acct = tx.Acct
        qty = tx.Quantity
        net = tx['Net Amt on Acct']
        total = tx['Total']

        from_curr = tx['Currency of Net']
        to_curr = self.main_currency
        fx_rate = self.forex.rate_for(from_curr, to_curr, tx['Date'])

        record[f'Q_{symbol}'] = np.round(record[f'Q_{symbol}'] - qty, 2)
        record[acct] = np.round(record[acct] + net, 2)
        record['Tx Fee'] = np.round(record['Tx Fee'] + tx.Cost * fx_rate, 2)
        return self.log_record('sell', net, total, prev_record, record, f'Q_{symbol}', acct, 'Tx Fee')

    def other_fee(self, tx, record):
        net = tx['Net Amt on Acct']
        total = tx['Total']
        prev_record = record.copy()
        record[tx['Acct']] = np.round(record[tx['Acct']] + tx['Net'], 2)
        record['Other Fees'] = np.round(record['Other Fees'] - tx['Net'], 2)
        return self.log_record(tx['Activity'], net, total, prev_record, record, tx['Acct'], 'Other Fees')

    def inout(self, tx, record):
        net = tx['Net Amt on Acct']
        total = tx['Total']
        prev_record = record.copy()
        record[tx['Acct']] = np.round(record[tx['Acct']] + tx['Net Amt on Acct'], 2)
        record['Base Acct'] = np.round(record['Base Acct'] - tx['Net Amt on Acct'], 2)
        record['In-Out'] = np.round(tx['Net Amt on Acct'], 2)
        return self.log_record(tx['Activity'], net, total, prev_record, record, tx['Acct'], 'Base Acct')

    def forex(self, tx, record):
        net = tx['Net Amt on Acct']
        total = tx['Total']
        prev_record = record.copy()

        # forex records come in pairs, each one with its own currency
        record[tx['Acct']] = np.round(record[tx['Acct']] + tx['Net Amt on Acct'], 2)
        return self.log_record(tx['Activity'], net, total, prev_record, record, tx['Acct'])

    def dividend(self, tx, record):
        net = tx['Net Amt on Acct']
        total = tx['Total']
        prev_record = record.copy()

        from_curr = tx['Currency of Net']
        to_curr = self.main_currency
        fx_rate = self.forex.rate_for(from_curr, to_curr, tx['Date'])

        record[tx['Acct']] = np.round(record[tx['Acct']] + net, 2)
        record['Dividend'] = np.round(record['Dividend'] + net * fx_rate, 2)
        record['Other Fees'] = np.round(record['Other Fees'] - tx.Cost * fx_rate, 2)
        return self.log_record('Dividend', net, total, prev_record, record, tx['Acct'], 'Dividend')

    def warn(self, tx, _):
        raise ValueError(f"No such action: {tx.Activity}")


#
#         Specialized utitlity functions
#
def _float(x: str) -> float:
    try:
        return float(x)
    except ValueError:
        return 0.0
