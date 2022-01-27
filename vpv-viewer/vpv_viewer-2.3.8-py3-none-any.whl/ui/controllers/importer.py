# Copyright 2016 Medical Research Council Harwell.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# @author Neil Horner <n.horner@har.mrc.ac.uk>
import re
from pathlib import Path

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
import os
from vpv.ui.views.ui_importer import Ui_Dialog

VOLUME = 'Volume'
HEATMAP = 'Heatmap data'
LAMA_DATA = 'LAMA data'
VECTORS = "Vectors"
ANNOTATIONS = "Annotations"
IMAGE_SERIES = "Image series"
IMPC_ANALYSIS = "IMPC analysis"

TYPE_CHOICES = (VOLUME, HEATMAP, ANNOTATIONS, VECTORS, IMAGE_SERIES, IMPC_ANALYSIS)

# Ignore folders with these names when loading multiple directories. Find a better way to do this
SUBFOLDERS_TO_IGNORE = ['resolution_images', 'pyramid_images']


class Import(QDialog):
    def __init__(self, parent, callback, virtual_stack_callback, last_dir, appdata, dragged_files=None):
        super(Import, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # self.ui.table.setSelectionBehavior(self.ui.table.SelectRows)
        # self.ui.table.setSelectionMode(self.ui.table.SingleSelection)
        # self.ui.table.setDragDropMode(self.ui.table.InternalMove)
        # self.ui.table.setDragDropOverwriteMode(False)

        self.last_dir = last_dir
        self.callback = callback
        self.appdata = appdata
        self.virtual_stack_callback = virtual_stack_callback

        # Connect up the buttons for movin gthe rows around
        # self.ui.pushButtonUp.clicked.connect(self.move_up)
        # self.ui.pushButtonDown.clicked.connect(self.move_down)

        # Setup signals
        self.ui.pushButtonCancel.clicked.connect(self.on_cancel)
        self.ui.pushButtonChooseFile.clicked.connect(self.on_choose_files)
        self.ui.pushButtonChoseDir.clicked.connect(self.on_load_virtual_stack)
        self.ui.pushButtonOK.clicked.connect(self.on_ok)
        self.ui.checkBoxAllSameType.clicked.connect(self.on_all_same_type)
        self.type_combo_boxes = None
        self.ui.virtualStackWidget.hide()
        self.ui.pushButtonFilter.clicked.connect(self.filter_virtual_stack)

        # Setup folder filtering
        self.ui.lineEditFolderFilter.editingFinished.connect(self.set_folder_filter_pattern)

        # Create the table
        self.files_to_open = []
        self.folder_include_pattern = None

        self.vs_file_list = []
        self.vs_file_list_to_ignore = set()

        self.use_virtual_stack = False
        self.all_same_type = False

        if dragged_files:
            self.files_to_open = dragged_files
            # If one path is dropped onto the main window and it's a directory, as if we want to load a stack of slices
            if len(dragged_files) == 1 and os.path.isdir(dragged_files[0]):

                # use_folder_of_slices = QtGui.QMessageBox.question(parent, 'Choose data type?',
                #                                                   "Load individual 2D slices from folder (yes)\n"
                #                                                   "Load multiple image volumes (No)",
                #                                                   'Hello' | QtGui.QMessageBox.No)
                box = QMessageBox()
                box.setIcon(QMessageBox.NoIcon)
                box.setWindowTitle('Choose data type')
                box.setText('Load individual 2D slices from folder, or load multiple single images volumes?')
                box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                button_y = box.button(QMessageBox.Yes)
                button_y.setText('Load stack from individual 2D image slices')
                button_n = box.button(QMessageBox.No)
                button_n.setText('Load multiple 3D image volumes')
                box.exec_()
                if box.clickedButton() == button_y:
                    self.setWindowTitle("Load stack of 2D slices")
                    self.load_virtual_stack(dragged_files[0])
                else:
                    self.populate_file_list()
                    self.setWindowTitle("Load image volumes")
            else:
                self.populate_file_list()
                self.setWindowTitle("Load image volumes")
        else:
            self.populate_file_list()
            self.setWindowTitle("Load image volumes")

        self.show()

    def set_folder_filter_pattern(self):
        """
        Gets a signal to indicate folder filtering has been specified.
        Gets the filter pattern an filters the available images accordingly
        """
        pattern = self.ui.lineEditFolderFilter.text()
        self.folder_include_pattern = str(pattern)
        self.populate_file_list()

    def folder_filter(self, path: str) -> bool:
        """

        Returns
        -------
        True if path matches pattern
        False if path does not match pattern
        """
        # path

        if not self.folder_include_pattern:
            return True  # Do no filtering as there's no pattern

        # Replace any asterix in the pattern to '.+' to match anything` ````
        pattern = self.folder_include_pattern.replace('*', '.+')

        # 211019 temp bodge: ignore these LAMA subfolders that keep getting in the way
        if any([x in path for x in SUBFOLDERS_TO_IGNORE]):
            return False

        if re.search(pattern, path, re.IGNORECASE):
            return True  # Found pattern in path
        else:
            return False

    def filter_virtual_stack(self):
        contains_text = self.ui.lineEditFileNameContains.displayText()
        contains = [x.strip() for x in contains_text.split(',') if x]
        dn_contain_text = self.ui.lineEditFileNameDoesNotContain.displayText()
        dn_contain = [x.strip() for x in dn_contain_text.split(',') if x]
        files_to_use = set()
        files_to_remove = set()
        for c in contains:
            files_to_use.update([x for x in self.vs_file_list if c in x])
        for d in dn_contain:
            files_to_remove.update([x for x in self.vs_file_list if d in x])
        self.vs_file_list_to_ignore.update(set(self.vs_file_list).difference(files_to_use))
        self.vs_file_list_to_ignore.update(files_to_remove)
        self.populate_table_for_virtual_stack()

    def on_all_same_type(self, checked):
        self.all_same_type = checked

    def move_down(self):
        row = self.ui.table.currentRow()
        column = self.ui.table.currentColumn()
        if row < self.ui.table.rowCount() - 1:
            self.ui.table.insertRow(row + 2)
            for i in range(self.ui.table.columnCount()):
                self.ui.table.setItem(row + 2, i, self.ui.table.takeItem(row, i))
                #self.ui.table.setCurrentCell(row + 2, i)
            self.ui.table.removeRow(row)

    def move_up(self):
        row = self.ui.table.currentRow()
        column = self.ui.table.currentColumn();
        if row > 0:
            self.ui.table.insertRow(row - 1)
            for i in range(self.ui.table.columnCount()):
                self.ui.table.setItem(row - 1, i, self.ui.table.takeItem(row + 1, i))
                self.ui.table.setCurrentCell(row - 1, column)
            self.ui.table.removeRow(row + 1)

    def on_cancel(self):

        self.close()

    def on_choose_files(self):

        qstring_filenames = QFileDialog.getOpenFileNames(self, "Choose some data", self.last_dir)
        self.files_to_open = [x for x in qstring_filenames]
        self.populate_file_list()

    def set_last_dir(self, dir_):
        self.last_dir = dir_

    def on_load_virtual_stack(self):
        dir_ = QFileDialog.getExistingDirectory(None, "Selet a folder of of images to create virtual stack")
        self.load_virtual_stack(dir_)

    def load_virtual_stack(self, dir_):
        """
        Load a series of images into a virtual stack
        :return:
        """
        self.ui.virtualStackWidget.show()
        # Load the saved fitler terms
        saved_include_patterns = self.appdata.get_include_filter_patterns()
        saved_exclude_patterns = self.appdata.get_exclude_filter_patterns()

        last_dir = dir_
        self.last_dir = last_dir
        self.vs_file_list = self.get_all_filles_in_dir(dir_)
        self.use_virtual_stack = True
        self.populate_table_for_virtual_stack()
        self.ui.lineEditFileNameContains.setText("{}".format(','.join(saved_include_patterns)))
        self.ui.lineEditFileNameDoesNotContain.setText("{}".format(','.join(saved_exclude_patterns)))

    def get_files_for_virtual_stack(self):
        file_list = []
        for row in range(self.ui.table.rowCount()):
            if self.ui.table.cellWidget(row, 2).isChecked():
                path = self.ui.table.item(row, 0).data(QtCore.Qt.UserRole)
                file_list.append(path)
        self.virtual_stack_callback(file_list, self.last_dir)
        self.ui.virtualStackWidget.hide()
        self.close()

    def on_ok(self):
        """
        Load the data from the table that has not been unchecked
        :return:
        """
        if self.use_virtual_stack:
            self.get_files_for_virtual_stack()
            # Save the file filter patterns
            exclude_patterns = self.ui.lineEditFileNameDoesNotContain.text().strip().split(',')
            include_patterns = self.ui.lineEditFileNameContains.text().strip().split(',')
            self.appdata.set_include_filter_patterns(include_patterns)
            self.appdata.set_exclude_filter_patterns(exclude_patterns)
            return
        volumes = []
        datafiles = []
        vector_files = []
        image_series = []
        annotations = []
        impc_analysis = []

        for row in range(self.ui.table.rowCount()):
            if self.ui.table.cellWidget(row, 2).isChecked():
                type_ = str(self.ui.table.cellWidget(row, 1).currentText())
                if type_ == VOLUME:
                    vol = self.ui.table.item(row, 0).data(QtCore.Qt.UserRole)
                    volumes.append(vol)
                elif type_ == HEATMAP:
                    datafiles.append(self.ui.table.item(row, 0).data(QtCore.Qt.UserRole))
                elif type_ == VECTORS:
                    vector_files.append(self.ui.table.item(row, 0).data(QtCore.Qt.UserRole))
                elif type_ == IMAGE_SERIES:
                    image_series.append(self.ui.table.item(row, 0).data(QtCore.Qt.UserRole))
                elif type_ == ANNOTATIONS:
                    annotations.append(self.ui.table.item(row, 0).data(QtCore.Qt.UserRole))
                elif type_ == IMPC_ANALYSIS:
                    impc_analysis.append(self.ui.table.item(row, 0).data(QtCore.Qt.UserRole))

        self.callback(volumes, datafiles, annotations, vector_files, image_series, impc_analysis,
        self.last_dir, self.ui.checkBoxMemoryMap.isChecked(), self.ui.checkBoxDistrbute.isChecked())

        self.close()

    def get_all_filles_in_dir(self, dir_):

        files_to_open = []
        for path, subdirs, files in os.walk(dir_):
            for name in files:
                path_ = os.path.join(path, name)
                if self.guess_type(path_):
                    files_to_open.append(os.path.join(path, name))

        return files_to_open

    def type_combo_changed(self, index):
        if self.all_same_type:
            if self.type_combo_boxes:
                for cb in self.type_combo_boxes:
                    cb.setCurrentIndex(index)

    def populate_file_list(self):

        # Clear table
        self.ui.table.setRowCount(0)

        files_to_open = self.files_to_open

        folder_paths = []
        folders_to_remove = []

        # If a single directory has been dropped onto vpv_viewer
        for path in files_to_open:
            if os.path.isdir(path):
                folder_paths.extend(self.get_all_filles_in_dir(path))
                folders_to_remove.append(path)

        if len(folder_paths) > 0:
            files_to_open.extend(folder_paths)

        for folder in folders_to_remove:
            if folder in files_to_open:
                files_to_open.remove(folder)

        # Filter based on pattern
        files_to_open = [x for x in files_to_open if self.folder_filter(x)]

        self.ui.table.setRowCount(len(files_to_open))

        self.type_combo_boxes = []

        for row, path in enumerate(files_to_open):

            type_guess = self.guess_type(path)

            if not self.folder_filter(path):
                continue

            if not type_guess:
                continue

            item = QtGui.QTableWidgetItem(path)
            # Show last couple of path parts so we can seee where it's oaded from
            part_path = str(Path(*Path(path).parts[-3:]))
            item.setText(part_path)
            item.setData(QtCore.Qt.UserRole, path)
            self.ui.table.setItem(row, 0, item)

            type_combo = QtGui.QComboBox()
            type_combo.addItems(TYPE_CHOICES)
            type_combo.setCurrentIndex(type_combo.findText(type_guess))
            type_combo.activated.connect(self.type_combo_changed)
            self.type_combo_boxes.append(type_combo)
            self.ui.table.setCellWidget(row, 1, type_combo)

            load_checkbox = QtGui.QCheckBox()
            load_checkbox.setChecked(True)
            self.ui.table.setCellWidget(row, 2, load_checkbox)

        self.ui.table.resizeColumnsToContents()
        table_width = self.ui.table.horizontalHeader().length()
        self.setFixedWidth(table_width + 43)
        # As a bodge to get the last browsed dir, get the path of the first file in the list
        try:
            self.set_last_dir(os.path.split(files_to_open[0]))[0]
        except:
            pass

    def populate_table_for_virtual_stack(self):
        filelist = sorted(set(self.vs_file_list).difference(self.vs_file_list_to_ignore))
        self.ui.labelNumberOfFiles.setText(str(len(filelist)))
        self.ui.table.clear()
        self.ui.table.setRowCount(len(filelist))

        for row, item in enumerate(filelist):

            data_path = QtGui.QTableWidgetItem(item)
            data_path.setText(os.path.basename(item))
            data_path.setData(QtCore.Qt.UserRole, item)
            self.ui.table.setItem(row, 0, data_path)

            load_checkbox = QtGui.QCheckBox()
            load_checkbox.setChecked(True)
            self.ui.table.setCellWidget(row, 2, load_checkbox)

        self.ui.table.resizeColumnsToContents()
        table_width = self.ui.table.horizontalHeader().length()
        self.setFixedWidth(table_width + 43)

    def guess_type(self, data_path):
        volume_types = ['.nrrd', '.tiff', '.tif', '.nii', '.mnc', '.npz', '.bmp', '.json', '.gz', '.zip']
        extension = os.path.splitext(data_path)[1].lower()

        data_basname = os.path.basename(data_path)

        if extension == '.zip':
            return IMPC_ANALYSIS

        if extension == '.xml':
            return ANNOTATIONS

        if extension not in volume_types:
            return False

        heatmap_suggestions = ('stats', 'inten', 'jac')
        if any(x in data_basname for x in heatmap_suggestions):
            return HEATMAP
        if 'vector' in data_basname:
            return VECTORS

        else:
            return VOLUME

    def get_files_from_dir(self, dir_):

        self.populate_file_list([dir_])
