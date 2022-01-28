import os
import itertools
import pytest
from eelbrain.testing import TempDir

from ..stc_dataset import DatasetSTCLoader


def _create_fake_files(tmpdir):
    """Write empty stc files to tmpdir to be detected
    by the DatasetSTCLoader"""
    subjects = ("R0000", "A9999")
    factor1 = ("level-a", "level-b")
    factor2 = ("noun", "verb")
    folder_combos = itertools.product(factor1, factor2)
    file_combos = itertools.product(subjects, factor1, factor2)
    folders = ["_".join(f) for f in folder_combos]
    files = ["_".join(f) + "-lh.stc" for f in file_combos]
    for f in folders:
        folder_path = os.path.join(tmpdir, f)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        files_to_write = filter(lambda x: f in x, files)
        for fw in files_to_write:
            file_path = os.path.join(folder_path, fw)
            open(file_path, "a").close()


def test_loader():
    tmp = TempDir()
    _create_fake_files(tmp)
    loader = DatasetSTCLoader(tmp)
    levels = loader.levels
    # check detected level names
    assert "level-a" in levels[0]
    assert "level-b" in levels[0]
    assert "noun" in levels[1]
    assert "verb" in levels[1]
    assert "R0000" in loader.subjects
    with pytest.raises(ValueError):
        loader.set_factor_names(["only-one-factor"])
    loader.set_factor_names(["factor1", "factor2"])
    assert loader.design_shape == "2 x 2"
    ds = loader.make_dataset(load_stcs=False)
    assert "factor1" in ds
    assert "factor2" in ds
    assert "subject" in ds
    assert ds["subject"].random
