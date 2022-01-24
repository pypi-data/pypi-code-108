# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utils for running evaluation metrics."""
from typing import Any, Dict

from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import DatasetProcessingType, \
    CommonObjectDetectionDatasetWrapper

from ...common.logging_utils import get_logger
from ..common import masktools
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException

logger = get_logger(__name__)


def prepare_dataset_for_eval(dataset_wrapper):
    """Convert a dataset wrapper object to a dictionary that can be consumed by cocotools/vocmap during evaluation.

    :param dataset: Dataset wrapper with ground truth data used for evaluation
    :type dataset: CommonObjectDetectionDatasetWrapper object (see object_detection.data.dataset_wrappers)
    :return: Dataset in format that can be converted into a cocotools index.
    :rtype: Dict of dicts
    """
    images = []
    # If a detection matches a ground truth with id 0, it is not treated as true positive in cocotools
    # map computation due to a bug in cocotools. Start ann_id from 1 to avoid this.
    ann_id = 1
    annotations = []
    categories = []
    all_crowd = True   # add a all_crowd flag to validate if the dataset only contains crowd bounding boxes

    # Create an dataset wrapper to process only images since we don't need tile groud truth boxes
    # to compute metrics
    image_dataset_wrapper = CommonObjectDetectionDatasetWrapper(dataset_wrapper.dataset, DatasetProcessingType.IMAGES)

    for _, image_targets, image_info in image_dataset_wrapper:
        if not image_info:
            logger.warning("Since image_info is not found, image will be ignored")
            continue

        # image_targets is a tensor for yolo datasets and a dict for OD datasets.
        if image_targets is None or (isinstance(image_targets, dict) and not image_targets):
            logger.warning("Since image_targets is not found, image will be ignored")
            continue

        image_id = image_info["filename"]

        img_dict = {}

        img_dict["id"] = image_id
        img_dict["height"] = image_info["height"]
        img_dict["width"] = image_info["width"]

        images.append(img_dict)

        box_info = image_dataset_wrapper.dataset.prepare_image_targets_for_eval(
            image_targets, img_dict["height"], img_dict["width"])

        boxes = box_info["boxes"]
        labels = box_info["labels"]

        areas = image_info["areas"]
        is_crowds = image_info["iscrowd"]

        masks = box_info.get("masks", [None] * len(boxes))

        for box, label, area, is_crowd, mask in zip(boxes, labels, areas, is_crowds, masks):

            ann: Dict[str, Any] = {}

            box_width = box[2] - box[0]
            box_height = box[3] - box[1]

            ann["bbox"] = [box[0], box[1], box_width, box_height]
            classification = image_dataset_wrapper.dataset.index_to_label(label)

            if mask is not None:
                ann["segmentation"] = masktools.encode_mask_as_rle(mask)

            ann["category_id"] = classification
            ann["image_id"] = image_id
            ann["id"] = ann_id
            ann["area"] = area
            ann["iscrowd"] = is_crowd
            ann_id += 1

            annotations.append(ann)

            # edit all_crowd flag when we meet the first non-crowd bounding boxes.
            if all_crowd and not is_crowd:
                all_crowd = False

        categories = [{"id": cat} for cat in image_dataset_wrapper.dataset.classes]

    if all_crowd:
        error = "No non-crowd evaluation ground truth bounding boxes found, check input jsonl"
        logger.error(error)
        raise AutoMLVisionDataException(error, has_pii=False)

    return {"images": images, "annotations": annotations, "categories": categories}


def prepare_bounding_boxes_for_eval(bounding_box_list):
    """Converts a list of  bounding box records to a format that can be consumed by cocotools/vocmap.

    :param bounding_box_list: Bounding box records for a set of images on cpu
    :type bounding_box_list: List of ImageBoxes (see object_detection.common.bounding_box)
    :return: Detections in format that can be consumed by cocotools/vocmap
    :rtype: List of dicts
    """
    detections = []

    # Mask RCNN always predicts a mask, so only need to check first box record for mask
    has_mask = bounding_box_list[0].has_mask() if bounding_box_list else False

    for bounding_box_record in bounding_box_list:
        image_id = bounding_box_record.image_name

        for box_record in bounding_box_record._boxes:

            record = {"image_id": image_id,
                      "bbox": box_record.bounding_box,
                      "category_id": box_record.label,
                      "score": box_record.score}

            if has_mask:
                record["segmentation"] = box_record.rle_mask

            detections.append(record)

    return detections
