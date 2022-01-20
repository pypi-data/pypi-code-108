#! /usr/bin/env python3
"""
Sub-Package STDLIB.INI of Package PLIB3 -- Python INI Objects
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

The idea behind these classes is to provide a platform-independent system for
handling INI options.

The PIniInterface class handles platform-specific stuff so the other classes
don't have to worry about it; they just call that class's generic methods.

The PIniFileOption, PIniFileSection, and PIniFileBase classes implement the
platform-independent option-handling system. They can be used on their own,
but it will generally be easier to use PIniFile with its easier interface.

The PIniFile class is set up to give a simple "list of lists" interface that
links the variables in your app with the correct INI file section and option,
so all you have to do is set up the list to be passed to buildini().

The buildlist parameter of buildini() is a list of tuples (one per section),
each of which also stores a list of tuples (one per option), thusly:

    buildlist = [s-tuple, ...]

    s-tuple = (sectionname, optionlist)

    optionlist = [o-tuple, ...]

    o-tuple = (optionname, optiontype, optiondefault, optionget, optionset)
    - or -  = (optionname, optiontype, optiondefault, attrname)
    - or -  = (optionname, optiontype, optiondefault)

where sectionname is the name of the INI section, optionname is the name of
the INI option, optiontype is one of the three data type flags below,
optiondefault is the default value of the option, and optionget and optionset
are functions that read and write the app variable for the option; or,
attrname is a string giving the name of the attribute on the INI file object
to be used to store the value of the option. If neither of these is present,
the default attribute name <sectionname>_<optionname> is used to store the
value.

The get and set functions, if used, should be of the following form:

    def optionget(): return optionvar
    def optionset(value): optionvar = value

Typical usage: create an instance of PIniFile; then call buildini() on it with
a "list of lists" giving the sections and options, then call readini() to load
the INI data. Call writeini() to save the INI data, typically either when the
app closes or when the user selects "Save Preferences" or suchlike.
"""

from .PIniFile import PIniFile  # the other classes are internal only
