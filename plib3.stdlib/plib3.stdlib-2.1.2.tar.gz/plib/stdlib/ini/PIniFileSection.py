#! /usr/bin/env python3
"""
Module PIniFileSection
Sub-Package STDLIB.INI of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``PIniFileSection`` class.
"""

import collections

from .PIniFileOption import PIniFileOption


class PIniFileSection(object):
    """OS-independent class for preferences section with multiple options.
    
    Section has a name and a dictionary of names (keys) vs.
    PIniFileOption instances. Expects to be given a PIniFileInterface
    instance to read or write its options.
    """
    
    # The option class can be changed by resetting this class field.
    _optclass = PIniFileOption
    
    def __init__(self, sname):
        object.__init__(self)
        self.sectname = sname
        self.options = collections.OrderedDict()
    
    def addoption(self, oname, vtype, adefault):
        self.options[oname] = self._optclass(oname, vtype, adefault)
    
    def getvalue(self, oname):
        if oname in self.options:
            return self.options[oname].getvalue()
        else:
            return None
    
    def setvalue(self, oname, avalue):
        if oname in self.options:
            self.options[oname].setvalue(avalue)
    
    def read(self, intf):
        intf.opensection(self.sectname)
        for oname in self.options.keys():
            self.options[oname].read(intf)
        intf.closesection(self.sectname)
    
    def write(self, intf):
        intf.opensection(self.sectname)
        for oname in self.options.keys():
            self.options[oname].write(intf)
        intf.closesection(self.sectname)
