# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Code generation related constants."""


class CodeGenConstants:
    TagName = "_aml_system_codegen"
    ScriptFilename = "script.py"
    ScriptRunNotebookFilename = "script_run_notebook.ipynb"
    OutputPath = "outputs/generated_code/"
    ScriptOutputPath = OutputPath + ScriptFilename
    ScriptRunNotebookOutputPath = OutputPath + ScriptRunNotebookFilename
    DefaultComputeSku = "STANDARD_DS4_V2"


class FunctionNames:
    SETUP_INSTRUMENTATION_FUNC_NAME = "setup_instrumentation"
    GET_TRAIN_DATASET_FUNC_NAME = "get_training_dataset"
    GET_VALID_DATASET_FUNC_NAME = "get_validation_dataset"
    PREPARE_DATA_FUNC_NAME = "prepare_data"
    FEATURIZE_FUNC_NAME = "generate_data_transformation_config"
    PREPROC_FUNC_NAME = "generate_preprocessor_config"
    MODEL_FUNC_NAME = "generate_algorithm_config"
    BUILD_MODEL_FUNC_NAME = "build_model_pipeline"
    TRAIN_MODEL_FUNC_NAME = "train_model"
    CALCULATE_METRICS_NAME = "calculate_metrics"
