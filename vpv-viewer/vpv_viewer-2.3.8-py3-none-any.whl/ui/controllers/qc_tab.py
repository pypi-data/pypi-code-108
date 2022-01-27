from pathlib import Path
import shutil
from datetime import datetime
import os

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog

import yaml
import addict
from ordered_set import OrderedSet

from vpv.ui.views.ui_qctab import Ui_QC
from vpv.utils.appdata import AppData
from vpv.common import info_dialog, question_dialog, Layers, error_dialog
from lama.common import get_file_paths
from lama.paths import get_specimen_dirs, LamaSpecimenData


SUBFOLDERS_TO_IGNORE = ['resolution_images', 'pyramid_images']


class QC(QtGui.QWidget):

    load_specimen_signal = QtCore.pyqtSignal(list, str)
    clear_data_signal = QtCore.pyqtSignal()

    def __init__(self, vpv, mainwindow, appdata: AppData):
        super(QC, self).__init__(mainwindow)
        self.ui = Ui_QC()
        self.ui.setupUi(self)
        self.vpv = vpv
        self.appdata = appdata

        self.ui.pushButtonLoad.clicked.connect(self.load_data)
        self.ui.pushButtonSaveQC.clicked.connect(self.save_qc)
        self.ui.pushButtonNextSpecimen.clicked.connect(self.next_specimen)
        self.ui.listWidgetQcSpecimens.currentRowChanged.connect(self.load_specimen)
        self.ui.checkBoxFlagWholeImage.clicked.connect(self.flag_whole_image)
        self.ui.textEditSpecimenNotes.textChanged.connect(self.specimen_note_changed)
        self.ui.checkBoxFlagWholeImage.stateChanged.connect(self.whole_embryo_flag_slot)
        self.ui.pushButtonFlagAllLabels.clicked.connect(self.flag_all_labels)

        self.mainwindow = mainwindow
        self.specimen_index: int = 0

        self.qc_results_file: Path = None
        self.is_active = False
        self.atlas_meta = None
        self.root_dir = None  # The folder that is opened, all paths relative to this
        self.screenshot_dir = None
        self.last_label_clicked: int = 0

        self.specimens = []  # Containing SpecimenPaths objects

        header = self.ui.tableWidgetFlagged.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        self.atlas_meta_name = None  # Name of atlas metadata file so we know which atlas version we QCd against'

    def flag_all_labels(self):
        for label in self.atlas_meta.index:
            self.specimens[self.specimen_index].qc_flagged.add(label)
        self.update_flagged_list()

    def whole_embryo_flag_slot(self, state: int):
        if state == 0:
            self.screenshot(0, remove=True)
        elif state == 2:
            self.screenshot(0)

    def screenshot(self, label: int, remove=False):
        """
        Get the current specimen and save a screen shot of the current views that highlight the QC issue.
        if label == 0, save screenshot for whole embryo
        """

        current_spec: LamaSpecimenData = self.specimens[self.specimen_index]
        preprocessed_id = current_spec.specimen_root.name.split('_')[1]
        # Make screenshot dir for line if not already exists
        ss_dir = self.screenshot_dir / current_spec.line_id
        ss_dir.mkdir(exist_ok=True)

        # If there's an atlas an the label is not in it, return
        if label == 0:
            label_name = 'whole_embryo'

        elif label < 0 or (self.atlas_meta is not None and label not in self.atlas_meta.index):
            return

        elif self.atlas_meta is not None:
            label_name = self.atlas_meta.at[label, 'label_name']

        ss_file: Path = ss_dir / f'{preprocessed_id}_{label_name if label_name else self.last_label_clicked}.jpg'

        if remove:

            ss_file.unlink(missing_ok=True)
            print(f'Removed QC screenshot: {ss_file}')
        else:
            image = self.mainwindow.ui.centralwidget.grab()
            image.save(str(ss_file), quality=30)
            print(f'QC screenshot saved: {ss_file}')

    def specimen_note_changed(self):
        text = str(self.ui.textEditSpecimenNotes.toPlainText())
        self.specimens[self.specimen_index].notes = text

    def flag_whole_image(self, checked):
        self.specimens[self.specimen_index].flag_whole_image = checked

    def load_atlas_metadata(self):
        self.atlas_meta, self.atlas_meta_name = self.vpv.load_atlas_meta()

    def label_clicked_slot(self, label_num):

        label_num = int(label_num)

        if not self.is_active:
            return

        if label_num == 0:
            return

        s: set = self.specimens[self.specimen_index].qc_flagged

        if label_num in s: # remove if already in flag list. Ask before delete.

            label_name = self.atlas_meta.at[label_num, 'label_name']
            remove_comfirmed = question_dialog(None, f'{label_name}', 'Remove QC flag and screenshot?')

            if remove_comfirmed:
                s.remove(label_num)
                self.screenshot(label_num, remove=True)
        else:
            s.add(label_num)
            self.screenshot(label_num)

        self.last_label_clicked = label_num
        self.update_flagged_list()

    def update_flagged_list(self):
        self.ui.tableWidgetFlagged.clear()
        spec_qc = self.specimens[self.specimen_index]
        self.ui.tableWidgetFlagged.setRowCount(0)

        for i,  f in enumerate(spec_qc.qc_flagged):
            if f == 0:
                continue

            if self.atlas_meta is not None:
                label_name = self.atlas_meta.at[f, 'label_name']
            else:
                label_name = ''
            self.ui.tableWidgetFlagged.insertRow(i)
            self.ui.tableWidgetFlagged.setItem(i, 0, QtGui.QTableWidgetItem(str(f)))
            self.ui.tableWidgetFlagged.setItem(i, 1,  QtGui.QTableWidgetItem(label_name))

    def update_specimen_list(self):
        self.ui.listWidgetQcSpecimens.clear()

        for s in self.specimens:
            view_path = str(Path(*s.outroot.parts[-4:]))
            self.ui.listWidgetQcSpecimens.addItem(view_path)

    def next_specimen(self):
        new_index = self.specimen_index + 1
        self.load_specimen(new_index)

    def load_specimen(self, idx):
        try:
            spec_qc = self.specimens[idx]
        except IndexError:
            spec_qc = self.specimens[0]

        spec_qc.qc_done = True
        spec_dir = spec_qc.outroot.parent
        # self.load_specimen_into_viewer(spec_dir)

        num_top_views = 3

        # Set the top row of views
        for i in range(num_top_views):
            vol_id = spec_qc.vol_id
            label_id = spec_qc.label_id
            self.vpv.views[i].layers[Layers.vol1].set_volume(vol_id)
            self.vpv.views[i].layers[Layers.vol2].set_volume(label_id)

        title = spec_dir.name
        self.vpv.mainwindow.setWindowTitle(title)

        self.vpv.data_manager.show2Rows(False)

        # Set colormap
        # Todo. Fall back to 'anatomy_labels' if atlas metadata does not have color info
        lut_name = 'custom_atlas_labels' if 'colour' in self.atlas_meta.columns else 'anatomy_labels'
        self.vpv.data_manager.on_vol2_lut_changed(lut_name)

        # opacity
        self.vpv.data_manager.modify_layer(Layers.vol2, 'set_opacity', 0.4)

        self.vpv.data_manager.update()

        self.specimen_index = idx
        self.update_flagged_list()

        self.ui.checkBoxFlagWholeImage.blockSignals(True)
        self.ui.checkBoxFlagWholeImage.setChecked(spec_qc.flag_whole_image)
        self.ui.checkBoxFlagWholeImage.blockSignals(False)

        self.ui.textEditSpecimenNotes.setText(spec_qc.notes)
        self.ui.listWidgetQcSpecimens.setCurrentRow(idx)

    def save_qc(self):
        # Convert the list of SpecimenDataPath objects to a yaml

        # make a backup first

        bu_file = self.qc_results_file.parent / 'backup' / f'{self.qc_results_file.stem} {str(datetime.now())}'
        bu_dir = bu_file.parent
        bu_dir.mkdir(exist_ok=True)

        try:
            shutil.copy(self.qc_results_file, bu_file)
        except Exception as e: # catch everything. We don't want to lose QC data.
            print(f'cannot save qc backup {e}')

        results = {}
        with open(self.qc_results_file, 'w') as fh:

            s: LamaSpecimenData
            for s in self.specimens:
                if not s.qc_done:
                    continue

                preprocessed_id = s.specimen_root.name.split('_')[1]
                results[preprocessed_id] = {'qc_flagged': list(s.qc_flagged),
                                            'flag_whole_image': s.flag_whole_image,
                                            'notes': s.notes,
                                            'path': str(s.outroot),
                                            'atlas_version': self.atlas_meta_name}

            yaml.dump(results, fh)
            info_dialog(self.mainwindow, 'Saved OK', f'QC dsaved to {self.qc_results_file}')

    def load_qc(self, root):
        print('loading qc')

        if self.qc_results_file and self.qc_results_file.is_file():
            info_dialog(self.mainwindow, 'Previous QC file exists', 'Continuing QC')
            with open(self.qc_results_file, 'r') as fh:
                qc_info = addict.Dict(yaml.load(fh))
        else:
            info_dialog(self.mainwindow, 'QC file NOT found', 'A new qc session will be started')  # Do it on next save
            qc_info = {}

        self.specimens = get_specimen_dirs(root)

        self.vpv.clear_views()

        # For each Lama specimen object, assign previously qc-flagged labels
        for s in self.specimens:
            s.setup() # Lets get rid of setup method
            s.qc_done = False
            preprocesed_id = s.specimen_root.name.split('_')[1]
            if preprocesed_id in qc_info:
                s.qc_done = True
                s.qc_flagged = OrderedSet(qc_info[preprocesed_id]['qc_flagged'])
                s.flag_whole_image = qc_info[preprocesed_id]['flag_whole_image']
                s.notes = qc_info[preprocesed_id]['notes']
            else:
                s.qc_flagged = OrderedSet()
                s.flag_whole_image = False
                s.notes = None

            # Load the specimens into VPV
            s.vol_id, s.label_id, = self.load_specimen_into_vpv(s.specimen_root)

    def load_data(self):

        dir_ = QFileDialog.getExistingDirectory(None, "Select root directory containing lama runs",
                                                self.appdata.last_qc_dir)
        self.appdata.last_qc_dir = str(dir_)

        root = Path(dir_)

        self.load_atlas_metadata()

        if self.specimens:  # Any qc in memory?
            doit = question_dialog(self.mainwindow, 'Load QC?', 'This will delete any previously made qc flags')
            if not doit:
                return

        last_qc_dir = self.appdata.last_qc_output_dir

        if not last_qc_dir:
            last_qc_dir = Path()

        suggested_qc_file = Path(last_qc_dir) / f'{root.name}_vpv_qc.yaml'

        res = QFileDialog.getSaveFileName(self.mainwindow, "Select new or existing qc file",
                                                           str(suggested_qc_file), "QC files (*.yaml)")
        self.qc_results_file = Path(res[0])
        self.appdata.last_qc_output_dir = str(self.qc_results_file.parent)

        # create dir for storing screenshota
        self.screenshot_dir = self.qc_results_file.parent / 'screenshots'
        self.screenshot_dir.mkdir(exist_ok=True)

        # Check that we can write to this directory
        if not os.access(self.qc_results_file.parent, os.W_OK):
            error_dialog(self.mainwindow, 'Data not loaded!', 'Directory needs to be writable for qc output')
            return

        self.load_qc(root)
        self.root_dir = root
        # self.load_specimens_into_vpv(root)
        self.update_specimen_list()
        self.load_specimen(0)

    def load_specimen_into_vpv(self, spec_dir: Path, rev=True, title=None):


        invert_yaml = next(spec_dir.glob('**/inverted_transforms/invert.yaml'))
        with open(invert_yaml, 'r') as fh:
            invert_order = yaml.load(fh)['inversion_order']

        # 080121 Both methods of label propagation now use the rigidly-aligned images to overlay label onto
        vol_dir = next(spec_dir.rglob('**/reg*/*rigid*'))

        if not rev:
            try:
                lab_dir = next(spec_dir.rglob('**/inverted_labels/similarity'))
            except StopIteration:
                lab_dir = next(spec_dir.rglob('**/inverted_labels/affine'))
        else:
            # Labels progated by reverse registration
            last_dir = invert_order[-1]
            lab_dir = next(spec_dir.rglob(f'**/inverted_labels/{last_dir}'))

        vol = get_file_paths(vol_dir, ignore_folders=SUBFOLDERS_TO_IGNORE)[0]
        lab = get_file_paths(lab_dir, ignore_folders=SUBFOLDERS_TO_IGNORE)[0]

        vpv_ids = self.vpv.load_volumes([vol, lab], 'vol')

        return vpv_ids








