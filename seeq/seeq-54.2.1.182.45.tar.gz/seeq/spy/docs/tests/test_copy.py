import os
import tempfile

import pytest

from seeq.base import system
from seeq.spy.docs import _copy


@pytest.mark.unit
def test_copy():
    with tempfile.TemporaryDirectory() as temp_folder:
        long_folder_name = os.path.join(temp_folder, 'long_' * 10)
        _copy.copy(long_folder_name)

        assert os.path.exists(long_folder_name)

        for file_name in _copy.ADVANCED_ONLY_FILES:
            assert not os.path.exists(os.path.join(long_folder_name, file_name))

        with pytest.raises(RuntimeError):
            _copy.copy(long_folder_name)

        assert os.path.exists(long_folder_name)

        _copy.copy(long_folder_name, overwrite=True, advanced=True)

        assert os.path.exists(long_folder_name)
        assert os.path.exists(os.path.join(long_folder_name, 'spy.workbooks.ipynb'))
        assert os.path.exists(os.path.join(long_folder_name, 'Advanced Reports and Dashboards.ipynb'))

        system.removetree(long_folder_name)
