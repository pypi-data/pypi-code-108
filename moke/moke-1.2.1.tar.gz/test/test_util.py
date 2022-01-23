#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for ``moke.util``
"""
import unittest
import moke.util

class Test_core(unittest.TestCase):

    def test_import(self):
        assert moke.util.run_app

if __name__ == "__main__":
    unittest.main()