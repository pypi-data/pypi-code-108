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
__date__ = "08/02/2017"

"""Module defining the dition of a single H5Struct"""

import logging
from tomwer.gui.reconstruction.ftserie.h5editor import H5StructsEditor

logger = logging.getLogger(__name__)


class H5StructEditor(H5StructsEditor):
    """simple class which link an interface with an h5 struct used for pyhst"""

    def __init__(self, structID):
        self.structID = structID
        H5StructsEditor.__init__(self, (self.structID,))

    def linkComboboxWithH5Variable(
        self,
        qcombobox,
        h5ParamName,
        fitwithindex=False,
        dic=None,
        filters=None,
        setDefault=True,
    ):
        """

        :param qcombobox: the QCombobox in the interface to edit/display the
            given h5ParamName
        :param h5ParamName: the parameter ID in the H5 structure.
        :param fitwithindex: true if we want to store the index in the h5File,
            otherwise store the string
        :param filters: filter to apply on the string to get the requested
            value
        """
        return H5StructsEditor.linkComboboxWithH5Variable(
            self,
            qcombobox=qcombobox,
            structID=self.structID,
            h5ParamName=h5ParamName,
            fitwithindex=fitwithindex,
            dic=dic,
            filters=filters,
            setDefault=setDefault,
        )

    def linkCheckboxWithH5Variable(self, qcheckbox, h5ParamName, invert=False):
        """

        :param qcheckbox: the QCheckBox in the interface to edit/display the
            given h5ParamName
        :param h5ParamName: the parameter ID in the H5 structure.
        :param invert: true if we will not store the value state == checked but
            state == unchecked
        :param structID: the structID associated with the param ID
        """
        return H5StructsEditor.linkCheckboxWithH5Variable(
            self,
            qcheckbox=qcheckbox,
            structID=self.structID,
            h5ParamName=h5ParamName,
            invert=invert,
        )

    def LinkLineEditWithH5Variable(self, qlineedit, h5ParamName, h5paramtype=str):
        """

        :param qlineedit: the QLineEdit in the interface to edit/display the
            given h5ParamName
        :param h5ParamName: the parameter ID in the H5 structure.
        :param h5ParamName: the parameter ID in the H5 structure.
        """
        return H5StructsEditor.LinkLineEditWithH5Variable(
            self,
            qlineedit=qlineedit,
            h5ParamName=h5ParamName,
            structID=self.structID,
            h5paramtype=h5paramtype,
        )

    def LinkSelectionLineEditWithH5Variable(
        self, qlineedit, h5ParamName, h5paramtype=str
    ):
        """

        :param qlineedit: the QLineEdit in the interface to edit/display the
            given h5ParamName
        :param h5ParamName: the parameter ID in the H5 structure.
        :param h5ParamName: the parameter ID in the H5 structure.
        """
        return H5StructsEditor.LinkSelectionLineEditWithH5Variable(
            self,
            qlineedit=qlineedit,
            h5ParamName=h5ParamName,
            structID=self.structID,
            h5paramtype=h5paramtype,
        )

    def linkGroupWithH5Variable(self, group, h5ParamName, getter, setter):
        return H5StructsEditor.linkGroupWithH5Variable(
            self,
            group=group,
            structID=self.structID,
            h5ParamName=h5ParamName,
            getter=getter,
            setter=setter,
        )
