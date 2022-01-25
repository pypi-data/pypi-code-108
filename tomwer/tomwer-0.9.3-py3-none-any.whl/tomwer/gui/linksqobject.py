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

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "14/03/2017"

"""Module linking QtObjects with an Octave reconstruction parameter from a
specific H5StructEditor"""


class LinkQObject:
    """Class used to store the QObject associated to an H5 parameter"""

    def __init__(self, qobject):
        self.qobject = qobject


class LinkComboBox(LinkQObject):
    """
    Class used to store the Combobox associated to an H5 parameter

    :param qcombobox: the QCombobox in the interface to edit/display the
        given h5ParamName
    :param h5ParamName: the parameter ID in the H5 structure.
    :param fitwithindex: true if we want to store the index in the h5File,
        otherwise store the string
    :param dic: if not None then instead for storing index or string we will
        store the associated value with this key. Keys are the one displayed in
        the QComboBox, values the one in the H5file
    :param filters: filter to apply on the combobox value to get the requested
        value (only apply on load/getting values)
    :param setDefault: if value to set not found in the existing values then
        set the default value, If False add the value to the QComboBox
    """

    def __init__(
        self, qcombobox, fitwithindex, dic=None, filters=None, setDefault=True
    ):
        LinkQObject.__init__(self, qcombobox)
        assert dic is None or type(dic) is dict
        # filter only apply if we want to get the combobox value
        assert filters is None or fitwithindex is False
        self.fitwithindex = fitwithindex
        self.dicCBtoH5 = dic
        self.dicH5ToCB = dict((v, k) for k, v in iter(dic.items())) if dic else None
        self.filters = filters
        self.setDefault = setDefault


class LinkCheckBox(LinkQObject):
    """
    Class used to store the QCheckBox associated to an H5 parameter

    :param qcheckbox: the QCheckBox in the interface to edit/display the
        given h5ParamName
    :param h5ParamName: the parameter ID in the H5 structure.
    :param invert: true if we will not store the value state == checked but
        state == unchecked
    """

    def __init__(self, qcheckbox, invert):
        LinkQObject.__init__(self, qcheckbox)
        self.invert = invert


class LinkLineEdit(LinkQObject):
    """
    Class used to store the QCheckBox associated to an H5 parameter

    :param qlineedit: the QCheckBox in the interface to edit/display the
        given h5ParamName
    :param h5ParamName: the parameter ID in the H5 structure.
    :param h5paramtype: Define the type of the output value
    """

    def __init__(self, qlineedit, h5paramtype):
        LinkQObject.__init__(self, qlineedit)
        self.h5paramtype = h5paramtype


class LinkSelLineEdit(LinkQObject):
    """
    Class used to store the QCheckBox associated to an H5 parameter

    :param qlineedit: the QCheckBox in the interface to edit/display the
        given h5ParamName
    :param h5ParamName: the parameter ID in the H5 structure.
    :param h5paramtype: Define the type of the output value
    """

    def __init__(self, qlineedit, h5paramtype):
        LinkQObject.__init__(self, qlineedit)
        self.h5paramtype = h5paramtype


class LinkGroup(LinkQObject):
    """
    Class used to store an H5 reconstruction parameter with a simple getter and
    setter to call

    :param qlineedit: the QCheckBox in the interface to edit/display the
        given h5ParamName
    :param h5ParamName: the parameter ID in the H5 structure.
    :param setter: the function to set the variable in the GUI
    :param getter: the function to get the variable value
    """

    def __init__(self, group, getter, setter):
        LinkQObject.__init__(self, group)
        self.getter = getter
        self.setter = setter
