# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import shutil
import sys

import pytest

from portmod.execute import sandbox_execute
from portmod.globals import env
from portmod.loader import load_pkg_fq
from portmod.perms import Permissions
from portmod.repo.loader import __safe_load_file
from portmodlib.atom import FQAtom
from portmodlib.execute import execute

from .env import TEST_REPO_DIR, setup_env, tear_down_env

TMP_REPO = os.path.join(os.path.dirname(env.TMP_DIR), "not-portmod")
TMP_FILE = os.path.join(TMP_REPO, "test", "test.pybuild")
env.ALLOW_LOAD_ERROR = False


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    Sets up and tears down the test environment
    """
    dictionary = setup_env("test")
    yield dictionary
    tear_down_env()


def canimport(name: str) -> bool:
    """Returns true if the given module can be imported"""
    try:
        __import__(name)
        return True
    except ModuleNotFoundError:
        return False


@pytest.mark.skipif(
    not canimport("pytest_benchmark"), reason="requires pytest-benchmark"
)
def test_main_import_speed(benchmark):
    merge_path = shutil.which("portmod")
    command = f"{merge_path} --help"

    benchmark(execute, command)


@pytest.mark.skipif(
    not canimport("pytest_benchmark"), reason="requires pytest-benchmark"
)
def test_loader_speed(benchmark):
    def load():
        path = os.path.join(TEST_REPO_DIR, "test/test/test-1.0.pybuild")
        __safe_load_file(path)

    benchmark(load)


@pytest.mark.skipif(
    not canimport("pytest_benchmark"), reason="requires pytest-benchmark"
)
def test_cache_speed(benchmark):
    from portmod.cache import cache

    atom = FQAtom("test/test-1.0::test")

    def test():
        # This may add overhead, but load_pkg_fq does most of its work prior
        # to the load_cache call, which is relatively fast
        cache.clear()
        load_pkg_fq(atom)

    benchmark(test)


@pytest.mark.skipif(
    not canimport("pytest_benchmark") or sys.platform != "win32",
    reason="requires pytest-benchmark and win32",
)
def test_sbieini_query_speed(benchmark):
    sini = shutil.which("sbieini.exe")
    benchmark(execute, f'"{sini}" query Portmod Enabled')


@pytest.mark.skipif(
    not canimport("pytest_benchmark") or sys.platform != "win32",
    reason="requires pytest-benchmark and win32",
)
def test_sbieini_set_delete_speed(benchmark):
    sini = shutil.which("sbieini.exe")

    def test():
        execute(f'"{sini}" set Portmod Enabled y')
        execute(f'"{sini}" delete Portmod Enabled y')

    benchmark(test)


@pytest.mark.skipif(
    not canimport("pytest_benchmark"),
    reason="requires pytest-benchmark",
)
def test_sandboxed_python_speed(benchmark):
    def test():
        sandbox_execute(["python", "-c", ""], Permissions())

    benchmark(test)


@pytest.mark.skipif(
    not canimport("pytest_benchmark") or sys.platform != "win32",
    reason="requires pytest-benchmark and win32",
)
def test_sbie_execute_speed(benchmark):
    def test():
        sandbox_execute(["cmd", "/c", "call"], Permissions())

    benchmark(test)


@pytest.mark.skipif(
    not canimport("pytest_benchmark"),
    reason="requires pytest-benchmark",
)
def test_sandboxed_wrapper_speed(benchmark):
    def test():
        sandbox_execute(["python", "-m", "portmodlib._wrapper"], Permissions())

    benchmark(test)


@pytest.mark.skipif(
    not canimport("pytest_benchmark"),
    reason="requires pytest-benchmark",
)
def test_unsandboxed_wrapper_speed(benchmark):
    def test():
        execute(
            [
                "python",
                "-c",
                "from portmodlib._wrapper import main\nmain()",
                "pybuild",
                os.path.join(
                    os.path.dirname(__file__),
                    "testrepo",
                    "test",
                    "test",
                    "test-1.0.pybuild",
                ),
                "cache",
            ],
        )

    benchmark(test)
