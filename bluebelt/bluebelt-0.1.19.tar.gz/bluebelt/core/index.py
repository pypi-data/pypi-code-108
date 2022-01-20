import warnings
import datetime
import pandas as pd

import bluebelt.core.decorators


class DatetimeMultiIndex(pd.MultiIndex):
    def __new__(cls, *args, **kwargs):
        cls._obj = super(DatetimeMultiIndex, cls).__new__(cls, *args, **kwargs)
        return cls._obj
    
    def __init__(self, level=None, *args, **kwargs):
        if 'week' in kwargs.get('names'):
            warnings.warn(f'the names have a "week" value, are you sure this should be a {type(self)} index', Warning)
        self._obj._level = self._obj.names[-1]

    def _complete(self, **kwargs):
        '''
        add missing levels to the index
        '''
        _dict = self._obj.to_frame(index=False).to_dict()

        _default_dict = {
            'year': {key: datetime.datetime.now().year for key in range(self._obj.shape[0])},
            'month': {key: 1 for key in range(self._obj.shape[0])},
            'day': {key: 1 for key in range(self._obj.shape[0])},
            'hour': {key: 0 for key in range(self._obj.shape[0])},
            'minute': {key: 0 for key in range(self._obj.shape[0])},
            'second': {key: 0 for key in range(self._obj.shape[0])},
        }

        for level, data in _default_dict.items():
            _dict[level] = _dict.get(level, _default_dict[level])
        return DatetimeMultiIndex.from_frame(pd.DataFrame.from_dict(_dict)[_default_dict.keys()])

    def to_datetimeindex(self, **kwargs):
        '''
        convert to pd.DatetimeIndex
        '''
        return pd.Index([datetime.datetime(*row) for row in self._complete()])
        
    def to_isodatetimemultiindex(self, **kwargs):
        '''
        convert to IsoDatetimeMultiIndex
        '''
    
        levels = ['year','week','day']
        level = kwargs.get('level', levels[-1])
        
        if level in levels:
            levels = levels[:levels.index(level)+1]

        return IsoDatetimeMultiIndex.from_frame(self.to_datetimeindex().isocalendar()[levels])
        
    to_isodtmi = to_isodatetimemultiindex

class DayOfYearMultiIndex(pd.MultiIndex):

    #
    # needs more testing

    
    def __new__(cls, *args, **kwargs):
        cls._obj = super(DayOfYearMultiIndex, cls).__new__(cls, *args, **kwargs)
        return cls._obj
    
    def __init__(self, *args, **kwargs):
        if 'week' in kwargs.get('names'):
            warnings.warn(f'the names have a "week" value, are you sure this should be a {type(self)} index', Warning)
        self._obj._level = self._obj.names[-1]

    def _complete(self, **kwargs):
        '''
        add missing levels to the index
        '''
        _dict = self._obj.to_frame(index=False).to_dict()

        _default_dict = {
            'year': {key: datetime.datetime.now().year for key in range(self._obj.shape[0])},
            'day': {key: key for key in range(self._obj.shape[0])},
            'hour': {key: 0 for key in range(self._obj.shape[0])},
            'minute': {key: 0 for key in range(self._obj.shape[0])},
            'second': {key: 0 for key in range(self._obj.shape[0])},
        }

        for level, data in _default_dict.items():
            _dict[level] = _dict.get(level, _default_dict[level])
        return DatetimeMultiIndex.from_frame(pd.DataFrame.from_dict(_dict)[_default_dict.keys()])

    def to_datetimeindex(self, **kwargs):
        '''
        convert to pd.DatetimeIndex
        '''
        # consider:
        # return pd.Index([datetime.datetime(row[0], 1, 1) + datetime.timedelta(row[1] - 1) for row in self._complete()])
        return pd.Index([datetime.datetime(row[0], 1, 1) + datetime.timedelta(row[1] - 1) for row in self])
        
    def to_isodatetimemultiindex(self, **kwargs):
        '''
        convert to IsoDatetimeMultiIndex
        '''
    
        levels = ['year','week','day']
        level = kwargs.get('level', levels[-1])
        
        if level in levels:
            levels = levels[:levels.index(level)+1]

        return IsoDatetimeMultiIndex.from_frame(self.to_datetimeindex().isocalendar()[levels])
        
    to_isodtmi = to_isodatetimemultiindex

class IsoDatetimeMultiIndex(pd.MultiIndex):
    def __new__(cls, *args, **kwargs):
        cls._obj = super(IsoDatetimeMultiIndex, cls).__new__(cls, *args, **kwargs)
        return cls._obj
    
    def __init__(self, *args, **kwargs):
        if 'month' in kwargs.get('names'):
            warnings.warn(f'the names have a "month" value, are you sure this should be a {type(self)} index', Warning)
        self._obj._level = self._obj.names[-1]

    def _complete(self, **kwargs):
        '''
        add missing levels to the index
        '''
        _dict = self._obj.to_frame(index=False).to_dict()

        _default_dict ={
            'year': {key: datetime.datetime.now().year for key in range(self._obj.shape[0])},
            'week': {key: 1 for key in range(self._obj.shape[0])},
            'day': {key: 1 for key in range(self._obj.shape[0])},
        }


        for level, data in _default_dict.items():
            _dict[level] = _dict.get(level, _default_dict[level])
        return IsoDatetimeMultiIndex.from_frame(pd.DataFrame.from_dict(_dict)[_default_dict.keys()])
        
    def to_datetimeindex(self, **kwargs):
        '''
        convert to pd.DatetimeIndex
        '''
        return pd.Index([datetime.datetime.fromisocalendar(*row) for row in self._complete()])

    def to_datetimemultiindex(self, **kwargs):
        '''
        convert to DatetimeMultiIndex
        '''

        datetime_index = self._complete().to_datetimeindex()

        _dict = {
            'year': datetime_index.year, # year including the century
            'month': datetime_index.month, # month (1 to 12)
            'day': datetime_index.day, # day of the month (1 to 31)
            'hour': datetime_index.hour, # hour, using a 24-hour clock (0 to 23)
            'minute': datetime_index.minute,
            'second': datetime_index.second,
        }
        
        level = kwargs.get('level', list(_dict.keys())[-1])

        # filter _dict is level exists
        if level in _dict.keys():
            _dict = {key: _dict[key] for key in list(_dict.keys())[:list(_dict.keys()).index(level)+1]}

        return DatetimeMultiIndex.from_frame(pd.DataFrame(_dict))
            
class PlanningIndex(pd.MultiIndex):
    def __new__(cls, *args, **kwargs):
        cls._obj = super(PlanningIndex, cls).__new__(cls, *args, **kwargs)
        return cls._obj
    
    def __init__(self, *args, **kwargs):
        if not 'week' and 'day' and 'shift' in kwargs.get('names'):
            warnings.warn(f'the names have a don\'t have a \'week\', \'day\' and \'shift\' value, are you sure this should be a {type(self)} index', Warning)
        # self._obj._level = self._obj.names[-2]

    # def _complete(self, **kwargs):
    #     '''
    #     add missing levels to the index
    #     '''
    #     _dict = self._obj.to_frame(index=False).to_dict()

    #     _default_dict ={
    #         'year': {key: datetime.datetime.now().year for key in range(self._obj.shape[0])},
    #         'week': {key: 1 for key in range(self._obj.shape[0])},
    #         'day': {key: 1 for key in range(self._obj.shape[0])},
    #         'shift': {key: 'd' for key in range(self._obj.shape[0])},
    #     }


    #     for level, data in _default_dict.items():
    #         _dict[level] = _dict.get(level, _default_dict[level])
    #     return IsoDatetimeMultiIndex.from_frame(pd.DataFrame.from_dict(_dict)[_default_dict.keys()])
        
    # def to_datetimeindex(self, **kwargs):
    #     '''
    #     convert to pd.DatetimeIndex
    #     '''
    #     return pd.Index([datetime.datetime.fromisocalendar(*row) for row in self._complete()])

    # def to_datetimemultiindex(self, **kwargs):
    #     '''
    #     convert to DatetimeMultiIndex
    #     '''

    #     datetime_index = self._complete().to_datetimeindex()

    #     _dict = {
    #         'year': datetime_index.year, # year including the century
    #         'month': datetime_index.month, # month (1 to 12)
    #         'day': datetime_index.day, # day of the month (1 to 31)
    #         'hour': datetime_index.hour, # hour, using a 24-hour clock (0 to 23)
    #         'minute': datetime_index.minute,
    #         'second': datetime_index.second,
    #     }
        
    #     level = kwargs.get('level', list(_dict.keys())[-1])

    #     # filter _dict is level exists
    #     if level in _dict.keys():
    #         _dict = {key: _dict[key] for key in list(_dict.keys())[:list(_dict.keys()).index(level)+1]}

    #     return DatetimeMultiIndex.from_frame(pd.DataFrame(_dict))

@bluebelt.core.decorators.class_methods
@pd.api.extensions.register_index_accessor('blue')
class IndexToolkit():
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def to_isodatetimemultiindex(self, **kwargs):
        '''
        change the pandas.DatetimeIndex to a IsoDatetimeMultiIndex
        '''

        if not isinstance(self._obj, pd.DatetimeIndex):
            raise ValueError(f'The object is not a pandas.DatetimeIndex but a {type(self._obj)}')
            
        levels = ['year','week','day']
        level = kwargs.get('level', levels[-1])

        # get the levels
        if isinstance(level, str) and level in levels:
            levels = levels[:levels.index(level)+1]
        elif isinstance(level, list):
            _levels = [l for l in level if l in levels]
            if len(_levels) > 0:
                levels = _levels

        frame = self._obj.isocalendar()[levels]

        return IsoDatetimeMultiIndex.from_frame(frame[levels])

    to_idtmi = to_isodatetimemultiindex
    to_iso = to_isodatetimemultiindex
    iso = to_isodatetimemultiindex

    def to_datetimemultiindex(self, **kwargs):
        '''
        change the pandas.DatetimeIndex to a DatetimeMultiIndex
        '''

        if not isinstance(self._obj, pd.DatetimeIndex):
            raise ValueError(f'The object is not a DatetimeIndex but a {type(self._obj)}')
        
        _dict = {
            'year': self._obj.year, # year including the century
            'month': self._obj.month, # month (1 to 12)
            'day': self._obj.day, # day of the month (1 to 31)
            'hour': self._obj.hour, # hour, using a 24-hour clock (0 to 23)
            'minute': self._obj.minute,
            'second': self._obj.second,
        }
        
        level = kwargs.get('level', list(_dict.keys())[-1])

        # filter _dict with the levels
        if isinstance(level, str) and level in _dict.keys():
            _dict = {key: _dict[key] for key in list(_dict.keys())[:list(_dict.keys()).index(level)+1]}
        elif isinstance(level, list):
            _t_dict = {k: v for k, v in _dict.items() if k in level}
            if len(_t_dict) > 0:
                _dict = _t_dict

        return DatetimeMultiIndex.from_frame(pd.DataFrame(_dict))
    
    to_dtmi = to_datetimemultiindex

    def to_dayofyearmultiindex(self, **kwargs):
        '''
        change the pandas.DatetimeIndex to a DayOfYearMultiIndex
        '''

        if not isinstance(self._obj, pd.DatetimeIndex):
            raise ValueError(f'The object is not a DatetimeIndex but a {type(self._obj)}')
        
        _dict = {
            'year': self._obj.year, # year including the century
            'day': self._obj.dayofyear, # day of the month (1 to 366)
            'hour': self._obj.hour, # hour, using a 24-hour clock (0 to 23)
            'minute': self._obj.minute,
            'second': self._obj.second,
        }
        
        level = kwargs.get('level', list(_dict.keys())[-1])

        # filter _dict with the levels
        if isinstance(level, str) and level in _dict.keys():
            _dict = {key: _dict[key] for key in list(_dict.keys())[:list(_dict.keys()).index(level)+1]}
        elif isinstance(level, list):
            _t_dict = {k: v for k, v in _dict.items() if k in level}
            if len(_t_dict) > 0:
                _dict = _t_dict

        return DayOfYearMultiIndex.from_frame(pd.DataFrame(_dict))
    
    to_doymi = to_dayofyearmultiindex
    