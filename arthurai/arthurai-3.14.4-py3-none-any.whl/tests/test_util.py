from datetime import datetime
from typing import Dict, Any, Union, List
from unittest.mock import patch, MagicMock

import numpy as np
import pytest
import pytz

from arthurai.common.exceptions import UserValueError
from arthurai.util import generate_timestamps, normal_random_ints_fixed_sum

MOCK_NOW_VALUE = datetime(2020, 11, 13, tzinfo=pytz.utc)

generate_timestamp_value_cases = [
    ({'total': 8},
     np.array([1, 1, 1, 1, 1, 1, 1, 1]),
     [pytz.utc.localize(dt) for dt in
      (datetime(2020, 11, 6), datetime(2020, 11, 7), datetime(2020, 11, 8), datetime(2020, 11, 9),
       datetime(2020, 11, 10), datetime(2020, 11, 11), datetime(2020, 11, 12), datetime(2020, 11, 13))]),
    ({'total': 4, 'duration': "2d"},
     np.array([1, 2, 1]),
     [pytz.utc.localize(dt) for dt in
      (datetime(2020, 11, 11), datetime(2020, 11, 12), datetime(2020, 11, 12), datetime(2020, 11, 13))]),
    ({'total': 10, 'duration': "3d"},
     np.array([3, 3, 2, 2]),
     [pytz.utc.localize(dt) for dt in
      (datetime(2020, 11, 10), datetime(2020, 11, 10), datetime(2020, 11, 10), datetime(2020, 11, 11),
       datetime(2020, 11, 11), datetime(2020, 11, 11), datetime(2020, 11, 12), datetime(2020, 11, 12),
       datetime(2020, 11, 13), datetime(2020, 11, 13))]),
    ({'total': 1, 'duration': "3d"}, None, UserValueError),
    ({'total': 11, 'duration': "3h", 'freq': "H"},
     np.array([3, 4, 2, 2]),
     [pytz.utc.localize(dt) for dt in
      (datetime(2020, 11, 12, hour=21), datetime(2020, 11, 12, hour=21), datetime(2020, 11, 12, hour=21),
      datetime(2020, 11, 12, hour=22), datetime(2020, 11, 12, hour=22), datetime(2020, 11, 12, hour=22),
      datetime(2020, 11, 12, hour=22), datetime(2020, 11, 12, hour=23), datetime(2020, 11, 12, hour=23),
      datetime(2020, 11, 13), datetime(2020, 11, 13))]),
    ({'total': 4, 'duration': "2d", 'end': datetime(2020, 12, 13, tzinfo=pytz.utc)},
     np.array([2, 1, 1]),
     [pytz.utc.localize(dt) for dt in
      (datetime(2020, 12, 11), datetime(2020, 12, 11), datetime(2020, 12, 12), datetime(2020, 12, 13))]),
]


@pytest.mark.parametrize("kwargs,repeats,expected", generate_timestamp_value_cases)
def test_generate_timestamps_values(kwargs: Dict[str, Any], repeats: np.ndarray, expected: Union[List[datetime], type]):
    """
    Test that generate_timestamps() outputs match expected values for a few cases
    """
    mock_now = MagicMock()
    mock_now.return_value = MOCK_NOW_VALUE
    mock_randints = MagicMock(normal_random_ints_fixed_sum)
    mock_randints.return_value = repeats
    with patch("arthurai.util._datetime_now", mock_now):
        with patch("arthurai.util.normal_random_ints_fixed_sum", mock_randints):
            if isinstance(expected, list):
                actual = generate_timestamps(**kwargs)
                assert actual == expected
            elif issubclass(expected, Exception):
                with pytest.raises(expected):
                    generate_timestamps(**kwargs)
            else:
                raise TypeError("did not understand 'expected' value")


random_ints_cases = [
    {'num_values': 47, 'total_sum': 58730},
    {'num_values': 47, 'total_sum': 47},
    {'num_values': 13, 'total_sum': 2302},
    {'num_values': 92, 'total_sum': 50238}
]


@pytest.mark.parametrize("kwargs", random_ints_cases)
def test_normal_random_ints_fixed_sum(kwargs: Dict[str, Any]):
    np.random.seed(91)
    actual = normal_random_ints_fixed_sum(**kwargs)
    assert len(actual) == kwargs['num_values']
    assert actual.sum() == kwargs['total_sum']
