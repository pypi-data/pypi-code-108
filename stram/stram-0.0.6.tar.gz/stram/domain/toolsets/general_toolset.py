import datetime
from math import inf
from os.path import join
from collections import deque

import numpy as np
import tensorflow as tf


def clip_0_255(image):
    """
    Clip image values to be in range [0..255].

    Args:
        image (tf.Tensor): an input image tensor
    Returns:
        image (tf.Tensor): the image tensor with the values clipped
    """
    return tf.clip_by_value(image, clip_value_min=0.0, clip_value_max=255.0)


def initialize_mask(image, mask):
    """
    Create mask variable and ensure it's in good shape and type. If the mask contains
    only one non-zero label, this will be turned into 1.

    Args:
        image (np.ndarray): input image of shape [H, W, 3]
        mask (np.ndarray): input mask of shape [H, W]
    Returns:
        mask (np.ndarray): mask of shape [H, W, 1]
    Raises:
        ValueError, if the shape of `mask` doesn't match the shape of `image`
    """
    mask_shape = image.shape[:2]

    if mask is None:
        return np.ones(mask_shape + (1,), dtype=np.int32)
    elif mask.shape != mask_shape:
        raise ValueError(
            f'Image and Mask must have the same shape but they '
            f'are {mask_shape} and {mask.shape}'
        )
    else:
        non_zero_labels = np.setdiff1d(mask, [0])
        if len(non_zero_labels) == 1:
            mask[mask == non_zero_labels[0]] = 1

    return np.expand_dims(mask, axis=-1).astype(np.int32)


def validate_masks(content_mask, style_mask):
    """
    Check if the two masks have matching labels.

    Args:
        content_mask (np.ndarray): mask of shape [H, W, 1]
        style_mask (np.ndarray): mask of shape [H, W, 1]
    Raises:
        ValueError, if the masks don't have matching labels
    """
    content_diff = np.setdiff1d(content_mask, style_mask)
    if not (np.array_equal(content_diff, []) or np.array_equal(content_diff, [0])):
        raise ValueError(
            f'Content mask contains elements {content_diff} '
            'which are not present in the style mask'
        )
    style_diff = np.setdiff1d(style_mask, content_mask)
    if not (np.array_equal(style_diff, []) or np.array_equal(style_diff, [0])):
        raise ValueError(
            f'Style mask contains elements {style_diff} '
            'which are not present in the content mask'
        )


def get_colour_map():
    """
    Create an RGB colour map dictionary for grayscale masks.
    The colour map uses 15 preset distinctive colours.

    Returns:
        colour_map (dict): maps label to RGB value
    """
    return {
        0: np.array([170, 110, 40], dtype=np.uint8),  # brown
        1: np.array([255, 225, 25], dtype=np.uint8),  # yellow
        2: np.array([0, 130, 200], dtype=np.uint8),  # blue
        3: np.array([230, 25, 75], dtype=np.uint8),  # red
        4: np.array([60, 180, 75], dtype=np.uint8),  # green
        5: np.array([250, 190, 212], dtype=np.uint8),  # pink
        6: np.array([0, 0, 128], dtype=np.uint8),  # navy
        7: np.array([255, 255, 255], dtype=np.uint8),  # white
        8: np.array([128, 0, 0], dtype=np.uint8),  # maroon
        9: np.array([70, 240, 240], dtype=np.uint8),  # cyan
        10: np.array([240, 50, 230], dtype=np.uint8),  # magenta
        11: np.array([0, 128, 128], dtype=np.uint8),  # teal
        12: np.array([128, 128, 0], dtype=np.uint8),  # olive
        13: np.array([220, 190, 255], dtype=np.uint8),  # lavender
        14: np.array([255, 215, 190], dtype=np.uint8),  # apricot
    }


def colour_mask(mask, colour_map):
    """
    Create an RGB image from a grayscale mask according to `colour_map`.

    Args:
        mask (np.ndarray): single channel image
        colour_map (dict): maps label to RGB value
    Returns:
        coloured_mask (tf.Tensor): 3-channeled image tensor
    """
    coloured_mask = np.empty(mask.shape + (3,), dtype=np.uint8)

    for label in np.unique(mask):
        if label == 0:
            colour = (np.array([0, 0, 0], dtype=np.uint8),)  # black
        else:
            colour = colour_map[label % len(colour_map)]
        coloured_mask[mask == label] = colour

    return tf.expand_dims(coloured_mask, axis=0)


def create_optimizer(optimizer_name, optimizer_params, learning_rate_params):
    """
    Create an optimizer with polynomial decay.

    Args:
        optimizer_name (str): the name of the optimizer (Adam, SGD, etc.)
        optimizer_params (dict): parameters for the optimizer
        learning_rate_params (dict): parameters for the learning rate scheduler
    Returns:
        optimizer (tf.optimizers.Optimizer): the optimizer object
    """
    lr_casting = dict(
        initial_learning_rate=float,
        end_learning_rate=float,
        decay_steps=int,
        power=float,
    )
    lr_config = {k: lr_casting[k](v) for k, v in learning_rate_params.items()}
    lr_scheduler = tf.optimizers.schedules.PolynomialDecay.from_config(lr_config)
    Optimizer = getattr(tf.optimizers, optimizer_name)

    return Optimizer(learning_rate=lr_scheduler, **optimizer_params)


def create_summary_writer(path):
    """
    Create a summary writer for monitoring loss functions and image styling progress
    It should only be used for debugging purposes (not in production).

    Args:
        path (str): the location where the summary folder will be created
    Returns:
        summary_writer (tf.summary.SummaryWriter): the summary writer object
    """
    summary_folder = join(path, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    return tf.summary.create_file_writer(summary_folder)


def variation_loss(image):
    """
    Loss value for the pixel variation computed by averaging the absolute differences
    between all pairs of neighbouring pixels.

    Args:
        image (tf.Tensor): an input image tensor
    Returns:
        loss_value (tf.float32): the loss value
    """
    image_area = tf.shape(image)[-2] * tf.shape(image)[-3]
    total_variation_loss = tf.image.total_variation(image)[0]

    return tf.cast(total_variation_loss, tf.float32) / tf.cast(image_area, tf.float32)


class EarlyStopper:
    """
    Tracks a metric over time and flags when its improvement stagnates according
    to some preconfigured properties like patience and delta.

    Args:
        delta (float): minimum relative improvement expected over the history buffer;
                       if this improvement percentage is not attained, then STOP
        patience (int): size of the buffer that holds the history of values
    """

    def __init__(self, delta, patience):
        self.actual_delta = None
        self.expected_delta = delta

        self.min_value = inf
        self.patience = patience
        self.history = deque([], self.patience)

    def __call__(self, value):
        """
        Adds the value to the history buffer and informs the external caller if the
        training should stop.

        Args:
            value (float): current metric value
        Returns:
            stop (bool): True for "should stop", False for "should continue"
        """
        self.min_value = min(self.min_value, value)

        if len(self.history) < self.patience:
            self.history.appendleft(value)
            return False

        ancient_value = self.history.pop()
        self.actual_delta = (ancient_value - self.min_value) / ancient_value

        if self.expected_delta < self.actual_delta:
            self.history.appendleft(value)
            return False

        return True

    def deltas_info(self):
        """
        Return a message that displays the values for actual_delta and expected_delta.

        Returns:
            message (str): displays the current values for deltas
        """
        return (
            f'expected_delta={self.expected_delta}; '
            + f'actual_delta={self.actual_delta:.10f}'
        )
