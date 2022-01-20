# -*- coding: utf-8 -*-

# imprint: a program for creating documents from data and content templates
#
# Copyright (C) 2019  Joseph R. Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Author: Joseph Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
# Version: 13 Apr 2019: Initial Coding


"""
An implementation of the custom invoice handlers.

A string handler and a table handler are included.
"""

import pandas as pd

from haggis.files import ensure_extension
from haggis.files.docx import style_row, style_column

from imprint.handlers.table import fixed_width_table
from imprint.handlers.utilities import get_file


def _get_df(config, kwds):
    """
    Loads a formatted dataframe based on the configuration.

    Return
    ------
    df : pandas.DataFrame
        The loaded data. The index is a normalized version of the Label
        column.
    damage : float
        The incurred damage, removed from the dataframe.
    security_deposit : float
        The security deposit, removed from the dataframe.
    """
    file = get_file(config, kwds)
    df = pd.read_csv(file, header=0, index_col=None)
    df.set_index(df['Label'].str.title(), inplace=True)
    if 'Damage' in df.index:
        damage = df.loc['Damage', 'Price']
        df.drop(index='Damage', inplace=True)
    else:
        damage = 0.0
    security_deposit = df.loc['Security Deposit', 'Price']
    df.drop(index='Security Deposit', inplace=True)

    return df, damage, security_deposit


def damage_assessment(config, kwds):
    """
    Generate a sentence about property damage.

    The string is based on the numerical value of the damage, taken from
    the line labeled ``Damage`` in the financial data file. The line is
    optional and defaults to zero.

    The line labeled ``Security Deposit`` is compared against if any
    damage occurred. This line is mandatory.
    """
    df, damage, security_deposit = _get_df(config, kwds)

    if damage:
        start = ('The damage done to rental items was assessed at '
                 f'${damage:0.2f}')
        if damage <= security_deposit:
            return start + (', which has already been deducted from your '
                            'security deposit.')

        return start + (
            '. Since your security deposit was insufficient to cover the '
            f'amount, an additional ${damage - security_deposit:0.2f} has '
            'been billed to your account to make up for the difference.'
        )

    return (
        'No damage to rental items was found, so your security deposit has '
        'been applied to the amount due.'
    )


def invoice_table(config, kwds, doc, style, *, image_log_name=None):
    """
    Generate a table containing the actual invoice.

    The table will be 5 columns x (N + 3) rows, including a header row
    and index column. If damage is non-zero, the number of rows is
    (N + 4), with N being the number of items. Image logging is ignored.

    The data comes from a financial file in CSV format. The CSV must
    contain the columns "Label", "Price" and "Quantity". It must contain
    a row labeled "Security Deposit" and optionally one labeled "Damage".

    Configuration Keys
    ------------------
    file : str
        The name of the financial data CSV file (required).
    formatted : bool
        Whether ``file`` is a format string to be interpolated with the
        keywords, or just a raw string.
    """
    df, damage, security_deposit = _get_df(config, kwds)

    rows = df.shape[0] + 3 + bool(damage)

    table = fixed_width_table(doc, style, rows=rows, alignment='^',
                              col_widths=[0.25, 3.25, 1.0, 1.25, 1.25])

    for col, label in enumerate(('ITEM/SERVICE', 'PRICE',
                                 'QUANTITY', 'TOTAL'), start=1):
        table.cell(0, col).text = label

    for row, (index, item) in enumerate(df.iterrows(), start=1):
        table.cell(row, 0).text = f'{row:d}'
        table.cell(row, 1).text = f'{item["Label"]}'
        table.cell(row, 2).text = f'{item["Price"]:0.2f}'
        table.cell(row, 3).text = f'{item["Quantity"]:0.0f}'
        table.cell(row, 4).text = f'{item["Price"] * item["Quantity"]:0.2f}'

    if damage:
        row += 1
        table.cell(row, 0).text = 'X'
        table.cell(row, 1).text = 'Damages'
        table.cell(row, 2).text = f'{damage:0.2f}'
        table.cell(row, 3).text = '-'
        table.cell(row, 4).text = f'{damage:0.2f}'

    row += 1
    table.cell(row, 0).text = 'D'
    table.cell(row, 1).text = 'Security Deposit'
    table.cell(row, 2).text = f'({security_deposit:0.2f})'
    table.cell(row, 3).text = '-'
    table.cell(row, 4).text = f'-{security_deposit:0.2f}'

    row += 1
    total = (df['Price'].dot(df["Quantity"]) + damage - security_deposit)
    table.cell(row, 0).text = 'T'
    table.cell(row, 4).text = f'{total:0.2f}'

    style_column(doc, 'Cell Text',   table, 1)
    style_column(doc, 'Cell Number', table, 2)
    style_column(doc, 'Cell Number', table, 3)
    style_column(doc, 'Cell Number', table, 4)
    style_row(doc, 'Table Heading',  table, 0)
    style_row(doc, 'Strong',         table, -1)

    if image_log_name:
        with open(ensure_extension(image_log_name, '.csv'), 'w') as file:
            df.to_csv(file, index=False, float_format='%0.2f')
            print(f'Security Deposit,{security_deposit:0.2f}', file=file)
            print(f'Damage,{damage:0.2f}', file=file)
