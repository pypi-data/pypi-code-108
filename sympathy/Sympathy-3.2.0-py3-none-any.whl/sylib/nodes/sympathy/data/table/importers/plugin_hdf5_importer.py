# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
import fnmatch
import warnings

import numpy as np
# Ignore a warning from numpy>=1.14 when importing h5py<=2.7.1:
with warnings.catch_warnings():
    warnings.simplefilter('ignore', FutureWarning)
    import h5py

from sympathy.api import importers
from sympathy.api import node as synode
from sympathy.api import qt2 as qt_compat
from sympathy.api.exceptions import SyDataError
QtCore = qt_compat.import_module('QtCore')
QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')

ENCODING = '__sy_encoding__'

preview_rows = 20


class DataImportHdf5Widget(QtWidgets.QWidget):
    def __init__(self, parameters, filename):
        super(DataImportHdf5Widget, self).__init__()
        self._parameters = parameters
        self._filename = filename
        self._path_items = {}
        self._init_gui()
        self._connect_gui()

    def _init_parameters(self):
        pass

    def _init_gui(self):
        vlayout = QtWidgets.QVBoxLayout()
        button_hlayout = QtWidgets.QHBoxLayout()

        self.select_splitter = QtWidgets.QSplitter(self)
        self.select_treeview = QtWidgets.QTreeView(self.select_splitter)
        self.select_table = QtWidgets.QTableWidget(self.select_splitter)

        self.path_lineedit = QtWidgets.QLineEdit()
        self.path_add_button = QtWidgets.QPushButton('Add')
        self.path_remove_button = QtWidgets.QPushButton('Remove')
        self.path_preview_button = QtWidgets.QPushButton('Preview')

        self.path_list = QtWidgets.QListWidget()
        self.path_table = QtWidgets.QTableWidget()

        self.model = QtGui.QStandardItemModel()
        self.select_treeview.setModel(self.model)
        self.selection_model = self.select_treeview.selectionModel()
        self.select_treeview.setHeaderHidden(True)
        self.path_list.setAlternatingRowColors(True)
        self.path_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)

        style = self.select_treeview.style()
        self.folder_icon = QtGui.QIcon()
        self.file_icon = QtGui.QIcon()
        self.file_link_icon = QtGui.QIcon()

        self.folder_icon.addPixmap(
            style.standardPixmap(QtWidgets.QStyle.SP_DirClosedIcon),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.folder_icon.addPixmap(
            style.standardPixmap(QtWidgets.QStyle.SP_DirOpenIcon),
            QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.file_icon.addPixmap(
            style.standardPixmap(QtWidgets.QStyle.SP_FileIcon))
        self.file_icon.addPixmap(
            style.standardPixmap(QtWidgets.QStyle.SP_FileLinkIcon))

        for path in self._parameters['path_list'].list:
            item = QtWidgets.QListWidgetItem(path)
            self._path_items[path] = item
            self.path_list.addItem(item)

        button_hlayout.addWidget(self.path_add_button)
        button_hlayout.addWidget(self.path_remove_button)
        button_hlayout.addWidget(self.path_preview_button)

        vlayout.addWidget(self.select_splitter)
        vlayout.addWidget(self.path_lineedit)
        vlayout.addWidget(self.path_list)
        vlayout.addLayout(button_hlayout)
        vlayout.addWidget(self.path_table)

        try:
            if self._filename is not None:
                with h5py.File(self._filename, 'r') as hf:
                    self._add_items(self.model, hf)
        except Exception:
            pass

        self.setLayout(vlayout)

    def _connect_gui(self):
        self.path_add_button.clicked.connect(self.add)
        self.path_remove_button.clicked.connect(self.remove)
        self.path_preview_button.clicked.connect(self.preview)
        self.selection_model.selectionChanged.connect(self.select_preview)

    def _add_items(self, parent, data, link=False):
        # Handle group tree or leaf node.
        if link:
            # Do not follow links.
            return

        for key in data.keys():
            # Handle node.
            source = data.get(key, getlink=True)
            item_link = isinstance(source, h5py.ExternalLink)
            prefix = data.name
            name = '/' + key if prefix == '/' else '/'.join([prefix, key])
            value = data[key]

            if isinstance(value, h5py.Group):
                # Add group node, process its children unless it is linked.
                if item_link:
                    item = QtGui.QStandardItem(self.folder_icon, key)
                else:
                    item = QtGui.QStandardItem(self.folder_icon, key)
                    self._add_items(item, value)
                item.setData(name + '/*', QtCore.Qt.UserRole)
            else:
                # Add dataset node.
                if item_link:
                    item = QtGui.QStandardItem(self.file_icon, key)
                else:
                    item = QtGui.QStandardItem(self.file_icon, key)
                item.setEditable(False)
                item.setData(name, QtCore.Qt.UserRole)

            parent.appendRow(item)

    def add(self):
        path = str(self.path_lineedit.text())
        if path and path not in self._path_items:
            item = QtWidgets.QListWidgetItem(path)
            self._path_items[path] = item
            list_ = self._parameters['path_list'].list
            list_.append(path)
            self._parameters['path_list'].list = list_
            self.path_list.addItem(item)

    def remove(self):
        for item in self.path_list.selectedItems():
            index = self.path_list.row(item)
            path = self._parameters['path_list'].list[index]
            del self._path_items[path]
            list_ = self._parameters['path_list'].list
            del list_[index]
            self._parameters['path_list'].list = list_
            self.path_list.takeItem(index)

    def preview(self):
        try:
            if self._filename:
                with h5py.File(self._filename, 'r') as hf:
                    fill_table(self.path_table,
                               hf,
                               self._parameters['path_list'].list)
        except Exception:
            pass

    def select_preview(self, index1, index2):
        item = self.model.itemFromIndex(index1.indexes()[0])
        path = str(item.data(QtCore.Qt.UserRole))

        self.path_lineedit.clear()
        self.path_lineedit.setText(path)

        try:
            with h5py.File(self._filename, 'r') as hf:
                fill_table(self.select_table, hf, [path])
        except Exception:
            pass


def fill_table(table, hdf5, paths):
    """Populate table with all datasets referenced by path as columns."""
    unique_names, same_length, lengths, names = check_data(hdf5, paths)
    cols = dict(zip(names, range(len(names))))

    def fail(table, text):
        table.clear()
        table.setColumnCount(1)
        table.setRowCount(1)
        table.setHorizontalHeaderLabels(
            [name.split('/')[-1] for name in names])
        table.setItem(0, 0, QtWidgets.QTableWidgetItem(text))
        table.item(0, 0).setBackground(
            QtGui.QColor.fromRgb(228, 186, 189))

    def inner(dataset):
        size = dataset.size
        data = []
        onedim = len(dataset.shape) == 1

        if onedim and size:
            data = dataset[:preview_rows]

        size = len(data)
        col = cols[dataset.name]
        row = -1

        for row in range(len(data)):
            table.setItem(
                row,
                col,
                QtWidgets.QTableWidgetItem(str(data[row])))

        table.setItem(
            row + 1,
            col,
            QtWidgets.QTableWidgetItem('({} rows)'.format(size)))
        table.item(row + 1, col).setBackground(
            QtGui.QColor.fromRgb(253, 246, 227))

    if unique_names and same_length:
        try:
            table.clear()
            if lengths and len(lengths[0]) == 1:
                table.setColumnCount(len(names))
                table.setRowCount(lengths[0][0] + 1)
                table.setHorizontalHeaderLabels(
                    [name.split('/')[-1] for name in names])

                for path in paths:
                    traverse(hdf5, path, inner)
        except Exception:
            raise
            # fail(table, 'Exception when building table')
    else:
        if not same_length:
            fail(table, 'Not the same lengths')
        elif not unique_names:
            fail(table, 'Not unique names')
        if len(lengths) and len(lengths[0]) != 1:
            fail(table, 'Not 1D array')

    table.setVerticalHeaderLabels([str(i)
                                   for i in range(table.rowCount())])


class DataImportHdf5(importers.TableDataImporterBase):
    """Importer for Hdf5 files."""

    IMPORTER_NAME = "HDF5"

    def __init__(self, fq_infilename, parameters):
        super(DataImportHdf5, self).__init__(fq_infilename, parameters)
        if parameters is not None:
            self._init_parameters()

    def name(self):
        return self.IMPORTER_NAME

    def _init_parameters(self):
        try:
            path_list = self._parameters['path_list']
        except KeyError:
            self._parameters.set_list(
                'path_list', label='Selected paths',
                description='The paths selected to import data from.',
                value=[],
                _old_list_storage=True,
                editor=synode.Util.combo_editor())
        else:
            path_list._old_list_storage = True

    def valid_for_file(self):
        """
        Is filename a valid Table.
        We cannot know for sure whether to prefer this importer or the table
        importer. So for now this importer will only be manually selectable.

        Additionally there is not much that this importer can do without a
        valid path. There are really few sensible choices beyond doing
        something like path = '*' and even that would work poorly in general.
        """
        return False

    def parameter_view(self, parameters):
        return DataImportHdf5Widget(parameters, self._fq_infilename)

    def import_data(self,
                    out_datafile,
                    parameters=None,
                    progress=None):

        paths = parameters['path_list'].list
        try:
            with h5py.File(self._fq_infilename, 'r') as hdf5:
                names_ok, lengths_ok, lengths, names = check_data(hdf5, paths)
                if names_ok and lengths_ok:
                    import_data(out_datafile, hdf5, paths)
        except Exception as e:
            raise self.import_failed(e)


def traverse(hdf5, path, function):
    """
    Traverse hdf5 group hierarchy according to path given.
    Glob patterns are allowed.
    Applies function to datasets that are referenced by the pattern.
    To be useful function needs to keep state internally or perform IO such as
    printing..
    """
    def recursive(group, parts):
        remaining = len(parts)
        if remaining == 0:
            pass
        else:
            for key in fnmatch.filter(group.keys(), parts[0]):
                value = group[key]
                if remaining == 1:
                    if isinstance(value, h5py.Dataset):
                        function(value)
                else:
                    if isinstance(value, h5py.Group):
                        recursive(value, parts[1:])

    recursive(hdf5, path.split('/')[1:])


def check_data(hdf5, paths):
    """
    Checks that datasets referenced by paths have the same length and that
    their names are unique.
    Return (unique_names, same_length, lengths, names)
    unique_names is True if all names are unique otherwise False.
    same_length is True if all lengths are the same length otherwise False.
    lengths is a list of the lengths.
    names is a list of the names.
    """
    lengths = []
    names = []

    def inner(dataset):
        lengths.append(dataset.shape)
        names.append(dataset.name)

    for path in paths:
        traverse(hdf5, path, inner)

    short_names = [name.split('/')[-1] for name in names]
    unique_names = len(short_names) == len(set(short_names))
    same_length = all(lengths)
    return (unique_names, same_length, lengths, names)


def import_data(table, hdf5, paths):
    """Import all datasets referenced by path as columns into table."""
    def inner(dataset):
        array = dataset[...]
        name = dataset.name.split('/')[-1]
        if ENCODING in dataset.attrs:
            encoding = dataset.attrs[ENCODING]
            data = array.tolist()
            if isinstance(data, list):
                table.set_column_from_array(
                    name, np.array([x.decode(encoding) for x in data]))
            else:
                table.set_column_from_array(name,
                                            np.array(data.decode(encoding)))
        else:
            table.set_column_from_array(name, array)

    for path in paths:
        traverse(hdf5, path, inner)


def print_data(hdf5, paths):
    """Print the path of all datasets referenced by path."""
    def inner(dataset):
        print(dataset.name)

    for path in paths:
        traverse(hdf5, path, inner)
