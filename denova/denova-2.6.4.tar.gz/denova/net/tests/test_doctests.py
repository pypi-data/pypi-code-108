#!/usr/bin/env python3
'''
    Tests the doctests for denova.net.

    The tests starting with xtest aren't being
    maintained so have been disabled.

    Copyright 2019-2020 DeNova
    Last modified: 2020-10-02
'''

import os
import sys
from doctest import testmod
from unittest import main, TestCase

import denova.net.browser
import denova.net.html_addons
import denova.net.http_addons
import denova.net.openssl
import denova.net.utils
import denova.net.web_log_parser


class TestDoctests(TestCase):

    def test_browser(self):
        ''' Test browser doctests. '''

        test_result = testmod(denova.net.browser, report=True)
        self.assertEqual(test_result[0], 0)

    def test_html_addons(self):
        ''' Test html_addons doctests. '''

        test_result = testmod(denova.net.html_addons, report=True)
        self.assertEqual(test_result[0], 0)

    def test_http_addons(self):
        ''' Test http_addons doctests. '''

        test_result = testmod(denova.net.http_addons, report=True)
        self.assertEqual(test_result[0], 0)

    def test_utils(self):
        ''' Test net utils doctests. '''

        test_result = testmod(denova.net.utils, report=True)
        self.assertEqual(test_result[0], 0)

    def test_openssl(self):
        ''' Test openssl doctests. '''

        test_result = testmod(denova.net.openssl, report=True)
        self.assertEqual(test_result[0], 0)

    def web_log_parser(self):
        ''' Test web_log_parser doctests. '''

        test_result = testmod(denova.net.web_log_parser, report=True)
        self.assertEqual(test_result[0], 0)


if __name__ == "__main__":

    success = main()
    # exit with a system return code
    code = int(not success)
    sys.exit(code)

