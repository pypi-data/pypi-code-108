# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from pathlib import Path

from eelbrain import datasets, load, save
from eelbrain.testing import TempDir, requires_pyarrow, assert_dataset_equal


@requires_pyarrow
def test_arrow_io():
    tempdir = TempDir()
    ds = datasets.get_uts()

    path = Path(tempdir) / 'test.arrow'
    save.arrow(ds, path)
    ds2 = load.arrow(path)
    assert_dataset_equal(ds2, ds)
