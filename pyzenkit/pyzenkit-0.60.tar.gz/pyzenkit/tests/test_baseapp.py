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
Unit test module for testing the :py:mod:`pyzenkit.baseapp` module.
"""

__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import unittest

import os
import shutil

import pyzenkit.baseapp


#
# Global variables
#
APP_NAME       = 'test-baseapp.py'
JSON_FILE_NAME = pyzenkit.baseapp.DemoBaseApp.get_resource_path('tmp/script-state.json')
CFG_FILE_NAME  = pyzenkit.baseapp.DemoBaseApp.get_resource_path('tmp/{}.conf'.format(APP_NAME))
CFG_DIR_NAME   = pyzenkit.baseapp.DemoBaseApp.get_resource_path('tmp/{}'.format(APP_NAME))


class TestPyzenkitBaseApp(unittest.TestCase):
    """
    Unit test class for testing the :py:class:`pyzenkit.baseapp.BaseApp` class.
    """

    def disabledsetUp(self):
        pyzenkit.baseapp.BaseApp.json_save(CFG_FILE_NAME, {'test': 'x'})
        try:
            os.mkdir(CFG_DIR_NAME)
        except FileExistsError:
            pass

        self.obj = pyzenkit.baseapp.DemoBaseApp(
            name        = APP_NAME,
            description = 'TestBaseApp - Testing application'
        )
    def disabledtearDown(self):
        os.remove(CFG_FILE_NAME)
        shutil.rmtree(CFG_DIR_NAME)

    def disabledtest_01_utils(self):
        """
        Perform tests of generic application utils.
        """
        self.maxDiff = None

        # Test the name generation capabilities.
        self.assertEqual(self.obj.name, APP_NAME)

        # Test the saving of JSON files.
        self.assertTrue(self.obj.json_save(JSON_FILE_NAME, { "test": 1 }))

        # Test that the JSON file was really created.
        self.assertTrue(os.path.isfile(JSON_FILE_NAME))

        # Test the loading of JSON files.
        self.assertEqual(self.obj.json_load(JSON_FILE_NAME), { "test": 1 })

        # Remove the JSON file we are done with.
        os.remove(JSON_FILE_NAME)

    def disabledtest_02_argument_parsing(self):
        """
        Perform tests of argument parsing.
        """
        self.maxDiff = None

        # Test argument parsing.
        argp = self.obj._init_argparser()  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(
            vars(argp.parse_args(['--verbose'])),
            {
                'action': None,
                'config_dir': None,
                'config_dir_silent': None,
                'config_file': None,
                'config_file_silent': None,
                'debug': None,
                'group': None,
                'input': None,
                'limit': None,
                'log_file': None,
                'log_level': None,
                'name': None,
                'pstate_dump': None,
                'pstate_file': None,
                'pstate_log': None,
                'quiet': None,
                'runlog_dir': None,
                'runlog_dump': None,
                'runlog_log': None,
                'user': None,
                'verbosity': 1
            }
        )

    def disabledtest_03_plugin(self):
        """
        Perform tests of plugin mode.
        """
        self.maxDiff = None

        self.obj.plugin()


#-------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
