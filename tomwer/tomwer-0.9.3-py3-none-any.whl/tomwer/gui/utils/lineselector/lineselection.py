# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
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
__date__ = "25/09/2017"

import re
import numpy

SELECTION_PATTERN = re.compile(r"\d?[:]?\d?")


def selectionIsValid(selection):
    """
    Return true if the given selection as a string is valid

    :return: bool
    """
    assert type(selection) is str
    _selection = selection.replace(" ", "")
    selections = _selection.split(";")
    for sel in selections:
        if not re.match(SELECTION_PATTERN, sel):
            return False
    return True


def getSelection(projections, selection):
    """

    :param str selection:
    :return numpy.ndarray:
    """

    def evalSelection(projections, sel):
        assert type(projections) is numpy.ndarray
        return eval("projections[" + sel + "]")

    assert type(selection) is str
    if selection == "":
        return projections
    _selection = selection.replace(" ", "")
    selections = _selection.split(";")
    if len(selections) == 1:
        return evalSelection(projections, selection)
    else:
        res = None
        for iSel, sel in enumerate(range(len(selections))):
            if iSel == 0:
                res = evalSelection(projections, selections[iSel])
            else:
                res = numpy.append(res, evalSelection(projections, selections[iSel]))
        return res
