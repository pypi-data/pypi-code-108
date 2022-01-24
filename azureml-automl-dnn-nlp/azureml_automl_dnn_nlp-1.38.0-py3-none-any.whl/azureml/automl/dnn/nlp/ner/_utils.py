# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""utilities for NER task."""

import logging
import os
import uuid
from typing import Any, Dict, List

from azureml.automl.runtime.shared.score import constants
from azureml.core.run import Run

_logger = logging.getLogger(__name__)


def get_labels(labels_file_path: str) -> List[str]:
    """
    Retrieve labels from saved labels file
    :param labels_file_path:
    :return: list of labels
    """
    """Get labels."""
    if labels_file_path:
        with open(labels_file_path, "r") as f:
            readlines = f.read()
            labels = readlines.splitlines()
        if "O" not in labels:
            labels = ["O"] + labels
        if "" in labels:
            labels.remove("")
        return labels
    else:
        return ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]


def write_predictions_to_file(
        predictions_file_path: str,
        test_file_path: str,
        preds_list: List,
        preds_proba_list: List
) -> None:
    """
    Write predictions to file.
    :param predictions_file: predictions file to write
    :param test_input_reader: input text file reader
    :param preds_list: predictions list
    :param preds_proba_list: predictions proba list
    :return:
    """
    with open(predictions_file_path, "w") as writer:
        with open(test_file_path, "r") as f:
            example_id = 0
            lines = f.readlines()
            for line in lines:
                if line.startswith("-DOCSTART-") or line == "" or line == "\n":
                    writer.write(line)
                    if not preds_list[example_id]:
                        example_id += 1
                elif preds_list[example_id]:
                    output_line = line.split()[0] + " " + preds_list[example_id].pop(0) + " "\
                        + str(preds_proba_list[example_id].pop(0)) + "\n"
                    writer.write(output_line)
                else:
                    _logger.warning("Maximum sequence length exceeded: No prediction available for this line.")

    _logger.info("Test predictions saved")


def log_metrics(
        run: Run,
        results: Dict
) -> None:
    """
    Log metric information.
    :param run: run context to log metrics to
    :param results: dictionary containing metrics
    :return:
    """
    for metric_name in results:
        if metric_name in constants.TEXT_NER_SET:
            run.log(metric_name, results[metric_name])
    _logger.info("Metrics result saved")


def create_unique_dir(name: str) -> str:
    """
    Creates a directory with a unique id attached.
    :param name: name of the unique dir. The final name will be of format name_{some unique id}
    """
    unique_id = uuid.uuid1().fields[0]
    dir_name = "{}_{}".format(name, unique_id)
    os.makedirs(dir_name, exist_ok=True)
    return dir_name


def remove_metric_prefix(
        metrics: Dict[str, Any],
        prefix: str
) -> Dict[str, Any]:
    """
    Remove unnecessary prefix added by huggingface code
    :param metrics: dictionary containing metrics info
    :param prefix: prefix to remove
    :return: dictionary containing new metrics name
    """
    metrics_key = list(metrics.keys())
    for key in metrics_key:
        if key.startswith(prefix):
            metrics[key[len(prefix):]] = metrics.pop(key)
    return metrics
