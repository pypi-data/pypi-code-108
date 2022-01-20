# Nice to have but unused!
# Would prove useful if we wish to create a more robust decoration of pandas

from typing import Optional, Dict
import inspect
from functools import wraps

from pandas._typing import Axes, Dtype
import pandas as pd
import numpy as np

def __pandas_to_banner(decorator):
    def decorate(cls):
        functions = inspect.getmembers(cls, predicate=inspect.isfunction) #Only instance methods

        for func in functions:
            if func[0] not in ('__init__'):
                setattr(
                    cls, 
                    func[0], 
                    decorator(func[-1])
                )
        
        return cls
    return decorate

def __pandas_decorator(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response = func(*args, **kwargs)
        
        if isinstance(response, pd.DataFrame):
            response = DataFrame.from_pd_df(response)

        elif isinstance(response, pd.Series):
            response = Series.from_pd_series(response)
        
        return response

    return inner
    
@__pandas_to_banner(__pandas_decorator)
class DataFrame(pd.DataFrame):
    def __init__(self, data=None, index: Optional[Axes]=None, columns: Optional[Axes]=None, dtype: Optional[Dtype]=None, copy: bool=False):
        super().__init__(
            data=data, index=index, columns=columns, dtype=dtype, copy=copy
        )

    @classmethod
    def from_pd_df(cls, df: pd.DataFrame):
        ''' Cast Pandas.DataFrame into Banner.DataFrame'''
        return cls(data=df)

    @property
    def coulombic_efficiency(self):
        if not all(col in self for col in ('cap_dchg', 'cap_chg')):
            return

        return self['cap_dchg'] / self['cap_chg'] * 100

@__pandas_to_banner(__pandas_decorator)
class Series(pd.Series):
    def __init__(self, data=None, index=None, dtype=None, name=None, copy=False, fastpath=False):
        super().__init__(
            data=data, index=index, dtype=dtype, name=name, copy=copy, fastpath=fastpath
        )

    @classmethod
    def from_pd_series(cls, series: pd.Series):
        return cls(data=series)