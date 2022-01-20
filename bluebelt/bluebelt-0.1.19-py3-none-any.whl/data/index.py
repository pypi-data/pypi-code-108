import pandas as pd

def iso_index(_obj, **kwargs):
    '''
    change the pandas.DatetimeIndex of a pandas.Series or pd.DataFrame to
    a pandas.MultiIndex from pd.DatetimeImdex.isocalendar() year, week, day
    '''

    if not isinstance(_obj.index, pd.DatetimeIndex):
        raise ValueError(f'The Series or DataFrame Index is not a DatetimeIndex but a {type(_obj.index)}')
        
    levels = ['year','week','day']
    level = kwargs.get('level', levels[-1])
    
    if level in levels:
        levels = levels[:levels.index(level)+1]

    index = pd.MultiIndex.from_frame(_obj.index.isocalendar()[levels])
    if isinstance(_obj, pd.Series):
        return pd.Series(index=index, data=_obj.values, name=_obj.name)
    else:
        return pd.DataFrame(index=index, data=_obj.values, columns=_obj.columns)

def dt_index(_obj, **kwargs):
    '''
    change the pandas.DatetimeIndex of a pandas.Series or pd.DataFrame to
    a pandas.MultiIndex from pd.DatetimeImdex. year, month, day, hour, minute, second
    '''

    if not isinstance(_obj.index, pd.DatetimeIndex):
        raise ValueError(f'The Series or DataFrame Index is not a DatetimeIndex but a {type(_obj.index)}')
    
    _dict = {
        'year': _obj.index.year, # year including the century
        'month': _obj.index.month, # month (1 to 12)
        'day': _obj.index.day, # day of the month (1 to 31)
        'hour': _obj.index.hour, # hour, using a 24-hour clock (0 to 23)
        'minute': _obj.index.minute,
        'second': _obj.index.second,
    }
    
    level = kwargs.get('level', list(_dict.keys())[-1])

    # filter _dict is level exists
    if level in _dict.keys():
        _dict = {key: _dict[key] for key in list(_dict.keys())[:list(_dict.keys()).index(level)+1]}

    index = pd.MultiIndex.from_frame(pd.DataFrame(_dict))
    
    if isinstance(_obj, pd.Series):
        return pd.Series(index=index, data=_obj.values, name=_obj.name)
    else:
        return pd.DataFrame(index=index, data=_obj.values, columns=_obj.columns)
