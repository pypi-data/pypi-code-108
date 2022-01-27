# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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
import sys
import math
import functools

from sympathy.api import qt2 as qt_compat
from sympathy.api.exceptions import SyUserCodeError

from . import util
QtGui = qt_compat.import_module('QtGui')  # noqa
QtWidgets = qt_compat.import_module('QtWidgets')  # noqa


class SortWidget(QtWidgets.QWidget):

    def __init__(self, input_list, node_context, parent=None):
        super(SortWidget, self).__init__(parent)
        self._node_context = node_context
        self._input_list = input_list
        self._parameters = node_context.parameters
        self._init_gui()

    def _init_gui(self):
        vlayout = QtWidgets.QVBoxLayout()
        compare_label = QtWidgets.QLabel('Compare function for sorting:')

        self._compare_text = self._parameters['sort_function'].gui()
        reverse_gui = self._node_context.parameters['reverse'].gui()

        self._preview_button = QtWidgets.QPushButton("Preview sorting")
        self._preview_table = QtWidgets.QTableWidget()

        compare_vlayout = QtWidgets.QVBoxLayout()
        compare_vlayout.addWidget(reverse_gui)
        compare_vlayout.addWidget(compare_label)
        compare_vlayout.addWidget(self._compare_text)

        preview_vlayout = QtWidgets.QVBoxLayout()
        preview_vlayout.addWidget(self._preview_button)
        preview_vlayout.addWidget(self._preview_table)

        sorting_hlayout = QtWidgets.QHBoxLayout()
        sorting_hlayout.addLayout(compare_vlayout)
        sorting_hlayout.addLayout(preview_vlayout)

        vlayout.addLayout(sorting_hlayout)

        self.setLayout(vlayout)
        self._preview_button.clicked.connect(self._preview_update)

    def _preview_update(self):
        try:
            self._preview_table.clear()

            sort_ind = sorted_list(
                self._parameters['sort_function'].value,
                self._input_list,
                reverse=self._node_context.parameters['reverse'].value,
                enum=True)

            self._preview_table.setRowCount(2)
            self._preview_table.setColumnCount(len(sort_ind))
            self._preview_table.setVerticalHeaderLabels(
                ['Previous indices', 'Sorted indices'])
            self._preview_table.setHorizontalHeaderLabels(
                [' '] * len(sort_ind))
            for ind, new_ind in enumerate(sort_ind):
                self._preview_table.setItem(0, ind, QtWidgets.QTableWidgetItem(
                    str(ind)))
                self._preview_table.setItem(1, ind, QtWidgets.QTableWidgetItem(
                    str(new_ind)))
            self._preview_table.resizeColumnsToContents()
        except:
            self._preview_table.clear()
            self._preview_table.setRowCount(1)
            self._preview_table.setColumnCount(1)
            self._preview_table.setItem(
                0, 0, QtWidgets.QTableWidgetItem(
                    'Sorting function not valid'))


def sorted_list(sort_function_str, input_list, reverse=False):
    inf = float('inf')

    def isnan(item):
        try:
            return math.isnan(item)
        except TypeError:
            return False

    if len(input_list) == 0:
        return []

    try:
        key_func = util.base_eval(sort_function_str)

        nans_is = [isnan(key_func(item)) for item in input_list]

        nans = (item for i, item in enumerate(input_list) if nans_is[i])
        vals = (item for i, item in enumerate(input_list) if not nans_is[i])

        if reverse:
            for item in nans:
                yield item

        for item in sorted(
                vals,
                key=key_func,
                reverse=reverse):
            yield item

        if not reverse:
            for item in nans:
                yield item

    except Exception:
        raise SyUserCodeError(sys.exc_info(), 'Error executing sort function.')
