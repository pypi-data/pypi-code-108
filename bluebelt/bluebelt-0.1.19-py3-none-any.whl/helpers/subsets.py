from bluebelt.core.exceptions import *

def subset(frame, inverse=False, **kwargs):
        
    #check if filter values are lists and repair

    # filters = {key: ([value] if not isinstance(value, list) else value) for key, value in kwargs.items()}
    filters={}
    for col in kwargs:
        if col in frame.columns:
            values = kwargs.get(col) if isinstance(kwargs.get(col), list) else [kwargs.get(col)]
            for value in values:
                if value not in frame[col].values:
                    raise InputError(f'{value} is not in {col}')
            filters[col]=values
        else:
            raise InputError(f'{col} is not in the dataframe')

    #filter  
    if inverse:
        frame=frame[frame.isin(filters).sum(axis=1) != len(filters.keys())]
    else:
        frame=frame[frame.isin(filters).sum(axis=1) == len(filters.keys())]
        
    return frame