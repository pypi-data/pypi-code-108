import codecs
import numbers
import pathlib
import pkg_resources
import time

import dclab
from PyQt5 import uic, QtCore, QtWidgets

from ..widgets import show_wait_cursor
from ..._version import version

STAT_METHODS = sorted(dclab.statistics.Statistics.available_methods.keys())
STAT_METHODS.remove("%-gated")  # This does not make sense with Pipeline


class ComputeStatistics(QtWidgets.QDialog):
    def __init__(self, parent, pipeline, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, parent, *args, **kwargs)
        path_ui = pkg_resources.resource_filename(
            "shapeout2.gui.compute", "comp_stats.ui")
        uic.loadUi(path_ui, self)
        # for external statistics
        self.path = None
        # set pipeline
        self.pipeline = pipeline
        # Signals
        self.pushButton_path.clicked.connect(self.on_browse)
        self.comboBox.currentIndexChanged.connect(self.on_combobox)
        # Populate statistics methods
        self.listWidget_stats.clear()
        for meth in STAT_METHODS:
            wid = QtWidgets.QListWidgetItem(meth)
            wid.setCheckState(2)
            self.listWidget_stats.addItem(wid)
        # Populate filter ray comboBox
        self.comboBox_filter_ray.clear()
        self.comboBox_filter_ray.addItem("No filtering", None)
        for ii, slot in enumerate(pipeline.slots):
            if slot.slot_used:
                raytext = "Ray {} ({})".format(ii, slot.name)
                self.comboBox_filter_ray.addItem(raytext, slot.identifier)
        # initialize rest
        if len(self.pipeline.slots) == 0:
            self.comboBox.setCurrentIndex(1)
        else:
            self.comboBox.setCurrentIndex(0)
        self.on_combobox()  # computes self.features

    def done(self, r):
        if r:
            success = self.export_statistics()
        else:
            success = True
        if success:
            super(ComputeStatistics, self).done(r)

    @show_wait_cursor
    @QtCore.pyqtSlot()
    def export_statistics(self):
        """Export statistics to .tsv"""
        # get features
        features = []
        for ii in range(self.listWidget_features.count()):
            if self.listWidget_features.item(ii).checkState() == 2:
                features.append(self.features[ii])
        # get methods
        methods = []
        for ii in range(self.listWidget_stats.count()):
            if self.listWidget_stats.item(ii).checkState() == 2:
                methods.append(STAT_METHODS[ii])

        prog = QtWidgets.QProgressDialog("Computing statistics...", "Abort", 1,
                                         1, self)
        prog.setMinimumDuration(0)
        time.sleep(0.01)
        prog.setValue(0)
        # compute statistics
        values = []
        if self.comboBox.currentIndex() == 0:
            # from pipeline
            prog.setMaximum(len(self.pipeline.slots))
            for slot_index in range(len(self.pipeline.slots)):
                slot = self.pipeline.slots[slot_index]
                if slot.slot_used:  # only export slots "used" (#15)
                    ds = self.pipeline.get_dataset(slot_index)
                    h, v = dclab.statistics.get_statistics(ds,
                                                           methods=methods,
                                                           features=features)
                    h = ["Path", "Slot", "Name"] + h
                    v = ["{}".format(ds.path), slot_index, slot.name] + v
                    values.append(v)
                if prog.wasCanceled():
                    break
                prog.setValue(slot_index + 1)
                QtWidgets.QApplication.processEvents(
                    QtCore.QEventLoop.AllEvents, 300)
        else:
            # from path
            inpath = pathlib.Path(self.path)
            files = sorted(inpath.rglob("*.rtdc"))
            prog.setMaximum(len(files))
            for ii, pp in enumerate(files):
                ds = dclab.new_dataset(pp)
                title = ds.title
                slot_id = self.comboBox_filter_ray.currentData()
                if slot_id is not None:
                    ds = self.pipeline.apply_filter_ray(rtdc_ds=ds,
                                                        slot_id=slot_id)
                    title += " ({})".format(slot_id)
                h, v = dclab.statistics.get_statistics(ds,
                                                       methods=methods,
                                                       features=features)
                h = ["Path", "Name"] + h
                v = ["{}".format(pp), title] + v
                values.append(v)
                prog.setValue(ii + 1)
                QtWidgets.QApplication.processEvents(
                    QtCore.QEventLoop.AllEvents, 300)
        # Output path
        opath, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save statistics', '', 'tab-separated values (*.tsv)')
        if not opath:
            # Abort export
            return False
        elif not opath.endswith(".tsv"):
            opath += ".tsv"
        opath = pathlib.Path(opath)
        # Header
        header = ["Statistics Output",
                  "Shape-Out {}".format(version),
                  "",
                  "\t".join(h),
                  ]
        # Data
        data = []
        for v in values:
            line = []
            for vi in v:
                if (isinstance(vi, numbers.Real)
                        and not isinstance(vi, numbers.Integral)):
                    line.append("{:.5e}".format(vi))
                else:
                    line.append("{}".format(vi))
            data.append("\t".join(line))
        # Write BOM
        with opath.open("wb") as fd:
            fd.write(codecs.BOM_UTF8)
        # Write rest
        with opath.open("a", encoding="utf-8") as fd:
            for line in header:
                fd.write("# " + line + "\r\n")
            for line in data:
                fd.write(line + "\r\n")
        return True  # True means success

    def on_browse(self):
        out = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                         'Export directory')
        if out:
            self.path = out
            self.lineEdit_path.setText(self.path)
            self.comboBox.setCurrentIndex(1)
        else:
            self.path = None
            self.comboBox.setCurrentIndex(0)

    def on_combobox(self):
        if self.comboBox.currentIndex() == 1:
            # Datasets from a folder
            self.widget_other.show()
            if self.path is None:
                self.on_browse()
            if self.path:
                self.update_feature_list(use_pipeline=False)
                # else, on_combobox is triggered again
        else:
            # Datasets from current session
            self.widget_other.hide()
            self.update_feature_list(use_pipeline=True)

    def update_feature_list(self, use_pipeline=True):
        if use_pipeline:
            self.features = self.pipeline.get_features(scalar=True,
                                                       union=True,
                                                       label_sort=True)
        else:
            # We want to compute statistics from a folder
            # TODO:
            # - Add ml_score_??? features

            # label-sorted features
            features = dclab.dfn.scalar_feature_names
            labs = [dclab.dfn.get_feature_label(f) for f in features]
            lf = sorted(zip(labs, features))
            self.features = [it[1] for it in lf]

        self.listWidget_features.clear()
        for feat in self.features:
            wid = QtWidgets.QListWidgetItem(dclab.dfn.get_feature_label(feat))
            wid.setCheckState(0)
            self.listWidget_features.addItem(wid)
