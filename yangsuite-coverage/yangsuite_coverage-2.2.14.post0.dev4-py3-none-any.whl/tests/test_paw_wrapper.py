# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Test paw wrapper tool."""

import os
import unittest2 as unittest
from yscoverage.paw_wrapper import (
    check_model_exist,
    check_file_writable,
    match_directory,
    set_json_header,
    TESTDIRS,
    get_model_list,
    init_json_data,
    paw_results,
    get_baseline_coverage
)


class TestPawWrapper(unittest.TestCase):
    """Tests for paw wrapper tool."""
    @classmethod
    def setUpClass(cls):
        """Function that will be automatically called before each test."""
        cls.testdir = os.path.join(os.path.dirname(__file__), 'data')
        cls.wsdir = os.path.join(cls.testdir, 'ws')
        cls.modelfile = os.path.join(cls.wsdir, 'modelfiles')
        cls.modelfile_num = 1

    def test_check_model_exists(self):
        found = check_model_exist(self.testdir, 'Cisco-IOS-XE-aaa')
        self.assertEqual(found, False)

    def test_match_directory(self):
        result = []
        result = match_directory(TESTDIRS, self.testdir)
        self.assertIsNotNone(result)

    def test_get_model_list(self):
        modelnames, run_precommit = get_model_list(self.modelfile)
        self.assertEqual(len(modelnames), self.modelfile_num)
        self.assertEqual(run_precommit, True)

    def test_set_json_header(self):
        set_json_header('workspace1', 'polaris_dev', self.modelfile)
        self.assertIn("ws_root", paw_results)
        self.assertIn("command", paw_results)
        self.assertIn("overall_status", paw_results)
        self.assertIn("exit_code", paw_results)
        self.assertIn("contact_alias", paw_results)
        self.assertIn("reason", paw_results)
        self.assertIn("num_file_analyzed", paw_results)
        self.assertNotIn("precommit", paw_results)

    def test_init_json_data(self):
        parentname, logpath = init_json_data(True)
        self.assertIn("baseline", parentname)

        parentname, logpath = init_json_data(False)
        self.assertIn("withdiffs", parentname)

    def test_check_file_writable(self):
        ret = check_file_writable(self.modelfile)
        self.assertEqual(ret, True)

    def test_get_baseline_coverage(self):
        data = dict()
        default_coverage = float(4.2)
        modelname = "Cisco-IOS-XE-aaa"
        data["baseline"] = [{"modelname": modelname,
                             "coverage": default_coverage}]

        coverage = get_baseline_coverage(data, modelname)

        self.assertEqual(coverage, coverage)
