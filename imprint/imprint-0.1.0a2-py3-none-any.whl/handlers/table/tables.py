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
:py:mod:`imprint.handlers.table.tables` contains basic built-in
:ref:`plugins-handlers` for inserting simple tables into a document.

All the handlers in this module are compatible with the
:ref:`plugin interface <plugins-tables-signature>` used by the
:ref:`xml-spec-tags-table` tag.

This module contains handlers that are only enabled when some optional
dependencies are installed. See :py:mod:`imprint.handlers.table` for
more information.
"""

import logging
from shutil import copyfile

try:
    import pandas as pd
except ImportError:
    from sys import stderr
    print('It appears that you do not have pandas installed. '
          'Try one of the following:\n\n'
          '    pip install imprint[all]\n\n'
          'OR\n\n'
          '    pip install pandas', file=stderr)
    raise

from haggis.files.docx import merge_row
from haggis.recipes import dict_select

from . import fixed_width_table
from ..utilities import get_file


__all__ = ['CSVFile', 'DataFrame']


#: Private logger for this module
_logger = logging.getLogger(__name__)


def CSVFile(config, kwds, doc, style, *, image_log_name=None):
    """
    Generate a table from a CSV file.

    Files can be parsed with or without header information. By default,
    the first row and column are both considered to be headers.

    If image logging is enabled (``image_log_name`` is not falsy), the
    contents of the file is copied to the specified output CSV file. A
    ``.csv`` extension will be appended to the name.

    The following :ref:`plugins-data-configuration` keys are used:

        file
            The (mandatory) file name.
        formatted
            Whether or not ``file`` is a format string that has keyword
            replacements in it. Defaults to truthy. Set to falsy if
            the name contains random opening braces.
        row_header
            Whether or not to treat the first row of the CSV as a table
            header. Optional, defaults to :py:obj:`True`.
        col_header
            Whether or not to treat the first column of the CSV as a
            table header. Optional, defaults to :py:obj:`True`.
        heading
            A text label that will appear across the entire first row of
            the table if specified.
        alignment
            The direction in which the table is to be aligned on the
            page. One of { ``'<'``, ``'^'``, ``'>'`` }. Defaults to
            center (``'^'``).
        width
            The size of the table, either as a number in inches, or a
            string representing a number with optional units. See
            :py:func:`haggis.files.docx.str2length` for a full list of
            units. Defaults to 7.0 inches.
        col_widths
            A sequence of column widths. If the sequence is longer than
            the actual number of columns, extra elements will be
            silently ignored. If shorter, the remaining *width* will be
            divided equally between remaining columns. If the sum of the
            used portion of *col_widths* is greater than *width*, an
            error will be raised. The elements of the sequence can be
            numbers in inches, or strings with optional units, just like
            *width*.
        row_height : None or length-spec or sequence[length-spec]
            The height to assign to each row. :py:obj:`None` is the
            default, meaning to let the rows adjust themselves. If a
            single number or numerical string with optional units, it
            will be applied to all the newly created rows. If a
            sequence, only the minimum of ``rows`` and the length of the
            sequence will be affected. A sequence may contain any of the
            values allowed as scalars (including :py:obj:`None`).

    Notes
    -----
    - Whether or not the headings appear as actual headings depends on
      the requested table style.
    - This plugin uses the `pandas`_ library rather than the builtin
      :py:mod:`csv` module to ensure data shape and type normalization.
    """
    input_path = get_file(config, kwds)
    _logger.trace('Loading datarame from %r', input_path)

    row_header = config.get('row_header', True)
    col_header = config.get('col_header', True)

    header = 0 if row_header else None
    index_col = 0 if col_header else None

    data_frame = pd.read_csv(input_path, header=header, index_col=index_col)

    df_config = {
        'data': data_frame,
        'header': row_header,
        'index': col_header,
    }
    df_config.update(dict_select(config, ('heading', 'alignment', 'width',
                                          'col_widths', 'row_height')))

    if image_log_name:
        copyfile(input_path, image_log_name + '.csv')

    return DataFrame(df_config, kwds, doc, style, image_log_name=None)


def DataFrame(config, kwds, doc, style, *, image_log_name=None):
    """
    Generate a table from a `pandas`_ :py:class:`~pandas.DataFrame`.

    Files can be parsed with or without header information. By default
    both the column names and the index are considered headers. Headers
    can be omitted on either side.

    If image logging is enabled (``image_log_name`` is not falsy), the
    contents of the dataframe is dumped to the specified file in CSV
    format. A ``.csv`` extension will be appended to the name.

    The following :ref:`plugins-data-configuration` keys are used:

        data
            The (mandatory) :py:class:`~pandas.DataFrame` to display.
        header
            Whether or not to use the column names as a table header.
            Defaults to :py:obj:`True`.
        index
            Whether or not to use the index as a table header. Defaults
            to :py:obj:`True`. If both *index* and *header* are truthy,
            The name of the index will appear in the upper-leftmost cell
            of the generated table.
        heading
            A text label that will appear across the entire first row of
            the table if specified.
        alignment
            The direction in which the table is to be aligned on the
            page. One of { ``'<'``, ``'^'``, ``'>'`` }. Defaults to
            center (``'^'``).
        width
            The size of the table, either as a number in inches, or a
            string representing a number with optional units. See
            :py:func:`haggis.files.docx.str2length` for a full list of
            units. Defaults to 7.0 inches.
        col_widths
            A sequence of column widths. If the sequence is longer than
            the actual number of columns, extra elements will be
            silently ignored. If shorter, the remaining *width* will be
            divided equally between remaining columns. If the sum of the
            used portion of *col_widths* is greater than *width*, an
            error will be raised. The elements of the sequence can be
            numbers in inches, or strings with optional units, just like
            *width*.
        row_height : None or length-spec or sequence[length-spec]
            The height to assign to each row. :py:obj:`None` is the
            default, meaning to let the rows adjust themselves. If a
            single number or numerical string with optional units, it
            will be applied to all the newly created rows. If a
            sequence, only the minimum of ``rows`` and the length of the
            sequence will be affected. A sequence may contain any of the
            values allowed as scalars (including :py:obj:`None`).

    Notes
    -----
    Whether or not the headings appear as actual headings depends on the
    requested table style.
    """
    data = config['data']

    label = config.get('heading')
    heading = bool(label)

    header = bool(config.get('header', True))
    index = bool(config.get('index', True))

    offset = header + heading

    rows = data.shape[0] + offset
    cols = data.shape[1] + index

    kwargs = dict_select(config, ('alignment', 'width',
                                  'col_widths', 'row_height'))
    table = fixed_width_table(doc, style, rows, cols, **kwargs)

    if heading:
        table.cell(0, 0).text = label
        merge_row(table, row=0)
    if header:
        for col, name in enumerate(data.columns, start=index):
            table.cell(heading, col).text = format(name)
    if index:
        for row, val in enumerate(data.index, start=offset):
            table.cell(row, 0).text = format(val)
        if header and data.index.name:
            table.cell(heading, 0).text = format(data.index.name)

    for r_t, r_df in enumerate(range(data.shape[0]), start=offset):
        for c_t, c_df in enumerate(range(data.shape[1]), start=index):
            table.cell(r_t, c_t).text = format(data.iloc[r_df, c_df])

    if image_log_name:
        data.to_csv(image_log_name + '.csv')
