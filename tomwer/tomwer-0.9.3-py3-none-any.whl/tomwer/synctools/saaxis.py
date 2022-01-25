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
from tomwer.core.process.reconstruction.saaxis.params import SAAxisParams
import logging

logger = logging.getLogger(__name__)


class QSAAxisParams(SAAxisParams, qt.QObject):

    sigChanged = qt.Signal()
    """Signal emitted when at least one element of the dictionary change"""

    sigAxisUrlChanged = qt.Signal()
    """Signal emitted when the axis url change"""

    def __init__(self):
        qt.QObject.__init__(self)
        SAAxisParams.__init__(self)

    def changed(self):
        self.sigChanged.emit()

    def axis_urls_changed(self):
        self.sigAxisUrlChanged.emit()
