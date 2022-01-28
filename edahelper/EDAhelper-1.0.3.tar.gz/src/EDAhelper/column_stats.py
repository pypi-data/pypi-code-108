import pandas as pd
import numpy as np
import statistics

def column_stats(data, columns):
    """
  Obtain summary statistics of column(s) including count, mean, median, mode, Q1, Q3, 
  variance, standard deviation, correlation, and covariance in table format.

  Parameters
  -------------

  data: array_like
           The data set from which columns will be selected

  columns: vector of strings
            Columns for which to obtain summary stats, correlation matrix, and covariance matrix
            (if > 1 column arguments used)

  Returns
  -------------
  array
          Summary table detailing all statistics and correlations between chosen columns

  Examples
  -------------
  >>> column_stats(iris, ('sepal_width', 'petal_length'))
  >>>
  """
    if not isinstance(columns, (list, tuple, np.ndarray)):
        raise TypeError("'columns' should be a list, tuple, or array")
    for column in columns:
        if not isinstance(column, str):
            raise TypeError("item in columns should be of type string")
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data should be a DataFrame")
        
    for column in columns:
        for row in data[column]:
            if isinstance(row, str):
                raise TypeError("values should be of type integer")
    
    
    statsdict = {'Column': [], 'Count': [], 'Mean': [], 'Median': [], 'Mode': [], 'Q1': [], 'Q3': [], 'Var': [], 'Stdev': []}
    for column in columns:
        statsdict['Column'].append(column)
        statsdict['Count'].append(round(float(data[column].describe().loc['count']), 3))
        statsdict['Mean'].append(round(float(data[column].describe().loc['mean']), 3))
        statsdict['Median'].append(round(float(data[column].describe().loc['50%']), 3))
        statsdict['Mode'].append(statistics.mode(data[column]))
        statsdict['Q1'].append(round(float(data[column].describe().loc['25%']), 3))
        statsdict['Q3'].append(round(float(data[column].describe().loc['75%']), 3))
        statsdict['Var'].append(round(data[column].var(), 3))
        statsdict['Stdev'].append(round(data[column].std(), 3))
        

    cols = []
    for column in columns:
        cols.append(column)
        
    covmatrix = pd.DataFrame(data, columns = cols)

    corrmatrix = pd.DataFrame(data, columns = cols)   
    return pd.DataFrame.from_dict(statsdict), corrmatrix.corr(), covmatrix.cov()
