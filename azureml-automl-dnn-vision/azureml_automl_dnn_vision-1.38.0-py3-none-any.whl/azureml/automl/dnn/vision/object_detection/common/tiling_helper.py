# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper utilities for image tiling for object detection."""

import itertools
import numpy as np
import time
import torch

from pycocotools import mask as pycoco_mask
from torch.tensor import Tensor
from typing import Any, cast, Dict, List, Tuple

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.tiling_dataset_element import Tile
from azureml.automl.dnn.vision.common.tiling_utils import get_tiles
from azureml.automl.dnn.vision.common.average_meter import AverageMeter
from azureml.automl.dnn.vision.object_detection.common.constants import DatasetFieldLabels
from azureml.automl.dnn.vision.object_detection.data.object_annotation import ObjectAnnotation

logger = get_logger(__name__)


def generate_tiles_annotations(annotations: List[ObjectAnnotation], tile_grid_size: Tuple[int, int],
                               tile_overlap_ratio: float,
                               image_size: Tuple[int, int]) -> Dict[Tile, List[Dict[str, Any]]]:
    """Generate annotation for tiles when image is split according to a grid size.

    :param annotations: List of annotations for image.
    :type annotations: List[ObjectAnnotation]
    :param tile_grid_size: Tuple indicating number of tiles along width and height dimensions.
    :type tile_grid_size: Tuple[int, int]
    :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
    :type tile_overlap_ratio: float
    :param image_size: Tuple indicating width and height of the image.
    :type image_size: Tuple[int, int]
    :return: Annotations for each tile. Each Key in the dictionary is a tile.
    :rtype: Dict[Tile, List[Dict]]
    """
    # Tile pixel co-ordinates.
    tiles_list = get_tiles(tile_grid_size, tile_overlap_ratio, image_size)
    tiles = torch.tensor([tile.as_tuple() for tile in tiles_list], device="cpu")

    # Annotation box percentage co-ordinates
    annotation_boxes = torch.tensor(
        [[annotation._x0_percentage, annotation._y0_percentage,
          annotation._x1_percentage, annotation._y1_percentage] for annotation in annotations], device="cpu")
    # Convert to pixel co-ordinates.
    annotation_boxes = annotation_boxes.mul(torch.tensor([image_size[0], image_size[1]], device="cpu").repeat(1, 2))

    # Compute intersection between tiles and annotation boxes
    tiles_count = tiles.shape[0]
    annotation_boxes_count = annotation_boxes.shape[0]
    intersection_boxes = torch.zeros((tiles_count, annotation_boxes_count, 4), device="cpu")
    intersection_boxes[:, :, 0] = torch.max(torch.cartesian_prod(tiles[:, 0], annotation_boxes[:, 0]), dim=1)[0]\
        .view(tiles_count, annotation_boxes_count)
    intersection_boxes[:, :, 1] = torch.max(torch.cartesian_prod(tiles[:, 1], annotation_boxes[:, 1]), dim=1)[0]\
        .view(tiles_count, annotation_boxes_count)
    intersection_boxes[:, :, 2] = torch.min(torch.cartesian_prod(tiles[:, 2], annotation_boxes[:, 2]), dim=1)[0]\
        .view(tiles_count, annotation_boxes_count)
    intersection_boxes[:, :, 3] = torch.min(torch.cartesian_prod(tiles[:, 3], annotation_boxes[:, 3]), dim=1)[0]\
        .view(tiles_count, annotation_boxes_count)

    # Use floor() to prevent boxes which will have zero area further down the pipeline.
    # In augmentations.py, int(x_min) and int(x_max) are used to calculate box_w, using floor here to make sure box_w
    # is zero in cases where x_max > x_min, but int(x_max) == int(x_min) so that we don't add those boxes to
    # the tile_annotations.
    intersection_boxes_area = torch.clamp(intersection_boxes[:, :, 2].floor() - intersection_boxes[:, :, 0].floor(),
                                          min=0.0) * \
        torch.clamp(intersection_boxes[:, :, 3].floor() - intersection_boxes[:, :, 1].floor(), min=0.0)

    # Compute new annotation box co-ordinates.
    # Compute intersection boxes co-ordinates relative to tile top X and top Y.
    relative_intersection_boxes = intersection_boxes.sub(tiles[:, :2].repeat(1, 2).view(-1, 1, 4))
    # Scale intersection boxes co-ordinates wrt tile size.
    tile_sizes = torch.cat(((tiles[:, 2] - tiles[:, 0]).view(-1, 1),
                            (tiles[:, 3] - tiles[:, 1]).view(-1, 1)), dim=1)
    relative_intersection_boxes = relative_intersection_boxes.div(tile_sizes.repeat(1, 2).view(-1, 1, 4))

    result = {}
    for index in range(tiles.shape[0]):
        tile_annotations = []
        # Valid annotation box in a tile would be boxes which have intersection area with the tile box.
        valid_intersection_box_indices = torch.nonzero(intersection_boxes_area[index, :])
        for annotation_index in valid_intersection_box_indices:
            original_annotation = annotations[annotation_index]
            tile_annotations.append({
                DatasetFieldLabels.CLASS_LABEL: original_annotation.label,
                DatasetFieldLabels.X_0_PERCENT: relative_intersection_boxes[index, annotation_index, 0].item(),
                DatasetFieldLabels.Y_0_PERCENT: relative_intersection_boxes[index, annotation_index, 1].item(),
                DatasetFieldLabels.X_1_PERCENT: relative_intersection_boxes[index, annotation_index, 2].item(),
                DatasetFieldLabels.Y_1_PERCENT: relative_intersection_boxes[index, annotation_index, 3].item(),
                DatasetFieldLabels.IS_CROWD: original_annotation.iscrowd
            })

        tile_tuple = cast(Tuple[float, float, float, float], tuple(tiles[index].tolist()))
        result[Tile(tile_tuple)] = tile_annotations

    return result


def convert_tile_boxes_to_image_dimensions(tile_boxes: Tensor, tile: Tile,
                                           tile_shape: Tuple[int, int], original_tile_shape: Tuple[int, int],
                                           image_shape: Tuple[int, int], original_image_shape: Tuple[int, int],
                                           device: torch.device):
    """Convert tile bounding boxes into image co-ordinates.

    :param tile_boxes: Tile bounding boxes
    :type tile_boxes: torch.Tensor
    :param tile: Tile co-ordinates within original image
    :type: Tile
    :param tile_shape: Tile width, tile height after transformation
    :type tile_shape: Tuple[int, int]
    :param original_tile_shape: Tile width, tile height before transformation
    :type original_tile_shape: Tuple[int, int]
    :param image_shape: Image width, image height before transformation
    :type image_shape: Tuple[int, int]
    :param original_image_shape: Image width, image height before transformation
    :type original_image_shape: Tuple[int, int]
    :param device: Target device
    :type device: torch.device
    """
    tile_width_ratio = tile_shape[0] / original_tile_shape[0]
    tile_height_ratio = tile_shape[1] / original_tile_shape[1]
    image_width_ratio = image_shape[0] / original_image_shape[0]
    image_height_ratio = image_shape[1] / original_image_shape[1]
    # Move bounding boxes from tile co-ordinates to image co-ordinates.
    #   Resize to old tile dimensions
    tile_boxes.div_(torch.tensor([tile_width_ratio, tile_height_ratio], device=device).repeat(2))
    #   Move relative to image 0, 0 in old dimensions
    tile_boxes.add_(torch.tensor([tile.top_left_x, tile.top_left_y], device=device).repeat(2))
    #   Resize to new image dimensions
    tile_boxes.mul_(torch.tensor([image_width_ratio, image_height_ratio], device=device).repeat(2))


def get_duplicate_box_indices(bounding_boxes: Tensor, bounding_box_scores: Tensor, bounding_box_labels: Tensor,
                              bounding_box_tiles: Tensor, nms_thresh: float, device: torch.device):
    """Get duplicate box indices by running nms with a predefined iou threshold across boxes from different tiles
    and entire image.
    Two boxes participate in nms only when they are of the same label and they come from different tiles
    (or one box from tile and one box from entire image). When multiple boxes overlap, i.e,
    have iou > iou_threhsold, the box with the highest score is picked and the others are marked as duplicates.

    Assumption is that image_dimensions are passed in bounding_box_tiles for boxes from the entire image
    to facilitate easy computation of duplicate boxes.

    :param bounding_boxes: Bounding boxes in (xmin, ymin, xmax, ymax) format.
    :type bounding_boxes: Tensor of shape (N, 4) and dtype torch.float
    :param bounding_box_scores: Bounding box scores.
    :type bounding_box_scores: Tensor of shape (N) and dtype torch.float
    :param bounding_box_labels: Bounding box labels.
    :type bounding_box_labels: Tensor of shape (N) and dtype torch.int64
    :param bounding_box_tiles: Tiles in which bounding boxes are predicted in (xmin, ymin, width, height) format.
                               Note that for boxes predicted in the entire image, this should be image dimensions.
    :type bounding_box_tiles: Tensor of shape (N, 4) and dtype torch.float
    :param nms_thresh: The iou threshold to use to perform nms.
    :type nms_thresh: float
    :param device: Target device
    :type device: torch.device
    :return: Tensor with value 1 for box indices that are duplicates.
    :rtype: Tensor of shape (N) and dtype torch.uint8
    """
    num_boxes = bounding_boxes.shape[0]
    duplicate_boxes = torch.zeros(num_boxes, dtype=torch.uint8, device=device)

    if num_boxes == 0:
        return duplicate_boxes

    bounding_boxes_np = bounding_boxes.clone().detach().cpu().numpy()
    bounding_boxes_np[:, 2] = bounding_boxes_np[:, 2] - bounding_boxes_np[:, 0]
    bounding_boxes_np[:, 3] = bounding_boxes_np[:, 3] - bounding_boxes_np[:, 1]
    iscrowd = np.zeros(num_boxes, dtype=np.uint8)
    iou = pycoco_mask.iou(bounding_boxes_np, bounding_boxes_np, iscrowd)
    iou_tensor = torch.from_numpy(iou).to(device)

    # Remove overlapping boxes with lower score from bounding box list.
    _, box_indices_sorted = torch.sort(bounding_box_scores, descending=True)
    for index, entry in enumerate(box_indices_sorted.tolist()):
        if duplicate_boxes[entry] == 1:
            continue

        candidate_box_indices = torch.zeros(num_boxes, dtype=torch.bool, device=device)
        # Remaining elements in sorted list
        candidate_box_indices[box_indices_sorted[index + 1:]] = 1
        # Not yet detected as duplicates
        candidate_box_indices.logical_and_(torch.logical_not(duplicate_boxes))
        # With the same label
        candidate_box_indices.logical_and_(bounding_box_labels == bounding_box_labels[entry])
        # From other tiles
        candidate_box_indices.logical_and_((bounding_box_tiles != bounding_box_tiles[entry]).any(dim=1))
        # IoU > iou_threshold
        candidate_box_indices.logical_and_(iou_tensor[entry, :] > nms_thresh)

        duplicate_boxes[candidate_box_indices.nonzero(as_tuple=True)[0]] = 1

    return duplicate_boxes


def merge_predictions_from_tiles_and_images_single_image(image_label_with_info_list: List[Dict], nms_thresh: float,
                                                         per_image_nms_time: AverageMeter, device: torch.device):
    """Get image label_with_info after merging label_with_infos from entire image and image tiles for a single image

    This function does the following steps to merge the predictions
        - Boxes from tiles are scaled to image dimensions. Please note that this scaling takes into account
          the image/tile size changes due to data transforms
        - Then, nms is applied on scaled boxes from image tiles and boxes from entire image using an iou_threhsold.
          When multiple boxes overlap, the box with the highest score is preserved and the others are removed.
        - A single label_with_info dictionary is returned with the new set of boxes and their corresponding labels
          and scores. For all the other keys, it contains the values from input label_with_info corresponding to
          the entire image.

    :param image_label_with_info_list: List of dictionaries containing predicted labels and info from entire image and
                                       tiles for a single image.
    :type image_label_with_info_list: List[Dict]
    :param nms_thresh: The iou threshold to use to perform nms while merging predictions from tiles and image.
    :type nms_thresh: float
    :param per_image_nms_time: Meter to compute duplicate box detection time.
    :type per_image_nms_time: AverageMeter
    :param device: Target device
    :type device: torch.device
    :return: Dictionary containing image info and merged, de-duped image labels.
    :rtype: Dict
    """
    # Create a list of bounding boxes from image and tiles
    boxes = []
    box_scores = []
    box_labels = []
    box_tiles = []

    # Find the label_with_info for the entire image
    image_label_with_info = None
    for label_with_info in image_label_with_info_list:
        if "tile" not in label_with_info or label_with_info["tile"] is None:
            image_label_with_info = label_with_info
            break

    if image_label_with_info is None:
        raise AutoMLVisionSystemException("Found tile annotations without image annotations.", has_pii=False)

    image_shape = (image_label_with_info["width"], image_label_with_info["height"])
    original_image_shape = (image_label_with_info["original_width"], image_label_with_info["original_height"])

    for label_with_info in image_label_with_info_list:
        num_boxes = label_with_info["boxes"].shape[0]
        if "tile" in label_with_info and label_with_info["tile"] is not None:
            # predictions from image tiles
            convert_tile_boxes_to_image_dimensions(
                tile_boxes=label_with_info["boxes"], tile=label_with_info["tile"],
                tile_shape=(label_with_info["width"], label_with_info["height"]),
                original_tile_shape=(label_with_info["original_width"], label_with_info["original_height"]),
                image_shape=image_shape,
                original_image_shape=original_image_shape,
                device=device)

            box_tiles.append(torch.tensor([label_with_info["tile"].as_tuple()], device=device).expand(num_boxes, 4))
        else:
            # predictions from entire image.
            # Pass image dimnesions as tile here to facilitate easy computation of duplicate boxes.
            image_dimensions = [0, 0, label_with_info["original_width"], label_with_info["original_height"]]
            box_tiles.append(torch.tensor([image_dimensions], device=device).expand(num_boxes, 4))

        boxes.append(label_with_info["boxes"])
        box_scores.append(label_with_info["scores"])
        box_labels.append(label_with_info["labels"])

    boxes_tensor = torch.cat(boxes, dim=0)
    box_scores_tensor = torch.cat(box_scores, dim=0)
    box_labels_tensor = torch.cat(box_labels, dim=0)
    box_tiles_tensor = torch.cat(box_tiles, dim=0)

    # Perform nms and get the list of duplicate boxes to be removed.
    nms_start_time = time.time()
    duplicate_box_indices = get_duplicate_box_indices(boxes_tensor, box_scores_tensor,
                                                      box_labels_tensor, box_tiles_tensor, nms_thresh, device)
    per_image_nms_time.update(time.time() - nms_start_time)

    valid_box_indices = torch.logical_not(duplicate_box_indices)

    merged_image_label_with_info = image_label_with_info
    merged_image_label_with_info["boxes"] = boxes_tensor[valid_box_indices]
    merged_image_label_with_info["scores"] = box_scores_tensor[valid_box_indices]
    merged_image_label_with_info["labels"] = box_labels_tensor[valid_box_indices]

    return merged_image_label_with_info


def merge_predictions_from_tiles_and_images(label_with_info_list: List[Dict], nms_thresh: float, device: torch.device,
                                            merge_predictions_time: AverageMeter, nms_time: AverageMeter):
    """ Get a list of image labels with infos after merging predictions from tiles and images for all the images.

    :param label_with_info_list: List of dictionary containing info and predicted labels for images and image tiles
                                 across all images.
    :type image_label_with_info_list: List[Dict]
    :param nms_thresh: The iou threshold to use to perform nms while merging predictions from tiles and image.
    :type nms_thresh: float
    :param device: Target device
    :type device: torch.device
    :param merge_predictions_time: Meter to record time taken to merge predictions.
    :type merge_predictions_time: AverageMeter
    :param nms_time: Meter to record time taken to perform nms during merging.
    :type nms_time: AverageMeter
    :return: List of dictionary containing image info and merged image labels.
    :rtype: List[Dict]
    """
    per_image_label_with_info_list: Dict[str, List[Dict]] = {}
    # The order of images in the labels_with_info_list is maintained in image_names. This makes sure that the
    # return value is in the same order (of images) as the input label_with_info_list.
    # This is important in scoring as validate_score_run function assumes that the output predictions
    # are in the order of the input images list.
    image_names: List[str] = []

    merge_start_time = time.time()

    for label_with_info in label_with_info_list:
        image_name = label_with_info["filename"]
        if image_name not in per_image_label_with_info_list:
            image_names.append(image_name)
            per_image_label_with_info_list[image_name] = []
        per_image_label_with_info_list[image_name].append(label_with_info)

    result = []

    per_image_nms_time = AverageMeter()
    for image_name in image_names:
        image_label_with_info_list = per_image_label_with_info_list[image_name]
        merged_image_label_with_info = merge_predictions_from_tiles_and_images_single_image(
            image_label_with_info_list, nms_thresh, per_image_nms_time, device)
        result.append(merged_image_label_with_info)

    nms_time.update(per_image_nms_time.sum)
    merge_predictions_time.update(time.time() - merge_start_time)
    logger.info("Time taken to merge predictions from tiles and images: {merge_predictions_time.val:.4f} "
                "({merge_predictions_time.avg:.4f})".format(merge_predictions_time=merge_predictions_time))
    logger.info("Time taken to perform nms while merging predictions from tiles and image: {nms_time.val:.4f} "
                "({nms_time.avg:.4f})".format(nms_time=nms_time))

    return result
