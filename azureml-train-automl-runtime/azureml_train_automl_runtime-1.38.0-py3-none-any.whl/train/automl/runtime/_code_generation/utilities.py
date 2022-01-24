# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Code gen related utility methods."""


import logging
from typing import Any, Optional, Tuple

from azureml.core import Run
from sklearn.pipeline import Pipeline

from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.featurization import DataTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries import TimeSeriesTransformer
from azureml.train.automl._constants_azureml import RunState
from azureml.train.automl.runtime._code_generation import code_generator, notebook_generator
from azureml.train.automl.runtime._code_generation.constants import CodeGenConstants

logger = logging.getLogger(__name__)


def generate_model_code_and_notebook(current_run: Run, pipeline: Optional[Any] = None) -> None:
    """
    Given a child run, generate the code and notebook for the outputted model and upload them as artifacts.
    """
    try:
        logger.info("Generating code for the trained model.")
        code = code_generator.generate_full_script(current_run, pipeline)

        with open("script.py", "w") as f:
            f.write(code)

        current_run.upload_file(CodeGenConstants.ScriptOutputPath, "script.py")
        logger.info(f"Script has been generated, output saved to {CodeGenConstants.ScriptOutputPath}")

        Contract.assert_value(current_run.parent, "parent")
        notebook = notebook_generator.generate_script_run_notebook(
            current_run, environment=current_run.get_environment()
        )
        with open("script_run_notebook.ipynb", "w") as f:
            f.write(notebook)
        current_run.upload_file(CodeGenConstants.ScriptRunNotebookOutputPath, "script_run_notebook.ipynb")
        logger.info(
            f"Script has been generated, output saved to {CodeGenConstants.ScriptRunNotebookOutputPath}"
        )

        try:
            # Quickly check for errors in the script
            _codegen_utilities.check_code_syntax(code)
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            logger.warning(
                "Code generation encountered an error when checking output. The generated code may "
                "require some manual editing to work properly."
            )

        current_run.set_tags({CodeGenConstants.TagName: RunState.COMPLETE_RUN})
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        logger.warning("Code generation failed; skipping.")
        current_run.set_tags({CodeGenConstants.TagName: RunState.FAIL_RUN})


def get_input_datasets(parent_run: Run) -> Tuple[str, Optional[str]]:
    """
    Given a parent run, fetch the IDs of the training and validation datasets, if present.

    :param parent_run: the run to fetch IDs from
    :return: a tuple of (training, validation) dataset IDs
    """
    parent_run_details = parent_run.get_details()
    input_datasets = parent_run_details.get("inputDatasets", [])
    training_dataset_id = None
    validation_dataset_id = None

    for input_dataset in input_datasets:
        consumption_block = input_dataset.get("consumptionDetails", {})
        dataset_name = consumption_block.get("inputName", None)

        if dataset_name == "training_data":
            training_dataset_id = input_dataset["dataset"].id
        elif dataset_name == "validation_data":
            validation_dataset_id = input_dataset["dataset"].id

    assert training_dataset_id is not None, "No training dataset found"
    return training_dataset_id, validation_dataset_id


def pipeline_has_preprocessor(pipeline: Pipeline) -> bool:
    """
    Check whether this pipeline has a preprocessor.

    :param pipeline: the pipeline to check
    :return: True if a preprocessor is present, False otherwise
    """
    return len(pipeline.steps) > 1 and not isinstance(pipeline.steps[-2][1], (DataTransformer, TimeSeriesTransformer))


def pipeline_has_featurizer(pipeline: Pipeline) -> bool:
    """
    Check whether this pipeline has a featurizer.

    :param pipeline: the pipeline to check
    :return: True if a featurizer is present, False otherwise
    """
    return len(pipeline.steps) > 1 and isinstance(pipeline.steps[0][1], (DataTransformer, TimeSeriesTransformer))
