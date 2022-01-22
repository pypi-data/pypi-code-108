#!/usr/bin/env python

import os.path
import tempfile
import unittest

from glue import pidfile


class TestPidfile(unittest.TestCase):

    def test_get_lock(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lockfile = os.path.join(tmpdir, "lock.pid")
            pidfile.get_lock(lockfile)
            pidfile.confirm_lock(lockfile)

    def test_duplicate_lock(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lockfile = os.path.join(tmpdir, "lock.pid")
            pidfile.get_lock(lockfile)
            pidfile.confirm_lock(lockfile)
            # cannot get the same lock twice
            with self.assertRaises(RuntimeError):
                pidfile.get_lock(lockfile)


if __name__ == "__main__":
    unittest.main(verbosity=2)
