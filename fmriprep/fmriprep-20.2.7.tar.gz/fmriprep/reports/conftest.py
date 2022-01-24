"""py.test configuration"""
import os
from pathlib import Path
import pytest
import tempfile


@pytest.fixture(autouse=True)
def populate_doctest_namespace(doctest_namespace):
    doctest_namespace["os"] = os
    doctest_namespace["Path"] = Path
    tmpdir = tempfile.TemporaryDirectory()

    doctest_namespace["tmpdir"] = tmpdir.name

    cwd = os.getcwd()
    os.chdir(tmpdir.name)
    yield
    os.chdir(cwd)
    tmpdir.cleanup()
