# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
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
__date__ = "31/03/2021"


from silx.gui import qt
from tomwer.core.scan.scanbase import TomwerScanBase
import weakref
import logging
from tomwer.core.scan.edfscan import EDFTomoScan

_logger = logging.getLogger(__name__)


class ScanOverviewWidget(qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scan = None
        self.setLayout(qt.QVBoxLayout())
        self._tree = qt.QTreeWidget(self)
        self._tree.setColumnCount(2)
        self._tree.setHeaderLabels(("entry", "value"))
        self.layout().addWidget(self._tree)

        # 1: define instrument
        self._instrument = qt.QTreeWidgetItem(self._tree)
        self._instrument.setText(0, "instrument")
        # 1.1 define beam
        self._beam = qt.QTreeWidgetItem(self._instrument)
        self._beam.setText(0, "beam")
        self._energy = qt.QTreeWidgetItem(self._beam)
        self._energy.setText(0, "energy")
        # 1.1 define detector
        self._frames = qt.QTreeWidgetItem(self._instrument)
        self._frames.setText(0, "frames")
        self._projections = qt.QTreeWidgetItem(self._frames)
        self._projections.setText(0, "projections")
        self._darks = qt.QTreeWidgetItem(self._frames)
        self._darks.setText(0, "darks")
        self._flats = qt.QTreeWidgetItem(self._frames)
        self._flats.setText(0, "flats")
        self._alignments = qt.QTreeWidgetItem(self._frames)
        self._alignments.setText(0, "alignments")

        self._x_pixel_size = qt.QTreeWidgetItem(self._instrument)
        self._x_pixel_size.setText(0, "x pixel size")
        self._y_pixel_size = qt.QTreeWidgetItem(self._instrument)
        self._y_pixel_size.setText(0, "y pixel size")

        # 2: define sample
        self._sample = qt.QTreeWidgetItem(self._tree)
        self._sample.setText(0, "sample")
        self._sample_name = qt.QTreeWidgetItem(self._sample)
        self._sample_name.setText(0, "name")

        # 3: other hight level items
        self._startTime = qt.QTreeWidgetItem(self._tree)
        self._startTime.setText(0, "start_time")
        self._endTime = qt.QTreeWidgetItem(self._tree)
        self._endTime.setText(0, "end_time")
        self._title = qt.QTreeWidgetItem(self._tree)
        self._title.setText(0, "title")

        # set up
        self._instrument.setExpanded(True)
        self._frames.setExpanded(True)
        self._sample.setExpanded(True)
        self._beam.setExpanded(True)

    def setScan(self, scan):
        if scan is None:
            self._scan = scan
            self.clear()
        elif not isinstance(scan, TomwerScanBase):
            raise TypeError(f"{scan} is expected to be an instance of {TomwerScanBase}")
        else:
            self._scan = weakref.ref(scan)
        self.update_tree()

    def getScan(self):
        if self._scan is None or self._scan() is None:
            return None
        else:
            return self._scan()

    def update_tree(self):
        if self.getScan() is not None:
            for fct in (
                self._updateInstrument,
                self._updateSample,
                self._updateTimes,
                self._updateNames,
            ):
                try:
                    fct()
                except Exception as e:
                    _logger.info(e)
            self._tree.resizeColumnToContents(0)

    def _updateInstrument(self):
        self._updateFrames()
        self._updateEnergy()
        self._updatePixelSize()

    def _setColoredTxt(
        self, item, text, column=1, hightlight_red=False, hightlight_orange=False
    ):
        if text in (None, str(None)):
            text = "?"
        if hightlight_red:
            bkg_color = qt.QColor(220, 0, 0, 200)
        elif hightlight_orange:
            bkg_color = qt.QColor(200, 160, 0, 150)
        else:
            bkg_color = qt.QColor(0, 220, 0, 50)

        item.setText(column, text)
        item.setBackground(0, qt.QBrush(bkg_color))

    def _updateSample(self):
        pass

    def _updateTimes(self):
        scan = self.getScan()
        self._startTime.setText(1, str(scan.start_time))
        self._endTime.setText(1, str(scan.end_time))

    def _updateFrames(self):
        scan = self.getScan()
        assert isinstance(scan, TomwerScanBase)
        # frames
        n_frames = len(scan.frames)
        self._setColoredTxt(
            item=self._frames,
            text=str(n_frames),
            hightlight_red=(n_frames in (0, None)),
        )
        # projections
        n_proj = len(scan.projections)
        self._setColoredTxt(
            item=self._projections,
            text=str(n_proj),
            hightlight_red=(n_proj in (0, None)),
        )
        # darks
        n_darks = len(scan.darks)
        self._setColoredTxt(
            item=self._darks,
            text=str(n_darks),
            hightlight_red=(n_darks in (0, None)),
        )

        # flats
        n_flats = len(scan.flats)
        self._setColoredTxt(
            item=self._flats,
            text=str(n_flats),
            hightlight_red=(n_flats in (0, None)),
        )
        # align
        n_alignment = len(scan.alignment_projections)
        self._setColoredTxt(
            item=self._alignments,
            text=str(n_alignment),
        )

    def _updateEnergy(self):
        scan = self.getScan()
        assert isinstance(scan, TomwerScanBase)
        energy = scan.energy
        self._setColoredTxt(
            item=self._energy,
            text=f"{energy} (kev)",
            hightlight_red=energy in (0, None),
        )

    def _updateNames(self):
        scan = self.getScan()
        assert isinstance(scan, TomwerScanBase)
        sample_name = scan.sample_name
        sequence_name = scan.sequence_name
        self._title.setText(1, sequence_name)
        self._sample_name.setText(1, sample_name)

    def _updateTomoN(self):
        scan = self.getScan()
        assert isinstance(scan, TomwerScanBase)
        tomo_n = scan.tomo_n
        self._setColoredTxt(
            item=self._tomoNQLE,
            text=str(tomo_n),
        )

    def _updateScanRange(self):
        scan = self.getScan()
        assert isinstance(scan, TomwerScanBase)
        scan_range = scan.scan_range
        self._setColoredTxt(
            item=self._scanRangeQLE,
            text=str(scan_range),
        )

    def _updatePixelSize(self):
        scan = self.getScan()
        assert isinstance(scan, TomwerScanBase)
        if isinstance(scan, EDFTomoScan):
            x_pixel_size = y_pixel_size = scan.pixel_size
        else:
            x_pixel_size = scan.x_pixel_size
            y_pixel_size = scan.y_pixel_size
        self._setColoredTxt(
            item=self._x_pixel_size,
            text=f"{x_pixel_size} (m)",
            hightlight_red=x_pixel_size in (None, 0.0, 1.0),
        )
        self._setColoredTxt(
            item=self._y_pixel_size,
            text=f"{y_pixel_size} (m)",
            hightlight_red=y_pixel_size in (None, 0.0, 1.0),
        )

    def clear(self):
        self._tree.clear()
