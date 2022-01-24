# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Functions to write the model at the end of training."""

import os
import shutil

from azureml.automl.dnn.vision.common.constants import ArtifactLiterals


def write_scoring_script(output_dir):
    """Writes the scoring and featurization scripts.

    :param output_dir: path to output directory
    :type output_dir: str
    """
    os.makedirs(output_dir, exist_ok=True)

    # Save score and featurize script
    dirname = os.path.dirname(os.path.abspath(__file__))
    shutil.copy(os.path.join(dirname, ArtifactLiterals.SCORE_SCRIPT),
                os.path.join(output_dir, ArtifactLiterals.SCORE_SCRIPT))
    shutil.copy(os.path.join(dirname, ArtifactLiterals.FEATURIZE_SCRIPT),
                os.path.join(output_dir, ArtifactLiterals.FEATURIZE_SCRIPT))
