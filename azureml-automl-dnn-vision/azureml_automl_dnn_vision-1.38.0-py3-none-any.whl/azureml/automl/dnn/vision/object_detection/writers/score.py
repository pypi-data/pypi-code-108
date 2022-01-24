# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Functions for inference using a trained model"""
import os
import time

import torch
from typing import Any, Dict, Optional

from ...common.average_meter import AverageMeter
from ...common.constants import ScoringLiterals, SettingsLiterals
from ...common.system_meter import SystemMeter
from ..common.object_detection_utils import _fetch_model_from_artifacts, _validate_score_run, \
    _write_dataset_file_line, _write_prediction_file_line, _write_masks_as_images
from ..models import detection
from ..trainer.train import move_images_to_device

from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.dataloaders import RobustDataLoader
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper
from azureml.automl.dnn.vision.common.logging_utils import clean_settings_for_logging, get_logger
from azureml.automl.dnn.vision.common.prediction_dataset import PredictionDataset
from azureml.automl.dnn.vision.object_detection.common import masktools
from azureml.automl.dnn.vision.object_detection.common.constants import MaskToolsLiterals, \
    safe_to_log_settings, TilingLiterals, TilingParameters, MaskImageExportParameters, MaskImageExportLiterals
from azureml.automl.dnn.vision.object_detection.common.tiling_helper import \
    merge_predictions_from_tiles_and_images

from azureml.core.run import Run, _OfflineRun
from azureml.core import Workspace
from torch.utils.data import Dataset, DataLoader

logger = get_logger(__name__)


def _score_with_model(model_wrapper, run, target_path, output_file, root_dir,
                      image_list_file, device, batch_size=1,
                      ignore_data_errors=True,
                      labeled_dataset_file=None,
                      input_dataset_id=None, always_create_dataset=False,
                      num_workers=None,
                      validate_score=False, log_output_file_info=False,
                      write_masks_as_images=False,
                      mask_image_type=MaskImageExportParameters.DEFAULT_IMAGE_TYPE,
                      mask_output_dir=None):

    if output_file is None:
        os.makedirs(ScoringLiterals.DEFAULT_OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(ScoringLiterals.DEFAULT_OUTPUT_DIR,
                                   ScoringLiterals.PREDICTION_FILE_NAME)

    if labeled_dataset_file is None:
        os.makedirs(ScoringLiterals.DEFAULT_OUTPUT_DIR, exist_ok=True)
        labeled_dataset_file = os.path.join(ScoringLiterals.DEFAULT_OUTPUT_DIR,
                                            ScoringLiterals.LABELED_DATASET_FILE_NAME)

    if mask_output_dir is None and write_masks_as_images:
        mask_output_dir = ScoringLiterals.DEFAULT_OUTPUT_DIR

    model = model_wrapper.model
    classes = model_wrapper.classes
    # Extract masktool settings for instance segmentation
    masktool_settings = None
    if hasattr(model_wrapper, "masktool_settings"):
        masktool_settings = model_wrapper.masktool_settings
    model.eval()
    inference_settings = model_wrapper.inference_settings

    score_start = time.time()
    ws: Workspace = None if isinstance(run, _OfflineRun) else run.experiment.workspace
    model_wrapper.disable_model_transform()

    mask_score_threshold = masktools._get_setting_or_default(masktool_settings,
                                                             MaskToolsLiterals.MASK_PIXEL_SCORE_THRESHOLD)
    tile_grid_size = inference_settings.get(TilingLiterals.TILE_GRID_SIZE, None)
    tile_overlap_ratio = inference_settings.get(TilingLiterals.TILE_OVERLAP_RATIO,
                                                TilingParameters.DEFAULT_TILE_OVERLAP_RATIO)
    tile_predictions_nms_thresh = inference_settings.get(TilingLiterals.TILE_PREDICTIONS_NMS_THRESH,
                                                         TilingParameters.DEFAULT_TILE_PREDICTIONS_NMS_THRESH)

    logger.info("Building the prediction dataset")
    dataset: PredictionDataset[Dataset] = PredictionDataset(root_dir=root_dir, image_list_file=image_list_file,
                                                            transforms=model_wrapper.get_inference_transform(),
                                                            ignore_data_errors=ignore_data_errors,
                                                            input_dataset_id=input_dataset_id, ws=ws,
                                                            tile_grid_size=tile_grid_size,
                                                            tile_overlap_ratio=tile_overlap_ratio)

    dataloader: RobustDataLoader[DataLoader] = RobustDataLoader(dataset, batch_size=batch_size,
                                                                collate_fn=dataset.collate_function,
                                                                num_workers=num_workers)

    batch_time = AverageMeter()
    end = time.time()
    system_meter = SystemMeter()
    tiling_merge_predictions_time = AverageMeter()
    tiling_nms_time = AverageMeter()

    model.to(device)

    logger.info("Starting the inference")

    with torch.no_grad():
        with open(output_file, "w") as fw, open(labeled_dataset_file, "w") as ldsf:
            label_with_info_list = []
            for i, (filenames, image_batch, image_infos) in \
                    enumerate(utils._data_exception_safe_iterator(iter(dataloader))):
                image_batch = move_images_to_device(image_batch, device)
                labels = model(image_batch)

                for filename, label, image, image_info in zip(filenames, labels, image_batch, image_infos):
                    label_with_info = {}
                    label_with_info.update(image_info)
                    label_with_info.update(label)
                    label_with_info.update(
                        {"filename": filename, "width": image.shape[2], "height": image.shape[1]}
                    )

                    # Store on cpu to save gpu memory
                    label_with_info["boxes"] = label_with_info["boxes"].cpu()
                    label_with_info["labels"] = label_with_info["labels"].cpu()
                    label_with_info["scores"] = label_with_info["scores"].cpu()

                    # encode masks as rle to save memory
                    masks = label_with_info.get("masks", None)
                    if masks is not None:
                        masks = masks.cpu()
                        masks = (masks > mask_score_threshold)
                        rle_masks = []
                        for mask in masks:
                            rle = masktools.encode_mask_as_rle(mask)
                            rle_masks.append(rle)
                        label_with_info["masks"] = rle_masks

                    label_with_info_list.append(label_with_info)

                batch_time.update(time.time() - end)
                end = time.time()
                if i % 100 == 0 or i == len(dataloader) - 1:
                    mesg = "Epoch: [{0}/{1}]\t" "Time {batch_time.value:.4f}" \
                           " ({batch_time.avg:.4f})".format(i, len(dataloader), batch_time=batch_time)
                    logger.info(mesg)

                    system_meter.log_system_stats()

            if dataset._tile_grid_size is not None:
                merged_label_with_info_list = merge_predictions_from_tiles_and_images(
                    label_with_info_list=label_with_info_list, nms_thresh=tile_predictions_nms_thresh,
                    device="cpu", merge_predictions_time=tiling_merge_predictions_time, nms_time=tiling_nms_time)
            else:
                merged_label_with_info_list = label_with_info_list

            predictions_output_start_time = time.time()
            logger.info("Writing predictions to prediction file")
            # count number of lines written to prediction
            prediction_num_lines = 0
            for label_with_info in merged_label_with_info_list:
                prediction_num_lines += 1
                image_shape = (label_with_info["height"], label_with_info["width"])
                _write_prediction_file_line(fw, label_with_info["filename"], label_with_info, image_shape, classes,
                                            masktool_settings)
                _write_dataset_file_line(ldsf, label_with_info["filename"], label_with_info, image_shape, classes,
                                         masktool_settings)
                if write_masks_as_images:
                    mask_image_settings = {MaskImageExportLiterals.IMAGE_TYPE: mask_image_type}
                    _write_masks_as_images(label_with_info, classes,
                                           output_dir=mask_output_dir,
                                           settings=mask_image_settings)
            logger.info("Time taken to write predictions to prediction file: {}".format(
                time.time() - predictions_output_start_time))
            logger.info("Number of lines written to prediction file: {}".format(prediction_num_lines))

        if log_output_file_info:
            logger.info("Prediction file closed status: {}".format(fw.closed))
            logger.info("Labeled dataset file closed status: {}".format(ldsf.closed))
            with open(output_file, "r") as fw, open(labeled_dataset_file, "r") as ldsf:
                # count number of lines actually written to the output files
                logger.info("Number of lines read from prediction file: {}".format(len(fw.readlines())))
                logger.info("Number of lines read from labeled dataset file: {}".format(len(ldsf.readlines())))

        if always_create_dataset or input_dataset_id is not None:
            datastore = ws.get_default_datastore()
            AmlDatasetHelper.create(run, datastore, labeled_dataset_file, target_path)

    # measure total scoring time
    score_time = time.time() - score_start
    utils.log_end_scoring_stats(score_time, batch_time, system_meter, run, prediction_num_lines)

    # Begin validation if flag is passed
    if validate_score:
        logger.info("Validation flag was passed. Starting validation.")
        use_bg_label = detection.use_bg_label(model_wrapper.model_name)
        _validate_score_run(input_dataset_id=input_dataset_id, workspace=ws, use_bg_label=use_bg_label,
                            output_file=output_file, score_run=run)


def score(training_run_id: str, device: str, settings: Dict[str, Any], experiment_name: Optional[str] = None,
          output_file: Optional[str] = None, root_dir: Optional[str] = None, image_list_file: Optional[str] = None,
          ignore_data_errors: bool = True, output_dataset_target_path: Optional[str] = None,
          input_dataset_id: Optional[str] = None, validate_score: bool = False,
          log_output_file_info: bool = False) -> None:
    """Load model and infer on new data.

    :param training_run_id: Name of the training run to load model from
    :type training_run_id: str
    :param device: device to be used for inferencing
    :type device: str
    :param settings: settings for model inference
    :type settings: dict
    :param experiment_name: Name of experiment to load model from
    :type experiment_name: str
    :param output_file: Name of file to write results to
    :type output_file: str
    :param root_dir: prefix to be added to the paths contained in image_list_file
    :type root_dir: str
    :param image_list_file: path to file containing list of images
    :type image_list_file: str
    :param ignore_data_errors: boolean flag on whether to ignore input data errors
    :type ignore_data_errors: bool
    :param output_dataset_target_path: path on Datastore for the output dataset files.
    :type output_dataset_target_path: str
    :param input_dataset_id: The input dataset id.  If this is specified image_list_file is not required.
    :type input_dataset_id: str
    :param validate_score: boolean flag on whether to validate the score
    :type validate_score: bool
    :param log_output_file_info: boolean flag on whether to log output file debug info
    :type log_output_file_info: bool
    """
    logger.info("Final settings (pii free): \n {}".format(clean_settings_for_logging(settings, safe_to_log_settings)))
    logger.info("Settings not logged (might contain pii): \n {}".format(settings.keys() - safe_to_log_settings))

    system_meter = SystemMeter(log_static_sys_info=True)
    system_meter.log_system_stats()

    # Extract relevant parameters from inference settings
    num_workers = settings[SettingsLiterals.NUM_WORKERS]
    batch_size = settings[ScoringLiterals.BATCH_SIZE]

    # Restore model
    model_wrapper = _fetch_model_from_artifacts(run_id=training_run_id,
                                                experiment_name=experiment_name,
                                                device=device,
                                                model_settings=settings)
    logger.info("Model restored successfully")

    # Extract masktool settings for instance segmentation
    if model_wrapper.model_name[:15] == "maskrcnn_resnet":
        valid_masktool_keys = [MaskToolsLiterals.MASK_PIXEL_SCORE_THRESHOLD,
                               MaskToolsLiterals.MAX_NUMBER_OF_POLYGON_POINTS]
        masktool_settings = {key: settings[key] for key in valid_masktool_keys if key in settings}
        model_wrapper.masktool_settings = masktool_settings

    # Extract output mask as image settings
    write_masks_as_images = settings[MaskImageExportLiterals.EXPORT_AS_IMAGE]
    mask_image_type = settings[MaskImageExportLiterals.IMAGE_TYPE]

    current_scoring_run = Run.get_context()

    if output_dataset_target_path is None:
        output_dataset_target_path = AmlDatasetHelper.get_default_target_path()

    logger.info("[start prediction: batch_size: {}]".format(batch_size))
    _score_with_model(model_wrapper, current_scoring_run,
                      output_dataset_target_path,
                      output_file=output_file,
                      root_dir=root_dir,
                      image_list_file=image_list_file,
                      device=device,
                      batch_size=batch_size,
                      ignore_data_errors=ignore_data_errors,
                      input_dataset_id=input_dataset_id,
                      num_workers=num_workers,
                      validate_score=validate_score,
                      log_output_file_info=log_output_file_info,
                      write_masks_as_images=write_masks_as_images,
                      mask_image_type=mask_image_type)
