# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
"""
Hierarchical view of the node library.

- LibraryItemInterface: Items in the view (folders or nodes).
- LibraryItem: Folder
- LibraryNodeItem: Node
- LibraryModel: Qt Library Model
- LibraryWidget: Widget containing the library
- LibraryFilterProxyModel: Proxy model that supports filtering and sorting
- LibraryView: Widget with a filter and the library
"""
import json
import itertools

import os
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

from .. import util
from .. import appcore
from .. import settings
from .. import tree_view
from sympathy.utils.prim import uri_to_path
from sympathy.app import flow
from sympathy.app.datatypes import DataType


class LibraryGroupItem(tree_view.TreeItem):
    """A LibraryItem is a folder item in the library model."""

    def __init__(self, name, parent, style, tool_tip=''):
        super().__init__()
        self._name = name
        self._parent = parent
        self._style = style
        self._icon = QtGui.QIcon()
        self._icon.addPixmap(
            style.standardPixmap(QtWidgets.QStyle.SP_DirClosedIcon),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._icon.addPixmap(
            style.standardPixmap(QtWidgets.QStyle.SP_DirOpenIcon),
            QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._tool_tip = tool_tip or name

    def icon(self):
        return self._icon

    def identifier(self):
        return self._name

    def tool_tip(self):
        return self._tool_tip


class FlatLibraryGroupItem(LibraryGroupItem):
    """A FlatLibraryGroupItem is a header item for a sequence of tags."""

    def __init__(self, name, parent, style):
        super().__init__(name, parent, style)
        self._icon = QtGui.QIcon()
        self._brush = QtCore.Qt.lightGray

    def highlighted(self):
        """Highlighted text"""
        return '<font color="#999999">{}</font>'.format(self._highlighted_text)


class LibraryNodeItem(tree_view.LeafItem):
    """A LibraryNodeItem is a leaf item in the library model representing a
    Node.
    """

    icon_cache = {}

    def __init__(self, node, parent):
        super().__init__()

        def escape(s):
            return (s.replace('&', '&amp;')
                     .replace('<', '&lt;')
                     .replace('>', '&gt;'))

        self._parent = parent
        self._node = node
        self._name = node.name
        self._tool_tip = '<b>{}</b><p>{}</p>{} -> {}'.format(
            self._node.name, self._node.description,
            ', '.join([escape(str(p.datatype)) for p in self._node.inputs]),
            ', '.join([escape(str(p.datatype)) for p in self._node.outputs]))

    def is_leaf(self):
        return True

    def icon(self):
        if self._node.has_svg_icon:
            icon_path = uri_to_path(self._node.icon)
            if icon_path in self.icon_cache:
                return self.icon_cache[icon_path]
            else:
                result = QtGui.QIcon(icon_path)
                self.icon_cache[icon_path] = result
                return result
        else:
            return QtGui.QIcon(util.icon_path('sub_application.svg'))

    def identifier(self):
        return self._node.node_identifier

    def tool_tip(self):
        return self._tool_tip

    def node(self):
        return self._node


class LibraryModel(tree_view.TreeModel):
    """
    The library model. Responsible for building and updating the (viewed)
    library.
    """

    def __init__(self, library_root, style, exclude_builtins=False,
                 parent=None):
        self._library_root = library_root
        self._old_root = None
        self._style = style
        self._exclude_builtins = exclude_builtins

        super().__init__(LibraryGroupItem('Root', None, self._style),
                         parent=parent)

    def _build_model(self):
        """Build the tree model using path for hierarchy."""
        def hidden_node(node):
            if not settings.instance()['Gui/library_show_hidden']:
                tags = node.tags if node.tags else self.tags
                for tag in tags:
                    if tag.startswith('Hidden.'):
                        return True
            return False

        libraries = self._library_root.libraries

        # Attempt to avoid crash in gc.
        self._old_root = self._root
        self._root = LibraryGroupItem('Root', None, self._style)
        self._index_to_item = {}
        try:
            self._old_root.deleteLater()
        except AttributeError:
            pass

        for library in self._library_root.libraries:
            name = library.name
            child = LibraryGroupItem(name, self._root, self._style)
            libs = {}

            paths = set()

            all_nodes = set()
            all_nodes.update({n for n in library.nodes})
            paths.update({tuple(n.path) for n in library.nodes})

            # Add possibly missing levels
            subpaths = set()
            for path in paths:
                subpaths.update({path[:i + 1] for i, _ in enumerate(path)})

            paths.update(subpaths)
            max_depth = max([len(n) for n in paths]) if paths else 0

            self._root.add_child(child)

            for depth_ in range(max_depth):
                depth = depth_ + 1
                libraries = [p for p in sorted(paths) if len(p) == depth]
                for lib in libraries:
                    if (self._exclude_builtins and
                            (lib[0] == 'sympathy' or lib[0] == 'internal')):
                        continue
                    else:
                        if depth == 1:
                            parent = child
                        else:
                            parent = libs[lib[:-1]]
                        item = LibraryGroupItem(lib[-1], parent, self._style)
                        parent.add_child(item)
                        libs[lib] = item
                        for node in (n for n in all_nodes
                                     if tuple(n.path) == lib):
                            if not hidden_node(node):
                                node_item = LibraryNodeItem(node, item)
                                item.add_child(node_item)

    def mimeTypes(self):
        return [appcore.AppCore.mime_type_node()]

    def mimeData(self, indices):
        nodes = []
        for index in indices:
            nodes.append(self.data(index, tree_view.IdentityRole))

        mime_data = QtCore.QMimeData()
        mime_data.setData(appcore.AppCore.mime_type_node(),
                          json.dumps(nodes).encode('ascii'))
        return mime_data


class SeparateTagLibraryModel(LibraryModel):
    def __init__(self, library_root, style, model_type='Disk', parent=None):
        self._model_type = model_type
        super().__init__(library_root, style, parent=parent)

    def _build_tags(self, parent, tags, path, tag_mapping):
        if tags and not tags.term:
            for tag in tags:
                child = LibraryGroupItem(
                    tag.name, parent, self._style, tag.desc)
                parent.add_child(child)
                self._build_tags(
                    child, tag, '.'.join([path, tag.key]) if path else tag.key,
                    tag_mapping)
        else:
            tag_mapping[path] = parent

    def _build_node(self, node, tag_mapping):
        tags = node.tags
        if not tags:
            tags = self.tags

        # Filter hidden nodes.
        if not settings.instance()['Gui/library_show_hidden']:
            for tag in tags:
                try:
                    if tag.startswith('Hidden.'):
                        return
                except Exception:
                    return

        for tag in tags:
            parent = tag_mapping.get(tag, None)
            if parent:
                child = LibraryNodeItem(node, parent)
                parent.add_child(child)
                # Insert based on the first available tag.
                return

        for tag in self.tags:
            parent = tag_mapping[tag]
            child = LibraryNodeItem(node, parent)
            parent.add_child(child)

    def _build_model(self):
        """
        Build the tree model using tags separated by libraries for hierarchy.
        """
        if self._model_type == 'Disk':
            return super()._build_model()

        self._root = LibraryGroupItem('Root', None, self._style)

        for library in self._library_root.libraries:
            name = library.name
            child = LibraryGroupItem(name, self._root, self._style)
            tag_mapping = {
                tag: LibraryGroupItem(tag, child, self._style)
                for tag in self.tags}
            for value in tag_mapping.values():
                child.add_child(value)
            self._root.add_child(child)
            if self._library_root.tags:
                self._build_tags(child, self._library_root.tags.root, None,
                                 tag_mapping)
            for node in library.nodes:
                self._build_node(node, tag_mapping)


class TagLibraryModel(SeparateTagLibraryModel):
    tags = ['Unknown']

    def __init__(self, library_root, style, model_type='Disk',
                 parent=None):
        super().__init__(library_root, style,
                         model_type=model_type,
                         parent=parent)

    def _build_model(self):
        """Build the tree model using path for hierarchy."""
        if self._model_type in ['Disk', 'Separated']:
            return super()._build_model()
        elif self._model_type != 'Tag':
            return

        # Proceed with 'Tag Layout'.

        tag_mapping = {}
        libraries = self._library_root.libraries
        all_nodes = set()

        for lib in libraries:
            all_nodes.update({n for n in lib.nodes})

        self._root = LibraryGroupItem('Root', None, self._style)

        for tag in self.tags:
            if tag not in tag_mapping:
                child = LibraryGroupItem(tag, self._root, self._style)
                self._root.add_child(child)
                tag_mapping[tag] = child

        if self._library_root.tags:
            self._build_tags(self._root, self._library_root.tags.root, None,
                             tag_mapping)

        for node in all_nodes:
            self._build_node(node, tag_mapping)

    def set_type(self, model_type):
        model_type_prev = self._model_type
        self._model_type = model_type
        if self._model_type != model_type_prev:
            self.update_model()


class FlatTagLibraryModel(TagLibraryModel):
    tags = ['Unknown']

    def __init__(self, library_root, style, model_type='Disk',
                 parent=None):
        super().__init__(library_root, style,
                         model_type=model_type,
                         parent=parent)

    def _all_tags(self):
        def inner(tags, path, res):
            if tags:
                if tags.term:
                    res['.'.join(tag.key for tag in path)] = path
                else:
                    for tag in tags:
                        inner(tag, path + [tag], res)
        res = {}
        inner(self._library_root.tags.root, [], res)
        return res

    def _build_model(self):
        """Build the tree model using path for hierarchy."""
        if self._model_type in ['Disk', 'Tag', 'Separated']:
            return super()._build_model()
        elif self._model_type != 'FlatTag':
            return

        # Proceed with 'FlatTag Layout'.
        tag_mapping = {}
        libraries = self._library_root.libraries
        all_nodes = set()
        all_tags = self._all_tags()

        for lib in libraries:
            all_nodes.update({n for n in lib.nodes})

        self._root = LibraryGroupItem('Root', None, self._style)

        for tag in itertools.chain(all_tags, self.tags):
            if tag not in tag_mapping:
                tags = all_tags.get(tag)
                name = self.tags[0]
                if tags:
                    name = '/'.join(tag.name for tag in tags)

                child = FlatLibraryGroupItem(name, self._root, self._style)
                self._root.add_child(child)
                tag_mapping[tag] = child

        for node in all_nodes:
            self._build_node(node, tag_mapping)

    def flags(self, index):
        if self._model_type != 'FlatTag':
            return super().flags(index)

        if not index.isValid():
            return 0

        item = self._index_to_item.get(index.internalId())

        if item is not None and item.is_leaf():
            return (QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsDragEnabled |
                    QtCore.Qt.ItemIsSelectable)
        else:
            return QtCore.Qt.NoItemFlags


class LibraryWidget(tree_view.TreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('Gui::MainWindow::Library::View')


class LibraryFilterProxyModel(tree_view.TreeFilterProxyModelBase):
    """
    Proxy model that supplies sorting and filtering for the library model.
    """

    def __init__(self, parent=None):
        self._input_type = None
        self._output_type = None
        self._current_libraries = set()
        super().__init__(parent)

    def _show_item(self, item):
        node = item.node()
        if node is None:
            return False
        if not node.installed and (os.path.normcase(os.path.abspath(
                os.path.dirname(node.library)))
                not in self._current_libraries):
            return False

        input_match = self._match_port_type(self._input_type, node._inputs)
        output_match = self._match_port_type(
            self._output_type, node._outputs)

        return input_match and output_match

    def _match_port_type(self, type_, ports):
        if type_ is not None:
            return any(port.datatype.match(type_) for port in ports)
        return True

    def update_port_type(self, datatype, output):
        if not isinstance(datatype, DataType):
            datatype = None
        if output:
            self._output_type = datatype
        else:
            self._input_type = datatype
        self.update_filter(self._filter)
        return datatype

    def set_current_libraries(self, libraries):
        prev = self._current_libraries
        self._current_libraries = set([os.path.normcase(l) for l in libraries])
        if prev != self._current_libraries:
            self.invalidateFilter()
            self.sort(0, QtCore.Qt.AscendingOrder)


class LibraryView(tree_view.FilterTreeView):
    """Library view combination widget - library view and filter edit."""

    def __init__(self, parent=None):
        tree_model = LibraryFilterProxyModel()
        tree_widget = LibraryWidget()
        self._model_type = 'Disk'
        super().__init__(tree_model, tree_widget, parent)
        self.setObjectName('Gui::MainWindow::Library::ViewWidget')

    @QtCore.Slot(str)
    def set_model_type(self, model_type):
        self._model_type = model_type
        self._setup_view()
        self._model.set_type(model_type)

    def set_model(self, model):
        self._model_type = model._model_type
        super().set_model(model)

    def _setup_view(self):
        if self._model_type == 'FlatTag':
            self._view.setIndentation(0)
            self._view.setItemsExpandable(False)
            self._view.expandAll()
            self._view.set_highlight_mode(True)
        else:
            super()._setup_view()

    def update_libraries(self, flow):
        self._proxy_model.set_current_libraries(util.library_paths(flow))

    @QtCore.Slot(str)
    def update_input_filter(self, new_type=None):
        self._update_port_filter(new_type, output=False)

    @QtCore.Slot(str)
    def update_output_filter(self, new_type=None):
        self._update_port_filter(new_type, output=True)

    def _get_port_datatype(self, new_type):
        if isinstance(new_type, DataType):
            return new_type
        elif new_type:
            return DataType.from_str(new_type)
        return None

    def _update_port_filter(self, new_type, output):
        datatype = self._get_port_datatype(new_type)
        used_datatype = self._proxy_model.update_port_type(
            datatype, output=output)
        self._handle_expanding(isinstance(used_datatype, DataType))

    def _handle_expanding(self, state):
        if state or (self._model and self._model_type == 'FlatTag'):
            self._view.expandAll()
        else:
            self._view.collapseAll()

    def _handle_switch_to_list_view(self):
        self._view.setFocus()
        try:
            proxy_index = self._proxy_model.index(0, 0)
            if self._model_type == 'FlatTag':
                if not proxy_index.parent().isValid():
                    proxy_index = self._proxy_model.index(0, 0, proxy_index)
                self._view.setCurrentIndex(proxy_index)
            else:
                self._view.setCurrentIndex(proxy_index)
        except Exception:
            pass

    @QtCore.Slot(flow.Flow)
    def current_flow_changed(self, flow):
        self._proxy_model.set_current_libraries(util.library_paths(flow))
        if self._proxy_model._filter != '':
            self._handle_expanding(self._proxy_model._filter != '')


class QuickSearchDialog(QtWidgets.QDialog):
    item_accepted = QtCore.Signal(object, object, QtCore.QPointF)

    def __init__(
            self, library_root, flow_, port, scene_position, title=None,
            parent=None):
        super().__init__(
            parent, QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint)
        self._library_root = library_root
        self._port = port
        self._title = title

        model_type = 'FlatTag'

        self._model = FlatTagLibraryModel(
            self._library_root, self.style(),
            model_type=model_type,
            parent=self)
        self.scene_position = scene_position

        self._view = LibraryView(parent=self)
        self._view.current_flow_changed(flow_)
        self._view.set_model(self._model)

        settings_ = settings.instance()
        matcher_type = settings_['Gui/library_matcher_type']
        highlighter_type = settings_['Gui/library_highlighter_type']
        highlighter_color = settings_['Gui/library_highlighter_color']

        self._view.set_highlighter(
            (matcher_type, highlighter_type, highlighter_color))

        if self._port is not None:
            if self._port.type == flow.Type.InputPort:
                self._view.update_output_filter(self._port.datatype)
            else:
                self._view.update_input_filter(self._port.datatype)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)
        if self._title is not None:
            title_label = QtWidgets.QLabel(self._title)
            layout.addWidget(title_label)
        layout.addWidget(self._view)
        self.setLayout(layout)
        self._view.item_accepted.connect(self._accept)

    def _accept(self, item):
        self.item_accepted.emit(item, self._port, self.scene_position)
        self.accept()

    def focus_filter(self):
        self._view.focus_filter()
