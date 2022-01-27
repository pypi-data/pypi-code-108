# Created from https://github.com/nipype/pydra-fsl/blob/master/pydra/tasks/fsl/conftest.py

import os
import shutil
import pytest
import py.path as pp
from tempfile import mkdtemp

TEST_DATADIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "tests/data"))
temp_folder = mkdtemp()
data_dir = os.path.join(temp_folder, "data")
shutil.copytree(TEST_DATADIR, data_dir)


@pytest.fixture(autouse=True)
def _docdir(request):
    doctest_plugin = request.config.pluginmanager.getplugin("doctest")
    if isinstance(request.node, doctest_plugin.DoctestItem):

        # get the fixture dynamically by its name
        tmpdir = pp.local(data_dir)

        # chdir only for duration of the test
        with tmpdir.as_cwd():
            yield

    else:
        # For normal tests, yield:
        yield


def pytest_unconfigure(config):
    shutil.rmtree(temp_folder)
