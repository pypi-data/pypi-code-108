from unittest.mock import patch
from tests.utils import TERM

from hestia_earth.models.utils.input import _new_input

class_path = 'hestia_earth.models.utils.input'


@patch(f"{class_path}._include_methodModel", side_effect=lambda n, x: n)
@patch(f"{class_path}.download_hestia", return_value=TERM)
def test_new_input(*args):
    # with a Term as string
    input = _new_input('term')
    assert input == {
        '@type': 'Input',
        'term': TERM
    }

    # with a Term as dict
    input = _new_input(TERM)
    assert input == {
        '@type': 'Input',
        'term': TERM
    }
