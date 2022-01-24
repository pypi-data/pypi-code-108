# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Container for generic featurizers."""
from typing import Any

import logging

from nimbusml.preprocessing.missing_values import Handler as NimbusMLMissingValuesHandler
from nimbusml.preprocessing.schema import ColumnSelector as NimbusMLColumnSelector
from sklearn.cluster import MiniBatchKMeans
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MaxAbsScaler

from azureml.automl.core.constants import _TransformerOperatorMappings, TransformerParams, _OperatorNames

from .imputation_marker import ImputationMarker
from .lambda_transformer import LambdaTransformer

logger = logging.getLogger(__name__)


class GenericFeaturizers:
    """Container for generic featurizers."""

    @classmethod
    def imputation_marker(cls, *args: Any, **kwargs: Any) -> ImputationMarker:
        """Create imputation marker."""
        return ImputationMarker()

    @classmethod
    def lambda_featurizer(cls, *args: Any, **kwargs: Any) -> LambdaTransformer:
        """Create lambda featurizer."""
        return LambdaTransformer(*args, **kwargs)

    @classmethod
    def imputer(cls, *args: Any, **kwargs: Any) -> SimpleImputer:
        """Create Imputer."""
        strategy_key = 'strategy'
        strategy = kwargs.get(strategy_key, None)
        operator = _TransformerOperatorMappings.Imputer.get(strategy)
        if not operator:
            if strategy_key in kwargs:
                logger.warning("Given strategy is not supported, proceeding with default value")
            operator = _OperatorNames.Mean
            kwargs[strategy_key] = operator.lower()

        imputer = SimpleImputer(*args, **kwargs)

        # For engineered feature names. Since `SimpleImputer` is an sklearn class, we set the `operator_name` and
        # `transformer_name`. If it was an AutoMLTransformer we would have set the internal fields `_operator_name`
        # and `_transformer_name`.
        setattr(imputer, 'operator_name', operator)
        setattr(imputer, '_transformer_name', 'Imputer')
        return imputer

    @classmethod
    def minibatchkmeans_featurizer(cls, *args: Any, **kwargs: Any) -> MiniBatchKMeans:
        """Create mini batch k means featurizer."""
        # remove logger key as we don't own this featurizer
        return MiniBatchKMeans(*args, **kwargs)

    @classmethod
    def maxabsscaler(cls, *args: Any, **kwargs: Any) -> MaxAbsScaler:
        """Create maxabsscaler featurizer."""
        # remove logger key as we don't own this featurizer
        return MaxAbsScaler(*args, **kwargs)

    @classmethod
    def nimbus_missing_values_handler(cls, *args: Any, **kwargs: Any) -> NimbusMLMissingValuesHandler:
        """Create Imputer."""
        return NimbusMLMissingValuesHandler(*args, **kwargs)

    @classmethod
    def nimbus_column_selector(cls, *args: Any, **kwargs: Any) -> NimbusMLColumnSelector:
        """Create Column Selector transform."""
        return NimbusMLColumnSelector(*args, **kwargs)
