import pandas as pd
import numpy as np
import math

import matplotlib.pyplot as plt

from bluebelt.core.checks import check_kwargs

import bluebelt.core.decorators

import bluebelt.core.index

import warnings

def _get_grouped_result(self, result):

    # get the index
    if self.iso:
        index = bluebelt.core.index.IsoDatetimeMultiIndex.from_frame(result.index.to_frame(index=False))
    else:
        index = bluebelt.core.index.DatetimeMultiIndex.from_frame(result.index.to_frame(index=False))

    # get the return object
    if isinstance(result, pd.Series):
        return pd.Series(index=index, data=result.values, dtype=self._obj.dtype, name=self._obj.name)
    elif isinstance(self._obj, pd.DataFrame):
        return pd.DataFrame(index=index, data=result.values, columns=self._obj.columns)
    else:
        return None

def resolution_methods(cls):

    def sum(self):
        result = self.grouped.sum()
        return _get_grouped_result(self, result)

    def mean(self):
        result = self.grouped.mean()
        return _get_grouped_result(self, result)

    def var(self):
        result = self.grouped.var()
        return _get_grouped_result(self, result)
            
    def std(self):
        result = self.grouped.std()
        return _get_grouped_result(self, result)

    def min(self):
        result = self.grouped.min()
        return _get_grouped_result(self, result)

    def max(self):
        result = self.grouped.max()
        return _get_grouped_result(self, result)

    
    def count(self):
        result = self.grouped.count()
        return _get_grouped_result(self, result)
    
    def value_range(self):
        result = self.grouped.apply(lambda x: x.max() - x.min())
        return _get_grouped_result(self, result)

    def diff_quantity(self):
        result = ( (self.grouped.sum() - self.grouped.sum().shift()) / self.grouped.sum().shift() ).abs().fillna(0)
        return _get_grouped_result(self, result)

    def diff_distribution(self, **kwargs):

        values = kwargs.get('values', None)

        # _obj = self._obj[values] if isinstance(self._obj, pd.DataFrame) and values is not None else
        
        if isinstance(self._obj, pd.Series):
            index_groups = self.grouped.obj.index.names

            if (self.grouped.obj.index.names.index(self.level) + 1) < len(index_groups):
                group = index_groups[self.grouped.obj.index.names.index(self.level) + 1]
                result = self.grouped.apply(lambda s: s.groupby(group).sum()).unstack(level=-1)
                result = pd.Series((result - result.shift().multiply((result.sum(axis=1) / result.sum(axis=1).shift()), axis=0)).abs().sum(axis=1) / (result.sum(axis=1) * 2), name=self._obj.name)
            else:
                result = pd.Series(index=self.grouped.sum().index, data=[0]*self.grouped.sum().size, name=self._obj.name)

            # final assembly
            return _get_grouped_result(self, result)
        else:
            raise ValueError("diff_distribution can not be called form a pandas.DataFrame Groupby object")


    setattr(cls, 'sum', sum)
    setattr(cls, 'mean', mean)
    setattr(cls, 'var', var)
    setattr(cls, 'std', std)
    setattr(cls, 'min', min)
    setattr(cls, 'max', max)
    setattr(cls, 'count', count)
    setattr(cls, 'value_range', value_range)
    setattr(cls, 'diff_quantity', diff_quantity)
    setattr(cls, 'diff_distribution', diff_distribution)
    
    return cls

@bluebelt.core.decorators.class_methods
@resolution_methods
class GroupByDatetimeIndex():
    """
    Group a pandas.Series or pandas.DataFrame by DateTime index and apply a specific function.
        arguments
        series: pandas.Series
        how: str
            a string with date-time keywords that can be parsed to group the index
            keywords:
            
            default value "week"

        Apply one of the following functions:
            .sum()
            .mean()
            .min()
            .max()
            .std()
            .value_range()
            .count()
            .subsize_count()

        e.g. series.blue.data.group_index(how="week").sum()
        
    """
    
    def __init__(self, _obj, level="week", iso=True, **kwargs):

        self._obj = _obj
        self.level = level
        self.iso = iso
        self.nrows = self._obj.shape[0]
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        
        # check for iso compatibility
        if self.iso and ('month' in self.level):
            warnings.warn(f'rule={self.level} is not possible when using iso=True; iso will be set to False', Warning)
            self.iso = False
        elif not self.iso and ('week' in self.level):
            warnings.warn(f'rule={self.level} is not possible when using iso=False; iso will be set to True', Warning)
            self.iso = True

        # check the index type
        if not isinstance(self._obj.index, bluebelt.core.index.IsoDatetimeMultiIndex):
            # convert to isodatetimemultiindex or datetimemultiindex
            if self.iso:
                index = bluebelt.core.index.IndexToolkit(self._obj.index, **kwargs).to_isodatetimemultiindex()
            else:
                index = bluebelt.core.index.IndexToolkit(self._obj.index, **kwargs).to_datetimemultiindex()
        else:
            index = self._obj.index

        # set self.grouped
        if isinstance(self._obj, pd.Series):
            self.grouped = pd.Series(index=index, data=self._obj.values, dtype=self._obj.dtype, name=self._obj.name).groupby(level=self.level)
        elif isinstance(self._obj, pd.DataFrame):
            self.grouped = pd.DataFrame(index=index, data=self._obj.values, columns=self._obj.columns).groupby(level=self.level)
        else:
            pass #self._obj = None

        # else:
        #     self.grouped = None

    def __str__(self):
        return ""
    
    def __repr__(self):
        return self.grouped.__repr__()


    def subsize_count(self, count=3, size=1):

            """
            Count the number of times a list of <count> items with size <size> fit in the groupby object (which is a pandas Series)
            e.g.
            groupby object: pd.Series([10, 8, 3, 3, 5])
            count = 3
            size = 1

            returns 9

            step 0: (3, 3, 5, 8, 10)
            step 1: (3, 3, 4, 7, 9)
            step 2: (3, 3, 3, 6, 8)
            step 3: (2, 3, 3, 5, 7)
            step 4: (2, 2, 3, 4, 6)
            step 5: (2, 2, 2, 3, 5)
            step 6: (1, 2, 2, 2, 4)
            step 7: (1, 1, 1, 2, 3)
            step 8: (0, 1, 1, 1, 2)
            step 9: (0, 0, 0, 1, 1)

            """
            if isinstance(count, (float, int)):
                count = [int(count)]
            
            result = {}
            for c in count:
                result[c] = self.grouped.apply(lambda x: _subsize_count(series=x, count=c, size=size)).values
            result = pd.DataFrame(result, index=self.grouped.groups.keys()) #self.grouped.apply(lambda x: _subsize_count(series=x, count=count, size=size))
            
            if len(count) == 2:
                _dict = {}
                for val in range(int(result.values.min()), int(result.values.max())):

                    under = np.where(val < result.iloc[:,0:2].min(axis=1), result.iloc[:,0:2].min(axis=1) - val, 0)
                    over = np.where(val > result.iloc[:,0:2].max(axis=1), val - result.iloc[:,0:2].max(axis=1), 0)
                    _dict[val] = under + over

                # get the keys with the most zeros
                _o_dict = {key: len([x for x in value if x == 0]) for key, value in _dict.items()}
                most_zeros = _o_dict.get(max(_o_dict, key=_o_dict.get))

                _dict = {key: value for (key, value) in _dict.items() if _o_dict.get(key) == most_zeros}

                # get the smallest sum
                _o_dict = {key: sum(value) for (key, value) in _dict.items()}
                min_val = _o_dict.get(min(_o_dict, key=_o_dict.get))
                _dict = {key: value for (key, value) in _dict.items() if _o_dict.get(key) == min_val}

                # build the optimum series and merge with result
                optimum = tuple(_dict.keys()) if len(_dict.keys()) > 1 else list(_dict.keys())[0]
                optimum = pd.Series(index=result.index, data=[optimum]*result.shape[0], name='optimum')

                result = result.merge(optimum, left_index=True, right_index=True)

            return result

def _subsize_count(series, count=3, size=1):
    series = pd.Series(series)/size
    result = series.sum()*count
    for i in range(count, 0, -1):
        result = min(result, math.floor(series.nsmallest(len(series) - count + i).sum() / i))
    return result

def _subseries_count(series, subseries=None, **kwargs):
    series = pd.Series(series)
    subseries = pd.Series(subseries)
    result=series.sum()*subseries.sum()
    for i in range(len(subseries), 0, -1):
        result = min(result, math.floor(series.nsmallest(len(series) - len(subseries) + i).sum() / subseries.nsmallest(i).sum()))
    return result