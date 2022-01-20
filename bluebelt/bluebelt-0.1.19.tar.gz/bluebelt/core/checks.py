import pandas as pd
import numpy as np

def check_kwargs(kwargs):


    kwargs = _flatten_dict(kwargs)

    series = kwargs.pop('series', None)
    frame = kwargs.pop('frame', None)
    columns = kwargs.pop('columns', None)
    ncols = kwargs.pop('ncols', None)
    alpha = kwargs.pop('alpha', None)
    confidence = kwargs.pop('confidence', None)
    
    
    if series is not None and not isinstance(series, pd.Series):
        raise ValueError(f'series must be a pandas Series not a {type(series)}')

    if isinstance(frame, pd.DataFrame):
        if columns is not None and not isinstance(columns, (str, list)):
            raise ValueError(f'columns must be a string or a list not a {type(columns)}')
            
        if ncols is not None and not isinstance(ncols, (int, list, tuple)):
            # this should never happen
            raise ValueError(f'ncols must be an integer, list or tuple not a {type(ncol)}')
        
        if isinstance(ncols, int):
            if isinstance(columns, str) and ncols != 1:
                raise ValueError(f'columns must be a list not a {type(columns)}')
            elif isinstance(columns, list) and ncols != len(columns):
                raise ValueError(f'columns must be a list of {ncols} columns not {len(columns)} columns')
            elif columns is None and frame.shape[1] != ncols:
                raise ValueError(f'frame must have {ncols} columns not {frame.shape[1]} columns')
        elif isinstance(ncols, (list, tuple)):
            if ncols[0] is None:
                # column length must be less than or equal to ncols[1}]
                if isinstance(columns, str) and 1 != ncols[1]:
                    raise ValueError(f'columns must be a list not a {type(columns)}')
                if isinstance(columns, list) and len(columns) > ncols[1]:
                    raise ValueError(f'columns must be a list of {ncols[1]} or less columns not {len(columns)} columns')
                elif frame.shape[1] > ncols[1]:
                    raise ValueError(f'frame must have {ncols[1]} or less columns not {frame.shape[1]} columns')
            elif ncols[1] is None:
                # column length must be greater than or equal to ncols[1}]
                if isinstance(columns, str) and 1 != ncols[0]:
                    raise ValueError(f'columns must be a list not a {type(columns)}')
                if isinstance(columns, list) and len(columns) < ncols[0]:
                    raise ValueError(f'columns must be a list of {ncols[0]} or more columns not {len(columns)} columns')
                elif frame.shape[1] < ncols[0]:
                    raise ValueError(f'frame must have {ncols[0]} or more columns not {frame.shape[1]} columns')
            else:
                # column length must be between ncols[0] and ncols[1]
                if isinstance(columns, str) and 1 not in np.arange(ncols[0], ncols[1]+1):
                    raise ValueError(f'columns must be a list not a {type(columns)}')
                if isinstance(columns, list) and len(columns) not in np.arange(ncols[0], ncols[1]+1):
                    raise ValueError(f'columns must be a list of between {ncols[0]} and {ncols[1]} columns not {len(columns)} columns')
                elif frame.shape[1] not in np.arange(ncols[0], ncols[1]+1):
                    raise ValueError(f'frame must have between {ncols[0]} and {ncols[1]} columns not {frame.shape[1]} columns')
    elif frame is not None:
        raise ValueError(f'frame must be a pandas Series or a pandas DataFrame not a {type(frame)}')

    if alpha is not None and not isinstance(alpha, (int, float)):
        raise ValueError(f'alpha must be a float or an integer not a {type(alpha)}')
    elif alpha is not None and not (0 < alpha < 1):
        raise ValueError(f'0 < alpha < 1 is required, but alpha={alpha} was given')
    
    if confidence is not None and not (0 < confidence < 1):
        raise ValueError(f'0 < confidence < 1 is required, but confidence={confidence} was given')
    
    if 'popmean' in kwargs:
        popmean = kwargs.pop('popmean', None)
        if popmean is None:
            raise ValueError('popmean must be provided')
        elif not isinstance(popmean, (int, float)):
            raise ValueError(f'popmean must be an integer or a float not a {type(popmean)}')

    # return rest kwargs
    return kwargs

def _flatten_dict(d):
    def expand(key, value):
        if isinstance(value, dict):
            return [ (k, v) for k, v in _flatten_dict(value).items() ]
        else:
            return [ (key, value) ]

    items = [ item for k, v in d.items() for item in expand(k, v) ]

    return dict(items)
