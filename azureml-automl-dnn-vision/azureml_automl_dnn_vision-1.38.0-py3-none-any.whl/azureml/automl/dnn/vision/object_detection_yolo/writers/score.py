# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Functions for inference using a trained model"""
import os
import time
import torch
from typing import List, Any, Dict, Optional
from torch.utils.data.dataloader import DataLoader

from azureml.automl.dnn.vision.common.constants import SettingsLiterals, ScoringLiterals
from azureml.automl.dnn.vision.common.dataloaders import RobustDataLoader
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper
from azureml.automl.dnn.vision.common.logging_utils import get_logger, clean_settings_for_logging
from azureml.automl.dnn.vision.common.utils import _data_exception_safe_iterator, log_end_scoring_stats
from azureml.automl.dnn.vision.object_detection_yolo.common.constants import YoloLiterals, \
    safe_to_log_settings
from azureml.core.run import Run, _OfflineRun
from azureml.core import Workspace

from ..data.datasets import PredictionDatasetYolo
from ..utils.utils import non_max_suppression, unpad_bbox
from ...common.average_meter import AverageMeter
from ...common.system_meter import SystemMeter
from ...object_detection.common.object_detection_utils import _fetch_model_from_artifacts, \
    _write_prediction_file_line, _write_dataset_file_line, _validate_score_run

logger = get_logger(__name__)


def _convert_to_rcnn_output(output, image, pad):
    # output: nx6 (x1, y1, x2, y2, conf, cls)
    rcnn_label: Dict[str, List[Any]] = {"boxes": [], "labels": [], "scores": []}

    # Adjust bbox to effective image bounds
    _, height, width = image.shape
    img_height, img_width = unpad_bbox(output[:, :4] if output is not None else None, (height, width), pad)

    if output is not None:
        rcnn_label["boxes"] = output[:, :4]
        rcnn_label["labels"] = output[:, 5:6].long()
        rcnn_label["scores"] = output[:, 4:5]

    return rcnn_label, (img_height, img_width)


def _score_with_model(model_wrapper, run, target_path, output_file, root_dir,
                      image_list_file, device, batch_size=1,
                      ignore_data_errors=True,
                      labeled_dataset_file=None,
                      input_dataset_id=None, always_create_dataset=False,
                      num_workers=None,
                      validate_score=False,
                      log_output_file_info=False):
    if output_file is None:
        os.makedirs(ScoringLiterals.DEFAULT_OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(ScoringLiterals.DEFAULT_OUTPUT_DIR,
                                   ScoringLiterals.PREDICTION_FILE_NAME)
    if labeled_dataset_file is None:
        os.makedirs(ScoringLiterals.DEFAULT_OUTPUT_DIR, exist_ok=True)
        labeled_dataset_file = os.path.join(ScoringLiterals.DEFAULT_OUTPUT_DIR,
                                            ScoringLiterals.LABELED_DATASET_FILE_NAME)

    classes = model_wrapper.classes
    img_size = model_wrapper.specs[YoloLiterals.IMG_SIZE]
    model = model_wrapper.model
    model.eval()

    score_start = time.time()
    ws: Workspace = None if isinstance(run, _OfflineRun) else run.experiment.workspace

    logger.info("Building the prediction dataset")
    dataset = PredictionDatasetYolo(root_dir=root_dir, image_list_file=image_list_file, img_size=img_size,
                                    ignore_data_errors=ignore_data_errors,
                                    input_dataset_id=input_dataset_id, ws=ws)

    dataloader: DataLoader = RobustDataLoader(dataset, batch_size=batch_size,
                                              collate_fn=dataset.collate_function,
                                              num_workers=num_workers)

    batch_time = AverageMeter()
    end = time.time()
    system_meter = SystemMeter()

    model.to(device)

    logger.info("Starting the inference")

    with torch.no_grad():
        with open(output_file, "w") as fw, open(labeled_dataset_file, "w") as ldsf:
            # count number of lines written to prediction
            prediction_num_lines = 0
            for i, (filenames, image_batch, pads) in enumerate(_data_exception_safe_iterator(iter(dataloader))):
                image_batch = image_batch.to(device).float() / 255.0
                inf_out, _ = model(image_batch)

                # Run NMS
                outputs = non_max_suppression(inf_out,
                                              conf_thres=model_wrapper.specs[YoloLiterals.BOX_SCORE_THRESH],
                                              iou_thres=model_wrapper.specs[YoloLiterals.BOX_IOU_THRESH])

                for filename, output, image, pad in zip(filenames, outputs, image_batch, pads):
                    prediction_num_lines += 1
                    # convert yolo output to faster-rcnn output format
                    label, image_shape = _convert_to_rcnn_output(output, image, pad)

                    _write_prediction_file_line(fw, filename, label, image_shape, classes)
                    _write_dataset_file_line(ldsf, filename, label, image_shape, classes)

                batch_time.update(time.time() - end)
                end = time.time()
                if i % 100 == 0 or i == len(dataloader) - 1:
                    mesg = "Epoch: [{0}/{1}]\t" "Time {batch_time.value:.4f}" \
                           " ({batch_time.avg:.4f})".format(i, len(dataloader), batch_time=batch_time)
                    logger.info(mesg)

                    system_meter.log_system_stats()

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
    log_end_scoring_stats(score_time, batch_time, system_meter, run, prediction_num_lines)

    # Begin validation if flag is passed
    if validate_score:
        _validate_score_run(input_dataset_id=input_dataset_id, workspace=ws, use_bg_label=False,
                            output_file=output_file, score_run=run)


def score(run_id: str, device: str, settings: Dict[str, Any], experiment_name: Optional[str] = None,
          output_file: Optional[str] = None, root_dir: Optional[str] = None,
          image_list_file: Optional[str] = None, ignore_data_errors: bool = True,
          output_dataset_target_path: Optional[str] = None, input_dataset_id: Optional[str] = None,
          validate_score: bool = False, log_output_file_info: bool = False):
    """Load model and infer on new data.

    :param run_id: Name of the run to load model from
    :type run_id: str
    :param device: device to use for inferencing
    :type device: Optional[str]
    :param settings: settings for model inference
    :type settings: Dict[str, Any]
    :param experiment_name: Name of experiment to load model from
    :type experiment_name: Optional[str]
    :param output_file: Name of file to write results to
    :type output_file: Optional[str]
    :param root_dir: prefix to be added to the paths contained in image_list_file
    :type root_dir: Optional[str]
    :param image_list_file: path to file containing list of images
    :type image_list_file: Optional[str]
    :param ignore_data_errors: boolean flag on whether to ignore input data errors
    :type ignore_data_errors: bool
    :param output_dataset_target_path: path on Datastore for the output dataset files.
    :type output_dataset_target_path: Optional[str]
    :param input_dataset_id: The input dataset id.  If this is specified image_list_file is not required.
    :type input_dataset_id: Optional[str]
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
    model_wrapper = _fetch_model_from_artifacts(run_id=run_id,
                                                experiment_name=experiment_name,
                                                device=device,
                                                model_settings=settings)
    logger.info("Model restored successfully")

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
                      log_output_file_info=log_output_file_info)
