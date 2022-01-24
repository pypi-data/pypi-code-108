# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains automated machine learning classes for transforming data in Azure Machine Learning."""

# Categorical
from .categorical import CategoricalFeaturizers, CatImputer, LabelEncoderTransformer, \
    HashOneHotVectorizerTransformer, OneHotEncoderTransformer

# Datetime
from .datetime import DateTimeFeaturesTransformer, DateTimeFeaturizers

# Data providers
from .data import DataProviders, WordEmbeddingsInfo

# Generic
from .generic import ImputationMarker, LambdaTransformer, GenericFeaturizers

# Numeric
from .numeric import BinTransformer, NumericFeaturizers

# Text
from .text import get_ngram_len, NaiveBayes, StringCastTransformer, max_ngram_len, \
    TextFeaturizers, WordEmbeddingTransformer, TFIDF_VECTORIZER_CONFIG, NimbusMLTextTargetEncoder, \
    BagOfWordsTransformer, StatsTransformer, StringConcatTransformer, BiLSTMAttentionTransformer

# Timeseries
from .timeseries import TimeSeriesTransformer, TimeSeriesPipelineType, NumericalizeTransformer, \
    MissingDummiesTransformer, LaggingTransformer

from .automltransformer import AutoMLTransformer
