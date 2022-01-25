#!/usr/bin/env python3
'''
    Tests the doctests for denova.python.

    The tests starting with xtest aren't being
    maintained so have been disabled.

    Copyright 2019-2022 DeNova
    Last modified: 2022-01-24
'''

import os
import sys
from doctest import testmod
from unittest import main, TestCase, TextTestRunner, TestSuite

import denova.python.dict
import denova.python.elapsed_time
import denova.python.format
import denova.python.iter
import denova.python.log
import denova.python._log
import denova.python.performance
import denova.python.text_file
import denova.python.times
import denova.python.utils


class TestDoctests(TestCase):

    def test_dict(self):
        ''' Test dict doctests. '''

        test_result = testmod(denova.python.dict, report=True)
        self.assertEqual(test_result[0], 0)

    def test_elapsed_time(self):
        ''' Test elapsed_time doctests. '''

        test_result = testmod(denova.python.elapsed_time, report=True)
        self.assertEqual(test_result[0], 0)

    def test_format(self):
        ''' Test format doctests. '''

        test_result = testmod(denova.python.format, report=True)
        self.assertEqual(test_result[0], 0)

    def test_iter(self):
        ''' Test iter doctests. '''

        test_result = testmod(denova.python.iter, report=True)
        self.assertEqual(test_result[0], 0)

    def test_log(self):
        ''' Test log doctests. '''

        test_result = testmod(denova.python.log, report=True)
        self.assertEqual(test_result[0], 0)

    def test__log(self):
        ''' Test _log doctests. '''

        test_result = testmod(denova.python._log, report=True)
        self.assertEqual(test_result[0], 0)

    def test_performance(self):
        ''' Test performance doctests. '''

        test_result = testmod(denova.python.performance, report=True)
        self.assertEqual(test_result[0], 0)

    def test_text_file(self):
        ''' Test text_file doctests. '''

        test_result = testmod(denova.python.text_file, report=True)
        self.assertEqual(test_result[0], 0)

    def test_times(self):
        ''' Test times doctests. '''

        test_result = testmod(denova.python.times, report=True)
        self.assertEqual(test_result[0], 0)

    def test_utils(self):
        ''' Test python utils doctests. '''

        test_result = testmod(denova.python.utils, report=True)
        self.assertEqual(test_result[0], 0)


if __name__ == "__main__":

    success = main()
    # exit with a system return code
    code = int(not success)
    sys.exit(code)

