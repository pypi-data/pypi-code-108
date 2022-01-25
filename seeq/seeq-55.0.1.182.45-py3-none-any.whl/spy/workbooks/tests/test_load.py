import os

import pytest

from seeq import spy
from seeq.base import system


def get_example_export_path():
    return system.cleanse_path(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'Documentation',
                                            'Example Export'))


def load_example_export():
    return spy.workbooks.load(get_example_export_path())


@pytest.mark.system
def test_load_folder():
    workbooks = load_example_export()
    assert len(workbooks) == 2


@pytest.mark.system
def test_load_zipfile():
    workbooks = spy.workbooks.load(get_example_export_path() + '.zip')
    assert len(workbooks) == 2
