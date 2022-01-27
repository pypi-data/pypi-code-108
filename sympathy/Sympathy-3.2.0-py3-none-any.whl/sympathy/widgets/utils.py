# This file is part of Sympathy for Data.
# Copyright (c) 2019 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import lxml.html

from Qt import QtWidgets, QtCore


def table_values_to_clipboard(values, headers=None):
    """
    Put the values into the clipboard in a format understood by many other
    applications (incl. Excel).

    values should be a list of lists of table values, where each inner list
    represents one row of values.
    """
    def escape_html(text):
        return (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;'))

    if headers is None:
        headers = []

    if not values:
        return
    elif len(values) == 1 and len(values[0]) == 1 and not headers:
        # Only a single value was selected. Copy it without the table.
        csv = str(values[0][0])
        html = escape_html(str(values[0][0]))
    else:
        csv_lines = []
        html_lines = ['<html><body><table>']

        if headers:
            html_lines.append('<thead><tr>')
            html_lines.extend('<th>{}</th>'.format(
                escape_html(str(header))) for header in headers)
            html_lines.append('</tr></thead>')

        html_lines.append('<tbody>')
        for row_i, row in enumerate(values):
            html_row_values = []
            for col_i, value in enumerate(row):
                html_row_values.append('<td>{}</td>'.format(
                    escape_html(str(value))))

            csv_lines.append('\t'.join([str(v) for v in row]))
            html_lines.append('<tr>')
            html_lines.extend(html_row_values)
            html_lines.append('</tr>')
        html_lines.append('</tbody>')
        html_lines.append('</table></body></html>')
        csv = '\n'.join(csv_lines)
        html = '\n'.join(html_lines)

    mime_data = QtCore.QMimeData()
    mime_data.setHtml(html)
    mime_data.setText(csv)
    QtWidgets.QApplication.clipboard().setMimeData(mime_data)


def table_values_from_clipboard(return_headers=False):
    """
    Get values from the clipboard into a list of lists. Can read copied values
    from many applications, incl. Excel.

    Each inner list represents one row of values. Rows are padded if needed
    such that all rows contain the same number of values.

    If return_headers is True, a list of headers is also returned alongside the
    values.

    Note that all returned values are strings and so they might need to be
    parsed to other types.
    """
    clipboard = QtWidgets.QApplication.clipboard()
    mime_data = clipboard.mimeData()

    headers = []
    values = []
    if mime_data.hasHtml():
        html = mime_data.html()
        root = lxml.html.fromstring(html)
        table = root.find('.//table')
        if table is not None:
            # Find first tr tag with th children:
            header_line = table.find('.//tr[th]')
            if header_line is not None:
                headers = [cell.text_content().strip()
                           for cell in header_line.findall('th')]

            # Find all tr tags with td children:
            for line in table.iterfind('.//tr[td]'):
                values.append([cell.text_content().strip()
                               for cell in line.findall('td')])
        else:
            values.append([root.text_content()])
    elif mime_data.hasText():
        text = clipboard.text()
        for line in text.splitlines():
            line = line.strip()
            if line:
                values.append(line.split('\t'))

    # Pad all rows to the length of the maximum length of any row.
    if values:
        max_column_counts = max(len(row) for row in values)
        if return_headers:
            max_column_counts = max(max_column_counts, len(headers))
            headers = headers + ['']*(max_column_counts - len(headers))
        values = [row + ['']*(max_column_counts - len(row))
                  for row in values]

    if return_headers:
        return values, headers
    else:
        return values


def format_data(data, decimals=None):
    """
    Construct text data format for use in, for example, a table
    cell, label, etc.
    """
    s = '{}'
    if decimals is not None:
        s = '{: 1.%sf}' % decimals

    try:
        # In case data is numpy type.
        data = data.tolist()
    except AttributeError:
        pass

    if isinstance(data, float) and decimals is not None:
        data = s.format(data)
    elif isinstance(data, complex) and decimals is not None:
        real = data.real
        imag = data.imag
        data = s.format(real)
        if imag >= 0:
            data += "+" + str(s.format(imag))[1:] + "j"
        else:
            data += str(s.format(imag)) + "j"
    # elif isinstance(data, datetime.datetime):
    #     data = data.isoformat()
    elif isinstance(data, bytes):
        # repr will show printable ascii characters as usual but will
        # replace any non-ascii or non-printable characters with an escape
        # sequence. The slice removes the quotes added by repr.
        data = repr(data)[2:-1]
    elif data is None:
        data = '--'
    return str(data)
