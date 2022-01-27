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
import os
import sys
import numpy as np
from Qt import QtWidgets

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'Python')))

import sympathy.api
import sympathy.utils.complete


def test_table():
    test = sympathy.api.table.File()
    test['a0'] = np.arange(3)
    test['a1'] = np.arange(3) + 1
    test.name = 'hello'
    return test


def main():
    app = QtWidgets.QApplication(sys.argv)

    data = test_table()
    model = sympathy.utils.complete.DictTreeModel(
        data.completions().to_dict(data, name='arg'))

    treeview = QtWidgets.QTreeView()
    treeview.setModel(model)

    lineedit = QtWidgets.QLineEdit()
    completer = sympathy.utils.complete.TreeItemCompleter(model)

    lineedit.setCompleter(completer)
    lineedit.show()

    treeview.show()
    app.exec_()


if __name__ == '__main__':
    main()
