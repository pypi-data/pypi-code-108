# test for functions that plot all the images. Use pytest.long_run to avoid running it for development
import os
import sys

import pytest
import tempfile
import shutil

import qa4sm_reader.plot_all as pa


# if sys.platform.startswith("win"):
#     pytestmark = pytest.mark.skip(
#         "Failing on Windows."
#     )


@pytest.fixture
def plotdir():
    plotdir = tempfile.mkdtemp()

    return plotdir


def test_plot_all(plotdir):
    """Plot all - including metadata based plots - to temporary directory and count files"""
    testfile = '0-ISMN.soil_moisture_with_1-C3S.sm.nc'
    testfile_path = os.path.join(
        os.path.dirname(__file__), '..', 'tests', 'test_data', 'metadata', testfile
    )

    pa.plot_all(
        filepath=testfile_path,
        out_dir=plotdir,
        save_all=True,
        save_metadata=True,
    )

    assert len(os.listdir(plotdir)) == 60
    assert all(os.path.splitext(file)[1] in [".png", ".csv"] for file in os.listdir(plotdir)), \
        "Not all files have been saved as .png or .csv"

    shutil.rmtree(plotdir)
