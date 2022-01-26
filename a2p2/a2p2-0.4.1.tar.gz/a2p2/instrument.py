#!/usr/bin/env python

__all__ = []

import logging

logger = logging.getLogger(__name__)

class Instrument():

    def __init__(self, facility, insname, help="Help TBD"):
        self.facility = facility
        self.insname = insname
        self.help = help
        facility.registerInstrument(self)

    def getName(self):
        return self.insname

    def getShortName(self):
        """
        Keep left part of _ tokenized name.
        EG. useful to replace MATISSE_LM or MATISSE_N by MATISSE in some common parts (config or treeview).
        """
        if not "_" in self.insname:
            return self.insname
        return self.insname[0:self.insname.index("_")]

    def getHelp(self):
        return self.help
