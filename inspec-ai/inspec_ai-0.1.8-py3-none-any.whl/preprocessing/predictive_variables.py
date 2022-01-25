from typing import Tuple, Union

import numpy as np
import pandas as pd

from sklearn.linear_model import Lasso

from inspec_ai.analytics import telemetry_service

@telemetry_service.track_function_executed("get_predictive_features")
def get_predictive_features(
    x_train: Union[pd.DataFrame, np.ndarray],
    y_train: Union[pd.DataFrame, np.ndarray],
    alpha: float = 0.1,
) -> Tuple[np.ndarray, np.ndarray]:
    """Gets the predictives features of a dataset based on the coefficients returned by a Lasso model used as a baseline.

    Args:
        x_train: Numpy array or pandas Series. Training dataset.
        y_train: Numpy array or pandas Series. Predicted target values.

    Returns: 
        The dataset with only the optimal features.
        The list of coefficients used to establish the optimal features

    """
    _x_train = _pandas_to_ndarray(x_train)
    _y_train = _pandas_to_ndarray(y_train)

    _validate_inputs(_x_train, _y_train)

    model = Lasso(alpha=alpha)
    model.fit(_x_train, _y_train)

    optimal_features = _x_train[:, (model.coef_ != 0)]

    return optimal_features, model.coef_


def _pandas_to_ndarray(data):
    if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
        return data.values

    if isinstance(data, np.ndarray):
        return data

    if isinstance(data, list):
        return np.array(data)

    raise ValueError(
        f"Inputs must be Pandas Dataframe or Numpy arrays. Cannot convert {type(data)} to numpy array."
    )


def _validate_inputs(x_train: np.ndarray, y_train: np.ndarray) -> None:
    if len(x_train) != len(y_train):
        raise ValueError(
            "The provided inputs must contain the same number of elements: x_train and y_train."
        )

