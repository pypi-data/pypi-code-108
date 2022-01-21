# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Test precommit tool."""

import os
import shutil
import unittest2 as unittest
import tempfile
from yscoverage.precommit import (
    get_changed_xpaths,
    get_all_xpaths,
    get_test_data,
    get_test_xpaths,
    report_new_xpaths,
    report_deleted_xpaths,
    report_missing_xpaths,
    report_broken_xpaths,
    report_obsolete_xpaths,
    report_invalid_testcases,
    calculate_test_coverage
)


class TestPrecommit(unittest.TestCase):
    """Tests for model coverage."""

    @classmethod
    def setUpClass(cls):
        """Function that will be automatically called before each test."""
        cls.testdir = os.path.join(os.path.dirname(__file__), 'data')
        cls.wsdir = os.path.join(cls.testdir, 'ws')
        cls.baseline = os.path.join(cls.wsdir, 'baseline', 'binos')
        cls.withdiffs = os.path.join(cls.wsdir, 'withdiff')
        cls.modelpath = 'mgmt/dmi/model/yang/src'
        cls.testpath = 'binos/mgmt/dmi/model/tests'
        cls.fset = set()
        cls.fset.add((os.path.join(cls.withdiffs, cls.modelpath),
                      "Cisco-IOS-XE-cdp"))
        cls.fcov = set()
        cls.fcov.add("Cisco-IOS-XE-cdp")
        cls.submodule = set()
        cls.submodule.add("Cisco-IOS-XE-logging")
        """Total number of xpaths in cdp model"""
        cls.cdp_model_xpaths = 136
        """Total number of xpaths in logging model"""
        cls.logging_model_xpaths = 144
        """Total number of test xpaths for cdp model"""
        cls.cdp_model_test_xpaths = 7

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.zipfile = os.path.join(self.tmpdir, 'zip_tmpfile')
        self.reportname = os.path.join(self.tmpdir, 'full_report.txt')
        os.makedirs(self.zipfile, exist_ok=True)

    def tearDown(self):
        """Remove the test directory"""
        shutil.rmtree(self.tmpdir)

    def test_get_changed_xpaths(self):
        new_xpaths, del_xpaths = get_changed_xpaths(self.withdiffs,
                                                    self.modelpath,
                                                    self.baseline,
                                                    self.fset)

        self.assertEqual({'/native/cdp/testrun'}, new_xpaths)
        self.assertEqual(set(), del_xpaths)

    def test_get_all_xpaths_module(self):
        newxps, obsxps, submod = get_all_xpaths(self.withdiffs,
                                                self.modelpath,
                                                self.fcov)

        """Validate there are 136 xpaths in Cisco-IOS-XE-cdp."""
        self.assertEqual(len(newxps), self.cdp_model_xpaths)
        """Validate obsolete xpaths. """
        self.assertEqual(obsxps, set())
        """Is this a submodule? """
        self.assertFalse(submod)

    def test_get_all_xpaths_submodule(self):
        newxps, obsxps, submod = get_all_xpaths(self.withdiffs,
                                                self.modelpath,
                                                self.submodule)

        """Validate there are 144 xpaths in the submodule."""
        self.assertEqual(len(newxps), self.logging_model_xpaths)
        """Validate obsolete xpaths. """
        self.assertEqual(obsxps, set())
        """Is this a submodule? """
        self.assertTrue(submod)

    def test_get_test_xpaths(self):
        """Validate get_test_xpaths function."""
        tdl, error = get_test_data(os.path.join(self.withdiffs, self.testpath),
                                   self.fset,
                                   self.zipfile)

        tc_xpaths = get_test_xpaths(tdl)

        """Validate there are 180 test xpaths for Cisco-IOS-XE-cdp."""
        self.assertEqual(len(tc_xpaths), self.cdp_model_test_xpaths)

    def test_report_new_xpaths(self):
        newxps = {'/native/cdp/holdtime',
                  '/native/cdp/run',
                  '/native/cdp/testrun',
                  '/native/cdp/timer',
                  '/native/interface/AppGigabitEthernet/cdp/enable',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app-config/'
                  'app',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app-config/'
                  'tlvtype',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app-config/'
                  'value',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app/tlvtype',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app/value',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/location',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'location-config',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'server-location',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'server-location-config'}

        tdl = [{'category': 'CDP',
                'cli_verified': False,
                'oper_verified': False,
                'path': '/ws/graceho-sjc/yangsuite-coverage/yscoverage/tests/'
                        'data/ws/withdiff/binos/mgmt/dmi/model/tests/ned',
                'task_name': 'hardening_cdp_enable_create',
                'test_name': set(),
               'xpaths': {'/native/interface/BDI/name',
                          '/native/interface/BDI/cdp/enable'}},
               {'category': 'CDP',
                'cli_verified': False,
                'oper_verified': False,
                'path': '/ws/graceho-sjc/yangsuite-coverage/yscoverage/tests/'
                        'data/ws/withdiff/binos/mgmt/dmi/model/tests/ned',
                'task_name': 'hardening_cdp_tlv_app_merge',
                'test_name': set(),
                'xpaths': {'/native/interface/BDI/cdp/tlv/app/app',
                           '/native/interface/BDI/name'}},
               {'category': 'CDP',
                'cli_verified': False,
                'oper_verified': False,
                'path': '/ws/graceho-sjc/yangsuite-coverage/yscoverage/'
                        'tests/data/ws/withdiff/binos/mgmt/dmi/model/tests/'
                        'ned',
                'task_name': 'hardening_interface_bdi_name',
                'test_name': set(),
                'xpaths': {'/native/interface/BDI',
                           '/native/interface/BDI/name'}}]

        """Validate report_new_xpaths function."""
        no_cli, no_cliver, no_operver = report_new_xpaths(self.reportname,
                                                          newxps,
                                                          tdl)

        self.assertEqual(no_cli, True)
        self.assertEqual(no_cliver, False)
        self.assertEqual(no_operver, False)

    def test_report_deleted_xpaths(self):
        delxps = {'/native/cdp/holdtime',
                  '/native/cdp/run',
                  '/native/cdp/testrun',
                  '/native/cdp/timer',
                  '/native/interface/AppGigabitEthernet/cdp/enable',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app-config/'
                  'app',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app-config/'
                  'tlvtype',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app-config/'
                  'value',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app/tlvtype',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app/value',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/location',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'location-config',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'server-location',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'server-location-config'}

        """Validate report_deleted_xpaths function."""
        report_deleted_xpaths(self.reportname, delxps)

        testval = False
        with open(self.reportname) as f:
            for line in f:
                if ("Removed xpaths" in line):
                    testval = True

        self.assertEqual(testval, True)

    def test_report_missing_xpaths(self):
        newxps = {'/native/cdp/holdtime',
                  '/native/cdp/run',
                  '/native/cdp/testrun',
                  '/native/cdp/timer',
                  '/native/interface/AppGigabitEthernet/cdp/enable',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'app-config/app',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'app-config/tlvtype',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'app-config/value',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app/tlvtype',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/app/value',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/location',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'location-config',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'server-location',
                  '/native/interface/AppGigabitEthernet/cdp/tlv/'
                  'server-location-config'}

        tcxps = {'/native/cdp/run',
                 '/native/cdp/testrun',
                 '/native/cdp/timer',
                 '/native/interface/AppGigabitEthernet/cdp/enable',
                 '/native/interface/AppGigabitEthernet/cdp/tlv/app',
                 '/native/interface/AppGigabitEthernet/cdp/tlv/app-config/app'}

        """Excluded xpaths"""
        exps = ['/native/interface/AppGigabitEthernet/cdp/tlv/location',
                '/native/interface/AppGigabitEthernet/cdp/tlv/location-config']

        total_missing_tc = 9
        """Validate report_deleted_xpaths function."""
        trim_missing_tc = report_missing_xpaths(self.reportname,
                                                newxps,
                                                tcxps,
                                                exps,
                                                False)

        self.assertEqual(len(trim_missing_tc), total_missing_tc)

    def test_report_broken_xpaths(self):
        delxps = {'/native/cdp/holdtime',
                  '/native/cdp/run',
                  '/native/cdp/testrun',
                  '/native/cdp/timer',
                  '/native/interface/AppGigabitEthernet/cdp\
                      /tlv/server-location-config'}

        tcxps = {'/native/cdp/run',
                 '/native/interface/AppGigabitEthernet/cdp/tlv/app-config/app'}

        """Validate report_broken_xpaths function."""
        btc = report_broken_xpaths(self.reportname, delxps, tcxps)

        self.assertEqual(btc, True)

    def test_report_obsolete_xpaths(self):
        obsxps = {'/native/cdp/holdtime',
                  '/native/cdp/run',
                  '/native/cdp/testrun'}

        """Validate report_obsolete_xpaths function."""
        report_obsolete_xpaths(self.reportname, obsxps)

        testval = False
        with open(self.reportname) as f:
            for line in f:
                if ("Below xpaths should mark obsolete in the model" in line):
                    testval = True

        self.assertEqual(testval, True)

    def test_report_invalid_testcases(self):
        obsxps = {'/native/cdp/holdtime',
                  '/native/cdp/run',
                  '/native/cdp/testrun'}

        tcxps = {'/native/cdp/run',
                 '/native/cdp/testrun'}

        tdl = [{'category': 'CDP',
                'cli_verified': False,
                'oper_verified': False,
                'path': '/ws/graceho-sjc/yangsuite-coverage/yscoverage/tests/'
                        'data/ws/withdiff/binos/mgmt/dmi/model/tests/ned',
                'task_name': 'hardening_cdp_enable_create',
                'test_name': set(),
               'xpaths': {'/native/cdp/run',
                          '/native/cdp/testrun'}}]

        """Excluded xpaths"""
        exps = ['/native/interface/AppGigabitEthernet/cdp/tlv/location',
                '/native/interface/AppGigabitEthernet/cdp/tlv/location-config']

        """Validate report_invalid_testcases function."""
        invalid_test = report_invalid_testcases(self.reportname,
                                                obsxps,
                                                tcxps,
                                                tdl,
                                                exps)

        self.assertEqual(len(invalid_test), 0)

    def test_calculate_test_coverage(self):
        total_xpaths = {'/native/cdp/holdtime',
                        '/native/cdp/run',
                        '/native/cdp/testrun'}

        missing_tc = {'/native/cdp/testrun'}

        exception_tc = {'/native/cdp/testrun'}

        """Excluded xpaths"""
        expl = ['/native/cdp/testrun']

        invalid_tc = {'/native/cdp/testrun1'}

        """Validate calculate_test_coverage function."""
        calculate_test_coverage(self.reportname,
                                total_xpaths,
                                missing_tc,
                                exception_tc,
                                expl,
                                invalid_tc)

        testval = False
        with open(self.reportname) as f:
            for line in f:
                if ("Test Coverage" in line):
                    testval = True

        self.assertEqual(testval, True)
