# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Functions for managing segmenation masks for instance segmenation."""
import PIL
import cv2
import numpy
from pycocotools import mask as pycoco_mask
from simplification.cutil import simplify_coords
from skimage import measure
from typing import Any, Dict, Optional
import torch

from .constants import MaskToolsParameters, MaskToolsLiterals


def convert_polygon_to_rle_masks(polygon, height, width):
    """Convert a polygon outline (in pixel coordinates) to list of rle masks.

    :param polygon: Polygon segments that outline the mask,
    in the form [[x0, y0, x1, y1, ..., x_n, y_n], [x0, y0, ...]],
    in pixel coordinates.
    :type: List of lists of floats
    :param height: Height of image
    :type height: int
    :param width: Width of image
    :type width: int
    :return: List of run-length encoded Segmentation masks
    :rtype: List <class 'dict'>
    """
    if not polygon or not polygon[0]:
        return None

    rle_masks = pycoco_mask.frPyObjects(polygon, height, width)
    return rle_masks


def decode_rle_masks_as_binary_mask(rle_masks):
    """Decode list of run-length encoded masks representing a single outline to a binary mask.

    :param rle_masks: List of run-length encoded masks
    :type rle_masks: List <class 'dict'>
    :return: Segmentation mask
    :rtype: height x width numpy array
    """
    if not rle_masks:
        return None

    masks = []

    for rle in rle_masks:
        m = pycoco_mask.decode(rle)
        masks.append(m)

    # Overlapping segments are used to represent holes in the
    # mask - exclusive or cuts these holes in the bit masks
    base_mask = masks[0]

    for m in masks[1:]:
        base_mask = numpy.logical_xor(base_mask, m)

    return base_mask


def encode_mask_as_rle(mask):
    """Encode binary mask via run-length encoding.

    :param mask: Binary mask in torch.Size([height, width]) or torch.Size([1, height, width])
    :type: mask: <class 'torch.Tensor'>
    :return: Run length encoding of the binary mask
    :rtype: <class 'dict'>
    """
    if len(mask.shape) == 2:
        mask = mask.unsqueeze(0)

    rle = pycoco_mask.encode(numpy.array(mask[0, :, :, numpy.newaxis],
                                         dtype=numpy.uint8,
                                         order="F"))[0]
    rle["counts"] = rle["counts"].decode("utf-8")
    return rle


def convert_mask_to_polygon(
        rle_mask, max_polygon_points=MaskToolsParameters.DEFAULT_MAX_NUMBER_OF_POLYGON_POINTS,
        max_refinement_iterations=MaskToolsParameters.DEFAULT_MAX_NUMBER_OF_POLYGON_SIMPLIFICATIONS,
        edge_safety_padding=MaskToolsParameters.DEFAULT_MASK_SAFETY_PADDING):
    """Convert a run length encoded mask to a polygon outline in normalized coordinates.

    :param rle_mask: Run length encoding of a binary mask
    :type: rle_mask: <class 'dict'>
    :param max_polygon_points: Maximum number of (x, y) coordinate pairs in polygon
    :type: max_polygon_points: int
    :param max_refinement_iterations: Maximum number of times to refine the polygon
    trying to reduce the number of pixels to meet max polygon points.
    :type: max_refinement_iterations: int
    :param edge_safety_padding: Number of pixels to pad the mask with
    :type edge_safety_padding: int
    :return: normalized polygon coordinates
    :rtype: list of list
    """
    # Convert rle mask to numpy bitmask
    mask_array = decode_rle_masks_as_binary_mask([rle_mask])
    image_shape = mask_array.shape

    # Pad the mask to avoid errors at the edge of the mask
    embedded_mask = numpy.zeros((image_shape[0] + 2 * edge_safety_padding,
                                 image_shape[1] + 2 * edge_safety_padding),
                                dtype=numpy.uint8)
    embedded_mask[edge_safety_padding:image_shape[0] + edge_safety_padding,
                  edge_safety_padding:image_shape[1] + edge_safety_padding] = mask_array

    # Find Image Contours
    contours = measure.find_contours(embedded_mask, 0.5)
    simplified_contours = []

    for contour in contours:

        # Iteratively reduce polygon points, if necessary
        if max_polygon_points is not None:
            simplify_factor = 0
            while len(contour) > max_polygon_points and simplify_factor < max_refinement_iterations:
                contour = simplify_coords(contour, simplify_factor)
                simplify_factor += 1

        # Convert to [x, y, x, y, ....] coordinates and correct for padding
        unwrapped_contour = [0] * (2 * len(contour))
        unwrapped_contour[::2] = numpy.ceil(contour[:, 1]) - edge_safety_padding
        unwrapped_contour[1::2] = numpy.ceil(contour[:, 0]) - edge_safety_padding

        simplified_contours.append(unwrapped_contour)

    return _normalize_contour(simplified_contours, image_shape)


def _normalize_contour(contours, image_shape):

    height, width = image_shape[0], image_shape[1]

    for contour in contours:
        contour[::2] = [x * 1. / width for x in contour[::2]]
        contour[1::2] = [y * 1. / height for y in contour[1::2]]

    return contours


def grabcut_mask_refine(image, unrefined_mask,
                        margin=MaskToolsParameters.DEFAULT_GRABCUT_MARGIN,
                        model_levels=MaskToolsParameters.DEFAULT_GRABCUT_MODEL_LEVELS,
                        number_iterations=MaskToolsParameters.DEFAULT_GRABCUT_NUMBER_ITERATIONS):
    """Use grabcut to refine a rough mask.

    :param image: Image associated with mask. Can be a torch CxWxH Tensor or PIL Image
    (object retuirned by PIL.Image.open())
    :type: image: <class 'torch.Tensor'> or <class PIL.JpegImagePlugin.JpegImageFile>
    :param unrefined_mask: Rough bitmap mask to be refined
    :type: numpy.ndarray of shape (height, width) with pixel values 1 or 0
    :param margin: Pixel width of margin to draw around rough polygon boundary.
    :type margin: int
    :model_levels: Number of levels in the grabcut background and foreground models.
    See opencv grabcut documentation. (Optional, defaults to 65, recommend do not change
    unless there is a compelling reason).
    (https://docs.opencv.org/4.3.0/d8/d83/tutorial_py_grabcut.html)
    :type model_levels: int
    :number_iterations: Number of iterations in the grabcut refinement.
    See opencv grabcut documentation. (Optional, defaults to 5).
    :type number_iterations: int
    :return: Refined bitmap mask with pixel values 1 or 0
    :rtype: numpy.ndarray of shape (height, width)
    """
    # Convert image to numpy array, either PIL image or torch tensor
    if isinstance(image, PIL.JpegImagePlugin.JpegImageFile) or \
       isinstance(image, PIL.PngImagePlugin.PngImageFile):
        cv2_image = numpy.array(image, dtype=numpy.uint8)
    elif isinstance(image, torch.Tensor):
        rgb_image_tensor = image.transpose(2, 0).transpose(0, 1)
        cv2_image = numpy.array(rgb_image_tensor.numpy() * 255, dtype=numpy.uint8)

    height, width, _ = cv2_image.shape

    # Construct starting mask - create 'ambiguous' border around mask
    base_mask = _initialize_grabcut_mask(unrefined_mask, margin)

    # Use grabcut to find edges in the 'ambiguous' border
    background_model = numpy.zeros((1, model_levels), numpy.float64)
    foreground_model = numpy.zeros((1, model_levels), numpy.float64)

    grabcut_refined_mask, _, _ = cv2.grabCut(
        cv2_image, base_mask, None,
        background_model, foreground_model, number_iterations,
        cv2.GC_INIT_WITH_MASK)

    # Construct new mask, marking foregound and probable foregound as
    # foregound
    new_mask = numpy.zeros((height, width))
    new_mask[(grabcut_refined_mask == cv2.GC_FGD) | (grabcut_refined_mask == cv2.GC_PR_FGD)] = 1

    return new_mask


def _initialize_grabcut_mask(base_mask, margin):
    """Initialize a grabcut mask from a binary mask.

    :param base_mask: Binary bitmap of the unrefined mask
    :type: numpy array of 1s and 0s of shape (h, w)
    :param margin: Number of pixels around the 0 to 1 boundary in the unrefined
    mask to mark as "ambiguous"
    :type: int
    :returns: numpy bitmask with a margin around the boundary marked with the
    cv2 "amibiguous" pixel value
    :rtype: numpy array of shape (h, w)

    Grabcut works by taking an initial pixel mask with each pixel labeled
    as "definite foregound" (cv2.GC_FGD), "definite background" (cv2.GC_BGD)
    "probable foreground" (cv2.GC_PR_FGD) or "probable background" (cv2.GC_PR_BGD).

    Then, a graphcut algorithm assigns either "foreground" or "background" label
    to any "probable" pixel.

    To make the initial pixel mask, we mark any pixel within a certain manhattan
    distance of the initial foregound/background border as "probable foregound."
    This is the margin. Any remaning pixels in the initial mask are then labeled
    "definite foregound" and any remaining pixels not in in the initial mask are
    then labeled "definite background."

    To determine which pixels are within the margin distance of the boundary,
    for each pixel we compute the sum of all pixels within a square around it
    (like a convolution with kernel = ones((2*margin + 1, 2*margin + 1))). If the sum is
    0, all pixels in the square are 0, so there are only background pixels in
    the square, and the suare can be safely marked as "definite background."
    If the sum is (2*margin + 1)**2, all pixels in the square are 1, so there are only
    foreground pixels in the square, and the pixel can be safely marked as
    "definite foregound." If it is neither of these, there is at least one
    foreground and one background pixel in the square, so the pixel is within
    the margin distance to the boundary, and is marked "probable foregound."
    """
    base_mask_height, base_mask_width = base_mask.shape
    padded_mask = numpy.zeros((base_mask_height + 2 * margin,
                               base_mask_width + 2 * margin))
    overlay_mask = numpy.zeros((base_mask_height,
                                base_mask_width))

    # Compute sum of pixels in "margin" radius square of each pixel
    for i in range(2 * margin + 1):
        for j in range(2 * margin + 1):
            padded_mask[i: base_mask_height + i,
                        j: base_mask_width + j] += base_mask
    overlay_mask = padded_mask[margin: -margin, margin: -margin]

    # Initialize all pixels as "probable foregound"
    grabcut_mask = cv2.GC_PR_FGD * numpy.ones((base_mask_height, base_mask_width),
                                              dtype=numpy.uint8)

    # Label definite foreground and definite background pixels
    grabcut_mask[overlay_mask == (2 * margin + 1)**2] = cv2.GC_FGD
    grabcut_mask[overlay_mask == 0.] = cv2.GC_BGD

    return grabcut_mask


def _get_setting_or_default(masktool_settings: Optional[Dict[str, Any]], key: str) -> Any:
    """Get setting value from masktool_settings using a key. If masktool_settings is None, fetches the default value.

    :param masktool_settings: dictionary containing settings for masktool
    :type: masktool_settings: Optional[Dict[str, Any]]
    :param key: Key for the setting.
    :type key: str
    :return: Value for the setting.
    :rtype: Any
    """
    key_to_default_mapping = {
        MaskToolsLiterals.MASK_PIXEL_SCORE_THRESHOLD: MaskToolsParameters.DEFAULT_MASK_PIXEL_SCORE_THRESHOLD,
        MaskToolsLiterals.MAX_NUMBER_OF_POLYGON_POINTS: MaskToolsParameters.DEFAULT_MAX_NUMBER_OF_POLYGON_POINTS
    }
    if masktool_settings is not None:
        return masktool_settings[key]
    else:
        # need to consider when masktool_settings is None coming from score_validation_data()
        return key_to_default_mapping[key]


def _extract_settings_and_convert_mask_to_polygon(rle_mask, masktool_settings):
    """A wrapper for convert_mask_to_polygon function with relevant settings extraction

    :param rle_mask: Run length encoding of a binary mask
    :type: rle_mask: <class 'dict'>
    :param masktool_settings: dictionary containing settings for masktool
    :type: masktool_settings: dict
    :return: Refined bitmap mask with pixel values 1 or 0
    :rtype: numpy.ndarray of shape (height, width)
    """
    max_polygon_points = _get_setting_or_default(masktool_settings, MaskToolsLiterals.MAX_NUMBER_OF_POLYGON_POINTS)
    mask = convert_mask_to_polygon(rle_mask, max_polygon_points=max_polygon_points)

    return mask
