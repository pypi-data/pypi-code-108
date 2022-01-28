import pytest

from ._event import BaseEventForTest, BaseEventWithError, NewEventForTest


def test_valid_mandatory_field():
    class NewEvent(BaseEventWithError):
        src = '192.168.0.1'

    with pytest.raises(ValueError):
        NewEvent()


def test_valid_extension_field():
    class NewEvent(BaseEventForTest):
        src = {'error data'}

    with pytest.raises(ValueError):
        NewEvent()()


def test_valid_mandatory_field_in_fly():
    with pytest.raises(ValueError):
        NewEventForTest()(Version='error')


def test_valid_extension_field_on_fly():
    with pytest.raises(ValueError):
        NewEventForTest()(src='error')
