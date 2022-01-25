from copy import deepcopy
import itertools
from typing import Dict, List, Tuple, Union
import warnings

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

from inspec_ai._analytics import telemetry_service

KNOWN_IMPUTATION_STRATEGIES = ["mean", "median", "most_frequent"]
X_AND_Y_INVALID_FORMAT_ERROR = (
    "The input datasets x and y should be either numpy arrays or pandas dataframes."
)

@telemetry_service.track_function_executed("fill_missing_values")
def fill_missing_values(
    x: Union[pd.DataFrame, pd.Series, np.ndarray],
    y: Union[pd.DataFrame, pd.Series, np.ndarray],
    replacement_strategies: Dict = None,
) -> Tuple[Union[pd.DataFrame, pd.Series, np.ndarray], Dict]:
    """Fills the dataset's missing values using the optimal strategy for each column.

    Requires the x and y datasets to be only filled with numerical values and nans. Assuming that the optimal strategy for a simple model is also optimal for a more complex model, the function
    uses a grid search strategy with a linear regression model.

    Args:
        x: Training data with numerical and np.nan values
        y: Target numerical values.
        replacement_strategies: Optional. A dictionary allowing the user to select the missing values replacement strategy. The keys should refer to x column names and values to corresponding replacement strategies. The
            available strategies are: 'mean', 'median' and 'most_frequent'. The function will determine the optimal strategies for the remaining columns.

    Returns: The dataset with filled missing values and a dictionary containing containing the applied strategy for each column with missing values.

    """
    if isinstance(x, pd.DataFrame):
        return _fill_missing_values_pandas_dataframe(x, y, replacement_strategies)

    elif isinstance(x, pd.Series):
        return _fill_missing_values_pandas_series(x, y, replacement_strategies)

    elif isinstance(x, np.ndarray):
        return _fill_missing_values_numpy(x, y, replacement_strategies)

    else:
        raise ValueError(X_AND_Y_INVALID_FORMAT_ERROR)


def _fill_missing_values_pandas_dataframe(
    x: pd.DataFrame, y: pd.DataFrame, replacement_strategies: Dict = None
) -> Tuple[pd.DataFrame, Dict]:
    # Step 0: Setup
    x_tmp = deepcopy(x)
    y_tmp = deepcopy(y)

    if not replacement_strategies:
        replacement_strategies = {}

    _validate_replacement_strategies(list(x_tmp.columns), replacement_strategies)

    selected_strategies = dict((col, None) for col in x_tmp.columns)
    column_has_missing_values = np.isnan(x_tmp).any()

    if (column_has_missing_values == False).all():
        warnings.warn("The dataset has no missing values, returned as is.")
        return x, {}

    # Step 1: Fill missing values with the user's selected strategies
    x_tmp, applied_strategies = _apply_imputation_strategies(
        x_tmp, replacement_strategies
    )
    selected_strategies.update(applied_strategies)

    # Step 2: Check if there are still any admissible columns
    (
        admissible_columns,
        columns_with_all_missing_values,
    ) = _get_admissible_columns_for_imputation_and_columns_with_all_missing_values(
        x_tmp
    )

    if not admissible_columns:
        return x_tmp, replacement_strategies

    # Step 3: Automatically impute columns
    x_without_all_missing_values_columns = x_tmp.drop(
        columns=columns_with_all_missing_values, inplace=False
    )
    (
        imputed_variables,
        best_strategies_combination,
    ) = _find_and_apply_the_best_imputation_strategies(
        x_without_all_missing_values_columns, y_tmp, admissible_columns
    )

    for col in admissible_columns:
        x_tmp[col] = imputed_variables[col]

    # Step 4: format output
    formatted_best_strategies = {
        admissible_columns[i]: best_strategies_combination[i]
        for i in range(len(best_strategies_combination))
    }
    selected_strategies.update(formatted_best_strategies)

    return x_tmp, selected_strategies


def _fill_missing_values_pandas_series(
    x: pd.Series, y: pd.Series, replacement_strategies: Dict = None
) -> Tuple[pd.Series, Dict]:

    if not x.name:
        x.name = 0

    x_tmp, selected_strategies = _fill_missing_values_pandas_dataframe(
        pd.DataFrame(x), pd.DataFrame(y), replacement_strategies
    )

    return x_tmp.iloc[:, 0], selected_strategies


def _fill_missing_values_numpy(
    x: np.ndarray, y: np.ndarray, replacement_strategies: Dict[int, str] = None
) -> Tuple[np.ndarray, Dict]:
    x_tmp, selected_strategies = _fill_missing_values_pandas_dataframe(
        pd.DataFrame(x), pd.DataFrame(y), replacement_strategies
    )
    return x_tmp.values, selected_strategies


def _impute_values_of_series(values, strategy):
    column_values = deepcopy(values)
    column_values = column_values.values.reshape(-1, 1)

    imputer = SimpleImputer(strategy=strategy)
    imputer.fit(column_values)

    return imputer.transform(column_values)


def _apply_imputation_strategies(x: pd.DataFrame, replacement_strategies: Dict):
    column_has_missing_values = np.isnan(x).any()
    column_is_all_missing_values = np.isnan(x).all()
    applied_strategies = {}

    for col_name, strategy in replacement_strategies.items():
        if column_is_all_missing_values[col_name]:
            warnings.warn(
                f"Could not fill missing values for column '{col_name}' with strategy '{strategy}' since it does not contain any non-missing value."
            )

        elif not column_has_missing_values[col_name]:
            warnings.warn(
                f"Could not fill missing values for column '{col_name}' with strategy '{strategy}' since it does have any missing value."
            )

        else:
            x[col_name] = _impute_values_of_series(x[col_name], strategy)
            applied_strategies[col_name] = strategy

    return x, applied_strategies


def _get_admissible_columns_for_imputation_and_columns_with_all_missing_values(
    x: pd.DataFrame,
):
    column_has_missing_values = np.isnan(x).any()
    column_is_all_missing_values = np.isnan(x).all()

    column_is_admissible_for_imputation = (
        column_has_missing_values & -column_is_all_missing_values
    )

    admissible_columns = list(
        column_is_admissible_for_imputation[column_is_admissible_for_imputation].index
    )

    columns_with_all_missing_values = list(
        column_is_all_missing_values[column_is_all_missing_values].index
    )

    for column in column_is_all_missing_values[column_is_all_missing_values].index:
        warnings.warn(
            f"Could not fill missing values for column '{column}' since it does not contain any non-missing value."
        )

    return admissible_columns, columns_with_all_missing_values


def _find_and_apply_the_best_imputation_strategies(
    x: pd.DataFrame, y: pd.DataFrame, columns: List[str]
):
    known_imputations = {col: {} for col in columns}

    for column in columns:
        for strategy in KNOWN_IMPUTATION_STRATEGIES:
            known_imputations[column][strategy] = _impute_values_of_series(
                x[column], strategy
            )

    # Find best imputation strategies combination (grid search)
    strategies_combinations = _lists_cartesian_product(
        [KNOWN_IMPUTATION_STRATEGIES] * len(columns)
    )

    rmse = {}

    for combination in strategies_combinations:
        trial_x = deepcopy(x)

        for index, strategy in enumerate(combination):
            col = columns[index]
            trial_x[col] = known_imputations[col][strategy]

        trial_model = LinearRegression()
        trial_model.fit(trial_x, y)
        trial_rmse = mean_squared_error(y, trial_model.predict(trial_x))

        rmse[trial_rmse] = combination

    min_rmse = min(list(rmse.keys()))
    best_strategies_combination = rmse[min_rmse]

    for index, strategy in enumerate(best_strategies_combination):
        col = columns[index]
        x[col] = known_imputations[col][strategy]

    return x[columns], best_strategies_combination


def _lists_cartesian_product(list_of_lists):
    out = []

    for element in itertools.product(*list_of_lists):
        out.append(element)

    return out


def _validate_replacement_strategies(x_columns: List, replacement_strategies: Dict):
    for col_name in replacement_strategies.keys():
        if col_name not in x_columns:
            raise ValueError(
                f"'{col_name}' is not a column of the x dataset. "
                f"Please ensure that the keys of replacement_strategies are columns of the x dataset."
            )

    for strategy in replacement_strategies.values():
        if strategy not in KNOWN_IMPUTATION_STRATEGIES:
            raise ValueError(
                f"'{strategy}' is not an available missing value replacement strategy. Please ensure that"
                f"the values of replacement_strategies are valid replacement strategies. The valid"
                f"replacement strategies are: {str(KNOWN_IMPUTATION_STRATEGIES)[1:-1]}"
            )
