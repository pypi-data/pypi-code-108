#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import pytest
# make sure to prefix your class with Test
# it finds both test_ prefixed functions.

class TestPytest(object):
    def test_one(self):
        x = "this"
        assert "h" in x


    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")

# pytest -k test_one test_class.py
# 匹配的范围是文件名、类名、函数名为变量，用and来区分, 例：pytest -k "test_ and not test_two" test_class.py

# 测试执行前，pytest会为每个测试创建独立的唯一的临时路径。
    def test_needsfiles(tmpdir):
        print("tmpdir=", tmpdir)
        assert 0

    @pytest.fixture
    def fix_func(self):
        print("fix_func has been called.")

    def test_fix_func(self, fix_func):  # fix_func作为方法参数，会发现是一个被@pytest.fixture装饰器修饰的方法，则先执行。
        print("test_fix_func has been called.")
        assert 0


# conftest.py: sharing fixture functions
# The discovery of fixture functions starts at test classes, then test modules, then conftest.py files and finally builtin and third party plugins
    def test_share_fixture(self, share_fixture_func):
        print("test_share_fixture test case.")
        assert 0

    def test_share_fixture1(self, share_fixture_func):  # share_fixture_func即便在该module下被调用两次，但其定义处加上scope=module，则在module范围内也只执行一次。
        print("test_share_fixture1 test case.")
        assert 0

# Sharing test data

if __name__ == "__main__":
    pytest.main(["-s",  "test_class.py"])
