import hashlib
import pathlib
import pkg_resources
import signal
import sys
import traceback
import warnings

import dclab
from dclab.cli import repack
from dclab.cli import common

import h5py
import imageio
import imageio_ffmpeg
import nptdms
import numpy
from PyQt5 import uic, QtCore, QtWidgets

from . import dlg_icheck
from .dlg_icheck import IntegrityCheckDialog
from . import history
from . import message_box
from . import meta_tool
from . import update
from .wait_cursor import show_wait_cursor, ShowWaitCursor
from ._version import version as __version__


class DCKit(QtWidgets.QMainWindow):
    def __init__(self, check_update=True):
        super(DCKit, self).__init__()
        path_ui = pkg_resources.resource_filename("dckit", "main.ui")
        uic.loadUi(path_ui, self)
        self.setWindowTitle("DCKit {}".format(__version__))
        # update check
        self._update_thread = None
        self._update_worker = None
        # Disable native menubar (e.g. on Mac)
        self.menubar.setNativeMenuBar(False)
        # signals
        self.pushButton_integrity.clicked.connect(self.on_task_integrity_all)
        self.pushButton_compress.clicked.connect(self.on_task_compress)
        self.pushButton_metadata.clicked.connect(self.on_task_metadata)
        self.pushButton_split.clicked.connect(self.on_task_split)
        self.pushButton_tdms2rtdc.clicked.connect(self.on_task_tdms2rtdc)
        self.pushButton_join.clicked.connect(self.on_task_join)
        self.tableWidget.itemChanged.connect(self.on_table_text_changed)
        self.checkBox_repack.clicked.connect(self.on_repack)
        # File menu
        self.action_add.triggered.connect(self.on_add_measurements)
        self.action_add_folder.triggered.connect(self.on_add_folder)
        self.action_clear.triggered.connect(self.on_clear_measurements)
        # Help menu
        self.actionSoftware.triggered.connect(self.on_action_software)
        self.actionAbout.triggered.connect(self.on_action_about)
        #: contains all imported paths (index is DCKit-id)
        self.pathlist = []
        # contains all integrity buttons (keys are DCKit-ids)
        self.integrity_buttons = {}
        # if "--version" was specified, print the version and exit
        if "--version" in sys.argv:
            print(__version__)
            QtWidgets.QApplication.processEvents(
                QtCore.QEventLoop.AllEvents, 300)
            sys.exit(0)
        # check update after version printing (QThread: Destroyed error)
        if check_update:
            # Update Check
            self.on_action_check_update(True)
        self.show()
        self.raise_()
        self.activateWindow()
        self.setWindowState(QtCore.Qt.WindowState.WindowActive)

    @show_wait_cursor
    def append_paths(self, pathlist):
        """Append selected paths to table"""
        datas = []
        # get meta data for all paths
        for path in pathlist:
            try:  # avoid any errors
                info = {"DCKit-id": (0, len(self.pathlist)),
                        "integrity": (1, None),
                        "path": (2, path),
                        "sample": (3, meta_tool.get_sample_name(path)),
                        "run index": (4, meta_tool.get_run_index(path)),
                        "event count": (5, meta_tool.get_event_count(path)),
                        "flow rate": (6, meta_tool.get_flow_rate(path)),
                        "chip region": (None, meta_tool.get_chip_region(path)),
                        }
            except BaseException:
                warnings.warn("Could not append dataset {} ".format(path)
                              + "(traceback follows)!\n"
                              + "{}".format(traceback.format_exc()))
                # stop doing anything
                continue
            self.pathlist.append(pathlib.Path(path))
            datas.append(info)
        # populate table widget
        for info in datas:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            for key in info:
                col, val = info[key]
                if col is None:
                    continue
                if key == "integrity":
                    # button
                    btn = QtWidgets.QToolButton(self)
                    btn.setText("run check")
                    self.tableWidget.setCellWidget(row, col, btn)
                    btn.clicked.connect(self.on_integrity_check)
                    self.integrity_buttons[info["DCKit-id"][1]] = btn
                else:
                    # text
                    item = QtWidgets.QTableWidgetItem("{}".format(val))
                    if key == "sample":
                        # allow editing sample name
                        item.setFlags(QtCore.Qt.ItemIsEnabled
                                      | QtCore.Qt.ItemIsEditable)
                    elif key == "path":
                        item.setText(pathlib.Path(val).name)
                        item.setToolTip(str(val))
                        item.setFlags(QtCore.Qt.ItemIsEnabled)
                    elif key == "flow rate":
                        if info["chip region"][1] == "channel":
                            item.setText("{:.5f}".format(val))
                        else:
                            item.setText("reservoir")
                        item.setFlags(QtCore.Qt.ItemIsEnabled)
                    else:
                        item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.tableWidget.setItem(row, col, item)
        if datas:
            # set header widhts
            self.tableWidget.setColumnWidth(info["DCKit-id"][0], 10)
            self.tableWidget.setColumnWidth(info["integrity"][0], 100)
            self.tableWidget.setColumnWidth(info["path"][0], 180)
            self.tableWidget.setColumnWidth(info["run index"][0], 80)
            self.tableWidget.setColumnWidth(info["flow rate"][0], 100)
            self.tableWidget.setColumnWidth(info["event count"][0], 80)
            self.tableWidget.setColumnWidth(info["sample"][0], 300)

    def dragEnterEvent(self, e):
        """Whether files are accepted"""
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """Add dropped files to view"""
        urls = e.mimeData().urls()
        pathlist = []
        for ff in urls:
            pp = pathlib.Path(ff.toLocalFile())
            if pp.is_dir():
                pathlist += meta_tool.find_data(pp)
            elif pp.suffix in [".rtdc", ".tdms"]:
                pathlist.append(pp)
        self.append_paths(pathlist)

    def get_metadata(self, row):
        path = self.get_path(row)
        metadata = IntegrityCheckDialog.metadata_from_path(path)
        # update sample name
        newname = self.tableWidget.item(row, 3).text()
        if "experiment" not in metadata:
            metadata["experiment"] = {}
        metadata["experiment"]["sample"] = newname
        return metadata

    def get_path(self, row):
        """Return dataset path from a given row

        This is necessary, because the user can sort columns
        """
        path_index = int(self.tableWidget.item(row, 0).text())
        path = self.pathlist[path_index]
        return path

    @QtCore.pyqtSlot()
    def on_action_about(self):
        about_text = "DCKit is a tool for managing RT-DC data.\n\n" \
            + "Author: Paul Müller\n" \
            + "Code: https://github.com/ZELLMECHANIK-DRESDEN/DCKit\n"
        QtWidgets.QMessageBox.about(self,
                                    "DCKit {}".format(__version__),
                                    about_text)

    @QtCore.pyqtSlot(bool)
    def on_action_check_update(self, b):
        if b and self._update_thread is None:
            self._update_thread = QtCore.QThread()
            self._update_worker = update.UpdateWorker()
            self._update_worker.moveToThread(self._update_thread)
            self._update_worker.finished.connect(self._update_thread.quit)
            self._update_worker.data_ready.connect(
                self.on_action_check_update_finished)
            self._update_thread.start()

            version = __version__
            ghrepo = "ZELLMECHANIK-DRESDEN/DCKit"

            QtCore.QMetaObject.invokeMethod(self._update_worker,
                                            'processUpdate',
                                            QtCore.Qt.QueuedConnection,
                                            QtCore.Q_ARG(str, version),
                                            QtCore.Q_ARG(str, ghrepo),
                                            )

    @QtCore.pyqtSlot(dict)
    def on_action_check_update_finished(self, mdict):
        # cleanup
        self._update_thread.quit()
        self._update_thread.wait()
        self._update_worker = None
        self._update_thread = None
        # display message box
        ver = mdict["version"]
        web = mdict["releases url"]
        dlb = mdict["binary url"]
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("DCKit {} available!".format(ver))
        msg.setTextFormat(QtCore.Qt.RichText)
        text = "You can install DCKit {} ".format(ver)
        if dlb is not None:
            text += 'from a <a href="{}">direct download</a>. '.format(dlb)
        else:
            text += 'by running `pip install --upgrade dckit`. '
        text += 'Visit the <a href="{}">official release page</a>!'.format(web)
        msg.setText(text)
        msg.exec_()

    @QtCore.pyqtSlot()
    def on_action_software(self):
        libs = [dclab,
                imageio,
                imageio_ffmpeg,
                h5py,
                nptdms,
                numpy,
                ]
        sw_text = "DCKit {}\n\n".format(__version__)
        sw_text += "Python {}\n\n".format(sys.version)
        sw_text += "Modules:\n"
        for lib in libs:
            sw_text += "- {} {}\n".format(lib.__name__, lib.__version__)
        sw_text += "- PyQt5 {}\n".format(QtCore.QT_VERSION_STR)
        if hasattr(sys, 'frozen'):
            sw_text += "\nThis executable has been created using PyInstaller."
        QtWidgets.QMessageBox.information(self,
                                          "Software",
                                          sw_text)

    @QtCore.pyqtSlot()
    def on_add_folder(self):
        """Search folder for RT-DC data and add to table"""
        # show a dialog for selecting folder
        path = QtWidgets.QFileDialog.getExistingDirectory(self)
        if not path:
            return
        # find RT-DC data
        pathlist = meta_tool.find_data(path)
        if not pathlist:
            raise ValueError("No RT-DC data found in {}!".format(path))
        # add to list
        self.append_paths(pathlist)

    @QtCore.pyqtSlot()
    def on_add_measurements(self):
        """Select .tdms and .rtdc files and add to table"""
        # show a dialog for adding multiple single files (.tdms and .rtdc)
        pathlist, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            'Select RT-DC data',
            '',
            'RT-DC data (*.tdms *.rtdc)')
        if pathlist:
            # add to list
            self.append_paths(pathlist)

    @QtCore.pyqtSlot()
    def on_clear_measurements(self):
        """Clear the table"""
        for _ in range(len(self.pathlist)):
            self.tableWidget.removeRow(0)
        self.pathlist.clear()
        self.integrity_buttons.clear()
        # clear lru_cache
        meta_tool.get_rtdc_meta.cache_clear()
        dlg_icheck.check_dataset.cache_clear()

    @QtCore.pyqtSlot()
    def on_repack(self):
        """The checkbox is clicked (no repacking is performed)"""
        if self.checkBox_repack.isChecked():
            # ask the user whether he knows what he is doing
            dlg = QtWidgets.QDialog()
            path_ui = pkg_resources.resource_filename("dckit", "dlg_repack.ui")
            uic.loadUi(path_ui, dlg)
            ret = dlg.exec_()
            if ret == QtWidgets.QDialog.Rejected:
                self.checkBox_repack.setChecked(False)
                self.pushButton_metadata.setEnabled(True)
            else:
                self.pushButton_metadata.setEnabled(False)
        else:
            self.pushButton_metadata.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_integrity_check(self, button=None):
        if button is None:
            button = self.sender()
            skip_ui = False
        else:
            skip_ui = True
        # find DCKit-id
        for did in self.integrity_buttons:
            if button is self.integrity_buttons[did]:
                break
        else:
            raise ValueError("Could not find button {}".format(button))
        # get path
        path = self.pathlist[did]
        with ShowWaitCursor():
            dlg = IntegrityCheckDialog(self, path)
        if skip_ui:
            dlg.done(True)
        else:
            dlg.exec_()
        button.setText(dlg.state)
        colors = {"failed": "#A50000",
                  "tolerable": "#7A6500",
                  "passed": "#007A04"}
        button.setStyleSheet("color: {}".format(colors[dlg.state]))

    @QtCore.pyqtSlot()
    def on_table_text_changed(self):
        """Reset sample name if set to empty string"""
        curit = self.tableWidget.currentItem()
        if curit is not None and curit.text() == "":
            row = self.tableWidget.currentRow()
            path = self.get_path(row)
            sample = meta_tool.get_sample_name(path)
            self.tableWidget.item(row, 3).setText(sample)

    @QtCore.pyqtSlot()
    def on_task_compress(self):
        """Compress .rtdc data losslessly"""
        # Open the target directory
        pout = QtWidgets.QFileDialog.getExistingDirectory(self)
        details = []
        invalid = []
        paths_compressed = []
        if pout:
            with ShowWaitCursor():
                pout = pathlib.Path(pout)
                for row in range(self.tableWidget.rowCount()):
                    path = self.get_path(row)
                    metadata = self.get_metadata(row)
                    name = metadata["experiment"]["sample"]
                    prtdc = pout / get_rtdc_output_name(origin_path=path,
                                                        sample_name=name)
                    if path.suffix == ".rtdc":
                        task_dict = {
                            "name": "compress HDF5 data",
                        }
                        dclab.cli.compress(path_in=path, path_out=prtdc)
                        append_execution_log(prtdc, task_dict)
                        task_dict_meta = self.write_metadata(prtdc, metadata)
                        if task_dict_meta:
                            append_execution_log(prtdc, task_dict_meta)
                        # write any warnings to separate log files
                        extract_warning_logs(prtdc)
                        # update list for UI
                        details.append("{} -> {}".format(path, prtdc))
                        paths_compressed.append(prtdc)
                        # repack if checked
                        # (we still did the compression in case dclab needed
                        # to fix things)
                        self.repack(prtdc)
                    else:
                        # do not do anything with .rtdc files
                        invalid.append(path)
        else:
            return

        if invalid:
            message_box.ignored(
                message=f"{len(invalid)} files were ignored (no .rtdc data).",
                details="Affected files are:\n"
                        + "\n\n".join([str(p) for p in invalid]))

        # finally, show the feedback dialog
        if len(details):
            message_box.success(
                message=f"Successfully compressed {len(details)} .rtdc files!",
                details="\n\n".join(details))
        elif not invalid:
            message_box.nothing_todo()
        return paths_compressed, invalid

    @show_wait_cursor
    @QtCore.pyqtSlot()
    def on_task_integrity_all(self):
        for did in self.integrity_buttons:
            btn = self.integrity_buttons[did]
            self.on_integrity_check(button=btn)

    @QtCore.pyqtSlot()
    def on_task_join(self):
        """Join multiple RT-DC measurements"""
        # show a dialog with sample name
        dlg = QtWidgets.QDialog()
        path_ui = pkg_resources.resource_filename("dckit", "dlg_join.ui")
        uic.loadUi(path_ui, dlg)
        dlg.lineEdit.setText(self.get_metadata(0)["experiment"]["sample"])
        ret = dlg.exec_()
        if ret == QtWidgets.QDialog.Accepted:
            sample = dlg.lineEdit.text()
            metadata = {"experiment": {"run index": 1,
                                       "sample": sample}}
            po, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Output path', '', 'RT-DC files (*.rtdc)')
            if po:
                po = pathlib.Path(po)
                if not po.suffix == ".rtdc":
                    po = po.parent / (po.name + ".rtdc")
                pi = []
                for row in range(self.tableWidget.rowCount()):
                    pi.append(self.get_path(row))
                # finally, show the feedback dialog
                msg = QtWidgets.QMessageBox()
                if pi:
                    with ShowWaitCursor():
                        dclab.cli.join(path_out=po,
                                       paths_in=pi,
                                       metadata=metadata)
                    # write any warnings to separate log files
                    extract_warning_logs(po)
                    # repack if checked
                    self.repack(po)
                    # display message
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setText(f"Successfully joined {len(pi)} datasets!")
                    msg.setWindowTitle("Success")
                    msg.setDetailedText("\n".join([str(pp) for pp in pi]))
                else:
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    msg.setText("Nothing to do!")
                    msg.setWindowTitle("Warning")
                msg.exec_()

    @QtCore.pyqtSlot()
    def on_task_metadata(self):
        """Update the metadata including the sample names of the datasets"""
        invalid = []
        details = []
        with ShowWaitCursor():
            for row in range(self.tableWidget.rowCount()):
                path = self.get_path(row)
                # check whether we are allowed to do this
                if path.suffix == ".tdms":
                    # not supported for tdms files
                    invalid.append(path)
                else:
                    metadata = self.get_metadata(row)
                    task_dict_meta = self.write_metadata(path, metadata)
                    if task_dict_meta:
                        append_execution_log(path, task_dict_meta)
                        # update list for UI
                        details.append("{}: update metadata".format(path))
                        # remove item from check cache
                        if path in IntegrityCheckDialog.user_metadata:
                            IntegrityCheckDialog.user_metadata.pop(path)
                    dlg_icheck.check_dataset.cache_clear()
        if invalid:
            # show message regarding .tdms data
            message_box.ignored(
                message=f"{len(invalid)} files were ignored (no .rtdc data).",
                info="Changing the metadata for .tdms files is "
                     + "not supported! Please convert the files to "
                     + "the .rtdc file format.",
                details="Affected files are:\n"
                        + "\n\n".join([str(p) for p in invalid]))

        # finally, show the feedback dialog
        if len(details):
            message_box.success(
                message=f"Updated the metadata of {len(details)} files!",
                details="\n\n".join(details))
        elif not invalid:
            message_box.nothing_todo(
                message="Nothing to update! You did not edit any metadata in "
                        + "the 'Sample' column or via the integrity check or "
                        + "you are attempting to update .tdms data (which "
                        + "is not supported - use 'Convert .tdms to .rtdc' "
                        + "instead).")

    @QtCore.pyqtSlot()
    def on_task_split(self):
        split_events, okPressed = QtWidgets.QInputDialog.getInt(
            self, "Events per output file", "Limit events to:",
            10000, 0, 1000000, 5000)
        details = []
        errors = []
        paths_split = []

        if okPressed:
            pout = QtWidgets.QFileDialog.getExistingDirectory(self)
            if pout:
                with ShowWaitCursor():
                    pout = pathlib.Path(pout)
                    task_dict = {
                        "name": "split every {} events".format(split_events),
                    }
                    for row in range(self.tableWidget.rowCount()):
                        path = self.get_path(row)
                        try:
                            psplit = dclab.cli.split(
                                path_in=path,
                                path_out=pout,
                                split_events=split_events,
                                skip_initial_empty_image=True,
                                skip_final_empty_image=True,
                                ret_out_paths=True,
                                verbose=False)
                        except BaseException:
                            errors.append([path, traceback.format_exc()])
                            # remove erroneous files
                            for pp in pout.glob(path.stem+"_*"):
                                pp.unlink()
                        else:
                            for pp in psplit:
                                append_execution_log(pp, task_dict)
                                # write any warnings to separate log files
                                extract_warning_logs(pp)
                                # update list for UI
                                details.append("created {}".format(pp))
                                # repack if checked
                                self.repack(pp)
                            paths_split.append(path)
        if errors:
            # Show an error dialog for the files that could not be converted
            message_box.error(
                message="Errors encountered while splitting!",
                details="Affected files are:\n\n"
                        + "\n\n".join(["{}:\n{}".format(*e) for e in errors]))

        # finally, show the feedback dialog
        if len(details):
            message_box.success(
                message=f"Splitting into {len(details)} files completed.",
                details="\n\n".join(details))
        elif not errors:
            message_box.nothing_todo()
        return paths_split, errors

    @QtCore.pyqtSlot()
    def on_task_tdms2rtdc(self):
        """Convert .tdms files to .rtdc files"""
        pout = QtWidgets.QFileDialog.getExistingDirectory(self)
        details = []
        errors = []
        invalid = []
        paths_converted = []
        if pout:
            pout = pathlib.Path(pout)
            with ShowWaitCursor():
                for row in range(self.tableWidget.rowCount()):
                    path = self.get_path(row)
                    metadata = self.get_metadata(row)
                    name = metadata["experiment"]["sample"]
                    prtdc = pout / get_rtdc_output_name(origin_path=path,
                                                        sample_name=name)
                    if path.suffix == ".tdms":
                        task_dict = {
                            "name": "convert .tdms to .rtdc",
                        }
                        try:
                            dclab.cli.tdms2rtdc(path_tdms=path,
                                                path_rtdc=prtdc,
                                                compute_features=False,
                                                skip_initial_empty_image=True,
                                                skip_final_empty_image=True,
                                                verbose=False)
                        except BaseException:
                            errors.append([path, traceback.format_exc()])
                            if prtdc.exists():
                                prtdc.unlink()
                        else:
                            append_execution_log(prtdc, task_dict)
                            task_dict_meta = self.write_metadata(prtdc,
                                                                 metadata)
                            if task_dict_meta:
                                append_execution_log(prtdc, task_dict_meta)
                            # write any warnings to separate log files
                            extract_warning_logs(prtdc)
                            # update list for UI
                            details.append("{} -> {}".format(path, prtdc))
                            paths_converted.append(prtdc)
                            # repack if checked
                            self.repack(prtdc)
                    else:
                        # do not do anything with .rtdc files
                        invalid.append(path)
        if invalid:
            # Show an error dialog for the tdms files
            message_box.ignored(
                message="Only .tdms files supported as input, got "
                        + f"{len(invalid)} other files!",
                details="Affected files are:\n\n"
                        + "\n\n".join([str(p) for p in invalid]))

        if errors:
            message_box.error(
                message=f"{len(errors)} files could not be converted!",
                details="Affected files are:\n\n"
                        + "\n\n".join(["{}:\n{}".format(*e) for e in errors]))

        # finally, show the feedback dialog
        if len(details):
            message_box.success(
                message=f"Converted {len(details)} files to .rtdc.",
                details="\n\n".join(details))
        elif not (errors or invalid):
            message_box.nothing_todo()
        return paths_converted, invalid, errors

    @show_wait_cursor
    def repack(self, path):
        """repack and strip logs if the checkbox is checked"""
        if not self.checkBox_repack.isChecked():
            return

        path = pathlib.Path(path)
        # rename the original file
        path_orig = path.with_name(path.stem + "_original.rtdc")
        path.rename(path_orig)
        try:
            repack(path_in=path_orig, path_out=path, strip_logs=True)
        except BaseException:
            path_orig.unlink()
            if path.exists():
                path.unlink()
            raise
        else:
            path_orig.unlink()

    @show_wait_cursor
    def write_metadata(self, path, metadata):
        """Write metadata to an HDF5 file

        Returns
        -------
        `task_dict` if anything changed or None
        """
        # entry for the log
        task_dict = {
            "name": "update metadata",
            "old": {},
            "new": {},
        }
        # update in-place
        with h5py.File(path, "a") as h5:
            for sec in metadata:
                for key in metadata[sec]:
                    h5key = "{}:{}".format(sec, key)
                    value = metadata[sec][key]
                    value_old = h5.attrs.get(h5key, None)
                    if isinstance(value_old, bytes):
                        value_old = value_old.decode("utf-8")
                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    if value != value_old:
                        task_dict["new"][h5key] = value
                        task_dict["old"][h5key] = value_old
                        if isinstance(value, str):  # (after task_dict)
                            value = numpy.string_(value.encode("utf-8"))
                        h5.attrs[h5key] = value
        if task_dict["new"]:
            return task_dict
        else:
            return None


def append_execution_log(path, task_dict):
    info = common.get_job_info()
    info["libraries"]["dckit"] = __version__
    info["task"] = task_dict
    history.append_history(path, info)


def excepthook(etype, value, trace):
    """
    Handler for all unhandled exceptions.

    :param `etype`: the exception type (`SyntaxError`,
        `ZeroDivisionError`, etc...);
    :type `etype`: `Exception`
    :param string `value`: the exception error message;
    :param string `trace`: the traceback header, if any (otherwise, it
        prints the standard Python header: ``Traceback (most recent
        call last)``.
    """
    vinfo = "Unhandled exception in DCKit version {}:\n".format(
        __version__)
    tmp = traceback.format_exception(etype, value, trace)
    exception = "".join([vinfo]+tmp)

    errorbox = QtWidgets.QMessageBox()
    errorbox.addButton(QtWidgets.QPushButton('Close'),
                       QtWidgets.QMessageBox.YesRole)
    errorbox.addButton(QtWidgets.QPushButton(
        'Copy text && Close'), QtWidgets.QMessageBox.NoRole)
    errorbox.setText(exception)
    ret = errorbox.exec_()
    if ret == 1:
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(exception)


def extract_warning_logs(path):
    path = pathlib.Path(path)
    logs = meta_tool.get_rtdc_logs(path)
    for lname in logs:
        if lname.count("warnings"):
            plog = path.with_name(path.stem + "_" + lname + ".log")
            plog.write_text("\r\n".join(logs[lname]))


def get_rtdc_output_name(origin_path, sample_name):

    if meta_tool.get_chip_region(origin_path) == "channel":
        fl_or_res = "{:.4f}uls".format(meta_tool.get_flow_rate(origin_path))
    else:
        fl_or_res = "reservoir"

    name = "{}_M{}_{}_{}_{}.rtdc".format(
        meta_tool.get_date(origin_path),
        meta_tool.get_run_index(origin_path),
        fl_or_res,
        sample_name,
        sha256(origin_path)[:8])
    return get_valid_filename(name)


def get_valid_filename(value):
    """
    Return the given string converted to a string that can be used
    for a clean filename.
    """
    ret = ""

    valid = "abcdefghijklmnopqrstuvwxyz" \
            + "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
            + "0123456789" \
            + "._-()"
    replace = {
        " ": "_",
        "[": "(",
        "]": ")",
        "µ": "u",
    }

    for ch in value:
        if ch in valid:
            ret += ch
        elif ch in replace:
            ret += replace[ch]
        else:
            ret += "?"

    ret = ret.strip(".")
    return ret


def sha256(path):
    return dclab.util.hashfile(path, constructor=hashlib.sha256)


# Make Ctr+C close the app
signal.signal(signal.SIGINT, signal.SIG_DFL)
# Display exception hook in separate dialog instead of crashing
sys.excepthook = excepthook
