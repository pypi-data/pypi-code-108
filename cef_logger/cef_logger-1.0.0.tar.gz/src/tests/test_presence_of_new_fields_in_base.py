import pytest

from ._event import BaseEventForTest, NewEventForTest


@pytest.mark.parametrize('field', [*BaseEventForTest.__fields__])
def test_presence_of_new_fields_in_base(field):
    assert hasattr(NewEventForTest(), field)
