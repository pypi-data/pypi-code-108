import unittest
import mock
import os
import tempfile
import shutil

import dslibrary
from tests.t_utils import reset_env


class TestRunNoContext(unittest.TestCase):
    """
    When you use dslibrary with no context at all, it makes some simple assumptions.
    """

    def test_default_parameters_from_command_line(self):
        # --NAME=VALUE
        dsl = dslibrary.instance()
        with mock.patch("sys.argv", ["source.py", "--x=7"]):
            r = dsl.get_parameter("x")
            assert r == 7, r
        # --NAME VALUE
        dsl = dslibrary.instance()
        with mock.patch("sys.argv", ["source.py", "--x", "123"]):
            r = dsl.get_parameter("x")
            assert r == 123, r
        # string type
        dsl = dslibrary.instance()
        with mock.patch("sys.argv", ["source.py", "--x", "123a"]):
            r = dsl.get_parameter("x")
            assert r == "123a", r

    def test_open_resource_local_file_in_cwd(self):
        """
        All inputs and outputs are just files relative to the current directory.
        """
        project = tempfile.mkdtemp()
        with open(os.path.join(project, "f"), 'w') as f:
            f.write("abc")
        cwd0 = os.getcwd()
        os.chdir(project)
        try:
            dsl = dslibrary.instance()
            r = dsl.read_resource("f", mode="r")
            assert r == "abc"
            r = dsl.read_resource("f", mode="rb")
            assert r == b"abc"
        finally:
            os.chdir(cwd0)
        shutil.rmtree(project)

    def tearDown(self) -> None:
        reset_env("test_run_no_context")
