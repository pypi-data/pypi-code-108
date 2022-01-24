# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Tools for using using pycocotools for evaluating model performance."""

from .utils import prepare_dataset_for_eval
from ...common.logging_utils import get_logger

logger = get_logger(__name__)

coco_supported = False
try:
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval
    coco_supported = True
except ImportError:
    logger.warning("Pycocotools import failed. Coco Map score computation is not supported.")
    coco_supported = False


def create_coco_index(dataset_wrapper):
    """Creates a cocotools index from a dataset

    :param dataset_wrapper: Dataset for evaluations
    :type dataset_wrapper: CommonObjectDetectionDatasetWrapper object (see object_detection.data.dataset_wrappers)
    :return: Index created from dataset
    :rtype: cocotools index object
    """
    if not coco_supported:
        logger.warning("Pycocotools import failed. Returning None for coco_index")
        return None

    coco_dataset = COCO()
    coco_dataset.dataset = prepare_dataset_for_eval(dataset_wrapper)
    coco_dataset.createIndex()

    return coco_dataset


def score_from_index(coco_index, boxes, task='bbox'):
    """Scores the a set of bounding box records from an index created from a set of ground truth bounding boxes.

    :param coco_index: Ground truth index
    :type coco_index: cocotools index object
    :param boxes: Detections for a set of images
    :type boxes: List of ImageBoxes (see object_detection.common.boundingbox)
    :param task: Task - either bbox or segm, depending on which scoring task for pycocotools
    :type: str
    :return: List of scores - [Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ]]
        please refer to the coco challenge: cocodataset.org for detailed description of these metrics.
    :rtype: List of floats
    """
    if not coco_supported:
        logger.warning("Pycocotools import failed. Returning 0 for coco map scores.")
        return [0.] * 12

    # No detections
    if len(boxes) == 0:
        return [0.] * 12

    coco_detections = coco_index.loadRes(boxes)
    cocoEval = COCOeval(coco_index, coco_detections, task)
    cocoEval.evaluate()
    cocoEval.accumulate()
    cocoEval.summarize()

    return cocoEval.stats


def score(dataset_wrapper, boxes, task="bbox"):
    """Scores the a set of bounding box records from a set of ground truth bounding boxes.

    :param dataset_wrapper: Dataset with ground truth data used for evaluation
    :type dataset_wrapper: CommonObjectDetectionDatasetWrapper object (see object_detection.data.dataset_wrappers)
    :param boxes: Detections for a set of images
    :type boxes: List of ImageBoxes (see object_detection.common.boundingbox)
    :param task: Task - either bbox or segm, depending on which scoring task for pycocotools
    :type: str
    :return: List of scores - [Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ]]
        please refer to the coco challenge: cocodataset.org for detailed description of these metrics.
    :rtype: List of floats
    """
    if not coco_supported:
        logger.warning("Pycocotools import failed. Returning 0 for coco map scores.")
        return [0.] * 12

    coco_dataset = COCO()
    coco_dataset.dataset = prepare_dataset_for_eval(dataset_wrapper)
    coco_dataset.createIndex()
    coco_detections = coco_dataset.loadRes(boxes)
    cocoEval = COCOeval(coco_dataset, coco_detections, task)
    cocoEval.evaluate()
    cocoEval.accumulate()
    cocoEval.summarize()

    return cocoEval.stats


def convert_coco_metrics(coco_eval_stats):
    """Convert list of coco scores to a dictionary with pre-defined key name

    :param coco_eval_stats: List of scores - [Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ],
        Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ],
        Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ]]
        please refer to the coco challenge: cocodataset.org for detailed description of these metrics.
    :type: List of floats
    :return: dictionary containing coco scores with pre-defined key name
    :rtype: dict
    """
    coco_metrics = {'Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ]': coco_eval_stats[0],
                    'Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ]': coco_eval_stats[1],
                    'Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ]': coco_eval_stats[2],
                    'Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ]': coco_eval_stats[3],
                    'Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ]': coco_eval_stats[4],
                    'Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ]': coco_eval_stats[5],
                    'Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ]': coco_eval_stats[6],
                    'Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ]': coco_eval_stats[7],
                    'Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ]': coco_eval_stats[8],
                    'Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ]': coco_eval_stats[9],
                    'Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ]': coco_eval_stats[10],
                    'Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ]': coco_eval_stats[11]}

    return coco_metrics
