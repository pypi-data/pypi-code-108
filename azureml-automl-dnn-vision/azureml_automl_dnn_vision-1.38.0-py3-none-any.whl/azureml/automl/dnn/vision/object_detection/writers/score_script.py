# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Score images from model produced by another run."""

import argparse
import ast

from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.constants import SettingsLiterals
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.parameters import add_task_agnostic_scoring_parameters
from azureml.automl.dnn.vision.object_detection.writers.score import score
from azureml.automl.dnn.vision.object_detection.common.constants import ModelLiterals, \
    MaskToolsLiterals, MaskToolsParameters, inference_settings_defaults, TilingLiterals, \
    MaskImageExportLiterals, MaskImageExportParameters

logger = get_logger(__name__)


TASK_TYPE = "%%TASK_TYPE%%"


@utils._exception_handler
def main(raw_args=None):
    """Wrapper method to execute script only when called and not when imported.

    :param raw_args: a list of arguments to pass to argparse. If None, the command line arguments are parsed.
                     Useful for testing this method.
    :type raw_args: list
    """

    parser = argparse.ArgumentParser(description="Object detection scoring", allow_abbrev=False)
    add_task_agnostic_scoring_parameters(parser, inference_settings_defaults)

    parser.add_argument(utils._make_arg(SettingsLiterals.OUTPUT_DATASET_TARGET_PATH),
                        help='Datastore target path for output dataset files')

    # Model Settings
    # should not set defaults for those model settings arguments to use those from training settings by default
    parser.add_argument(utils._make_arg(ModelLiterals.MIN_SIZE), type=int,
                        help="Minimum size of the image to be rescaled before feeding it to the backbone")

    parser.add_argument(utils._make_arg(ModelLiterals.MAX_SIZE), type=int,
                        help="Maximum size of the image to be rescaled before feeding it to the backbone")

    parser.add_argument(utils._make_arg(ModelLiterals.BOX_SCORE_THRESH), type=float,
                        help="During inference, only return proposals with a classification score \
                        greater than box_score_thresh")

    parser.add_argument(utils._make_arg(ModelLiterals.BOX_NMS_THRESH), type=float,
                        help="NMS threshold for the prediction head. Used during inference")

    parser.add_argument(utils._make_arg(ModelLiterals.BOX_DETECTIONS_PER_IMG), type=int,
                        help="Maximum number of detections per image, for all classes.")

    # Masktool settings for instance segmentation
    parser.add_argument(utils._make_arg(MaskToolsLiterals.MASK_PIXEL_SCORE_THRESHOLD), type=float,
                        help="Score cutoff for considering a pixel as in object \
                        when converting a mask to polygon points",
                        default=MaskToolsParameters.DEFAULT_MASK_PIXEL_SCORE_THRESHOLD)

    parser.add_argument(utils._make_arg(MaskToolsLiterals.MAX_NUMBER_OF_POLYGON_POINTS), type=int,
                        help="Maximum number of (x, y) coordinate pairs in polygon \
                        after converting from a mask",
                        default=MaskToolsParameters.DEFAULT_MAX_NUMBER_OF_POLYGON_POINTS)

    # Settings for exporting masks as images
    parser.add_argument(utils._make_arg(MaskImageExportLiterals.EXPORT_AS_IMAGE), type=bool,
                        help="Export masks as images",
                        default=MaskImageExportParameters.DEFAULT_EXPORT_AS_IMAGE)

    parser.add_argument(utils._make_arg(MaskImageExportLiterals.IMAGE_TYPE), type=str,
                        help="Type of image to export mask as (options are jpg, png, bmp)",
                        default=MaskImageExportParameters.DEFAULT_IMAGE_TYPE)

    # Tiling settings
    # should not set defaults for those tiling settings arguments to use those from training settings by default
    # Note that we use ast.literal_eval here to keep it consistent with arguments passed for training in runner.py.
    parser.add_argument(utils._make_arg(TilingLiterals.TILE_GRID_SIZE), type=ast.literal_eval,
                        help="The tile grid size to use for tiling the image during inference. \
                        Should be a tuple of two integers passed as a string. Example: --tile_grid_size \"(3, 2)\"")
    parser.add_argument(utils._make_arg(TilingLiterals.TILE_OVERLAP_RATIO), type=float,
                        help="Overlap ratio between adjacent tiles in each dimension")
    parser.add_argument(utils._make_arg(TilingLiterals.TILE_PREDICTIONS_NMS_THRESH), type=float,
                        help="The iou threshold to use to perform nms while merging predictions from tiles and \
                        image.")

    args, unknown = parser.parse_known_args()
    args_dict = vars(args)

    # Set up logging
    task_type = TASK_TYPE
    utils._set_logging_parameters(task_type, args_dict)

    if unknown:
        logger.info("Got unknown args, will ignore them.")

    device = utils._get_default_device()
    settings = utils._merge_dicts_with_not_none_values(args_dict, inference_settings_defaults)

    score(args.run_id, device=device, settings=settings,
          experiment_name=args.experiment_name,
          output_file=args.output_file, root_dir=args.root_dir,
          image_list_file=args.image_list_file,
          output_dataset_target_path=args.output_dataset_target_path,
          input_dataset_id=args.input_dataset_id,
          validate_score=args.validate_score,
          log_output_file_info=args.log_output_file_info)


if __name__ == "__main__":
    # execute only if run as a script
    main()
