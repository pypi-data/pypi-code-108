# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Score images from model produced by another run."""

import argparse
import logging
import torch

from azureml.train.automl import constants
from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals, ScoringLiterals
from azureml.automl.dnn.nlp.ner.inference.score import score
from azureml.automl.dnn.nlp.common import _utils

logger = logging.getLogger(__name__)


def _make_arg(arg_name: str) -> str:
    return "--{}".format(arg_name)


def _get_default_device():
    return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def main():
    """Execute script only when called and not when imported."""
    parser = argparse.ArgumentParser()
    parser.add_argument(_make_arg(ScoringLiterals.RUN_ID),
                        help='run id of the experiment that generated the model')
    parser.add_argument(_make_arg(ScoringLiterals.EXPERIMENT_NAME),
                        help='experiment that ran the run which generated the model')
    parser.add_argument(_make_arg(ScoringLiterals.OUTPUT_FILE),
                        help='path to output file')
    parser.add_argument(_make_arg(ScoringLiterals.INPUT_DATASET_ID),
                        help='input_dataset_id')
    parser.add_argument(_make_arg(ScoringLiterals.LOG_OUTPUT_FILE_INFO),
                        help='log output file debug info', type=bool, default=False)

    args, unknown = parser.parse_known_args()

    task_type = constants.Tasks.TEXT_NER
    _utils._set_logging_parameters(task_type, args)

    if unknown:
        logger.info("Got unknown args, will ignore them")

    score(
        args.run_id,
        args.input_dataset_id,
        DataLiterals.NER_DATA_DIR,
        OutputLiterals.OUTPUT_DIR
    )


if __name__ == "__main__":
    # Execute only if run as a script
    main()
