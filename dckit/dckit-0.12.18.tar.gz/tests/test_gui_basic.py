"""basic tests"""
import dclab
import h5py
import numpy as np
from PyQt5.QtWidgets import QFileDialog, QDialog, QMessageBox, QInputDialog

from dckit.main import DCKit


from helper_methods import retrieve_data


def test_simple(qtbot):
    """Open the main window and close it again"""
    main_window = DCKit(check_update=False)
    main_window.close()


def test_list_entries(qtbot):
    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")
    mw.append_paths([path])
    meta = mw.get_metadata(0)
    assert meta["experiment"]["sample"] == "calibration_beads"


def test_task_compress(qtbot, monkeypatch):
    path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")
    path_out = path.with_name("compressed")
    path_out.mkdir()
    # Monkeypatch
    monkeypatch.setattr(QDialog, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(path_out))

    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([path])
    pouts, invalid = mw.on_task_compress()
    assert len(pouts) == 1
    assert len(invalid) == 0
    with dclab.new_dataset(pouts[0]) as ds, dclab.new_dataset(path) as ds0:
        assert len(ds) == len(ds0)
        assert len(ds.logs) != 0
        scf = list(set(ds.features_scalar + ds0.features_scalar))
        for feat in scf:
            assert feat in ds0
            assert feat in ds
            assert np.all(ds[feat] == ds0[feat])


def test_task_compress_and_repack_strip_issue19(qtbot, monkeypatch):
    """Same test as above, only tests whether repack and strip logs works"""
    path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")
    path_out = path.with_name("compressed")
    path_out.mkdir()
    # Monkeypatch
    monkeypatch.setattr(QDialog, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(path_out))

    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([path])
    mw.checkBox_repack.setChecked(True)
    pouts, invalid = mw.on_task_compress()
    assert len(pouts) == 1
    assert len(invalid) == 0
    with dclab.new_dataset(pouts[0]) as ds, dclab.new_dataset(path) as ds0:
        assert len(ds) == len(ds0)
        assert len(ds.logs) == 0
        scf = list(set(ds.features_scalar + ds0.features_scalar))
        for feat in scf:
            assert feat in ds0
            assert feat in ds
            assert np.all(ds[feat] == ds0[feat])


def test_task_join(qtbot, monkeypatch):
    path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")
    path_out = path.with_name("out.rtdc")
    # Monkeypatch
    monkeypatch.setattr(QDialog, "exec_", lambda *args: QDialog.Accepted)
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getSaveFileName",
                        lambda *args: (str(path_out), None))

    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([path, path])
    mw.on_task_join()
    with dclab.new_dataset(path_out) as ds, dclab.new_dataset(path) as ds0:
        assert len(ds) == 2*len(ds0)


def test_task_metadata_sample(qtbot, monkeypatch):
    # Monkeypatch message box to always return OK
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")
    mw.append_paths([path])
    mw.tableWidget.item(0, 3).setText("Peter Pan")
    mw.on_task_metadata()
    with dclab.new_dataset(path) as ds:
        assert ds.config["experiment"]["sample"] == "Peter Pan"


def test_task_split_trace(qtbot, monkeypatch):
    path = retrieve_data("rtdc_data_hdf5_rtfdc.zip")
    path_out = path.parent / "split"
    path_out.mkdir()
    # Monkeypatch
    monkeypatch.setattr(QDialog, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(path_out))
    monkeypatch.setattr(QInputDialog, "getInt",
                        lambda *args: [3, QMessageBox.Ok])
    # Initialize
    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([path])
    paths_split, errors = mw.on_task_split()
    assert not errors
    assert len(paths_split) == 1

    paths_out = sorted(path_out.glob("*.rtdc"))
    assert len(paths_out) == 3

    for pp, size in zip(paths_out, [3, 3, 1]):
        with h5py.File(pp, mode="r") as h5:
            assert len(h5["events"]["trace"]["fl1_raw"]) == size, pp


def test_task_tdms2rtdc(qtbot, monkeypatch):
    path = retrieve_data("rtdc_data_traces_video.zip")
    path_out = path.with_name("converted")
    path_out.mkdir()
    # Monkeypatch message box to always return OK
    monkeypatch.setattr(QMessageBox, "exec_", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory",
                        lambda *args: str(path_out))
    mw = DCKit(check_update=False)
    qtbot.addWidget(mw)
    mw.append_paths([path])
    assert mw.tableWidget.rowCount() == 1
    paths_converted, invalid, errors = mw.on_task_tdms2rtdc()
    assert len(errors) == 0
    assert len(invalid) == 0
    assert len(paths_converted) == 1
    with dclab.new_dataset(paths_converted[0]) as ds:
        assert ds.config["setup"]["module composition"] == "Cell_Flow_2, Fluor"


def test_task_tdms2rtdc_bad_online_contour_no_absdiff(qtbot, monkeypatch):
    """This tests for a regression

    The [online_contour]: "no absdiff" keyword was somehow set to
    "please select" instead of ignoring it if the user did not choose
    anything.

    ValueError: could not convert string to float: 'please select'
    """
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
    assert mw.tableWidget.rowCount() == 1
    paths_converted, invalid, errors = mw.on_task_tdms2rtdc()
    assert len(errors) == 0
    assert len(invalid) == 0
    assert len(paths_converted) == 1
    with dclab.new_dataset(paths_converted[0]) as ds:
        assert ds.config["setup"]["module composition"] == "Cell_Flow_2, Fluor"
