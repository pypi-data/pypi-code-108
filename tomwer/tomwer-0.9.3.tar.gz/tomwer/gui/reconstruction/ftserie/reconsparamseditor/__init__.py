# /*##########################################################################
# Copyright (C) 2016-2017 European Synchrotron Radiation Facility
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

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "09/02/2017"

from silx.gui import qt
from tomwer.gui.reconstruction.ftserie.reconsparamseditor.beamgeowidget import (
    BeamGeoWidget,
)
from tomwer.gui.reconstruction.ftserie.reconsparamseditor.displaywidget import (
    DisplayWidget,
)
from tomwer.gui.reconstruction.ftserie.reconsparamseditor.expertwidget import (
    ExpertWidget,
)
from tomwer.gui.reconstruction.ftserie.reconsparamseditor.ftwidget import FTWidget
from tomwer.gui.reconstruction.ftserie.reconsparamseditor.paganinwidget import (
    PaganinWidget,
    PaganinRangeWidget,
)
from tomwer.gui.reconstruction.ftserie.reconsparamseditor.pyhstwidget import PyHSTWidget

import logging
from tomwer.core.octaveh5editor import OctaveH5Editor
from tomwer.gui.reconstruction.ftserie.reconsparamseditor.ftaxiswidget import (
    FTAxisWidget,
)
from tomwer.gui.reconstruction.ftserie.h5editor.h5structseditor import H5StructsEditor
from tomwer.gui.reconstruction.ftserie.reconsparamseditor.dkrfwidget import DKRFWidget
from tomwer.synctools.ftseries import QReconsParams

logger = logging.getLogger(__name__)


class ReconsParamsEditor(OctaveH5Editor, qt.QTabWidget):
    """
    Build the Widget allowing edition of the fields of the h5 file.

    :param QObject parent: the QObject parent
    :param reconsparams: reconstruction parameters edited by the widget
    """

    def __init__(self, parent=None, reconsparams=None):
        qt.QTabWidget.__init__(self, parent)
        OctaveH5Editor.__init__(self)
        self.reconsparams = reconsparams or QReconsParams()

        self.__buildGUI()
        self._isLoading = False
        self.loadReconsParams(recons_params=self.reconsparams)

    def __buildGUI(self):
        self._mainWidget = FTWidget(reconsparams=self.reconsparams.ft, parent=self)
        self.addTab(self._mainWidget, "Main")

        self._displayWidget = DisplayWidget(
            reconsparams=self.reconsparams.ft, parent=self
        )
        self.addTab(self._displayWidget, "Display")

        self._axisWidget = FTAxisWidget(reconsparams=self.reconsparams, parent=self)
        # for now keep the ftseries as it was previously
        self.addTab(self._axisWidget, "Axis")

        self._PaganinWidget = self._getPaganinWidget()
        self.addTab(self._PaganinWidget, "Paganin")

        self._PyHSTWidget = PyHSTWidget(
            reconsparams=self.reconsparams.pyhst, parent=self
        )
        self.addTab(self._PyHSTWidget, "PyHST")

        self._beamGeoWidget = BeamGeoWidget(
            reconsparams=self.reconsparams.beam_geo, parent=self
        )
        self.addTab(self._beamGeoWidget, "Geometry")

        self._dkRefWidget = DKRFWidget(reconsparams=self.reconsparams.dkrf, parent=self)
        # self.addTab(self._dkRefWidget, 'Dark and refs')

        # hide dkref widget which is not needed anymore
        self._dkRefWidget.hide()

        self._expertWidget = ExpertWidget(
            reconsparams=self.reconsparams.ft, parent=self
        )
        self.addTab(self._expertWidget, "Expert")

        self._otherWidget = OtherWidget(reconsparams=self.reconsparams, parent=self)
        self.addTab(self._otherWidget, "Other")

        self._axisWidget._qcbHalfAcq.toggled.connect(
            self._mainWidget._enableVolumeSelection
        )

    def setReconsParams(self, recons_params):
        if recons_params is None:
            return

        self.reconsparams = recons_params
        assert isinstance(recons_params, QReconsParams)
        for widget in (
            self._mainWidget,
            self._displayWidget,
            self._axisWidget,
            self._PaganinWidget,
            self._PyHSTWidget,
            self._beamGeoWidget,
            self._dkRefWidget,
            self._expertWidget,
            self._otherWidget,
        ):
            widget.setReconsParams(recons_params=self.reconsparams)

        self.loadReconsParams(recons_params=self.reconsparams)

    def _getPaganinWidget(self):
        return PaganinWidget(parent=self, reconsparams=self.reconsparams.paganin)

    # implementation of OctaveH5Editor function
    def getStructs(self):
        structs = {}
        for itab in range(self.count()):
            widgetStructs = self.widget(itab).getStructs()
            for structID in widgetStructs:
                if structID not in structs:
                    structs[structID] = {}
                structs[structID].update(widgetStructs[structID])

        return structs

    def loadReconsParams(self, recons_params):
        """Load the H5File amd update all the widgets."""
        assert isinstance(recons_params, QReconsParams)
        # self._recons_params.load(recons_params)
        if self._isLoading is True:
            return
        self._isLoading = True
        OctaveH5Editor.loadReconsParams(self, recons_params)
        tabs = (
            self._mainWidget,
            self._displayWidget,
            self._axisWidget,
            self._PaganinWidget,
            self._PyHSTWidget,
            self._beamGeoWidget,
            self._expertWidget,
            self._dkRefWidget,
            self._otherWidget,
        )

        for tab in tabs:
            tab.load(recons_params)
        self._isLoading = False

    def isParamH5Managed(self, structID, parameter):
        """

        :param str structID: ID of the h5 group
        :param str parameter: name of the parameter

        :return bool: true if one of the tab widget is dealing with the couple
            structID/parameter
        """
        for itab in range(self.count()):
            if self.widget(itab).isParamH5Managed(structID, parameter):
                return True

        return False

    def setScan(self, scan):
        """The scan actually display. Need to show some radio for example in
        the 'on radio' option"""
        self._mainWidget.setScan(scan=scan)
        self._axisWidget.setScan(scan=scan)


class OtherWidget(H5StructsEditor, qt.QScrollArea):
    """
    Group all h5 parameter which doesn't fit to any other widget.

    .. warning: this widget can execute only one load. If multiple load please
                recreate this widget each time.
    """

    def __init__(self, parent=None, reconsparams=None):
        qt.QScrollArea.__init__(self, parent=None)
        H5StructsEditor.__init__(self)
        self.setLayout(qt.QVBoxLayout())
        self.widgetsGroup = {}  # create one group per structure
        self.paramType = {}
        self._recons_params = None
        self.setReconsParams(recons_params=reconsparams)

    def setReconsParams(self, recons_params):
        assert isinstance(recons_params, QReconsParams)
        _recons_params = recons_params

        if self._recons_params:
            self._recons_params.sigChanged.disconnect(self._update_params)
        self._recons_params = _recons_params
        self.load(self._recons_params)
        self._recons_params.sigChanged.connect(self._update_params)

    def clear(self):
        for st in self.paramToWidget:
            for _widget in self.paramToWidget[st].values():
                _widget.parent().layout().removeWidget(_widget)
                # TODO: delete ?

            grp = self.widgetsGroup[st]
            self.layout().removeWidget(grp)

        self.widgetsGroup.clear()
        self.paramType.clear()
        H5StructsEditor.clear(self)

    def _update_params(self):
        """Update all parameter"""
        self.load(self._recons_params)

    def load(self, recons_params):
        assert isinstance(recons_params, QReconsParams)
        structures = recons_params.unmanaged_params_tree()
        self.clear()

        assert isinstance(structures, dict)
        for st in structures:
            assert st not in self.widgetsGroup
            self.widgetsGroup[st] = qt.QGroupBox(title=st, parent=self)
            self.widgetsGroup[st].setLayout(qt.QVBoxLayout())
            # add the group to the main widget
            self.layout().addWidget(self.widgetsGroup[st])
            self.paramToWidget[st] = {}
            self.paramType[st] = {}
            self.structsManaged[st] = []
            for param in structures[st]:
                widget = qt.QWidget(parent=self.widgetsGroup[st])
                widget.setLayout(qt.QHBoxLayout())
                # add the widget ot the group box
                self.widgetsGroup[st].layout().addWidget(widget)

                widget.layout().addWidget(qt.QLabel(param, parent=widget))

                self.paramType[st][param] = type(structures[st][param])
                widgetEditor = qt.QLineEdit(
                    parent=widget, text=str(structures[st][param])
                )
                widgetEditor.editingFinished.connect(self._atLeastOneParamChanged)

                self.paramToWidget[st][param] = widgetEditor
                self.structsManaged[st].append(param)
                widget.layout().addWidget(widgetEditor)

        self.spacer = qt.QWidget(self)
        self.spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(self.spacer)

    def getParamValue(self, structID, paramID):
        if not self.isParamH5Managed(structID, paramID):
            return None
        else:
            value = self.paramToWidget[structID][paramID].text()
            return self.paramType[structID][paramID](value)

    # inheritance of H5StructsEditor
    def getStructs(self):
        """

        :return: dict of managed struct
        """
        structs = {}
        for st in self.paramToWidget:
            structs[st] = {}
            for param in self.paramToWidget[st]:
                structs[st][param] = self.getParamValue(st, param)
        return structs

    def _atLeastOneParamChanged(self):
        for st in self.paramToWidget:
            for param in self.paramToWidget[st]:
                value = self.getParamValue(st, param)
                self._reconsParams.setValue(structID=st, paramID=param, value=value)


class ReconsParamSetEditor(ReconsParamsEditor):
    """
    Edit reconstruction parameters but those can have several values
    """

    def _getPaganinWidget(self):
        return PaganinRangeWidget(parent=self, reconsparams=self.reconsparams.paganin)

    def getReconsParamSet(self):
        return self.reconsparams.to_unique_recons_set()
