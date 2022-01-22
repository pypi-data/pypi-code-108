#! /usr/bin/env python3
"""
Module PIniFileOption
Sub-Package STDLIB.INI of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``PIniFileOption`` class.
"""


class PIniFileOption(object):
    """OS-independent class for a single preference option.
    
    Option must have a name, data type, value, and default (used if option is
    not yet read or not present in the preferences file). Expects to be given
    a PIniFileInterface instance to read or write its value.
    """
    
    def __init__(self, oname, vtype, adefault):
        object.__init__(self)
        self.optname = oname
        self.opttype = vtype
        self.optvalue = adefault
        self.optdefault = adefault
    
    def getvalue(self):
        return self.optvalue
    
    def setvalue(self, avalue):
        self.optvalue = avalue
    
    def read(self, intf):
        self.optvalue = intf.readvalue(self.optname, self.opttype,
                                       self.optdefault)
    
    def write(self, intf):
        intf.writevalue(self.optname, self.opttype, self.optvalue)
