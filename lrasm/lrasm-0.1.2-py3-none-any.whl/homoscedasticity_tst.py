import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
from matplotlib.pyplot import figure
from scipy import stats

def homoscedasticity_test(X, y, threshold = 0.05):
    """This function recieves a linear regression model and outputs a
    scatter plot figure of residuals plotted against fitted values. It prints
    a statement indicating the results of the homoscedasticity test and outputs
    a dataframe containing spearman correlation coefficients between the 
    absolute residuals and the fitted y values.

    Parameters
    ----------
    X : pd.Dataframe
        Dataframe containing exploratory variable data

    y : pd.series
        Dataframe containing response variable data
        
    Returns
    -------
    pd.DataFrame
        Scatter plot of residuals plotted against fitted values

    Examples
    --------
    >>> homoscedasticity_test(X_train, y_train) 
    >>> 
    >>> correlation_coefficient	p_value
    >>>                   0.038	  0.427
    """

    if not isinstance(X, pd.DataFrame):
        print("Error: X must be a dataframe")
        return None, None

    if not isinstance(y, pd.Series):
        print("Error: y must be a series")
        return None, None

    if not X.shape[1] == X.select_dtypes(include=np.number).shape[1]:
        print("Error: X must only contain numeric data.")
        return None, None

    if not pd.api.types.is_numeric_dtype(y):
        print("Error: y must only contain numeric data.")
        return None, None

    lr = linear_model.LinearRegression()
    lr.fit(X, y)
    preds = lr.predict(X)
    comp_df = pd.DataFrame({"Real" : y, "Predicted": preds, "residuals": y-preds})
    comp_df["abs_res"] = abs(comp_df.residuals)

    plot = figure(figsize=(10, 6), dpi=80)
    plt.scatter(x=comp_df["Predicted"], y=comp_df["residuals"], alpha = 0.5)
    plt.axhline(y = 0.0, color = 'r', linestyle = '--')
    plt.xlabel("Fitted Target Values")
    plt.ylabel("Residuals")
    plt.title("Plot of Residuals vs Fitted Values")
    
    y2 = comp_df.abs_res
    X2 = comp_df["Predicted"]
    corr = round(abs(stats.spearmanr(X2, y2).correlation), 3)
    pval = round(abs(stats.spearmanr(X2, y2).pvalue),3)
    corr_df = pd.DataFrame({"correlation_coefficient": [corr], "p_value" : [pval]})
    
    print("The correlation coefficient between the absolute residuals and the fitted y values is: ", str(corr), " With a p value of: ", str(pval))

    if pval > threshold:
        print("The p value of the correlation is above the rejection threshold, thus the correlation is likely not significant. \
        \nThe data is likely to be homoscedastic if the cluster of points has similar width throughout the X axis on the residuals plot.")
    else:
        print("The p value of the correlation is below the rejection threshold, thus the correlation is likely significant. \
        \nThe data is unlikely to be homoscedastic.")

    return corr_df, plot
