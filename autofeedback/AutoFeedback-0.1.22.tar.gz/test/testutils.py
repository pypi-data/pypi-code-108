import unittest
from AutoFeedback.utils import check_module
from subprocess import check_call
from sys import executable


class UnitTests(unittest.TestCase):
    def setUp(self):
        check_call(
            [executable, "-m", "pip", "uninstall", "-y", "pip-install-test"])

    def test_1_not_installed(self):
        from importlib.util import find_spec
        installed = find_spec("pip_install_test") is not None
        assert (not installed)

    def test_2_installed(self):
        from importlib.util import find_spec
        check_module("pip-install-test")
        installed = find_spec("pip_install_test") is not None
        assert (installed)

    def tearDown(self):
        check_call(
            [executable, "-m", "pip", "uninstall", "-y", "pip-install-test"])
