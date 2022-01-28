import numpy as np
import pandas as pd
from sklearn import linear_model
from scipy import stats

def normality_test(X, y, p_value_thresh = 0.05):
    """This function recieves a linear regression model and p-value threshold
     and outputs the p-value from a shapiro wilks test along with a statement 
     indicating the results of the normality test

    Parameters
    ----------
    X : pd.Dataframe
        Dataframe containing exploratory variable data
    y : pd.Series
        Dataframe containing response variable data
    p_value_thresh: float
        The threshold user defines for the p-value, default set to 0.05
        
    Returns
    -------
    float
        p-value of the shapiro wilk test
    
    Examples
    --------
    >>> normality_test(X_train, y_train, p_value_thresh = 0.05).
    """ 

    if not isinstance(X, pd.DataFrame):
        raise TypeError("Error: X must be a dataframe")
        
    if not isinstance(y, pd.Series):
        raise TypeError("Error: y must be a series")

    if not X.shape[1] == X.select_dtypes(include=np.number).shape[1]:
        raise TypeError("Error: X must only contain numeric data.")

    if not pd.api.types.is_numeric_dtype(y):
        raise TypeError("Error: y must only contain numeric data.")

    if not X.shape[0] == len(y):
        raise ValueError("Error: x and y must have the same number of data points")

    lr = linear_model.LinearRegression()
    lr.fit(X, y)
    preds = lr.predict(X)
    residuals = y-preds
    shapiro_test = stats.shapiro(residuals)
    p_value = shapiro_test.pvalue
    res = "Pass"

    if p_value >= p_value_thresh:
        print("After applying the Shapiro Wilks test for normality of the residuals the regression assumption of normality has passed and you can continue with your analysis")
    else:
        print("After applying the Shapiro Wilks test for normality of the residuals the regression assumption of normality has failed and you should make some djustments before continuing with your analysis")
        res = "Fail"

    return (p_value,res)

