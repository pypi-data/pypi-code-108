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
import os
import itertools
import traceback

from .. api import component
from .. utils.components import get_components
from .. platform import node
from .. platform.exceptions import sywarn
from .. platform.parameter_helper_gui import ParameterView
from .. platform import qt_compat2
QtGui = qt_compat2.import_module(str('QtGui'))
QtWidgets = qt_compat2.import_module(str('QtWidgets'))


class DataExporterLocator(object):
    """Given a folder locate all eligable exporter classes derived from
    the IDataExporter interface."""
    def __init__(self, exporter_parent_class):
        super(DataExporterLocator, self).__init__()
        self._exporter_parent_class = exporter_parent_class

    def exporter_from_name(self, exporter_name):
        """Return the exporter associated with exporter_name."""
        exporters = get_components('plugin_*.py', self._exporter_parent_class)
        return next(exporter for exporter in exporters
                    if exporter.EXPORTER_NAME == exporter_name)

    def available_exporters(self):
        """Return the available exporters."""
        exporters = get_components('plugin_*.py', self._exporter_parent_class)
        return {exporter.EXPORTER_NAME: exporter for exporter in exporters}


class ExporterConfigurationWidget(QtWidgets.QWidget):
    status_changed = qt_compat2.Signal()
    tab_changed = qt_compat2.Signal(bool)
    hide_filename = qt_compat2.Signal(bool)
    filename_changed = qt_compat2.Signal()

    def __init__(self, available_exporters, parameters,
                 input_list, filenames_list, parent=None,
                 filename_selection=True, node=None):
        super(ExporterConfigurationWidget, self).__init__(parent)
        self._input_list = input_list
        self._filenames_list = filenames_list
        self._parameters = parameters
        self._custom_parameters = parameters['custom_exporter_data']
        self._available_exporters = available_exporters
        self._exporters = {}
        self._node = node
        self._init_gui(filename_selection)
        self.init_index()

    def _init_gui(self, filename_selection):
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setContentsMargins(0, 10, 0, 0)
        vlayout.setSpacing(0)
        vlayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        hlayout = QtWidgets.QHBoxLayout()

        exporter_label = QtWidgets.QLabel("Exporter to use")
        self._exporter_combobox = QtWidgets.QComboBox()
        hlayout.addWidget(exporter_label)
        hlayout.addWidget(self._exporter_combobox)
        hlayout.addSpacing(250)

        self.stacked_widget = QtWidgets.QStackedWidget()

        exporters = sorted(
            self._available_exporters.values(),
            key=lambda x: x.display_name())

        for i, exporter_cls in enumerate(exporters):
            self._exporter_combobox.addItem(exporter_cls.display_name())
            self._exporter_combobox.setItemData(i, exporter_cls.identifier())

        for exporter_cls in exporters:
            exp_name = exporter_cls.identifier()
            disp_name = exporter_cls.display_name()

            try:
                if exp_name not in self._custom_parameters:
                    self._custom_parameters.create_group(exp_name)

                exporter = exporter_cls(self._custom_parameters[exp_name])
                exporter.set_node(self._node)
                self._exporters[exp_name] = exporter

                if hasattr(exporter, 'parameter_view'):
                    parameter_widget = (
                        exporter.parameter_view(self._input_list))
                else:
                    parameter_widget = QtWidgets.QLabel()

            except Exception:
                parameter_widget = QtWidgets.QLabel('Failed to load')
                sywarn("{} importer failed to build its configuration gui. "
                       "The exception was:\n{}".format(
                           disp_name, traceback.format_exc()))

            self.custom_group = self._custom_parameters[exp_name]

            settings_widget = QtWidgets.QWidget()
            settings_layout = QtWidgets.QVBoxLayout()
            settings_layout.setContentsMargins(5, 5, 5, 5)
            settings_widget.setLayout(settings_layout)

            # Create default filename extension info from exporter.
            # If this is explicitly set to none then it will not be used.

            output_extension = getattr(exporter_cls, 'FILENAME_EXTENSION', '')

            use_extension = (exporter_cls.file_based() and
                             output_extension is not None)
            filename_extension = 'filename_extension'

            if use_extension:
                if filename_extension not in self.custom_group:
                    try:
                        self.custom_group.set_string(
                            'filename_extension',
                            value=output_extension,
                            label='Filename extension')
                    except AttributeError:
                        self.custom_group.set_string(
                            'filename_extension', value='',
                            label='Filename extension')

            try:
                parameter_widget.filename_changed.connect(
                    self._filename_changed)
            except AttributeError:
                pass

            if use_extension and filename_selection:
                filename_gui = self.custom_group['filename_extension'].gui()
                filename_gui.valueChanged.connect(self._filename_changed)
                settings_layout.insertWidget(0, filename_gui)

            settings_layout.insertWidget(0, parameter_widget)
            self.stacked_widget.addWidget(settings_widget)

        vlayout.addItem(hlayout)
        vlayout.addWidget(self.stacked_widget)
        vlayout.addItem(QtWidgets.QSpacerItem(500, 1))

        self.setLayout(vlayout)

        self._exporter_combobox.currentIndexChanged[int].connect(
            self._exporter_changed)
        self._exporter_combobox.activated.connect(
            self.stacked_widget.setCurrentIndex)

    def init_index(self):
        active_exporter = self._parameters['active_exporter'].value
        index = 0
        if active_exporter != '':
            index = self._exporter_combobox.findData(active_exporter)
            if index == -1:
                index = 0
        self._exporter_combobox.setCurrentIndex(index)
        self._exporter_changed(index)

    def _exporter_changed(self, index):
        active_exporter = str(self._exporter_combobox.itemData(index))
        self._parameters['active_exporter'].value = active_exporter
        self.stacked_widget.setCurrentIndex(index)
        exporter = self._exporters.get(active_exporter, None)
        if exporter is None:
            file_based = False
            hide_filename = True
        else:
            file_based = exporter.file_based()
            hide_filename = exporter.hide_filename()
        self.tab_changed.emit(not file_based)
        self.hide_filename.emit(hide_filename)
        self.status_changed.emit()

    def _filename_changed(self):
        self.filename_changed.emit()

    def create_filenames(self):
        exporter = self._exporters.get(
            self._parameters['active_exporter'].value, None)
        if exporter is not None:
            if self._filenames_list:
                return self._filenames_list
            elif self._input_list.is_valid():
                filename = self._parameters['filename'].value
                try:
                    return exporter.create_filenames(
                        self._input_list, filename)
                except Exception:
                    pass
        return []

    @property
    def valid(self):
        return self._parameters.value_or_empty('active_exporter') != ''


def inf_filename_gen(filename_wo_ext, filename_ext=None):
    """Return an infinite filename generator.
       >>> filenames = inf_filename_gen('test', 'csv')
       >>> next(filenames)
       'test.csv'
       >>> next(filenames)
       'test_1.csv'
    """
    if '' == filename_wo_ext:
        def number(x): return '{0}'.format(str(x))
    else:
        def number(x): return '' if x == 0 else '_{0}'.format(str(x))
    extsep = '' if not filename_ext else os.path.extsep
    if filename_ext is None:
        return ('{0}{1}'.format(
            filename_wo_ext, number(index))
            for index in itertools.count())
    return ('{0}{1}{2}{3}'.format(
            filename_wo_ext, number(index), extsep, filename_ext)
            for index in itertools.count())


class ExporterWidget(ParameterView):
    def __init__(self, parameter_root, input_list, filename_list,
                 exporter_param_widget,
                 parent=None, filename_selection=True, node=None):
        super(ExporterWidget, self).__init__(parent=parent)
        self._input_list = input_list
        self._filename_list = filename_list
        self._parameter_root = parameter_root
        self._exporter_param_widget = exporter_param_widget
        self._input_file_count = self._get_input_file_count()
        self._init_gui(filename_selection)
        self._node = node

        self._exporter_param_widget.status_changed.connect(self.status_changed)
        self._exporter_param_widget.filename_changed.connect(
            self._update_filename)
        self._exporter_param_widget.tab_changed.connect(self._toogle_gui)
        self._exporter_param_widget.hide_filename.connect(
            self._toggle_filename)

        self._exporter_param_widget.init_index()

    def _init_gui(self, filename_selection):
        vlayout = QtWidgets.QVBoxLayout()

        if 'directory' not in self._parameter_root:
            self._parameter_root.set_string(
                'directory', label='Output directory',
                description='Select the directory where to export the files.',
                editor=node.Util.directory_editor().value())

        if 'filename' not in self._parameter_root:
            self._parameter_root.set_string(
                'filename', label='Filename',
                description='Filename without extension.')

        outputs_vlayout = QtWidgets.QVBoxLayout()

        for child in self._parameter_root.children():
            if child.name not in ['active_exporter',
                                  'custom_exporter_data']:
                child_gui = child.gui()
                if child.name == 'filename':
                    child_gui.valueChanged.connect(self._update_filename)
                    self.filename_gui = child_gui
                outputs_vlayout.addWidget(child_gui)

        self._preview_label = QtWidgets.QLabel('')
        self._preview_label.setMaximumWidth(500)
        self._preview_label.setWordWrap(True)

        outputs_vlayout.addWidget(self._preview_label)

        self.outputs_groupbox = QtWidgets.QGroupBox('Outputs')
        self.outputs_groupbox.setLayout(outputs_vlayout)

        vlayout.addWidget(self._exporter_param_widget)
        vlayout.addWidget(self.outputs_groupbox)
        self.setLayout(vlayout)

        self._update_filename()

    def _toogle_gui(self, status):
        if status:
            self._preview_label.setText('')
            self.outputs_groupbox.setEnabled(False)
        else:
            self._update_filename()
            self.outputs_groupbox.setEnabled(True)

    def _toggle_filename(self, status):
        self.filename_gui.setEnabled(not status)

    def _update_filename(self):
        filenames = self._exporter_param_widget.create_filenames()

        if isinstance(filenames, list):
            length = len(list(filenames))
        else:
            length = self._input_file_count

        # Preview at most 5 entries.
        length = min(5, length)

        preview_filenames = [fq_filename for fq_filename, _ in zip(
            filenames, range(length))]
        if not len(preview_filenames):
            self._preview_label.setText('Nothing to preview')
        else:
            self._preview_label.setText(', '.join(preview_filenames))

    def _get_input_file_count(self):
        if self._input_list.is_valid():
            inputfile_count = len(self._input_list)
        else:
            # When no input data is available show preview for three
            # filenames.
            inputfile_count = 3
        return inputfile_count

    @property
    def valid(self):
        return self._exporter_param_widget.valid


# Compat for legacy plugins.
# TODO(erik): Remove these.

class ExporterAccessManagerBase(object):
    def __init__(self, exporter):
        self._exporter = exporter

    def create_filenames(self, parameter_root, node_context_input):
        if self._exporter.file_based():
            filename = parameter_root['filename'].value
            return self._exporter.create_filenames(
                node_context_input, filename)
        return self._exporter.create_filenames(node_context_input, None)

    def parameter_view(self, parameter_root, node_context_input):
        return self._exporter.parameter_view(node_context_input)

    def file_based(self):
        return self._exporter.file_based()

    def hide_filename(self):
        return self._exporter.hide_filename()


def create_fq_filenames(directory, filenames):
    gen = (os.path.join(directory, filename) for filename in filenames)
    if isinstance(filenames, list):
        return list(gen)
    else:
        return gen
    return gen


# External API


class IDataExporter(component.NodePlugin):
    """Interface for a DataExporter. It's important to set EXPORTER_NAME
    to a unique name otherwise errors will occur."""
    EXPORTER_NAME = "UNDEFINED"
    DISPLAY_NAME = None
    one_to_one, one_to_many, many_to_one = range(3)

    def __init__(self, parameters):
        """
        Parameters
        ----------
        parameters : ParameterGroup
                     plugin parameters.
        """

        self._parameters = parameters

    @classmethod
    def identifier(cls):
        """
        Returns
        -------
        str
            Unique identifier for importer.
        """
        return cls.EXPORTER_NAME

    @classmethod
    def display_name(cls):
        """
        Returns
        -------
        str
            Display name for return.
        """
        return cls.DISPLAY_NAME or cls.EXPORTER_NAME

    def create_filenames(self, data, filename, ext=True):
        """
        Parameters
        ----------
        data : list of sydata
               Items to export.
        filename : str
                   Base filename without extension.
        ext : bool or str
              Extensions string or True to add
              default extension, False for no extension.
        Returns
        -------
        list of str
            relative filenames with extension.
        """
        raise NotImplementedError

    def export_data(self, in_sytext, fq_outfilename,
                    parameters=None, progress=None):
        raise NotImplementedError

    def parameter_view(self, *args):
        """
        Returns
        -------
        QtWidgets.QWidget
            GUI widget for exporter.
        """
        return QtWidgets.QWidget()

    @staticmethod
    def file_based():
        """
        Returns
        -------
        bool
            True if exporter is file based (creates files on disk) instead.
        """

        raise NotImplementedError

    @staticmethod
    def hide_filename():
        """
        Returns
        -------
        bool
            True if filename preview should be hidden from view.
        """

        raise NotImplementedError

    def cardinality(self):
        """
        Relation between input elements and output elements created.

        Returns
        -------
        int
            Cardinality enum.
            IDataExporter.one_to_one, IDataExporter.one_to_many
            IDataExporter.many_to_one.
        """
        return self.one_to_one


class DataExporterBase(IDataExporter):

    def __init__(self, parameters):
        self._parameters = parameters
        self._node = None

    @classmethod
    def plugin_impl_name(cls) -> str:
        return cls.EXPORTER_NAME

    @staticmethod
    def file_based():
        return True

    @staticmethod
    def hide_filename():
        return False

    def node(self):
        """Return the current node or None if set_node was not called."""
        return self._node

    def set_node(self, node):
        self._node = node

    def create_filenames(self, data, filename, ext=True):
        if self.file_based():
            if ext is True:
                ext = self._parameters[
                    'filename_extension'].value
            if ext is False:
                ext = None
            if self.cardinality() == self.one_to_one:
                return inf_filename_gen(
                    filename, ext)
            elif self.cardinality() == self.many_to_one:
                if ext is not None:
                    return ['{}.{}'.format(filename, ext)]
                else:
                    return [filename]
            elif self.cardinality() == self.one_to_many:
                raise NotImplementedError
        return []


class ADAFDataExporterBase(DataExporterBase):
    pass


class TableDataExporterBase(DataExporterBase):
    pass


class TextDataExporterBase(DataExporterBase):
    @staticmethod
    def plugin_base_name():
        return 'Export Text'


class FigureDataExporterBase(DataExporterBase):
    @staticmethod
    def plugin_base_name():
        return 'Export Figure'


class DatasourceDataExporterBase(DataExporterBase):
    pass


def available_plugins(plugin_base_class):
    dil = DataExporterLocator(plugin_base_class)
    return dil.available_exporters()


def configuration_widget(plugins, parameters, input_list,
                         external_filenames, node=None):
    conf_widget = ExporterConfigurationWidget(plugins, parameters, input_list,
                                              external_filenames)
    # TODO(erik): no obvious need for two classes here, merge them?!
    # They are only used from here and together.
    widget = ExporterWidget(
        parameters, input_list, external_filenames, conf_widget)
    return widget
