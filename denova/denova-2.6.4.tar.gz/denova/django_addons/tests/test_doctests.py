#!/usr/bin/env python3
'''
    Tests the doctests for denova.django_addons.

    The tests starting with xtest aren't being
    maintained so have been disabled.

    Copyright 2019-2021 DeNova
    Last modified: 2021-02-22
'''

import sys
from doctest import testmod
from unittest import main, TestCase

import denova.django_addons.data_image
import denova.django_addons.singleton
import denova.django_addons.utils
import denova.django_addons.views


class TestDoctests(TestCase):

    def test_data_image(self):
        ''' Test data_image doctests. '''

        test_result = testmod(denova.django_addons.data_image, report=True)
        self.assertEqual(test_result[0], 0)

    def test_singleton(self):
        ''' Test singleton doctests. '''

        test_result = testmod(denova.django_addons.singleton, report=True)
        self.assertEqual(test_result[0], 0)

    def test_utils(self):
        ''' Test django_addonst utils doctests. '''

        test_result = testmod(denova.django_addons.utils, report=True)
        self.assertEqual(test_result[0], 0)

    def test_views(self):
        ''' Test views doctests. '''

        test_result = testmod(denova.django_addons.views, report=True)
        self.assertEqual(test_result[0], 0)


if __name__ == "__main__":

    success = main()
    # exit with a system return code
    code = int(not success)
    sys.exit(code)

