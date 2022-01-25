import cv2
import numpy as np

from . import D_TYPE


def blend(img, mask, bg=None, morph=False, otype=np.uint8):
    mask = expand_dims(mask)

    if morph:
        mask = normalizing(mask)

    output = img * mask if bg is None else img * mask + bg * (1 - mask)

    return output.astype(otype)


def expand_dims(img):
    return np.expand_dims(img, axis=2) if len(img.shape) == 2 else img[..., :1]


def normalizing(img, dtype=D_TYPE):
    return img.astype(dtype) / 255


def smooth(img, mask, anchor=(5, 5)):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, anchor=anchor)
    gt_mask = cv2.dilate(mask, kernel, iterations=1)
    blur = cv2.blur(img, anchor=anchor)
    output = blend(blur, gt_mask, bg=img, morph=True)

    output = blend(img, mask, bg=output, morph=True)

    return output
