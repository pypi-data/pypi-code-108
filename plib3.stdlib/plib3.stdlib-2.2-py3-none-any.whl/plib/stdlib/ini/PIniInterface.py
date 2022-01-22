#! /usr/bin/env python3
"""
Module PIniInterface
Sub-Package STDLIB.INI of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``PIniInterface`` class.
"""

import os

# Only OS's currently comprehended are POSIX and NT

if os.name == "posix":
    # In Unix/Linux we use config files, default is appname.ini in
    # the user's home directory (tweak this by changing the inipath
    # and/or iniext globals before creating any class instances)
    from configparser import *
    inipath = "~"
    iniext = ".ini"

elif os.name == "nt":
    # In Windows we access the Registry, so we need to map data types to
    # what the Registry understands; default root key for options is
    # HKEY_CURRENT_USER\Software\MyAppName, this can be tweaked by
    # changing the inipath global before creating any class instances
    # (the iniext global can also be changed to append something to
    # MyAppName but this is very rare)
    from winreg import *
    regtypes = {
        int: REG_DWORD,
        bool: REG_DWORD,
        str: REG_SZ
    }
    inipath = "Software"
    iniext = ""


class PIniInterface(object):
    """Low-level interface with the OS mechanisms for storing preferences.
    
    The intent is to hide all OS-dependent code in this class so the
    other classes see a single consistent API.
    """
    
    falsestr = 'no'
    truestr = 'yes'
    
    def __init__(self):
        object.__init__(self)
        if os.name == "posix":
            self.parser = SafeConfigParser()
            self.inifile = None
        else:
            self.parser = None
        
        self.regkey = None
        self.openkey = None
        
        self.openiname = ''
        self.opensname = ''
    
    def ininame(self, iname):
        if os.name == "posix":
            return os.path.expanduser(os.path.join(inipath, iname + iniext))
        
        elif os.name == "nt":
            return os.path.normpath(os.path.join(inipath, iname + iniext))
        
        else:
            return iname
    
    def initialize(self, iname):
        if self.parser is not None:
            ininame = self.ininame(iname)
            if os.path.isfile(ininame):
                self.inifile = open(ininame, 'rU')
                try:
                    self.parser.readfp(self.inifile)
                finally:
                    self.inifile.close()
            self.inifile = None
        
        else:
            self.regkey = CreateKey(HKEY_CURRENT_USER, self.ininame(iname))
        
        self.openiname = iname
    
    def shutdown(self, iname, dosave=False):
        if self.parser is not None:
            if dosave:
                self.inifile = open(self.ininame(iname), "w")
                self.parser.write(self.inifile)
                self.inifile.close()
                self.inifile = None
        
        elif self.regkey is not None:
            CloseKey(self.regkey)
            self.regkey = None
        
        self.openiname = ''
    
    def opensection(self, sname):
        if self.parser is not None:
            if not self.parser.has_section(sname):
                self.parser.add_section(sname)
        
        elif self.regkey is not None:
            self.openkey = CreateKey(self.regkey, sname)
        
        self.opensname = sname
    
    def closesection(self, sname):
        if self.openkey is not None:
            CloseKey(self.openkey)
            self.openkey = None
        
        self.opensname = ''
    
    def readvalue(self, oname, vtype, adefault):
        if self.parser is not None:
            if self.parser.has_option(self.opensname, oname):
                if vtype is int:
                    return self.parser.getint(self.opensname, oname)
                elif vtype is bool:
                    return self.parser.getboolean(self.opensname, oname)
                elif vtype is str:
                    return self.parser.get(self.opensname, oname)
                else:
                    raise TypeError("Invalid INI option type: {}".format(repr(vtype)))
            else:
                return adefault
        
        elif self.openkey is not None:
            try:
                retval = QueryValueEx(self.openkey, oname)[0]
            except WindowsError:
                retval = adefault
            if vtype == int:
                return int(retval)
            elif vtype == bool:
                return bool(retval)
            else:
                return retval
        
        else:
            return None
    
    def writevalue(self, oname, vtype, avalue):
        if self.parser is not None:
            # Dunno why ConfigParser doesn't have setint, setboolean
            # corresponding to getint, getboolean above, but oh well...
            if vtype == bool:
                avalue = (self.falsestr, self.truestr)[avalue]
            else:
                avalue = str(avalue)
            self.parser.set(self.opensname, oname, avalue)
        
        elif self.openkey is not None:
            # SetValueEx wants to see a value of the appropriate type
            # even though it's going to convert it to a string anyway
            # (and even though QueryValueEx always returns a string)
            if vtype in (bool, int):
                avalue = int(avalue)
            else:
                avalue = str(avalue)
            SetValueEx(self.openkey, oname, 0, regtypes[vtype], avalue)
