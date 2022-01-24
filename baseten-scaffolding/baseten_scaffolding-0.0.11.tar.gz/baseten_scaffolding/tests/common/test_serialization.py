import datetime
import decimal
import uuid

import numpy as np
import pytest

from baseten_scaffolding.scaffold_templates.common.serialization import (
    b10_msgpack_deserialize, b10_msgpack_serialize, is_b10_serializable
)


JSON_TYPE_INSTANCES = [
    "Hello World",
    5,
    5.4,
    False,
    None,
    {'bar': 'baz'},
    [1, 2, 3, 4],
    [1.2, 2.3, 3.1],
    {'foo': [1, 2, 3]},
]


NUMPY_TYPE_INSTANCES = [
    np.array([1.01, 2.71828, 3.14, 0, 1000]),
    {'foo': np.array([1.01, 2.71828, 3.14, 0, 1000])},
    np.array([[1, 2, 3], [4, 5, 6]]),
]


@pytest.mark.parametrize(
    'test_value',
    JSON_TYPE_INSTANCES
)
def test_json_is_b10_serializable(test_value):
    assert is_b10_serializable(test_value)


@pytest.mark.parametrize(
    'test_value',
    NUMPY_TYPE_INSTANCES
)
def test_numpy_is_b10_serializable(test_value):
    assert is_b10_serializable(test_value)


def test_object_is_not_b10_serializable():
    class Object:
        pass
    assert not is_b10_serializable(Object())


@pytest.mark.parametrize(
    'test_value',
    JSON_TYPE_INSTANCES
)
def test_json_serialize_and_unserialize(test_value):
    results = b10_msgpack_deserialize(b10_msgpack_serialize(test_value))
    assert results == test_value


@pytest.mark.parametrize(
    'test_value',
    NUMPY_TYPE_INSTANCES
)
def test_numpy_serialize_and_unserialize(test_value):
    results = b10_msgpack_deserialize(b10_msgpack_serialize(test_value))
    np.array_equal(results, test_value)


def test_datetime_serialize():
    today_date = datetime.date.today()
    now_datetime = datetime.datetime.now()
    now_time = now_datetime.time()
    an_hour = datetime.timedelta(hours=1)

    assert today_date == b10_msgpack_deserialize(b10_msgpack_serialize(today_date))
    assert datetime.datetime.fromisoformat(now_datetime.isoformat()) == \
           b10_msgpack_deserialize(b10_msgpack_serialize(now_datetime))
    assert datetime.time.fromisoformat(now_time.isoformat()) == \
           b10_msgpack_deserialize(b10_msgpack_serialize(now_time))
    assert an_hour == b10_msgpack_deserialize(b10_msgpack_serialize(an_hour))


def test_nested_datetime_serialize():
    today_date = datetime.date.today()
    t_delta = datetime.timedelta(hours=1)
    d = {'a': 123, 'b': [today_date, today_date - t_delta], 'c': t_delta}
    assert d == b10_msgpack_deserialize(b10_msgpack_serialize(d))


@pytest.mark.parametrize(
    'test_value',
    [
        uuid.uuid4(),
        decimal.Decimal('10.99'),
    ]
)
def test_special_types(test_value):
    assert test_value == b10_msgpack_deserialize(b10_msgpack_serialize(test_value))
