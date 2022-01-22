import datetime as dt
from typing import List

import numpy as np
import pandas as pd

from kessho.portfolio.tools import create_quotes_cache


def create_time_series(txdf: pd.DataFrame, positions: List[str] = None,
                       first_day=None, last_day=None) -> pd.DataFrame:

    positions = positions or list(txdf.Symbol.unique())
    first_day = first_day or min(txdf.Date)
    last_day = last_day or dt.date.today()

    records = []
    currencies = list(txdf.Acct.unique())
    for c in currencies:
        if c in positions:
            positions.remove(c)
    prices = create_quotes_cache(positions, first_day, last_day)

    cols = currencies + [f'P_{pos}' for pos in positions] + [f'Q_{pos}' for pos in positions]
    record = {c: 0.0 for c in cols}
    record['Tx Fee'] = 0.0

    for day in pd.date_range(first_day, last_day):
        day = day.date()
        record = record.copy()
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
            action = ACTIONS.get(tx.Activity) or warn
            action(tx, record)

    return pd.DataFrame.from_records(records)


def buy(tx, record):
    symbol = tx.Symbol
    acct = tx.Acct
    qty = tx.Quantity
    net = tx['Net Amt on Acct']

    record[f'Q_{symbol}'] = np.round(record[f'Q_{symbol}'] + qty, 2)
    record[acct] = np.round(record[acct] + net, 2)
    record['Tx Fee'] = np.round(record['Tx Fee'] + tx.Cost, 2)
    return record


def sell(tx, record):
    symbol = tx.Symbol
    acct = tx.Acct
    qty = tx.Quantity
    net = tx['Net Amt on Acct']

    record[f'Q_{symbol}'] = np.round(record[f'Q_{symbol}'] + qty, 2)
    record[acct] = np.round(record[acct] + net, 2)
    record['Tx Fee'] = np.round(record['Tx Fee'] + tx.Cost, 2)
    return record


def inout(tx, record):
    record[tx['Acct']] = np.round(record[tx['Acct']] + tx['Net Amt on Acct'], 2)
    return record


def warn(tx, _):
    raise ValueError(f"No such action: {tx.Activity}")


ACTIONS = {
    'Kauf': buy,
    'Verkauf': sell,
    'Jahresgebühr': inout,
    'Einzahlung': inout,
    'Auszahlung': inout,
    'Zins': inout,
    'Fx-Belastung Comp.': inout,
    'Fx-Gutschrift Comp.': inout,
    'Forex-Belastung': inout,
    'Forex-Gutschrift': inout,
    'Berichtigung Börsengeb.': inout,
    'Dividende': inout,
    'Bonusprogramm': inout,
    'Kosten für titel': inout,
    'Spesen Steuerauszug': inout,
}
