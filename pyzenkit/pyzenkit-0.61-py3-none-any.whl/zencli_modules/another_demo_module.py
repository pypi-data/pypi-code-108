#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (C) 2015-2016 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
.. warning::

    This module is under development, please do not use it yet.

"""


from pyzenkit.zencli import ZenCLIModule

VERSION = "0.1-beta1"

class OtherTestModule(ZenCLIModule):
    """
    Base class for all pluggable ZenCLI modules
    """
    def process(self):
        print("Process: Inside OtherTestModule")

if __name__ == "__main__":
    MODULE = OtherTestModule()
    MODULE.process()
