# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class AutoMLErrorStrings:
    """
    All un-formatted error strings that accompany the common error codes in AutoML.

    Dev note: Please keep this list sorted on keys.
    """

    # region UserErrorStrings
    ALLOWED_MODELS_NON_EXPLAINABLE = "All models in the allowlist are not explainable, " \
                                     "but model_explainability is set to True. " \
                                     "Please allow one of explainable model or set model_explainability to False. " \
                                     "Non explainable models: {non_explainable_models}."
    ALLOWED_MODELS_SUBSET_OF_BLOCKED_MODELS = "All allowed models are within blocked models list. Please " \
                                              "remove models from the exclude list or add models to the allow list."
    ALLOWED_MODELS_UNSUPPORTED = "Allowed models [{allowed_models}] are not supported for scenario: " \
                                 "{scenario}."
    ALL_ALGORITHMS_ARE_BLOCKED = "All models are blocked. Please ensure that at least one model is allowed."
    ALL_FEATURES_ARE_EXCLUDED = "X should contain at least one feature with a minimum of two unique values to train."
    ALL_TARGETS_NAN = "All the values in the target column are either empty or NaN. Please make sure there are at " \
                      "least two distinct values in the target column."
    ALL_TARGETS_OVERLAPPING = "At least two distinct values for the target column are required for " \
                              "{task_type} task. Please check the values in the target column."
    ALL_TARGETS_UNIQUE = "For a {task_type} task, the label cannot be unique for every sample."
    ARIMAX_OLS_FIT_EXCEPTION = "Unable to fit the ARIMAX model, because of exception " \
                               "during fitting of the linear model. " \
                               "Exception: {exception}. Please check your data and run the AutoML again."
    ARIMAX_OLS_LINALG_ERROR = "Unable to fit the ARIMAX model, because " \
                              "linear model does not converge. Please check your data. " \
                              "Original Error: {error}"
    BAD_DATA_IN_WEIGHT_COLUMN = "Weight column contains invalid values such as 'NaN' or 'infinite'"
    CACHE_OPERATION = "Cache operation ('{operation_name}') failed due to an OS error. This is most commonly caused " \
                      "due to insufficient resources on the OS (e.g. process limits, disk space) or inadequate " \
                      "permissions on the project directory ({path}). Error details: {os_error_details}."
    CANCEL_UNSUPPORTED_FOR_LOCAL_RUNS = "Cancel operation is not supported for local runs. Local runs may be " \
                                        "canceled by raising a keyboard interrupt (e.g. via. `Ctrl + C`)"
    COMPUTE_NOT_READY = "Compute not in 'Succeeded' state. Please choose another compute or wait till it is ready."
    CONFLICTING_FEATURIZATION_CONFIG_DROPPED_COLUMNS = "Featurization '{sub_config_name}' customization contains " \
                                                       "columns ({dropped_columns}), which are also configured to be" \
                                                       " dropped via drop_columns. Please resolve the inconsistency " \
                                                       "by reconfiguring the columns that are to be customized."
    CONFLICTING_FEATURIZATION_CONFIG_RESERVED_COLUMNS = "Featurization '{sub_config_name}' customization contains " \
                                                        "reserved columns ({reserved_columns}). Please resolve the " \
                                                        "inconsistency by reconfiguring the columns that are to be " \
                                                        "customized."
    CONFLICTING_VALUE_FOR_ARGUMENTS = "Conflicting or duplicate values are provided for arguments: [{arguments}]"
    CONTENT_MODIFIED = "The data was modified while being read. Error: {dprep_error}"
    CONTINUE_RUN_UNSUPPORTED_FOR_ADB = "The module '{module_name}' must be installed in order to continue an ADB " \
                                       "experiment. Please install this dependency to allow continuing an " \
                                       "experiment. This can be done via. `pip install {module_name}`."
    CONTINUE_RUN_UNSUPPORTED_FOR_IMAGE_RUNS = "Continuing an AutoML Image run is not supported."
    CONTINUE_RUN_UNSUPPORTED_FOR_UNTRACKED_RUNS = "Continuing this experiment is not supported. This is because " \
                                                  "tracking child runs is disabled for this experiment."
    CREDENTIALLESS_DATASTORE_NOT_SUPPORTED = "Credentialless datastore options are not supported by AutoML. " \
                                             "Please ensure {data_store} has valid credentials associated to " \
                                             "use AutoML."
    DATABASE_QUERY = "Database query error while fetching data. Error: {dprep_error}"
    DATAPREP_SCRIPT_EXECUTION = "Encountered error while fetching data. Error: {dprep_error}"
    DATAPREP_STEP_TRANSLATION = "Encountered step translation error while fetching data. Error: {dprep_error}"
    DATAPREP_VALIDATION = "Validation error while fetching data. Error: {dprep_error}"
    DATASETS_FEATURE_COUNT_MISMATCH = "The number of features in [{first_dataset_name}]({first_dataset_shape}) does " \
                                      "not match with those in [{second_dataset_name}]({second_dataset_shape}). " \
                                      "Please inspect your data, and make sure that features are aligned in " \
                                      "both the Datasets."
    DATASET_CONTAINS_INF = "The input dataset {data_object_name} contains infinity values (e.g. np.inf). " \
                           "Please drop these rows before submitting the experiment again."
    DATASET_FILE_READ = "Fetching data from the underlying storage account timed out. Please retry again after " \
                        "some time, or optimize your blob storage performance."
    DATASTORE_NOT_FOUND = "The provided Datastore was not found. Error: {dprep_error}"
    DATA_AUTH_BAD = "Datastore {data_store_name} was not accessible. Please update the authentication to the " \
                    "datastore and retry."
    DATA_FROM_MULTIPLE_GROUPS = "The input file {file_name} in the dataset contains data for more than one training " \
                                "level node. Please check the following table to remove those rows\n" \
                                "{unique_df_summary}"
    DATA_MEMORY_ERROR = "Failed to retrieve data from {data} due to MemoryError."
    DATA_NOT_PARTITIONED = "The dataset provided was not partitioned."
    DATA_OTHER_NON_AUTH_ERROR = "Datastore {data_store_name} access failed with error: {exception}."
    DATA_PATH_INACCESSIBLE = "The provided path to the data in the Datastore was inaccessible. Please make sure " \
                             "you have the necessary access rights on the resource. Error: {dprep_error}"
    DATA_PATH_NOT_FOUND = "The provided path to the data in the Datastore does not exist. Error: {dprep_error}"
    DATA_SCRIPT_NOT_FOUND = "The data script (containing get_data function) could not be located at: {script_path}. " \
                            "Ensure that the file exists, and the function get_data (returning X, y, X_valid, " \
                            "y_valid) is callable.\n Please note that this scenario is deprecated. Instead, " \
                            "pass in a training_data and/or validation_data along with a label_column_name as part " \
                            "of AutoMLConfig."
    DATA_SHAPE_MISMATCH = "One or more data input arrays has incompatible dimensions. When providing X, y, weights " \
                          "as separate input arrays, ensure that X is a two-dimensional array, while y and weights " \
                          "are one-dimensional arrays. Note that this way of providing inputs is deprecated, " \
                          "instead use 'training_data' and 'validation_data' to specify data inputs, along with " \
                          "'label' and 'weights' column names."
    DATE_OUT_OF_RANGE_DURING_PADDING = \
        "The padding of time series has failed " \
        "because given the forecast frequency {freq} and the start date {start} it should " \
        "start at the date earlier than {min}."
    DATE_OUT_OF_RANGE_DURING_PADDING_GRAIN = \
        "The padding of short time series with identifier(s) {grain} has failed " \
        "because given the forecast frequency {freq} and the start date {start} it should " \
        "start at the date earlier than {min}."
    DEPENDENCY_WRONG_VERSION = "The model you attempted to retrieve requires '{module}' to be installed at " \
                               "'{ver}'. You have '{module}=={cur_version}', please reinstall '{module}{ver}' " \
                               "(e.g. `pip install {module}{ver}`) and rerun the previous command."
    DISK_FULL = "Operation {operation_name} failed due to low disk space. Please free up some space before " \
                "continuing with the experiment."
    DUPLICATE_COLUMNS = "'{data_object_name}' consists of duplicate columns: [{duplicate_columns}]. Please either " \
                        "drop the columns that are repeated, or rename one of the columns so that they are unique."
    EMPTY_LAGS_FOR_COLUMNS = "The lags for all columns are represented by empty lists. Please set the " \
                             "target_lags parameter to None to turn off the lag feature and run the experiment again."
    EXECUTION_FAILURE = "Failed to execute the requested operation: {operation_name:log_safe}. Error details: " \
                        "{error_details}"
    EXPERIMENT_TIMED_OUT = "Experiment timeout reached, skipping execution of the child run and terminating the " \
                           "parent run. Consider increasing experiment_timeout_hours."
    EXPERIMENT_TIMEOUT_FOR_DATA_SIZE = "The ExperimentTimeout should be set more than {minimum} minutes with an " \
                                       "input data of rows*cols({rows}*{columns}={total}), and up to {maximum}."
    EXPLAINABILITY_PACKAGE_MISSING = "Cannot complete the model explainability operation due to missing packages: " \
                                     "[{missing_packages}]"
    FEATURE_TYPE_UNSUPPORTED = "The column '{column_name}' in the input Dataset is of unsupported type: " \
                               "'{column_type}'. Supported type(s): '{supported_types}'"
    FEATURE_UNSUPPORTED_FOR_INCOMPATIBLE_ARGUMENTS = "Feature [{feature_name}] is unsupported due to incompatible " \
                                                     "values for argument(s): [{arguments}]"
    FEATURIZATION_CONFIG_COLUMN_MISSING = "The column(s) '{columns}' specified in the Featurization " \
                                          "{sub_config_name} customization is not present in the dataframe. " \
                                          "Valid columns: {all_columns}"
    FEATURIZATION_CONFIG_EMPTY_FILL_VALUE = "A fill value is required for constant value imputation. Please provide " \
                                            "a non-empty value for '{argument_name}' parameter. Example code: " \
                                            "`featurization_config.add_transformer_params('Imputer', ['column_name']" \
                                            ", \"{{'strategy': 'constant', 'fill_value': 0}}\")`"
    FEATURIZATION_CONFIG_FORECASTING_STRATEGY = "Only the following strategies are enabled for a " \
                                                "Forecasting task's target column: ({strategies}). Please fix your " \
                                                "featurization configuration and try again."
    FEATURIZATION_CONFIG_INVALID_TYPE = "The column {column_name} should be able to convert to {data_type} if " \
                                        "featurization configuration's {featurization_option} is enabled. " \
                                        "Please fix your data and try again."
    FEATURIZATION_CONFIG_MULTIPLE_IMPUTERS = "Only one imputation method may be defined for each column. In the " \
                                             "provided configuration, multiple imputers are assigned to the " \
                                             "following columns {columns}\n. Please verify that only one imputer " \
                                             "is defined per column."
    FEATURIZATION_CONFIG_PARAM_OVERRIDDEN = "Failed while {stage} learned transformations. This could be caused by " \
                                            "transformer parameters being overridden. Please check logs for " \
                                            "detailed error messages."
    FEATURIZATION_CONFIG_WRONG_IMPUTATION_VALUE = "A fill value can not be np.inf or np.NaN. Please correct " \
                                                  "the value and run AutoML again."
    FEATURIZATION_REQUIRED = "The training data contains features of type {feature_types}, that can't automatically " \
                             "be processed. Please turn on featurization by setting it as 'auto' or giving " \
                             "custom featurization settings. Feature(s) that require featurization: [{features}]"
    FORECAST_EMPTY_AGGREGATION = "The aggregation of the data set has resulted in empty dataframe. Please use the " \
                                 "dataset with the later dates."
    FORECAST_FIT_NOT_SUPPORT = "For a forecasting model, `fit` is not supported. " \
                               "Please submit an AutoML run to get the fitted model instead."
    FORECAST_HORIZON_EXCEEDED = \
        "Input prediction data X_pred or input forecast_destination contains dates later than " \
        "the forecast horizon. Please shorten the prediction data so that it is within the " \
        "forecast horizon or adjust the forecast_destination date."
    FORECAST_PREDICT_NOT_SUPPORT = "For a forecasting model, `predict` is not supported. " \
                                   "Please use `forecast` instead."
    GENERIC_TRANSFORM_EXCEPTION = "Failed to transform the input data using {transformer_name}"
    GRAIN_ABSENT = "The time series identifier {grain} does not exist in the training dataset. " \
                   "Please inspect your data."
    GRAIN_COLUMNS_AND_GRAIN_NAME_MISMATCH = "The number of time series identifier columns is different " \
                                            "from the length of a time series identifier name."
    GRAIN_SHORTER_THAN_TEST_SIZE = "Some time series identifiers in the input dataset are shorter than the " \
                                   "test size. For a test_size of {test_size}, " \
                                   "the minimum number of rows per time series identifier must be at least " \
                                   "{min_rows_per_grain}. Please either try to reduce the test_size or provide more " \
                                   "data per time series identifier."
    HIERARCHY_ALL_PARALLEL_FAILURE = "All the steps in {parallel_step} failed with UserError. " \
                                     "Please check {file_name} in artifacts for details."
    HIERARCHY_EXPLANATIONS_NOT_FOUND = "The {exp_type} explanations were not found."
    HIERARCHY_NO_TRAINING_RUN = "No valid training run can be found in the experiment. Please make sure" \
                                " that at least one successful training run is in the same experiment."
    HIERARCHY_PREDICTIONS_NOT_FOUND = "Unable to allocate predictions as no intermediate model predictions were found."
    HTTP_CONNECTION_FAILURE = "Failed to establish HTTP connection to the service. This may be caused due the local " \
                              "compute being overwhelmed with HTTP requests. Please make sure that there are " \
                              "enough network resources available for the experiment to run. More details: " \
                              "{error_details}"
    IMAGE_DUPLICATE_PARAMETERS = "Found duplicate entries for AutoML Image parameter '{parameter_name}'. " \
                                 "Please provide only one entry."
    IMAGE_ODD_NUM_ARGUMENTS = "An even number of elements in the arguments list is required. " \
                              "[{num_arguments}] elements were provided."
    IMAGE_PARAMETER_SPACE_EMPTY = "The parameter space must contain at least one parameter."
    INCOMPATIBLE_DEPENDENCY = "The installed version of '{package}' does not match the expected version.\n" \
                              "Installed: {current_package}\nExpected: {expected_package}\n" \
                              "Install the required package by running 'pip install \"{expected_package}\"'."
    INCOMPATIBLE_OR_MISSING_DEPENDENCY = "Install the required versions of packages using the requirements file. " \
                                         "Requirements file location: {validated_requirements_file_path}. " \
                                         "Alternatively, use remote target to avoid dependency management. \n" \
                                         "{missing_packages_message_header}\n{missing_packages_message}"
    INCOMPATIBLE_OR_MISSING_DEPENDENCY_DATABRICKS = "Install the required versions of packages by setting up the " \
                                                    "environment as described in documentation.\n" \
                                                    "{missing_packages_message_header}\n{missing_packages_message}"
    INCONSISTENT_COLUMN_TYPE_IN_TRAIN_VALID = "Datatype for column {column_name} was detected as {train_dtype} in " \
                                              "the training set, but was found to be {validation_dtype} in the " \
                                              "validation set. Please ensure that the datatypes between training " \
                                              "and validation sets are aligned."
    INCONSISTENT_NUMBER_OF_SAMPLES = "The number of samples in {data_one} and {data_two} are inconsistent. If you " \
                                     "are using an AzureML Dataset as input, this may be caused as a result of " \
                                     "having multi-line strings in the data. Please make sure that " \
                                     "'support_multi_line' is set to True when creating a Dataset. Example: " \
                                     "Dataset.Tabular.from_delimited_files('http://path/to/csv', " \
                                     "support_multi_line = True)"
    INDISTINCT_LABEL_COLUMN = "The label column {label_column_name} was also contained within the training data. " \
                              "Please rename this column in either X or y."
    INPUT_DATASET_EMPTY = "The provided Dataset contained no data. Please make sure there are non-zero number " \
                          "of samples and features in the data."
    INPUT_DATA_WITH_MIXED_TYPE = "A mix of Dataset and Pandas objects provided. " \
                                 "Please provide either all Dataset or all Pandas objects."
    INSUFFICIENT_GPU_MEMORY = "There is not enough GPU memory on the machine to do the requested operation. " \
                              "Please try running the experiment on a VM with higher GPU memory, decrease the batch " \
                              "size or image size."
    INSUFFICIENT_MEMORY = "There is not enough memory on the machine to do the requested operation. " \
                          "Please try running the experiment on a VM with higher memory."
    INSUFFICIENT_MEMORY_LIKELY = "'Subprocess (pid {pid}) killed by unhandled signal {errorcode} ({errorname}). " \
                                 "This is most likely due to an out of memory condition. " \
                                 "Please try running the experiment on a VM with higher memory."
    INSUFFICIENT_MEMORY_WITH_HEURISTICS = "There is not enough memory on the machine to do the requested operation. " \
                                          "The amount of available memory is {avail_mem} out of {total_mem} total " \
                                          "memory. To fit the model at least {min_mem} more memory is required. " \
                                          "Please try running the experiment on a VM with higher memory.\n" \
                                          "If your data have multiple time series, you can also consider using many " \
                                          "model solution to workaround the memory issue, please refer to " \
                                          "https://aka.ms/manymodel for details."
    INSUFFICIENT_SAMPLE_SIZE = "The training dataset '{data_object_name}' has {sample_count} usable records (i.e. " \
                               "those which are not NaN or None), which is less than the minimum required " \
                               "training sample size of {minimum_count}. Consider adding more data points to " \
                               "ensure better model accuracy."
    INSUFFICIENT_SHM_MEMORY = "There is not enough shared memory on the machine to do the requested operation. " \
                              "Please try running the experiment with a smaller batch size."
    INVALID_ARGUMENT_FOR_TASK = "Invalid argument(s) '{arguments}' for task type '{task_type}'."
    INVALID_ARGUMENT_TYPE = "Argument [{argument}] is of unsupported type: [{actual_type}]. " \
                            "Supported type(s): [{expected_types}]"
    INVALID_ARGUMENT_TYPE_WITH_CONDITION = "Argument [{argument}] is of unsupported type: [{actual_type}] when " \
                                           "'{condition_str}'.\n" \
                                           "Supported type(s): [{expected_types}]"
    INVALID_ARGUMENT_WITH_SUPPORTED_VALUES = "Invalid argument(s) '{arguments}' specified. " \
                                             "Supported value(s): '{supported_values}'."
    INVALID_ARGUMENT_WITH_SUPPORTED_VALUES_FOR_TASK = "Invalid argument(s) '{arguments}' specified for task type " \
                                                      "'{task_type}'. Supported value(s): '{supported_values}'."
    INVALID_COMPUTE_TARGET_FOR_DATABRICKS = "Databricks compute cannot be directly attached for AutoML runs. " \
                                            "Please pass in a spark context instead using the spark_context " \
                                            "parameter and set compute_target to 'local'."
    INVALID_CV_SPLITS = "cv_splits_indices should be a List of List[numpy.ndarray]. Each List[numpy.ndarray] " \
                        "corresponds to a CV fold and should have just 2 elements: The indices for training set " \
                        "and for the validation set."
    INVALID_DAMPING_SETTINGS = "Conflicting values are provided for arguments [{model_type}] and [{is_damped}]. " \
                               "Damping can only be applied when there is a trend term."
    INVALID_FEATURIZER = "[{featurizer_name}] is not a valid featurizer for featurizer type: [{featurizer_type}]"
    INVALID_FORECAST_DATE_FOR_GRAIN = "The forecast date ({forecast_date}) for time series identifier '{grain}' " \
                                      "cannot be less than the first observed date in the training data " \
                                      "({first_observed_date}). Please inspect the data."
    INVALID_INPUT_DATATYPE = "Input of type '{input_type}' is not supported. Supported types: [{supported_types}]" \
                             "Please refer to documentation for converting to Supported types: " \
                             "https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.dataset.dataset" \
                             "?view=azure-ml-py"
    INVALID_ITERATION = "Invalid iteration. Run {run_id} has {num_iterations} iterations."
    INVALID_LABEL_COLUMN_VALUES = "Found one or more of the following issues with the label column. " \
                                  "1) There more than than 2,147,483,647 labels. " \
                                  "2) Label column type is not valid for multi-class. " \
                                  "3) Label column contains invalid values for multi-class."
    INVALID_METRIC_FOR_SINGLE_VALUED_COLUMN = "The data in {data_object_name} is single valued. Please make sure " \
                                              "that the data is well represented with all classes for a " \
                                              "classification task. Or please try one of the following as primary " \
                                              "metrics: {valid_primary_metrics}."
    INVALID_ONNX_DATA = "The onnx resource passed in is invalid. Please make sure the x_train data is a pandas " \
                        "DataFrame and it has column names during training."
    INVALID_OPERATION_ON_RUN_STATE = "Operation [{operation_name}] on the RunID [{run_id}] is invalid. " \
                                     "Current run state: [{run_state}]"
    INVALID_PARAMETER_SELECTION = "The {parameter} parameter may take value of {values}."
    INVALID_SERIES_FOR_STL = "Cannot calculate STL decomposition on a series with NaN values. Please either fill in " \
                             "these values or drop these rows from the series."
    INVALID_STL_FEATURIZER_FOR_MULTIPLICATIVE_MODEL = "Cannot use multiplicative model type [{model_type}] because " \
                                                      "trend contains negative or zero values."
    INVALID_VALUES_IN_CV_SPLIT_COLUMN = "The CV split column must contain integer values from the set [0, 1], and " \
                                        "not all same such that it divides the dataset into a train-valid split. A " \
                                        "value of 1 indicates the row should be used for training while 0 indicates " \
                                        "the row should be used for validation."
    INVALID_VALUES_IN_DATA = "The input dataset cannot be pre-processed. This is usually caused by having an " \
                             "invalid value in one of the cells (e.g. a numpy array), or the rows in the dataset " \
                             "having different shapes. Clean up the data manually before re-submitting."
    ITERATION_TIMED_OUT = "Iteration timeout reached, skipping execution of the child run. " \
                          "Consider increasing iteration_timeout_minutes."
    LARGE_DATA_ALGORITHMS_WITH_UNSUPPORTED_ARGUMENTS = "AveragedPerceptronClassifier, FastLinearRegressor, " \
                                                       "OnlineGradientDescentRegressor are incompatible with " \
                                                       "following arguments: X, " \
                                                       "n_cross_validations, enable_dnn, test_size, " \
                                                       "enable_onnx_compatible_models, enable_subsampling, " \
                                                       "task_type=forecasting, spark_context and local compute"
    LOAD_MODEL_DEPENDENCY_MISSING = "The model you attempted to retrieve requires '{module}' to be installed at " \
                                    "'{ver}'. Please install '{module}{ver}' (e.g. `pip install {module}{ver}`) and " \
                                    "then rerun the previous command."
    LOCAL_INFERENCE_UNSUPPORTED = "Local inference is not supported for this feature."
    LOCAL_MANAGED_USER_ERROR = "Local managed run failed when trying to submit to the user compute with " \
                               "error type: {error_type}"
    MALFORMED_JSON_STRING = "Failed to parse the provided JSON string. Error: {json_decode_error}"
    MEMORY_EXHAUSTED = "There is not enough memory on the machine to fit the model. " \
                       "The amount of available memory is {avail_mem} out of {total_mem} " \
                       "total memory. To fit the model at least {min_mem} more memory is required. " \
                       "Please install more memory or use bigger virtual " \
                       "machine to generate model on this dataset."
    METHOD_NOT_FOUND = "Required method [{method_name}] is not found."
    MISSING_CACHE_CONTENTS = "Some of the intermediate data that was cached on the local disk (at path {path}) are " \
                             "no longer available. Missing file(s): {files}. Please try submitting the experiment " \
                             "again."
    MISSING_COLUMNS_IN_DATA = "Expected column(s) {columns} not found in {data_object_name}."
    MISSING_CREDENTIALS_FOR_WORKSPACE_BLOB_STORE = "Could not create a connection to the AzureFileService due to " \
                                                   "missing credentials. Either an Account Key or SAS token needs " \
                                                   "to be linked the default workspace blob store."
    MISSING_POSITIVE_LABEL = "Positive class label {positive_label} is missing from label column. " \
                             "Please check your positive_label and try again."
    MISSING_SECRETS = "Failed to get data from the Datastore due to missing secrets. Error: {dprep_error}"
    MISSING_VALIDATION_CONFIG = "No form of validation was provided. Please provide either a validation dataset, or " \
                                "specify the type of validation you would like to use."
    MODEL_DOWNLOAD_MISSING_DEPENDENCY = "Model download dependencies are missing. Please install {module}."
    MODEL_EXPLANATIONS_DATA_METADATA_DIMENSION_MISMATCH = "Mismatch found between number of features " \
                                                          "{number_of_features} and number of feature names " \
                                                          "{number_of_feature_names}"
    MODEL_EXPLANATIONS_FEATURE_NAME_LENGTH_MISMATCH = "Mismatch found between number of feature names " \
                                                      "{number_of_feature_names} and a dimension of the " \
                                                      "feature map {dimension_of_feature_map}"
    MODEL_EXPLANATIONS_UNSUPPORTED_FOR_ALGORITHM = "Model explanations are currently unsupported for {algorithm_name}."
    MODEL_MISSING = "Could not find a model with valid score for metric '{metric}'. Please ensure that at least one " \
                    "run was successfully completed with a valid score for the given metric."
    MODEL_NOT_FOUND = "Model with name {model_name} was not found in the workspace. Either this group was " \
                      "not seen during training or this group failed at training time. " \
                      "Please make sure this group exists in training data and had successful training."
    MODEL_NOT_PICKLABLE = "Model with name {model_name} was not deserializable in the current environment. " \
                          "Please use this environment to train the model."
    MODEL_NOT_SUPPORTED = "The model {model_name} is not supported by current " \
                          "version of AutoML and will not be used. " \
                          "Please upgrade SDK to the latest version to enable it."
    NON_DNN_TEXT_FEATURIZATION_UNSUPPORTED = "For non-English pre-processing of text data, please set " \
                                             "enable_dnn=True and make sure you are using GPU compute."
    NON_OVERLAPPING_COLUMNS_IN_TRAIN_VALID = "Some columns that are present in the validation dataset are absent " \
                                             "from the training dataset. Missing columns: [{missing_columns}]. " \
                                             "Please make sure that the columns in both the datasets are consistent."
    NO_FEATURE_TRANSFORMATIONS_ADDED = "No features could be identified or generated for the given data. " \
                                       "Please pre-process the data manually, or provide custom featurization options."
    NO_METRICS_DATA = "No metrics related data was present at the time of \'{metric}\' calculation either because " \
                      "data was not uploaded in time or because no runs were found in completed state. " \
                      "If the former, please try again in a few minutes."
    NUMBER_COLUMN_CONVERSION_ERROR = "The column {column} cannot be converted to number. Please check your data " \
                                     "and run the AutoML again."
    N_CROSS_VALIDATIONS_EXCEEDS_TRAINING_ROWS = "Number of usable training rows ({training_rows}) (i.e. excluding " \
                                                "rows with NaN or invalid target values)  is less than total " \
                                                "requested CV splits ({n_cross_validations}). " \
                                                "Please reduce the number of splits requested, or increase the size " \
                                                "of the input dataset with valid prediction targets."
    ONNX_NOT_ENABLED = "Requested an ONNX compatible model but the run has ONNX compatibility disabled."
    ONNX_SPLITS_NOT_ENABLED = "Requested a split ONNX featurized model but the run has split ONNX feautrization " \
                              "disabled."
    ONNX_UNSUPPORTED_DATATYPE = "Sparse matrices are currently not supported for ONNX compatibility. Please " \
                                "provide the input dataset as one of {supported_datatypes}, or disable ONNX " \
                                "compatibility by setting the flag 'enable_onnx_compatible_models' to False."
    OVERLAPPING_YMIN_YMAX = "The minimum and maximum value in the target column is the same: {value}. At least two " \
                            "distinct values for the target column are required for a regression task."
    PANDAS_DATETIME_CONVERSION_ERROR = "Column {column} of type {column_type} cannot be converted to pandas datetime."
    POWER_TRANSFORMER_INVERSE_TRANSFORM = "Failed to inverse transform: y_min is greater than the observed minimum " \
                                          "in y."
    QUANTILE_RANGE = "Value for argument quantile ({quantile}) is out of range. Quantiles must be strictly " \
                     "greater than 0 and less than 1."
    REMOTE_INFERENCE_UNSUPPORTED = "Remote inference is not supported for local or ADB runs."
    RUNTIME_MODULE_DEPENDENCY_MISSING = "Module '{module_name}' is required in the current environment for running " \
                                        "Remote or Local (in-process) runs. Please install this dependency " \
                                        "(e.g. `pip install {module_name}`) or provide a RunConfiguration."
    RUN_INTERRUPTED = "The run was terminated due to an interruption while being executed."
    SAMPLE_COUNT_MISMATCH = "The number of rows in X, y, weights are not same. If you are passing X, y & weights " \
                            "separately as arrays, ensure that the number of rows in all the arrays are equal. " \
                            "Note that this way of providing inputs is deprecated, instead use 'training_data' " \
                            "and 'validation_data' to specify data inputs along with 'label' and 'weights' " \
                            "column names."
    SAMPLE_WEIGHTS_UNSUPPORTED = "Sample weights are not supported for the following primary metrics: " \
                                 "{primary_metrics}."
    SEASONALITY_EXCEEDS_SERIES = "Series must be at least as long as input seasonality: {seasonality}."
    SEASONALITY_INSUFFICIENT_DATA = "Must have at least a full season of data for each time series identifier. " \
                                    "The series with identifier '{grain}' has {sample_count} observations with " \
                                    "seasonality '{seasonality}'."
    SNAPSHOT_LIMIT_EXCEED = "Snapshot is either large than {size} MB or {files} files"
    STL_FEATURIZER_INSUFFICIENT_DATA = 'STL featurizer requires at least two data points in each time series. Series' \
                                       ' ({grain}) contains only one data point. Please either add more data points ' \
                                       'or remove this series from the dataset.'
    STREAMING_INCONSISTENT_FEATURES = "The training dataset had {original_column_count} columns, but sub-sampling " \
                                      "the dataset produced {new_column_count} columns. Please verify that any " \
                                      "quotes or new-line characters are handled correctly."
    TCN_EMBEDDING_INVALID_FACTOR = "Invalid embedding factor {embed_factor}."
    TCN_EMBEDDING_INVALID_MULTILEVEL = "`multilevel` {multilevel} must be one of {multi_levels}."
    TCN_EMBEDDING_UNSUPPORTED_CALC_TYPE = "Unsupport {embed_calc_type} embedding output size calculation requeted."
    TCN_FORECAST_DEEPAR_NAN_IN_TRAINING_LOSS = "NaN in TCN forecast DeepAR training loss."
    TCN_METRICS_CALCULATION_ERROR = "Failed to calculate TCN metrics."
    TCN_MODEL_NOT_CONVERGENT = "Invalid Model, TCN training did not converge."
    TCN_RUNTIME_ERROR = "TCN run has met runtime error."
    TENSORFLOW_ALGOS_ALLOWED_BUT_DISABLED = "Tensorflow isn't enabled but only Tensorflow models were specified in " \
                                            "allowed_models."
    TIMESERIES_AGG_WITHOUT_FREQ = "Please provide the freq (forecast frequency) parameter to perform the data set " \
                                  "aggregation."
    TIMESERIES_CANNOT_INFER_FREQ_FROM_TIME_IDX = "Could not infer the frequency of the time index: {time_index}. " \
                                                 "Please provide the freq (forecast frequency) parameter. " \
                                                 "Examples: weekly - 'W', daily - 'D', hourly = 'H'. " \
                                                 "Forecasting parameters documentation: " \
                                                 "https://docs.microsoft.com/en-us/python/" \
                                                 "api/azureml-automl-core/azureml.automl." \
                                                 "core.forecasting_parameters.forecastingparameters" \
                                                 "?view=azure-ml-py " \
                                                 "Error details: {ex_info}"
    TIMESERIES_CANNOT_INFER_SINGLE_FREQ_FOR_ALL_TS = "Could not infer a single frequency for all time-series."
    TIMESERIES_COLUMN_NAMES_OVERLAP = "Some of the columns that are created by the [{class_name}] already " \
                                      "exist in the input TimeSeriesDataFrame: [{column_names}]." \
                                      "Please set `overwrite_columns` to `True` to proceed anyways."
    TIMESERIES_CONTEXT_AT_END_OF_Y = "The latest y values are non-NaN which indicates that there is nothing to " \
                                     "forecast. If it is expected, please run forecast() with " \
                                     "ignore_data_errors=True. In this case the NaNs before the time-wise latest " \
                                     "NaNs will be imputed and the known y values will be returned."
    TIMESERIES_CUSTOM_FEATURE_TYPE_CONVERSION = "Type conversion failed for converting the input column " \
                                                "{column_name} to the target column purpose {purpose}. Please check " \
                                                "whether your column can be converted to {target_type} by using " \
                                                "`pd.astype` and try again."
    TIMESERIES_DATA_FORMATTING_ERROR = "Internal error formatting time-series data: {exception}. " \
                                       "Please contact product support."
    TIMESERIES_DF_CANNOT_DROP_SPECIAL_COL = "The [{column_name}] column cannot be dropped. " \
                                            "Please remove it from the drop column list."
    TIMESERIES_DF_CANNOT_INFER_FREQ_FROM_TS_ID = \
        "Time series frequency cannot be inferred for time series identifier(s) [{grain_name_str}]. " \
        "Please ensure that each time series' time stamps are regularly spaced. " \
        "Filling with default values such as 0 may be needed for very sparse series."
    TIMESERIES_DF_CANNOT_INFER_FREQ_WITHOUT_TIME_IDX = "Cannot infer frequency without a time index."
    TIMESERIES_DF_COL_TYPE_NOT_SUPPORTED = "The type of column(s) '{col_name}' in the time series dataframe " \
                                           "is not supported. The supported type is [{supported_type}]."
    TIMESERIES_DF_COL_VALUE_NOT_EQUAL_ACROSS_ORIGIN = \
        "At least for one subset of data " \
        "which shares the same {grain_colnames} (time series identifier column names) " \
        "and {time_colname} (time_colname) value, the values of {colname} are not equal across " \
        "different {origin_time_colname} (origin_time_colname)."
    TIMESERIES_DF_CONTAINS_NAN = "One of X_pred columns contains only NaNs. If it is expected, please run forecast()" \
                                 " with ignore_data_errors=True."
    TIMESERIES_DF_CONTAINS_NAT = "The provided time column {time_column_name} contains pd.NaT which may be a result" \
                                 "of some data points not fitting the expected time format to start training. " \
                                 "To continue, please reformat the time stamp to the supported " \
                                 "month-day-year format and try again."
    TIMESERIES_DF_DUPLICATED_INDEX = "The data contains more than one value for a `time_index` and time series " \
                                     "identifier combination. Please ensure that time series identifier columns and " \
                                     "time column together uniquely determine a single value."
    TIMESERIES_DF_DUPLICATED_INDEX_TM_COL_NAME = \
        "The specified time column, '{time_column_name}', contains rows with duplicate timestamps. " \
        "If your data contains multiple time series, review the time series identifier column setting " \
        "to define the time series identifiers for your data. If the dataset needs to be aggregated, " \
        "please provide freq and target_aggregation_function parameters and run AutoML again."
    TIMESERIES_DF_DUPLICATED_INDEX_TM_COL_TM_IDX_COL_NAME = \
        "Found duplicated rows for {time_column_name} and {grain_column_names} combinations. " \
        "Please make sure the time series identifier setting is correct so that each series represents " \
        "one time-series, or clean the data to make sure there are no duplicates before passing to AutoML. " \
        "If the dataset needs to be aggregated, please provide freq and target_aggregation_function parameters " \
        "and run AutoML again."
    TIMESERIES_DF_DUPLICATED_INDEX_WITH_AUTO_TIMESERIES_ID_DETECTION = \
        "Duplicated timestamps were found and AutoML was unable to automatically detect " \
        "the time series id column names. " \
        "Please make sure the time series identifier setting is correct so that it corresponds to " \
        "one time-series, or preprocess the data to make sure there are no duplicates and run the experiment again. " \
        "Possible candidates for time series identifier column names: {detected_time_series_id_columns}"
    TIMESERIES_DF_FREQUENCY_CHANGED = "For time series identifier [{grain}], " \
                                      "the frequency of the training data [{train_freq}] is different from the " \
                                      "frequency of validation data [{valid_freq}]." \
                                      "Please make sure the frequencies are same."
    TIMESERIES_DF_FREQUENCY_ERROR = "An error occurred checking frequencies."
    TIMESERIES_DF_FREQUENCY_GENERIC_ERROR = "A non-specific error occurred checking frequencies across series."
    TIMESERIES_DF_FREQUENCY_LESS_THEN_FC = "The detected data frequency ({data_freq}) " \
                                           "is lower than the forecast frequency ({forecast_freq}). " \
                                           "Please set the freq parameter to a lower frequency. " \
                                           "Documentation on freq parameter: " \
                                           "{freq_doc}"
    TIMESERIES_DF_FREQUENCY_NOT_CONSISTENT = \
        "The frequency for the input data is not consistent. The expected frequency is a data " \
        "point every '{freq}'. Review the time series data to ensure consistent frequency alignment " \
        "and specify the frequency parameter. Learn more {forecasting_config}."
    TIMESERIES_DF_FREQUENCY_NOT_CONSISTENT_GRAIN = \
        "The frequency for the following time series identifier [{grain_level}] is not consistent. " \
        "The expected frequency is a data point every '{freq}'. Review the time series data to " \
        "ensure consistent frequency alignment and specify the frequency parameter. " \
        "Learn more {forecasting_config}."
    TIMESERIES_DF_INCORRECT_FORMAT = "Timeseries dataframe has incorrect format."
    TIMESERIES_DF_INDEX_VALUES_NOT_MATCH = "Index values for data_frames do not match."
    TIMESERIES_DF_INVALID_ARG_FC_PIPE_DESTINATION_AND_Y_PRED = \
        "Input prediction data y_pred and forecast_destination are both set. " \
        "Please provide either y_pred or a forecast_destination date, but not both."
    TIMESERIES_DF_INVALID_ARG_FC_PIPE_NO_DEST_OR_X_PRED = \
        "Input prediction data X_pred and forecast_destination are both None. " \
        "Please provide either X_pred or a forecast_destination date, but not both."
    TIMESERIES_DF_INVALID_ARG_FC_PIPE_Y_ONLY = "If y_pred is provided X_pred should not be None."
    TIMESERIES_DF_INVALID_ARG_FORECAST_HORIZON = "All forecast horizon values must be of integer type." \
                                                 "And all forecast horizon values must be greater than zero."
    TIMESERIES_DF_INVALID_ARG_NO_VALIDATION = \
        "Time-series only supports rolling-origin cross validation and train/validate splits." \
        "Provide either a n_cross_validations parameter or a validation dataset."
    TIMESERIES_DF_INVALID_ARG_ONLY_ONE_ARG_REQUIRED = \
        "Only one of the two parameters [{arg1}] and [{arg2}] should be set. " \
        "Please provide at least either one of them, but not both."
    TIMESERIES_DF_INVALID_ARG_PARAM_INCOMPATIBLE = \
        "The parameter [{param}] is incompatible with time-series when using rolling-origin cross validation. " \
        "Please remove the parameter."
    TIMESERIES_DF_INV_VAL_ALL_GRAINS_CONTAIN_SINGLE_VAL = \
        "All time series in the dataframe contain less than 2 values."
    TIMESERIES_DF_INV_VAL_CANNOT_CONVERT_TO_PD_TIME_IDX = \
        "Cannot convert the time column values into type pd.DateTimeIndex.\n" \
        "Review the values in the column to ensure that each entry is in a datetime format."
    TIMESERIES_DF_INV_VAL_COL_OF_GRP_NAME_IN_TM_IDX = \
        "Cannot return group column because some of the columns in group_colnames are part of the index."
    TIMESERIES_DF_INV_VAL_OF_NUMBER_TYPE_IN_TEST_DATA = \
        "Cannot convert the column [{column}] to float type, which was identified as numerical data type. " \
        "At least one of the records in this column is not a valid number. " \
        "Please check the validation, training or the inferencing data."
    TIMESERIES_DF_INV_VAL_TM_IDX_WRONG_TYPE = \
        "The time index is neither pd.Timestamp/pd.DateTimeIndex nor pd.Period/pd.PeriodIndex"
    TIMESERIES_DF_MISSING_COLUMN = \
        "One or more columns for [{column_names}] were not found in the dataframe.\n" \
        "Please check that these columns are present in your dataframe. You can run `<X>.columns`."
    TIMESERIES_DF_MULTI_FREQUENCIES_DIFF = "More than one series in the input data, and their frequencies differ. " \
                                           "Please separate series by frequency and build separate models. " \
                                           "If frequencies were incorrectly inferred, please " \
                                           "fill in gaps in series. If the dataset needs to be aggregated, " \
                                           "please provide freq and target_aggregation_function parameters " \
                                           "and run AutoML again."
    TIMESERIES_DF_MULTI_FREQUENCIES_DIFF_DATA = "More than one series in the input data, and their " \
                                                "frequencies differ. Please separate series by frequency " \
                                                "and build separate models. If frequencies were incorrectly " \
                                                "inferred, please fill in gaps in series. If the dataset needs " \
                                                "to be aggregated, please provide freq and " \
                                                "target_aggregation_function parameters and run AutoML again. " \
                                                "Frequency counts: {freq_counts_dict}, sample series per frequency: "\
                                                "{freq_to_series_dict}."
    TIMESERIES_DF_OUT_OF_PHASE = "Scoring data frequency is not consistent with training " \
                                 "data frequency or has different phase."
    TIMESERIES_DF_TM_COL_CONTAINS_NAT_ONLY = "The time column {time_column_name} is empty. " \
                                             "Please make sure the column contains valid timestamp values"
    TIMESERIES_DF_TRAINING_VALID_DATA_NOT_CONTIGUOUS = \
        "Training and validation data are not contiguous in time series identifier [{grain}]."
    TIMESERIES_DF_UNIQUE_TARGET_VALUE_GRAIN = "The input data contains time series with only unique target " \
                                              "values. One such series that displays this behavior is the time " \
                                              "series {grain}. Please only provide series " \
                                              "with non-unique target values."
    TIMESERIES_DF_UNSUPPORTED_TYPE_OF_LEVEL = "Unsupported type given for level."
    TIMESERIES_DF_WRONG_TYPE_ERROR = "The type of the timeseries dataframe is incorrect."
    TIMESERIES_DF_WRONG_TYPE_OF_GRAIN_COLUMN = "Each time series identifier column must contain data of one type, " \
                                               "The column {column} contains {num_types} data types. Please correct " \
                                               "the contents of time series identifier column or set the column " \
                                               "purpose to convert it to correct type and run the experiment " \
                                               "again."
    TIMESERIES_DF_WRONG_TYPE_OF_LEVEL_VALUES = "Unsupported types [{actual_type}] given for level values. " \
                                               "Expected types must be all strings or all ints."
    TIMESERIES_DF_WRONG_TYPE_OF_TIME_COLUMN = "The type of time column must be one of the following: {column_types}"
    TIMESERIES_DF_WRONG_TYPE_OF_VALUE_COLUMN = "Non numeric value(s) were encountered in the target column. " \
                                               "Please check the data and run the experiment again."
    TIMESERIES_EMPTY_SERIES = "One of the series is empty after dropping all NaNs. Please inspect your data."
    TIMESERIES_FREQUENCY_NOT_SUPPORTED = "The training data has a frequency of [{freq}]. " \
                                         "Lagging and rolling window features are not supported for " \
                                         "frequencies of less than 1 minute. Please follow one of the " \
                                         "suggestions and resubmit your experiment.\n" \
                                         "1) Disable lagging and rolling window settings\n" \
                                         "2) Specify the 'freq' and 'target_aggregation_function' " \
                                         "to aggregate to a frequency of 1 minute or greater " \
                                         "(only supported in the SDK)\n" \
                                         "3) Aggregate the training data to a frequency of at " \
                                         "least 1 minute"
    TIMESERIES_GRAIN_ABSENT = "One of the time series identifiers is not presented."
    TIMESERIES_GRAIN_ABSENT_NO_DATA_CONTEXT = \
        "The time series with ID {grain} was not present in the training set. " \
        "Please set short_series_handling_configuration parameter or " \
        "add the missing time series to the training set and train the model again."
    TIMESERIES_GRAIN_ABSENT_NO_GRAIN_IN_TRAIN = \
        "One of time series [{grain}] was not present in the training dataset. " \
        "Please remove it from the prediction dataset to proceed."
    TIMESERIES_GRAIN_ABSENT_NO_LAST_DATE = "The last training date was not provided." \
                                           "One of time series in scoring set was not present in training set."
    TIMESERIES_GRAIN_ABSENT_VALID_TRAIN_VALID_DAT = \
        "Training and validation datasets contain different sets of time series identifiers.\n" \
        "Time series identifier [{grains}] found in [{dataset_contain}] data but not in the " \
        "[{dataset_not_contain}] data."
    TIMESERIES_INPUT_IS_NOT_TSDF = "The input should be an instance of TimeSeriesDataFrame."
    TIMESERIES_INSUFFICIENT_DATA = \
        "The series provided for given time series identifiers ({grains}) is insufficient" \
        " for a valid training with CV ({num_cv}), step size [{cv_step_size}], " \
        "forecast horizon ({max_horizon}), lags " \
        "({lags}) and rolling window size ({window_size}). Please either consider adding " \
        "more data points, dropping the identifier(s), or reducing one of max horizon, " \
        "the number of cross validations, lags or rolling window size."
    TIMESERIES_INSUFFICIENT_DATA_FORECAST = "The series provided for given time series identifiers " \
                                            "({grains}) is insufficient for {operation} " \
                                            "with forecast horizon ({max_horizon}), lags " \
                                            "({lags}) and rolling window size ({window_size}). " \
                                            "Please either consider adding more data points " \
                                            "or dropping these time series / grains."
    TIMESERIES_INSUFFICIENT_DATA_FOR_ALL_GRAINS = \
        "All the timeseries in the dataset has insufficient data." \
        "Each timeseries should have at least [{min_points}] for forecast horizon [{forecast_horizon}]." \
        "Increase the data for every time series or use smaller max_horizon or enable short series handling."
    TIMESERIES_INSUFFICIENT_DATA_FOR_CV_OR_HORIZON = "Series is too short for the requested number of CV folds, " \
                                                     "CV step size " \
                                                     "or requested horizon. Cannot have (n_splits - 1)*n_step + 1 + " \
                                                     "num_horizon = {cur_samples} greater than the number of samples" \
                                                     ": {num_samples}."
    TIMESERIES_INSUFFICIENT_DATA_VALIDATE_TRAIN_DATA = \
        "Insufficient data was provided for the specified training configurations. " \
        "The data points should have at least [{min_points}] for a valid training with cv [{n_cross_validations}], " \
        "cross validation step size [{cv_step_size}], forecast horizon [{max_horizon}], "\
        "lags [{lags}] and rolling window size [{window_size}]. " \
        " The current dataset only has [{shape}] points. Reduce the values of these settings to train."
    TIMESERIES_INVALID_DATE_OFFSET_TYPE = "The dataset frequency must be a string or None. The string must " \
                                          "represent a pandas date offset. Please refer to documentation on " \
                                          "freq parameter: {freq_url}"
    TIMESERIES_INVALID_PIPELINE = "Invalid forecasting pipeline found."
    TIMESERIES_INVALID_PIPELINE_EXECUTION_TYPE = "The execution type [{exec_type}] specified is " \
                                                 "invalid or not supported."
    TIMESERIES_INVALID_TIMESTAMP = "One or more rows in the input dataset have an invalid date/time. Please ensure " \
                                   "you can run `pandas.to_datetime(X)` without any errors."
    TIMESERIES_INVALID_TYPE_IN_PIPELINE = "Invalid types found in pipeline with steps [{steps}]."
    TIMESERIES_INVALID_VALUE_IN_PIPELINE = "Invalid values found in pipeline with steps [{steps}]."
    TIMESERIES_LAGGING_NANS = \
        "Unable to create cross validation folds. This error can be caused by missing values " \
        "(or NaNs) at the end of the dataset. Increase the forecast horizon, or turn off target lags and rolling " \
        "windows to continue."
    TIMESERIES_LEADING_NANS = "Unable to create cross validation folds. This error can be caused by missing values " \
                              "(or NaNs) at the beginning of the dataset. Disable the target lags and " \
                              "rolling window size to continue."
    TIMESERIES_MAX_HORIZON_WITH_TIMECOLUMN_VAL_OUTOFRANGE = \
        "The provided max_horizon [{max_horizon}] along with the values of time index column " \
        "represents a time value out of usable range."
    TIMESERIES_MISSING_VALUES_IN_Y = "All of the values in y_pred are NA or missing. At least one value of " \
                                     "y_pred should not be NA or missing."
    TIMESERIES_NAN_GRAIN_VALUES = "The time series identifier {time_series_id} contains empty values. " \
                                  "Please fill these values and run the AutoML job again."
    TIMESERIES_NON_CONTIGUOUS_TARGET_COLUMN = "The y values contain non-contiguous NaN values. If it is expected, " \
                                              "please run forecast() with ignore_data_errors=True. In this case the " \
                                              "NaNs before the time-wise latest NaNs will be imputed."
    TIMESERIES_NOTHING_TO_PREDICT = "Actual values are present for all times in the input dataframe - there is " \
                                    "nothing to forecast. Please set 'y' values to np.NaN for times where you " \
                                    "need a forecast."
    TIMESERIES_NO_DATA_CONTEXT = "No y values were provided. We expected non-null target values as prediction " \
                                 "context because there is a gap between train and test and the forecaster depends " \
                                 "on previous values of target. If it is expected, please run forecast() with " \
                                 "ignore_data_errors=True. In this case the values in the gap will be imputed."
    TIMESERIES_NO_USABLE_GRAINS = "The forecasting data set does not contain time series identifiers, used " \
                                  "in training data, which results in empty forecast. Please check the " \
                                  "data and run the experiment again."
    TIMESERIES_ONE_POINT_PER_GRAIN = "Could not determine the data set time frequency. " \
                                     "Possibly all series in the data set have one row and no freq parameter was " \
                                     "provided. Please provide the freq (forecast frequency) " \
                                     "parameter or review the time_series_id_column_names setting " \
                                     "to decrease the number of time series."
    TIMESERIES_REFERENCE_DATES_MISALIGNED = "Reference dates are misaligned. Expected dates on grid {date_grid}"
    TIMESERIES_RESERVED_COLUMN = "Column name {col} is in the reserved column names list, " \
                                 "please change that column name."
    TIMESERIES_TIME_COL_NAME_OVERLAP_ID_COL_NAMES = \
        "Time column name [{time_column_name}] is present in the time series identifier columns. " \
        "Please remove it from time series identifiers list."
    TIMESERIES_TIME_IDX_DATES_MISALIGNED = "Time index dates are misaligned. Expected dates on grid {time_index}"
    TIMESERIES_TRANS_CANNOT_INFER_FREQ = "The freq cannot be inferred. Please provide freq argument."
    TIMESERIES_TYPE_MISMATCH_DROP_FULL_CV = "The dataset contains column(s) which have values only at the end " \
                                            "of the dataset: {columns}. Please remove these column(s) and run " \
                                            "the AutoML experiment again."
    TIMESERIES_TYPE_MISMATCH_FULL_CV = "Detected multiple types for columns {columns}. Please set " \
                                       "FeaturizationConfig.column_purposes to force consistent types."
    TIMESERIES_WRONG_COLUMNS_IN_TEST_SET = "The scoring data set does not contain columns on which " \
                                           "the model was trained. " \
                                           "Columns not present in the test set: {train_cols}."
    TIMESERIES_WRONG_SHAPE_DATA_EARLY_DESTINATION = \
        "Input prediction data X_pred or input forecast_destination contains dates " \
        "prior to the latest date in the training data. " \
        "Please remove prediction rows with datetimes in the training date range " \
        "or adjust the forecast_destination date."
    TIMESERIES_WRONG_SHAPE_DATA_SIZE_MISMATCH = "The length of '{var1_name}' [{var1_len}] is different from " \
                                                "the '{var2_name}' length [{var2_len}]."
    TIME_COLUMN_VALUE_OUT_OF_RANGE = "Column '{column_name}' has a date or time value that is out of usable range. " \
                                     "Please drop any rows with date or time less than {min_timestamp} or greater " \
                                     "than {max_timestamp}."
    TRAINING_DATA_COLUMNS_INCONSISTENT = "For {partition_name} in the dataset, we have found the following issues:\n" \
                                         "{col_in_expected_msg}\n{col_in_input_msg}"
    TRANSFORMER_Y_MIN_GREATER = "{transformer_name} error. 'y_min' is greater than the observed minimum in 'y'. " \
                                "Please consider either clipping 'y' to the domain, or pass safe=True during " \
                                "transformer initialization."
    UNHASHABLE_VALUE_IN_DATA = "The column(s) [{column_names}] in the input dataset cannot be " \
                               "pre-processed. This is usually caused by an un-hashable value in one of the " \
                               "cells (e.g. a numpy array). Please inspect your data."
    UNRECOGNIZED_FEATURES = "All columns were automatically detected to be dropped by AutoML as no useful " \
                            "information could be inferred from the input data. The detected column purposes are the" \
                            " following,\n{column_drop_reasons}\nPlease either inspect your input data or " \
                            "use featurization config to give hints about the desired data transformation."

    XGBOOST_ALGOS_ALLOWED_BUT_NOT_INSTALLED = "Only XGBoost model is configured as an allowed model, but " \
                                              "xgboost is not installed. Allow additional models, remove " \
                                              "XGBoost from the allowed_models list, or run " \
                                              "'pip install xgboost=={version}."
    # endregion

    # region SystemErrorStrings
    ARTIFACT_UPLOAD_FAILURE = "Failed when trying to upload contents to artifact store." \
                              "Please retry the experiment or contact support."
    AUTOML_INTERNAL = "Encountered an internal AutoML error. Error Message/Code: {error_details}"
    AUTOML_INTERNAL_LOG_SAFE = "Encountered an internal AutoML error. Error Message/Code: {error_message:log_safe}. " \
                               "Additional Info: {error_details}"
    AUTOML_VISION_INTERNAL = "Encountered an internal AutoML Image error. Error Message/Code: {error_details}. " \
                             "Traceback: {traceback:log_safe}. Additional information: {pii_safe_message:log_safe}."
    DATA = "Encountered an error while reading or writing the Dataset. Error Message/Code: {error_details}"
    FORECASTING_ARIMA_NO_MODEL = "Fitting AutoArima model failed on one grain."
    FORECASTING_EXPOSMOOTHING_NO_MODEL = "Couldn't select a model on time series identifier {times_series_grain_id}." \
                                         " All fit from the Exponential Smoothing models failed."
    SERVICE = "Encountered an error while communicating with the service. Error Message/Code: {error_details}"
    TEXTDNN_MODEL_DOWNLOAD_FAILED = "Encountered an internal AutoML error. \
                                     Exception raised while initializing {transformer:log_safe} model for text dnn.\
                                     Please try the experiment again, and contact support if the error persists. \
                                     Error Message/Code: {error_details}"
    # endregion
