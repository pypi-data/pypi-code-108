import pytest
from simses.commons.timeseries.average.mean_average import MeanAverage
from simses.commons.timeseries.timevalue import TimeValue


@pytest.fixture()
def uut():
    return MeanAverage()


def create_list_with(start: int, end: int) -> [TimeValue]:
    data: [TimeValue] = list()
    for value in range(start, end + 1, 1):
        data.append(TimeValue(0, value))
    return data


@pytest.mark.parametrize('start, end, result',
                         [
                             (0, 0, 0),
                             (0, 10, 5),
                             (5, 15, 10)
                         ]
                         )
def test_next(start, end, result, uut):
    data: [TimeValue] = create_list_with(start, end)
    assert abs(uut.average(data) - result) < 1e-10
