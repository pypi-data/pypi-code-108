import cv2
import numpy as np

from . import D_TYPE

PNG_SHAPE = 4

FUNC_ALPHA = {
    1: lambda x: x,
    2: lambda x: np.expand_dims(x, axis=2),
    3: lambda x: x[..., :1],
    4: lambda x: x[..., -1:]
}


def normalize(img, dtype=D_TYPE):
    return img.astype(dtype) / 255


def mask_dims(img):
    if len(img.shape) == 2:
        axis = 2
    elif len(img.shape) >= 3:
        axis = img.shape[2]
    else:
        axis = 1

    return FUNC_ALPHA[axis](img)


def color_dims(img):
    return img[..., :3] if len(img.shape) >= 3 and img.shape[2] >= 3 else img


def concatenate(img, mask, dims=True):
    return np.concatenate((color_dims(img), mask_dims(mask) if dims else mask), axis=2)


def daub(img, mask=None, bg_color=(144, 238, 144), otype=np.uint8):
    img_rgb = color_dims(img)
    mask = normalize(mask_dims(mask) if mask is not None else FUNC_ALPHA[PNG_SHAPE](img))

    bg_img = np.zeros(img_rgb.shape, dtype=np.uint8)
    for i in range(3):
        bg_img[..., i].fill(bg_color[i])

    result = img_rgb * mask + bg_img * (1 - mask)

    return result.astype(otype)


def blend(img, mask, bg=None, norm=True, otype=np.uint8):
    mask = mask_dims(mask)

    if norm:
        mask = normalize(mask)

    if bg is None:
        output = concatenate(img * mask, mask, dims=False)
    else:
        output = (img * mask + bg * (1 - mask))

    return output.astype(otype)


def smooth(img, mask, ksize=(5, 5), otype=np.uint8):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=ksize)
    gt_mask = cv2.dilate(mask, kernel, iterations=1)
    blur = cv2.blur(img, ksize=ksize)
    output = blend(blur, gt_mask, bg=img)

    output = blend(img, mask, bg=output)

    return output.astype(otype)
