# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Container for Categorical featurizers."""
from typing import Any
import numpy as np
from azureml.automl.core.constants import _OperatorNames
from nimbusml.feature_extraction.categorical import OneHotVectorizer as NimbusMLOneHotVectorizer
from nimbusml.feature_extraction.categorical import OneHotHashVectorizer as NimbusMLOneHotHashVectorizer

from azureml.automl.core.shared import constants

from ..generic.countbased_target_encoder import CountBasedTargetEncoder
from ..generic.crossvalidation_target_encoder import CrossValidationTargetEncoder
from ..generic.woe_target_encoder import WoEBasedTargetEncoder

from .cat_imputer import CatImputer
from .hashonehotvectorizer_transformer import HashOneHotVectorizerTransformer
from .labelencoder_transformer import LabelEncoderTransformer
from .onehotencoder_transformer import OneHotEncoderTransformer


class CategoricalFeaturizers:
    """Container for Categorical featurizers."""

    @classmethod
    def cat_imputer(cls, *args: Any, **kwargs: Any) -> CatImputer:
        """Create categorical imputer."""
        op_name_key = 'operator_name'
        if op_name_key in kwargs:
            operator_name = kwargs.pop('operator_name')
        else:
            operator_name = _OperatorNames.Mode

        imputer = CatImputer(*args, **kwargs)
        # For engineered feature names
        setattr(imputer, '_operator_name', operator_name)
        return imputer

    @classmethod
    def hashonehot_vectorizer(cls, *args: Any, **kwargs: Any) -> HashOneHotVectorizerTransformer:
        """Create hash one hot vectorizer."""
        return HashOneHotVectorizerTransformer(*args, **kwargs)

    @classmethod
    def labelencoder(cls, *args: Any, **kwargs: Any) -> LabelEncoderTransformer:
        """Create label encoder."""
        return LabelEncoderTransformer(*args, **kwargs)

    @classmethod
    def cat_targetencoder(cls, *args: Any, **kwargs: Any) -> CrossValidationTargetEncoder:
        """Create categorical target encoder featurizer."""
        return CrossValidationTargetEncoder(CountBasedTargetEncoder, *args, **kwargs)

    @classmethod
    def woe_targetencoder(cls, *args: Any, **kwargs: Any) -> CrossValidationTargetEncoder:
        """Create weight of evidence featurizer."""
        return CrossValidationTargetEncoder(WoEBasedTargetEncoder, *args, **kwargs)

    @classmethod
    def onehotencoder(cls, *args: Any, **kwargs: Any) -> OneHotEncoderTransformer:
        """Create onehotencoder."""
        if 'dtype' not in kwargs:
            kwargs['dtype'] = np.uint8
        if 'handle_unknown' not in kwargs:
            kwargs['handle_unknown'] = 'ignore'
        return OneHotEncoderTransformer(*args, **kwargs)

    @classmethod
    def nimbusml_onehotencoder(cls, *args: Any, **kwargs: Any) -> NimbusMLOneHotVectorizer:
        """OneHotEncoder using NimbusML."""
        return NimbusMLOneHotVectorizer(*args, **kwargs)

    @classmethod
    def nimbusml_hash_onehotencoder(cls, *args: Any, **kwargs: Any) -> NimbusMLOneHotHashVectorizer:
        """OneHotHashEncoder using NimbusML."""
        return NimbusMLOneHotHashVectorizer(*args, **kwargs)
