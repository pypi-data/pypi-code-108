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
import os.path
import glob
import base64
import json
from sympathy.api import qt as qt_compat
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')


class PresetsWidget(QtWidgets.QWidget):
    """A widget for handling preset data (loading, storing)."""

    def __init__(self, parent=None):
        super(PresetsWidget, self).__init__(parent)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        hlayout = QtWidgets.QHBoxLayout()

        presets_label = QtWidgets.QLabel("Presets")
        self.presets_combobox = QtWidgets.QComboBox()
        self.presets_save_button = QtWidgets.QPushButton("Save")
        self.presets_saveas_button = QtWidgets.QPushButton("Save As...")
        self.presets_load_button = QtWidgets.QPushButton("Load")

        hlayout.addWidget(self.presets_load_button)
        hlayout.addWidget(self.presets_save_button)
        hlayout.addWidget(self.presets_saveas_button)

        vlayout.addWidget(presets_label)
        vlayout.addWidget(self.presets_combobox)
        vlayout.addItem(hlayout)

        self.setLayout(vlayout)

        self.presets_load_button.clicked[bool].connect(self._presetLoad)
        self.presets_save_button.clicked[bool].connect(self._presetSave)
        self.presets_saveas_button.clicked[bool].connect(self._presetSaveAs)

    def set_presets(self, item_list):
        self.presets_combobox.addItems(sorted(item_list))

    def append_preset(self, item):
        self.presets_combobox.addItem(item)
        self.presets_combobox.setCurrentIndex(
            self.presets_combobox.count() - 1)

    def get_selected_preset(self):
        return self.presets_combobox.currentText()

    def _presetLoad(self):
        self.emit(QtCore.SIGNAL('presetLoad()'))

    def _presetSave(self):
        self.emit(QtCore.SIGNAL('presetSave()'))

    def _presetSaveAs(self):
        self.emit(QtCore.SIGNAL('presetSaveAs()'))


class PresetHandlerWidget(QtWidgets.QWidget):
    def __init__(self, parameters, definition, parent=None):
        super(PresetHandlerWidget, self).__init__(parent)

        self._parameters = parameters
        self._nodeid = definition['nodeid']
        self._loaded_data = None

        self._preset_dir = self._create_preset_dir()

        vlayout = QtWidgets.QVBoxLayout()

        self._preset_view = PresetsWidget()

        # Init preset view
        self._name_file_map = self._list_presets_on_disk(self._preset_view)

        vlayout.addWidget(self._preset_view)

        self.setLayout(vlayout)

        QtCore.QObject.connect(self._preset_view,
                               QtCore.SIGNAL("presetLoad()"),
                               self.preset_load)
        QtCore.QObject.connect(self._preset_view,
                               QtCore.SIGNAL("presetSave()"),
                               self.preset_save)
        QtCore.QObject.connect(self._preset_view,
                               QtCore.SIGNAL("presetSaveAs()"),
                               self.preset_saveas)

    def _create_preset_dir(self):
        preset_dir = os.path.join(os.getcwd(), 'presets', self._nodeid)
        if not os.path.isdir(preset_dir):
            os.makedirs(preset_dir)
        return preset_dir

    def _list_presets_on_disk(self, preset_view):
        preset_files = glob.glob(os.path.join(self._preset_dir, '*'))
        name_file_map = {}

        for preset_filename in preset_files:
            with open(preset_filename, 'r') as f:
                data = f.read()
                data_format = json.loads(data)
                preset_view.append_preset(data_format['name'])
                name_file_map[data_format['name']] = preset_filename

        return name_file_map

    def loaded_data(self):
        return self._loaded_data

    def preset_load_name(self, preset_name):
        fq_filename = self._name_file_map[preset_name]

        self._parameters['active_preset']['value'] = preset_name

        with open(fq_filename, 'r') as f:
            data = f.read()
            data_format = json.loads(data)
            self._loaded_data = data_format['data']

        # Update combobox the correct name
        model = self._preset_view.presets_combobox.model()
        item_count = model.rowCount(model.parent(model.index(0, 0)))
        preset_names = [str(model.data(model.index(i, 0)).toString())
                        for i in range(0, item_count)]

        if preset_name in preset_names:
            self._preset_view.presets_combobox.setCurrentIndex(
                preset_names.index(preset_name))

        self.emit(QtCore.SIGNAL("presetLoad()"))

    def preset_load(self):
        preset_name = str(self._preset_view.get_selected_preset())
        self.preset_load_name(preset_name)

    def preset_save(self):
        preset_name = str(self._preset_view.get_selected_preset())
        fq_filename = self._name_file_map[preset_name]

        self._parameters['active_preset']['value'] = preset_name

        data_format = {}
        data_format['name'] = preset_name
        data_format['nodeid'] = self._nodeid
        data_format['data'] = self._parameters

        with open(fq_filename, 'w') as f:
            f.write(json.dumps(data_format, sort_keys=True, indent=4))

    def preset_saveas(self):
        preset_name, ok = QtGui.QInputDialog.getText(self,
                                                     "Save As...",
                                                     "Preset name:")
        preset_name = str(preset_name)
        if ok:
            preset_filename_base64 = base64.urlsafe_b64encode(preset_name)
            fq_filename = os.path.join(self._preset_dir,
                                       preset_filename_base64 + '.json')

            self._parameters['active_preset']['value'] = preset_name

            data_format = {}
            data_format['name'] = preset_name
            data_format['nodeid'] = self._nodeid
            data_format['data'] = self._parameters

            with open(fq_filename, 'w') as f:
                f.write(json.dumps(data_format, sort_keys=True, indent=4))

            if preset_name not in self._name_file_map:
                self._preset_view.append_preset(preset_name)
            self._name_file_map[preset_name] = fq_filename
