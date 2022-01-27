# This file is part of Sympathy for Data.
# Copyright (c) 2018, Combine Control Systems AB
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

import json
import re
from collections import OrderedDict

import numpy as np

from sympathy.api import ParameterView
from sympathy.api import qt2
from sympathy.api import table

QtWidgets = qt2.import_module('QtWidgets')


TABLE_KIND = {
    "Single row": 0,
    "Multiple rows": 1,
    "": 0,
    "SINGLE": "Single row",
    "MULTIPLE": "Multiple rows"
}


def add_jsontable_parameters(parameters):

    try:
        parameters['table_kind']
    except KeyError:
        parameters.set_string('table_kind', value=TABLE_KIND['SINGLE'],
                              description='What kind of table to create')

    try:
        parameters['minimize_col_names']
    except KeyError:
        parameters.set_boolean(
            'minimize_col_names', value=True, label='Minimize colum names',
            description='Create column names that are minimal')

    try:
        parameters['nomask']
    except KeyError:
        parameters.set_boolean(
            'nomask', value=False,
            label='Use zero-like values instead of masks',
            description=(
                'When unchecked data cells that are missing '
                'will be masked. When checked such cells are instead '
                'assigned 0, 0.0, False, "", etc. depending on the type '
                'of the value column.'))


class JsonTableWidget(ParameterView):
    """ A widget for converting a JSON object to a table """
    def __init__(self, parameters, parent=None):
        super(JsonTableWidget, self).__init__(parent=parent)
        self._parameters = parameters
        self._init_gui()

    def save_parameters(self):
        self._parameters['table_kind'].value = (
            self._tablekind_combobox.currentText())

    def _init_gui(self):
        vlayout = QtWidgets.QVBoxLayout()
        hlayout = QtWidgets.QHBoxLayout()

        tablekind_label = QtWidgets.QLabel("Table kind")
        self._tablekind_combobox = QtWidgets.QComboBox()
        self._tablekind_combobox.setToolTip('What kind of table to create')
        hlayout.addWidget(tablekind_label)
        hlayout.addWidget(self._tablekind_combobox)

        self._stacked_widget = QtWidgets.QStackedWidget()

        # Adding Single row GUI
        self._tablekind_combobox.addItem(TABLE_KIND["SINGLE"])
        self._stacked_widget.addWidget(
            self._parameters['minimize_col_names'].gui())

        # Adding Multiple rows GUI
        self._tablekind_combobox.addItem(TABLE_KIND["MULTIPLE"])
        self._stacked_widget.addWidget(self._parameters['nomask'].gui())

        vlayout.addItem(hlayout)
        vlayout.addWidget(self._stacked_widget)

        self._tablekind_combobox.currentIndexChanged[int].connect(
            self._tablekind_changed)
        self._tablekind_combobox.activated.connect(
            self._stacked_widget.setCurrentIndex)
        self.setLayout(vlayout)

        self._tablekind_combobox.setCurrentIndex(
            TABLE_KIND[self._parameters["table_kind"].value])

    def _tablekind_changed(self, index):
        self._parameters["table_kind"].value = (
            self._tablekind_combobox.currentText())
        self._stacked_widget.setCurrentIndex(index)


# -------------------------------------------------------
# Helper classes for creating a table from a JSON object
# -------------------------------------------------------


DEFAULT_SEPARATOR = "."


class JsonLeaf(object):
    """
    A leaf in a JSON structure, i.e. an item where the value is
    not a list or a dictionary
    """
    def __init__(self, keys, value, separator=DEFAULT_SEPARATOR):
        self.keys = keys
        self.value = value
        self.separator = separator

    def __str__(self):
        return "({}={})".format(self.key(), self.value)

    def is_atomic(self):
        return len(self.keys) == 1

    def has_listkey(self):
        return re.match("\[\d+\]", self.keys[0]) is not None

    def key(self):
        alt_keys = [self.keys[0]]
        for i, (ikey, prevkey) in enumerate(
                zip(self.keys[1:], self.keys[:-1])):
            if re.match("\[\d+\]", ikey) is not None:
                alt_keys[-1] += ikey
            else:
                alt_keys.append(ikey)
        return self.separator.join(alt_keys)


class JsonRow(object):
    """
    A list of JsonLeaf objects
    """
    def __init__(self):
        self._items = []

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._items[item]
        else:
            for myitem in self._items:
                if myitem.key() == item:
                    return myitem

    def __str__(self):
        return "\t".join([str(item) for item in self._items])

    def headers(self):
        return [item.key() for item in self._items]

    def values(self):
        return [item.value for item in self._items]

    def append(self, item):
        """ Append an item to the list """
        if not isinstance(item, JsonLeaf):
            raise ValueError("Can only add JsonLeaf objects to a JsonRow")
        self._items.append(item)

    def extend(self, row, prepend=False):
        """ Extend the list with the items from another list """
        if prepend:
            row._items.reverse()
            for item in row._items:
                self._items.insert(0, item)
        else:
            self._items.extend(row._items)

    def minimize_keys(self):
        """
        Remove unnecessary path information from the keys of the items,
        while stile keeping them unique
        """
        max_depth = max([len(item.keys) for item in self._items], default=0)
        testable = [True] * len(self._items)
        minimal_keys = [None] * len(self._items)

        for depth in range(1, max_depth):
            # Build a trial set of keys
            trial_keys = [None]*len(self._items)
            for i, item in enumerate(self._items):
                if not testable[i]:
                    continue
                if depth >= len(item.keys):
                    trial_keys[i] = item.keys[-1]
                else:
                    trial_keys[i] = item.separator.join(item.keys[depth:])
            # Now check if we created any clashes
            for i, (item, trial_key) in enumerate(zip(self._items, trial_keys)):
                if not testable[i]:
                    continue
                count = sum([trial_key == key_b for key_b in trial_keys if key_b])
                if count > 1:
                    testable[i] = False
                    minimal_keys[i] = item.separator.join(item.keys[depth-1:])
                else:
                    minimal_keys[i] = trial_key

        if all(mk is None for mk in minimal_keys):  # Nothing was changed, all keys were unique from the beginning
            return

        new_items = []
        for item, min_key in zip(self._items, minimal_keys):
            new_items.append(JsonLeaf(min_key.split(item.separator),
                                     item.value, separator=item.separator))
        self._items = new_items

    def remove_leading(self):
        """ Remove the first key for all items in the list """
        for item in self._items:
            val = item.keys.pop(0)
            if item.is_atomic() and item.has_listkey():
                item.keys[0] = val+item.keys[0]


class JsonTable(object):
    """
    A list of JsonRow objects that together make up a table
    representation of an JSON structure
    """
    def __init__(self, json_obj, separator=DEFAULT_SEPARATOR):
        self._dict = json_obj.get()
        self._separator = separator
        self._rows = []
        self._flatten()

    def __str__(self):
        return json.dumps(self._dict)

    def is_group(self):
        return isinstance(self._dict, (list, dict))

    def _column(self, header, nomask):
        """Return a column in the table"""

        def mask_array(arr, mask):
            if nomask:
                return arr
            else:
                return np.ma.masked_array(arr, mask)

        column = []

        for i, row in enumerate(self._rows):
            item = row[header]
            if item is None or item.value is None:
                column.append(None)
            else:
                column.append(item.value)

        mask = np.array([v is None for v in column])

        if np.any(mask):
            values = [v for v in column if v is not None]
            if values:
                dtype = np.array(values).dtype
                zero_val = np.zeros(1, dtype=dtype)[0]
                values = np.array(
                    [zero_val if v is None else v for v in column])
            else:
                values = np.zeros(len(column), dtype=str)

            values = mask_array(values, mask)
        elif column:
            values = np.array(column)
        else:
            values = np.array([], dtype=str)

        return values

    def _expand_rows(self):
        """ Expand a single row to multiple rows """
        def _walk(rows):
            created_rows = []
            expanded = False
            for row in rows:
                not_expanding = JsonRow()
                expanding = OrderedDict()
                expanding_list = None
                for item in row:
                    if item.is_atomic():
                        not_expanding.append(item)
                    else:
                        if expanding_list is None:
                            expanding_list = item.has_listkey()
                        if expanding_list != item.has_listkey():
                            not_expanding.append(item)
                            continue
                        if item.keys[0] not in expanding:
                            expanding[item.keys[0]] = JsonRow()
                        expanding[item.keys[0]].append(item)
                if len(expanding) > 0:
                    for key, value in expanding.items():
                        value.remove_leading()
                        value.extend(not_expanding, prepend=True)
                        created_rows.append(value)
                    expanded = True
                else:
                    created_rows.append(not_expanding)

            if not expanded:
                return created_rows
            else:
                return _walk(created_rows)

        self._flatten()
        self._rows = _walk(self._rows)

    def _flatten(self):
        """ Flatten the JSON structure into a single row """
        self._rows = [JsonRow()]

        def walk(node, parents):
            if isinstance(node, list):
                for i, value in enumerate(node):
                    walk(value, parents+["[{}]".format(i)])
            elif isinstance(node, dict):
                for key, value in node.items():
                    walk(value, parents+[key])
            else:
                leaf = JsonLeaf(parents, node, self._separator)
                self._rows[0].append(leaf)

        walk(self._dict, [])

    def _make_columns(self, nomask):
        """ Make columns from a unique set of headers """
        headers = list(self._rows[0].headers())
        for row in self._rows[1:]:
            headers.extend([header for header in row.headers()
                            if header not in headers])
        for header in headers:
            data = self._column(header, nomask)
            yield header, data

    def create_multiple_rows_table(self, nomask):
        """
        Create a Table file object with several rows by expanding
        the JSON structure into multiple rows

        :param nomask: If to mask missing values or assign them zero-like
                       values
        :return: A Table file object
        """
        self._expand_rows()
        tbl = table.File()
        for name, data in self._make_columns(nomask):
            tbl.set_column_from_array(name, data)
        return tbl

    def create_single_row_table(self, minimize_column_names=True):
        """
        Create a Table file object with a single row by
        flattening the JSON structure

        :param minimize_column_names: if to minimize the column names
        :return: a Table file object
        """
        self._flatten()
        if minimize_column_names:
            self._rows[0].minimize_keys()
        return table.File.from_rows(column_names=self._rows[0].headers(),
                                    rows=[self._rows[0].values()])
