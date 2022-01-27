from simses.commons.timeseries.average.average import Average
from simses.commons.timeseries.timevalue import TimeValue


class MeanAverage(Average):
    """
    MeanAverage provides a arithmetic mean behaviour of averaging.
    """

    def __init__(self):
        super().__init__()

    def average(self, data: [TimeValue]) -> float:
        values: [float] = list()
        for d in data:
            values.append(d.value)
        mean = sum(values) / len(values)
        return mean
