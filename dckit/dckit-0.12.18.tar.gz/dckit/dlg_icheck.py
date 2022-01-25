import copy
import html
import json
import functools
import numbers

import pkg_resources
import warnings

import dclab
from dclab.features.emodulus.viscosity import KNOWN_MEDIA
import numpy as np
from PyQt5 import uic, QtWidgets

from . import meta_tool
from .wait_cursor import show_wait_cursor


class IntegrityCheckDialog(QtWidgets.QDialog):
    #: A dictionary of missing metadata keys
    editable_metadata = {}
    #: Remembers user-defined metadata
    user_metadata = {}
    #: Global metadata defaults - Do not update any dictionary with
    #: this. It may override things! Instead, use the classmethod
    #: `metadata_from_path` or the function `get_metadata_value`.
    default_metadata = {}

    def __init__(self, parent, path, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, parent, *args, **kwargs)
        path_ui = pkg_resources.resource_filename("dckit", "dlg_icheck.ui")
        uic.loadUi(path_ui, self)

        self.path = path
        #: metadata (remember across instances)
        if self.path not in IntegrityCheckDialog.user_metadata:
            IntegrityCheckDialog.user_metadata[self.path] = {}
        self.metadata = IntegrityCheckDialog.user_metadata[self.path]
        #: missing metadata keys
        if self.path not in IntegrityCheckDialog.editable_metadata:
            IntegrityCheckDialog.editable_metadata[self.path] = {}
        self.editables = IntegrityCheckDialog.editable_metadata[self.path]
        #: return state ("unchecked", "passed", "incomplete", "tolerable")
        self.state = "unchecked"
        # check and fill data
        self.populate_ui()
        # signals and slots
        self.toolButton_global.clicked.connect(self.on_global)

    @classmethod
    def metadata_from_path(cls, path):
        """Return the missing metadata for a specific path

        This makes use of user_metadata, editable_metadata, and
        default_metadata.

        default_metadata is only used if the data are not present
        in user_metadata and given in editable_metadata.
        """
        if path not in cls.user_metadata:
            # first create the class to populate ´editable_metadata´
            IntegrityCheckDialog(None, path)
        editables = cls.editable_metadata[path]
        userdata = cls.user_metadata[path]
        defaults = cls.default_metadata
        metadata = {}
        # first fill up the default values (if applicable)
        for sec in editables:
            if sec not in metadata:
                metadata[sec] = {}
            for key in editables[sec]:
                if sec in defaults and key in defaults[sec]:
                    metadata[sec][key] = defaults[sec][key]
        # then fill up the userdata
        for sec in userdata:
            if sec not in metadata:
                metadata[sec] = {}
            for key in userdata[sec]:
                metadata[sec][key] = userdata[sec][key]
        return metadata

    def populate_ui(self):
        """Run check and set missing UI elements"""
        # perform initial check
        cues = self.check(use_metadata=False)
        # Fill in user-changeable things
        miss_count = 0
        wrong_count = 0
        self.user_widgets = {}
        for cue in cues:
            if cue.category in ["metadata missing", "metadata wrong"]:
                # label
                sec = cue.cfg_section
                key = cue.cfg_key
                # standard choices we know of
                if sec == "setup" and key == "medium":
                    cue.cfg_choices = KNOWN_MEDIA + ["other"]
                lab = QtWidgets.QLabel("[{}]: {}".format(sec, key))
                lab.setToolTip(dclab.dfn.get_config_value_descr(sec, key))
                if cue.level == "violation":
                    lab.setStyleSheet('color: #A50000')
                else:
                    lab.setStyleSheet('color: #7A6500')
                if cue.category == "metadata missing":
                    self.gridLayout_missing.addWidget(lab, miss_count, 0)
                else:
                    self.gridLayout_wrong.addWidget(lab, wrong_count, 0)
                # control
                if cue.cfg_choices is None:
                    dt = dclab.dfn.get_config_value_type(cue.cfg_section,
                                                         cue.cfg_key)
                    if dt is str:
                        wid = QtWidgets.QLineEdit(self)
                        wid.setText(self.get_metadata_value(sec, key) or "")
                    elif dt == numbers.Integral:
                        wid = QtWidgets.QSpinBox(self)
                        wid.setMinimum(-1337)
                        wid.setMaximum(999999999)
                        value = self.get_metadata_value(sec, key) or -1337
                        wid.setValue(value)
                    elif dt == numbers.Number:
                        wid = QtWidgets.QDoubleSpinBox(self)
                        wid.setMinimum(-1337)
                        wid.setMaximum(999999999)
                        wid.setDecimals(5)
                        value = self.get_metadata_value(sec, key) or -1337
                        wid.setValue(value)
                    elif dt == (bool, np.bool_):
                        wid = QtWidgets.QComboBox(self)
                        wid.addItem("Please select", "no selection")
                        wid.addItem("True", "true")
                        wid.addItem("False", "false")
                        curdata = str(
                            self.get_metadata_value(sec, key)).lower()
                        idx = wid.findData(curdata)
                        wid.setCurrentIndex(max(0, idx))
                    else:
                        raise ValueError("No action specified '{}'".format(dt))
                else:
                    wid = QtWidgets.QComboBox(self)
                    wid.setEditable(True)  # allow user edits
                    # Set placeholder Text for lineEdit, since its editable.
                    wid.lineEdit().setPlaceholderText("Please select")
                    for item in cue.cfg_choices:
                        # Text comboboxes have no "data", because they
                        # are editable and the UI user cannot set any data.
                        wid.addItem(item)
                    wid.setCurrentText(self.get_metadata_value(sec, key))
                if cue.category == "metadata missing":
                    self.gridLayout_missing.addWidget(wid, miss_count, 1)
                    miss_count += 1
                else:
                    self.gridLayout_wrong.addWidget(wid, wrong_count, 1)
                    wrong_count += 1
                # remember all widgets for saving metadata later
                if sec not in self.user_widgets:
                    self.user_widgets[sec] = {}
                self.user_widgets[sec][key] = wid
                # remember which keys were missing
                if sec not in self.editables:
                    self.editables[sec] = []
                if key not in self.editables[sec]:
                    self.editables[sec].append(key)
        if not miss_count:
            self.groupBox_missing.hide()
        if not wrong_count:
            self.groupBox_wrong.hide()
        # Show complete log
        cues2 = self.check(use_metadata=True, expand_section=False)
        text = ""
        colors = {"info": "k",
                  "alert": "#7A6500",
                  "violation": "#A50000"}
        for cue in cues2:
            text += f"<div style='color:{colors[cue.level]}'>" \
                    + f"{html.escape(cue.msg)}</div>"

        self.textEdit.setText(text)

        # Logs
        logs = meta_tool.get_rtdc_logs(self.path)
        if logs:
            for log in logs:
                self.comboBox_logs.addItem(log, log)
        else:
            self.widget_logs.hide()
        self.comboBox_logs.currentIndexChanged.connect(self.on_logs)
        # save metadata (updates from defaults/global)
        self.save_current_metadata()

    def check(self, use_metadata=True, expand_section=True):
        if use_metadata:
            metadata_dump = json.dumps(self.metadata_from_path(self.path),
                                       sort_keys=True)
        else:
            metadata_dump = json.dumps({})
        cues = check_dataset(self.path, metadata_dump, expand_section)
        return cues

    @show_wait_cursor
    def done(self, r):
        if r:
            # save metadata
            self.save_current_metadata()
        # run check again
        cues = self.check(use_metadata=True, expand_section=False)
        levels = dclab.rtdc_dataset.check.ICue.get_level_summary(cues)
        if levels["violation"]:
            self.state = "failed"
        elif levels["alert"]:
            self.state = "tolerable"
        else:
            self.state = "passed"

        super(IntegrityCheckDialog, self).done(r)

    def get_metadata_value(self, sec, key):
        """Return the metadata value for a specific section and key

        This function gets the metadata from three sources with the
        following priority:

        1. self.metadata (previously saved by the user)
        2. dataset on disk (using meta_tool)
        3. self.default_metadata
        """
        value = None
        # Try user-defined values
        if sec in self.metadata and key in self.metadata[sec]:
            value = self.metadata[sec][key]
        # Try dataset
        if value is None:
            config = meta_tool.get_rtdc_config(self.path)
            if sec in config and key in config[sec]:
                value = config[sec][key]
        # Try default/global metadata
        if (value is None
            and sec in self.default_metadata
                and key in self.default_metadata[sec]):
            value = self.default_metadata[sec][key]
        return value

    def on_global(self):
        """Use the current metadata as default metadata"""
        # We will override self.default_metadata with this
        self.save_current_metadata()
        self.default_metadata.clear()
        self.default_metadata.update(copy.deepcopy(self.metadata))

    def on_logs(self):
        log = self.comboBox_logs.currentData()
        if log is None:
            return
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle("{}: {}".format(self.path.name, log))
        path_ui = pkg_resources.resource_filename("dckit", "dlg_log.ui")
        uic.loadUi(path_ui, dlg)
        dlg.label.setText(log)
        logs = meta_tool.get_rtdc_logs(self.path)
        text = "\n".join(logs[log])
        dlg.plainTextEdit.setPlainText(text)
        dlg.exec_()

    def save_current_metadata(self):
        for sec in self.user_widgets:
            for key in self.user_widgets[sec]:
                wid = self.user_widgets[sec][key]
                if isinstance(wid, QtWidgets.QComboBox):
                    value_a = wid.currentData()
                    if isinstance(value_a, str):
                        # for boolean combobox
                        if value_a == "true":
                            value = True
                        elif value_a == "false":
                            value = False
                        else:
                            # "no selection" / "Please select"
                            value = None
                    else:
                        # Text combobox (e.f. [setup]: medium)
                        assert value_a is None, "sanity check"
                        text_a = wid.currentText()
                        if text_a:
                            value = wid.currentText()
                        else:
                            # no text in combobox means no data
                            value = None
                elif isinstance(wid, (QtWidgets.QSpinBox,
                                      QtWidgets.QDoubleSpinBox)):
                    value = wid.value()
                else:
                    value = wid.text()
                if value is not None and value and value != -1337:
                    if sec not in self.metadata:
                        self.metadata[sec] = {}
                    self.metadata[sec][key] = value
                else:
                    # remove the value from the metadata
                    if sec in self.metadata and key in self.metadata[sec]:
                        self.metadata[sec].pop(key)


@functools.lru_cache(maxsize=1000)
def check_dataset(path, metadata_dump, expand_section):
    """Caching wrapper for integrity checks"""
    metadata = json.loads(metadata_dump)
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        # ignore "ResourceWarning: unclosed file <_io.BufferedReader name=29"
        warnings.simplefilter("ignore", ResourceWarning)

        with dclab.new_dataset(path) as ds:
            ds.config.update(metadata)
            ic = dclab.rtdc_dataset.check.IntegrityChecker(ds)
            cues = ic.check(expand_section=expand_section)

            # Also check for medium "other" and offer to edit it
            for cue in cues:
                if cue.identifier == "Shape-In issue #3":
                    warnings.warn("DCKit attempted to fix '[setup]: medium'! "
                                  "(Shape-In issue #3)",
                                  meta_tool.MetadataEditedWarning)
                if (cue.category in ["metadata missing", "metadata wrong"]
                    and cue.cfg_section == "setup"
                        and cue.cfg_key == "medium"):
                    # The cue already exists.
                    break
            else:
                # The cue does not exist - add it.
                medium = ds.config.get("setup", {}).get("medium", "")
                if medium in ["other", ""]:
                    cues.append(dclab.rtdc_dataset.check.ICue(
                        msg="User might want to edit 'medium'",
                        level="alert",
                        category="metadata missing",
                        cfg_section="setup",
                        cfg_key="medium"))
        for ww in ws:
            cues.append(dclab.rtdc_dataset.check.ICue(
                msg="{}: {}".format(ww.category.__name__, ww.message),
                level="alert",
                category="warning"))
    return cues
