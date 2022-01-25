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
__date__ = "10/01/2018"


from silx.gui import qt
import logging
from tomwer.core.process.reconstruction.darkref.darkrefs import DarkRefs
from tomwer.core.process.reconstruction.darkref import params as dkrf
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.gui.utils.sandboxes import RegularExpressionSandBox
from tomwer.synctools.ftseries import QReconsParams, _QDKRFRP

logger = logging.getLogger(__name__)


class DarkRefWidget(qt.QWidget):
    """
    A simple widget managing the copy of an incoming folder to an other one

    :param parent: the parent widget
    """

    sigScanReady = qt.Signal(TomwerScanBase)
    """signal emitted when a scan is ready"""
    sigProcessingStart = qt.Signal()
    """signal emitted when a processing starts"""
    sigProcessingEnd = qt.Signal()
    """signal emitted when a processing ends"""

    def __init__(self, reconsparams, parent, process_id=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self.mainWidget = DarkRefTab(parent=self, reconsparams=reconsparams)
        self.layout().addWidget(self.mainWidget)

        # expose API
        self.setReconsParams = self.mainWidget.setReconsParams

        # set up
        self.mainWidget.setReconsParams(recons_params=reconsparams)

    def _processingStarted(self):
        self.sigProcessingStart.emit()

    def _processingEnded(self):
        self.sigProcessingEnd.emit()

    def setName(self, name):
        self._darkRef.name = name

    def setForceSync(self, sync):
        raise NotImplementedError("")
        self._darkRef.setForceSync(sync)

    def _scanReady(self, scan):
        assert isinstance(scan, TomwerScanBase)
        self.sigScanReady.emit(scan)

    @property
    def recons_params(self):
        return self.mainWidget.recons_params


class QDarkRefs(DarkRefs):
    def _instanciateReconsParams(self):
        return QReconsParams(empty=True)

    def _computationStarts(self):
        pass

    def _computationEnds(self):
        pass


class _WhatCheckBox(qt.QWidget):
    """
    Widget grouping a checkbox and a combobox to know the requested mode
    (None, median, average) for a what (ref, dark)
    """

    sigChanged = qt.Signal(dkrf.Method)
    """Signal emitted when the calculation mode change"""

    def __init__(self, parent, text):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QHBoxLayout())
        self._checkbox = qt.QCheckBox(text=text, parent=self)
        self.layout().addWidget(self._checkbox)
        self._modeCB = qt.QComboBox(parent=self)
        for mode in dkrf.Method:
            if mode is dkrf.Method.none:
                continue
            self._modeCB.addItem(mode.name.title())
        self._modeCB.setItemData(
            self._modeCB.findText(dkrf.Method.median.name.title()),
            "Compute the median for each serie",
            qt.Qt.ToolTipRole,
        )
        self._modeCB.setItemData(
            self._modeCB.findText(dkrf.Method.average.name.title()),
            "Compute the average for each serie",
            qt.Qt.ToolTipRole,
        )
        self._modeCB.setItemData(
            self._modeCB.findText(dkrf.Method.first.name.title()),
            "Pick the first frame for a serie",
            qt.Qt.ToolTipRole,
        )
        self._modeCB.setItemData(
            self._modeCB.findText(dkrf.Method.last.name.title()),
            "Pick the last frame for a serie",
            qt.Qt.ToolTipRole,
        )

        self.layout().addWidget(self._modeCB)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self._checkbox.setChecked(True)
        self._checkbox.toggled.connect(self._modeCB.setEnabled)
        self._checkbox.toggled.connect(self._modeChange)
        self._modeCB.currentIndexChanged.connect(self._modeChange)
        self._updateReconsParam = True
        """Boolean used to know if we have to apply modifications on
        the self._reconsParams (in the case user made modification)
        or not (in the case we are simply reading structure and to avoid
        looping in signals with other QObject)"""

    def getMode(self):
        if self._checkbox.isChecked() is True:
            return getattr(dkrf.Method, self._modeCB.currentText().lower())
        else:
            return dkrf.Method.none

    def getModeName(self):
        return self.getMode().name.split(".")[-1].title()

    def _modeChange(self, *a, **b):
        self.sigChanged.emit(self.getMode())

    def setMode(self, mode):
        _mode = mode
        if type(_mode) is str:
            _mode = getattr(dkrf.Method, mode.lower())
        assert _mode in dkrf.Method
        self._checkbox.toggled.disconnect(self._modeChange)
        self._modeCB.currentIndexChanged.disconnect(self._modeChange)
        self._checkbox.setChecked(_mode is not dkrf.Method.none)
        if _mode is not dkrf.Method.none:
            index = self._modeCB.findText(_mode.name.title())
            if index < 0:
                logger.error("index for %s is not recognized" % _mode)
            else:
                self._modeCB.setCurrentIndex(index)
        self._checkbox.toggled.connect(self._modeChange)
        self._modeCB.currentIndexChanged.connect(self._modeChange)
        self.sigChanged.emit(self.getMode())


class _TabGeneral(qt.QWidget):
    """Widget with the general information for dark and ref process"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())

        self._grpWhat = qt.QGroupBox("what", parent=self)
        self._grpWhat.setLayout(qt.QVBoxLayout())
        self._darkWCB = _WhatCheckBox(parent=self._grpWhat, text="dark")
        self._refWCB = _WhatCheckBox(parent=self._grpWhat, text="flat")
        self._grpWhat.layout().addWidget(self._darkWCB)
        self.sigDarkChanged = self._darkWCB.sigChanged
        self._grpWhat.layout().addWidget(self._refWCB)
        self.sigRefChanged = self._refWCB.sigChanged
        self.layout().addWidget(self._grpWhat)

        self._grpOptions = qt.QGroupBox("options", parent=self)
        self._grpOptions.setLayout(qt.QVBoxLayout())
        self._rmOptionCB = qt.QCheckBox(
            parent=self._grpOptions, text="remove raw files when done"
        )
        self.sigRmToggled = self._rmOptionCB.toggled
        self._skipOptionCB = qt.QCheckBox(
            parent=self._grpOptions, text="skip if already existing"
        )
        self.sigSkipToggled = self._skipOptionCB.toggled
        self._grpOptions.layout().addWidget(self._rmOptionCB)
        self._grpOptions.layout().addWidget(self._skipOptionCB)
        self.layout().addWidget(self._grpOptions)

        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)

        self.layout().addWidget(spacer)


class _TabExpert(qt.QWidget):
    """Expert process for dark and ref"""

    sigDarkPatternEdited = qt.Signal(str)
    sigRefPatternEdited = qt.Signal(str)

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())

        self._patternsWidget = qt.QWidget(parent=self)
        self._patternsWidget.setLayout(qt.QGridLayout())

        self._patternsWidget.layout().addWidget(
            qt.QLabel("dark file pattern", parent=self._patternsWidget), 0, 0
        )
        self._darkLE = qt.QLineEdit(parent=self._patternsWidget)
        self._darkLE.setToolTip(DarkRefs.getDarkPatternTooltip())
        self._darkLE.editingFinished.connect(self._darkPatternEdited)
        self._patternsWidget.layout().addWidget(self._darkLE, 0, 1)
        self._patternsWidget.layout().addWidget(
            qt.QLabel("flat file pattern", parent=self._patternsWidget), 1, 0
        )
        self._refLE = qt.QLineEdit(parent=self._patternsWidget)
        self._refLE.setToolTip(DarkRefs.getRefPatternTooltip())
        self._refLE.editingFinished.connect(self._refPatternEdited)

        self._patternsWidget.layout().addWidget(self._refLE, 1, 1)

        self.layout().addWidget(self._patternsWidget)

        textExtraInfo = (
            "note: to have more information about pattern usage \n"
            "see tooltips over dark and flat field patterns."
            "\nYou can also see help to have advance"
            "information"
        )
        labelNote = qt.QLabel(parent=self, text=textExtraInfo)
        labelNote.setSizePolicy(qt.QSizePolicy.Preferred, qt.QSizePolicy.Minimum)
        self.layout().addWidget(labelNote)

        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)

        self.layout().addWidget(spacer)

    def _darkPatternEdited(self):
        self.sigDarkPatternEdited.emit(self._darkLE.text())

    def _refPatternEdited(self):
        self.sigRefPatternEdited.emit(self._refLE.text())


class DarkRefTab(qt.QTabWidget):
    # TODO: should modify the reconsparams to

    def __init__(self, parent, reconsparams):
        self.recons_params = None
        qt.QTabWidget.__init__(self, parent)
        self.tabGeneral = _TabGeneral(parent=self)
        self.addTab(self.tabGeneral, "general")
        self.tabExpert = _TabExpert(parent=self)
        self.addTab(self.tabExpert, "expert")
        self.tabSandBox = RegularExpressionSandBox(parent=self, pattern="")
        extraSandBoxInfo = qt.QLabel(
            "This sand box allow you to play with"
            "regular expressions and check the "
            "validity of a defined pattern versus "
            "acquisition names. This way you can be "
            "insure of the regular expression "
            "behavior",
            parent=self.tabSandBox,
        )
        extraSandBoxInfo.setWordWrap(True)
        self.tabSandBox.layout().insertWidget(0, extraSandBoxInfo)
        self.tabSandBox.setToolTip("play with regular expression")
        self.addTab(self.tabSandBox, "re sandbox")

        self._makeConnection()
        self.setReconsParams(recons_params=reconsparams)

    def _disconnectToReconsParams(self):
        assert self.recons_params
        try:
            self.tabGeneral.sigDarkChanged.disconnect(
                self.recons_params.__class__.dark_calc_method.setter
            )
            self.tabGeneral.sigRefChanged.disconnect(
                self.recons_params.__class__.ref_calc_method.setter
            )
            self.tabGeneral.sigRmToggled.disconnect(self.recons_params._set_remove_opt)
            self.tabGeneral.sigSkipToggled.disconnect(
                self.recons_params._set_skip_if_exist
            )

            self.tabExpert.sigDarkPatternEdited.disconnect(
                self.recons_params.__class__.dark_pattern.setter
            )
            self.tabExpert.sigRefPatternEdited.disconnect(
                self.recons_params.__class__.ref_pattern.setter
            )
            self.recons_params.sigChanged.disconnect(self._updateReconsParams)
        except Exception:
            pass

    def _connectToReconsParams(self):
        assert self.recons_params
        self.tabGeneral.sigDarkChanged.connect(
            self.recons_params.__class__.dark_calc_method.setter
        )
        self.tabGeneral.sigRefChanged.connect(
            self.recons_params.__class__.ref_calc_method.setter
        )
        self.tabGeneral.sigRmToggled.connect(self.recons_params._set_remove_opt)
        self.tabGeneral.sigSkipToggled.connect(self.recons_params._set_skip_if_exist)

        self.tabExpert.sigDarkPatternEdited.connect(
            self.recons_params.__class__.dark_pattern.setter
        )
        self.tabExpert.sigRefPatternEdited.connect(
            self.recons_params.__class__.ref_pattern.setter
        )
        self.recons_params.sigChanged.connect(self._updateReconsParams)

    def _updateReconsParams(self):
        self.loadStructs(self.recons_params.to_dict())

    def setReconsParams(self, recons_params):
        assert isinstance(recons_params, (QReconsParams, _QDKRFRP))
        if isinstance(recons_params, _QDKRFRP):
            _recons_params = recons_params
        else:
            _recons_params = recons_params.dkrf

        if self.recons_params:
            self._disconnectToReconsParams()

        self.recons_params = _recons_params
        self._updateReconsParams()
        self._connectToReconsParams()

    def _makeConnection(self):
        self.tabGeneral._refWCB.sigChanged.connect(self._refCalcModeChanged)
        self.tabGeneral._darkWCB.sigChanged.connect(self._darkCalcModeChanged)
        self.tabGeneral._rmOptionCB.toggled.connect(self._rmOptChanged)
        self.tabGeneral._skipOptionCB.toggled.connect(self._skipOptChanged)
        self.tabExpert._darkLE.editingFinished.connect(self._darkPatternChanged)
        self.tabExpert._refLE.editingFinished.connect(self._refPatternChanged)

    def loadStructs(self, structs):
        def warningKeyNotHere(key):
            logger.warning(
                "%s key not present in the given struct, "
                "cannot load value for it." % key
            )

        assert isinstance(structs, dict)

        if "DARKCAL" not in structs:
            warningKeyNotHere("DARKCAL")
        else:
            self.setDarkMode(structs["DARKCAL"])

        if "REFSCAL" not in structs:
            warningKeyNotHere("REFSCAL")
        else:
            self.setRefMode(structs["REFSCAL"])

        if "REFSOVE" not in structs:
            warningKeyNotHere("REFSOVE")
        else:
            self.setSkipOption(not structs["REFSOVE"])

        if "REFSRMV" not in structs:
            warningKeyNotHere("REFSRMV")
        else:
            self.setRemoveOption(structs["REFSRMV"])

        if "RFFILE" not in structs:
            warningKeyNotHere("RFFILE")
        else:
            self.setRefPattern(structs["RFFILE"])

        if "DKFILE" not in structs:
            warningKeyNotHere("DKFILE")
        else:
            self.setDarkPattern(structs["DKFILE"])

    def setRemoveOption(self, rm):
        self.tabGeneral._rmOptionCB.setChecked(rm)

    def setSkipOption(self, skip):
        self.tabGeneral._skipOptionCB.setChecked(skip)

    def setDarkMode(self, mode):
        self.tabGeneral._darkWCB.setMode(mode)

    def setRefMode(self, mode):
        self.tabGeneral._refWCB.setMode(mode)

    def setRefPattern(self, pattern):
        self.tabExpert._refLE.setText(pattern)

    def setDarkPattern(self, pattern):
        self.tabExpert._darkLE.setText(pattern)

    def _rmOptChanged(self):
        value = self.tabGeneral._rmOptionCB.isChecked()
        self.recons_params._set_remove_opt(value)

    def _skipOptChanged(self):
        value = self.tabGeneral._skipOptionCB.isChecked()
        self.recons_params._set_skip_if_exist(value)

    def _refPatternChanged(self):
        value = self.tabExpert._refLE.text()
        self.recons_params["RFFILE"] = value

    def _darkPatternChanged(self):
        value = self.tabExpert._darkLE.text()
        self.recons_params["DKFILE"] = value

    def _darkCalcModeChanged(self):
        value = self.tabGeneral._darkWCB.getMode()
        self.recons_params["DARKCAL"] = value

    def _refCalcModeChanged(self):
        value = self.tabGeneral._refWCB.getMode()
        self.recons_params["REFSCAL"] = value
