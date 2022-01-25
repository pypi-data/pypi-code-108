import pathlib

import dclab
import h5py
import pytest
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from dckit.main import DCKit
from dckit.dlg_icheck import IntegrityCheckDialog
from dckit.meta_tool import MetadataEditedWarning

from helper_methods import retrieve_data


def test_integrity_shapein_issue3(qtbot, monkeypatch):
    """Shape-In did not store the medium correctly

    https://github.com/ZELLMECHANIK-DRESDEN/ShapeIn_Issues/issues/3

    We don't do anything in this test. We just make sure that
    CellCarrierB is set automatically.
    """
    h5path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")
    with h5py.File(h5path, "a") as h5:
        h5.attrs["setup:software version"] = "2.2.2.0"
        h5.attrs["setup:medium"] = "CellCarrierB"
    h5path_m = h5path.with_name("M001_data.rtdc")
    h5path.rename(h5path_m)
    # Create SoftwareSettings.ini
    sinipath = h5path_m.with_name("M001_SoftwareSettings.ini")
    sinipath.write_text("Buffer_Medium_ID=0\nBuffer_Medium=CellCarrierB")
    # Proceed with loading
    path_out = pathlib.Path(h5path_m).parent
    # Monkeypatch message box to always return OK
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(path_out))
    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([h5path_m])
    assert mw.tableWidget.rowCount() == 1, "sanity check"
    # Now edit the medium (create dialog manually)
    with pytest.warns(MetadataEditedWarning):
        dlg = IntegrityCheckDialog(mw, h5path_m)
    assert dlg.get_metadata_value("setup", "medium") == "CellCarrier"
    assert "setup" in dlg.user_widgets, "setup section must be there"
    assert "medium" in dlg.user_widgets["setup"], "medium must be there"
    # finish the dialog
    dlg.done(True)

    # 1. Get metadata from dict (just to be sure)
    dlg2 = IntegrityCheckDialog(mw, h5path_m)
    assert dlg2.get_metadata_value("setup", "medium") == "CellCarrier"

    # 2. Make sure the combobox is set correctly (just to be sure)
    wid2 = dlg2.user_widgets["setup"]["medium"]
    assert wid2.currentText() == "CellCarrier"

    # 3. Compress and check (just to be sure)
    paths_compressed, invalid = mw.on_task_compress()
    assert len(invalid) == 0
    assert len(paths_compressed) == 1
    with dclab.new_dataset(paths_compressed[0]) as ds:
        assert ds.config["setup"]["medium"] == "CellCarrier"


def test_integrity_shapein_issue3_control(qtbot, monkeypatch):
    """Shape-In did not store the medium correctly

    https://github.com/ZELLMECHANIK-DRESDEN/ShapeIn_Issues/issues/3

    With a functional Shape-In version, DCKit should not attempt anything.
    """
    h5path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")
    with h5py.File(h5path, "a") as h5:
        h5.attrs["setup:software version"] = "2.2.3.0"  # [sic]
        h5.attrs["setup:medium"] = "CellCarrierB"
    h5path_m = h5path.with_name("M001_data.rtdc")
    # Create SoftwareSettings.ini (should not have any effect, because
    # the Shape-In version is expected to be safe.
    sinipath = h5path_m.with_name("M001_SoftwareSettings.ini")
    sinipath.write_text("Buffer_Medium_ID=0\nBuffer_Medium=CellCarrierB")
    h5path.rename(h5path_m)
    # Proceed with loading
    path_out = pathlib.Path(h5path_m).parent
    # Monkeypatch message box to always return OK
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(path_out))
    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([h5path_m])
    assert mw.tableWidget.rowCount() == 1, "sanity check"
    # Now edit the medium (create dialog manually)
    dlg = IntegrityCheckDialog(mw, h5path_m)
    assert dlg.get_metadata_value("setup", "medium") == "CellCarrierB"
    assert "setup" not in dlg.user_widgets, "setup section must not be there"
    # finish the dialog
    dlg.done(True)

    # 1. Get metadata from dict (just to be sure)
    dlg2 = IntegrityCheckDialog(mw, h5path_m)
    assert dlg2.get_metadata_value("setup", "medium") == "CellCarrierB"

    # 2. Compress and check (just to be sure)
    paths_compressed, invalid = mw.on_task_compress()
    assert len(invalid) == 0
    assert len(paths_compressed) == 1
    with dclab.new_dataset(paths_compressed[0]) as ds:
        assert ds.config["setup"]["medium"] == "CellCarrierB"


def test_integrity_shapein_issue3_control_2(qtbot, monkeypatch):
    """Shape-In did not store the medium correctly

    https://github.com/ZELLMECHANIK-DRESDEN/ShapeIn_Issues/issues/3

    This is a control test without SoftwareSettings.ini
    """
    h5path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")
    with h5py.File(h5path, "a") as h5:
        h5.attrs["setup:software version"] = "2.2.2.0"
        h5.attrs["setup:medium"] = "CellCarrierB"
    h5path_m = h5path.with_name("M001_data.rtdc")
    h5path.rename(h5path_m)
    # Proceed with loading
    path_out = pathlib.Path(h5path_m).parent
    # Monkeypatch message box to always return OK
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(path_out))
    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([h5path_m])
    assert mw.tableWidget.rowCount() == 1, "sanity check"
    # Now edit the medium (create dialog manually)
    dlg = IntegrityCheckDialog(mw, h5path_m)
    assert dlg.get_metadata_value("setup", "medium") == "CellCarrierB"
    assert "setup" in dlg.user_widgets, "setup section must be there"
    # finish the dialog
    dlg.done(True)

    # 1. Get metadata from dict (just to be sure)
    dlg2 = IntegrityCheckDialog(mw, h5path_m)
    assert dlg2.get_metadata_value("setup", "medium") == "CellCarrierB"

    # 2. Compress and check (just to be sure)
    paths_compressed, invalid = mw.on_task_compress()
    assert len(invalid) == 0
    assert len(paths_compressed) == 1
    with dclab.new_dataset(paths_compressed[0]) as ds:
        assert ds.config["setup"]["medium"] == "CellCarrierB"


def test_integrity_with_medium(qtbot, monkeypatch):
    """This tests for a regression

    It must be possible to edit the medium and the medium has to be
    stored in the user-defined metadata.
    """
    path = retrieve_data("rtdc_data_traces_video.zip")
    path_out = pathlib.Path(path).parent
    # Monkeypatch message box to always return OK
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(path_out))
    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([path])
    assert mw.tableWidget.rowCount() == 1, "sanity check"
    # Now edit the medium (create dialog manually)
    dlg = IntegrityCheckDialog(mw, path)
    assert dlg.get_metadata_value("setup", "medium") is None
    assert "setup" in dlg.user_widgets, "setup section must be there"
    assert "medium" in dlg.user_widgets["setup"], "medium must be there"
    # set medium to CellCarrier
    wid = dlg.user_widgets["setup"]["medium"]
    assert wid.currentData() is None
    wid.setCurrentText("CellCarrier")
    # finish the dialog
    dlg.done(True)

    # 1. Get metadata from dict
    dlg2 = IntegrityCheckDialog(mw, path)
    assert dlg2.get_metadata_value("setup", "medium") == "CellCarrier"

    # 2. Make sure the combobox is set correctly
    wid2 = dlg2.user_widgets["setup"]["medium"]
    assert wid2.currentText() == "CellCarrier"

    # 3. Convert and check
    paths_converted, invalid, errors = mw.on_task_tdms2rtdc()
    assert len(errors) == 0
    assert len(invalid) == 0
    assert len(paths_converted) == 1
    with dclab.new_dataset(paths_converted[0]) as ds:
        assert ds.config["setup"]["medium"] == "CellCarrier"


def test_integrity_with_medium_remove(qtbot, monkeypatch):
    """Same test as above but also test removal"""
    path = retrieve_data("rtdc_data_traces_video.zip")
    path_out = pathlib.Path(path).parent
    # Monkeypatch message box to always return OK
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(path_out))
    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([path])
    # set medium to CellCarrier
    dlg = IntegrityCheckDialog(mw, path)
    wid = dlg.user_widgets["setup"]["medium"]
    wid.setCurrentText("CellCarrier")
    dlg.done(True)
    # reset the medium to nothing
    dlg2 = IntegrityCheckDialog(mw, path)
    wid2 = dlg2.user_widgets["setup"]["medium"]
    wid2.setCurrentText("")
    dlg2.done(True)

    # 1. Get metadata from dict
    dlg3 = IntegrityCheckDialog(mw, path)
    wid3 = dlg3.user_widgets["setup"]["medium"]
    assert dlg3.get_metadata_value("setup", "medium") is None

    # 2. Make sure the combobox is set correctly
    assert wid3.currentText() == ""


def test_online_contour_no_absdiff(qtbot, monkeypatch):
    """Test booleanness of the metadata combo box"""
    path = retrieve_data("rtdc_data_traces_video.zip")
    # modify the data to not have the [online_contour]: "no absdiff" keyword
    p_para = path.parent / "M1_para.ini"
    ptext = p_para.read_text().split("\n")
    # remove [online_contour]: "no absdiff"
    for ii in range(len(ptext)):
        if ptext[ii].strip() == "Diff_Method = 1":
            ptext.pop(ii)
            break
    p_para.write_text("\n".join(ptext))
    path_out = path.with_name("converted")
    path_out.mkdir()
    # Monkeypatch message box to always return OK
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(path_out))
    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([path])
    # set value to True
    dlg = IntegrityCheckDialog(mw, path)
    wid = dlg.user_widgets["online_contour"]["no absdiff"]
    assert wid.currentIndex() == 0
    assert wid.currentData() == "no selection"
    idx = wid.findData("true")
    wid.setCurrentIndex(idx)
    assert wid.currentData() == "true"
    dlg.done(True)

    # 1. Get metadata from dict
    dlg2 = IntegrityCheckDialog(mw, path)
    assert dlg2.get_metadata_value("online_contour", "no absdiff")

    # 2. Make sure the combobox is set correctly
    wid2 = dlg2.user_widgets["online_contour"]["no absdiff"]
    assert wid2.currentData()

    # 3. Convert and check
    paths_converted, invalid, errors = mw.on_task_tdms2rtdc()
    assert len(errors) == 0
    assert len(invalid) == 0
    assert len(paths_converted) == 1
    with dclab.new_dataset(paths_converted[0]) as ds:
        assert ds.config["online_contour"]["no absdiff"]


def test_online_contour_no_absdiff_remove(qtbot, monkeypatch):
    """Test booleanness of the metadata combo box"""
    path = retrieve_data("rtdc_data_traces_video.zip")
    # modify the data to not have the [online_contour]: "no absdiff" keyword
    p_para = path.parent / "M1_para.ini"
    ptext = p_para.read_text().split("\n")
    # remove [online_contour]: "no absdiff"
    for ii in range(len(ptext)):
        if ptext[ii].strip() == "Diff_Method = 1":
            ptext.pop(ii)
            break
    p_para.write_text("\n".join(ptext))
    path_out = path.with_name("converted")
    path_out.mkdir()
    # Monkeypatch message box to always return OK
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(path_out))
    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([path])
    # set value
    dlg = IntegrityCheckDialog(mw, path)
    wid = dlg.user_widgets["online_contour"]["no absdiff"]
    idx = wid.findData("true")
    wid.setCurrentIndex(idx)
    dlg.done(True)
    # reset value
    dlg2 = IntegrityCheckDialog(mw, path)
    wid2 = dlg2.user_widgets["online_contour"]["no absdiff"]
    idx = wid2.findData("no selection")
    wid2.setCurrentIndex(idx)
    dlg2.done(True)

    # 1. Get metadata from dict
    dlg3 = IntegrityCheckDialog(mw, path)
    assert dlg3.get_metadata_value("online_contour", "no absdiff") is None

    # 2. Make sure the combobox is set correctly
    wid3 = dlg3.user_widgets["online_contour"]["no absdiff"]
    assert wid3.currentData() == "no selection"
