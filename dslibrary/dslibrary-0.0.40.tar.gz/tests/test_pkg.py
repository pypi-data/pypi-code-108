import os
import tempfile
import shutil
import unittest
import dslibrary
from dslibrary import ENV_DSLIBRARY_TARGET, ENV_DSLIBRARY_SPEC, run_model_method, DSLibrary
from dslibrary.transport.to_local import DSLibraryLocal
from dslibrary.transport.to_mmlibrary import DSLibraryViaMMLibrary
from dslibrary.transport.to_rest import DSLibraryViaREST
from dslibrary.transport.to_volume import DSLibraryViaVolume
from tests.t_utils import reset_env


class TestRunModelMethod(unittest.TestCase):

    def test_run_model_method(self):
        def m(a: int):
            return a+1
        dsl = DSLibrary(spec={"parameters": {"a": "4", "b": "b"}})
        r = run_model_method(m, dsl=dsl)
        assert r == 5


class TestMMFront(unittest.TestCase):

    def test_new_instance__local(self):
        try:
            tmpdir = tempfile.mkdtemp()
            os.environ[ENV_DSLIBRARY_TARGET] = f"local:{tmpdir}"
            mm = dslibrary.instance()
            assert isinstance(mm, DSLibraryLocal)
            assert mm._root == tmpdir
            shutil.rmtree(tmpdir)
        finally:
            os.environ[ENV_DSLIBRARY_TARGET] = ""

    def test_new_instance__rest(self):
        try:
            os.environ[ENV_DSLIBRARY_TARGET] = f"http://host:1234/path/"
            mm = dslibrary.instance()
            assert isinstance(mm, DSLibraryViaREST)
            assert mm._url == 'http://host:1234/path/'
        finally:
            os.environ[ENV_DSLIBRARY_TARGET] = ""

    def test_new_instance__mmlibrary(self):
        try:
            os.environ[ENV_DSLIBRARY_TARGET] = "mmlibrary"
            mm = dslibrary.instance()
            assert isinstance(mm, DSLibraryViaMMLibrary)
        finally:
            os.environ[ENV_DSLIBRARY_TARGET] = ""

    def test_new_instance__volume(self):
        try:
            os.environ[ENV_DSLIBRARY_TARGET] = f"volume:/path"
            mm = dslibrary.instance()
            assert isinstance(mm, DSLibraryViaVolume)
            assert mm._volume == "/path"
        finally:
            os.environ[ENV_DSLIBRARY_TARGET] = ""

    def tearDown(self) -> None:
        reset_env("test_pkg")
