import pathlib
import pkg_resources
import time

from PyQt5 import uic, QtCore, QtWidgets

import dclab

from ..widgets import show_wait_cursor

from ...util import get_valid_filename
from ..._version import version


class ExportData(QtWidgets.QDialog):
    def __init__(self, parent, pipeline, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, parent, *args, **kwargs)
        path_ui = pkg_resources.resource_filename(
            "shapeout2.gui.export", "e2data.ui")
        uic.loadUi(path_ui, self)
        # Get output path
        self.on_browse()
        # set pipeline
        self.pipeline = pipeline
        # update list widget
        self.on_radio()
        # Signals
        self.pushButton_path.clicked.connect(self.on_browse)
        self.toolButton_all.clicked.connect(self.on_select_all)
        self.toolButton_none.clicked.connect(self.on_select_none)
        self.radioButton_fcs.clicked.connect(self.on_radio)
        self.radioButton_rtdc.clicked.connect(self.on_radio)
        self.radioButton_tsv.clicked.connect(self.on_radio)

    @property
    def file_format(self):
        if self.radioButton_fcs.isChecked():
            return "fcs"
        elif self.radioButton_rtdc.isChecked():
            return "rtdc"
        else:
            return "tsv"

    def done(self, r):
        if r:
            self.export_data()
        super(ExportData, self).done(r)

    @show_wait_cursor
    @QtCore.pyqtSlot()
    def export_data(self):
        """Export data to the desired file format"""
        out = pathlib.Path(self.path)
        # get features
        features = []
        for ii in range(self.listWidget.count()):
            if self.listWidget.item(ii).checkState() == 2:
                features.append(self.features[ii])
        pend = len(self.pipeline.slots)
        prog = QtWidgets.QProgressDialog("Exporting...", "Abort", 1,
                                         pend, self)
        prog.setWindowTitle("Data Export")
        prog.setWindowModality(QtCore.Qt.WindowModal)
        prog.setMinimumDuration(0)
        time.sleep(0.01)
        prog.setValue(0)
        QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 300)
        for slot_index in range(len(self.pipeline.slots)):
            slot = self.pipeline.slots[slot_index]
            if slot.slot_used:  # only export slots "used" (#15)
                ds = self.pipeline.get_dataset(slot_index)
                fn = "SO2-export_{}_{}.{}".format(slot_index,
                                                  slot.name,
                                                  self.file_format)
                # remove bad characters from file name
                fn = get_valid_filename(fn)
                path = out / fn
                # check features
                fmiss = [ff for ff in features if ff not in ds.features]
                if fmiss:
                    lmiss = [dclab.dfn.get_feature_label(ff) for ff in fmiss]
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Features missing!",
                        (f"Dataslot {slot_index} does not have these features:"
                         + "\n"
                         + "".join([f"\n- {fl}" for fl in lmiss])
                         + "\n\n"
                         + f"They are not exported to .{self.file_format}!")
                    )
                if self.file_format == "rtdc":
                    ds.export.hdf5(
                        path=path,
                        features=[ff for ff in features if ff in ds.features],
                        override=True)
                elif self.file_format == "fcs":
                    ds.export.fcs(
                        path=path,
                        features=[ff for ff in features if ff in ds.features],
                        meta_data={"Shape-Out version": version},
                        override=True)
                else:
                    ds.export.tsv(
                        path=path,
                        features=[ff for ff in features if ff in ds.features],
                        meta_data={"Shape-Out version": version},
                        override=True)
            if prog.wasCanceled():
                break
            prog.setValue(slot_index + 1)
            QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents,
                                                 300)
        prog.setValue(pend)

    def on_browse(self):
        out = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                         'Export directory')
        if out:
            self.path = out
            self.lineEdit_path.setText(self.path)
        else:
            self.path = None

    def on_radio(self):
        self.update_feature_list()

    def on_select_all(self):
        for ii in range(self.listWidget.count()):
            wid = self.listWidget.item(ii)
            wid.setCheckState(2)

    def on_select_none(self):
        for ii in range(self.listWidget.count()):
            wid = self.listWidget.item(ii)
            wid.setCheckState(0)

    def update_feature_list(self, scalar=False):
        if self.file_format == "rtdc":
            self.features = self.pipeline.get_features(union=True,
                                                       label_sort=True)
            # do not allow exporting event index, since it will be
            # re-enumerated in any case.
            self.features.remove("index")
        else:
            self.features = self.pipeline.get_features(scalar=True,
                                                       union=True,
                                                       label_sort=True)

        self.listWidget.clear()
        for feat in self.features:
            wid = QtWidgets.QListWidgetItem(dclab.dfn.get_feature_label(feat))
            wid.setCheckState(2)
            self.listWidget.addItem(wid)
