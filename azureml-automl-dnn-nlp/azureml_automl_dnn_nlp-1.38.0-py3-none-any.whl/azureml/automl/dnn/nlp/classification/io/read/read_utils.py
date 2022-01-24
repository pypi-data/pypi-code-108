# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utility functions to load the final model and vectorizer during inferencing"""

import logging
import os
import pickle

from typing import Optional

from azureml.automl.dnn.nlp.common.constants import OutputLiterals
from azureml.automl.dnn.nlp.classification.multilabel.model_wrapper import ModelWrapper
from azureml.core.run import Run


_logger = logging.getLogger(__name__)


def load_model_wrapper(run_object: Run, artifacts_dir: Optional[str] = None) -> ModelWrapper:
    """Function to load model (in form of model wrapper) from the training run

    :param run_object: Run object
    :param artifacts_dir: artifacts directory
    :return: model wrapper containing pytorch mode, tokenizer, vectorizer
    """
    _logger.info("Loading model from artifacts")

    if artifacts_dir is None:
        artifacts_dir = OutputLiterals.OUTPUT_DIR

    run_object.download_file(os.path.join(artifacts_dir, OutputLiterals.MODEL_FILE_NAME),
                             output_file_path=OutputLiterals.MODEL_FILE_NAME)

    _logger.info("Finished loading model from training output")

    with open(OutputLiterals.MODEL_FILE_NAME, "rb") as f:
        model = pickle.load(f)
    return model
