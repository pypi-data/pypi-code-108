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
__date__ = "01/06/2018"


import os
from silx.gui import qt
import logging
from tomwer.core.process.reconstruction.lamino.tofu import getDark, getFlats, FFCWhen
from tomwer.core.utils import getDARK_N, getDim1Dim2
from tomwer.core.utils import getParametersFromParOrInfo
from tomwer.core.utils import getTomo_N, getPixelSize, getClosestEnergy
from tomwer.core.utils.char import PSI_CHAR, THETA_CHAR
from tomwer.gui import icons
from tomwer.gui.utils.illustrations import _IllustrationWidget, _IllustrationDialog
from tomwer.gui.utils.unitsystem import MetricEntry
from .TofuOptionLoader import _TofuOptionLoader, _getterSetter
from .misc import _AngleWidget, PadlockButton

_logger = logging.getLogger(__name__)


class InputProjectionsScrollArea(qt.QScrollArea):
    def __init__(self, parent):
        qt.QScrollArea.__init__(self, parent)
        self.widget = InputProjectionsWidget(parent=self)
        self.setWidget(self.widget)
        self.setWidgetResizable(True)

        # expose API
        self.loadFromScan = self.widget.loadFromScan
        self.setNumber = self.widget.setNumber
        self.getNumber = self.widget.getNumber
        self.getPixelSize = self.widget.getPixelSize
        self.setPixelSize = self.widget.setPixelSize
        self.pixelSizeIsLocked = self.widget.pixelSizeIsLocked
        self.getParameters = self.widget.getParameters
        self.loadFromScan = self.widget.loadFromScan
        self.setParameters = self.widget.setParameters
        self.rotationAngle = self.widget.rotationAngle
        self.centeringWidget = self.widget.centeringWidget
        self.getWhenApplyFFC = self.widget.getWhenApplyFFC
        self.setWhenApplyFFC = self.widget.setWhenApplyFFC
        self.isHalfAcquisition = self.widget.isHalfAcquisition
        self.setHalfAcquisition = self.widget.setHalfAcquisition
        self.setBlend = self.widget.setBlend
        self.setAdjustMean = self.widget.setAdjustMean


class InputProjectionsWidget(_TofuOptionLoader, qt.QWidget):
    """TabWidget containing all the information relative to the
    flat field correction"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())

        self.rotationAngle = RotationAngleGroupBox(parent=self)
        self.layout().addWidget(self.rotationAngle, 0, 0)

        self.centeringWidget = CenteringTofuGroupBox(parent=self)
        self.layout().addWidget(self.centeringWidget, 1, 0)

        self._numberOfFiles = NbFilesWidget(parent=self)
        self._numberOfFiles.layout().setContentsMargins(6, 2, 2, 2)
        self.layout().addWidget(self._numberOfFiles, 2, 0)

        # pixel size
        self._pixelWidget = qt.QWidget(parent=self)
        self._pixelWidget.setLayout(qt.QHBoxLayout())
        self._pixelWidget.layout().setContentsMargins(6, 2, 2, 2)

        self._pixelSize = MetricEntry(name="pixel size", parent=self, default_unit="m")
        self._pixelWidget.layout().addWidget(self._pixelSize._label)
        self._pixelWidget.layout().addWidget(self._pixelSize._qlePixelSize)
        self._pixelWidget.layout().addWidget(self._pixelSize._qcbUnit)
        self._pixelSizeLockButton = PadlockButton(parent=self)
        self._pixelWidget.layout().addWidget(self._pixelSizeLockButton)
        self.layout().addWidget(self._pixelWidget, 3, 0)

        # half  & options
        self._halfAcqWidget = qt.QWidget(parent=self)
        self._halfAcqWidget.setLayout(qt.QHBoxLayout())
        self._halfAcqWidget.layout().setContentsMargins(6, 2, 2, 2)
        self._halfAcqCB = qt.QCheckBox("half acquisition", parent=self)
        self._halfAcqWidget.layout().addWidget(self._halfAcqCB)
        self._blendCB = qt.QCheckBox("blend", parent=self)
        self._blendCB.setVisible(False)
        self._halfAcqWidget.layout().addWidget(self._blendCB)
        self._adjustMeanCB = qt.QCheckBox("adjust mean", parent=self)
        self._adjustMeanCB.setVisible(False)
        self._halfAcqWidget.layout().addWidget(self._adjustMeanCB)
        self.layout().addWidget(self._halfAcqWidget, 4, 0)

        # flat field correction
        self._ffcWidget = _FFCConfigWidget(parent=self)
        self.layout().addWidget(self._ffcWidget, 5, 0, 2, 2)

        self._phaseRetrieval = PhaseRetrievalWidget(parent=self)
        self._phaseRetrieval.setCheckable(True)
        self._phaseRetrieval.setChecked(False)
        self.layout().addWidget(self._phaseRetrieval, 7, 0)

        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        self._ffcWidget._absortivityActivated.connect(self._phaseRetrieval.setUnchecked)
        self._phaseRetrieval.activated.connect(self._ffcWidget.uncheckedAbsorptivity)

        # expose API
        self.setNumber = self._numberOfFiles.setNumberOfFiles
        self.getNumber = self._numberOfFiles.getNumberOfFiles
        self.getPixelSize = self._pixelSize.getValue
        self.setPixelSize = self._pixelSize.setValue
        self.pixelSizeIsLocked = self._pixelSizeLockButton.isLocked
        self.getWhenApplyFFC = self._ffcWidget.getWhenApplyFFC
        self.setWhenApplyFFC = self._ffcWidget.setWhenApplyFFC
        self.isHalfAcquisition = self._halfAcqCB.isChecked
        self.setHalfAcquisition = self._halfAcqCB.setChecked
        self.isBlend = self._blendCB.isChecked
        self.setBlend = self._blendCB.setChecked
        self.isAdjustMean = self._adjustMeanCB.isChecked
        self.setAdjustMean = self._adjustMeanCB.setChecked

        options = {
            "ffc-when": _getterSetter(
                getter=self.getWhenApplyFFC, setter=self.setWhenApplyFFC
            ),
            "number": _getterSetter(getter=self.getNumber, setter=self.setNumber),
            "reduction-mode": _getterSetter(
                getter=self._ffcWidget.getMethod, setter=self._ffcWidget.setMethod
            ),
            "darks": _getterSetter(
                getter=self._ffcWidget.getDarks, setter=self._ffcWidget.setDarks
            ),
            "flats": _getterSetter(
                getter=self._ffcWidget.getFlats, setter=self._ffcWidget.setFlats
            ),
            "flats2": _getterSetter(
                getter=self._ffcWidget.getSecondFlats,
                setter=self._ffcWidget.setSecondFlats,
            ),
            "absorptivity": _getterSetter(
                getter=self._ffcWidget.requireAbsorptivity,
                setter=self._ffcWidget.setAbsortivity,
            ),
            "fix-nan-and-inf": _getterSetter(
                getter=self._ffcWidget.removeNanAndInf,
                setter=self._ffcWidget.setNanAndInf,
            ),
            "dark-scale": _getterSetter(
                getter=self._ffcWidget.getDarkScale, setter=self._ffcWidget.setDarkScale
            ),
            "axis-angle-x": _getterSetter(
                getter=self.rotationAngle._laminoAngle.getAngle,
                setter=self.rotationAngle._laminoAngle.setAngle,
            ),
            "axis-angle-y": _getterSetter(
                getter=self.rotationAngle._axisAngleY.getAngle,
                setter=self.rotationAngle._axisAngleY.setAngle,
            ),
            "axis-angle-z": _getterSetter(
                getter=self.rotationAngle._axisAngleZ.getAngle,
                setter=self.rotationAngle._axisAngleZ.setAngle,
            ),
            "center-position-x": _getterSetter(
                getter=self.centeringWidget.getXCenter,
                setter=self.centeringWidget.setXCenter,
            ),
            "center-position-z": _getterSetter(
                getter=self.centeringWidget.getZCenter,
                setter=self.centeringWidget.setZCenter,
            ),
            "overall-angle": _getterSetter(
                getter=self.rotationAngle._overallAngle.getAngle,
                setter=self.rotationAngle._setOverallAngleI,
            ),
            "pixel-size": _getterSetter(
                getter=self.getPixelSize, setter=self.setPixelSize
            ),
            "half-acquisition": _getterSetter(
                getter=self.isHalfAcquisition, setter=self._halfAcqCB.setChecked
            ),
            "blend": _getterSetter(getter=self.isBlend, setter=self.setBlend),
            "adjust-mean": _getterSetter(
                getter=self.isAdjustMean, setter=self.setAdjustMean
            ),
        }
        _TofuOptionLoader.__init__(self, options=options, childs=[self._phaseRetrieval])

        # connect
        self._halfAcqCB.toggled.connect(self._updateFFCOptions)

    def _updateFFCOptions(self):
        # if we want the half acquisition, for now we force the ffc to be done
        # in preprocessing
        self._ffcWidget.forcePreprocessing(self._halfAcqCB.isChecked())
        self._blendCB.setVisible(self._halfAcqCB.isChecked())
        self._adjustMeanCB.setVisible(self._halfAcqCB.isChecked())

    def loadFromScan(self, scanID):
        if scanID is None:
            return
        try:
            nFile = getTomo_N(scanID)
            self.setNumber(nFile)
        except Exception as error:
            _logger.error(error)

        self.rotationAngle.loadFromScan(scanID=scanID)
        self.centeringWidget.loadFromScan(scanID=scanID)
        self._ffcWidget.loadFromScan(scanID=scanID)
        self._phaseRetrieval.loadFromScan(scanID=scanID)

        pixelSize = getPixelSize(scanID)
        if pixelSize is not None and self.pixelSizeIsLocked() is False:
            self.setPixelSize(float(pixelSize))


class _FFCConfigWidget(qt.QGroupBox):
    """Widget dedicated to the parameters used for the flat field correction"""

    _absortivityActivated = qt.Signal()
    """Signal emitted when the absorptivity is activated"""

    def __init__(self, parent):
        super(_FFCConfigWidget, self).__init__("flat field correction", parent)
        self.setLayout(qt.QGridLayout())

        self._whenGrp = _FFCWhenWidget(parent=self)
        self.layout().addWidget(qt.QLabel("when"), 0, 0)
        self.layout().addWidget(self._whenGrp, 0, 1)

        self.layout().addWidget(qt.QLabel("method"), 1, 0)
        self._method = qt.QComboBox(parent=self)
        self._method.addItem("median")
        self._method.addItem("Average")
        self.layout().addWidget(self._method, 1, 1)

        self.__absortivityLabel = qt.QLabel("absorptivity (*)")
        self.__absortivityLabel.setToolTip(
            "Activating absortivity will " "deactivate phase retrieval"
        )
        self.layout().addWidget(self.__absortivityLabel, 2, 0)

        self._absortivity = qt.QCheckBox(parent=self)
        self.layout().addWidget(self._absortivity, 2, 1)
        self._absortivity.setChecked(True)

        self.layout().addWidget(qt.QLabel("remove Nan and Inf"), 3, 0)
        self._removeNanInf = qt.QCheckBox(parent=self)
        self.layout().addWidget(self._removeNanInf, 3, 1)
        self._removeNanInf.setChecked(True)

        self.layout().addWidget(qt.QLabel("dark scale"), 4, 0)
        self._darkScaleSB = qt.QDoubleSpinBox(parent=self)
        self._darkScaleSB.setMinimum(0.0)
        self._darkScaleSB.setValue(1.0)
        self._darkScaleSB.setSingleStep(0.1)
        self.layout().addWidget(self._darkScaleSB, 4, 1)

        self.layout().addWidget(qt.QLabel("darks"), 5, 0)
        self._darksLE = qt.QLineEdit("", parent=self)
        self.layout().addWidget(self._darksLE, 5, 1)
        self.layout().addWidget(qt.QLabel("flats"), 6, 0)
        self._flatsLE = qt.QLineEdit("", parent=self)
        self.layout().addWidget(self._flatsLE, 6, 1)

        self.layout().addWidget(qt.QLabel("second flats"), 7, 0)
        self._secondFlatsLE = qt.QLineEdit("", parent=self)
        self.layout().addWidget(self._secondFlatsLE, 7, 1)

        self._absortivity.toggled.connect(self._absortivityStatusChanged)

        # expose API
        self.getWhenApplyFFC = self._whenGrp.getWhen
        self.setWhenApplyFFC = self._whenGrp.setWhen
        self.forcePreprocessing = self._whenGrp.forcePreprocessing

    def _absortivityStatusChanged(self, checked):
        if checked is True:
            self._absortivityActivated.emit()

    def uncheckedAbsorptivity(self):
        self._absortivity.setChecked(False)

    def getMethod(self):
        return self._method.currentText()

    def setMethod(self, method):
        _method = method
        if _method.lower == "median":
            _method = "median"
        if _method.title() == "Average":
            _method = "Average"
        index = self._method.findText(_method)
        if index < 0:
            _logger.warning("fail to set method %s, unrecognized method: ", _method)
        else:
            self._method.setCurrentIndex(index)

    def setAbsortivity(self, value=True):
        _value = value
        if _value == "":
            _value = True
        self._absortivity.setChecked(_value)

    def setNanAndInf(self, value=True):
        _value = value
        if _value == "":
            _value = True
        self._removeNanInf.setChecked(_value)

    def requireAbsorptivity(self):
        return self._absortivity.isChecked()

    def removeNanAndInf(self):
        return self._removeNanInf.isChecked()

    def getDarks(self):
        if self._darksLE.text() == "":
            return None
        else:
            return self._darksLE.text()

    def setDarks(self, val):
        self._darksLE.setText(val)

    def getFlats(self):
        if self._flatsLE.text() == "":
            return None
        else:
            return self._flatsLE.text()

    def setFlats(self, val):
        self._flatsLE.setText(val)

    def getSecondFlats(self):
        if self._secondFlatsLE.text() == "":
            return None
        else:
            return self._secondFlatsLE.text()

    def setSecondFlats(self, val):
        self._secondFlatsLE.setText(val)

    def hasDarks(self):
        return self._darksLE.text() != ""

    def getDarkScale(self):
        if self.hasDarks() is False:
            return None
        else:
            return float(self._darkScaleSB.value())

    def setDarkScale(self, value):
        if value is not None:
            self._darkScaleSB.setValue(float(value))

    def resetDarkScale(self):
        self._darkScaleSB.setValue(1.0)

    def loadFromScan(self, scanID):
        try:
            flats, secondFlat = getFlats(scan=scanID)
            self.setFlats(flats or "")
            self.setSecondFlats(secondFlat or "")
            darkN = getDARK_N(scanID)
            if darkN is not None:
                self._darkScaleSB.setValue(1.0 / int(darkN))
            darkFile = getDark(scan=scanID)
            if darkFile is not None:
                self.setDarks(darkFile)
                # in this case dark is already normalized, set dark scale to 1.0
                if os.path.basename(darkFile) in ("dark.edf", "darkHST.edf"):
                    self.resetDarkScale()
        except Exception as error:
            _logger.error(error)


class _FFCWhenWidget(qt.QWidget):
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self._group = qt.QButtonGroup(parent=self)

        name = FFCWhen.on_the_fly.name.replace("_", " ")
        self._onTheFlyQRB = qt.QRadioButton(name, self)
        self._onTheFlyQRB.setToolTip(
            "process flat field correction during "
            "reconstruction. Avoid multiple io read."
        )
        self.layout().addWidget(self._onTheFlyQRB)
        self._group.addButton(self._onTheFlyQRB)

        name = FFCWhen.preprocessing.name.replace("_", " ")
        self._preProcQRB = qt.QRadioButton(name, self)
        self._preProcQRB.setToolTip(
            "make flat field on a preprocessing step. "
            "Can be interesting if you intend to test "
            "several reconstruction parameters"
        )
        self.layout().addWidget(self._preProcQRB)
        self._group.addButton(self._preProcQRB)

        # setting: default on the fly
        self._onTheFlyQRB.setChecked(True)

    def getWhen(self):
        if self._onTheFlyQRB.isChecked():
            return FFCWhen.on_the_fly
        elif self._preProcQRB.isChecked():
            return FFCWhen.preprocessing
        else:
            raise ValueError('No "when" defined')

    def setWhen(self, name):
        if isinstance(name, FFCWhen):
            if name is FFCWhen.on_the_fly:
                self._onTheFlyQRB.setChecked(True)
            elif name is FFCWhen.preprocessing:
                self._preProcQRB.setChecked(True)
            else:
                raise ValueError("FFCWhen type is not managed")
        elif type(name) is str:
            try:
                _name = name.split(".")[-1]
                #  name.split('.')[-1] because name can be given as FFCWhen.on_the_fly...
                _when_instance = getattr(FFCWhen, _name.lower().replace(" ", "_"))
            except Exception:
                _logger.error('fail to determine "FFCWhen" value from ', name)
            else:
                self.setWhen(_when_instance)
        else:
            raise ValueError("name should be a str or a FFCWhen")

    def forcePreprocessing(self, force_):
        old = self.blockSignals(True)
        if force_:
            self._preProcQRB.setChecked(True)
        self.setEnabled(not force_)
        self.blockSignals(old)


class CenteringTofuGroupBox(qt.QGroupBox):
    """
    Widget used to display centering information
    """

    def __init__(self, parent):
        qt.QGroupBox.__init__(self, "centering", parent)
        self.setLayout(qt.QGridLayout())
        self.layout().addWidget(qt.QLabel("x center", parent=self), 0, 0)
        self._xCenterLE = qt.QLineEdit("0", parent=self)
        validator = qt.QDoubleValidator(parent=self)
        self._xCenterLE.setValidator(validator)
        self.layout().addWidget(self._xCenterLE, 0, 1)

        self.layout().addWidget(qt.QLabel("y center", parent=self), 1, 0)
        self._yCenterLE = qt.QLineEdit("0", parent=self)
        self._yCenterLE.setValidator(validator)
        self.layout().addWidget(self._yCenterLE, 1, 1)

        self._lockButton = PadlockButton(parent=self)
        self._lockButton.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding
        )
        self.layout().addWidget(self._lockButton, 0, 2, 2, 2)

        # expose API
        self.isLocked = self._lockButton.isLocked

    def getXCenter(self):
        return float(self._xCenterLE.text())

    def setXCenter(self, value):
        self._xCenterLE.setText(str(value))

    def getZCenter(self):
        return float(self._yCenterLE.text())

    def setZCenter(self, value):
        self._yCenterLE.setText(str(value))

    def loadFromScan(self, scanID):
        if self.isLocked() is False:
            # can be set from Dim 1 and Dim 2
            # question: here to avoid interpolation we simply make an integer
            # division which give an integer
            dim1, dim2 = getDim1Dim2(scanID)
            for dim, lineEdit in zip((dim1, dim2), (self._xCenterLE, self._yCenterLE)):
                if dim is not None:
                    lineEdit.setText(str(int(dim / 2)))

            # try to set x center from the .par file
            try:
                parFile = os.path.join(scanID, os.path.basename(scanID) + ".par")
                if os.path.exists(parFile) is True:
                    params = getParametersFromParOrInfo(parFile)
                    rot_axis_pos = None
                    for k in ("ROTATION_AXIS_POS", "ROTATION_AXIS_POSITION"):
                        if k.lower() in params:
                            rot_axis_pos = params[k.lower()]

                    if rot_axis_pos is not None:
                        self._xCenterLE.setText(str(rot_axis_pos))
            except Exception as error:
                _logger.error(error)


class NbFilesWidget(qt.QWidget):
    """
    Widget to display the number of file (projection) to be send to tofu
    """

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent=parent)
        self.setLayout(qt.QGridLayout())
        self.layout().addWidget(qt.QLabel("number of files", parent=self), 0, 0)
        self._nFileLE = qt.QLineEdit("0", parent=self)
        validator = qt.QIntValidator()
        validator.setBottom(0)
        self._nFileLE.setValidator(validator)
        self.layout().addWidget(self._nFileLE, 0, 1)

    def setNumberOfFiles(self, n):
        self._nFileLE.setText(str(n))

    def getNumberOfFiles(self):
        if self._nFileLE.text().isdigit():
            return int(self._nFileLE.text())
        else:
            return 0


class AngleIllustrations(qt.QWidget):
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self.setContentsMargins(0, 0, 0, 0)
        self._infoLabel = qt.QLabel(parent=self)
        icon = icons.getQIcon("information")
        self._infoLabel.setPixmap(icon.pixmap(qt.QSize(32, 32)))
        self.layout().addWidget(self._infoLabel)

        self.illustrationCB = qt.QComboBox(parent=self)
        self.illustrationCB.addItem("lamino angle")
        self.illustrationCB.addItem(PSI_CHAR + " angle")
        self.layout().addWidget(self.illustrationCB)

        self._illustrations = qt.QWidget(parent=self)
        self._illustrations.setLayout(qt.QHBoxLayout())
        self.layout().addWidget(self._illustrations)
        self._laminoAngleIllustration = _IllustrationWidget(
            parent=self, img="lamino_angle"
        )
        self._psiAngleIllustration = _IllustrationWidget(parent=self, img="psi_angle")
        self._illustrations.setMinimumSize(qt.QSize(200, 200))
        self._illustrations.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding
        )

        self._illustrations.setContentsMargins(0, 0, 0, 0)
        self._illustrations.layout().setSpacing(0)
        self._illustrations.layout().addWidget(self._laminoAngleIllustration)
        self._illustrations.layout().addWidget(self._psiAngleIllustration)
        self.layout().addWidget(self._illustrations)
        self.setActiveIllustration("lamino angle")
        self.illustrationCB.currentIndexChanged[str].connect(self.setActiveIllustration)

    def setActiveIllustration(self, name):
        assert name in ("lamino angle", PSI_CHAR + " angle", THETA_CHAR + " angle")
        if name == THETA_CHAR + " angle":
            _logger.info("No illustration of the delta angle for the moment")
            return
        self.blockSignals(True)
        index = self.illustrationCB.findText(name)
        assert index >= 0
        self.illustrationCB.setCurrentIndex(index)

        self._laminoAngleIllustration.setVisible(name == "lamino angle")
        self._psiAngleIllustration.setVisible(name == PSI_CHAR + " angle")

        self.blockSignals(False)


class RotationAngleGroupBox(qt.QGroupBox):
    def __init__(self, parent):
        qt.QGroupBox.__init__(self, "angles", parent)
        self.setLayout(qt.QHBoxLayout())

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self._angles = qt.QWidget(parent=self)
        self._angles.setLayout(qt.QVBoxLayout())
        self._angles.setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._angles)

        self._laminoAngle = _AngleWidget(
            parent=self._angles,
            name="rotation axis tilt",
            defaultVal=90,
            lockable=True,
            information=self._showLaminoAngleInfo,
        )
        self._angles.layout().addWidget(self._laminoAngle)
        self._axisAngleY = _AngleWidget(
            parent=self._angles,
            name=(PSI_CHAR + " angle"),
            lockable=True,
            information=self._showPsiAngleInfo,
        )
        self._angles.layout().addWidget(self._axisAngleY)

        self._axisAngleZ = _AngleWidget(
            parent=self._angles, name=(THETA_CHAR + " angle"), lockable=True
        )
        self._angles.layout().addWidget(self._axisAngleZ)
        self._axisAngleZ.setVisible(False)

        self._overallAngle = _AngleWidget(
            parent=self, name="overall angle", defaultVal=360, lockable=True
        )
        self._angles.layout().addWidget(self._overallAngle)

        self._spacer = qt.QWidget(parent=self._angles)
        self._spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self._angles.layout().addWidget(self._spacer)

        self._infoLamino = None
        self._infoPsi = None

        # expose some API
        self.getLaminoAngle = self._laminoAngle.getAngle
        self.getPsiAngle = self._axisAngleY.getAngle

    def _showLaminoAngleInfo(self):
        self.getInfoLaminoDialog().show()
        self.getInfoLaminoDialog().raise_()
        self.getInfoLaminoDialog().activateWindow()

    def _showPsiAngleInfo(self):
        self.getPsiLaminoDialog().show()
        self.getPsiLaminoDialog().raise_()
        self.getPsiLaminoDialog().activateWindow()

    def getInfoLaminoDialog(self):
        if self._infoLamino is None:
            self._infoLamino = _IllustrationDialog(
                parent=self, img="lamino_angle", title="information about lamino angle"
            )
        return self._infoLamino

    def getPsiLaminoDialog(self):
        if self._infoPsi is None:
            self._infoPsi = _IllustrationDialog(
                parent=self,
                img="psi_angle",
                title=" ".join(("information about", PSI_CHAR, "angle")),
            )
        return self._infoPsi

    def loadFromScan(self, scanID):
        assert type(scanID) is str
        _info_file = os.path.join(scanID, os.path.basename(scanID) + ".info")
        if os.path.isfile(_info_file) is True:
            info = getParametersFromParOrInfo(_info_file)
            if self._laminoAngle.isLocked() is False and "ctangle" in info:
                self._laminoAngle.setAngle(90.0 - float(info["ctangle"]))
            if self._overallAngle.isLocked() is False and "scanrange" in info:
                self._overallAngle.setAngle(float(info["scanrange"]))

    def _setOverallAngleI(self, val):
        """
        Set the inverse value to the lamino angle

        :param val:
        :return:
        """
        _val = float(val) * -1.0
        self._overallAngle.setAngle(_val)


class PhaseRetrievalWidget(_TofuOptionLoader, qt.QGroupBox):
    """
    Widget sued to defined the phase retrieval
    """

    activated = qt.Signal()
    """Emitted when the phase retrieval is activated"""

    METHODS = "tie", "ctf", "ctfhalfsin", "qp", "qphalfsine", "qp2"
    DEFAULT_METHOD = "tie"

    def __init__(self, parent):
        qt.QGroupBox.__init__(self, "phase retrieval (*)", parent)
        self.setToolTip("Activating phase retrieval will deactivate " "absorptivity")
        self.setLayout(qt.QGridLayout())
        # retrieval method
        self._retrievalMethodCB = qt.QComboBox(parent=self)
        for _method in self.METHODS:
            self._retrievalMethodCB.addItem(_method)
        assert self.DEFAULT_METHOD in self.METHODS
        self._retrievalMethodCB.setCurrentIndex(
            self._retrievalMethodCB.findText(self.DEFAULT_METHOD)
        )
        self.layout().addWidget(qt.QLabel("retrieval method:", self), 0, 0)
        self.layout().addWidget(self._retrievalMethodCB, 0, 1)

        # energy
        self.layout().addWidget(qt.QLabel("energy:", self), 1, 0)
        self._energy = qt.QLineEdit("65.0", parent=self)
        validator = qt.QDoubleValidator(parent=self._energy)
        self._energy.setValidator(validator)
        self.layout().addWidget(self._energy, 1, 1)
        self._energyLockButton = PadlockButton(parent=self)
        self.layout().addWidget(self._energyLockButton, 1, 2)

        # regularization rate
        self.layout().addWidget(qt.QLabel("regularization rate:", self), 3, 0)
        self._regularizationRate = qt.QLineEdit("1.5", parent=self)
        validator = qt.QDoubleValidator(parent=self._regularizationRate)
        self._regularizationRate.setValidator(validator)
        self.layout().addWidget(self._regularizationRate, 3, 1)
        self._regRateLockButton = PadlockButton(parent=self)
        self.layout().addWidget(self._regRateLockButton, 3, 2)

        # thresholding rate
        self.layout().addWidget(qt.QLabel("thresholding rate:", self), 4, 0)
        self._thresholdingRate = qt.QLineEdit("0.4", parent=self)
        validator = qt.QDoubleValidator(parent=self._thresholdingRate)
        self._thresholdingRate.setValidator(validator)
        self.layout().addWidget(self._thresholdingRate, 4, 1)

        # propagation distance
        self.layout().addWidget(qt.QLabel("propagation distance (m):", self), 5, 0)
        self._propagationDistance = qt.QLineEdit("0.08", parent=self)
        validator = qt.QDoubleValidator(parent=self._propagationDistance)
        self._propagationDistance.setValidator(validator)
        self.layout().addWidget(self._propagationDistance, 5, 1)
        self._propaDistLockButton = PadlockButton(parent=self)
        self.layout().addWidget(self._propaDistLockButton, 5, 2)

        # create some more speaking API
        self.energyIsLocked = self._energyLockButton.isLocked
        self.getRetrievalMethod = self._retrievalMethodCB.currentText
        self.propaDistIsLocked = self._propaDistLockButton.isLocked

        # signal/slot connection
        self.toggled.connect(self.__toggleCallback)

        options = {
            "retrieval-method": _getterSetter(
                getter=self._getRetrievalMethod, setter=self.setRetrievalMethod
            ),
            "energy": _getterSetter(getter=self._getEnergy, setter=self.setEnergy),
            "propagation-distance": _getterSetter(
                getter=self._getPropagationDistance, setter=self.setPropagationDistance
            ),
            "regularization-rate": _getterSetter(
                getter=self._getRegularizationRate, setter=self.setRegularizationRate
            ),
            "thresholding-rate": _getterSetter(
                getter=self._getThresholdingRate, setter=self.setThresholdingRate
            ),
        }
        _TofuOptionLoader.__init__(self, options=options)

    def loadFromScan(self, scanID):
        _info_file = os.path.join(scanID, os.path.basename(scanID) + ".info")
        if os.path.isfile(_info_file) is True:
            energy = getClosestEnergy(scanID)
            if energy is not None and self.energyIsLocked() is False:
                self.setEnergy(energy)
            info = getParametersFromParOrInfo(_info_file)
            if "distance" in info and self.propaDistIsLocked() is False:
                try:
                    dst = float(info["distance"])
                    # convert to meter
                    dst = dst / 1000.0
                    self.setPropagationDistance(dst)
                except Exception:
                    pass

    def setUnchecked(self):
        self.setChecked(False)

    def __toggleCallback(self, checked):
        if checked is True:
            self.activated.emit()

    # retrieval method
    def _getRetrievalMethod(self):
        if self.isChecked() is True:
            return self.getRetrievalMethod()
        else:
            return None

    def setRetrievalMethod(self, method):
        if method is not None:
            if method not in self.METHODS:
                _logger.error("method %s is not recognized as a retrieval " "method")
            else:
                index = self._retrievalMethodCB.find(method)
                self._retrievalMethodCB.setCurrentIndex(index)

    # energy
    def getEnergy(self):
        return float(self._energy.text())

    def _getEnergy(self):
        "Return None if not activated, otherwise the value"
        if self.isChecked() is True:
            return self.getEnergy()

    def setEnergy(self, energy):
        if energy is not None:
            self._energy.setText(str(energy))

    # propagation distance
    def getPropagationDistance(self):
        return float(self._propagationDistance.text())

    def _getPropagationDistance(self):
        if self.isChecked() is True:
            return self.getPropagationDistance()
        else:
            return None

    def setPropagationDistance(self, distance):
        if distance is not None:
            self._propagationDistance.setText(str(distance))

    # regularization rate
    def getRegularizationRate(self):
        return float(self._regularizationRate.text())

    def _getRegularizationRate(self):
        if self.isChecked() is True:
            return self.getRegularizationRate()
        else:
            return None

    def setRegularizationRate(self, rate):
        if rate is not None:
            self._regularizationRate.setText(str(rate))

    # thresholding rate
    def getThresholdingRate(self):
        return float(self._thresholdingRate.text())

    def _getThresholdingRate(self):
        if self.isChecked() is True:
            return self.getThresholdingRate()
        else:
            return None

    def setThresholdingRate(self, rate):
        if rate is not None:
            self._thresholdingRate.setText(str(rate))
