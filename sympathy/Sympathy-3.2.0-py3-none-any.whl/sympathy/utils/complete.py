# This file is part of Sympathy for Data.
# Copyright (c) 2019, Combine Control Systems AB
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
import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets
import re
import io
import tokenize

import sympathy.platform.qt_support as platform_qt_support


name_key = '*'
childs_key = '/'


def name_prefix_at_pos(text, pos):
    skip_types = {59: 'ENCODING', 4: 'NEWLINE', 0: 'ENDMARKER'}
    # FYI:
    # more_types = {1: 'NAME', 53: 'OP', 56: 'ERRORTOKEN'}

    tgen = tokenize.tokenize(io.BytesIO(text.encode('utf8')).readline)

    tlist = []
    try:
        for t in tgen:
            if t not in skip_types:
                tlist.append(t)
    except Exception:
        pass

    icurr = None

    for i, t in enumerate(tlist):
        start_col = t.start[1]
        end_col = t.end[1]

        if start_col <= pos and pos <= end_col:
            icurr = i

    start_col = None

    if icurr is not None:
        irlist = iter(reversed(tlist[:icurr + 1]))
        t = next(irlist, None)

        while t:
            if t.type == 1:
                start_col = t.start[1]
                t = next(irlist, None)
                if t:
                    if t.type == 53:
                        if t.string != '.':
                            break
                    elif t.type == 56:
                        # ERRORTOKEN, assuming unterminated string.
                        pass
                    else:
                        break
            else:
                t = next(irlist, None)

    text_under_cursor = ''
    if start_col is not None:
        text_under_cursor = text[start_col:pos]
    return text_under_cursor


class CompletionBuilder:
    def __init__(self):
        self._call_args_fn = None
        self._getitem_args_fn = None
        self._call = None
        self._getitem = None
        self._props = {}
        self._empty = True

    def prop(self, name, builder=None):
        res = builder
        if not res:
            res = CompletionBuilder()
        self._props[name] = res
        self._empty = False
        return res

    def call(self, args_fn=None, builder=None):
        res = builder
        if not res:
            res = CompletionBuilder()
        self._call = res
        self._call_args_fn = args_fn
        self._empty = False
        return res

    def getitem(self, args_fn=None, builder=None):
        res = builder
        if not res:
            res = CompletionBuilder()
        self._getitem = res
        self._getitem_args_fn = args_fn
        self._empty = False
        return res

    def to_dict(self, obj, name=None):
        def list_no_empty(items):
            return [i for i in items if i is not None]

        def single_to_list_no_empty(item):
            if item is None:
                return []
            return [item]

        def flat_single_to_list_no_empty(item):
            if item is None:
                return []
            else:
                return item[childs_key]

        def get(obj, key):
            op, arg = key
            if op == '[]':
                return obj[arg]
            elif op == '()':
                if arg is None:
                    return obj()
                else:
                    return obj(arg)
            elif op == '.':
                return getattr(obj, arg)
            assert False

        def nested(beg, end, child, obj, args_fn):
            prefix = f'{beg}{end}'
            if args_fn is None:
                res = {
                    name_key: beg,
                    childs_key: [{
                        name_key: end,
                        childs_key: flat_single_to_list_no_empty(
                            child.to_dict(get(obj, (prefix, None))))
                    }]
                }
            else:
                args = args_fn(obj)
                if isinstance(child, list):
                    res = {
                        name_key: beg,
                        childs_key: [{
                            name_key: repr(a),
                            childs_key: [{
                                name_key: end,
                                childs_key: flat_single_to_list_no_empty(
                                    c.to_dict(get(obj, ((prefix, a)))))
                            }]
                        }
                                     for c, a in zip(child, args)]
                    }
                else:
                    res = {
                        name_key: beg,
                        childs_key: [{
                            name_key: repr(a),
                            childs_key: [{
                                name_key: end,
                                childs_key: flat_single_to_list_no_empty(
                                    child.to_dict(get(obj, ((prefix, a)))))
                            }]
                        }
                                     for a in args]
                    }
            return res

        if name is None:
            if self._empty:
                return None
            name = 'root'

        res_list = []
        res = {name_key: name,  childs_key: res_list}
        props = {}
        call = {}
        getitem = {}
        if self._props:
            props = {name_key: '.', childs_key: list_no_empty([
                v.to_dict(get(obj, ('.', k)), k)
                for k, v in self._props.items()])}
        if self._call:
            call = nested(
                '(', ')', self._call, obj, self._call_args_fn)
        if self._getitem:
            getitem = nested(
                '[', ']', self._getitem, obj, self._getitem_args_fn)

        if props:
            res_list.append(props)
        if call:
            res_list.append(call)
        if getitem:
            res_list.append(getitem)

        return res


def builder():
    return CompletionBuilder()


def rename_root(obj, name):
    res = {}
    res.update(obj)
    res[name_key] = name
    return res


class TreeItem(object):
    def __init__(self, data, parent=None):
        self._data = data
        self._children = []
        self._data_children_list = None
        self._parent = parent

    def name(self):
        return self._data[name_key]

    def parent(self):
        return self._parent

    def row(self):
        if self._parent:
            return self._parent.index(self)
        else:
            return 0

    def _data_children(self):
        if self._data_children_list is None:
            self._data_children_list = list(self._data[childs_key])
        return self._data_children_list

    def child(self, row):
        try:
            child_ = self._children[row]
        except IndexError:
            children = self._data_children()
            child_ = None
            for i in range(len(self._children), row + 1):
                child_ = TreeItem(children[i], parent=self)
                self._children.append(child_)
        return child_

    def child_count(self):
        return len(self._data_children())

    def index(self, child):
        return self._children.index(child)


class DictTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, dict_model, parent=None):
        super().__init__(parent)
        dict_model = {name_key: 'root', childs_key: [dict_model]}
        self._data_root = dict_model
        self._root = TreeItem(dict_model, parent=None)
        self._index_to_item = {}
        self._item_enumerator = platform_qt_support.object_enumerator()

    def createIndex(self, row, column, item):
        index = super().createIndex(
            row, column, self._item_enumerator(item))
        self._index_to_item[index.internalId()] = item
        return index

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            item = self._index_to_item.get(parent.internalId())
            if item is None:
                return 0

            return item.child_count()
        else:
            return self._root.child_count()

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if parent.isValid():
            parent_item = self._index_to_item.get(parent.internalId())
        else:
            parent_item = self._root

        child_item = None
        if parent_item is not None:
            child_item = parent_item.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        empty_index = QtCore.QModelIndex()

        if not index.isValid():
            return empty_index

        item = self._index_to_item.get(index.internalId())
        if item:
            parent = item.parent()
            if parent and parent.parent():
                return self.createIndex(parent.row(), 0, parent)

        return empty_index

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        item = self._index_to_item.get(index.internalId())

        if item is None:
            pass
        elif role == QtCore.Qt.DisplayRole:
            return item.name()

    def setData(self, index, value, role):
        if not index.isValid():
            return None
        super().setData(index, value, role)

    def itemData(self, index):
        item = self._index_to_item.get(index.internalId())
        return item

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        item = self._index_to_item.get(index.internalId())

        if item is not None:
            return (QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsDragEnabled |
                    QtCore.Qt.ItemIsSelectable)
        else:
            return (QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsSelectable)

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.TextAlignmentRole:
            if orientation == QtCore.Qt.Horizontal:
                return QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
            else:
                return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        elif role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return 'Name'
            else:
                return section + 1
        else:
            return None

    def root_item(self):
        return self._root


class TreeItemCompleter(QtWidgets.QCompleter):

    _seps = '.()[]'
    _split_re = re.compile('([\\.\\[\\(\\)\\]])')

    def __init__(self, model=None, parent=None):
        parent = None
        super().__init__(parent)
        if model:
            self.setModel(model)
        self.setCompletionRole(QtCore.Qt.DisplayRole)

    def splitPath(self, path):
        split = self._split_re.split(path)
        if split and not split[0]:
            split = split[1:]

        split = [p for p in split if p]
        if path and path[-1] in self._seps:
            split.append('')
        return split

    def pathFromIndex(self, index):

        segs = []

        while index.isValid():
            segs.append(index.data(self.completionRole()))
            index = index.parent()
        return ''.join(reversed([s for s in segs if s is not None]))

    def setModel(self, model):
        return super().setModel(model)
