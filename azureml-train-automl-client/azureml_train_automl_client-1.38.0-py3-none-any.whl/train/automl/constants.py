# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines constants used in automated ML in Azure Machine Learning.

Before you begin an experiment, you specify the kind of machine learning problem you are solving
with the :class:`azureml.train.automl.automlconfig.AutoMLConfig` class.
Azure Machine Learning supports task types of classification, regression, and forecasting.
For more information, see [How to define a machine learning
task](https://docs.microsoft.com/azure/machine-learning/service/how-to-define-task-type).

For the task types classification, regression, and forecasing, the supported algorithms are listed,
respectively, in the :class:`azureml.train.automl.constants.SupportedModels.Classification`,
:class:`azureml.train.automl.constants.SupportedModels.Regression`, and
:class:`azureml.train.automl.constants.SupportedModels.Forecasting` classes. The listed algorithms
for each task type are used during the automation and tuning process. As a user, there is no need
for you to specify the algorithm. For more information, see [Configure automated ML experiments in
Python](https://docs.microsoft.com/azure/machine-learning/service/how-to-configure-auto-train).
"""

from azureml.automl.core.shared.constants import (
    ModelClassNames,
    MODEL_PATH,
    MODEL_PATH_TRAIN,
    MODEL_PATH_ONNX,
    MODEL_RESOURCE_PATH_ONNX,
    PROPERTY_KEY_OF_MODEL_PATH,
    CHILD_RUNS_SUMMARY_PATH,
    VERIFIER_RESULTS_PATH,
    LOCAL_MODEL_PATH,
    LOCAL_MODEL_PATH_TRAIN,
    LOCAL_MODEL_PATH_ONNX,
    LOCAL_MODEL_RESOURCE_PATH_ONNX,
    LOCAL_CHILD_RUNS_SUMMARY_PATH,
    LOCAL_VERIFIER_RESULTS_PATH,
    EnsembleConstants,
    Defaults,
    RunState,
    API,
    AcquisitionFunction,
    Status,
    PipelineParameterConstraintCheckStatus,
    OptimizerObjectives,
    Optimizer,
    Tasks as CommonTasks,
    ClientErrors,
    ServerStatus,
    TimeConstraintEnforcement,
    PipelineCost,
    Metric,
    MetricObjective,
    TrainingType,
    NumericalDtype,
    TextOrCategoricalDtype,
    TrainingResultsType,
    get_metric_from_type,
    get_status_from_type,
)

from azureml.automl.core.constants import (
    FeatureType, SupportedTransformers, FeaturizationConfigMode
)

from enum import Enum


AUTOML_IMAGE_RUN_SOURCE = "AutoMLImageSDK"
AUTOML_SETTINGS_PATH = "automl_settings.pkl"
AUTOML_FIT_PARAMS_PATH = "fit_params.pkl"
LOCAL_SCRIPT_NAME = "_local_managed_startup_script.py"
LOCAL_PREDICT_NAME = "_inference.py"
PREDICTED_METRIC_NAME = "predicted"
MODEL_FILE = "model.pkl"
PYPI_INDEX = 'https://pypi.python.org/simple'
PREDICT_OUTPUT_FILE = "predict_out.pkl"
INFERENCE_OUTPUT = "inference.csv"
MANAGED_RUN_ID_PARAM = "_local_managed_run_id"
SCRIPT_RUN_ID_PROPERTY = "_wrapper_run_id"


class SupportedModels:
    """Defines friendly names for automated ML algorithms supported by Azure Machine Learning.

    If you plan to export your auto ML created models to an
    `ONNX model <https://docs.microsoft.com/azure/machine-learning/concept-onnx>`, only
    those algorithms indicated with an * are able to be converted to the ONNX format.
    Learn more about converting models to
    `ONNX <https://docs.microsoft.com/azure/machine-learning/concept-automated-ml#automl--onnx>`.

    | Classification                      |
    | ------------------------------------|
    | Logistic Regression*                |
    | Light GBM*                          |
    | Gradient Boosting*                  |
    | Decision Tree*                      |
    | K Nearest Neighbors*                |
    | Linear SVC                          |
    | Support Vector Classification (SVC)*|
    | Random Forest*                      |
    | Extremely Randomized Trees*         |
    | Xgboost*                            |
    | Averaged Perceptron Classifier      |
    | Naive* Bayes                        |
    | Stochastic Gradient Descent (SGD)*  |
    | Linear SVM Classifier*              |
    | Tabnet Classifier                   |

    | Regression                          |
    | ----------------------------------- |
    | Elastic Net*                        |
    | Light GBM*                          |
    | Gradient Boosting*                  |
    | Decision Tree*                      |
    | K Nearest Neighbors*                |
    | LARS Lasso*                         |
    | Stochastic Gradient Descent (SGD)   |
    | Random Forest*                      |
    | Extremely Randomized Trees*         |
    | Xgboost*                            |
    | Online Gradient Descent Regressor   |
    | Fast Linear Regressor               |
    | Tabnet Regressor                    |

    | Time Series Forecasting             |
    | ----------------------------------- |
    | Elastic Net                         |
    | Light GBM                           |
    | Gradient Boosting                   |
    | Decision Tree                       |
    | K Nearest Neighbors                 |
    | LARS Lasso                          |
    | Stochastic Gradient Descent (SGD)   |
    | Random Forest                       |
    | Extremely Randomized Trees          |
    | Xgboost                             |
    | Auto-ARIMA                          |
    | Prophet                             |
    | ForecastTCN                         |
    """

    class Classification:
        """Defines the names of classification algorithms used in automated ML.

        Azure supports these classification algorithms, but you as a user do not
        need to specify the algorithms directly. Use the ``allowed_models`` and
        ``blocked_models`` parameters of :class:`azureml.train.automl.automlconfig.AutoMLConfig` class
        to include or exclude models.

        To learn more about in automated ML in Azure see:

        * `What is automated ML <https://docs.microsoft.com/azure/machine-learning/concept-automated-ml>`_

        * `How to define a machine learning
          task <https://docs.microsoft.com/azure/machine-learning/how-to-define-task-type>`_

        * `Configure automated ML experiments in
          Python <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train>`_

        * `TensorFlowDNN, TensorFlowLinearClassifier are deprecated.`
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
        """Defines the names of regression algorithms used in automated ML.

        Azure supports these regression algorithms, but you as a user do not
        need to specify the algorithms directly. Use the ``allowed_models`` and
        ``blocked_models`` parameters of :class:`azureml.train.automl.automlconfig.AutoMLConfig` class
        to include or exclude models.

        To learn more about in automated ML in Azure see:

        * `What is automated ML <https://docs.microsoft.com/azure/machine-learning/concept-automated-ml>`_

        * `How to define a machine learning
          task <https://docs.microsoft.com/azure/machine-learning/how-to-define-task-type>`_

        * `Configure automated ML experiments in
          Python <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train>`_

        * `TensorFlowDNN, TensorFlowLinearRegressor are deprecated.`
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
        """Defines then names of forecasting algorithms used in automated ML.

        Azure supports these regression algorithms, but you as a user do not
        need to specify the algorithms. Use the ``allowed_models`` and
        ``blocked_models`` parameters of :class:`azureml.train.automl.automlconfig.AutoMLConfig` class
        to include or exclude models.

        To learn more about in automated ML in Azure see:

        * `What is automated ML <https://docs.microsoft.com/azure/machine-learning/concept-automated-ml>`__

        * `How to define a machine learning
          task <https://docs.microsoft.com/azure/machine-learning/how-to-define-task-type>`__

        * `Configure automated ML experiments in
          Python <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train>`__
        """

        AutoArima = 'AutoArima'
        Average = 'Average'
        Arimax = 'Arimax'
        ExponentialSmoothing = 'ExponentialSmoothing'
        Naive = 'Naive'
        Prophet = 'Prophet'
        SeasonalAverage = 'SeasonalAverage'
        SeasonalNaive = 'SeasonalNaive'
        TCNForecaster = 'TCNForecaster'


MODEL_EXPLANATION_TAG = "model_explanation"

BEST_RUN_ID_SUFFIX = 'best'

MAX_ITERATIONS = 1000
MAX_SAMPLES_AUTOBLOCK = 5000
MAX_SAMPLES_AUTOBLOCKED_ALGOS = [SupportedModels.Classification.KNearestNeighborsClassifier,
                                 SupportedModels.Regression.KNearestNeighborsRegressor,
                                 SupportedModels.Classification.SupportVectorMachine]
EARLY_STOPPING_NUM_LANDMARKS = 20
PIPELINE_FETCH_BATCH_SIZE_LIMIT = 20

DATA_SCRIPT_FILE_NAME = "get_data.py"

"""Names of algorithms that do not support sample weights."""
Sample_Weights_Unsupported = {
    ModelClassNames.RegressionModelClassNames.ElasticNet,
    ModelClassNames.ClassificationModelClassNames.KNearestNeighborsClassifier,
    ModelClassNames.RegressionModelClassNames.KNearestNeighborsRegressor,
    ModelClassNames.RegressionModelClassNames.LassoLars
}

"""Algorithm names that we must force to run in single threaded mode."""
SINGLE_THREADED_ALGORITHMS = [
    ModelClassNames.ClassificationModelClassNames.KNearestNeighborsClassifier,
    ModelClassNames.RegressionModelClassNames.KNearestNeighborsRegressor
]

TrainingType.FULL_SET.remove(TrainingType.TrainValidateTest)


class ComputeTargets:
    """Defines names of compute targets supported in automated ML in Azure Machine Learning.

    Specify the compute target of an experiment run using the :class:`azureml.train.automl.automlconfig.AutoMLConfig`
    class.
    """

    ADB = 'ADB'
    AMLCOMPUTE = 'AmlCompute'
    BATCHAI = 'BatchAI'
    DSVM = 'VirtualMachine'
    LOCAL = 'local'

    _ALL = [ADB, AMLCOMPUTE, BATCHAI, DSVM, LOCAL]


class TimeSeries:
    """Defines parameters used for time-series forecasting.

    The parameters are specified with the :class:`azureml.train.automl.automlconfig.AutoMLConfig` class.
    The time series forecasting task requires these additional parameters during configuration.

    Attributes:
        DROP_COLUMN_NAMES: Defines the names of columns to drop from featurization.

        GRAIN_COLUMN_NAMES: Defines the names of columns that contain individual time series data in your training
            data.

        MAX_HORIZON: Defines the length of time to predict out based on the periodicity of the data.

        TIME_COLUMN_NAME: Defines the name of the column in your training data containing a valid time-series.

    """

    TIME_COLUMN_NAME = 'time_column_name'
    GRAIN_COLUMN_NAMES = 'grain_column_names'
    DROP_COLUMN_NAMES = 'drop_column_names'
    MAX_HORIZON = 'max_horizon'


class Tasks(CommonTasks):
    """A subclass of Tasks in common.core module that can be extended to add more task types for the SDK.

    You can set the task type for your automated ML experiments using the ``task`` parameter of the
    :class:`azureml.train.automl.automlconfig.AutoMLConfig` constructor. For more information about
    tasks, see `How to define a machine learning
    task <https://docs.microsoft.com/azure/machine-learning/how-to-define-task-type>`_.
    """

    CLASSIFICATION = CommonTasks.CLASSIFICATION
    REGRESSION = CommonTasks.REGRESSION
    FORECASTING = 'forecasting'
    IMAGE_CLASSIFICATION = CommonTasks.IMAGE_CLASSIFICATION
    IMAGE_CLASSIFICATION_MULTILABEL = CommonTasks.IMAGE_CLASSIFICATION_MULTILABEL
    IMAGE_MULTI_LABEL_CLASSIFICATION = CommonTasks.IMAGE_MULTI_LABEL_CLASSIFICATION  # for temporary back-compat
    IMAGE_OBJECT_DETECTION = CommonTasks.IMAGE_OBJECT_DETECTION
    IMAGE_INSTANCE_SEGMENTATION = CommonTasks.IMAGE_INSTANCE_SEGMENTATION
    ALL_IMAGE = CommonTasks.ALL_IMAGE
    TEXT_CLASSIFICATION = CommonTasks.TEXT_CLASSIFICATION
    TEXT_CLASSIFICATION_MULTILABEL = CommonTasks.TEXT_CLASSIFICATION_MULTILABEL
    TEXT_NER = CommonTasks.TEXT_NER
    ALL_TEXT = CommonTasks.ALL_TEXT
    ALL_DNN = CommonTasks.ALL_DNN
    ALL = [CommonTasks.CLASSIFICATION, CommonTasks.REGRESSION, FORECASTING] + ALL_IMAGE + ALL_TEXT


class ExperimentObserver:
    """Constants used by the Experiment Observer to report progress during preprocessing."""

    EXPERIMENT_STATUS_METRIC_NAME = "experiment_status"
    EXPERIMENT_STATUS_DESCRIPTION_METRIC_NAME = "experiment_status_description"


class Framework:
    """Constants for the various supported framework."""

    PYTHON = "python"
    PYSPARK = "pyspark"
    FULL_SET = {"python", "pyspark"}


class Scenarios:
    """Constants for the various curated environment scenarios."""

    AUTOML = "AutoML"  # New default for PROD SDK
    SDK = "SDK"  # Default for azureml.train.automl.VESRION<1.5.0
    SDK_COMPATIBLE = "SDK-1.13.0"  # Old default for PROD SDK
    SDK_COMPATIBLE_1120 = "SDK-Compatible"  # Default for azureml.train.automl.VESRION>1.5.0,<1.13.0
    _NON_PROD = "non-prod"
    VISION = "Vision"  # Default for all vision based tasks
    VISION_CANDIDATE = "Vision-Candidate"
    VISION_PREVIEW = "Vision-Preview"

    VISION_SET = {VISION, VISION_CANDIDATE, VISION_PREVIEW}


class Environments:
    """Curated environments defined for AutoML."""

    AUTOML = "AzureML-AutoML"
    AUTOML_DNN = "AzureML-AutoML-DNN"
    AUTOML_GPU = "AzureML-AutoML-GPU"
    AUTOML_DNN_GPU = "AzureML-AutoML-DNN-GPU"


class _DataArgNames:
    X = "X"
    y = "y"
    sample_weight = "sample_weight"
    X_valid = "X_valid"
    y_valid = "y_valid"
    sample_weight_valid = "sample_weight_valid"
    training_data = "training_data"
    validation_data = "validation_data"
    test_data = "test_data"


class SupportedInputDatatypes:
    """Input data types supported by AutoML for different Run types."""

    PANDAS = "pandas.DataFrame"
    TABULAR_DATASET = "azureml.data.tabular_dataset.TabularDataset"
    PIPELINE_OUTPUT_TABULAR_DATASET = "azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset"

    LOCAL_RUN_SCENARIO = [PANDAS, TABULAR_DATASET, PIPELINE_OUTPUT_TABULAR_DATASET]
    REMOTE_RUN_SCENARIO = [TABULAR_DATASET, PIPELINE_OUTPUT_TABULAR_DATASET]
    ALL = [PANDAS, TABULAR_DATASET, PIPELINE_OUTPUT_TABULAR_DATASET]


class HTSConstants:
    """Contants used by AutoML hierarchical timeseries runs."""

    HIERARCHY = "hierarchy_column_names"
    HTS_INPUT = "hts_raw"
    HTS_OUTPUT_PARTITIONED = "tabular_dataset_partition"
    TRAINING_LEVEL = "hierarchy_training_level"
    HTS_TRAINING_METADATA = "automl_training"
    HTS_EXPLANATIONS_OUT = "training_explanations"

    # Column names related constants
    HTS_CROSS_TIME_PROPORTION = "_hts_cross_time_proportion"
    HTS_CROSS_TIME_SUM = "_hts_cross_time_sum"
    HTS_ENDTIME = "_hts_endtime"
    HTS_FREQUENCY = "_hts_freq"
    HTS_HIERARCHY_SUM = "_hts_hierarchy_sum"
    HTS_STARTTIME = "_hts_starttime"
    PREDICTION_COLUMN = "automl_predictions"

    # Graph related constants
    NODE_ID = "node_id"
    HTS_ROOT_NODE_NAME = "AUTOML_TOP_NODE"
    HTS_ROOT_NODE_LEVEL = "AUTOML_TOP_LEVEL"

    # Logging related constants
    RUN_TYPE = "hierarchy-timeseries"
    LOGGING_PIPELINE_ID = "pipeline_run_id"
    LOGGING_RUN_ID = "script_run_id"
    LOGGING_RUN_TYPE = "run_type"
    LOGGING_RUN_SUBTYPE = "run_subtype"
    LOGGING_SCRIPT_SESSION_ID = "script_session_id"
    LOGGING_SUBSCRIPTION_ID = "subscription_id"
    LOGGING_REGION = "region"

    # script arguments constants
    PARTITIONED_DATASET_NAME = "--partitioned-dataset-name"
    PIPELINE_SCENARIO = "--pipeline-scenario"
    ALLOCATION_METHOD = "--allocation-method"
    BLOB_PATH = "--filedataset-blob-dir"
    FORECAST_LEVEL = "--forecast-level"
    HTS_GRAPH = "--hts-graph"
    INPUT_DATA_NAME = "--input-name"
    METADATA_INPUT = "--input-medatadata"
    NODES_COUNT = "--nodes-count"
    OUTPUT_PATH = "--output-path"
    RAW_FORECASTS = "--raw-forecasts"
    TRAINING_RUN_ID = "--training-runid"
    ENGINEERED_EXPLANATION = "--enable-engineered-explanation"
    EXPLANATION_DIR = "--explanation-dir"
    ENABLE_EVENT_LOGGER = "--enable-event-logger"

    DEFAULT_ARG_VALUE = "__DEFAULT_ARG_VALUE"

    # This argument is defined by PRS. Cannot change it.
    APPEND_HEADER_PRS = "--append_row_dataframe_header"

    # json fields constants
    AVERAGE_HISTORICAL_PROPORTIONS = "average_historical_proportions"
    COLLECT_SUMMARY_JSON_AGG_FILE = "aggregated_file"
    COLLECT_SUMMARY_JSON_ORIGIN_FILE = "origin_files"
    COLLECT_SUMMARY_JSON_SUMMARY = "summary"
    PROPORTIONS_OF_HISTORICAL_AVERAGE = "proportions_of_historical_average"
    RUN_INFO_STATUS = "status"
    COLUMN_VOCABULARY_DICT = "column_vocabulary_dict"
    RUN_INFO_AUTOML_RUN_ID = "run_id"
    RUN_INFO_FAILED_REASON = "failed_reason"

    # run properties and model tags constants
    MODEL_TAG_AUTOML = "AutoML"
    MODEL_TAG_MODEL_TYPE = "ModelType"
    MODEL_TAG_STEP_RUN_ID = "StepRunId"
    MODEL_TAG_RUN_ID = "RunId"
    MODEL_TAG_HIERARCHY = "Hierarchy"
    MODEL_TAG_HASH = "Hash"
    RUN_PROPERTIES_HTS_HIERARCHY = "hts_hierarchy"
    RUN_PROPERTIES_MANY_MODELS_RUN = "many_models_run"
    RUN_PROPERTIES_INPUT_FILE = "many_models_input_file"
    RUN_PROPERTIES_DATA_TAGS = "hts_data_tags"
    METADATA_JSON_METADATA = "metadata"
    JSON_VERSION = "version"

    # hts steps related constants
    STEP_DATASET_PARTITION = "dataset-partition"
    STEP_HIERARCHY_BUILDER = "hierarchy-builder"
    STEP_DATA_AGGREGATION = "data-aggregation-and-validation"
    STEP_DATA_AGGREGATION_FILEDATASET = "data-aggregation-filedataset"
    STEP_AUTOML_TRAINING = "automl-training"
    STEP_PROPORTIONS_CALCULATION = "proportions-calculation"
    STEP_DATASET_PARTITION_INF = "dataset-partition-inference"
    STEP_EXPLAIN_ALLOCATION = "forecast-explanation-allocation"
    STEP_FORECAST = "forecast-parallel"
    STEP_ALLOCATION = "forecast-allocation"

    # File related constants
    GRAPH_JSON_FILE = "hts_graph.json"
    HTS_CROSS_TIME_AGG_CSV = "hts_cross_time_agg.csv"
    HTS_DIR_EXPLANATIONS = "explanations"
    HTS_FILE_NODE_COLUMNS_INFO_JSON = "node_columns_info.json"
    HTS_FILE_DATASET_COLLECT_SUMMARY = "dataset_collect_summary.json"
    HTS_FILE_POSTFIX_NODE_COLUMNS_INFO_JSON = "_node_columns_info.json"
    HTS_FILE_POSTFIX_METADATA_CSV = "_metadata.csv"
    HTS_FILE_POSTFIX_RUN_INFO_JSON = "_run_info.json"
    HTS_FILE_POSTFIX_EXPLANATION_INFO_JSON = "_explanation_info.json"
    HTS_FILE_POSTFIX_ENG_COL_INFO_JSON = "_engineered_col_info.json"
    HTS_FILE_PRED_RESULTS_POSTFIX = "_results.json"
    HTS_FILE_PRED_RESULTS = "prediction_results.json"
    HTS_FILE_PREDICTIONS = "allocated_predictions.csv"
    HTS_FILE_RAW_PREDICTIONS = "raw_predictions.csv"
    HTS_FILE_PROPORTIONS_METADATA_JSON = "metadata.json"
    HTS_FILE_RUN_INFO_JSON = "run_info.json"
    HTS_FILE_EXPLANATION_INFO_JSON = "explanation_info.json"
    SETTINGS_FILE = "automl_settings.json"

    # Explanation types
    EXPLANATIONS_RAW_FEATURES = 'raw'
    EXPLANATIONS_ENGINEERED_FEATURES = 'engineered'

    # run properties
    HTS_PROPERTIES_PARTITIONED_TABULAR_DATASET_NAME = "partitioned_tabular_dataset"
    HTS_PROPERTIES_RUN_TYPE = "hts_run_type"
    HTS_PROPERTIES_TRAINING = "training"
    HTS_PROPERTIES_INFERENCE = "inference"
    HTS_PROPERTIES_SETTINGS = "hts_settings"
    HTS_PROPERTIES_TRAINING_RUN_ID = "hts_training_run_id"

    # run tags
    HTS_TAG_TRAINING_RUN_ID = "hts_training_run"

    # tuning parameters constants.
    HTS_COUNT_VECTORIZER_MAX_FEATURES = 5

    AGGREGATION_METHODS = {AVERAGE_HISTORICAL_PROPORTIONS, PROPORTIONS_OF_HISTORICAL_AVERAGE}

    HIERARCHY_PARAMETERS = {HIERARCHY, TRAINING_LEVEL}

    HTS_SCRIPTS_SCENARIO_ARG_DICT = {
        STEP_DATASET_PARTITION: [
            PARTITIONED_DATASET_NAME, TRAINING_RUN_ID, ENABLE_EVENT_LOGGER, INPUT_DATA_NAME, PIPELINE_SCENARIO],
        STEP_HIERARCHY_BUILDER: [OUTPUT_PATH, BLOB_PATH, ENABLE_EVENT_LOGGER, INPUT_DATA_NAME],
        STEP_DATA_AGGREGATION: [OUTPUT_PATH, BLOB_PATH, HTS_GRAPH, NODES_COUNT, ENABLE_EVENT_LOGGER],
        STEP_AUTOML_TRAINING: [
            OUTPUT_PATH, METADATA_INPUT, HTS_GRAPH, ENGINEERED_EXPLANATION, NODES_COUNT, ENABLE_EVENT_LOGGER],
        STEP_PROPORTIONS_CALCULATION: [METADATA_INPUT, HTS_GRAPH, ENABLE_EVENT_LOGGER],
        STEP_DATASET_PARTITION_INF: [
            PARTITIONED_DATASET_NAME, TRAINING_RUN_ID, NODES_COUNT, ENABLE_EVENT_LOGGER, INPUT_DATA_NAME,
            PIPELINE_SCENARIO],
        STEP_FORECAST: [TRAINING_RUN_ID, OUTPUT_PATH, ENABLE_EVENT_LOGGER],
        STEP_ALLOCATION: [
            FORECAST_LEVEL, ALLOCATION_METHOD, TRAINING_RUN_ID, OUTPUT_PATH, RAW_FORECASTS, ENABLE_EVENT_LOGGER],
        STEP_EXPLAIN_ALLOCATION: [
            EXPLANATION_DIR, HTS_GRAPH, ENGINEERED_EXPLANATION, OUTPUT_PATH, ENABLE_EVENT_LOGGER]
    }

    HTS_OUTPUT_ARGUMENTS_DICT = {
        ALLOCATION_METHOD: "allocation_method",
        BLOB_PATH: "filedataset_blob_dir",
        FORECAST_LEVEL: "forecast_level",
        HTS_GRAPH: "hts_graph",
        INPUT_DATA_NAME: "input_data_name",
        METADATA_INPUT: "input_metadata",
        NODES_COUNT: "nodes_count",
        OUTPUT_PATH: "output_path",
        PARTITIONED_DATASET_NAME: "partitioned_dataset_name",
        PIPELINE_SCENARIO: "pipeline_scenario",
        RAW_FORECASTS: "raw_forecasts",
        TRAINING_RUN_ID: "training_run_id",
        EXPLANATION_DIR: "explanation_dir",
        ENGINEERED_EXPLANATION: "engineered_explanation",
        ENABLE_EVENT_LOGGER: "enable_event_logger"
    }


class HTSSupportedInputType(Enum):
    """Enum for the supported input types."""

    FILE_DATASET = "file_dataset"
    TABULAR_DATASET = "tabular_dataset"
    PARTITIONED_TABULAR_INPUT = "partitioned_tabular_input"


class AutoMLPipelineScenario:
    """Constants for AutoML pipeline Scenario."""

    HTS = "hts"
    MANY_MODELS = "many_models"
