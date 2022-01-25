# coding: utf-8
###########################################################################
# Copyright (C) 2016-2019 European Synchrotron Radiation Facility
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
#############################################################################

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "03/05/2019"


from silx.gui import qt
from tomwer.core.process.reconstruction.ftseries.params import (
    ReconsParams,
    beamgeo,
    axis,
    paganin,
)
from tomwer.core.process.reconstruction.ftseries.params import pyhst, ft
from tomwer.core.process.reconstruction.darkref import params as dkrf

import logging

logger = logging.getLogger(__name__)


class _QAxisRP(axis.AxisRP, qt.QObject):

    sigChanged = qt.Signal()
    """Signal emitted when at least one element of the dictionary change"""

    def __init__(self):
        qt.QObject.__init__(self)
        axis.AxisRP.__init__(self)

    def changed(self):
        self.sigChanged.emit()


class _QBeamGeoRP(beamgeo.BeamGeoRP, qt.QObject):

    sigChanged = qt.Signal()
    """Signal emitted when at least one element of the dictionary change"""

    def __init__(self):
        qt.QObject.__init__(self)
        beamgeo.BeamGeoRP.__init__(self)

    def changed(self):
        self.sigChanged.emit()


class _QDKRFRP(dkrf.DKRFRP, qt.QObject):

    sigChanged = qt.Signal()
    """Signal emitted when at least one element of the dictionary change"""

    def __init__(self):
        qt.QObject.__init__(self)
        dkrf.DKRFRP.__init__(self)

    def changed(self):
        self.sigChanged.emit()


class _QFTRP(ft.FTRP, qt.QObject):

    sigChanged = qt.Signal()
    """Signal emitted when at least one element of the dictionary change"""

    def __init__(self):
        qt.QObject.__init__(self)
        ft.FTRP.__init__(self)

    def changed(self):
        self.sigChanged.emit()


class _QPaganinRP(paganin.PaganinRP, qt.QObject):

    sigChanged = qt.Signal()
    """Signal emitted when at least one element of the dictionary change"""

    def __init__(self):
        qt.QObject.__init__(self)
        paganin.PaganinRP.__init__(self)

    def changed(self):
        self.sigChanged.emit()


class _QPyhstRP(pyhst.PyhstRP, qt.QObject):

    sigChanged = qt.Signal()
    """Signal emitted when at least one element of the dictionary change"""

    def __init__(self):
        qt.QObject.__init__(self)
        pyhst.PyhstRP.__init__(self)

    def changed(self):
        self.sigChanged.emit()


class QReconsParams(ReconsParams, qt.QObject):

    sigChanged = qt.Signal()
    """Signal emitted when at least one element of the dictionary change"""

    def __init__(self, empty=False):
        ReconsParams.__init__(self, empty=empty)
        qt.QObject.__init__(self)

        # connect signal / Slot
        if self._ft:
            self._ft.sigChanged.connect(self.changed)
        if self._pyhst:
            self._pyhst.sigChanged.connect(self.changed)
        if self.axis:
            self._axis.sigChanged.connect(self.changed)
        if self.paganin:
            self._paganin.sigChanged.connect(self.changed)
        if self.beam_geo:
            self._beam_geo.sigChanged.connect(self.changed)
        if self.dkrf:
            self._dkrf.sigChanged.connect(self.changed)

    def _createSubParamsSet(self, empty):
        self._ft = None if empty else _QFTRP()
        self._pyhst = None if empty else _QPyhstRP()
        self._axis = None if empty else _QAxisRP()
        self._paganin = None if empty else _QPaganinRP()
        self._beam_geo = None if empty else _QBeamGeoRP()
        self._dkrf = None if empty else _QDKRFRP()

    def changed(self):
        self.sigChanged.emit()

    def _copy_ft_rp(self, other_rp):
        create_connection = self.ft is None
        ReconsParams._copy_ft_rp(self, other_rp=other_rp)
        if create_connection:
            self._ft.sigChanged.connect(self.changed)

    def _copy_pyhst_rp(self, other_rp):
        create_connection = self.pyhst is None
        ReconsParams._copy_pyhst_rp(self, other_rp=other_rp)
        if create_connection:
            self._pyhst.sigChanged.connect(self.changed)

    def _copy_axis_rp(self, other_rp):
        create_connection = self.axis is None
        ReconsParams._copy_axis_rp(self, other_rp=other_rp)
        if create_connection:
            self._axis.sigChanged.connect(self.changed)

    def _copy_paganin_rp(self, other_rp):
        create_connection = self.paganin is None
        ReconsParams._copy_paganin_rp(self, other_rp=other_rp)
        if create_connection:
            self._paganin.sigChanged.connect(self.changed)

    def _copy_beam_geo_rp(self, other_rp):
        create_connection = self.beam_geo is None
        ReconsParams._copy_beam_geo_rp(self, other_rp=other_rp)
        if create_connection:
            self._beam_geo.sigChanged.connect(self.changed)

    def _copy_dkrf_rp(self, other_rp):
        create_connection = self.dkrf is None
        ReconsParams._copy_dkrf_rp(self, other_rp=other_rp)
        if create_connection:
            self._dkrf.sigChanged.connect(self.changed)
