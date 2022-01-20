import pandas as pd
import numpy as np

import bluebelt.core.decorators

@bluebelt.core.decorators.class_methods
class Subset():
    """
    Create a subset based on the pandas.Dataframe column values        
        arguments
        inverse: boolean
            if True then the inverse of the filtered pandas Dataframe will be returned
            default value: False
        
        usage
        df
            | column_1  | column_2  | column_3  |
        -----------------------------------------
        0   | a         | a         | a         |
        1   | b         | a         | b         |
        2   | a         | b         | c         |
        3   | b         | b         | a         |
        4   | a         | c         | b         |
        5   | b         | c         | c         |
        6   | a         | a         | a         |
        7   | b         | a         | b         |
        8   | a         | b         | c         |
        9   | b         | b         | a         |
        

        subset = bluebelt.data.subsets.Subset(frame, column_1="a", column_2=["a", "b"])
        subset
            | column_1  | column_2  | column_3  |
        -----------------------------------------
        0   | a         | a         | a         |
        2   | a         | b         | c         |
        6   | a         | a         | a         |
        8   | a         | b         | c         |
        
        
    """
    def __init__(self, frame, inverse=False, **kwargs):

        self.frame = frame
        self.inverse = inverse
        self.kwargs = kwargs
        self.calculate(**kwargs)

    def calculate(self, **kwargs):

        # build filters
        filters={}
        for col in self.kwargs:
            if col in self.frame.columns:
                values = self.kwargs.get(col) if isinstance(self.kwargs.get(col), list) else [self.kwargs.get(col)]
                for value in values:
                    if value not in self.frame[col].values:
                        raise ValueError(f'{value} is not in {col}')
                filters[col]=values
            else:
                raise ValueError(f'{col} is not in frame')

        self.filters = filters

        # filter the frame
        if self.inverse:
            frame=self.frame[self.frame.isin(filters).sum(axis=1) != len(filters.keys())]
        else:
            frame=self.frame[self.frame.isin(filters).sum(axis=1) == len(filters.keys())]
            
        self.result = frame

    def __str__(self):
        return ""
    
    def __repr__(self):
        return (f'{self.__class__.__name__}(frame_length={self.frame.shape[0]:1.0f}, result_length={self.result.shape[0]:1.0f}, filter={self.filters})')
