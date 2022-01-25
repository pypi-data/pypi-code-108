import pandas as pd
from terality_serde import StructType

from . import ClassMethod, Struct
from .structure import StructIterator


class ClassMethodSeries(ClassMethod):
    _class_name: StructType = StructType.SERIES
    _pandas_class = pd.Series
    _additional_class_methods = ClassMethod._additional_class_methods | {
        "random",
        "random_integers",
    }


class Series(Struct, metaclass=ClassMethodSeries):
    """
    A terality.Series to handle one-dimensional data with axis labels.
    This behaves exactly like a pandas.Series : https://pandas.pydata.org/docs/reference/api/pandas.Series.html.

    The most common ways to build a terality Series are the following :

    - selecting a column of a terality DataFrame :
    >>> df = terality.DataFrame({"A": ["x", "y", "z"]})
    >>> df["A"]
    0    x
    1    y
    2    z
    Name: A, dtype: object

    - instantiating from a pandas.Series:
    >>> series_pd = pandas.Series(["x", "y", "z"], name="A")
    >>> series = terality.Series(series_pd)
    0    x
    1    y
    2    z
    Name: A, dtype: object

    - using the constructor:
    >>> series = terality.Series(["x", "y", "z"], name="A")
    >>> series
    0    x
    1    y
    2    z
    Name: A, dtype: object
    """

    _pandas_class_instance = pd.Series(dtype="float64")
    _accessors = {"str", "dt"}
    _additional_methods = Struct._additional_methods | {"get_range_auto", "random"}

    def __iter__(self):
        return StructIterator(self)

    def to_dict(self, into: type = dict):
        pd_series = self._call_method(None, "to_pandas")
        return pd_series.to_dict(into=into)

    def to_list(self):
        pd_series = self._call_method(None, "to_pandas")
        return pd_series.to_list()

    def tolist(self):
        return self.to_list()
