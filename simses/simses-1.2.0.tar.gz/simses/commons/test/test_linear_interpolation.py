import pytest
from simses.commons.timeseries.interpolation.linear_interpolation import LinearInterpolation
from simses.commons.timeseries.timevalue import TimeValue


@pytest.fixture()
def uut():
    return LinearInterpolation()


@pytest.mark.parametrize('time, recent_time, recent_value, last_time, last_value, result',
                         [
                             (0, 0, 0, 10, 10, 0),
                             (10, 0, 0, 10, 10, 10),
                             (5, 0, 0, 10, 10, 5)
                         ]
                         )
def test_next(time, recent_time, recent_value, last_time, last_value, result, uut):
    recent = TimeValue(tstmp=recent_time, value=recent_value)
    last = TimeValue(tstmp=last_time, value=last_value)
    assert abs(uut.interpolate(time, recent, last) - result) < 1e-10
