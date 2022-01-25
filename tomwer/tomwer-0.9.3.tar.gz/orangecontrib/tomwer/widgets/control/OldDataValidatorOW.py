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

__authors__ = ["C. Nemoz", "H. Payno"]
__license__ = "MIT"
__date__ = "01/12/2016"


import logging
from silx.gui import qt
from orangewidget import widget, gui
from orangewidget.widget import Output, Input
from tomwer.core.process.control.scanvalidator import ScanValidator
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.gui.qfolderdialog import QScanDialog
from tomwer.gui.viewerqwidget import ImageStackViewerValidator
from tomwer.gui.utils.waiterthread import QWaiterThread
from tomwer.web.client import OWClient
from tomwer.core.scan.scanbase import _TomwerBaseDock

logger = logging.getLogger(__name__)


WAIT_TIME_MEM_REL = 20
"""Time (in sec) to wait to check if the scan validator has to release his
stack of scans. This is a security to make sure we are not keeping
unnecessary data during an acquisition in lbsram"""


class OldDataValidatorOW(widget.OWBaseWidget, ScanValidator, openclass=True):
    name = "(old) data validator"
    id = "orange.widgets.tomwer.scanvalidator"
    description = """Widget displaying results of a reconstruction and asking to
    the user if he want to validate or not the reconstruction. User can also ask
    for some modification on the reconstruction parameters"""
    icon = "icons/validatorcrack.png"
    priority = 230
    keywords = ["tomography", "file", "tomwer", "acquisition", "validation"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    _warnValManualShow = False
    """
    used to know if the message to inform user about `validate manually` has
    already been displayed.
    This informative message will be show under the following conditions:

        * the scanValidator contains at least `_NB_SCAN_BF_WARN`
        * this dialog have never been showed in the current session.
    """

    _NB_SCAN_BF_WARN = 10
    """
    Limit of stored scans before displaying the informative message about
    `validate manually` checkbox
    """
    """Signal emitted when receive a scan"""
    scanready = qt.Signal(str)

    class Inputs:
        data = Input(name="data", type=TomwerScanBase)

    class Outputs:
        data = Output(name="data", type=TomwerScanBase)
        recons_params_changed = Output(
            name="change recons params",
            type=_TomwerBaseDock,
        )

    def __init__(
        self, parent=None, ftserie=None, memReleaserWaitLoop=WAIT_TIME_MEM_REL
    ):
        """a simple viewer of image stack

        :param parent: the parent widget
        :param ftserie: an ftserie to validate
        """
        widget.OWBaseWidget.__init__(self, parent)
        ScanValidator.__init__(self, memoryReleaser=QWaiterThread(memReleaserWaitLoop))
        self.destroyed.connect(self._clearMemoryReleaser)
        OWClient.__init__(self)

        self._buildGUI(ftserie)

    def _buildGUI(self, ftserie):
        self.tabsWidget = {}
        # building GUI
        self._scanWidgetLayout = gui.hBox(self.mainArea, self.name).layout()
        self._scanWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.widget = ImageStackViewerValidator(self)
        self._scanWidgetLayout.addWidget(self.widget)

        lateralWidget = qt.QWidget(parent=self)
        lateralWidget.setLayout(qt.QVBoxLayout())
        lateralWidget.layout().setContentsMargins(0, 0, 0, 0)

        # build the slider
        sliderWidget = qt.QWidget(parent=lateralWidget)
        sliderWidget.setLayout(qt.QHBoxLayout())

        self._qslider = qt.QSlider(qt.Qt.Vertical, parent=sliderWidget)
        self._qslider.valueChanged.connect(self.updateStackView)
        sliderWidget.layout().addWidget(self._qslider)

        sliderWidget.layout().addWidget(
            _VerticalLabel("stack of received scan", parent=sliderWidget, revert=True)
        )
        lateralWidget.layout().addWidget(sliderWidget)

        # add scan button
        self._addSlideButton = qt.QPushButton("Add scan", parent=lateralWidget)
        self._addSlideButton.pressed.connect(self._addScanCallBack)

        lateralWidget.layout().addWidget(self._addSlideButton)
        self._scanWidgetLayout.addWidget(lateralWidget)

        self.addScan(ftserie)
        self._connectValidationWidget()

    def _connectValidationWidget(self):
        validationWidget = self.widget.validationWidget
        validationWidget.sigValidateScan.connect(self.validateCurrentScan)
        validationWidget.sigCancelScan.connect(self.cancelCurrentScan)
        validationWidget.sigChangeReconstructionParametersScan.connect(
            self.changeReconsParamCurrentScan
        )
        validationWidget.toggled.connect(self.setManualValidation)

    def getValidationWidget(self, tab):
        return self.widget.validationWidget

    @Inputs.data
    def addScan(self, scan):
        if scan is None:
            return
        assert isinstance(scan, TomwerScanBase)
        ScanValidator.addScan(self, scan)

        self.updateStackView()
        # in the case the memory is full, the scan can have been already
        # validated and so not accessible
        if scan.path in self._scansToValidate:
            self.setActiveScan(self._scansToValidate[scan.path])

        if (
            self._warnValManualShow is False
            and len(self._scansToValidate) >= self._NB_SCAN_BF_WARN
        ):
            mess = (
                "Please note that the scanValidator is actually storing %s "
                "scan(s). \n"
                "Scan need to be validated manually in order to continue "
                "the workflow processing. \n"
                "you can either validate scan manually or uncheck the "
                "`validate manually` check box." % self._NB_SCAN_BF_WARN
            )

            mess = qt.QMessageBox(
                parent=self, icon=qt.QMessageBox.Information, text=mess
            )
            mess.setModal(False)
            mess.show()
            self._warnValManualShow = True
        if self.isValidationManual():
            self.show()
            self.activateWindow()
            self.raise_()

    def updateStackView(self):
        """
        Update the stack view.
         If active is given then this will be the new active value of the stack
        """
        currentDisplayed = self.getCurrentScanID()
        if currentDisplayed is None and len(self._scansToValidate) > 0:
            currentDisplayed = list(self._scansToValidate.keys())[0]

        self._qslider.setRange(0, len(self._scansToValidate) - 1)
        self.setActiveScan(currentDisplayed)

    def setActiveScan(self, scan):
        if scan is None:
            return
        _scanID = scan
        if isinstance(_scanID, TomwerScanBase):
            _scanID = scan.path

        self.widget.clear()
        if _scanID is None or _scanID not in self._scansToValidate:
            return
        else:
            self.widget.updateData(self._scansToValidate[_scanID])
            self.widget.validationWidget.setEnabled(True)
            index = list(self._scansToValidate.keys()).index(_scanID)
            self._qslider.valueChanged.disconnect(self.updateStackView)
            self._qslider.setValue(index)
            self._qslider.valueChanged.connect(self.updateStackView)

    def getCurrentScanID(self):
        """

        :return: the scan currently displayed on the viewer
        :rtype: str
        """
        index = self._qslider.value()
        if index >= len(self._scansToValidate):
            return None
        else:
            return list(self._scansToValidate.keys())[index]

    def getCurrentScan(self):
        """

        :return: the scan currently displayed on the viewer
        :rtype: :class:`.TomoBase`
        """
        scanID = self.getCurrentScanID()
        if scanID:
            return self._scansToValidate[scanID]

    # TODO: should be renamed valid current scan
    def validateCurrentScan(self):
        """This will validate the ftserie currently displayed

        :warning: this will cancel the currently displayed reconstruction.
            But if we are validating a stack of ftserie make sure this is the
            correct one you want to validate. Execution order in this case is
            not insured.
        """
        current_scan = self.getCurrentScan()
        if current_scan:
            assert isinstance(current_scan, TomwerScanBase)
            # TODO: in fact the curretn path is based on the folder, but since
            # we have data transfert it can evolve. So we should use a other
            # id or use the object __hash__
            ScanValidator._validateScan(self, current_scan)
            self.updateStackView()
        # if there is no more scan to validate, hide the widget
        if self.getCurrentScan() is None:
            self.hide()

    def cancelCurrentScan(self):
        """This will cancel the ftserie currently displayed

        :warning: this will cancel the currently displayed reconstruction.
            But if we are validating a stack of ftserie make sure this is the
            correct one you want to validate. Execution order in this case is
            not insured.
        """
        current_scan = self.getCurrentScan()
        if current_scan:
            self._cancelScan(current_scan)
            self.updateStackView()

    def changeReconsParamCurrentScan(self):
        """This will emit a signal to request am acquisition for the current
        ftSerieReconstruction

        :warning: this will cancel the currently displayed reconstruction.
            But if we are validating a stack of ftserie make sure this is the
            correct one you want to validate. Execution order in this case is
            not insured.
        """
        current_scan = self.getCurrentScan()
        if current_scan:
            ScanValidator._changeReconsParam(self, current_scan)
            self.updateStackView()

    def _addScanCallBack(self):
        dialog = QScanDialog(self, multiSelection=True)

        if not dialog.exec_():
            dialog.close()
            return

        foldersSelected = dialog.files_selected()
        new_active_scan = None
        for folder in foldersSelected:
            try:
                scans = ScanFactory.create_scan_objects(scan_path=folder)
            except Exception as e:
                logger.error(
                    "cannot create scan instances from {}. Error is {}".format(
                        folder, e
                    )
                )
            else:
                for scan in scans:
                    self.addScan(scan=scan)
                    new_active_scan = scan

        if new_active_scan is not None:
            self.setActiveScan(new_active_scan)

    def _validateStack(self, filter_=None):
        ScanValidator._validateStack(self)
        self.updateStackView()

    def _sendScanReady(self, scan):
        assert isinstance(scan, TomwerScanBase)
        self.widget.clear()
        self.Outputs.data.send(scan)
        self.scanready.emit(scan.path)

    def _sendScanCanceledAt(self, scan):
        assert isinstance(scan, TomwerScanBase)
        self.widget.clear()

    def _sendUpdateReconsParam(self, scan):
        self.widget.clear()
        self.Outputs.recons_param_changed.send(scan)

    def getNScanToValidate(self):
        return len(self._scansToValidate)


class _VerticalLabel(qt.QLabel):
    """Display vertically the given text"""

    def __init__(self, text, parent=None, revert=False):
        """

        :param text: the legend
        :param parent: the Qt parent if any
        """
        qt.QLabel.__init__(self, text, parent)
        self.revert = revert
        self.setLayout(qt.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

    def paintEvent(self, event):
        painter = qt.QPainter(self)
        painter.setFont(self.font())

        painter.translate(0, self.rect().height())
        painter.rotate(90)
        if self.revert:
            newRect = qt.QRect(
                -self.rect().height(),
                -self.rect().width(),
                self.rect().height(),
                self.rect().width(),
            )

        painter.drawText(newRect, qt.Qt.AlignHCenter, self.text())

        fm = qt.QFontMetrics(self.font())
        preferedHeight = fm.width(self.text())
        preferedWidth = fm.height()
        self.setFixedWidth(preferedWidth)
        self.setMinimumHeight(preferedHeight)
