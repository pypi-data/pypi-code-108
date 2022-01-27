"""Define algorithms for some statistics, such as
    [SSY](https://en.wikipedia.org/wiki/Total_sum_of_squares),
    [PRESS](https://en.wikipedia.org/wiki/PRESS_statistic),
    [R²](https://en.wikipedia.org/wiki/Coefficient_of_determination),
    [MAE](https://en.wikipedia.org/wiki/Mean_absolute_error),
    [RMSE](https://en.wikipedia.org/wiki/Root-mean-square_deviation),
    `R`…
    """
import numpy as np
from math import sqrt
from sklearn.preprocessing import scale


def ssy(y, mean_y=None) -> float:
    r"""Calculates [Total Sum of Squares](https://en.wikipedia.org/wiki/Total_sum_of_squares) of the dependent variable.

    \[ SSY = \sum\limits_{i} (y_i - \bar y)^2 \]

    Args:
        y (DataFrame, list, array): The vector to calculate SSY.
        mean_y (float, optional): Mean of `y`. If `None`, it'll be calculated. Defaults to None.

    Returns:
        float: SSY
    """
    if mean_y is None:
        mean_y = np.mean(y)
    ssy = sum((y-mean_y*np.ones(np.shape(y)))**2)
    return ssy


def calcPress(yreal, ypred) -> float:
    r"""Calculates [predicted residual error sum of squares](https://en.wikipedia.org/wiki/PRESS_statistic) of `ypred` regarding `yreal`.

    \[ PRESS = \sum\limits_{i} (y_i - \hat y_{i})^2 \]

    Args:
        yreal (DataFrame,list,array): The real data.
        ypred (DataFrame,list,array): The predicted data.

    Returns:
        float: PRESS
    """
    press = sum((yreal-ypred)**2)
    return press


def calcR2(yreal, ypred, mean_y=None) -> float:
    r"""Calculates the [coefficient of determination](https://en.wikipedia.org/wiki/Coefficient_of_determination) ( \( R^2 \) ).

    \[ R^2 = 1-\dfrac{PRESS}{SSY} \]

    Args:
        yreal (DataFrame,list,array): The real data.
        ypred (DataFrame,list,array): The predicted data.
        mean_y (float, optional): Mean of `yreal`. If `None`, it'll be calculated. Defaults to None.

    Returns:
        float: \( R^2 \)

    ## See also:
    * `qsarmodelingpy.calculate_parameters.calcPress`
    * `qsarmodelingpy.calculate_parameters.ssy`
    """
    ssy1 = ssy(yreal, mean_y)
    R2 = 1-(calcPress(yreal, ypred)/ssy1)
    return R2


def calcMAE(yreal, ypred) -> float:
    r"""Calculates the [Mean Absolute Error](https://en.wikipedia.org/wiki/Mean_absolute_error).

    \[ MAE = \dfrac{\sum\limits_{i=1}^n \left\vert y_i - \hat y_i \right\vert}{n} \]

    where \(y\) is the predicted value, \(\hat y\) is the true value and \(n\) is the number of data points.

    Args:
        yreal (DataFrame,list,array): The real data.
        ypred (DataFrame,list,array): The predicted data.

    Returns:
        float: MAE
    """
    MAE = 1/len(yreal)*np.sum(abs(yreal-ypred))
    return MAE


def calcRMSE(yreal, ypred) -> float:
    r"""Calculates the [Root Mean Square Error](https://en.wikipedia.org/wiki/Root-mean-square_deviation).

    \[ RMSE = \sqrt{\dfrac{PRESS}{n}} \]

    Args:
        yreal (DataFrame,list,array): The real data.
        ypred (DataFrame,list,array): The predicted data.

    Returns:
        float: RMSE

    ## See also:
    * `qsarmodelingpy.calculate_parameters.calcPress`
    """
    RMSE = sqrt(calcPress(yreal, ypred)/len(yreal))
    return RMSE


# TODO: expand documentation
def calcR(yreal, ypred) -> float:
    r"""Calculates \( R \).

    Args:
        yreal (DataFrame,list,array): The real data.
        ypred (DataFrame,list,array): The predicted data.

    Returns:
        float: R
    """
    r = np.dot(scale(yreal), scale(ypred))/(len(yreal))
    return r
