#! /usr/bin/env python3
"""
Module PIniFileBase
Sub-Package STDLIB.INI of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``PIniFileBase`` class.
"""

import collections

from .PIniInterface import PIniInterface
from .PIniFileSection import PIniFileSection


class PIniFileBase(object):
    """OS-independent base class for a preferences file.
    
    Has a name (which denotes the entire file), a dictionary of section
    names (keys) vs. PIniFileSection instances, and a PIniInterface to use
    for the actual reading/writing of preferences (the actual read/write
    mechanics walk the section/option hierarchy for simplicity of coding).
    
    Note this base class is factored out from PIniFile below to allow
    different methods of accessing the INI file structure. PIniFile uses
    the "dict of lists of tuples" method described above, but other
    methods are possible.
    """
    
    # The interface and section classes can be changed by
    # resetting these class fields.
    _intfclass = PIniInterface
    _sectclass = PIniFileSection
    
    def __init__(self, iname):
        object.__init__(self)
        self.ininame = iname
        self.sections = collections.OrderedDict()
        self.intf = self._intfclass()
    
    def addsection(self, sname):
        self.sections[sname] = self._sectclass(sname)
    
    def addoption(self, sname, oname, vtype, adefault):
        if sname not in self.sections:
            self.addsection(sname)
        self.sections[sname].addoption(oname, vtype, adefault)
    
    def getvalue(self, sname, oname):
        if sname in self.sections:
            return self.sections[sname].getvalue(oname)
        else:
            return None
    
    def setvalue(self, sname, oname, avalue):
        if sname in self.sections:
            self.sections[sname].setvalue(oname, avalue)
    
    def readvalues(self):
        self.intf.initialize(self.ininame)
        for sname in self.sections.keys():
            self.sections[sname].read(self.intf)
        self.intf.shutdown(self.ininame)
    
    def writevalues(self):
        self.intf.initialize(self.ininame)
        for sname in self.sections.keys():
            self.sections[sname].write(self.intf)
        self.intf.shutdown(self.ininame, True)
