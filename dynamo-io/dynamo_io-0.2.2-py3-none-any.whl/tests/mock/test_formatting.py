from dynamo_io import mock


def test_string():
    """Should encode as a string."""
    assert mock.string("foo") == {"S": "foo"}


def test_integer():
    """Should encode as integer number."""
    assert mock.integer(12.12) == {"N": "12"}


def test_float():
    """Should encode as a float number."""
    assert mock.number(12.12) == {"N": "12.12"}


def test_boolean():
    """Should encode as a boolean number."""
    assert mock.boolean(42) == {"BOOL": True}


def test_timestamp():
    """Should encode as a timestamp."""
    assert mock.timestamp() == {"N": "1577836800"}


def test_date_time():
    """Should encode as a datetime."""
    assert mock.date_time() == {"S": "2020-01-01T00:00:00Z"}
