# content of conftest.py
#
import sys
import pytest
from topoly import check_cuda

ALL = set("darwin linux win32".split())

def pytest_runtest_setup(item):
    supported_platforms = ALL.intersection(mark.name for mark in item.iter_markers())
    plat = sys.platform
    if supported_platforms and plat not in supported_platforms:
        pytest.skip("cannot run on platform {}".format(plat))
    for mark in item.iter_markers():
        if mark.name == 'cuda' and not check_cuda():
            pytest.skip('No CUDA - skipping test')



