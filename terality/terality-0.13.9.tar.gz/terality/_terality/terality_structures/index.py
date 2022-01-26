from typing import Set

import pandas as pd
from terality_serde import IndexType

from . import ClassMethod, Struct, StructIterator


class ClassMethodIndex(ClassMethod):
    _class_name: str = IndexType.INDEX
    _pandas_class = pd.Index


class Index(Struct, metaclass=ClassMethodIndex):
    """
    A terality Index, an immutable sequence used for indexing and alignment. The basic object storing axis labels for all terality objects.
    This behaves exactly like a pandas.Index : https://pandas.pydata.org/docs/reference/api/pandas.Index.html.

    The most common ways to build a terality Index are the following :


    - instantiating from a pandas.Index:
    >>> index = terality.Index(index_pd)

    - using the constructor (with low amount of data):
    >>> index = terality.Index(["A", "B", "C"])
    >>> index
    Index(['A', 'B', 'C'], dtype='object')
    """

    _pandas_class_instance = pd.Index([])
    _accessors = {"str"}
    _additional_methods = Struct._additional_methods | {"get_range_auto"}
    _indexers: Set[str] = set()

    def __iter__(self):
        return StructIterator(self)

    def to_list(self):
        pd_index = self._call_method(None, "to_pandas")
        return pd_index.to_list()

    def tolist(self):
        return self.to_list()


class ClassMethodMultiIndex(ClassMethodIndex):
    _class_name: str = IndexType.MULTI_INDEX
    _pandas_class = pd.MultiIndex


class MultiIndex(Index, metaclass=ClassMethodMultiIndex):
    """
    A terality MultiIndex. A multi-level, or hierarchical, index object for terality objects.
    This behaves exactly like a pandas.MultiIndex : https://pandas.pydata.org/docs/reference/api/pandas.MultiIndex.html.

    The most common ways to build a terality MultiIndex are the following :

    - instantiating from a pandas.MultiIndex:
    >>> index = terality.MultiIndex(index_pd)

    - using one of the helper method MultiIndex.from_arrays(), MultiIndex.from_product() and MultiIndex.from_tuples():
    >>> arrays = [[1, 1, 2, 2], ['red', 'blue', 'red', 'blue']]
    >>> terality.MultiIndex.from_arrays(arrays, names=['number', 'color'])
        MultiIndex([(1,  'red'),
                    (1, 'blue'),
                    (2,  'red'),
                    (2, 'blue')],
                   names=['number', 'color']
    """

    _pandas_class_instance = pd.MultiIndex(levels=[[0, 1], [2, 3]], codes=[[0, 1], [0, 1]])


class ClassMethodDatetimeIndex(ClassMethodIndex):
    _class_name: str = IndexType.DATETIME_INDEX
    _pandas_class = pd.DatetimeIndex


class DatetimeIndex(Index, metaclass=ClassMethodDatetimeIndex):
    """
    A terality DatetimeIndex, an immutable sequence of datetime64 data.
    This behaves exactly like a pandas.DatetimeIndex : https://pandas.pydata.org/docs/reference/api/pandas.DatetimeIndex.html.

    The most common ways to build a terality DatetimeIndex are the following :

    - using terality.to_datetime:
    >>> index = terality.to_datetime(['3/11/2000', '3/12/2000', '3/13/2000'])
    >>> index
    DatetimeIndex(['2000-03-11', '2000-03-12', '2000-03-13'], dtype='datetime64[ns]', freq=None)

    - instantiating from a pandas.DatetimeIndex:
    >>> index_pd = pandas.to_datetime(['3/11/2000', '3/12/2000', '3/13/2000'])
    >>> index = terality.DatetimeIndex(index_pd)
    DatetimeIndex(['2000-03-11', '2000-03-12', '2000-03-13'], dtype='datetime64[ns]', freq=None)
    """

    _pandas_class_instance = pd.DatetimeIndex([])


class ClassMethodInt64Index(ClassMethodIndex):
    _class_name: str = IndexType.INT64_INDEX
    _pandas_class = pd.Int64Index


class Int64Index(Index, metaclass=ClassMethodInt64Index):
    """"""  # pylint: disable = empty-docstring

    __doc__ += Index.__doc__  # type: ignore[operator]
    _pandas_class_instance = pd.Int64Index([])


class ClassMethodFloat64Index(ClassMethodIndex):
    _class_name: str = IndexType.FLOAT64_INDEX
    _pandas_class = pd.Float64Index


class Float64Index(Index, metaclass=ClassMethodFloat64Index):
    """"""  # pylint: disable = empty-docstring

    __doc__ += Index.__doc__  # type: ignore[operator]
    _pandas_class_instance = pd.Float64Index([])
