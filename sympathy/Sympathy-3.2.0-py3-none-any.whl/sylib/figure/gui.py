# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
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
import uuid
import functools
import itertools

from sympathy.api import qt2 as qt
from sympathy.api import ParameterView, node as synode
from sympathy.platform.widget_library import SyBaseToolBar
from sylib.figure import models
from sylib.figure import wizards
from sylib.icons import utils as icon_utils
from sylib.tree_model import qt_model, models as base_models

QtCore = qt.QtCore
QtGui = qt.QtGui
QtWidgets = qt.QtWidgets

MIME = {
    'layout_tree_item_id': 'application-x-sympathy/figure.layout.tree.item.id',
    'layout_tree_new_item':
        'application-x-sympathy/figure.layout.tree.new.item',
    'instance': 'application-x-sympathy/figure.instance'
}


TOOLBAR_ITEMS = [
    'separator',
    models.Axes,
    'separator',
    models.LinePlot,
    models.ScatterPlot,
    models.BarPlot,
    models.HistogramPlot,
    models.TimelinePlot,
    models.HeatmapPlot,
    models.BoxPlot,
    models.PieChart,
    models.Annotation,
    'separator',
    models.BarContainer,
    models.Iterator,
    'separator',
    models.Legend,
    models.Grid,
]


ITEM_TYPE_TO_CLASS = {
    i.node_type: i for i in TOOLBAR_ITEMS if i != 'separator'}


class DataModel:
    def __init__(self, data, data_table=None):
        self.instance = uuid.uuid4().bytes
        self._data_table = data_table
        self.set_data(data)

    def set_data(self, data):
        self.model = data
        self.root = models.Root(data)
        self.root.set_data_table(self._data_table)


class ParameterTreeView(qt_model.BaseParameterTreeView):
    def __init__(self, input_table, mime=MIME, parent=None):
        super(ParameterTreeView, self).__init__(input_table, mime, parent)
        self.completer_models = {
            'default':
                (qt_model.SyDataTreeCompleterModel,
                 (self._input_table, ),
                 {'parent': self})
        }

    def add(self, item_cls):
        selected_indices = self.selectedIndexes()
        model = self.model()
        figure_node = self.model().root_item()
        figure_index = model.item_to_index(figure_node)
        if selected_indices:
            selected_index = selected_indices[0]
        else:
            self.setCurrentIndex(figure_index)
            selected_index = figure_index
        selected_item = model.index_to_item(selected_index)

        parent_axes = selected_item.find_first_parent_node_with_class(
            models.Axes)
        if item_cls != models.Axes:
            if not figure_node.has_axes():
                parent_axes = self.add_child(
                    figure_node, models.Axes, figure_index)
            elif parent_axes is None:
                parent_axes = [c for c in figure_node.children if
                               isinstance(c, models.Axes)][0]

        plot_nodes = models.BasePlot, models.BasePlotContainer

        if item_cls in selected_item.valid_children():
            parent_node = selected_item
        elif issubclass(item_cls, models.Axes):
            parent_node = figure_node
        elif issubclass(item_cls, (models.Grid, models.Legend)):
            parent_node = parent_axes
        elif issubclass(item_cls, plot_nodes):
            if isinstance(selected_item, plot_nodes):
                parent_node = selected_item.parent
            else:
                parent_node = parent_axes.plot_container
        elif item_cls not in selected_item.valid_children():
            parent_node = selected_item.parent
        else:
            parent_node = selected_item
        parent_index = model.item_to_index(parent_node)

        if (item_cls in parent_node.valid_children() and
                item_cls in parent_node.get_available_children()):
            new_item = self.add_child(parent_node, item_cls, parent_index)
            new_item_idx = model.item_to_index(new_item)
            self.setCurrentIndex(new_item_idx)

    def drag_move_event_handling(self, event, item_class, index):
        if index.isValid():
            drop_indicator_position = self.dropIndicatorPosition()
            parent_item = index.model().data(index, QtCore.Qt.UserRole)
            if parent_item is None:
                event.ignore()
                return
            if drop_indicator_position != QtWidgets.QAbstractItemView.OnItem:
                # If the drop indicator is not on the item we need to get the
                # parent item in the tree instead.
                parent_item = parent_item.parent
            if item_class in parent_item.get_available_children():
                event.accept()
            else:
                event.ignore()
        else:
            # Only axes items are allowed outside tree (root level).
            # If Plots or PlotContainers are dragged in and no Axes exists, one
            # will be created automatically.
            root = self.model().model.root
            figure = root.find_all_nodes_with_class(models.Figure)[0]
            allowed_super_cls = (models.BasePlot, models.BasePlotContainer)
            if item_class in figure.get_available_children():
                event.accept()
            elif (issubclass(item_class, allowed_super_cls) and
                    not figure.has_axes()):
                # create axes
                axes = models.Axes.create_empty_instance(figure)
                model = self.model()
                figure_index = model.index(0, 0)
                model.insert_node(
                    axes, figure, figure_index, len(figure.children))
                # add item to axes
                event.accept()
            else:
                event.ignore()


class DictStackedWidget(QtWidgets.QStackedWidget):
    """A StackedWidget that stores widgets by key instead of by index."""
    currentChanged = QtCore.Signal(str)
    widgetRemoved = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._indices = []

    def addWidget(self, key, widget):
        """Add a widget with key."""
        super().addWidget(widget)
        self._indices.append(key)

    def insertWidget(self, key, widget):
        """Synonym to addWidget"""
        self.addWidget(key, widget)

    def currentKey(self):
        """Return the current key or None if there are no child widgets."""
        index = self.currentIndex()
        if index == -1:
            return None
        else:
            return self._indices[index]

    def hasKey(self, key):
        """Return True if a widget exists at key."""
        return key in self._indices

    def setCurrentKey(self, key):
        """Set current widget to that at key."""
        try:
            index = self._indices.index(key)
        except IndexError:
            return
        super().setCurrentIndex(index)
        self.currentChanged.emit(key)

    def setCurrentWidget(self, widget):
        """Set current widget to widget."""
        index = self.indexOf(widget)
        if index == -1:
            return
        else:
            key = self._indices[index]
            self.setCurrentKey(key)

    def widget(self, key):
        """Get widget at key."""
        try:
            index = self._indices.index(key)
        except IndexError:
            return None
        return super().widget(index)

    def removeWidget(self, widget):
        """
        Remove widget from the stacked widget without destroying it or
        changing its parent.
        """
        index = self.indexOf(widget)
        if index == -1:
            return
        else:
            super().removeWidget(widget)
            key = self._indices.pop(index)
            self.widgetRemoved.emit(key)


class ImageMenuItem(QtWidgets.QWidgetAction):
    """A menu item consisting of a large image."""
    def __init__(self, kind, tooltip, *, parent=None):
        super().__init__(parent)
        self._kind = kind
        self._tooltip = tooltip

    def createWidget(self, parent):
        icon = icon_utils.create_icon(getattr(
            icon_utils.SvgIcon, f"{self._kind}_wizard"))
        button = QtWidgets.QPushButton(parent=parent)
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(200, 100))
        button.setToolTip(self._tooltip)
        button.clicked.connect(self.triggered)
        return button


class FigureFromTableWidget(ParameterView):
    def __init__(self, input_table, parameters, parent=None):
        super().__init__(parent=parent)

        self.input_table = input_table
        self.parameters = parameters

        self._data_model = DataModel(parameters.value,
                                     data_table=self.input_table)
        self._model = qt_model.TreeItemModel(
            self._data_model, root_cls=models.Figure,
            item_type_to_class=ITEM_TYPE_TO_CLASS, mime=MIME)

        self._wizards = {name: None for name in wizards.wizard_classes.keys()}

        self._init_gui()
        self._init_from_parameters()

        exported_config = self._data_model.root.export_config()
        self._curr_config = exported_config

        self._poll_timer = QtCore.QTimer()
        self._poll_timer.setInterval(300)
        self._poll_timer.timeout.connect(self._poll_changes)
        self._poll_timer.start()

    def _init_gui(self):
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.stacked = DictStackedWidget()

        # Actions for going to home view (template selection) and to tree view
        self._show_home_action = QtWidgets.QAction(self, 'show_home')
        icon = icon_utils.create_icon(icon_utils.SvgIcon.template)
        self._show_home_action.setIcon(icon)
        self._show_home_action.setToolTip(
            "Create a new figure from a template.")
        self._show_home_action.triggered.connect(self._show_home)
        self._show_tree_action = QtWidgets.QAction(self, 'show_tree')
        icon = icon_utils.create_icon(icon_utils.SvgIcon.tools)
        self._show_tree_action.setIcon(icon)
        self._show_tree_action.setToolTip(
            "Continue configuration in advanced configuration view.")
        self._show_tree_action.triggered.connect(self._show_tree)
        self._back_action = QtWidgets.QAction(self, 'back')
        icon = icon_utils.create_icon(icon_utils.SvgIcon.back)
        self._back_action.setIcon(icon)
        self._back_action.setToolTip(
            "Discard and go back to template selection.")
        self._back_action.triggered.connect(self._show_home)

        # Init home view
        home_widget = QtWidgets.QWidget()
        home_layout = QtWidgets.QVBoxLayout()
        columns = 3
        for section_name, wizard_classes in wizards.sections.items():
            section_header = QtWidgets.QLabel(section_name)
            home_layout.addWidget(section_header)
            grid_layout = QtWidgets.QGridLayout()
            for i, wizard_cls in enumerate(wizard_classes):
                button = wizard_cls.get_button()
                button.clicked.connect(
                    functools.partial(self._show_wizard, wizard_cls.name))
                grid_layout.addWidget(button, i // columns, i % columns)
            # Fix layout if less than one full row of buttons were added to
            # a grid layout:
            for col in range(columns):
                grid_layout.addItem(QtWidgets.QSpacerItem(0, 0), 0, col)
                grid_layout.setColumnStretch(col, 1)
            home_layout.addLayout(grid_layout)
        home_widget.setLayout(home_layout)
        self.stacked.addWidget('home', home_widget)

        # Init tree view (advanced view)
        self.param_tree = ParameterTreeView(
            self.input_table, mime=MIME, parent=self)
        self.param_tree.setModel(self._model)
        self.toolbar = qt_model.BaseItemsToolBar(
            self.param_tree, TOOLBAR_ITEMS, mime=MIME, parent=self)
        first_action = self.toolbar.actions()[0]
        self.toolbar.insertAction(first_action, self._show_home_action)
        self.toolbar.insertSeparator(first_action)
        tree_layout = QtWidgets.QVBoxLayout()
        tree_layout.setSpacing(0)
        tree_layout.addWidget(self.toolbar)
        tree_layout.addWidget(self.param_tree)
        tree_container = QtWidgets.QWidget()
        tree_container.setLayout(tree_layout)
        self.stacked.addWidget('tree', tree_container)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.stacked)
        self.setLayout(main_layout)

    def _init_wizard(self, name):
        wizard_cls = wizards.wizard_classes[name]
        wizard = wizard_cls(self._model)
        self._wizards[name] = wizard
        wizard.wizard_changed.connect(
            functools.partial(self._wizard_changed, name))

        parameters_gui = wizard.gui()
        if parameters_gui is None:
            return

        toolbar = SyBaseToolBar()
        toolbar.addAction(self._back_action)
        toolbar.addAction(self._show_tree_action)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(parameters_gui)
        wizard_gui = QtWidgets.QWidget()
        wizard_gui.setLayout(layout)
        self.stacked.addWidget(name, wizard_gui)

    def _show_wizard(self, name):
        if self._wizards[name] is None:
            self._init_wizard(name)
        if self.stacked.hasKey(name):
            self.stacked.setCurrentKey(name)
        else:
            self._show_tree()
        self._wizard_changed(name)

    def _wizard_changed(self, name):
        self._model.set_data(self._wizards[name].get_model())
        self.expand_axes()

    def _show_home(self):
        # res = QtWidgets.QMessageBox.question(
        #     self, "Discard configuration?",
        #     "This will discard the current configuration. "
        #     "Are you sure you want to proceed?")
        # if res == QtWidgets.QMessageBox.No:
        #     return

        self.stacked.setCurrentKey('home')

    def _show_tree(self):
        self.stacked.setCurrentKey('tree')

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.param_tree.resizeColumnToContents(0)

    def _init_from_parameters(self):
        self.param_tree.resizeColumnToContents(0)

        if self._model.root_item().has_axes():
            self.stacked.setCurrentKey('tree')
        else:
            self.stacked.setCurrentKey('home')

        self.expand_axes()

    def expand_axes(self):
        # expand all axes
        num_axes = self._model.rowCount()
        for i in range(num_axes):
            index = self._model.index(i, 0)
            self.param_tree.setExpanded(index, True)
            # expand all Plots
            for row in range(self._model.rowCount(index)):
                child_index = self._model.index(row, 0, index)
                item = self._model.index_to_item(child_index)
                if isinstance(item, models.Plots):
                    self.param_tree.setExpanded(child_index, True)

    def save_parameters(self):
        if self.param_tree.state() == QtWidgets.QAbstractItemView.EditingState:
            index = self.param_tree.currentIndex()
            self.param_tree.currentChanged(index, index)
        self._save_parameters()

    def _save_parameters(self):
        self.parameters.value = self._data_model.root.export_config()

    def cleanup(self):
        self._poll_timer.timeout.disconnect(self._poll_changes)
        self._poll_timer.stop()

    def _poll_changes(self):
        # Resetting internal counter between calls to save parameters.
        self._data_model.root._given_ids.clear()
        exported_config = self._data_model.root.export_config()
        new_config = json.dumps(exported_config)
        if new_config != self._curr_config:
            self._curr_config = new_config
            self._save_parameters()
