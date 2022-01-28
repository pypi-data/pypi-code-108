# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from numpy.testing import assert_array_equal
from eelbrain import load
from eelbrain.testing import file_path
import pytest


@pytest.mark.skip("Broken with recent pyarrow versions")
def test_feather_io():
    ds = load.feather(file_path('mini.feather'))
    assert_array_equal(ds['participant'], [1, 1])
    assert_array_equal(ds['condition'], ['3B', '3B'])
