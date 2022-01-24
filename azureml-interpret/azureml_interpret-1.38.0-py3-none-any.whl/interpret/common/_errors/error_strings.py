# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class ErrorStrings:
    """
    All un-formatted error strings that accompany the common error codes for azureml-interpret.

    Dev note: Please keep this list sorted on keys.
    """

    CLASS_NUMBER_MISMATCH = "The number of classes provided ({actual}) does not match " \
                            "the expected number of classes ({expected})."
    DESERIALIZATION_FAILURE = "Could not deserialize the model due to an unexpected format."
    DIRECTORY_ALREADY_EXISTS = "A directory already exists at {path}. Please choose another path " \
                               "or set exist_ok=True to overwrite the existing contents."
    EVAL_DATA_SHAPE_MISMATCH = "The number of samples in the visualization data X ({X_length}) " \
                               "and y ({y_length}) does not match."
    EVAL_DATASET_MISSING = "An evaluation dataset is required to create an explanation."
    EXPERIMENT_MISSING_ID_AND_NAME = "The experiment does not have a valid ID or name."
    EXPLAIN_BEFORE_UPLOAD_CONFLICT = "The explain() method must be called before uploading explanations."
    EXPLANATION_NOT_FOUND = "No explanation asset could be found with ID {explanation_id}."
    EXPLANATION_FILTER_NOT_FOUND = "Explanation asset ID {explanation_id} was not found to match the " \
                                   "filter {filter_name}={filter_value}."
    EXPLANATION_FILTERS_NOT_FOUND = "Explanation asset ID {explanation_id} was not found to match the " \
                                    "supplied filters {filter_names}."
    EXPLANATION_TYPES_INVALID = "The argument 'explanation_types' must include one of the following " \
                                "explanation types: {explanation_types}."
    INIT_DATASET_MISSING = "An initialization dataset is required."
    INVALID_Y_TRUE_DIMENSION = "The true_ys input should be a one-dimensional array."
    MISSING_FEATURE_MAP_GETTING_RAW = "The 'feature_maps' argument is required when getting " \
                                      "raw importances from the engineered explanation."
    MODEL_NOT_KERAS = "The model being serialized by KerasSerializer must be one of [tf.keras.Model, " \
                      "keras.engine.sequential.Sequential, keras.models.Sequential, " \
                      "keras.engine.training.Model]"
    MODEL_NOT_SERIALIZABLE = "The model to be explained must be picklable or a custom serializer " \
                             "must be specified."
    OPTIONAL_DEPENDENCY_MISSING = "The dependency {dependency_name} is missing from the current environment."
    RAW_TRANSFORM_ARGUMENT_MISMATCH = "Either 'transformations' or 'feature_maps' should be passed, " \
                                      "but not both."
    SAMPLE_LIMIT_EXCEEDED = "The number of points supplied ({actual}) is greater " \
                            "than the supported maximum ({limit})."
    INVALID_EXPLANATION_DATA_TYPE = "Got unexpected type {actual}. Expecting {expected} type for explanations."
