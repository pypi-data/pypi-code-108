# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Classes that capture bounding box data from object detection networks."""

import json
from typing import List, Dict, Any, Optional

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException


class BoundingBox(json.JSONEncoder):
    """
    Describes all the information needed to describe a bounding box
    detected in an image, and all information needed for the cocotools
    to score the bounding box.
    """

    def __init__(self, label: str, box: List[float], score: float, rle_mask: Optional[Dict[str, Any]] = None) -> None:
        """
        :param label: Name of the object class
        :type label: str
        :param box: Pixel boundaries of bounding box in form [top, left, bottom, right]
        :type box: List[float]
        :param score: Score between 0 and 1 of confidence in box and classification, 0 being no confidence and 1 being
                      complete confidence.
        :type score: float
        :param rle_mask (optional): Run length encoded mask for instance segmentation
        :type rle_mask: <class 'dict'>, or None
        """
        self._label = label
        self._score = score
        self._x = box[0]
        self._y = box[1]
        self._width = box[2] - box[0]
        self._height = box[3] - box[1]
        self._area = self._width * self._height
        self._rle_mask = rle_mask

    @property
    def bounding_box(self) -> List[float]:
        """Get bounding box in coco eval format.

        :return: box in form [top, left, width, height] in pixels,
        :rtype: List[float]
        """
        return [self._x, self._y, self._width, self._height]

    @property
    def label(self) -> str:
        """Get the detected class.

        :return: class label
        :rtype: str
        """
        return self._label

    @property
    def score(self) -> float:
        """Get the confidence score of the detected class

        :return: confidence score
        :rtype: float
        """
        return self._score

    @property
    def area(self) -> float:
        """Get the area of the bounding box

        :return: Area in pixels of bounding box
        :rtype: float
        """
        return self._area

    @property
    def top_left_x(self) -> float:
        """Get top x of the bounding box.

        :return: x coordinate of top left corner
        :rtype: float
        """
        return self._x

    @property
    def top_left_y(self) -> float:
        """Get top y of the bounding box.

        :return: y coordinate of top left corner
        :rtype: float
        """
        return self._y

    @property
    def width(self) -> float:
        """Get width of the bounding box.

        :return: width of the bounding box
        :rtype: float
        """
        return self._width

    @property
    def height(self) -> float:
        """Get height of the bounding box.

        :return: height of the bounding box
        :rtype: float
        """
        return self._height

    @property
    def rle_mask(self):
        """Get the run length encoded mask of object instance, if present.

        :return: Run length encoded mask for instance segmentation
        :rtype: <class 'dict'>, or None
        """
        return self._rle_mask


class ImageBoxes:
    """
    Contains all the bounding box information for an image,
    as determined by an object detection method.

    Example usage:
    info = [{"filename": "/img1.jpg"}, {"filename": "/img2.jpg"}]
    index_map = ['cat', 'dog']
    # images is a torch tensor of a batch containing
    # img1.jpg and img2.jpg

    labels = model(images)

    # labels is now a dictionary of the form:
    # {'boxes': <Nx4 tensor of form (x0, y0, x1, y1) for N detected bounding boxes>,
    #  'labels': <Nx1 tensor with integer index of the class associated with each bounding box>,
    #  'scores': <Nx1 tensor with float confidence score of each detection>
    #  'rle_masks' (optional): Run length encoded masks for instance segmentation (if model supports)

    # Populate

    bounding_boxes = []

    for info, label in zip(info, labels):
        image_bounding_boxes = ImageBoxes(info['filename'],
                                          index_map)
        image_bounding_boxes.add_boxes(labels['boxes'],
                                       labels['labels'],
                                       labels['scores'],
                                       rle_masks if masks is not None else None)

        bounding_boxes.append(image_bounding_boxes)

    # bounding boxes can now be passed to cocotools.score_from_index
    # to get coco MAP score.
    """

    def __init__(self, image_name: str, index_map: List[str]) -> None:
        """
        :param image_name: Url of image
        :type image_name: str
        :param index_map: Map of integer indexes to class
        names
        :type index_map: list of strings
        """

        self._image_name = image_name
        self._area = 0
        self._width = 0
        self._height = 0
        self._boxes: List[BoundingBox] = []
        self._has_mask = False

        if not type(index_map) == list:
            raise AutoMLVisionValidationException("Index map must be a list of labels",
                                                  has_pii=False)

        self._index_map = index_map

    def add_boxes(self, boxes, labels, scores, rle_masks=None):
        """ Adds all the detected bounding boxes for an image
        to the record for that image.

        :param boxes: Bounding boxes detected in image
        :type boxes: Nx4 Float Tensor
        :param labels: Index of the class for each bounding box
        :type labels: N Int Tensor
        :param scores: Confidence score for each bounding box
        :type scores: N float tensor
        :param rle_masks (optional): Run length encoded masks for instance segmentation
        :type rle_masks: List of N <class 'dict'>, or None
        """

        self._has_mask = rle_masks is not None

        if not self._has_mask:
            rle_masks = [None] * len(boxes)

        for box, label, score, rle_mask in zip(boxes,
                                               labels,
                                               scores,
                                               rle_masks):

            classification = self._index_map[label]

            new_bounding_box = BoundingBox(classification,
                                           box,
                                           score,
                                           rle_mask)

            self._boxes.append(new_bounding_box)

    @property
    def image_name(self):
        """ Get the image names

        :return: Image URL
        :rtype: str
        """
        return self._image_name

    def has_mask(self):
        """ Check if mask field has been populated.

        :return: has mask
        :rtype: bool
        """
        return self._has_mask
