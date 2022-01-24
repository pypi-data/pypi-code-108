# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Common utilities for object detection and object detection yolo."""
import json
import os
import time
import torch
from torchvision import transforms
from typing import Any, Dict, Union
import azureml.automl.core.shared.constants as shared_constants

from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.artifacts_utils import _download_model_from_artifacts
from azureml.automl.dnn.vision.common.constants import ArtifactLiterals, MetricsLiterals, \
    SettingsLiterals, TrainingLiterals as CommonTrainingLiterals

from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper
from azureml.automl.dnn.vision.object_detection.common import boundingbox
from azureml.automl.dnn.vision.object_detection.common.constants import PredictionLiterals, \
    ValidationMetricType, MaskImageExportLiterals, MaskImageExportParameters, TilingLiterals

from azureml.automl.dnn.vision.object_detection.models.base_model_wrapper import \
    BaseObjectDetectionModelWrapper
from azureml.automl.dnn.vision.object_detection_yolo.models.yolo_wrapper import YoloV5Wrapper
from .masktools import _extract_settings_and_convert_mask_to_polygon, convert_polygon_to_rle_masks,\
    decode_rle_masks_as_binary_mask, encode_mask_as_rle
from ..data.datasets import AmlDatasetObjectDetection
from ..data.dataset_wrappers import CommonObjectDetectionDatasetWrapper, DatasetProcessingType
from ..eval import cocotools
from ..eval.utils import prepare_bounding_boxes_for_eval
from ..eval.vocmap import VocMap
from ..models import detection
from ...common.average_meter import AverageMeter
from ...common.exceptions import AutoMLVisionSystemException
from ...common.system_meter import SystemMeter

logger = get_logger(__name__)


def _load_model_wrapper(torch_model_file, device, model_settings) \
        -> Union[BaseObjectDetectionModelWrapper, YoloV5Wrapper]:
    checkpoint = torch.load(torch_model_file, map_location=device)
    model_state = checkpoint['model_state']
    model_name = checkpoint['model_name']
    number_of_classes = checkpoint['number_of_classes']
    specs = checkpoint['specs']
    settings = specs['model_settings']
    settings.update(specs['inference_settings'])

    # make sure we overwrite those matching model settings with the user provided ones (if any)
    for key in model_settings:
        if key in settings:
            settings[key] = model_settings[key]

    model_wrapper = detection.setup_model(model_name=model_name,
                                          model_state=model_state,
                                          number_of_classes=number_of_classes,
                                          specs=specs['model_specs'],
                                          classes=specs['classes'],
                                          device=device,
                                          settings=settings)

    return model_wrapper


def _fetch_model_from_artifacts(run_id, device, experiment_name=None, model_settings={}):
    _download_model_from_artifacts(run_id=run_id, experiment_name=experiment_name)

    return _load_model_wrapper(shared_constants.PT_MODEL_FILENAME, device, model_settings)


def _get_box_dims(image_shape, box):
    box_keys = ['topX', 'topY', 'bottomX', 'bottomY']
    height, width = image_shape[0], image_shape[1]

    box_dims = dict(zip(box_keys, [coordinate.item() for coordinate in box]))

    box_dims['topX'] = box_dims['topX'] * 1.0 / width
    box_dims['bottomX'] = box_dims['bottomX'] * 1.0 / width
    box_dims['topY'] = box_dims['topY'] * 1.0 / height
    box_dims['bottomY'] = box_dims['bottomY'] * 1.0 / height

    return box_dims


def _get_bounding_boxes(label, image_shape, classes, masktool_settings=None):
    bounding_boxes = []

    if 'masks' not in label:
        masks = [None] * len(label['boxes'])
    else:
        masks = label['masks']

    for box, label_index, score, mask in zip(label['boxes'], label['labels'], label['scores'], masks):
        box_dims = _get_box_dims(image_shape, box)

        box_record = {PredictionLiterals.BOX: box_dims,
                      PredictionLiterals.LABEL: classes[label_index],
                      PredictionLiterals.SCORE: score.item()}

        if mask is not None:
            # TODO: clean up the duplicates (here and the below from _write_dataset_file_line).
            #  Currently, we generate polygon twice which can be once.
            mask = _extract_settings_and_convert_mask_to_polygon(mask, masktool_settings)
            box_record[PredictionLiterals.POLYGON] = mask

        bounding_boxes.append(box_record)

    return bounding_boxes


def _write_prediction_file_line(fw, filename, label, image_shape, classes, masktool_settings=None):
    bounding_boxes = _get_bounding_boxes(label, image_shape, classes, masktool_settings)

    annotation = {PredictionLiterals.FILENAME: filename,
                  PredictionLiterals.BOXES: bounding_boxes}

    fw.write('{}\n'.format(json.dumps(annotation)))


def _write_dataset_file_line(fw, filename, label, image_shape, classes, masktool_settings=None):
    labels = []
    scores = []

    if 'masks' not in label:
        masks = [None] * len(label['boxes'])
    else:
        masks = label['masks']

    for box, label_index, score, mask in zip(label['boxes'], label['labels'], label['scores'], masks):
        label_record = _get_box_dims(image_shape, box)
        label_record[PredictionLiterals.LABEL] = classes[label_index]

        if mask is not None:
            mask = _extract_settings_and_convert_mask_to_polygon(mask, masktool_settings)
            label_record[PredictionLiterals.POLYGON] = mask

        labels.append(label_record)
        scores.append(score.item())

    AmlDatasetHelper.write_dataset_file_line(fw, filename, scores, labels)


def _create_mask_filename(filename_root, index, class_label, confidence_score, image_type):
    return (f"{filename_root}_{index}_label_{class_label}_conf_"
            f"{str(confidence_score).replace('.','')[:4]}.{image_type.lower()}")


def _write_masks_as_images(label, classes, output_dir, settings=None):

    if settings is None:
        settings = {}

    filename = label["filename"]

    filename_root = os.path.basename(filename).split(".")[0]
    converter = transforms.ToPILImage()

    export_image_type = settings.get(
        MaskImageExportLiterals.IMAGE_TYPE, MaskImageExportParameters.DEFAULT_IMAGE_TYPE)

    output_dir = os.path.join(output_dir, 'masks')

    if 'masks' in label:
        for i, (mask, label, score) in enumerate(zip(label['masks'], label['labels'], label['scores'])):
            binary_mask = decode_rle_masks_as_binary_mask([mask]) * 255
            pil_mask = converter(binary_mask)
            class_label = classes[label.item()]
            output_filename = _create_mask_filename(
                filename_root, i, class_label, score.item(), export_image_type)
            os.makedirs(os.path.join(output_dir, filename_root, class_label), exist_ok=True)
            pil_mask.save(os.path.join(output_dir, filename_root, class_label, output_filename))


def _parse_bounding_boxes(output_file, validation_dataset, val_index_map):
    logger.info("Start parsing predictions.")
    prediction_lines = 0
    bounding_boxes = []
    with open(output_file) as od:
        for prediction_line in od:
            prediction_lines += 1
            prediction_dict = json.loads(prediction_line)

            filename = validation_dataset._dataset_helper.get_image_full_path(prediction_lines - 1)
            # Ensure we deal with the same files in validation dataset as output file
            assert prediction_dict[PredictionLiterals.FILENAME] in filename

            image = utils._read_image(ignore_data_errors=True, image_url=filename)
            if image is None:
                logger.info("Skip invalid image {}.".format(image))
                continue

            height = image.height
            width = image.width

            image_boxes = boundingbox.ImageBoxes(filename, val_index_map)
            boxes = []
            labels = []
            scores = []
            has_mask = False
            rle_masks = []
            for box in prediction_dict[PredictionLiterals.BOXES]:
                box_coordinates = [box['box']["topX"] * width, box['box']["topY"] * height,
                                   box['box']["bottomX"] * width, box['box']["bottomY"] * height]
                boxes.append(box_coordinates)
                labels.append(validation_dataset.label_to_index_map(box[PredictionLiterals.LABEL]))
                scores.append(box[PredictionLiterals.SCORE])
                if PredictionLiterals.POLYGON in box:
                    has_mask = True  # If one box has polygon, all the boxes should have polygons.
                    polygon = box[PredictionLiterals.POLYGON]
                    for segment in polygon:
                        segment[::2] = [x * width for x in segment[::2]]
                        segment[1::2] = [y * height for y in segment[1::2]]
                    box_rle_masks = convert_polygon_to_rle_masks(polygon, height, width)
                    box_binary_mask = decode_rle_masks_as_binary_mask(box_rle_masks)
                    box_rle_mask = encode_mask_as_rle(torch.as_tensor(box_binary_mask, dtype=torch.uint8))
                    rle_masks.append(box_rle_mask)
            image_boxes.add_boxes(torch.tensor(boxes), torch.tensor(labels), torch.tensor(scores),
                                  rle_masks if has_mask else None)
            bounding_boxes.append(image_boxes)

    logger.info("End parsing {} predictions.".format(prediction_lines))
    return prepare_bounding_boxes_for_eval(bounding_boxes)


def compute_metrics(eval_bounding_boxes, val_metric_type,
                    val_coco_index, val_vocmap, computed_metrics, per_label_metrics,
                    coco_metric_time, voc_metric_time, primary_metric):
    """Compute metrics from validation bounding boxes.

    :param eval_bounding_boxes: Bounding boxes list
    :type eval_bounding_boxes: List
    :param val_metric_type: Validation metric evaluation type.
    :type val_metric_type: ValidationMetricType.
    :param val_coco_index: Cocoindex created from validation data
    :type val_coco_index: Pycocotool Cocoindex object
    :param val_vocmap: VocMap created from validation data
    :type val_vocmap: VocMap object
    :param computed_metrics: Dictionary to store all metrics
    :type computed_metrics: Dict
    :param per_label_metrics: Dictionary to store per label metrics across epochs
    :type per_label_metrics: Dict
    :param coco_metric_time: Meter to record coco computation time
    :type coco_metric_time: AverageMeter
    :param voc_metric_time: Meter to record vocmap computation time
    :type voc_metric_time: AverageMeter
    :param primary_metric: Metric that is evaluated and logged by AzureML run object.
    :type primary_metric: str
    :return: mAP score
    :rtype: float
    """

    if val_metric_type in ValidationMetricType.ALL_COCO and val_coco_index is None:
        raise AutoMLVisionSystemException("val_metric_type is {}. But, val_coco_index is None. "
                                          "Cannot compute metrics.".format(val_metric_type), has_pii=False)

    if val_metric_type in ValidationMetricType.ALL_VOC and val_vocmap is None:
        raise AutoMLVisionSystemException("val_metric_type is {}. But, val_vocmap is None. "
                                          "Cannot compute metrics.".format(val_metric_type), has_pii=False)

    map_score = 0.0

    task = "bbox"
    if eval_bounding_boxes and "segmentation" in eval_bounding_boxes[0]:
        task = "segm"

    if val_metric_type in ValidationMetricType.ALL_COCO:
        coco_metric_start = time.time()
        coco_score = cocotools.score_from_index(val_coco_index, eval_bounding_boxes, task)
        coco_metric_time.update(time.time() - coco_metric_start)
        logger.info("Coco Time {coco_time.value:.4f} ({coco_time.avg:.4f})".format(coco_time=coco_metric_time))

        computed_metrics[MetricsLiterals.COCO_METRICS] = cocotools.convert_coco_metrics(coco_score)
        map_score = coco_score[1]  # mAP at IoU 0.5

    if val_metric_type in ValidationMetricType.ALL_VOC:
        voc_metric_start = time.time()
        vocmap_result = val_vocmap.compute(eval_bounding_boxes, task)
        voc_metric_time.update(time.time() - voc_metric_start)

        vocmap_score = vocmap_result[VocMap.MAP]
        precision = vocmap_result[VocMap.PRECISION]
        recall = vocmap_result[VocMap.RECALL]

        logger.info("Voc Time {voc_time.value:.4f} ({voc_time.avg:.4f})".format(voc_time=voc_metric_time))

        computed_metrics[VocMap.PRECISION] = round(precision, 5)
        computed_metrics[VocMap.RECALL] = round(recall, 5)

        # update per_label_metrics
        if per_label_metrics is not None:
            per_label_metrics_current_value: Dict[str, Any] = {}
            # use label index instead of label name due to pii
            for label_index, label_metric in vocmap_result[VocMap.PER_LABEL_METRICS].items():
                if label_index not in per_label_metrics:
                    per_label_metrics[label_index] = {}
                if label_index not in per_label_metrics_current_value:
                    per_label_metrics_current_value[label_index] = {}
                for metric_name in [VocMap.PRECISION, VocMap.RECALL, VocMap.AVERAGE_PRECISION]:
                    if metric_name not in per_label_metrics[label_index]:
                        per_label_metrics[label_index][metric_name] = []

                    metric_score = round(label_metric[metric_name].item(), 5)
                    # keep all the previous metric scores
                    per_label_metrics[label_index][metric_name].append(metric_score)
                    # keep only current metric scores
                    per_label_metrics_current_value[label_index][metric_name] = metric_score

            computed_metrics[VocMap.PER_LABEL_METRICS] = per_label_metrics_current_value

        map_score = vocmap_score  # Overwrites coco_score when val_metric_type is COCO_VOC.

    computed_metrics[primary_metric] = round(map_score, 5)
    return map_score


def _evaluate_results(score_run, val_vocmap, eval_bounding_boxes):
    voc_metric_time = AverageMeter()
    computed_metrics: Dict[str, Any] = {}
    per_label_metrics: Dict[str, Any] = {}

    compute_metrics(eval_bounding_boxes, val_metric_type=ValidationMetricType.VOC,
                    val_coco_index=None, val_vocmap=val_vocmap,
                    computed_metrics=computed_metrics, per_label_metrics=per_label_metrics,
                    coco_metric_time=AverageMeter(), voc_metric_time=voc_metric_time,
                    primary_metric=VocMap.MAP)

    utils.log_all_metrics(computed_metrics, azureml_run=score_run, add_to_logger=True)
    properties_to_add = {
        VocMap.MAP: computed_metrics[VocMap.MAP],
        VocMap.PRECISION: computed_metrics[VocMap.PRECISION],
        VocMap.RECALL: computed_metrics[VocMap.RECALL],
    }
    score_run.add_properties(properties_to_add)


def _validate_score_run(input_dataset_id, workspace, use_bg_label, output_file, score_run):
    logger.info("Begin validating scoring run")
    if input_dataset_id is None:
        logger.warning("No input dataset specified, skipping validation.")
        return

    system_meter = SystemMeter(log_static_sys_info=True)
    system_meter.log_system_stats()

    logger.info("Initializing validation dataset.")
    try:
        validation_dataset: AmlDatasetObjectDetection = AmlDatasetObjectDetection(dataset_id=input_dataset_id,
                                                                                  is_train=False,
                                                                                  ignore_data_errors=True,
                                                                                  workspace=workspace,
                                                                                  download_files=False,
                                                                                  use_bg_label=use_bg_label)
        validation_dataset_wrapper = CommonObjectDetectionDatasetWrapper(
            dataset=validation_dataset, dataset_processing_type=DatasetProcessingType.IMAGES)
    except KeyError:
        logger.warning("Dataset does not contain ground truth, skipping validation.")
        return
    logger.info("End initializing validation dataset.")

    val_vocmap = VocMap(validation_dataset_wrapper)
    val_index_map = validation_dataset_wrapper.dataset.classes

    # Parse the predictions
    eval_bounding_boxes = _parse_bounding_boxes(output_file, validation_dataset_wrapper.dataset, val_index_map)
    # Compare the results
    _evaluate_results(score_run, val_vocmap, eval_bounding_boxes)


def score_validation_data(run, model_settings, settings, device, score_with_model):
    """ Runs validations on the best model to give predictions output

    :param run: azureml run object
    :type run: azureml.core.Run
    :param model_settings: dictionary containing model settings
    :type model_settings: dict
    :param settings: dictionary containing settings
    :type settings: dict
    :param device: device to use for inferencing
    :type device: str
    :param score_with_model: method to be called for scoring
    :type score_with_model: Callable
    """
    logger.info("Beginning validation for the best model")

    val_dataset_id = settings.get(SettingsLiterals.VALIDATION_DATASET_ID, None)
    ignore_data_errors = settings.get(SettingsLiterals.IGNORE_DATA_ERRORS, True)

    # Get image_list_file with path
    root_dir = settings.get(SettingsLiterals.IMAGE_FOLDER, None)
    val_labels_file = settings.get(SettingsLiterals.VALIDATION_LABELS_FILE, None)
    if val_labels_file is not None:
        val_labels_file = os.path.join(settings[SettingsLiterals.LABELS_FILE_ROOT], val_labels_file)
        root_dir = os.path.join(settings[SettingsLiterals.DATA_FOLDER], root_dir)

    if val_labels_file is None and val_dataset_id is None:
        logger.warning("No validation dataset or validation file was given, skipping scoring run.")
        return

    # Get target path
    target_path = settings.get(SettingsLiterals.OUTPUT_DATASET_TARGET_PATH, None)
    if target_path is None:
        target_path = AmlDatasetHelper.get_default_target_path()

    batch_size = settings[CommonTrainingLiterals.VALIDATION_BATCH_SIZE]
    output_file = settings.get(SettingsLiterals.VALIDATION_OUTPUT_FILE, None)
    num_workers = settings[SettingsLiterals.NUM_WORKERS]
    validate_scoring = settings[SettingsLiterals.VALIDATE_SCORING]
    log_scoring_file_info = settings.get(SettingsLiterals.LOG_SCORING_FILE_INFO, False)

    model = _fetch_model_from_artifacts(run_id=run.id, device=device,
                                        model_settings=model_settings)

    logger.info("[start scoring for validation data: batch_size: {}]".format(batch_size))

    score_with_model(model, run, target_path=target_path,
                     output_file=output_file, root_dir=root_dir,
                     image_list_file=val_labels_file, batch_size=batch_size,
                     ignore_data_errors=ignore_data_errors,
                     input_dataset_id=val_dataset_id,
                     num_workers=num_workers,
                     device=device,
                     validate_score=validate_scoring,
                     log_output_file_info=log_scoring_file_info)


def write_per_label_metrics_file(output_dir, per_label_metrics, val_index_map):
    """ Write per_label_metrics to a json file in the output directory.

    :param output_dir: Output directory
    :type output_dir: str
    :param per_label_metrics: Per label metrics accumulated over all the epochs
    :type per_label_metrics: dict
    :param val_index_map: Map from numerical indices to class names
    :type val_index_map: List of strings
    """
    # Replace label indices with label names.
    per_label_metrics_with_names = {val_index_map[label_index]: value
                                    for label_index, value in per_label_metrics.items()}

    per_label_metrics_file_path = os.path.join(output_dir, ArtifactLiterals.PER_LABEL_METRICS_FILE_NAME)

    with open(per_label_metrics_file_path, 'w') as f:
        json.dump(per_label_metrics_with_names, f)


def get_inference_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Get inference settings from settings dictionary

    :param settings: Settings
    :type settings: dict
    :return: Settings for inference.
    :rtype: dict
    """
    inference_settings_keys = [TilingLiterals.TILE_GRID_SIZE, TilingLiterals.TILE_OVERLAP_RATIO,
                               TilingLiterals.TILE_PREDICTIONS_NMS_THRESH]
    inference_settings: Dict[str, Any] = {}
    for key in inference_settings_keys:
        if key in settings:
            inference_settings[key] = settings[key]
    return inference_settings
