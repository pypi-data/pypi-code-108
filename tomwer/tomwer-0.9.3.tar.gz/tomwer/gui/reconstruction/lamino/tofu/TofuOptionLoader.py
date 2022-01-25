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


from collections import namedtuple

_getterSetter = namedtuple("_getterSetter", ["getter", "setter"])


class _TofuOptionLoader(object):
    """Simple class used to register the options managed by a TofuXWidget"""

    def __init__(self, options, childs=None):
        self._options = options
        self._childs = childs or []
        # expose API
        self._addChild = self._childs.append

    def _hasOption(self, option):
        return option in self._options

    def _setOption(self, option, value):
        assert option in self._options
        if value == "":
            self._options[option].setter()
        else:
            self._options[option].setter(value)

    def getParameters(self):
        """Add the value of the detain options + some extra parameters to be
        passed as 'free string'

        :return:
        :rtype: tuple (dict, list)
        """
        _ddict, extraParams = self._getNodeParameters()
        for child in self._childs:
            _childDict = child.getParameters()
            _ddict.update(_childDict)
        return _ddict

    def _getNodeParameters(self):
        """Add the value of the detain options + some extra parameters to be
        passed as 'free string'

        :return:
        :rtype: tuple (dict, list)
        """
        _ddict = {}
        for option in self._options:
            _ddict[option] = self._options[option].getter()
        return _ddict, []

    def setParameters(self, _ddict):
        """

        :param _ddict:
        :return: initial dictionary less the parameters managed by this option
                 loader
         :rtype dict:
        """
        _lddict = _ddict.copy()
        for child in self._childs:
            _lddict = child.setParameters(_lddict)
        _lddict = self._setNodeParameters(_lddict)
        return _lddict

    def _setNodeParameters(self, _ddict):
        """

        :param _ddict:
        :return: initial dictionary less the parameters managed by this option
                 loader
         :rtype dict:
        """
        updatedDict = _ddict.copy()
        for param, value in _ddict.items():
            if param in self._options:
                self._options[param].setter(value)
                del updatedDict[param]
        return updatedDict
