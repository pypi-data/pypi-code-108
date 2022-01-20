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
Unit test module for testing the :py:mod:`pyzenkit.daemonizer` module.
"""

__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import unittest

import os
import signal

import pyzenkit.daemonizer


PID_FILE = '/tmp/test.pyzenkit.daemonizer.pid'


class TestPyzenkitDaemonizer(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`pyzenkit.daemonizer` module.
    """

    def test_01_basic(self):
        """
        Perform the basic operativity tests.
        """
        self.assertRaises(FileNotFoundError, pyzenkit.daemonizer.write_pid, '/bogus/file', 123)
        self.assertRaises(Exception, pyzenkit.daemonizer.write_pid, '/bogus/file', "123")

        self.assertFalse(os.path.isfile(PID_FILE))
        pyzenkit.daemonizer.write_pid(PID_FILE, 12345)
        self.assertTrue(os.path.isfile(PID_FILE))
        self.assertEqual(pyzenkit.daemonizer.read_pid(PID_FILE), 12345)
        os.unlink(PID_FILE)
        self.assertFalse(os.path.isfile(PID_FILE))

    def test_02_daemonization_lite(self):
        """
        Perform lite daemonization tests.
        """
        def hnd_sig_hup(signum, frame):  # pylint: disable=locally-disabled,unused-argument
            """Test signal handler."""
            print("HANDLER CALLBACK: Received signal HUP ({})".format(signum))

        def hnd_sig_usr1(signum, frame):  # pylint: disable=locally-disabled,unused-argument
            """Test signal handler."""
            print("HANDLER CALLBACK: Received signal USR1 ({})".format(signum))

        def hnd_sig_usr2(signum, frame):  # pylint: disable=locally-disabled,unused-argument
            """Test signal handler."""
            print("HANDLER CALLBACK: Received signal USR2 ({})".format(signum))

        self.assertFalse(os.path.isfile(PID_FILE))
        (pid, pid_file) = pyzenkit.daemonizer.daemonize_lite(
            work_dir = '/tmp',
            pid_file = PID_FILE,
            umask    = 0o022,
            signals  = {
                signal.SIGHUP:  hnd_sig_hup,
                signal.SIGUSR1: hnd_sig_usr1,
                signal.SIGUSR2: hnd_sig_usr2,
            },
        )
        self.assertTrue(os.path.isfile(PID_FILE))
        self.assertTrue(os.path.isfile(pid_file))
        self.assertEqual(pyzenkit.daemonizer.read_pid(PID_FILE), pid)
        self.assertEqual(pyzenkit.daemonizer.read_pid(pid_file), pid)
        self.assertEqual(os.getcwd(), '/tmp')


#-------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
