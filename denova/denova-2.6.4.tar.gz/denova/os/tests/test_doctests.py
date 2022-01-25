#!/usr/bin/env python3
'''
    Tests the doctests for denova.os.

    This is a unit test that includes doctests when we run unit tests.

    The tests starting with xtest aren't being
    maintained so have been disabled.

    Copyright 2019-2022 DeNova
    Last modified: 2022-01-17
'''

import os
import sys
from doctest import testmod
from unittest import main, TestCase

import denova.os.cli
import denova.os.command
import denova.os.drive
import denova.os.fs
import denova.os.lock
import denova.os.osid
import denova.os.process
import denova.os.profile_addons
import denova.os.user


class TestDoctests(TestCase):
    ''' Include doctests when we run unit tests. '''

    def test_cli(self):
        ''' Test cli doctests. '''

        failure_count, test_count = testmod(denova.os.cli)
        self.assertEqual(failure_count, 0)
        print(f'Passed {test_count} "os.cli" doctests')

    def test_command(self):
        ''' Test command doctests. '''

        failure_count, test_count = testmod(denova.os.command)
        self.assertEqual(failure_count, 0)
        print(f'Passed {test_count} "os.command" doctests')

    def test_drive(self):
        ''' Test drive doctests. '''

        failure_count, test_count = testmod(denova.os.drive)
        self.assertEqual(failure_count, 0)
        print(f'Passed {test_count} "os.drive" doctests')

    def test_fs(self):
        ''' Test fs doctests. '''

        failure_count, test_count = testmod(denova.os.fs)
        self.assertEqual(failure_count, 0)
        print(f'Passed {test_count} "os.fs" doctests')

    def test_lock(self):
        ''' Test lock doctests. '''

        failure_count, test_count = testmod(denova.os.lock)
        self.assertEqual(failure_count, 0)
        print(f'Passed {test_count} "os.lock" doctests')

    def test_osid(self):
        ''' Test osid doctests. '''

        failure_count, test_count = testmod(denova.os.osid)
        self.assertEqual(failure_count, 0)
        print(f'Passed {test_count} "os.osid" doctests')

    def test_process(self):
        ''' Test process doctests. '''

        failure_count, test_count = testmod(denova.os.process)
        self.assertEqual(failure_count, 0)
        print(f'Passed {test_count} "os.process" doctests')

    def test_profile_addons(self):
        ''' Test profile_addons doctests. '''

        failure_count, test_count = testmod(denova.os.profile_addons)
        self.assertEqual(failure_count, 0)
        print(f'Passed {test_count} "os.profile_addons" doctests')

    def test_user(self):
        ''' Test user doctests. '''

        failure_count, test_count = testmod(denova.os.user)
        self.assertEqual(failure_count, 0)
        print(f'Passed {test_count} "os.user" doctests')



if __name__ == "__main__":

    success = main()
    # exit with a system return code
    code = int(not success)
    sys.exit(code)

