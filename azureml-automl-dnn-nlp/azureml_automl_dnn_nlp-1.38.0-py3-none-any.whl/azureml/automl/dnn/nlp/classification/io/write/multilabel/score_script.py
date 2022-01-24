# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Score text dataset from model produced by training run."""

import argparse
import logging
import torch

from azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer import MultilabelInferencer
from azureml.automl.dnn.nlp.common._utils import _set_logging_parameters, get_run_by_id
from azureml.automl.dnn.nlp.common.constants import ScoringLiterals
from azureml.train.automl import constants


_logger = logging.getLogger(__name__)


def _make_arg(arg_name: str) -> str:
    return "--{}".format(arg_name)


def _get_default_device():
    return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def main():
    """Wrapper method to execute script only when called and not when imported."""
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
    parser.add_argument(_make_arg(ScoringLiterals.ENABLE_DATAPOINT_ID_OUTPUT),
                        help='inference output will contain only datapoint ID and predictions',
                        type=bool, default=False)

    args, unknown = parser.parse_known_args()

    task_type = constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL
    _set_logging_parameters(task_type, args)

    device = _get_default_device()

    train_run = get_run_by_id(args.run_id, args.experiment_name)

    inferencer = MultilabelInferencer(run=train_run, device=device)
    inferencer.score(args.input_dataset_id, args.enable_datapoint_id_output)

    return


if __name__ == "__main__":
    # Execute only if run as a script
    main()
