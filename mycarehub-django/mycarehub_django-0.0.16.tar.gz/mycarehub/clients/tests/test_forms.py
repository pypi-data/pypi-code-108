from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from mycarehub.clients.forms import validate_date_past


def test_validate_date_wrong_format():
    value = "this is definitely not a date"
    with pytest.raises(ValidationError) as c:
        validate_date_past(value)

    assert "not a date" in str(c.value.messages)


def test_validate_date_future():
    today = timezone.now().date()
    future = today + timedelta(days=7)
    value = future
    with pytest.raises(ValidationError) as c:
        validate_date_past(value)

    assert "is a date that is in the future" in str(c.value.messages)


def test_validate_date_past():
    today = timezone.now().date()
    past = today - timedelta(days=7)
    value = past
    validate_date_past(value)  # no exception
