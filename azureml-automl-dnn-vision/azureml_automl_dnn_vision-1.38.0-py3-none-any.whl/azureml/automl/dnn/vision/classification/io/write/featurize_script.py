# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Featurize images from model produced by another run."""

import argparse

from azureml.automl.dnn.vision.classification.common.constants import ModelLiterals, \
    inference_settings_defaults
from azureml.automl.dnn.vision.classification.inference.score import featurize
from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.parameters import add_task_agnostic_scoring_parameters
from azureml.train.automl import constants

logger = get_logger(__name__)


@utils._exception_handler
def main():
    """Wrapper method to execute script only when called and not when imported."""
    parser = argparse.ArgumentParser(description="Image classification featurizing", allow_abbrev=False)
    add_task_agnostic_scoring_parameters(parser, inference_settings_defaults)

    # Model Settings
    # should not set defaults for those model settings arguments to use those from training settings by default
    parser.add_argument(utils._make_arg(ModelLiterals.RESIZE_SIZE), type=int,
                        help="Image size to which to resize before cropping for given dataset")

    parser.add_argument(utils._make_arg(ModelLiterals.CROP_SIZE), type=int,
                        help="Image crop size which is input to your neural network for given dataset")

    args, unknown = parser.parse_known_args()
    args_dict = vars(args)

    # Set up logging
    task_type = constants.Tasks.IMAGE_CLASSIFICATION
    utils._set_logging_parameters(task_type, args_dict)

    if unknown:
        logger.info("Got unknown args, will ignore them.")

    device = utils._get_default_device()
    settings = utils._merge_dicts_with_not_none_values(args_dict, inference_settings_defaults)

    featurize(args.run_id, device=device, settings=settings,
              experiment_name=args.experiment_name,
              output_file=args.output_file,
              root_dir=args.root_dir,
              image_list_file=args.image_list_file,
              input_dataset_id=args.input_dataset_id,
              log_output_file_info=args.log_output_file_info)


if __name__ == "__main__":
    # execute only if run as a script
    main()
