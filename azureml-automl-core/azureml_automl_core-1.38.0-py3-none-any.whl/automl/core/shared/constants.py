# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines automated ML constants used in Azure Machine Learning."""
from typing import List
import sys

from collections import OrderedDict
from enum import Enum


class SupportedModels:
    """Defines customer-facing names for algorithms supported by automated ML in Azure Machine Learning."""

    class Classification:
        """
        Defines classification algorithm names.

        TensorFlowDNN, TensorFlowLinearClassifier are deprecated.
        """

        LogisticRegression = 'LogisticRegression'
        SGDClassifier = 'SGD'
        MultinomialNB = 'MultinomialNaiveBayes'
        BernoulliNB = 'BernoulliNaiveBayes'
        SupportVectorMachine = 'SVM'
        LinearSupportVectorMachine = 'LinearSVM'
        KNearestNeighborsClassifier = 'KNN'
        DecisionTree = 'DecisionTree'
        RandomForest = 'RandomForest'
        ExtraTrees = 'ExtremeRandomTrees'
        LightGBMClassifier = 'LightGBM'
        GradientBoosting = 'GradientBoosting'
        TensorFlowDNNClassifier = 'TensorFlowDNN'
        TensorFlowLinearClassifier = 'TensorFlowLinearClassifier'
        XGBoostClassifier = 'XGBoostClassifier'
        AveragedPerceptronClassifier = 'AveragedPerceptronClassifier'
        TabNetClassifier = 'TabnetClassifier'

    class Regression:
        """Defines regression algorithm names.

        TensorFlowDNN, TensorFlowLinearRegressor are deprecated.
        """

        ElasticNet = 'ElasticNet'
        GradientBoostingRegressor = 'GradientBoosting'
        DecisionTreeRegressor = 'DecisionTree'
        KNearestNeighborsRegressor = 'KNN'
        LassoLars = 'LassoLars'
        SGDRegressor = 'SGD'
        RandomForestRegressor = 'RandomForest'
        ExtraTreesRegressor = 'ExtremeRandomTrees'
        LightGBMRegressor = 'LightGBM'
        TensorFlowLinearRegressor = 'TensorFlowLinearRegressor'
        TensorFlowDNNRegressor = 'TensorFlowDNN'
        XGBoostRegressor = 'XGBoostRegressor'
        FastLinearRegressor = 'FastLinearRegressor'
        OnlineGradientDescentRegressor = 'OnlineGradientDescentRegressor'
        TabNetRegressor = 'TabnetRegressor'

    class Forecasting(Regression):
        """Defines forecasting algorithm names."""

        Arimax = 'Arimax'
        AutoArima = 'AutoArima'
        Average = 'Average'
        ExponentialSmoothing = 'ExponentialSmoothing'
        Naive = 'Naive'
        Prophet = 'Prophet'
        SeasonalAverage = 'SeasonalAverage'
        SeasonalNaive = 'SeasonalNaive'
        TCNForecaster = 'TCNForecaster'


class _NonExplainableModels:
    """Defines the currently non explanable models."""

    FORECASTING = [SupportedModels.Forecasting.TCNForecaster]


class _PrivateModels:
    """Defines names for private/non-public-facing algorithms in automated ML in Azure Machine Learning."""

    class Forecasting:
        """Defines private forecasting algorithm names."""
        # pass

    class Regression:
        """Defines private regression algorithm names."""
        # pass

    class Classification:
        """Defines private classification algorithm names."""
        # pass


class ModelClassNames:
    """Defines class names for models.

    These are model wrapper class names in the pipeline specs.
    """

    class ClassificationModelClassNames:
        """Defines classification model names."""

        LogisticRegression = 'LogisticRegression'
        SGDClassifier = 'SGDClassifierWrapper'
        MultinomialNB = 'NBWrapper'
        BernoulliNB = 'NBWrapper'  # BernoulliNB use NBWrapper as classname
        SupportVectorMachine = 'SVCWrapper'
        LinearSupportVectorMachine = 'LinearSVMWrapper'
        KNearestNeighborsClassifier = 'KNeighborsClassifier'
        DecisionTree = 'DecisionTreeClassifier'
        RandomForest = 'RandomForestClassifier'
        ExtraTrees = 'ExtraTreesClassifier'
        LightGBMClassifier = 'LightGBMClassifier'
        GradientBoosting = 'GradientBoostingClassifier'
        TensorFlowDNNClassifier = 'TFDNNClassifierWrapper'
        TensorFlowLinearClassifier = 'TFLinearClassifierWrapper'
        XGBoostClassifier = 'XGBoostClassifier'
        NimbusMLAveragedPerceptronClassifier = 'NimbusMlAveragedPerceptronClassifier'
        NimbusMLLinearSVMClassifier = 'NimbusMlLinearSVMClassifier'
        CatBoostClassifier = 'CatBoostClassifier'
        TabNetClassifier = 'TabnetClassifier'
        AveragedPerceptronMulticlassClassifier = 'AveragedPerceptronMulticlassClassifier'
        LinearSvmMulticlassClassifier = 'LinearSvmMulticlassClassifier'

    class RegressionModelClassNames:
        """Defines regression model names."""

        ElasticNet = 'ElasticNet'
        GradientBoostingRegressor = 'GradientBoostingRegressor'
        DecisionTreeRegressor = 'DecisionTreeRegressor'
        KNearestNeighborsRegressor = 'KNeighborsRegressor'
        LassoLars = 'LassoLars'
        SGDRegressor = 'SGDRegressor'
        RandomForestRegressor = 'RandomForestRegressor'
        ExtraTreesRegressor = 'ExtraTreesRegressor'
        LightGBMRegressor = 'LightGBMRegressor'
        TensorFlowLinearRegressor = 'TFLinearRegressorWrapper'
        TensorFlowDNNRegressor = 'TFDNNRegressorWrapper'
        XGBoostRegressor = 'XGBoostRegressor'
        NimbusMLFastLinearRegressor = 'NimbusMlFastLinearRegressor'
        NimbusMLOnlineGradientDescentRegressor = 'NimbusMlOnlineGradientDescentRegressor'
        CatBoostRegressor = 'CatBoostRegressor'
        TabNetRegressor = 'TabnetRegressor'

    class ForecastingModelClassNames(RegressionModelClassNames):
        """Defines forecasting model names."""

        Arimax = 'Arimax'
        AutoArima = 'AutoArima'
        Average = 'Average'
        ExponentialSmoothing = 'ExponentialSmoothing'
        Naive = 'Naive'
        Prophet = 'Prophet'
        SeasonalAverage = 'SeasonalAverage'
        SeasonalNaive = 'SeasonalNaive'
        TCNForecaster = 'TCNForecaster'


class LegacyModelNames:
    """
    Defines names for all models supported by the Miro recommender in Automated ML.

    These names are still used to refer to objects in the Miro database, but are not
    used by any Automated ML clients.
    """

    class ClassificationLegacyModelNames:
        """Defines names for all Miro classification models."""

        LogisticRegression = 'logistic regression'
        SGDClassifier = 'SGD classifier'
        MultinomialNB = 'MultinomialNB'
        BernoulliNB = 'BernoulliNB'
        SupportVectorMachine = 'SVM'
        LinearSupportVectorMachine = 'LinearSVM'
        KNearestNeighborsClassifier = 'kNN'
        DecisionTree = 'DT'
        RandomForest = 'RF'
        ExtraTrees = 'extra trees'
        LightGBMClassifier = 'lgbm_classifier'
        GradientBoosting = 'gradient boosting'
        TensorFlowDNNClassifier = 'TF DNNClassifier'
        TensorFlowLinearClassifier = 'TF LinearClassifier'
        XGBoostClassifier = 'xgboost classifier'
        NimbusMLAveragedPerceptronClassifier = 'averaged perceptron classifier'
        NimbusMLLinearSVMClassifier = 'nimbusml linear svm classifier'
        CatBoostClassifier = 'catboost_classifier'
        TabNetClasifier = 'tabnet_classifier'

    class RegressionLegacyModelNames:
        """Defines names for all Miro regression models."""

        ElasticNet = 'Elastic net'
        GradientBoostingRegressor = 'Gradient boosting regressor'
        DecisionTreeRegressor = 'DT regressor'
        KNearestNeighborsRegressor = 'kNN regressor'
        LassoLars = 'Lasso lars'
        SGDRegressor = 'SGD regressor'
        RandomForestRegressor = 'RF regressor'
        ExtraTreesRegressor = 'extra trees regressor'
        LightGBMRegressor = 'lightGBM regressor'
        TensorFlowLinearRegressor = 'TF LinearRegressor'
        TensorFlowDNNRegressor = 'TF DNNRegressor'
        XGBoostRegressor = 'xgboost regressor'
        NimbusMLFastLinearRegressor = 'nimbusml fast linear regressor'
        NimbusMLOnlineGradientDescentRegressor = 'nimbusml online gradient descent regressor'
        CatBoostRegressor = 'catboost_regressor'
        TabNetRegressor = 'tabnet_regressor'

    class ForecastingLegacyModelNames(RegressionLegacyModelNames):
        """Defines names for all forecasting legacy models."""

        pass


ARTIFACT_TAG = "artifact"
MODEL_EXPLANATION_TAG = "model_explanation"

# Use different paths for local storage vs remote storage. This is because we can't store things in the outputs folder
# locally otherwise hosttools will attempt to upload the file (causing a resource conflict), but we can't change the
# remote path.
LOCAL_OUTPUT_PATH = "artifacts"
MODEL_FILENAME = "model.pkl"
PT_MODEL_FILENAME = "model.pt"
LOCAL_MODEL_PATH = LOCAL_OUTPUT_PATH + "/" + MODEL_FILENAME
LOCAL_MODEL_PATH_TRAIN = LOCAL_OUTPUT_PATH + "/" + "internal_cross_validated_models.pkl"
LOCAL_MODEL_PATH_ONNX = LOCAL_OUTPUT_PATH + "/" + "model.onnx"
LOCAL_MODEL_RESOURCE_PATH_ONNX = LOCAL_OUTPUT_PATH + "/" + "model_onnx.json"
LOCAL_DEPENDENCIES_PATH = LOCAL_OUTPUT_PATH + "/" + "env_dependencies.json"
LOCAL_CONDA_ENV_FILE_PATH = LOCAL_OUTPUT_PATH + "/" + "conda_env_v_1_0_0.yml"
LOCAL_SCORING_FILE_PATH = LOCAL_OUTPUT_PATH + "/" + "scoring_file_v_1_0_0.py"
LOCAL_SCORING_FILE_V2_PATH = LOCAL_OUTPUT_PATH + "/" + "scoring_file_v_2_0_0.py"
LOCAL_PIPELINE_GRAPH_PATH = LOCAL_OUTPUT_PATH + "/" + "pipeline_graph.json"
LOCAL_CHILD_RUNS_SUMMARY_PATH = LOCAL_OUTPUT_PATH + "/" + "child_runs_summary.json"
LOCAL_VERIFIER_RESULTS_PATH = LOCAL_OUTPUT_PATH + "/" + 'verifier_results.json'

# These are all the remote paths.
OUTPUT_PATH = "outputs"
MODEL_PATH = OUTPUT_PATH + "/" + MODEL_FILENAME
PT_MODEL_PATH = OUTPUT_PATH + "/" + PT_MODEL_FILENAME
MODEL_PATH_TRAIN = OUTPUT_PATH + "/" + "internal_cross_validated_models.pkl"
MODEL_PATH_ONNX = OUTPUT_PATH + "/" + "model.onnx"
MODEL_RESOURCE_PATH_ONNX = OUTPUT_PATH + "/" + "model_onnx.json"
PROPERTY_KEY_OF_MODEL_PATH = "model_output_path"
DEPENDENCIES_PATH = OUTPUT_PATH + "/" + "env_dependencies.json"
CONDA_ENV_FILE_PATH = OUTPUT_PATH + "/" + "conda_env_v_1_0_0.yml"
SCORING_FILE_PATH = OUTPUT_PATH + "/" + "scoring_file_v_1_0_0.py"
SCORING_FILE_V2_PATH = OUTPUT_PATH + "/" + "scoring_file_v_2_0_0.py"
PIPELINE_GRAPH_PATH = OUTPUT_PATH + "/" + "pipeline_graph.json"
CHILD_RUNS_SUMMARY_PATH = OUTPUT_PATH + "/" + "child_runs_summary.json"
VERIFIER_RESULTS_PATH = OUTPUT_PATH + "/" + 'verifier_results.json'
FEATURIZATION_ENGG_FEAT_NAMES_PATH = OUTPUT_PATH + "/" + "engineered_feature_names.json"
FEATURIZATION_SUMMARY_PATH = OUTPUT_PATH + "/" + "featurization_summary.json"
MLFLOW_OUTPUT_PATH = OUTPUT_PATH
MLFLOW_FEATURIZATION_OUTPUT = OUTPUT_PATH + "/" + "featurization"
MLFLOW_TRANSFORMER_PATH = MLFLOW_FEATURIZATION_OUTPUT + "/" + "data_transformer.pkl"

PIPELINE_GRAPH_VERSION = '1.0.0'
MAX_ITERATIONS = 1000
MAX_SAMPLES_AUTOBLOCK = 5000
MAX_SAMPLES_AUTOBLOCKED_ALGOS = [SupportedModels.Classification.KNearestNeighborsClassifier,
                                 SupportedModels.Regression.KNearestNeighborsRegressor,
                                 SupportedModels.Classification.SupportVectorMachine]
EARLY_STOPPING_NUM_LANDMARKS = 20
MULTINOMIAL_ALGO_TAG = 'Multinomial'
TIMEOUT_TAG = "timeout"

"""Names of algorithms that do not support sample weights."""
Sample_Weights_Unsupported = {
    ModelClassNames.RegressionModelClassNames.ElasticNet,
    ModelClassNames.ClassificationModelClassNames.KNearestNeighborsClassifier,
    ModelClassNames.RegressionModelClassNames.KNearestNeighborsRegressor,
    ModelClassNames.RegressionModelClassNames.LassoLars,
}
"""Algorithm names that we must force to run in single threaded mode."""
SINGLE_THREADED_ALGORITHMS = [
    ModelClassNames.ClassificationModelClassNames.KNearestNeighborsClassifier,
    ModelClassNames.RegressionModelClassNames.KNearestNeighborsRegressor
]
XGBOOST_SUPPORTED_VERSION = "0.90"  # Latest supported version of xgboost, update this as we change our supported range
XGBOOST_SUPPORTED_GPU_VERSION = "1.1.1"  # Current XGBoost version used on GPU environments (see GPU Curated Env).


class EnsembleConstants(object):
    """Defines constants used for Ensemble iterations."""

    VOTING_ENSEMBLE_PIPELINE_ID = "__AutoML_Ensemble__"
    STACK_ENSEMBLE_PIPELINE_ID = "__AutoML_Stack_Ensemble__"
    ENSEMBLE_PIPELINE_IDS = [VOTING_ENSEMBLE_PIPELINE_ID, STACK_ENSEMBLE_PIPELINE_ID]
    # by default, we'll use 20% of the training data (when doing TrainValidation split) for training the meta learner
    DEFAULT_TRAIN_PERCENTAGE_FOR_STACK_META_LEARNER = 0.2

    class StackMetaLearnerAlgorithmNames(object):
        """Defines algorithms supported for training the Stack Ensemble meta learner."""

        LogisticRegression = SupportedModels.Classification.LogisticRegression
        LogisticRegressionCV = "LogisticRegressionCV"
        LightGBMClassifier = SupportedModels.Classification.LightGBMClassifier
        ElasticNet = SupportedModels.Regression.ElasticNet
        ElasticNetCV = "ElasticNetCV"
        LightGBMRegressor = SupportedModels.Regression.LightGBMRegressor
        LinearRegression = "LinearRegression"
        ALL = [
            LogisticRegression,
            LogisticRegressionCV,
            LightGBMClassifier,
            ElasticNet,
            ElasticNetCV,
            LightGBMRegressor,
            LinearRegression]


class HyperparameterSweepingConstants:
    """Defines constants related with hyperparameter tunning."""
    AutoHPTuningParentPipelineId = '__AutoML_HyperparameterSweeping__'


class ModelName:
    """Defines a model name that includes customer, legacy, and class names."""

    def __init__(self, customer_model_name, legacy_model_name, model_class_name, is_deprecated=False):
        """Init ModelName."""
        self.customer_model_name = customer_model_name
        self.legacy_model_name = legacy_model_name
        self.model_class_name = model_class_name
        self.is_deprecated = is_deprecated

    def __repr__(self):
        return self.customer_model_name


class SupportedModelNames:
    """Defines supported models where each model has a customer name, legacy model name, and model class name."""

    SupportedClassificationModelList = [
        ModelName(
            SupportedModels.Classification.
            LogisticRegression,
            LegacyModelNames.ClassificationLegacyModelNames.LogisticRegression,
            ModelClassNames.ClassificationModelClassNames.LogisticRegression),
        ModelName(
            SupportedModels.Classification.
            SGDClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.SGDClassifier,
            ModelClassNames.ClassificationModelClassNames.SGDClassifier),
        ModelName(
            SupportedModels.Classification.
            MultinomialNB,
            LegacyModelNames.ClassificationLegacyModelNames.MultinomialNB,
            ModelClassNames.ClassificationModelClassNames.MultinomialNB),
        ModelName(
            SupportedModels.Classification.
            BernoulliNB,
            LegacyModelNames.ClassificationLegacyModelNames.BernoulliNB,
            ModelClassNames.ClassificationModelClassNames.BernoulliNB),
        ModelName(
            SupportedModels.Classification.
            SupportVectorMachine,
            LegacyModelNames.ClassificationLegacyModelNames.
            SupportVectorMachine,
            ModelClassNames.ClassificationModelClassNames.SupportVectorMachine),
        ModelName(
            SupportedModels.Classification.
            LinearSupportVectorMachine,
            LegacyModelNames.ClassificationLegacyModelNames.
            LinearSupportVectorMachine,
            ModelClassNames.ClassificationModelClassNames.
            LinearSupportVectorMachine),
        ModelName(
            SupportedModels.Classification.
            KNearestNeighborsClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.
            KNearestNeighborsClassifier,
            ModelClassNames.ClassificationModelClassNames.
            KNearestNeighborsClassifier),
        ModelName(
            SupportedModels.Classification.
            DecisionTree,
            LegacyModelNames.ClassificationLegacyModelNames.DecisionTree,
            ModelClassNames.ClassificationModelClassNames.DecisionTree),
        ModelName(
            SupportedModels.Classification.
            RandomForest,
            LegacyModelNames.ClassificationLegacyModelNames.RandomForest,
            ModelClassNames.ClassificationModelClassNames.RandomForest),
        ModelName(
            SupportedModels.Classification.
            ExtraTrees,
            LegacyModelNames.ClassificationLegacyModelNames.ExtraTrees,
            ModelClassNames.ClassificationModelClassNames.ExtraTrees),
        ModelName(
            SupportedModels.Classification.
            LightGBMClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.LightGBMClassifier,
            ModelClassNames.ClassificationModelClassNames.LightGBMClassifier),
        ModelName(
            SupportedModels.Classification.
            XGBoostClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.XGBoostClassifier,
            ModelClassNames.ClassificationModelClassNames.XGBoostClassifier),
        ModelName(
            SupportedModels.Classification.AveragedPerceptronClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.NimbusMLAveragedPerceptronClassifier,
            ModelClassNames.ClassificationModelClassNames.NimbusMLAveragedPerceptronClassifier),
        ModelName(
            SupportedModels.Classification.AveragedPerceptronClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.NimbusMLAveragedPerceptronClassifier,
            ModelClassNames.ClassificationModelClassNames.AveragedPerceptronMulticlassClassifier),
        ModelName(
            SupportedModels.Classification.
            GradientBoosting,
            LegacyModelNames.ClassificationLegacyModelNames.GradientBoosting,
            ModelClassNames.ClassificationModelClassNames.GradientBoosting),
        ModelName(
            SupportedModels.Classification.
            TensorFlowDNNClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.
            TensorFlowDNNClassifier,
            ModelClassNames.ClassificationModelClassNames.
            TensorFlowDNNClassifier,
            is_deprecated=True),
        ModelName(
            SupportedModels.Classification.
            TensorFlowLinearClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.
            TensorFlowLinearClassifier,
            ModelClassNames.ClassificationModelClassNames.
            TensorFlowLinearClassifier,
            is_deprecated=True),
        ModelName(
            SupportedModels.Classification.
            TabNetClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.TabNetClasifier,
            ModelClassNames.ClassificationModelClassNames.TabNetClassifier)]

    CommonSupportedRegressionModelList = [
        ModelName(
            SupportedModels.Regression.ElasticNet,
            LegacyModelNames.RegressionLegacyModelNames.ElasticNet,
            ModelClassNames.RegressionModelClassNames.ElasticNet),
        ModelName(
            SupportedModels.Regression.
            GradientBoostingRegressor,
            LegacyModelNames.RegressionLegacyModelNames.
            GradientBoostingRegressor,
            ModelClassNames.RegressionModelClassNames.
            GradientBoostingRegressor),
        ModelName(
            SupportedModels.Regression.
            DecisionTreeRegressor,
            LegacyModelNames.RegressionLegacyModelNames.DecisionTreeRegressor,
            ModelClassNames.RegressionModelClassNames.DecisionTreeRegressor),
        ModelName(
            SupportedModels.Regression.
            KNearestNeighborsRegressor,
            LegacyModelNames.RegressionLegacyModelNames.
            KNearestNeighborsRegressor,
            ModelClassNames.RegressionModelClassNames.
            KNearestNeighborsRegressor),
        ModelName(
            SupportedModels.Regression.LassoLars,
            LegacyModelNames.RegressionLegacyModelNames.LassoLars,
            ModelClassNames.RegressionModelClassNames.LassoLars),
        ModelName(
            SupportedModels.Regression.
            SGDRegressor,
            LegacyModelNames.RegressionLegacyModelNames.SGDRegressor,
            ModelClassNames.RegressionModelClassNames.SGDRegressor),
        ModelName(
            SupportedModels.Regression.
            RandomForestRegressor,
            LegacyModelNames.RegressionLegacyModelNames.RandomForestRegressor,
            ModelClassNames.RegressionModelClassNames.RandomForestRegressor),
        ModelName(
            SupportedModels.Regression.
            ExtraTreesRegressor,
            LegacyModelNames.RegressionLegacyModelNames.ExtraTreesRegressor,
            ModelClassNames.RegressionModelClassNames.ExtraTreesRegressor),
        ModelName(
            SupportedModels.Regression.
            LightGBMRegressor,
            LegacyModelNames.RegressionLegacyModelNames.LightGBMRegressor,
            ModelClassNames.RegressionModelClassNames.LightGBMRegressor),
        ModelName(
            SupportedModels.Regression.
            XGBoostRegressor,
            LegacyModelNames.RegressionLegacyModelNames.XGBoostRegressor,
            ModelClassNames.RegressionModelClassNames.XGBoostRegressor),
        ModelName(
            SupportedModels.Regression.
            TensorFlowLinearRegressor,
            LegacyModelNames.RegressionLegacyModelNames.
            TensorFlowLinearRegressor,
            ModelClassNames.RegressionModelClassNames.
            TensorFlowLinearRegressor,
            is_deprecated=True),
        ModelName(
            SupportedModels.Regression.
            TensorFlowDNNRegressor,
            LegacyModelNames.RegressionLegacyModelNames.TensorFlowDNNRegressor,
            ModelClassNames.RegressionModelClassNames.TensorFlowDNNRegressor,
            is_deprecated=True),
        ModelName(
            SupportedModels.Regression.
            TabNetRegressor,
            LegacyModelNames.RegressionLegacyModelNames.TabNetRegressor,
            ModelClassNames.RegressionModelClassNames.TabNetRegressor)]

    SupportedRegressionModelList = CommonSupportedRegressionModelList + [
        ModelName(
            SupportedModels.Regression.FastLinearRegressor,
            LegacyModelNames.RegressionLegacyModelNames.NimbusMLFastLinearRegressor,
            ModelClassNames.RegressionModelClassNames.NimbusMLFastLinearRegressor),
        ModelName(
            SupportedModels.Regression.OnlineGradientDescentRegressor,
            LegacyModelNames.RegressionLegacyModelNames.NimbusMLOnlineGradientDescentRegressor,
            ModelClassNames.RegressionModelClassNames.NimbusMLOnlineGradientDescentRegressor),
    ]

    SupportedForecastingModelList = CommonSupportedRegressionModelList + [
        ModelName(
            SupportedModels.Forecasting.AutoArima,
            None,
            ModelClassNames.ForecastingModelClassNames.AutoArima),
        ModelName(
            SupportedModels.Forecasting.ExponentialSmoothing,
            None,
            ModelClassNames.ForecastingModelClassNames.ExponentialSmoothing),
        ModelName(
            SupportedModels.Forecasting.Arimax,
            None,
            ModelClassNames.ForecastingModelClassNames.Arimax),
        ModelName(
            SupportedModels.Forecasting.Prophet,
            None,
            ModelClassNames.ForecastingModelClassNames.Prophet),
        ModelName(
            SupportedModels.Forecasting.TCNForecaster,
            None,
            ModelClassNames.ForecastingModelClassNames.TCNForecaster),
        ModelName(
            SupportedModels.Forecasting.Naive,
            None,
            ModelClassNames.ForecastingModelClassNames.Naive),
        ModelName(
            SupportedModels.Forecasting.SeasonalNaive,
            None,
            ModelClassNames.ForecastingModelClassNames.SeasonalNaive),
        ModelName(
            SupportedModels.Forecasting.Average,
            None,
            ModelClassNames.ForecastingModelClassNames.Average),
        ModelName(
            SupportedModels.Forecasting.SeasonalAverage,
            None,
            ModelClassNames.ForecastingModelClassNames.SeasonalAverage)]

    SupportedStreamingModelList = [
        ModelName(
            SupportedModels.Classification.AveragedPerceptronClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.NimbusMLAveragedPerceptronClassifier,
            ModelClassNames.ClassificationModelClassNames.AveragedPerceptronMulticlassClassifier),
        ModelName(
            SupportedModels.Classification.LinearSupportVectorMachine,
            LegacyModelNames.ClassificationLegacyModelNames.NimbusMLLinearSVMClassifier,
            ModelClassNames.ClassificationModelClassNames.LinearSupportVectorMachine),
        ModelName(
            SupportedModels.Regression.FastLinearRegressor,
            LegacyModelNames.RegressionLegacyModelNames.NimbusMLFastLinearRegressor,
            ModelClassNames.RegressionModelClassNames.NimbusMLFastLinearRegressor),
        ModelName(
            SupportedModels.Regression.OnlineGradientDescentRegressor,
            LegacyModelNames.RegressionLegacyModelNames.NimbusMLOnlineGradientDescentRegressor,
            ModelClassNames.RegressionModelClassNames.NimbusMLOnlineGradientDescentRegressor),
    ]


class _PrivateModelNames:
    """
    Defines private models where each model has a customer name, legacy model name, and model class name.
    Private models are not yet public facing, so they are not in SupportedModelNames.
    """
    PrivateClassificationModelList = []  # type: List[ModelName]
    PrivateRegressionModelList = []  # type: List[ModelName]
    PrivateForecastingModelList = PrivateRegressionModelList + []  # type: List[ModelName]


class ModelNameMappings:
    """Defines model name mappings."""

    CustomerFacingModelToLegacyModelMapClassification = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedClassificationModelList],
        [model.legacy_model_name for model in SupportedModelNames.
            SupportedClassificationModelList]))

    CustomerFacingModelToLegacyModelMapRegression = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedRegressionModelList],
        [model.legacy_model_name for model in SupportedModelNames.
            SupportedRegressionModelList]))

    CustomerFacingModelToLegacyModelMapForecasting = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedForecastingModelList],
        [model.legacy_model_name for model in SupportedModelNames.
            SupportedForecastingModelList]))

    PrivateModelToLegacyModelMapClassification = dict(zip(
        [model.customer_model_name for model in _PrivateModelNames.
            PrivateClassificationModelList],
        [model.legacy_model_name for model in _PrivateModelNames.
            PrivateClassificationModelList]))

    PrivateModelToLegacyModelMapRegression = dict(zip(
        [model.customer_model_name for model in _PrivateModelNames.
            PrivateRegressionModelList],
        [model.legacy_model_name for model in _PrivateModelNames.
            PrivateRegressionModelList]))

    PrivateModelToLegacyModelMapForecasting = dict(zip(
        [model.customer_model_name for model in _PrivateModelNames.
            PrivateForecastingModelList],
        [model.legacy_model_name for model in _PrivateModelNames.
            PrivateForecastingModelList]))

    CustomerFacingModelToClassNameModelMapClassification = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedClassificationModelList],
        [model.model_class_name for model in SupportedModelNames.
            SupportedClassificationModelList]))

    CustomerFacingModelToClassNameModelMapRegression = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedRegressionModelList],
        [model.model_class_name for model in SupportedModelNames.
            SupportedRegressionModelList]))

    CustomerFacingModelToClassNameModelMapForecasting = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedForecastingModelList],
        [model.model_class_name for model in SupportedModelNames.
            SupportedForecastingModelList]))

    ClassNameToCustomerFacingModelMapClassification = dict(zip(
        [model.model_class_name for model in SupportedModelNames.
            SupportedClassificationModelList],
        [model.customer_model_name for model in SupportedModelNames.
            SupportedClassificationModelList]))

    ClassNameToCustomerFacingModelMapRegression = dict(zip(
        [model.model_class_name for model in SupportedModelNames.
            SupportedRegressionModelList],
        [model.customer_model_name for model in SupportedModelNames.
            SupportedRegressionModelList]))

    ClassNameToCustomerFacingModelMapForecasting = dict(zip(
        [model.model_class_name for model in SupportedModelNames.
            SupportedForecastingModelList],
        [model.customer_model_name for model in SupportedModelNames.
            SupportedForecastingModelList]))


class ModelCategories:
    """Defines categories for models."""

    PARTIAL_FIT = {
        ModelClassNames.ClassificationModelClassNames.MultinomialNB,
        ModelClassNames.ClassificationModelClassNames.BernoulliNB,
        ModelClassNames.ClassificationModelClassNames.SGDClassifier,
        ModelClassNames.ClassificationModelClassNames.TensorFlowLinearClassifier,
        ModelClassNames.ClassificationModelClassNames.TensorFlowDNNClassifier,
        ModelClassNames.ClassificationModelClassNames.NimbusMLAveragedPerceptronClassifier,
        ModelClassNames.ClassificationModelClassNames.NimbusMLLinearSVMClassifier,
        ModelClassNames.ClassificationModelClassNames.AveragedPerceptronMulticlassClassifier,
        ModelClassNames.ClassificationModelClassNames.LinearSvmMulticlassClassifier,
        ModelClassNames.RegressionModelClassNames.NimbusMLFastLinearRegressor,
        ModelClassNames.RegressionModelClassNames.NimbusMLOnlineGradientDescentRegressor,
        ModelClassNames.RegressionModelClassNames.SGDRegressor,
        ModelClassNames.RegressionModelClassNames.TensorFlowLinearRegressor,
        ModelClassNames.RegressionModelClassNames.TensorFlowDNNRegressor
    }

    CLASSICAL_TIMESERIES_MODELS = {
        ModelClassNames.ForecastingModelClassNames.Average,
        ModelClassNames.ForecastingModelClassNames.AutoArima,
        ModelClassNames.ForecastingModelClassNames.ExponentialSmoothing,
        ModelClassNames.ForecastingModelClassNames.Naive,
        ModelClassNames.ForecastingModelClassNames.SeasonalAverage,
        ModelClassNames.ForecastingModelClassNames.SeasonalNaive,
        ModelClassNames.ForecastingModelClassNames.Arimax
    }


class PreprocessorCategories:
    """Defines categories for preprocessors."""

    PARTIAL_FIT = {'StandardScaler', 'MinMaxScaler', 'MaxAbsScaler'}


class Defaults:
    """Defines default values for pipelines."""

    DEFAULT_PIPELINE_SCORE = float('NaN')  # Jasmine and 016N
    INVALID_PIPELINE_VALIDATION_SCORES = {}
    INVALID_PIPELINE_FITTED = ''
    INVALID_PIPELINE_OBJECT = None


class RunState:
    """Defines states a run can be in."""

    START_RUN = 'running'
    FAIL_RUN = 'failed'
    CANCEL_RUN = 'canceled'
    COMPLETE_RUN = 'completed'
    PREPARE_RUN = 'preparing'


class API:
    """Defines names for the Azure Machine Learning API operations that can be performed."""

    CreateExperiment = 'Create Experiment'
    CreateParentRun = 'Create Parent Run'
    GetNextPipeline = 'Get Pipeline'
    SetParentRunStatus = 'Set Parent Run Status'
    StartRemoteRun = 'Start Remote Run'
    StartRemoteSnapshotRun = 'Start Remote Snapshot Run'
    CancelChildRun = 'Cancel Child Run'
    StartChildRun = 'Start Child Run'
    SetRunProperties = 'Set Run Properties'
    LogMetrics = 'Log Metrics'
    InstantiateRun = 'Get Run'
    GetChildren = 'Get Children'


class AcquisitionFunction:
    """Defines names for all acquisition functions used to select the next pipeline.

    The default is EI (expected improvement).
    """

    EI = "EI"
    PI = "PI"
    UCB = "UCB"
    THOMPSON = "thompson"
    EXPECTED = "expected"

    FULL_SET = {EI, PI, UCB, THOMPSON, EXPECTED}


class TrainingResultsType:
    """Defines potential results from runners class."""

    # Metrics
    TRAIN_METRICS = 'train'
    VALIDATION_METRICS = 'validation'
    TEST_METRICS = 'test'
    TRAIN_FROM_FULL_METRICS = 'train from full'
    TEST_FROM_FULL_METRICS = 'test from full'
    CV_METRICS = 'CV'
    CV_MEAN_METRICS = 'CV mean'

    # Other useful things
    TRAIN_TIME = 'train time'
    FIT_TIME = 'fit_time'
    PREDICT_TIME = 'predict_time'
    BLOB_TIME = 'blob_time'
    ALL_TIME = {TRAIN_TIME, FIT_TIME, PREDICT_TIME}
    TRAIN_PERCENT = 'train_percent'
    MODELS = 'models'

    # Status:
    TRAIN_VALIDATE_STATUS = 'train validate status'
    TRAIN_FULL_STATUS = 'train full status'
    CV_STATUS = 'CV status'


class MetricExtrasConstants:
    """Defines internal values of Confidence Intervals"""
    UPPER_95_PERCENTILE = "upper_ci_95"
    LOWER_95_PERCENTILE = "lower_ci_95"
    VALUE = "value"

    # Confidence Interval metric name format
    MetricExtrasFormat = "{}_extras"


class Metric:
    """Defines all metrics supported by classification and regression."""

    # Classification
    AUCBinary = 'AUC_binary'
    AUCMacro = 'AUC_macro'
    AUCMicro = 'AUC_micro'
    AUCWeighted = 'AUC_weighted'
    Accuracy = 'accuracy'
    WeightedAccuracy = 'weighted_accuracy'
    BalancedAccuracy = 'balanced_accuracy'
    NormMacroRecall = 'norm_macro_recall'
    LogLoss = 'log_loss'
    F1Binary = 'f1_score_binary'
    F1Micro = 'f1_score_micro'
    F1Macro = 'f1_score_macro'
    F1Weighted = 'f1_score_weighted'
    PrecisionBinary = 'precision_score_binary'
    PrecisionMicro = 'precision_score_micro'
    PrecisionMacro = 'precision_score_macro'
    PrecisionWeighted = 'precision_score_weighted'
    RecallBinary = 'recall_score_binary'
    RecallMicro = 'recall_score_micro'
    RecallMacro = 'recall_score_macro'
    RecallWeighted = 'recall_score_weighted'
    AvgPrecisionBinary = 'average_precision_score_binary'
    AvgPrecisionMicro = 'average_precision_score_micro'
    AvgPrecisionMacro = 'average_precision_score_macro'
    AvgPrecisionWeighted = 'average_precision_score_weighted'
    AccuracyTable = 'accuracy_table'
    ConfusionMatrix = 'confusion_matrix'
    MatthewsCorrelation = 'matthews_correlation'

    # Regression
    ExplainedVariance = 'explained_variance'
    R2Score = 'r2_score'
    Spearman = 'spearman_correlation'
    MAPE = 'mean_absolute_percentage_error'
    SMAPE = 'symmetric_mean_absolute_percentage_error'
    MeanAbsError = 'mean_absolute_error'
    MedianAbsError = 'median_absolute_error'
    RMSE = 'root_mean_squared_error'
    RMSLE = 'root_mean_squared_log_error'
    NormMeanAbsError = 'normalized_mean_absolute_error'
    NormMedianAbsError = 'normalized_median_absolute_error'
    NormRMSE = 'normalized_root_mean_squared_error'
    NormRMSLE = 'normalized_root_mean_squared_log_error'
    Residuals = 'residuals'
    PredictedTrue = 'predicted_true'

    # Forecast
    ForecastMAPE = 'forecast_mean_absolute_percentage_error'
    ForecastSMAPE = 'forecast_symmetric_mean_absolute_percentage_error'
    ForecastResiduals = 'forecast_residuals'
    ForecastTrainTable = 'forecast_train_table'
    ForecastValidateTable = 'forecast_validate_table'

    # Image Multi Label Classification
    IOU = 'iou'  # Intersection Over Union

    # Image Object Detection
    MeanAveragePrecision = 'mean_average_precision'

    SCALAR_CLASSIFICATION_SET = {
        AUCBinary, AUCMacro, AUCMicro, AUCWeighted, Accuracy,
        WeightedAccuracy, NormMacroRecall, BalancedAccuracy,
        LogLoss, F1Binary, F1Micro, F1Macro, F1Weighted, PrecisionBinary,
        PrecisionMicro, PrecisionMacro, PrecisionWeighted, RecallBinary,
        RecallMicro, RecallMacro, RecallWeighted, AvgPrecisionBinary,
        AvgPrecisionMicro, AvgPrecisionMacro, AvgPrecisionWeighted, MatthewsCorrelation
    }

    NONSCALAR_CLASSIFICATION_SET = {
        AccuracyTable, ConfusionMatrix
    }

    CLASSIFICATION_BINARY_SET = {
        AUCBinary, F1Binary, PrecisionBinary, RecallBinary, AvgPrecisionBinary
    }

    CLASSIFICATION_SET = (SCALAR_CLASSIFICATION_SET |
                          NONSCALAR_CLASSIFICATION_SET)

    SCALAR_REGRESSION_SET = {
        ExplainedVariance, R2Score, Spearman, MAPE, MeanAbsError,
        MedianAbsError, RMSE, RMSLE, NormMeanAbsError,
        NormMedianAbsError, NormRMSE, NormRMSLE
    }

    NONSCALAR_REGRESSION_SET = {
        Residuals, PredictedTrue
    }

    REGRESSION_SET = (SCALAR_REGRESSION_SET |
                      NONSCALAR_REGRESSION_SET)

    NONSCALAR_FORECAST_SET = {
        ForecastMAPE, ForecastResiduals,
        ForecastValidateTable,
        ForecastTrainTable
    }

    FORECAST_SET = (NONSCALAR_FORECAST_SET)

    CLASSIFICATION_PRIMARY_SET = {
        Accuracy, AUCWeighted, NormMacroRecall, AvgPrecisionWeighted,
        PrecisionWeighted
    }

    CLASSIFICATION_BALANCED_SET = {
        # this is for metrics where we would recommend using class_weights
        BalancedAccuracy, AUCMacro, NormMacroRecall, AvgPrecisionMacro,
        PrecisionMacro, F1Macro, RecallMacro
    }

    REGRESSION_PRIMARY_SET = {
        Spearman, NormRMSE, R2Score, NormMeanAbsError
    }

    IMAGE_CLASSIFICATION_PRIMARY_SET = {
        Accuracy
    }

    IMAGE_CLASSIFICATION_MULTILABEL_PRIMARY_SET = {
        IOU
    }

    IMAGE_OBJECT_DETECTION_PRIMARY_SET = {
        MeanAveragePrecision,
    }

    IMAGE_OBJECT_DETECTION_SET = {
        MeanAveragePrecision,
    }

    SAMPLE_WEIGHTS_UNSUPPORTED_SET = {
        WeightedAccuracy, Spearman, MedianAbsError, NormMedianAbsError
    }

    TEXT_CLASSIFICATION_PRIMARY_SET = {
        Accuracy, AUCWeighted, PrecisionWeighted
    }

    TEXT_CLASSIFICATION_MULTILABEL_PRIMARY_SET = {
        Accuracy
    }

    TEXT_NER_PRIMARY_SET = {
        Accuracy
    }

    FULL_SET = CLASSIFICATION_SET | REGRESSION_SET | FORECAST_SET | IMAGE_OBJECT_DETECTION_SET
    NONSCALAR_FULL_SET = (NONSCALAR_CLASSIFICATION_SET |
                          NONSCALAR_REGRESSION_SET |
                          NONSCALAR_FORECAST_SET)
    SCALAR_FULL_SET = (SCALAR_CLASSIFICATION_SET |
                       SCALAR_REGRESSION_SET)
    SCALAR_FULL_SET_TIME = (SCALAR_FULL_SET | TrainingResultsType.ALL_TIME)

    # TODO: These types will be removed when the artifact-backed
    # metrics are defined with protobuf
    # Do not use these constants except in artifact-backed metrics
    SCHEMA_TYPE_ACCURACY_TABLE = 'accuracy_table'
    SCHEMA_TYPE_CONFUSION_MATRIX = 'confusion_matrix'
    SCHEMA_TYPE_RESIDUALS = 'residuals'
    SCHEMA_TYPE_PREDICTIONS = 'predictions'
    SCHEMA_TYPE_MAPE = 'mape_table'
    SCHEMA_TYPE_SMAPE = 'smape_table'

    @classmethod
    def pretty(cls, metric):
        """Verbose names for metrics."""
        return {
            cls.AUCBinary: "Binary Area Under The Curve",
            cls.AUCMacro: "Macro Area Under The Curve",
            cls.AUCMicro: "Micro Area Under The Curve",
            cls.AUCWeighted: "Weighted Area Under The Curve",
            cls.Accuracy: "Accuracy",
            cls.WeightedAccuracy: "Weighted Accuracy",
            cls.NormMacroRecall: "Normed Macro Recall",
            cls.BalancedAccuracy: "Balanced Accuracy",
            cls.LogLoss: "Log Loss",
            cls.F1Binary: "Binary F1 Score",
            cls.F1Macro: "Macro F1 Score",
            cls.F1Micro: "Micro F1 Score",
            cls.F1Weighted: "Weighted F1 Score",
            cls.PrecisionBinary: "Binary Precision",
            cls.PrecisionMacro: "Macro Precision",
            cls.PrecisionMicro: "Micro Precision",
            cls.PrecisionWeighted: "Weighted Precision",
            cls.RecallBinary: "Binary Recall",
            cls.RecallMacro: "Macro Recall",
            cls.RecallMicro: "Micro Recall",
            cls.RecallWeighted: "Weighted Recall",
            cls.AvgPrecisionBinary: "Binary Average Precision",
            cls.AvgPrecisionMacro: "Macro Average Precision",
            cls.AvgPrecisionMicro: "Micro Average Precision",
            cls.AvgPrecisionWeighted: "Weighted Average Precision",
            cls.ExplainedVariance: "Explained Variance",
            cls.R2Score: "R2 Score",
            cls.Spearman: "Spearman Correlation",
            cls.MeanAbsError: "Mean Absolute Error",
            cls.MedianAbsError: "Median Absolute Error",
            cls.RMSE: "Root Mean Squared Error",
            cls.RMSLE: "Root Mean Squared Log Error",
            cls.NormMeanAbsError: "Normalized Mean Absolute Error",
            cls.NormMedianAbsError: "Normalized Median Absolute Error",
            cls.NormRMSE: "Normalized Root Mean Squared Error",
            cls.NormRMSLE: "Normalized Root Mean Squared Log Error",
            cls.MeanAveragePrecision: "Mean Average Precision (mAP)",
        }[metric]

    CLIPS_POS = {
        # TODO: If we are no longer transforming by default reconsider these
        # it is probably not necessary for them to be over 1
        LogLoss: 1,
        NormMeanAbsError: 1,
        NormMedianAbsError: 1,
        NormRMSE: 1,
        NormRMSLE: 1,
        # current timeout value but there is a long time
        TrainingResultsType.TRAIN_TIME: 10 * 60 * 2
    }

    CLIPS_NEG = {
        # TODO: If we are no longer transforming by default reconsider these
        # it is probably not necessary for them to be over 1
        # spearman is naturally limited to this range but necessary for transform_y to work
        # otherwise spearmen is getting clipped to 0 by default
        Spearman: -1,
        ExplainedVariance: -1,
        R2Score: -1
    }


class Status:
    """Defines possible child run states."""

    NotStarted = 'Not Started'
    Started = 'Started'
    InProgress = 'In Progress'
    Completed = 'Completed'
    Terminated = 'Terminated'

    FULL_SET = {NotStarted, Started, InProgress, Completed, Terminated}

    @classmethod
    def pretty(cls, metric):
        """
        Verbose printing of AutoMLRun statuses.

        :param cls: Class of type :class: `azureml.automl.core.shared.constants.Status`
        :param metric: The metric to print.
        :type metric: azureml.automl.core.constants.Metric
        :return: Pretty print of the metric.
        :rtype: str
        """
        return {
            cls.Started: "Started",
            cls.InProgress: "In Progress running one of the child iterations.",
            cls.Completed: "Completed",
            cls.Terminated: "Terminated before finishing execution",
        }[metric]


class FitPipelineComponentName:
    """Constants for the FitPipeline Component names."""

    PREPRARE_DATA = "PrepareData"
    COMPLETE_RUN = "CompleteRun"


class PipelineParameterConstraintCheckStatus:
    """Defines values indicating whether pipeline is valid."""

    VALID = 0
    REMOVE = 1
    REJECTPIPELINE = 2


class OptimizerObjectives:
    """Defines nthe objectives an algorithm can have relative to a metric.

    Some metrics should be maximized and some should be minimized.
    """

    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"
    NA = 'NA'

    FULL_SET = {MAXIMIZE, MINIMIZE, NA}


class Optimizer:
    """Defines the categories of pipeline prediction algorithms used.

    - "random" provides a baseline by selecting a pipeline randomly
    - "lvm" uses latent variable models to predict probable next pipelines
      given performance on previous pipelines.
    """

    Random = "random"
    LVM = "lvm"

    FULL_SET = {Random, LVM}


class Tasks:
    """Defines types of machine learning tasks supported by automated ML."""

    CLASSIFICATION = 'classification'
    REGRESSION = 'regression'
    FORECASTING = 'forecasting'
    IMAGE_CLASSIFICATION = 'image-classification'
    IMAGE_CLASSIFICATION_MULTILABEL = 'image-classification-multilabel'
    IMAGE_MULTI_LABEL_CLASSIFICATION = 'image-multi-labeling'  # for temporary backward-compatibility
    IMAGE_OBJECT_DETECTION = 'image-object-detection'
    IMAGE_INSTANCE_SEGMENTATION = 'image-instance-segmentation'
    ALL_IMAGE_CLASSIFICATION = [IMAGE_CLASSIFICATION, IMAGE_CLASSIFICATION_MULTILABEL,
                                IMAGE_MULTI_LABEL_CLASSIFICATION]
    ALL_IMAGE_OBJECT_DETECTION = [IMAGE_OBJECT_DETECTION, IMAGE_INSTANCE_SEGMENTATION]
    ALL_IMAGE = [IMAGE_CLASSIFICATION, IMAGE_CLASSIFICATION_MULTILABEL, IMAGE_MULTI_LABEL_CLASSIFICATION,
                 IMAGE_OBJECT_DETECTION, IMAGE_INSTANCE_SEGMENTATION]
    TEXT_CLASSIFICATION = 'text-classification'
    TEXT_CLASSIFICATION_MULTILABEL = 'text-classification-multilabel'
    TEXT_NER = 'text-ner'
    ALL_TEXT = [TEXT_CLASSIFICATION, TEXT_CLASSIFICATION_MULTILABEL, TEXT_NER]
    ALL_DNN = ALL_IMAGE + ALL_TEXT
    ALL_MIRO = [CLASSIFICATION, REGRESSION]
    ALL = ALL_MIRO + ALL_IMAGE + ALL_TEXT


class ImageTask(Enum):
    """Available Image task types."""

    IMAGE_CLASSIFICATION = Tasks.IMAGE_CLASSIFICATION
    IMAGE_CLASSIFICATION_MULTILABEL = Tasks.IMAGE_CLASSIFICATION_MULTILABEL
    IMAGE_OBJECT_DETECTION = Tasks.IMAGE_OBJECT_DETECTION
    IMAGE_INSTANCE_SEGMENTATION = Tasks.IMAGE_INSTANCE_SEGMENTATION


class ClientErrors:
    """Defines client errors that can occur when violating user-specified cost constraints."""

    EXCEEDED_TIME_CPU = "CPU time exceeded the specified limit. Please consider increasing the CPU time limit."
    EXCEEDED_TIME = "Wall clock time exceeded the specified limit. Please consider increasing the time limit."
    EXCEEDED_ITERATION_TIMEOUT_MINUTES = "Iteration timeout reached, skipping the iteration. " \
                                         "Please consider increasing iteration_timeout_minutes."
    EXCEEDED_EXPERIMENT_TIMEOUT_MINUTES = "Experiment timeout reached, skipping the iteration. " \
                                          "Please consider increasing experiment_timeout_minutes."
    EXCEEDED_MEMORY = "Memory usage exceeded the specified limit or was killed by the OS due to low memory " \
                      "conditions. Please consider increasing available memory."
    SUBPROCESS_ERROR = "The subprocess was killed due to an error."
    GENERIC_ERROR = "An unknown error occurred."

    ALL_ERRORS = {
        EXCEEDED_TIME_CPU, EXCEEDED_TIME, EXCEEDED_ITERATION_TIMEOUT_MINUTES, EXCEEDED_EXPERIMENT_TIMEOUT_MINUTES,
        EXCEEDED_MEMORY, SUBPROCESS_ERROR, GENERIC_ERROR
    }
    TIME_ERRORS = {
        EXCEEDED_TIME_CPU, EXCEEDED_TIME, EXCEEDED_ITERATION_TIMEOUT_MINUTES, EXCEEDED_EXPERIMENT_TIMEOUT_MINUTES
    }


class ServerStatus:
    """Defines server status values."""

    OK = 'ok'
    INCREASE_TIME_THRESHOLD = 'threshold'


class TimeConstraintEnforcement:
    """Enumeration of time contraint enforcement modes."""

    TIME_CONSTRAINT_NONE = 0
    TIME_CONSTRAINT_PER_ITERATION = 1
    TIME_CONSTRAINT_TOTAL = 2
    TIME_CONSTRAINT_TOTAL_AND_ITERATION = 3


class PipelineCost:
    """Defines cost model modes.

    - COST_NONE returns all predicted pipelines
    - COST_FILTER returns only pipelines that were predicted by cost models
      to meet the user-specified cost conditions
    - COST_SCALE divides the acquisition function score by the predicted time
    """

    COST_NONE = 0
    COST_FILTER = 1
    COST_SCALE_ACQUISITION = 2  # no filtering, so not great
    COST_SCALE_AND_FILTER = 3  # a little too greedy
    COST_SCALE_THEN_FILTER = 4  # annealing accomplishes the same thing more smoothly
    COST_ALTERNATE = 5  # switch between annealing and filtering, useful for debugging
    COST_SCALE_AND_FILTER_ANNEAL = 6  # scale acq_fn score by time but reduce impact of time
    # as the run is closer to completion because otherwise we also pick fast models
    COST_PROBABILITY = 7  # use a probability to filter out models
    COST_PROBABILITY_SAMPLE = 8  # sample models with probability
    # equal to the chance the model runs without timing out
    COST_MODEL_ALL_ANNEALING = {COST_SCALE_AND_FILTER_ANNEAL,
                                COST_PROBABILITY,
                                COST_PROBABILITY_SAMPLE}
    COST_MODEL_ALL_SCALE = COST_MODEL_ALL_ANNEALING | {COST_SCALE_ACQUISITION,
                                                       COST_SCALE_AND_FILTER,
                                                       COST_SCALE_THEN_FILTER,
                                                       COST_ALTERNATE}
    # TODO: Add a mode that looks at setting timeout to a percentile of the good models
    # because we dont want to restrict to only fast models if we need the expensive models
    # Used to restrict the number of piplines we predict cost for if we want to save time
    # currently set to the same values as the pruned index so no optimization is made
    MAX_COST_PREDICTS = 20000


class IterationTimeout:
    """Defines ways of changing the per_iteration_timeout."""

    TIMEOUT_NONE = 0
    TIMEOUT_SUGGEST_TIMEOUT = 1  # suggest timeout based on problem_info
    TIMEOUT_BEST_TIME = 2  # increase the timeout based on a factor of the best model seen so far
    TIMEOUT_DOUBLING = 3  # start with a low timeout and double it as time goes on
    TIMEOUT_PERCENTILE = 4  # set time to percentile of all models
    TIMEOUT_BEST_TIME_SUGGEST = 5  # TIMEOUT_BEST_TIME + TIMEOUT_SUGGEST_TIMEOUT
    TIMEOUT_DOUBLING_SUGGEST = 6  # TIMEOUT_DOUBLING + TIMEOUT_SUGGEST_TIMEOUT
    TIMEOUT_PERCENTILE_SUGGEST = 7  # TIMEOUT_DOUBLING + TIMEOUT_SUGGEST_TIMEOUT
    TIMEOUT_ALL_SUGGEST = {TIMEOUT_SUGGEST_TIMEOUT, TIMEOUT_BEST_TIME_SUGGEST,
                           TIMEOUT_DOUBLING_SUGGEST, TIMEOUT_PERCENTILE_SUGGEST}


class PipelineMaskProfiles:
    """Defines mask profiles for pipelines."""

    MASK_NONE = 'none'
    MASK_PARTIAL_FIT = 'partial_fit'
    MASK_LGBM_ONLY = 'lgbm'
    MASK_MANY_FEATURES = 'many_features'
    MASK_SPARSE = 'sparse'
    MASK_PRUNE = 'prune'
    MASK_TIME_PRUNE = 'time_prune'
    MASK_RANGE = 'range_mask'
    MASK_INDEX = 'pruned_index_name'

    ALL_MASKS = [
        MASK_NONE,
        MASK_PARTIAL_FIT, MASK_MANY_FEATURES,
        MASK_SPARSE,
        MASK_RANGE]


class SubsamplingTreatment:
    """Defines subsampling treatment in GP."""

    LOG = 'log'
    LINEAR = 'linear'


class SubsamplingSchedule:
    """Defines subsampling strategies."""

    HYPERBAND = 'hyperband'
    HYPERBAND_CLIP = 'hyperband_clip'
    FULL_PCT = 100.0


class EnsembleMethod:
    """Defines ensemble methods."""

    ENSEMBLE_AVERAGE = 'average'
    ENSEMBLE_STACK = 'stack_lr'
    # take the best model from each class, This is what H20 does
    ENSEMBLE_BEST_MODEL = 'best_model'
    # stack, but with a lgbm not a logistic regression
    ENSEMBLE_STACK_LGBM = 'stack_lgbm'
    # take the best model from each cluster of the model's latent space
    ENSEMBLE_LATENT_SPACE = 'latent_space'
    # take the best model from each of the datasets classes
    ENSEMBLE_BEST_CLASS = 'best_class'


class MetricObjective:
    """Defines mappings from metrics to their objective.

    Objectives are maximization or minimization (regression and
    classification).
    """

    Classification = {
        Metric.AUCBinary: OptimizerObjectives.MAXIMIZE,
        Metric.AUCMicro: OptimizerObjectives.MAXIMIZE,
        Metric.AUCMacro: OptimizerObjectives.MAXIMIZE,
        Metric.AUCWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.Accuracy: OptimizerObjectives.MAXIMIZE,
        Metric.WeightedAccuracy: OptimizerObjectives.MAXIMIZE,
        Metric.NormMacroRecall: OptimizerObjectives.MAXIMIZE,
        Metric.BalancedAccuracy: OptimizerObjectives.MAXIMIZE,
        Metric.LogLoss: OptimizerObjectives.MINIMIZE,
        Metric.F1Binary: OptimizerObjectives.MAXIMIZE,
        Metric.F1Micro: OptimizerObjectives.MAXIMIZE,
        Metric.F1Macro: OptimizerObjectives.MAXIMIZE,
        Metric.F1Weighted: OptimizerObjectives.MAXIMIZE,
        Metric.PrecisionBinary: OptimizerObjectives.MAXIMIZE,
        Metric.PrecisionMacro: OptimizerObjectives.MAXIMIZE,
        Metric.PrecisionMicro: OptimizerObjectives.MAXIMIZE,
        Metric.PrecisionWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.RecallBinary: OptimizerObjectives.MAXIMIZE,
        Metric.RecallMacro: OptimizerObjectives.MAXIMIZE,
        Metric.RecallMicro: OptimizerObjectives.MAXIMIZE,
        Metric.RecallWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.AvgPrecisionBinary: OptimizerObjectives.MAXIMIZE,
        Metric.AvgPrecisionMacro: OptimizerObjectives.MAXIMIZE,
        Metric.AvgPrecisionMicro: OptimizerObjectives.MAXIMIZE,
        Metric.AvgPrecisionWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.MatthewsCorrelation: OptimizerObjectives.MAXIMIZE,
        Metric.AccuracyTable: OptimizerObjectives.NA,
        Metric.ConfusionMatrix: OptimizerObjectives.NA,
        TrainingResultsType.TRAIN_TIME: OptimizerObjectives.MINIMIZE
    }

    Regression = {
        Metric.ExplainedVariance: OptimizerObjectives.MAXIMIZE,
        Metric.R2Score: OptimizerObjectives.MAXIMIZE,
        Metric.Spearman: OptimizerObjectives.MAXIMIZE,
        Metric.MeanAbsError: OptimizerObjectives.MINIMIZE,
        Metric.NormMeanAbsError: OptimizerObjectives.MINIMIZE,
        Metric.MedianAbsError: OptimizerObjectives.MINIMIZE,
        Metric.NormMedianAbsError: OptimizerObjectives.MINIMIZE,
        Metric.RMSE: OptimizerObjectives.MINIMIZE,
        Metric.NormRMSE: OptimizerObjectives.MINIMIZE,
        Metric.RMSLE: OptimizerObjectives.MINIMIZE,
        Metric.NormRMSLE: OptimizerObjectives.MINIMIZE,
        Metric.MAPE: OptimizerObjectives.MINIMIZE,
        Metric.SMAPE: OptimizerObjectives.MINIMIZE,
        Metric.Residuals: OptimizerObjectives.NA,
        Metric.PredictedTrue: OptimizerObjectives.NA,
        TrainingResultsType.TRAIN_TIME: OptimizerObjectives.MINIMIZE
    }

    Forecast = {
        Metric.ForecastResiduals: OptimizerObjectives.NA,
        Metric.ForecastMAPE: OptimizerObjectives.NA,
        Metric.ForecastSMAPE: OptimizerObjectives.NA,
        Metric.ForecastValidateTable: OptimizerObjectives.NA,
        Metric.ForecastTrainTable: OptimizerObjectives.NA
    }

    ImageClassification = {
        Metric.Accuracy: OptimizerObjectives.MAXIMIZE,
    }

    ImageClassificationMultiLabel = {
        Metric.IOU: OptimizerObjectives.MAXIMIZE,
    }

    ImageObjectDetection = {
        Metric.MeanAveragePrecision: OptimizerObjectives.MAXIMIZE,
    }

    TextClassification = {
        Metric.Accuracy: OptimizerObjectives.MAXIMIZE,
        Metric.AUCWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.PrecisionWeighted: OptimizerObjectives.MAXIMIZE,
    }

    TextClassificationMultilabel = {
        Metric.Accuracy: OptimizerObjectives.MAXIMIZE,
    }

    TextNer = {
        Metric.Accuracy: OptimizerObjectives.MAXIMIZE,
    }


class ModelParameters:
    """
    Defines parameter names specific to certain models.

    For example, to indicate which features in the dataset are categorical
    a LightGBM model accepts the 'categorical_feature' parameter while
    a CatBoost model accepts the 'cat_features' parameter.
    """

    CATEGORICAL_FEATURES = {
        ModelClassNames.ClassificationModelClassNames.LightGBMClassifier: 'categorical_feature',
        ModelClassNames.RegressionModelClassNames.LightGBMRegressor: 'categorical_feature',
        ModelClassNames.ClassificationModelClassNames.CatBoostClassifier: 'cat_features',
        ModelClassNames.RegressionModelClassNames.CatBoostRegressor: 'cat_features',
        ModelClassNames.ClassificationModelClassNames.TabNetClassifier: 'categorical_features',
        ModelClassNames.RegressionModelClassNames.TabNetRegressor: 'categorical_features'
    }


class SupportedCategoricals:
    """
    Defines supported categoricals learnersin _set_dataset_categoricals type :
    """
    CATEGORICAL_LEARNERS = [
        ModelClassNames.ClassificationModelClassNames.TabNetClassifier,
        ModelClassNames.RegressionModelClassNames.TabNetRegressor
    ]


class TrainingType:
    """Defines validation methods.

    Different experiment types will use different validation methods.
    """

    # Yields TRAIN_FROM_FULL_METRICS and TEST_FROM_FULL_METRICS
    TrainFull = 'train_full'
    # Yields VALIDATION_METRICS
    TrainAndValidation = 'train_valid'
    # Yields TRAIN_METRICS, VALIDATION_METRICS, and TEST_METRICS
    TrainValidateTest = 'train_valid_test'
    # Yields CV_METRICS and CV_MEAN_METRICS
    # NOTE: CrossValidation is a legacy key that should not be used anymore.
    # MeanCrossValidation should be used instead.
    CrossValidation = 'CV'
    MeanCrossValidation = 'MeanCrossValidation'
    FULL_SET = {
        TrainFull,
        TrainAndValidation,
        TrainValidateTest,
        CrossValidation,
        MeanCrossValidation}

    @classmethod
    def pretty(cls, metric):
        """Verbose names for training types."""
        return {
            cls.TrainFull: "Full",
            cls.TrainAndValidation: "Train and Validation",
            cls.CrossValidation: "Cross Validation",
            cls.MeanCrossValidation: "Mean of the Cross Validation",
        }[metric]


class NumericalDtype:
    """Defines supported numerical datatypes.

    Names correspond to the output of pandas.api.types.infer_dtype().
    """

    Integer = 'integer'
    Floating = 'floating'
    MixedIntegerFloat = 'mixed-integer-float'
    Decimal = 'decimal'
    Empty = 'empty'

    FULL_SET = {Integer, Floating, MixedIntegerFloat, Decimal, Empty}
    CONVERTIBLE = {Integer, Floating, MixedIntegerFloat, Decimal}


class DatetimeDtype:
    """Defines supported datetime datatypes.

    Names correspond to the output of pandas.api.types.infer_dtype().
    """

    Date = 'date'
    Datetime = 'datetime'
    Datetime64 = 'datetime64'

    FULL_SET = {Date, Datetime, Datetime64}


class TextOrCategoricalDtype:
    """Defines supported categorical datatypes."""

    String = 'string'
    Categorical = 'categorical'

    FULL_SET = {String, Categorical}


class TimeSeries:
    """Defines parameters used for timeseries."""

    AUTO = 'auto'
    COUNTRY = 'country'
    COUNTRY_OR_REGION = 'country_or_region'
    COUNTRY_OR_REGION_FOR_HOLIDAYS = 'country_or_region_for_holidays'
    CV_STEP_SIZE = 'cv_step_size'
    DROP_COLUMN_NAMES = 'drop_column_names'
    FEATURE_LAGS = 'feature_lags'
    FORECASTING_PARAMETERS = 'forecasting_parameters'
    FORECAST_HORIZON = 'forecast_horizon'
    FREQUENCY = 'freq'
    GRAIN_COLUMN_NAMES = 'grain_column_names'

    GROUP_COLUMN = 'group'
    GROUP_COLUMN_NAMES = 'group_column_names'
    HOLIDAY_COUNTRY = 'holiday_country'
    MAX_CORES_PER_ITERATION = 'max_cores_per_iteration'
    ITERATION_TIMEOUT_MINUTES = 'iteration_timeout_minutes'
    MAX_HORIZON = 'max_horizon'
    SEASONALITY = 'seasonality'
    SERIES_COLUMN_COUNT = 'series_column_count'
    SERIES_COUNT = 'series_count'
    SERIES_LEN_AVG = 'series_len_avg'
    SERIES_LEN_MIN = 'series_len_min'
    SERIES_LEN_MAX = 'series_len_max'
    SERIES_LEN_PERC_25 = 'series_len_perc_25'
    SERIES_LEN_PERC_50 = 'series_len_perc_50'
    SERIES_LEN_PERC_75 = 'series_len_perc_75'
    SHORT_SERIES_HANDLING = 'short_series_handling'
    SHORT_SERIES_HANDLING_CONFIG = 'short_series_handling_configuration'
    STL_OPTION_SEASON = 'season'
    STL_OPTION_SEASON_TREND = 'season_trend'
    TARGET_LAGS = 'target_lags'
    TARGET_ROLLING_WINDOW_SIZE = 'target_rolling_window_size'
    TIME_COLUMN_NAME = 'time_column_name'
    TIME_SERIES_ID_COLUMN_NAMES = 'time_series_id_column_names'
    USE_STL = 'use_stl'
    TARGET_AGG_FUN = 'target_aggregation_function'
    ALL_FORECASTING_PARAMETERS = {
        TIME_COLUMN_NAME, GRAIN_COLUMN_NAMES, TIME_SERIES_ID_COLUMN_NAMES, GROUP_COLUMN_NAMES, TARGET_LAGS,
        FEATURE_LAGS, TARGET_ROLLING_WINDOW_SIZE, MAX_HORIZON, FORECAST_HORIZON, COUNTRY_OR_REGION, HOLIDAY_COUNTRY,
        SEASONALITY, USE_STL, SHORT_SERIES_HANDLING, DROP_COLUMN_NAMES, COUNTRY, FREQUENCY,
        COUNTRY_OR_REGION_FOR_HOLIDAYS, SHORT_SERIES_HANDLING_CONFIG, CV_STEP_SIZE
    }


class ShortSeriesHandlingValues:
    """Define the possible values of ShortSeriesHandling config."""

    SHORT_SERIES_HANDLING_AUTO = TimeSeries.AUTO
    SHORT_SERIES_HANDLING_PAD = 'pad'
    SHORT_SERIES_HANDLING_DROP = 'drop'

    ALL = [SHORT_SERIES_HANDLING_AUTO, SHORT_SERIES_HANDLING_PAD, SHORT_SERIES_HANDLING_DROP]


class AggregationFunctions:
    """Define the aggregation functions for numeric columns."""

    SUM = 'sum'
    MAX = 'max'
    MIN = 'min'
    MEAN = 'mean'

    DATETIME = [MAX, MIN]
    ALL = [SUM, MAX, MIN, MEAN]


class TimeSeriesInternal:
    """Defines non user-facing TimeSeries constants."""

    ARIMA_TRIGGER_CSS_TRAINING_LENGTH = 101
    ARIMAX_RAW_COLUMNS = 'arimax_raw_columns'
    CROSS_VALIDATIONS = 'n_cross_validations'
    CV_STEP_SIZE_DEFAULT = None
    DROP_IRRELEVANT_COLUMNS = 'drop_irrelevant_columns'
    DROP_NA = 'dropna'  # dropna parameter of LagLeadOperator and RollingWindow. Currently set to DROP_NA_DEFAULT.
    DROP_NA_DEFAULT = False
    DUMMY_GRAIN_COLUMN = '_automl_dummy_grain_col'
    MAX_TIME_SERIES_ID_COLUMN_NUMBER = 10
    DUMMY_GROUP_COLUMN = '_automl_dummy_group_col'
    DUMMY_ORDER_COLUMN = '_automl_original_order_col'
    DUMMY_PREDICT_COLUMN = '_automl_predict_col'
    DUMMY_TARGET_COLUMN = '_automl_target_col'
    FEATURE_LAGS_DEFAULT = None
    FORCE_TIME_INDEX_FEATURES_DEFAULT = None
    FORCE_TIME_INDEX_FEATURES_NAME = 'force_time_index_features'
    FREQUENCY_DEFAULT = None
    GRANGER_CRITICAL_PVAL = 0.05
    GRANGER_DEFAULT_TEST = 'ssr_ftest'
    # The column name reserved for holiday feature
    HOLIDAY_COLUMN_NAME = '_automl_Holiday'
    HOLIDAY_COLUMN_NAME_DEPRECATED = '_Holiday'
    HORIZON_NAME = 'horizon_origin'
    IMPUTE_NA_NUMERIC_DATETIME = 'impute_na_numeric_datetime'
    LAGGING_COLUMNS = 'lagging_columns'  # The features generated from LAG_LEAD_OPERATOR
    LAGS_TO_CONSTRUCT = 'lags'  # The internal lags dictionary
    LAG_LEAD_OPERATOR = 'lag_lead_operator'
    MAKE_CATEGORICALS_NUMERIC = 'make_categoricals_numeric'
    MAKE_CATEGORICALS_ONEHOT = 'make_categoricals_onehot'
    MAKE_DATETIME_COLUMN_FEATURES = 'make_datetime_column_features'
    MAKE_GRAIN_FEATURES = 'make_grain_features'
    MAKE_NUMERIC_NA_DUMMIES = 'make_numeric_na_dummies'
    MAKE_SEASONALITY_AND_TREND = 'make_seasonality_and_trend'
    MAKE_TIME_INDEX_FEATURES = 'make_time_index_featuers'
    MAX_HORIZON_DEFAULT = 1
    MAX_HORIZON_FEATURIZER = 'max_horizon_featurizer'
    # The amount of memory occupied by perspective data frame
    # at which we decide to switch off lag leads and rolling windows.
    MEMORY_FRACTION_FOR_DF = 0.7
    ORIGIN_TIME_COLNAME = 'origin_time_column_name'
    ORIGIN_TIME_COLNAME_DEFAULT = 'origin'
    ORIGIN_TIME_COLUMN_NAME = 'origin_time_colname'
    ORIGIN_TIME_OCCURRENCE_COLUMN_NAME = '_automl_origin_by_occurrence'
    # overwrite_columns parameter of LagLeadOperator and RollingWindow. Currently set to OVERWRITE_COLUMNS_DEFAULT.
    OVERWRITE_COLUMNS = 'overwrite_columns'
    OVERWRITE_COLUMNS_DEFAULT = True
    PAID_TIMEOFF_COLUMN_NAME = '_automl_IsPaidTimeOff'
    PAID_TIMEOFF_COLUMN_NAME_DEPRECATED = '_IsPaidTimeOff'
    PERTURBATION_NOISE_CV = 1e-6
    PREFIX_FOR_GRAIN_FEATURIZATION = 'grain'
    PREFIX_SEPERATOR_FOR_GRAIN_FEATURIZATION = '_'
    PROPHET_PARAM_DICT = 'prophet_param_dict'
    RESTORE_DTYPES = 'restore_dtypes_transform'
    ROLLING_WINDOW_OPERATOR = 'rolling_window_operator'
    ROW_IMPUTED_COLUMN_NAME = '_automl_row_imputed'
    RUN_MAX_HORIZON = 'forecasting_max_horizon'
    RUN_TARGET_LAGS = 'forecasting_target_lags'
    RUN_WINDOW_SIZE = 'forecasting_target_rolling_window_size'
    RUN_FREQUENCY = 'forecasting_freq'
    ROLLING_WINDOW_COLUMNS = 'rolling_window_columns'  # The features generated from ROLLING_WINDOW_OPERATOR.
    SEASONALITY_VALUE_DETECT = TimeSeries.AUTO
    SEASONALITY_VALUE_DEFAULT = SEASONALITY_VALUE_DETECT
    SEASONALITY_VALUE_NONSEASONAL = 1
    SHORT_SERIES_DROPPEER = "grain_dropper"
    SHORT_SERIES_HANDLING_DEFAULT = True
    STL_SEASON_SUFFIX = '_season'
    STL_TREND_SUFFIX = '_trend'
    TARGET_LAGS_DEFAULT = None
    TIMESERIES_PARAM_DICT = 'timeseries_param_dict'
    # The rolling window transform dictionary, currently not publicly available.
    TRANSFORM_DICT = 'transform_dictionary'
    TRANSFORM_OPTS = 'transform_options'  # The options for rolling window transform.
    USE_STL_DEFAULT = None
    WINDOW_OPTS = 'window_options'  # The internal window options (Currently is not used).
    WINDOW_SIZE = 'window_size'  # The internal window_size variable
    WINDOW_SIZE_DEFDAULT = None
    WINDOW_SIZE_DEFAULT = WINDOW_SIZE_DEFDAULT

    RESERVED_COLUMN_NAMES = {DUMMY_GROUP_COLUMN,
                             DUMMY_ORDER_COLUMN,
                             DUMMY_GRAIN_COLUMN,
                             DUMMY_TARGET_COLUMN}
    SEASONALITY_VALUE_DEFAULT = SEASONALITY_VALUE_DETECT
    STL_VALID_OPTIONS = {TimeSeries.STL_OPTION_SEASON_TREND,
                         TimeSeries.STL_OPTION_SEASON}
    TRANSFORM_DICT_DEFAULT = {'min': DUMMY_TARGET_COLUMN,
                              'max': DUMMY_TARGET_COLUMN,
                              'mean': DUMMY_TARGET_COLUMN}
    SHORT_SERIES_HANDLING_CONFIG_DEFAULT = ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_AUTO

    # Features derived from the time index
    TIME_INDEX_FEATURE_ID_YEAR = 0
    TIME_INDEX_FEATURE_ID_YEAR_ISO = 1
    TIME_INDEX_FEATURE_ID_HALF = 2
    TIME_INDEX_FEATURE_ID_QUARTER = 3
    TIME_INDEX_FEATURE_ID_MONTH = 4
    TIME_INDEX_FEATURE_ID_MONTH_LBL = 5
    TIME_INDEX_FEATURE_ID_DAY = 6
    TIME_INDEX_FEATURE_ID_HOUR = 7
    TIME_INDEX_FEATURE_ID_MINUTE = 8
    TIME_INDEX_FEATURE_ID_SECOND = 9
    TIME_INDEX_FEATURE_ID_AM_PM = 10
    TIME_INDEX_FEATURE_ID_AM_PM_LBL = 11
    TIME_INDEX_FEATURE_ID_HOUR12 = 12
    TIME_INDEX_FEATURE_ID_WDAY = 13
    TIME_INDEX_FEATURE_ID_WDAY_LBL = 14
    TIME_INDEX_FEATURE_ID_QDAY = 15
    TIME_INDEX_FEATURE_ID_YDAY = 16
    TIME_INDEX_FEATURE_ID_WEEK = 17

    TIME_INDEX_FEATURE_IDS = [TIME_INDEX_FEATURE_ID_YEAR, TIME_INDEX_FEATURE_ID_YEAR_ISO,
                              TIME_INDEX_FEATURE_ID_HALF, TIME_INDEX_FEATURE_ID_QUARTER,
                              TIME_INDEX_FEATURE_ID_MONTH, TIME_INDEX_FEATURE_ID_MONTH_LBL,
                              TIME_INDEX_FEATURE_ID_DAY, TIME_INDEX_FEATURE_ID_HOUR,
                              TIME_INDEX_FEATURE_ID_MINUTE, TIME_INDEX_FEATURE_ID_SECOND,
                              TIME_INDEX_FEATURE_ID_AM_PM, TIME_INDEX_FEATURE_ID_AM_PM_LBL,
                              TIME_INDEX_FEATURE_ID_HOUR12, TIME_INDEX_FEATURE_ID_WDAY,
                              TIME_INDEX_FEATURE_ID_WDAY_LBL, TIME_INDEX_FEATURE_ID_QDAY,
                              TIME_INDEX_FEATURE_ID_YDAY, TIME_INDEX_FEATURE_ID_WEEK]

    TIME_INDEX_FEATURE_NAMES_DEPRECATED = ['year', 'year_iso', 'half', 'quarter', 'month',
                                           'month_lbl', 'day', 'hour', 'minute', 'second',
                                           'am_pm', 'am_pm_lbl', 'hour12', 'wday',
                                           'wday_lbl', 'qday', 'yday', 'week']
    TIME_INDEX_FEATURE_NAMES = ['_automl_year', '_automl_year_iso', '_automl_half', '_automl_quarter',
                                '_automl_month', '_automl_month_lbl', '_automl_day', '_automl_hour',
                                '_automl_minute', '_automl_second', '_automl_am_pm', '_automl_am_pm_lbl',
                                '_automl_hour12', '_automl_wday', '_automl_wday_lbl', '_automl_qday',
                                '_automl_yday', '_automl_week']
    TIME_INDEX_FEATURE_NAME_MAP_DEPRECATED = \
        OrderedDict(zip(TIME_INDEX_FEATURE_IDS, TIME_INDEX_FEATURE_NAMES_DEPRECATED))
    TIME_INDEX_FEATURE_NAME_MAP = OrderedDict(zip(TIME_INDEX_FEATURE_IDS, TIME_INDEX_FEATURE_NAMES))
    TARGET_AGG_FUN_DEFAULT = None
    USER_FRIENDLY_DEFAULT_GRAIN = 'default'
    FORECASTER_ESTIMATOR_TYPE = 'regressor'


class TimeSeriesWebLinks:
    """Define the web links for the time series documentation."""

    PANDAS_DO_URL = 'https://pandas.pydata.org/pandas-docs/stable/timeseries.html#dateoffset-objects'
    FORECAST_PARAM_DOCS = 'https://docs.microsoft.com/en-us/python/api/azureml-automl-core/' \
                          'azureml.automl.core.forecasting_parameters.forecastingparameters' \
                          '?view=azure-ml-py'
    FORECAST_CONFIG_DOC = 'https://docs.microsoft.com/azure/machine-learning/' \
                          'how-to-auto-train-forecast#configuration-settings'


class Subtasks:
    """Defines names of the subtasks."""

    FORECASTING = 'forecasting'

    ALL = [FORECASTING]


class Transformers:
    """Defines transformers used for data processing."""

    X_TRANSFORMER = 'datatransformer'
    Y_TRANSFORMER = 'y_transformer'

    TIMESERIES_TRANSFORMER = 'timeseriestransformer'

    ALL = [X_TRANSFORMER, Y_TRANSFORMER, TIMESERIES_TRANSFORMER]


class LearnerColumns:
    """Defines all columns used for learner pipeline."""
    DefaultLearners = 'DefaultLearners'
    CatIndicatorLearners = 'CatIndicatorLearners'


class TelemetryConstants:
    """Defines telemetry constants."""
    COMPONENT_NAME = "automl"

    # Spans that are shared across different child run types
    # Formatting for span name: <Component_Name>.<Span_Name> e.g. automl.Training
    SPAN_FORMATTING = "{}.{}"
    # RunInitialization: Initialize common variables across remote wrappers
    RUN_INITIALIZATION = "RunInitialization"
    RUN_INITIALIZATION_USER_FACING = "Initializing AutoML run"
    # DataFetch: Setup and Featurization data fetching
    DATA_PREPARATION = "DataPrep"
    DATA_PREPARATION_USER_FACING = "Preparing input data"
    # LoadCachedData: Training and Model Explain load data from cache
    LOAD_CACHED_DATA = "LoadCachedData"
    LOAD_CACHED_DATA_USER_FACING = "Loading cached data"

    # Spans specific to Setup Run
    FEATURIZATION_STRATEGY = "FeaturizationStrategy"
    FEATURIZATION_STRATEGY_USER_FACING = "Deciding featurization actions"
    DATA_VALIDATION = "DataValidation"
    DATA_VALIDATION_USER_FACING = "Validating input data"

    # Spans specific to Featurization
    FEATURIZATION = "Featurization"
    FEATURIZATION_USER_FACING = "Featurizing data"

    # Spans specific to Training
    LOAD_ONNX_CONVERTER = "LoadOnnxConverter"
    LOAD_ONNX_CONVERTER_USER_FACING = "Loading ONNX converter"
    RUN_TRAINING = "RunE2ETraining"
    RUN_TRAINING_USER_FACING = "Running E2E training"
    TRAINING = "Training"
    TRAINING_USER_FACING = "Training model"
    VALIDATION = "Validation"
    VALIDATION_USER_FACING = "Validating model quality"
    METRIC_AND_SAVE_MODEL_NAME = "SaveModelArtifacts"
    METRIC_AND_SAVE_MODEL_USER_FACING = "Uploading run output metadata"
    ONNX_CONVERSION = "OnnxConversion"
    ONNX_CONVERSION_USER_FACING = "Converting to ONNX model"
    LOG_METRICS = "LogMetrics"
    LOG_METRICS_USER_FACING = "Logging run metrics"

    # Spans specific to Training
    BATCH_TRAINING = "BatchTraining"
    BATCH_TRAINING_USER_FACING = "Training model in batch"

    # Spans specific to Model Explain
    MODEL_EXPLANATION = "ModelExplanation"
    MODEL_EXPLANATION_USER_FACING = "Running model explainability"

    # Local Managed
    ScriptRunFinalizing = "ScriptRunFinalizing"
    ScriptRunStarting = "ScriptRunStarting"

    # Spans specific to Confidence Interval
    COMPUTE_CONFIDENCE_METRICS = "ComputeConfidenceMetrics"
    BOOTSTRAP_STEPS = "BootstrapSteps"

    # TODO: refactor / organize below and use compatible telemetry constants for activity logger and RH tracing
    COMPUTE_METRICS_NAME = 'ComputeMetrics'
    DOWNLOAD_ENSEMBLING_MODELS = 'DownloadEnsemblingModels'
    DOWNLOAD_MODEL = 'DownloadModel'
    FAILURE = 'Failure'
    FIT_ITERATION_NAME = 'FitIteration'
    GET_BEST_CHILD = 'GetBestChild'
    GET_CHILDREN = 'GetChildren'
    GET_OUTPUT = 'GetOutput'
    GET_PIPELINE_NAME = 'GetPipeline'
    OUTPUT_NAME = 'Output'
    PACKAGES_CHECK = 'PackagesCheck'
    PRE_PROCESS_NAME = 'PreProcess'
    PREDICT_NAME = 'Predict'
    REGISTER_MODEL = 'RegisterModel'
    REMOTE_INFERENCE = 'RemoteInference'
    RUN_CV_MEAN_NAME = 'RunCVMean'
    RUN_CV_NAME = 'RunCV'
    RUN_ENSEMBLING_NAME = 'RunEnsembling'
    RUN_NAME = 'Run'
    RUN_PIPELINE_NAME = 'RunPipeline'
    RUN_TRAIN_FULL_NAME = 'TrainFull'
    RUN_TRAIN_VALID_NAME = 'TrainValid'
    SUCCESS = 'Success'
    TIME_FIT_ENSEMBLE_NAME = 'TimeFitEnsemble'
    TIME_FIT_INPUT = 'TimeFitInput'
    TIME_FIT_NAME = 'TimeFit'


def get_metric_from_type(t):
    """Get valid metrics for a given training type."""
    return {
        TrainingType.TrainFull: TrainingResultsType.TEST_FROM_FULL_METRICS,
        TrainingType.TrainAndValidation: (
            TrainingResultsType.VALIDATION_METRICS),
        TrainingType.TrainValidateTest: (
            TrainingResultsType.VALIDATION_METRICS),
        TrainingType.MeanCrossValidation: TrainingResultsType.CV_MEAN_METRICS
    }[t]


def get_status_from_type(t):
    """Get valid training statuses for a given training type."""
    return {
        TrainingType.TrainFull: TrainingResultsType.TRAIN_FULL_STATUS,
        TrainingType.TrainAndValidation: (
            TrainingResultsType.TRAIN_VALIDATE_STATUS),
        TrainingType.TrainValidateTest: (
            TrainingResultsType.TRAIN_VALIDATE_STATUS),
        TrainingType.MeanCrossValidation: TrainingResultsType.CV_MEAN_METRICS
    }[t]


class ValidationLimitRule:
    """Defines validation rules."""

    def __init__(
        self,
        lower_bound: int,
        upper_bound: int,
        number_of_cv: int
    ):
        """Init the rule based on the inputs."""
        self.LOWER_BOUND = lower_bound
        self.UPPER_BOUND = upper_bound
        self.NUMBER_OF_CV = number_of_cv


class RuleBasedValidation:
    """Defines constants for the rule-based validation setting."""

    # Autofeaturization iteration count to skip validation split
    AUTOFEATURIZATION_ITERATION_COUNT = 0
    # Default CV number
    DEFAULT_N_CROSS_VALIDATIONS = 1  # is basically using train-validation split
    # Default train validate ratio
    DEFAULT_TRAIN_VALIDATE_TEST_SIZE = 0.1
    # Default train validate seed
    DEFAULT_TRAIN_VALIDATE_RANDOM_STATE = 42

    VALIDATION_LIMITS_NO_SPARSE = [
        ValidationLimitRule(0, 1000, 10),
        ValidationLimitRule(1000, 20000, 3),
        ValidationLimitRule(20000, sys.maxsize, 1)
    ]

    SPARSE_N_CROSS_VALIDATIONS = 1  # sparse is basically using train-validation split

    UNIQUE_CLASS_SUBSTR = "y has only 1 member"
    TARGET_TYPE_INCONSISTENCY_SUBSTR = "'<' not supported"


# Hashing seed value for murmurhash
hashing_seed_value = 314489979

# Default app_name in custom dimensions of the logs.
DEFAULT_LOGGING_APP_NAME = "AutoML"
LOW_MEMORY_THRESHOLD = 0.5


class FeatureSweeping:
    """Defines constants for Feature Sweeping."""
    pass


class AutoMLJson:
    """Defines constants for JSON created by automated ML."""

    SCHEMA_TYPE_FAULT_VERIFIER = 'fault_verifier'


class AutoMLValidation:
    TIMEOUT_DATA_BOUND = 10000000


class CheckImbalance:
    """
    If the ratio of the samples in the minority class to the samples in the majority class
    is equal to or lower than this threshold, then Imbalance will be detected in the dataset.
    """
    MINORITY_TO_MAJORITY_THRESHOLD_RATIO = 0.2


class SupportedInputDatatypes:
    """Input data types supported by AutoML for different Run types."""

    PANDAS = "pandas.DataFrame"
    TABULAR_DATASET = "azureml.data.tabular_dataset.TabularDataset"
    PIPELINE_OUTPUT_TABULAR_DATASET = "azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset"

    LOCAL_RUN_SCENARIO = [PANDAS, TABULAR_DATASET, PIPELINE_OUTPUT_TABULAR_DATASET]
    REMOTE_RUN_SCENARIO = [TABULAR_DATASET, PIPELINE_OUTPUT_TABULAR_DATASET]
    ALL = [PANDAS, TABULAR_DATASET, PIPELINE_OUTPUT_TABULAR_DATASET]


class ErrorLinks(Enum):
    """Constants to store the link to correct the errors."""
    DUPLICATED_INDEX = 'https://aka.ms/ForecastingConfigurations'


class AutoMLDefaultTimeouts:
    """Constants to store the default timeouts"""
    DEFAULT_ITERATION_TIMEOUT_SECONDS = 3600
    DEFAULT_EXPERIMENT_TIMEOUT_SECONDS = 86400 * 6  # 6 days.
    DEFAULT_FEATSWEEP_TIMEOUT_SECONDS = int(DEFAULT_EXPERIMENT_TIMEOUT_SECONDS / 4.0)  # 1/4 of exp timeout.
