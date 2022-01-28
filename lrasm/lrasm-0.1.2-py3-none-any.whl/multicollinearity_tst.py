import pandas as pd
import numpy as np
from statsmodels.stats.outliers_influence import variance_inflation_factor

def multicollinearity_test(X, VIF_thresh):
    """This function recieves a data frame of predictors and outputs VIF for each feature 
    along with a stetement whether or not the multicollinearity assumption is violated.
    
    Parameters
    ----------
    X : pd.Dataframe
        Dataframe containing exploratory variable data

    VIF_thresh: float
        The threshold for VIF
        
    Returns
    -------
    VIF
        VIF for explarotary variables
    Print statement
        Whether the multicollinearity assumption is violated. 
    
    Examples
    --------
    >>> multicollinearity_test(X_train, VIF_thresh) 
    """
    #X = X._get_numeric_data() #drop non-numeric cols

    if not isinstance(X, pd.DataFrame):
        raise TypeError("Error: X must be a data frame")
        
    if not X.shape[1] == X.select_dtypes(include=np.number).shape[1]:
        raise TypeError("Error: X must only contain numeric data.")

    vif_df = pd.DataFrame()
    vif_df['features'] = X.columns
    vif_df["VIF"] = [variance_inflation_factor(X.values, i) for i in range(len(X.columns))]

    possible_multicollinearity = sum([1 for vif in vif_df['VIF'] if vif > VIF_thresh])
    definite_multicollinearity = sum([1 for vif in vif_df['VIF'] if vif > 100])

    print('{0} cases of possible multicollinearity'.format(possible_multicollinearity))
    print('{0} cases of definite multicollinearity'.format(definite_multicollinearity))

    if definite_multicollinearity == 0:
        if possible_multicollinearity == 0:
            print('Multicollinearity assumption is satisfied')
        else:
            print('Assumption partially satisfied')
            print()
            print('Consider removing variables with high Variance Inflation Factors')
            
    else:
        print('Assumption not satisfied')
        print()
        print('Coefficients are likely probomatic with at leats one VIF greater than 100. Consider removing features with high VIFs')

    return vif_df    

