import os
import warnings
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame

# necessary for iterative imputer
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.impute._base import _BaseImputer
from sklearn.linear_model import BayesianRidge, LinearRegression
from sklearn.preprocessing import PolynomialFeatures

from akerbp.mlpet.Datasets.utilities import get_col_types, standardize_names


def simple_impute(
    df: DataFrame,
    **kwargs,
) -> DataFrame:
    """
    Imputes missing values in specified columns with sklearn's SimpleImputer
    using the mean strategy for numeric columns and the most_frequent strategy
    for categorical columns

    Args:
        df (pd.DataFrame): dataframe with columns to impute

    Keyword Args:
        categorical_curves: List of column names that should be considered as
            categorical. If not provided, defaults to trying to determine these
            using the get_col_types utility function

    Returns:
        pd.DataFrame: dataframe with imputed values
    """
    num_cols, cat_cols = get_col_types(df, kwargs.get("categorical_curves", []))

    # Impute numerical columns
    missing_cols_num = df[num_cols].isnull().sum().gt(0).index.tolist()
    if "DEPTH" in missing_cols_num:
        missing_cols_num.remove("DEPTH")
    num_imputer = SimpleImputer(strategy="mean")
    num_imputer.fit(df[missing_cols_num])
    df.loc[:, missing_cols_num] = pd.DataFrame(
        num_imputer.transform(df[missing_cols_num]),
        columns=missing_cols_num,
    )

    # Impute the categorical columns
    missing_cols_cat = df[cat_cols].isnull().sum().gt(0).index.tolist()
    cat_imputer = SimpleImputer(strategy="most_frequent")
    cat_imputer.fit(df[missing_cols_cat])
    df.loc[:, missing_cols_cat] = pd.DataFrame(
        cat_imputer.transform(df[missing_cols_cat]),
        columns=missing_cols_cat,
    )

    return df


def iterative_impute(df: DataFrame, **kwargs) -> DataFrame:
    """
    Imputes missing values in specified columns with iterative imputer

    Args:
        df (pd.DataFrame): dataframe with columns to impute

    Keyword Args:
        imputer (str, optional): sklearn imputer class. NOT YET IMPLEMENTED.
            Defaults to None.

    Returns:
        pd.DataFrame: dataframe with imputed values
    """
    imputer: _BaseImputer = kwargs.get("imputer")
    # Only interested in numerical columns so no need to flood console with
    # warnings related to categorical curves
    num_cols, _ = get_col_types(df, warn=False)

    # Iterative impute
    missing_featutes = df[num_cols].isnull().sum().gt(0).index.tolist()
    if "DEPTH" in missing_featutes:
        missing_featutes.remove("DEPTH")
    if imputer is None:
        imputer = IterativeImputer(estimator=BayesianRidge())
        imputer.fit(df[missing_featutes])
    else:
        raise ValueError("Providing an imputer is not implemented yet!")
    df.loc[:, missing_featutes] = pd.DataFrame(
        imputer.transform(df[missing_featutes]),
        columns=missing_featutes,
    )
    return df


def generate_imputation_models(df: DataFrame, **kwargs) -> Dict[str, Dict[str, Any]]:
    """
    Generates 3rd order polynomial regression models with the DEPTH column as the
    target y variable and each curve in the provided curves keyword argument as the
    x variable (i.e. a model per curve).

    Args:
        df (pd.DataFrame): dataframe to get data

    Keywords Args:
        curves (list): list of curves names to generate models for. If this
            argument is not provided, no models are generated because it defaults
            to an empty list.

    Returns:
        dict: dictionary with models for each curve based on DEPTH
    """
    curves: List[str] = kwargs.get("curves", [])
    imputation_models = {c: {"poly_transform": None, "model": None} for c in curves}

    if curves:
        if "DEPTH" not in df.columns:
            raise KeyError(
                "To generate imputation models, the 'DEPTH' column is required."
                " It does not exist in the provided dataframe!"
            )
        for c in curves:
            # remove nan values
            df = df[(df[c].notna()) & (df.DEPTH.notna())]
            # polynomial features and regression fitting
            poly = PolynomialFeatures(3)
            poly.fit(np.array(df.DEPTH.values).reshape(-1, 1))
            depth_poly = poly.transform(np.array(df.DEPTH.values).reshape(-1, 1))
            linear_model = LinearRegression()
            linear_model.fit(depth_poly, df[c])
            imputation_models[c]["poly_transform"] = poly
            imputation_models[c]["model"] = linear_model

    return imputation_models


def individual_imputation_models(df: DataFrame, **kwargs) -> Dict[str, Dict[str, Any]]:
    """
    Determines whether an individual or global model would be best for a given
    list of curves to check and generates individual models if the checks are
    passed. We check the percentage of missing data and the
    spread of actual data with some thresholds to decide if we should use an
    individual model. If the spread of the data is greater than 0.7 and the
    percentage of missing data is less than 60%, an individual model is created.
    These thresholds can be changed via the kwargs.

    Args:
        df (pd.DataFrame): dataframe with data

    Keyword Args:
        curves (list): list of curves to create individual models for provided
            they pass the relevant thresholds
        imputation_models (dict): models given for each curve
            (usually global models). If not provided, defaults to an empty dict
        data_spread_threshold (float): The data spread threshold that determines
             whether or not an individual model for the curve should be created.
        missing_data_threshold (float): The data spread threshold that determines
             whether or not an individual model for the curve should be created.

    Returns:
        dict: updated imputation models dictionary (if provided via kwargs)
            with individual models replacing existing models (where applicable)
    """
    # Process kwargs
    curves: List[str] = kwargs.get("curves", [])
    imputation_models: Dict[str, Dict[str, Any]] = kwargs.get("imputation_models", {})
    data_spread_threshold = kwargs.get("data_spread_threshold", 0.7)
    missing_data_threshold = kwargs.get("missing_data_threshold", 0.6)

    if curves:
        curves_to_generate_individual_model_for = []
        for c in curves:
            # if a curve model was not in the given models dicitonary, add it
            if c not in imputation_models:
                curves_to_generate_individual_model_for.append(c)
            # also add it if an individual model would be better
            else:
                perc_missing = df[c].isna().mean()
                idx_nona = df[~df[c].isna()].index
                spread = (idx_nona.max() - idx_nona.min()) / (
                    df.index.max() - df.index.min()
                )
                if (
                    spread > data_spread_threshold
                    and perc_missing < missing_data_threshold
                ):
                    curves_to_generate_individual_model_for.append(c)
        if len(curves_to_generate_individual_model_for) > 0:
            individual_models = generate_imputation_models(
                df, **{"curves": curves_to_generate_individual_model_for}
            )
            # replace global models by individual ones
            imputation_models.update(individual_models)

    return imputation_models


def apply_depth_trend_imputation(df: DataFrame, **kwargs) -> DataFrame:
    """
    Apply imputation models to impute curves in given dataframe

    Args:
        df (pd.DataFrame): dataframe to which impute values

    Keyword Args:
        curves (list): list of curves to apply the imputation to.
        imputation_models (dict): imputation models for each curve. If a model
            is not provided for each curve, a KeyError is raised

    Returns:
        pd.DataFrame: dataframe with imputed values based on depth trend
    """
    # Process kwargs
    curves: List[str] = kwargs.get("curves", [])

    if curves:
        try:
            imputation_models = kwargs["imputation_models"]
        except KeyError as e:
            raise KeyError(
                "No imputation models could be applied to the requested curves "
                "because no models were passed to the method!"
            ) from e

        for c in curves:
            if c not in imputation_models:
                raise KeyError(
                    f"Attempting to impute for {c} but no corresponding imputation "
                    "model was provided for that curve!"
                )
            missing = df[(df[c].isna()) & (df.DEPTH.notna())].index
            if len(missing) > 0:
                well_data_missing = df.loc[missing, "DEPTH"]
                # impute values with depth trend - linear model
                poly_preds = imputation_models[c]["poly_transform"].transform(
                    np.array(well_data_missing.values).reshape(-1, 1)
                )
                poly_preds = imputation_models[c]["model"].predict(poly_preds)
                df.loc[missing, c] = poly_preds
    return df


def impute_depth_trend(df: DataFrame, **kwargs) -> DataFrame:
    """
    Imputation of curves based on polynomial regression models of the curve based on DEPTH

    Args:
        df (pd.DataFrame): df to impute curves

    Keyword Args:
        curves_to_impute (list): list of curves to depth impute
        imputation_models (dict): dictionary with curves as keys and the sklearn model as value
        save_imputation_models (bool): whether to save the models in the folder_path
        folder_path (str): The path to the folder where the imputation models
            should be saved.
        allow_individual_models (bool): whether to allow individual models if seen that it has enough data
        to do so (better performance per well)
        curves_mappings (dict): A mapping dictionary to allow mapping curve names
            to more standardized names. Defaults to {} (ie. no standardization).

    Returns:
        pd.DataFrame: dataframe with curves imputed
    """

    curves: List[str] = kwargs.get("curves_to_impute", [])
    imputation_models: Dict[str, Dict[str, Any]] = kwargs.get("imputation_models", {})
    save_imputation_models = kwargs.get("save_imputation_models", False)
    folder_path = kwargs.get("folder_path", "")
    allow_individual_models = kwargs.get("allow_individual_models", True)
    curves_mappings: Dict[str, str] = kwargs.get("curves_mapping", {})

    if curves:
        # we need to first standardize names if possible
        if curves_mappings:
            curves, _ = standardize_names(curves, curves_mappings)

        # check if depth and all other curves in df
        if not all(c in df.columns for c in curves + ["DEPTH"]):
            ValueError(
                "Cannot perform depth trend imputation as not all curves are in the dataset."
            )

        # if imputation models do not exist
        if not imputation_models:
            # generate models
            imputation_models = generate_imputation_models(df, **{"curves": curves})
            if save_imputation_models:
                if folder_path:
                    joblib.dump(
                        imputation_models,
                        os.path.join(
                            folder_path,
                            f"imputation_models_for_{'_'.join(curves)}.joblib",
                        ),
                    )
                else:
                    raise ValueError(
                        "Save imputation models was set to true but no "
                        " folder_path kwarg was passed to the method!"
                    )
        else:
            # check if imputation models is provided as a dict with the same format
            if isinstance(imputation_models, dict):
                if not all(c in curves for c in imputation_models):
                    if allow_individual_models:
                        warnings.warn(
                            "Some provided curves for imputing do not have models. Models will be generated."
                        )
                    else:
                        raise ValueError(
                            "Curves included in the imputation models dictionary inconsistent with curves to impute",
                            imputation_models.keys(),
                            curves,
                        )
            # check if it is preferable to use individual models instead of given global models
            if allow_individual_models:
                imputation_models = individual_imputation_models(
                    df, **{"curves": curves, "imputation_models": imputation_models}
                )

        # apply imputation
        df = apply_depth_trend_imputation(
            df, **{"curves": curves, "imputation_models": imputation_models}
        )

    return df
