#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of PyZenKit package.
#
# Copyright (C) since 2016 CESNET, z.s.p.o (http://www.ces.net/)
# Copyright (C) since 2015 Honza Mach <honza.mach.ml@gmail.com>
# Use of this package is governed by the MIT license, see LICENSE file.
#
# This project was initially written for personal use of the original author. Later
# it was developed much further and used for project of author`s employer.
#-------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`pyzenkit.zendaemon` module.
"""

__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import unittest

import os
import shutil

import pyzenkit.baseapp
import pyzenkit.zendaemon

#
# Global variables
#
APP_NAME      = 'test-zendaemon.py'
CFG_FILE_NAME = pyzenkit.zendaemon.DemoZenDaemon.get_resource_path('/tmp/{}.conf'.format(APP_NAME))
CFG_DIR_NAME  = pyzenkit.zendaemon.DemoZenDaemon.get_resource_path('/tmp/{}'.format(APP_NAME))

class TestPyzenkitZenDaemon(unittest.TestCase):
    """
    Unit test class for testing the :py:class:`pyzenkit.zendaemon.ZenDaemon` class.
    """

    def disabledsetUp(self):
        pyzenkit.baseapp.BaseApp.json_save(CFG_FILE_NAME, {'test': 'x'})
        try:
            os.mkdir(CFG_DIR_NAME)
        except FileExistsError:
            pass

        self.obj = pyzenkit.zendaemon.DemoZenDaemon(
            name = APP_NAME,
            description = 'TestZenDaemon - Testing daemon'
        )

    def disabledtearDown(self):
        os.remove(CFG_FILE_NAME)
        shutil.rmtree(CFG_DIR_NAME)

    def disabledtest_01_calc_statistics(self):
        """
        Perform the test of statistics calculation.
        """
        self.maxDiff = None

        result = pyzenkit.zendaemon.calc_statistics(
            {'cnt_test_a1': 50, 'cnt_test_a2': 100, 'sub': {'cnt_test_b1': 500, 'cnt_test_b2': 1000}},
            {},
            50
        )
        self.assertEqual(
            result,
            {
                'cnt_test_a1': {'cnt': 50, 'inc': 50, 'pct': 100.0, 'spd': 1.0},
                'cnt_test_a2': {'cnt': 100, 'inc': 100, 'pct': 100.0, 'spd': 2.0},
                'sub': {
                    'cnt_test_b1': {'cnt': 500, 'inc': 500, 'pct': 100.0, 'spd': 10.0},
                    'cnt_test_b2': {'cnt': 1000, 'inc': 1000, 'pct': 100.0, 'spd': 20.0}}
            }
        )


#-------------------------------------------------------------------------------


if __name__ == "__main__":
    #unittest.main()
    pass
