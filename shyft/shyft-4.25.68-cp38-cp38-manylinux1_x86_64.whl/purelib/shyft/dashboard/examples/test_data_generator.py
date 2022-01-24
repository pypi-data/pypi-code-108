import numpy as np
from time import sleep
from shyft.time_series import UtcPeriod, point_interpretation_policy, TimeSeries, DoubleVector, TsVector, TimeAxis, Calendar
from shyft.dashboard.time_series.state import State, Unit, Quantity
from shyft.dashboard.time_series.sources.ts_adapter import TsAdapter


class ExampleTsAdapterSine(TsAdapter):

    def __init__(self, unit_to_decorate: Unit, time_range: UtcPeriod,
                 point_interpretation: point_interpretation_policy = None, async_on=False) -> None:
        self.async_on = async_on
        self.cal = Calendar()
        self.point_interpretation = point_interpretation or point_interpretation_policy.POINT_INSTANT_VALUE
        self.unit_to_decorate = unit_to_decorate
        # generate a time series with random data with dt 1h
        n = time_range.diff_units(self.cal, self.cal.HOUR)
        ta = TimeAxis(time_range.start, self.cal.HOUR, n)
        # random singal with sin + cos + white noise
        t = ta.time_points[:-1]
        f1 = int(1./time_range.timespan())  # EA trying to make it work by converting to int
        f2 = int(4./time_range.timespan())  # EA trying to make it work by converting to int
        vals = np.sin(2.*np.pi*f1*t) + np.cos(2.*np.pi*f2*t) + np.random.randn(n)*0.25 + np.random.rand(1)*10
        vals1 = np.sin(2.*np.pi*f1*t) + np.cos(2.*np.pi*f2*t) + np.random.randn(n)*0.25 + np.random.rand(1)*10
        vals2 = np.sin(2.*np.pi*f1*t) + np.cos(2.*np.pi*f2*t) + np.random.randn(n)*0.25 + np.random.rand(1)*10
        self.ts1 = TimeSeries(ta, DoubleVector.from_numpy(vals), self.point_interpretation) - 1
        self.ts2 = TimeSeries(ta, DoubleVector.from_numpy(vals1), self.point_interpretation)
        self.ts3 = TimeSeries(ta, DoubleVector.from_numpy(vals2), self.point_interpretation) + 1

    def __call__(self, *, time_axis, unit) -> Quantity[TsVector]:
        # average the known values to fit to the current given time axis
        if self.async_on:
            sleep(np.random.randint(1, 4, 1)[0])
        ts1 = self.ts1.average(time_axis)
        ts1.set_point_interpretation(self.point_interpretation)
        ts2 = self.ts2.average(time_axis)
        ts2.set_point_interpretation(self.point_interpretation)
        ts3 = self.ts3.average(time_axis)
        ts3.set_point_interpretation(self.point_interpretation)
        tsv = TsVector([ts1, ts2, ts3])

        return State.unit_registry.Quantity(tsv, self.unit_to_decorate)
