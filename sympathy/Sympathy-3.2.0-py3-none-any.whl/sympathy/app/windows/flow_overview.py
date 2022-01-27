# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
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
import functools

import itertools
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui

from .. import flow
from .. import util
from .. import signals
from .. import tree_view
from sympathy.utils.prim import uri_to_path, format_display_string


class IndirectNode(object):
    """
    Workaround wrapper to make Lambda supported by
    QTreeWidgetItem.setData.
    """
    def __init__(self, node):
        self.node = node


class NodeItemMixin(object):

    def __init__(self, obj, parent, style=None, *args, **kwargs):
        self._obj = obj
        self._style = style
        super().__init__(*args, **kwargs)
        self._parent = parent

    def identifier(self):
        return self._obj.full_uuid

    def icon(self):
        if self._obj.has_svg_icon:
            return uri_to_path(self._obj.icon)
        else:
            return util.icon_path('missing.svg')

    def node(self):
        return self._obj


class NodeItem(NodeItemMixin, tree_view.LeafItem):

    def name(self):
        return format_display_string(self._obj.name)

    def tool_tip(self):
        return self._obj.description


class TextItem(NodeItemMixin, tree_view.LeafItem):
    def name(self):
        return format_display_string(self._obj.text())

    def tool_tip(self):
        return self._obj.text()


class FlowItem(NodeItemMixin, tree_view.TreeItem):

    def name(self):
        if self._obj:
            return format_display_string(self._obj.display_name)
        return 'Root'

    def tool_tip(self):
        return self._obj.description

    def children(self):
        return iter(self._children)

    def insert_child(self, i, child):
        self._children.insert(i, child)


class RootItem(FlowItem):

    def __init__(self, style=None):
        super().__init__(None, parent=None, style=style)

    def name(self):
        return 'Root'

    def tool_tip(self):
        return ''

    def icon(self):
        return None

    def node(self):
        return None


class FlowOverviewModel(tree_view.TreeModel):

    def __init__(self, style, parent=None):

        self._signals = signals.SignalHandler()
        self._highlight = None
        self._node_to_item = {}
        self._style = style
        self._root_flow = None
        self._flow = None
        self._icon_cache = {}
        self._running = True
        self._delay = []
        self._delay_flow = None
        super().__init__(RootItem(style=self._style), parent=parent)

    def stop_updates(self, flow_):
        was_running = self._running
        self._running = False
        self._delay_flow = flow_
        self._delay.clear()
        self.beginResetModel()

    def start_updates(self, flow_):
        was_running = self._running
        self._running = True
        if not was_running and flow_:

            for action, parent_flow, node in self._delay:
                if parent_flow == flow_:
                    if action == 'create':
                        self._node_created(node)
                    elif action == 'remove':
                        self._node_removed(
                            node, parent_flow=parent_flow)

        self._delay.clear()

        # self._node_to_item.clear()
        # self._index_to_item.clear()

        self.endResetModel()

    @property
    def flow(self):
        return self._root_flow

    @flow.setter
    def flow(self, value):
        root_flow = value
        old_flow = self._flow
        old_root_flow = self._root_flow

        self._flow = value

        if value:
            while root_flow.flow is not None:
                root_flow = root_flow.flow

            self._set_new_root_flow(root_flow, True)

        else:
            self._set_new_root_flow(None, False)

        # Update highlighted (bold) flow.
        if root_flow is old_root_flow and old_flow:
            for f in [old_flow, value]:
                item = self._node_to_item.get(f)
                index = self._item_index(item)
                self.dataChanged.emit(index, index, [tree_view.PositionRole])

    def default_expand_indices(self):
        f = self._flow
        res = []

        while f:
            item = self._node_to_item.get(f)
            if item:
                res.append(self._item_index(item))
            f = f.flow
        return res

    def _set_new_root_flow(self, root_flow, populate):
        if root_flow is self._root_flow:
            return

        self.beginResetModel()

        self._highlight = None
        self._node_to_item = {}
        self._remove_all_node_signals()
        self._root = RootItem(self._style)

        self._node_to_item.clear()
        self._index_to_item.clear()

        self.endResetModel()
        self.beginResetModel()

        self._root_flow = root_flow
        if root_flow is not None:
            if populate:
                self._populate_model(root_flow, self._root,
                                     QtCore.QModelIndex())
        self.endResetModel()

    def _build_model(self):
        self._remove_all_node_signals()
        self._set_new_root_flow(self._root_flow, True)

    # https://wiki.qt.io/Technical_FAQ#How_can_a_QModelIndex_be_retrived_from_the_model_for_an_internal_data_item.3F
    def _item_index(self, parent):
        path = []

        while parent:
            path.append(parent)
            parent = parent.parent()

        index = QtCore.QModelIndex()
        parent = self._root

        for item in list(reversed(path))[1:]:
            index = self.index(parent.index(item), 0, index)
            parent = item

        return index

    def _populate_model(self, node, parent_item, parent_index=None):
        def create_item(node_, parent_item_):
            if node_.type == flow.Type.Flow:
                cls = FlowItem
            elif node_.type == flow.Type.TextField:
                cls = TextItem
            else:
                cls = NodeItem

            item = cls(node_, parent_item_, self._style)
            return item

        if node in self._node_to_item:
            # Never overwrite a node in self._node_to_item. That could lead to
            # all sorts of broken states.
            self._node_removed(node)

        if node is not None:

            item = create_item(node, parent_item)

            if parent_index is None:
                parent_index = self._item_index(parent_item)

            pos = parent_item.child_count()

            if self._running:
                self.beginInsertRows(parent_index, pos, pos)

            parent_item.insert_child(pos, item)
            self._node_to_item[node] = item
            item_index = self.index(pos, 0, parent_index)

            if self._running:
                self.endInsertRows()

            self._add_node_signals(node)
            if node.type == flow.Type.Flow:
                for node_ in sorted(
                        itertools.chain(node.shallow_nodes(),
                                        node.shallow_text_fields()),
                        key=self._node_position):
                    self._populate_model(node_, item, parent_index=item_index)

    def _handle_name_changed(self, node, new_name):
        item = self._node_to_item[node]
        index = self._item_index(item)
        self.dataChanged.emit(
            index, index,
            [QtCore.Qt.DisplayRole, tree_view.HighlightRole])

    def _node_position(self, node):
        return node.position.x(), node.position.y()

    def _handle_node_moved(self, node, new_position):
        new_position = new_position.x(), new_position.y()
        parent_item = self._node_to_item[node.flow]
        item = self._node_to_item[node]
        parent_index = self._item_index(parent_item)
        org_pos = parent_item.index(item)

        # Loop through items siblings to find a new place for it.

        children = list(parent_item.children())
        children.remove(item)

        new_pos = list(sorted(itertools.chain(
            (self._node_position(i.node()) for i in children),
            [new_position]))).index(new_position)

        # See index handling for beginMoveRows.
        # http://doc.qt.io/qt-5/qabstractitemmodel.html#beginMoveRows
        move_pos = new_pos + 1 if new_pos > org_pos else new_pos

        move_ok = self.beginMoveRows(
            parent_index, org_pos, org_pos, parent_index, move_pos)

        if not move_ok:
            return

        parent_item.remove_child(item)
        parent_item.insert_child(new_pos, item)
        self.endMoveRows()

    def _handle_node_created(self, node):
        if not self._running:
            if self._delay_flow and self._delay_flow is node.flow:
                self._delay.append(('create', self._delay_flow, node))
        else:
            self._node_created(node)

    def _node_created(self, node):
        parent_flow = node.flow
        parent_item = self._node_to_item[parent_flow]
        # self._populate_model(node, parent_item, insert=True)
        self._populate_model(node, parent_item)
        # Make sure the node was put at the correct position in the tree.
        self._handle_node_moved(node, node.position)

    def _handle_node_removed(self, node):
        # When deleting a subflow it doesn't seem to emit node_removed for all
        # of its children. This loop takes care of that, but could in some
        # cases lead to nodes being deleted twice.
        if not self._running:
            if self._delay_flow and self._delay_flow is node.flow:
                self._delay.append(('remove', self._delay_flow, node))
        else:
            self._node_removed(node, parent_flow=None)

    def _node_removed(self, node, parent_flow=None):

        if node.type == flow.Type.Flow:
            for node_ in itertools.chain(node.shallow_nodes(),
                                         node.shallow_text_fields()):
                self._node_removed(node_)

        # Guard against nodes being deleted twice.
        try:
            item = self._node_to_item[node]
        except KeyError:
            return

        if parent_flow is None:
            parent_flow = node.flow
        parent_item = self._node_to_item[parent_flow]
        parent_index = self._item_index(parent_item)
        pos = parent_item.index(item)
        self.beginRemoveRows(parent_index, pos, pos)
        parent_item.remove_child(item)
        del self._node_to_item[node]
        self._remove_node_signals(node)
        self.endRemoveRows()

    def _handle_icon_changed(self, node):
        item = self._node_to_item[node]
        index = self._item_index(item)
        self.dataChanged.emit(
            index, index,
            [QtCore.Qt.DecorationRole])

    def _add_node_signals(self, node):
        self._signals.connect_reference(node, [
            (node.position_changed,
             functools.partial(self._handle_node_moved, node)),
            (node.name_changed,
             functools.partial(self._handle_name_changed, node))])

        if node.type == flow.Type.Flow:
            self._signals.connect_reference(node, [
                (node.icon_changed,
                 functools.partial(self._handle_icon_changed, node)),
                (node.text_field_created, self._handle_node_created),
                (node.text_field_removed, self._handle_node_removed),
                (node.node_created, self._handle_node_created),
                (node.node_removed, self._handle_node_removed),
                (node.subflow_created, self._handle_node_created),
                (node.subflow_removed, self._handle_node_removed)])

    def _remove_node_signals(self, node):
        # Disconnect all signals
        self._signals.disconnect_all(node)

    def _remove_all_node_signals(self):
        # Disconnect all signals for all nodes
        self._signals.disconnect_all()

    def _get_node_icon(self, item):
        icon_path = item.icon()

        icon = self._icon_cache.get(icon_path)
        if not icon:
            icon = QtGui.QIcon(icon_path)
            self._icon_cache[icon_path] = icon
        return icon

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if not index.isValid():
            return None
        if role == QtCore.Qt.DecorationRole:
            item = self._index_to_item.get(index.internalId())
            return self._get_node_icon(item)
        elif role == tree_view.PositionRole:
            item = self._index_to_item.get(index.internalId())
            return self._node_position(item.node())
        elif role == tree_view.BoldRole:
            item = self._index_to_item.get(index.internalId())
            return item.node() is self._flow
        else:
            res = super().data(index, role=role)
            return res

    def flags(self, index):
        if not index.isValid():
            return 0
        return (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)


class FlowOverviewFilterProxyModel(tree_view.TreeFilterProxyModelBase):
    pass


class FlowOverviewWidget(tree_view.TreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('Gui::MainWindow::FlowOverview::View')


class FlowOverview(tree_view.FilterTreeView):
    select_flow = QtCore.Signal(flow.Flow)
    select_node = QtCore.Signal(flow.Node)

    def __init__(self, style, parent=None):
        tree_model = FlowOverviewFilterProxyModel()
        tree_model.setSortRole(tree_view.PositionRole)
        self._expansions = None
        self._tree_model = tree_model
        tree_widget = FlowOverviewWidget()
        super().__init__(tree_model, tree_widget, parent)
        self.setObjectName('Gui::MainWindow::Library::ViewWidget')
        model = FlowOverviewModel(style)
        self.set_model(model)
        self._enabled = self.isVisible()
        tree_widget.selection_changed.connect(self._selection_changed)
        self._flow = None

    def set_flow(self, flow_window_=None):
        flow_ = None
        if flow_window_ is not None:
            flow_ = flow_window_.flow()

        self._flow = flow_
        if self._enabled:
            self._model.flow = flow_
            self._default_expand()

    def set_enabled(self, enabled):
        was_enabled = self._enabled
        self._enabled = enabled

        if was_enabled and not enabled:
            self._model.flow = None
        elif not was_enabled and enabled:
            self._model.flow = self._flow
            self._default_expand()

    def _selection_changed(self, node):
        if node is self._model.flow:
            self.select_flow.emit(node)
        else:
            self.select_node.emit(node)

    def _default_expand(self):
        self._view.collapseAll()
        if self._model:
            if self._expansions is not None:
                for index in self._expansions:
                    self._view.expand(self._proxy_model.mapFromSource(index))
            else:
                for index in self._model.default_expand_indices():
                    self._view.expand(self._proxy_model.mapFromSource(index))

    def start_updates(self, flow_):
        self._expansions = []

        def expansions(index):
            if self._view.isExpanded(index):
                self._expansions.append(self._proxy_model.mapToSource(index))

            for i in range(self._model.rowCount(
                    self._proxy_model.mapToSource(index))):

                next_index = self._tree_model.index(i, 0, index)
                if next_index.isValid():
                    expansions(next_index)

        expansions(QtCore.QModelIndex())

        self._model.start_updates(flow_)

    def stop_updates(self, flow_):
        self._model.stop_updates(flow_)
        self._expansions = None
