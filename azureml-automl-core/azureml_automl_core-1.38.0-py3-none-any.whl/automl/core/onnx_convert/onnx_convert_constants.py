# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Various constants used by the AutoML ONNX convert."""
import os
from enum import Enum


from azureml.automl.core.shared import constants


class SplitOnnxModelName(Enum):
    FeaturizerOnnxModel = 0
    EstimatorOnnxModel = 1


class OnnxConvertConstants:
    """Names for all model/operator names and ONNX operator names."""

    # The python version that is incompatible with onnx.
    OnnxIncompatiblePythonVersion = (3, 9)

    OnnxModelProducer = 'AutoML'
    OnnxModelNamePrefix = 'AutoML_ONNX_Model_'

    # Telemetry tags.
    LoggingTagPrefix = '[ONNXConverter]'
    EvtInitInput = '[InitInput]'
    EvtInitWithMetadata = '[InitWithMetadata]'
    EvtConvert = '[Convert]'

    StatusStart = '[Start]'
    StatusWarning = '[Warning]'
    StatusError = '[Error]'
    StatusEndSucceeded = '[End.Succeeded]'
    StatusEndFailed = '[End.Failed]'

    # Onnx model resources.
    InputRawColumnSchema = 'InputRawColumnSchema'
    InputOnnxColumnSchema = 'InputOnnxColumnSchema'
    RawColumnNameToOnnxNameMap = 'RawColumnNameToOnnxNameMap'
    CanEnableBatchMode = 'CanEnableBatchMode'

    # Splited onnx model paths.
    FeaturizerOnnxModelPath = constants.OUTPUT_PATH + "/" + "model_featurizer.onnx"
    EstimatorOnnxModelPath = constants.OUTPUT_PATH + "/" + "model_estimator.onnx"

    # Other data type names in the raw input data.
    Boolean = 'boolean'
    Mixed = 'mixed'
    MixedInteger = 'mixed-integer'

    # ---------------------------
    # Onnx domain names.
    # The traditional ML domain.
    OnnxMLDomain = 'ai.onnx.ml'
    # The MS domain.
    OnnxMSDomain = 'com.microsoft'

    # ---------------------------
    # The onnx op set version the whole converter is using.
    CurrentOnnxOPSetVersion = 11

    # ---------------------------
    # ONNX Operator names.
    ArrayFeatureExtractor = 'ArrayFeatureExtractor'
    FeatureVectorizer = 'FeatureVectorizer'
    OneHotEncoder = 'OneHotEncoder'
    LabelEncoder = 'LabelEncoder'
    Scaler = 'Scaler'

    IsNaN = 'IsNaN'
    Equal = 'Equal'
    And = 'And'
    Or = 'Or'
    Less = 'Less'
    Where = 'Where'

    MurmurHash3 = 'MurmurHash3'
    Cast = 'Cast'

    Tokenizer = 'Tokenizer'

    Sum = 'Sum'
    Sub = 'Sub'
    Div = 'Div'
    Mul = 'Mul'

    Slice = 'Slice'
    Concat = 'Concat'
    ReduceMax = 'ReduceMax'
    ReduceMean = 'ReduceMean'
    ArgMax = 'ArgMax'

    # ---------------------------
    # Dependent pkg Model/Operator names.
    SklearnCountVectorizer = 'SklearnCountVectorizer'
    SklearnTfidfVectorizer = 'SklearnTfidfVectorizer'
    LightGbmLGBMClassifier = 'LightGbmLGBMClassifier'
    LightGbmLGBMRegressor = 'LightGbmLGBMRegressor'
    XGBClassifier = 'XGBClassifier'
    XGBRegressor = 'XGBRegressor'
