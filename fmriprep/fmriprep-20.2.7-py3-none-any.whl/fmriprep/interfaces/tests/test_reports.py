import pytest

from ..reports import get_world_pedir


@pytest.mark.parametrize("orientation,pe_dir,expected", [
    ('RAS', 'j', 'Posterior-Anterior'),
    ('RAS', 'j-', 'Anterior-Posterior'),
    ('RAS', 'i', 'Left-Right'),
    ('RAS', 'i-', 'Right-Left'),
    ('RAS', 'k', 'Inferior-Superior'),
    ('RAS', 'k-', 'Superior-Inferior'),
    ('LAS', 'j', 'Posterior-Anterior'),
    ('LAS', 'i-', 'Left-Right'),
    ('LAS', 'k-', 'Superior-Inferior'),
    ('LPI', 'j', 'Anterior-Posterior'),
    ('LPI', 'i-', 'Left-Right'),
    ('LPI', 'k-', 'Inferior-Superior'),
])
def test_get_world_pedir(tmpdir, orientation, pe_dir, expected):
    assert get_world_pedir(orientation, pe_dir) == expected
