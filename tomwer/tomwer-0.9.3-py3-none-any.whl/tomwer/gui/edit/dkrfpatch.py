# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "30/10/2020"


import h5py
from silx.gui import qt
from silx.io.utils import h5py_read_dataset
from tomoscan.esrf.hdf5scan import ImageKey
from silx.io.url import DataUrl
from tomoscan.io import HDF5File
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from silx.gui.dialog.DataFileDialog import DataFileDialog
from tomwer.io.utils import get_default_directory
import tomwer.core.utils.nxtomoutils as nxtomo_utils

from typing import Union
import logging

_logger = logging.getLogger(__name__)


class _DarkOrFlatUrl(qt.QWidget):

    editingFinished = qt.Signal()
    """Signal emit when the url changes"""

    def __init__(self, parent, type_: ImageKey, when: str):
        assert when in ("start", "end")
        qt.QWidget.__init__(self, parent)
        self._type = type_
        self._when = when
        self.setLayout(qt.QHBoxLayout())

        self._qle = qt.QLineEdit("", self)
        self.layout().addWidget(self._qle)

        self._optionsCB = qt.QComboBox(self)
        self._optionsCB.addItem("full dataset")
        self.layout().addWidget(self._optionsCB)

        # connect signal / slot
        self._qle.editingFinished.connect(self._tryUpdateOptions)
        self._qle.editingFinished.connect(self._editingFinished)
        self._optionsCB.currentIndexChanged.connect(self._editingFinished)

    def _editingFinished(self):
        self.editingFinished.emit()

    def setUrl(self, url):
        """
        Define the url where the dataset can be picked
        If this is a dataset from an NXEntry containing dark / flat then we
        will propose to pick only a part of the dataset (only start / end of
         dark / flat)

        :param url:
        :return:
        """
        url = self._redirectDataPath(url, logger=_logger)

        def dataset_invalid(url):
            with HDF5File(url.file_path(), mode="r") as h5s:
                if not isinstance(h5s[url.data_path()], h5py.Dataset):
                    return True
            return False

        if url.data_path() in (None, "") or dataset_invalid(url):
            msg = qt.QMessageBox(self)
            msg.setIcon(qt.QMessageBox.Warning)
            text = "You should provide a path to a dataset or to a NXtomo entry"
            msg.setText(text)
            msg.exec_()
            return
        old = self.blockSignals(True)
        self._qle.setText(url.path())
        self._updateOptions(url)
        self.blockSignals(old)
        self._editingFinished()

    def setSerie(self, serie):
        type_name = self._type.name.lower().replace("_", " ")
        item_txt = "{} serie n°{}".format(type_name, serie)
        idx = self._optionsCB.findText(item_txt)
        if idx >= 0:
            self._optionsCB.setCurrentIndex(idx)

    def getSerieIndex(self):
        return self._optionsCB.currentIndex()

    def _redirectDataPath(self, url, logger=None):
        try:
            with HDF5File(url.file_path(), mode="r") as h5s:
                node = h5s[url.data_path()]

                if HDF5TomoScan.entry_is_nx_tomo(node):
                    if (
                        "detector" in node["instrument"]
                        and "data" in node["instrument"]["detector"]
                    ):
                        if logger:
                            _logger.info(
                                "NXTomo entry found. Set the directly the"
                                "detector data"
                            )
                        data_path = "/".join(
                            (url.data_path(), "instrument", "detector", "data")
                        )
                        url = DataUrl(file_path=url.file_path(), data_path=data_path)
                elif HDF5TomoScan.is_nxdetector(node):
                    if "data" in node:
                        if logger:
                            _logger.info(
                                "NX_detector entry found. Set the directly"
                                " the detector data"
                            )
                        data_path = "/".join((url.data_path, "data"))
                        url = DataUrl(file_path=url.file_path(), data_path=data_path)
        except Exception:
            pass
        return url

    def _tryUpdateOptions(self):
        try:
            url = DataUrl(path=self._qle.text())
            self._updateOptions(url)
        except Exception:
            pass

    def _updateOptions(self, url: DataUrl):
        self._optionsCB.clear()
        if url is None:
            return
        assert isinstance(url, DataUrl)
        assert h5py.is_hdf5(url.file_path()), "only manage hdf5 file"
        self._optionsCB.addItem("full dataset")
        if url.data_path() == "":
            _logger.error("data path should be specify")
            return
        # if we are on a 'detector / data dataset' then we can try to reach
        # image_key information
        image_keys = self._getImageKey(url)
        if image_keys is not None:
            n_serie = nxtomo_utils.get_n_series(
                image_key_values=image_keys, image_key_type=self._type
            )
            if n_serie is not None:
                type_name = self._type.name.lower().replace("_", " ")
                series_indexes = list(range(n_serie))
                for i_serie in series_indexes:
                    self._optionsCB.addItem("{} serie n°{}".format(type_name, i_serie))
                # if this is a end url then set to the last found entry
                if self._when == "end":
                    opt_idx = self._optionsCB.findText(
                        "{} serie n°{}".format(type_name, series_indexes[-1])
                    )
                else:
                    # else set it to the first entry
                    opt_idx = self._optionsCB.findText(
                        "{} serie n°{}".format(type_name, series_indexes[0])
                    )
                if opt_idx >= 0:
                    self._optionsCB.setCurrentIndex(opt_idx)

    def _getImageKey(self, url):
        # if we are on a 'detector / data dataset' then we can try to reach
        # image_key information
        with HDF5File(url.file_path(), mode="r") as h5s:
            dataset = h5s[url.data_path()]
            grp_parent = dataset.parent
            if grp_parent is not None and HDF5TomoScan.is_nxdetector(grp_parent):
                if "image_key" in grp_parent:
                    return h5py_read_dataset(grp_parent["image_key"])
        return None

    def _getSlices(self, image_key_values, serie_index):
        n_serie = -1
        start = None
        is_in_a_serie = False
        for i_frame, frame in enumerate(image_key_values):
            if frame == self._type.value and not is_in_a_serie:
                n_serie += 1
                is_in_a_serie = True
                if n_serie == serie_index:
                    start = i_frame
            elif frame != self._type.value and is_in_a_serie:
                is_in_a_serie = False
                if n_serie == serie_index:
                    return slice(start, i_frame)
        if start is not None:
            return slice(start, len(image_key_values))
        return None

    def getUrl(self):
        try:
            url_no_slices = DataUrl(path=self._qle.text())
            serie_index = self._optionsCB.currentText()
            if serie_index in ("", None):
                return None
            if serie_index == "full dataset":
                slices = None
            else:
                serie_index = int(serie_index.split("n°")[1])
                slices = self._getSlices(
                    image_key_values=self._getImageKey(url_no_slices),
                    serie_index=serie_index,
                )
            data_path = url_no_slices.data_path()
            url_slices = slices
            if url_slices is not None:
                url_slices = list(range(slices.start, slices.stop))
            url = DataUrl(
                file_path=url_no_slices.file_path(),
                data_path=data_path,
                data_slice=url_slices,
                scheme="silx",
            )
        except Exception as e:
            _logger.warning("Fail to create url. Reason is", str(e))
            return None
        else:
            return url


class DarkRefPatchWidget(qt.QWidget):
    """
    Widget to add dark and flat
    """

    sigConfigurationChanged = qt.Signal()
    """Signal emit when the configuration changed (url update)"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())

        # start dark
        self._sdCB = qt.QCheckBox("start dark", self)
        self.layout().addWidget(self._sdCB, 0, 0, 1, 1)
        self._sdQLE = _DarkOrFlatUrl(self, ImageKey.DARK_FIELD, when="start")
        self.layout().addWidget(self._sdQLE, 0, 2, 1, 1)
        self._selectSD = qt.QPushButton("select", self)
        self.layout().addWidget(self._selectSD, 0, 3, 1, 1)

        # start flat
        self._sfCB = qt.QCheckBox("start flat", self)
        self.layout().addWidget(self._sfCB, 1, 0, 1, 1)
        self._sfQLE = _DarkOrFlatUrl(self, ImageKey.FLAT_FIELD, when="start")
        self.layout().addWidget(self._sfQLE, 1, 2, 1, 1)
        self._selectSF = qt.QPushButton("select", self)
        self.layout().addWidget(self._selectSF, 1, 3, 1, 1)

        # end dark
        self._edCB = qt.QCheckBox("end dark ", self)
        self.layout().addWidget(self._edCB, 2, 0, 1, 1)
        self._edQLE = _DarkOrFlatUrl(self, ImageKey.DARK_FIELD, when="end")
        self.layout().addWidget(self._edQLE, 2, 2, 1, 1)
        self._selectED = qt.QPushButton("select", self)
        self.layout().addWidget(self._selectED, 2, 3, 1, 1)

        # end flat
        self._efCB = qt.QCheckBox("end flat", self)
        self.layout().addWidget(self._efCB, 3, 0, 1, 1)
        self._efQLE = _DarkOrFlatUrl(self, ImageKey.FLAT_FIELD, when="end")
        self.layout().addWidget(self._efQLE, 3, 2, 1, 1)
        self._selectEF = qt.QPushButton("select", self)
        self.layout().addWidget(self._selectEF, 3, 3, 1, 1)

        # signal / slot connection
        # connect select button
        self._selectSD.released.connect(self._selectSDDataset)
        self._selectSF.released.connect(self._selectSFDataset)
        self._selectED.released.connect(self._selectEDDataset)
        self._selectEF.released.connect(self._selectEFDataset)

        # set up
        for widget_ in (
            self._sdQLE,
            self._selectSD,
            self._edQLE,
            self._selectED,
            self._sfQLE,
            self._selectSF,
            self._efQLE,
            self._selectEF,
        ):
            widget_.setEnabled(False)

        # connect checkbox buttons
        self._sdCB.toggled.connect(self._toggleSD)
        self._sfCB.toggled.connect(self._toggleSF)
        self._edCB.toggled.connect(self._toggleED)
        self._efCB.toggled.connect(self._toggleEF)

        # connect QLE modifications
        self._sdQLE.editingFinished.connect(self._configurationChanged)
        self._sdCB.toggled.connect(self._configurationChanged)
        self._sfQLE.editingFinished.connect(self._configurationChanged)
        self._sfCB.toggled.connect(self._configurationChanged)
        self._efQLE.editingFinished.connect(self._configurationChanged)
        self._efCB.toggled.connect(self._configurationChanged)
        self._edQLE.editingFinished.connect(self._configurationChanged)
        self._edCB.toggled.connect(self._configurationChanged)

    def _configurationChanged(self):
        self.sigConfigurationChanged.emit()

    def _selectSDDataset(self):
        self._selectDataset("start dark", self._sdQLE)

    def _selectSFDataset(self):
        self._selectDataset("start flat", self._sfQLE)

    def _selectEDDataset(self):
        self._selectDataset("end dark", self._edQLE)

    def _selectEFDataset(self):
        self._selectDataset("end flat", self._efQLE)

    def _updateEnable(self, toggled, widgets):
        for w in widgets:
            w.setEnabled(toggled)

    def _toggleSD(self, toggled):
        self._updateEnable(toggled=toggled, widgets=(self._sdQLE, self._selectSD))

    def _toggleSF(self, toggled):
        self._updateEnable(toggled=toggled, widgets=(self._sfQLE, self._selectSF))

    def _toggleED(self, toggled):
        self._updateEnable(toggled=toggled, widgets=(self._edQLE, self._selectED))

    def _toggleEF(self, toggled):
        self._updateEnable(toggled=toggled, widgets=(self._efQLE, self._selectEF))

    def _selectDataset(self, what, outputQLE):
        # we can select a dataset or an entry. If this is an entry then we
        # will copy the target dark / flat...
        # ou ajouter un from: to
        assert isinstance(outputQLE, _DarkOrFlatUrl)
        dialog = DataFileDialog()
        dialog.setWindowTitle(what)
        dialog.setDirectory(get_default_directory())

        if dialog.exec_() and dialog.selectedDataUrl() is not None:
            old = outputQLE.blockSignals(True)
            url = dialog.selectedDataUrl()
            try:
                outputQLE.setUrl(url)
            except Exception as e:
                _logger.error(e)
            outputQLE.blockSignals(old)
            outputQLE.editingFinished.emit()

    def getStartDarkUrl(self) -> Union[None, DataUrl]:
        """

        :return: url defined by the user for patching the start darks
        :rtype:  Union[None, DataUrl]
        """
        if self._sdCB.isChecked():
            return self._sdQLE.getUrl()
        else:
            return None

    def getStartDarkIndex(self):
        return self._sdQLE.getSerieIndex()

    def setStartDarkUrl(self, url, serie_index=None) -> None:
        """

        :param DataUrl url:
        :param Union[int,None] serie_index: index of the serie to set
        """
        self._sdCB.setChecked(True)
        self._sdQLE.setUrl(url)
        if serie_index is not None:
            self._sdQLE.setSerie(serie_index)

    def getStartFlatUrl(self) -> Union[None, DataUrl]:
        """

        :return: url defined by the user for patching the start flats
        :rtype:  Union[None, DataUrl]
        """
        if self._sfCB.isChecked():
            return self._sfQLE.getUrl()
        else:
            return None

    def getStartFlatIndex(self):
        return self._sfQLE.getSerieIndex()

    def setStartFlatUrl(self, url, serie_index=None) -> None:
        """

        :param DataUrl url:
        :param Union[int,None] serie_index: index of the serie to set
        """
        self._sfCB.setChecked(True)
        self._sfQLE.setUrl(url)
        if serie_index is not None:
            self._sfQLE.setSerie(serie_index)

    def getEndDarkUrl(self) -> Union[None, DataUrl]:
        """

        :return: url defined by the user for patching the end darks
        :rtype:  Union[None, DataUrl]
        """
        if self._edCB.isChecked():
            return self._edQLE.getUrl()
        else:
            return None

    def getEndDarkIndex(self):
        return self._edQLE.getSerieIndex()

    def setEndDarkUrl(self, url, serie_index=None) -> None:
        """

        :param DataUrl url:
        :param Union[int,None] serie_index: index of the serie to set
        """
        self._edCB.setChecked(True)
        self._edQLE.setUrl(url)
        if serie_index is not None:
            self._edQLE.setSerie(serie_index)

    def getEndFlatUrl(self) -> Union[None, DataUrl]:
        """

        :return: url defined by the user for patching the end flats
        :rtype:  Union[None, DataUrl]
        """
        if self._efCB.isChecked():
            return self._efQLE.getUrl()
        else:
            return None

    def getEndFlatIndex(self):
        return self._efQLE.getSerieIndex()

    def setEndFlatUrl(self, url, serie_index=None) -> None:
        """

        :param DataUrl url:
        :param Union[int,None] serie_index: index of the serie to set
        """
        self._efCB.setChecked(True)
        self._efQLE.setUrl(url)
        if serie_index is not None:
            self._efQLE.setSerie(serie_index)

    def clear(self):
        for cb in self._sdCB, self._edCB, self._efCB, self._sfCB:
            cb.setChecked(False)
