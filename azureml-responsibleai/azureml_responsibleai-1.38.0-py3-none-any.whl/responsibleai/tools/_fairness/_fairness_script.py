# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


"""Worker script for creating and uploading Fairness widgets
"""

import argparse
import joblib
import json

from azureml.core import Dataset, Run
from azureml.core.model import Model

from azureml.responsibleai.tools._fairness import upload_fairness_local
from azureml.responsibleai.common._constants import LoggingConstants
from azureml.responsibleai.common._loggerfactory import _LoggerFactory, track, collect_run_info, collect_model_info

_logger = _LoggerFactory.get_logger(__name__)


def _get_logger():
    return _logger


PREDICTION_TYPES = ["binary_classification", "probability", "regression"]


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--title', type=str, required=True,
                        help="Title of this fairness widget instance")

    parser.add_argument('--datastore', type=str, required=True,
                        help='Name of datastore for storing Artifacts')

    parser.add_argument('--model_id', type=str, required=True,
                        help="Model id in AzureML")
    parser.add_argument('--model_loader_file', type=str, required=True,
                        help="Model loader PKL file")

    parser.add_argument('--dataset_id', type=str, required=True,
                        help="Dataset ID")
    parser.add_argument('--X_column_names', type=str, required=True,
                        help="JSON string list of column names for X")
    parser.add_argument('--y_column_name', type=str, required=True,
                        help="Column name for y")
    parser.add_argument('--A_column_names', type=str, required=True,
                        help="JSON string list of column names for A")

    parser.add_argument('--prediction_type', type=str, required=True,
                        help="What sort of predictions are present",
                        choices=PREDICTION_TYPES)

    return parser


@track(_get_logger, custom_dimensions={'app_name': 'FairnessRemoteJob'}, activity_type=LoggingConstants.REMOTE_JOB)
def execute():
    args = get_parser().parse_args()

    my_run = Run.get_context()

    try:
        # model may not be able to be loaded causing exception
        collect_run_info(_logger, "Starting fairnress remote job at {}".format(__file__), [my_run])
        collect_model_info(_logger,
                           "Starting fairness {} model container id collection".format(__file__),
                           [Model(my_run.experiment.workspace, id=args.model_id)])
    except Exception:
        pass

    loader = joblib.load(args.model_loader_file)

    ds = Dataset.get_by_id(
        workspace=my_run.experiment.workspace, id=args.dataset_id)
    X_column_names = json.loads(args.X_column_names)
    y_column_name = args.y_column_name
    A_column_names = json.loads(args.A_column_names)

    upload_fairness_local(my_run,
                          args.title,
                          args.datastore,
                          args.model_id,
                          loader,
                          ds,
                          X_column_names,
                          y_column_name,
                          A_column_names,
                          args.prediction_type)


if __name__ == '__main__':
    execute()
