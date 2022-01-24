# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Functions for score script."""

import os

from azureml.train.automl import constants

from azureml.automl.dnn.vision.common.constants import ArtifactLiterals

TASK_TYPE_PLACEHOLDER = "%%TASK_TYPE%%"


def write_scoring_script(output_dir, score_script_dir=None,
                         task_type=constants.Tasks.IMAGE_OBJECT_DETECTION):
    """Writes the scoring script

    :param output_dir: Name of dir to save model files. If it does not exist, it will be created.
    :type output_dir: str
    :param score_script_dir: directory of score_script to be copied (defaults to current dir if None)
    :type score_script_dir: str
    :param task_type: Task type used in training.
    :type task_type: str
    """
    os.makedirs(output_dir, exist_ok=True)

    # Save score script with appropriate task_type.
    if score_script_dir is None:
        score_script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(score_script_dir, ArtifactLiterals.SCORE_SCRIPT)) as source_file:
        with open(os.path.join(output_dir, ArtifactLiterals.SCORE_SCRIPT), "w") as output_file:
            output_file.write(source_file.read().replace(TASK_TYPE_PLACEHOLDER, task_type))
