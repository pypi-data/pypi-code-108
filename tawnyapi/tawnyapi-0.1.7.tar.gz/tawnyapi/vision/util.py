
import base64
from typing import List
import tempfile
import cv2
import logging
import os
import numpy as np


def _get_resized_shape(resize=None, original_img_shape=None, same_size=False):
    if resize is None or original_img_shape is None:
        return None, None, 1

    (h, w) = original_img_shape[:2]
    r = 1
    # TODO: check if round() is the optimal solution, alternative use same_size for same resize values
    # height
    if h >= w:
        r = resize / float(h)
        dim = (round(w * r), resize)
    # width
    else:
        r = resize / float(w)
        dim = (resize, round(h * r))

    if same_size:
        dim = (resize, resize)

    return dim[1], dim[0], r


def _resize_img(img, resize=None, same_size=False):
    (h, w, _) = _get_resized_shape(
        resize=resize, original_img_shape=img.shape, same_size=same_size)
    if h is None or w is None:
        return img
    resized_img = cv2.resize(img, (w, h))
    return resized_img


def _get_base64_images(images, resize=None, images_already_encoded=False):
    b64_images = []
    for img in images:
        if not images_already_encoded:
            img = _resize_img(img, resize=resize)
            _, buffer = cv2.imencode('.tif', img)
            b64_images.append(base64.b64encode(buffer).decode('ascii'))
        else:
            b64_images.append(base64.b64encode(img).decode('ascii'))
    return b64_images


def _load_images_from_paths(img_paths: List[str], load_as_bytes=False):
    images = []
    for img_path in img_paths:
        if load_as_bytes:
            with open(img_path, "rb") as f_in:
                images.append(f_in.read())
        else:
            img = cv2.imread(img_path, cv2.IMREAD_COLOR)
            images.append(img)
    return images


def _get_temp_folder():
    dirpath = tempfile._get_default_tempdir()
    dirpath = os.path.join(dirpath, 'tawnyapis')

    if not os.path.isdir(dirpath):
        logging.info(
            'create temporary directory for face detection models ...')
        os.makedirs(dirpath)

    return dirpath


def _box_norm(x1, y1, x2, y2):
    return np.sqrt(np.power(x2 - x1, 2) + np.power(y2 - y1, 2))


def _get_square_from_box(bounding_box, delta=1.0):
    x1, y1, x2, y2 = bounding_box
    delta_y = int((y2 - y1) / 2)
    delta_x = int((x2 - x1) / 2)

    s = min(delta_x, delta_y)

    center_x = x1 + delta_x
    center_y = y1 + delta_y
    s = int(s * delta)
    start_x = center_x - s
    end_x = center_x + s
    start_y = center_y - s
    end_y = center_y + s

    return start_x, start_y, end_x, end_y


def _add_padding_to_box(bounding_box, image_shape, scale=1.0):
    (h, w) = image_shape[:2]
    x1, y1, x2, y2 = bounding_box

    delta_h = int((y2 - y1) / 2)
    delta_w = int((x2 - x1) / 2)

    center_x = x1 + delta_w
    center_y = y1 + delta_h

    s_delta_w = int(scale * delta_w)
    s_delta_h = int(scale * delta_h)

    padding = min(s_delta_w-delta_w, s_delta_h-delta_h)
    new_delta_w = delta_w + padding
    new_delta_h = delta_h + padding

    start_x = max(0, center_x - new_delta_w)
    end_x = min(w, center_x + new_delta_w)
    start_y = max(0, center_y - new_delta_h)
    end_y = min(h, center_y + new_delta_h)

    return start_x, start_y, end_x, end_y
