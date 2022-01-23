#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for ``moke.core``
"""
import unittest
import moke.core
import os
from moke.util import run_app

class Test_util(unittest.TestCase):

    def test_path(self):
        assert moke.util.path

    def setUp(self):
        os.chdir("scripts")

    def tearDown(self):
        os.chdir("..")
        
    def test_run0(self):
        os.chdir("..")
        ret, out, err, cmd =  run_app("../bin/moke")
        assert ret == 1
        assert out == ""
        assert err
        assert cmd == "../bin/moke"
        os.chdir("scripts")
        
    def test_run1(self):
        ret, out, err, cmd =  run_app("../../bin/moke")
        assert ret == 2
        assert cmd == "../../bin/moke"
        assert out == ""
        assert err

    def test_run2(self):
        ret, out, err, cmd = run_app("../../bin/moke")
        assert ret == 2
        assert out == ""
        assert "usage: mokefile.py" in err
        assert cmd == "../../bin/moke"

    def test_grop1(self):
        ret, out, err, cmd = run_app("./grop.py")
        assert ret == 2
        assert out == ""
        assert "usage: grop.py" in err
        assert cmd == './grop.py'

    def test_grop2(self):
        ret, out, err, cmd = run_app('cat ../data/grop.inp | ./grop.py ".*\(\d{2}\).*"')
        assert out == "a line with a number (42)\n"
        assert ret == 0

    def test_grop1(self):
        ret, out, err, cmd = run_app("./grop.py")
        assert ret == 2
        assert out == ""
        assert "usage: grop.py" in err
        assert cmd == './grop.py'

    def test_grop2(self):
        ret, out, err, cmd = run_app('cat ../data/grop.inp | ./grop.py ".*\(\d{2}\).*"')
        assert out == "a line with a number (42)\n"
        assert ret == 0

    def test_mf1(self):
        ret, out, err, cmd =  run_app("moke fromdef_int")
        assert ret == 0

    def test_mf2(self):
        ret, out, err, cmd =  run_app("moke fromdef_float")
        assert ret == 0

    def test_mf3(self):
        ret, out, err, cmd =  run_app("echo 1 | moke fromdef_path_r")
        assert ret == 0
        
    def test_mf3(self):
        ret, out, err, cmd =  run_app("echo 1 | moke fromdef_path_w")
        assert ret == 0

    def test_mf4(self):
        ret, out, err, cmd =  run_app("moke fromdoc_none_int -i 10")
        assert ret == 0, err
    def test_mf1(self):
        ret, out, err, cmd =  run_app("moke fromdef_int")
        assert ret == 0

    def test_mf2(self):
        ret, out, err, cmd =  run_app("moke fromdef_float")
        assert ret == 0

    def test_mf3(self):
        ret, out, err, cmd =  run_app("echo 1 | moke fromdef_path_r")
        assert ret == 0
        
    def test_mf3(self):
        ret, out, err, cmd =  run_app("echo 1 | moke fromdef_path_w")
        assert ret == 0

    def test_mf4(self):
        ret, out, err, cmd =  run_app("../../bin/moke fromdoc_none_int -i 10")
        assert ret == 0, err


        
        
if __name__ == "__main__":
    unittest.main()