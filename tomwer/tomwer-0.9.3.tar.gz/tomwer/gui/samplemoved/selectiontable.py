# /*##########################################################################
# Copyright (C) 2017 European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
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
#############################################################################*/
"""Some widget construction to check if a sample moved"""

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "17/08/2021"


import os
from collections import OrderedDict
import functools
from silx.gui import qt
from silx.io.url import DataUrl
from tomwer.gui.imagefromfile import FileWithImage
import logging

logger = logging.getLogger(__name__)


class SelectionTable(qt.QTableWidget):
    """Table used to select the color channel to be displayed for each"""

    COLUMS_INDEX = OrderedDict([("url", 0), ("img A", 1), ("img B", 2)])

    sigImageAChanged = qt.Signal(str)
    """Signal emitted when the image A change. Param is the image url path"""

    sigImageBChanged = qt.Signal(str)
    """Signal emitted when the image B change. Param is the image url path"""

    def __init__(self, parent=None):
        qt.QTableWidget.__init__(self, parent)
        self.clear()

    def clear(self):
        qt.QTableWidget.clear(self)
        self.setRowCount(0)
        self.setColumnCount(len(self.COLUMS_INDEX))
        self.setHorizontalHeaderLabels(list(self.COLUMS_INDEX.keys()))
        self.horizontalHeader().setSectionResizeMode(qt.QHeaderView.ResizeToContents)
        self.verticalHeader().hide()
        self.setSortingEnabled(True)
        self._checkBoxes = {}

    def addRadio(self, name, **kwargs):
        if isinstance(name, DataUrl):
            self.addUrl(name, **kwargs)
        else:
            assert os.path.isfile(name)
            if not os.path.isfile(name):
                logger.error("%s is not a file path" % name)
                return

            imgFile = FileWithImage(name)
            for imgFrmFile in imgFile.getImages(_load=False):
                self.addUrl(imgFrmFile.url, **kwargs)

    def addUrl(self, url, **kwargs):
        """

        :param url:
        :param args:
        :return: index of the created items row
        :rtype int
        """
        assert isinstance(url, DataUrl)
        row = self.rowCount()
        self.setRowCount(row + 1)
        # nasty hack, should be done in silx or in tomoscan
        data_path_label = qt.QLabel(url.path())
        self.setCellWidget(row, self.COLUMS_INDEX["url"], data_path_label)

        widgetImgA = qt.QCheckBox(self)
        self.setCellWidget(row, self.COLUMS_INDEX["img A"], widgetImgA)
        callbackImgA = functools.partial(self._activeImgAChanged, url.path())
        widgetImgA.toggled.connect(callbackImgA)

        widgetImgB = qt.QCheckBox(self)
        self.setCellWidget(row, self.COLUMS_INDEX["img B"], widgetImgB)
        callbackImgB = functools.partial(self._activeImgBChanged, url.path())
        widgetImgB.toggled.connect(callbackImgB)

        self._checkBoxes[url.path()] = {"img A": widgetImgA, "img B": widgetImgB}
        return row

    def _activeImgAChanged(self, name):
        self._updatecheckBoxes("img A", name)
        self.sigImageAChanged.emit(name)

    def _activeImgBChanged(self, name):
        self._updatecheckBoxes("img B", name)
        self.sigImageBChanged.emit(name)

    def _updatecheckBoxes(self, whichImg, name):
        assert name in self._checkBoxes
        assert whichImg in self._checkBoxes[name]
        if self._checkBoxes[name][whichImg].isChecked():
            for radioUrl in self._checkBoxes:
                if radioUrl != name:
                    self._checkBoxes[radioUrl][whichImg].blockSignals(True)
                    self._checkBoxes[radioUrl][whichImg].setChecked(False)
                    self._checkBoxes[radioUrl][whichImg].blockSignals(False)

    def getSelection(self):
        """

        :return: url selected for img A and img B.
        """
        imgA = imgB = None
        for radioUrl in self._checkBoxes:
            if self._checkBoxes[radioUrl]["img A"].isChecked():
                imgA = radioUrl
            if self._checkBoxes[radioUrl]["img B"].isChecked():
                imgB = radioUrl
        return imgA, imgB

    def setSelection(self, url_img_a, url_img_b):
        """

        :param ddict: key: image url, values: list of active channels
        """
        if isinstance(url_img_a, qt.QRect) or isinstance(url_img_b, qt.QRect):
            return
        for radioUrl in self._checkBoxes:
            for img in ("img A", "img B"):
                self._checkBoxes[radioUrl][img].blockSignals(True)
                self._checkBoxes[radioUrl][img].setChecked(False)
                self._checkBoxes[radioUrl][img].blockSignals(False)

        self._checkBoxes[radioUrl][img].blockSignals(True)
        self._checkBoxes[url_img_a]["img A"].setChecked(True)
        self._checkBoxes[radioUrl][img].blockSignals(False)

        self._checkBoxes[radioUrl][img].blockSignals(True)
        self._checkBoxes[url_img_b]["img B"].setChecked(True)
        self._checkBoxes[radioUrl][img].blockSignals(False)
        self.sigImageAChanged.emit(url_img_a)
        self.sigImageBChanged.emit(url_img_b)


class AngleSelectionTable(SelectionTable):
    """The selection table but with the angle column.
    Allows to make selection on angles to
    """

    class _AngleItem(qt.QTableWidgetItem):
        """Simple QTableWidgetItem allowing ordering on angles"""

        def __init__(self, type=qt.QTableWidgetItem.Type):
            qt.QTableWidgetItem.__init__(self, type=type)

        def __lt__(self, other):
            a1 = IntAngle(self.text())
            a2 = IntAngle(other.text())
            return a1 < a2

    COLUMS_INDEX = OrderedDict(
        [("angle", 0), ("file name", 1), ("url", 2), ("img A", 3), ("img B", 4)]
    )

    def __init__(self, parent):
        SelectionTable.__init__(self, parent)
        self._anglesToUrl = {}

    def addUrl(self, url, **kwargs):
        assert "angle" in kwargs
        row = SelectionTable.addUrl(self, url, **kwargs)

        _item = qt.QTableWidgetItem()
        _item.setText(os.path.basename(url.file_path()))
        _item.setFlags(qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable)
        self.setItem(row, self.COLUMS_INDEX["file name"], _item)

        angle = "???"
        if "angle" in kwargs:
            angle = kwargs["angle"]

        item = self._AngleItem()
        item.setText(str(angle))
        self.setItem(row, self.COLUMS_INDEX["angle"], item)
        self._anglesToUrl[angle] = url.path()

    def setAngleSelection(self, angle_a_values, angle_b_values):
        """

        :param tuple angle_a_values: tuple of valid angle for angle a
        :param tuple angle_b_values: tuple of valid angle for angle b
        """
        url_angle_a = url_angle_b = None
        for angle_a_val in angle_a_values:
            if angle_a_val in self._anglesToUrl:
                url_angle_a = self._anglesToUrl[angle_a_val]
                break

        for angle_b_value in angle_b_values:
            if angle_b_value in self._anglesToUrl:
                url_angle_b = self._anglesToUrl[angle_b_value]
                break
        self.setSelection(url_angle_a, url_angle_b)

    def clear(self):
        SelectionTable.clear(self)
        self._anglesToUrl = {}


class IntAngle(str):
    """Simple class used to order angles"""

    def __new__(cls, *args, **kwargs):
        return str.__new__(cls, *args, **kwargs)

    def getAngle(self):
        """Return the acquisition angle as an int"""
        val = self
        if "(" in self:
            val = self.split("(")[0]
        if val.isdigit() is False:
            return False
        else:
            return int(val)

    def getAngleN(self):
        """Return the second information if the acquisition is the first
        one taken at this angle or not."""
        if "(" not in self:
            return 0
        return int(self.split("(")[1][:-1])

    def __lt__(self, other):
        if self.getAngle() == other.getAngle():
            return self.getAngleN() < other.getAngleN()
        else:
            return self.getAngle() < other.getAngle()
