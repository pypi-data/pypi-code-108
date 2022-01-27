import abc
from typing import Union

from shyft.time_series import TimeAxis, TsVector, TimeSeries

from shyft.dashboard.time_series.state import Quantity, Unit, State


class TsAdapter(abc.ABC):
    """
    This object defines the data for a data source.
    With the __call__ data for a given time axis and unit can be provided to be viewed by the ts viewer.
    The call method must return a Unit annotated TsVector with the time series to show.
    """
    @abc.abstractmethod
    def __call__(self, *, time_axis: TimeAxis, unit: Unit) -> Quantity[TsVector]:
        pass


class BasicTsAdapter(TsAdapter):
    """
    This class is the most basic implementation of a TsAdapter which takes a TimeSeries and returns its evaluation when
    called
    """
    def __init__(self, data: Union[TimeSeries, TsVector, State.Quantity], unit_registry, unit: str):
        self.data = data
        self.unit_registry = unit_registry
        self.unit = unit

    def __call__(self, *, time_axis: TimeAxis, unit: Unit) -> Quantity[TsVector]:
        o_tsv = TsVector([self.data.average(time_axis)])
        return self.unit_registry.Quantity(o_tsv, self.unit)
