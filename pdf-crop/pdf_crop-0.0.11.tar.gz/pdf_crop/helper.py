import numpy as np
from rich import print


def detect_top(array, cy, space, threshold):
    height, _, _ = array.shape
    for end_h in range(cy, 0, -space):
        start_h = max(end_h - threshold, 0)
        if np.count_nonzero(array[start_h:end_h, :, :]) == 0:
            return end_h
    return 0


def detect_bottom(array, cy, space, threshold):
    height, _, _ = array.shape
    for start_h in range(cy, height, space):
        end_h = min(start_h + threshold, height)
        if np.count_nonzero(array[start_h:end_h, :, :]) == 0:
            return start_h
    return height


def detect_left(array, cx, top, bottom, space, threshold):
    _, width, _ = array.shape
    for end_w in range(cx, 0, -space):
        start_w = max(end_w - threshold, 0)
        nnz = np.count_nonzero(array[top:bottom, start_w:end_w, :])
        if nnz == 0:
            return end_w
    return 0


def detect_right(array, cx, top, bottom, space, threshold):
    _, width, _ = array.shape
    for start_w in range(cx, width, space):
        end_w = min(start_w + threshold, width)
        nnz = np.count_nonzero(array[top:bottom, start_w:end_w, :])
        if nnz == 0:
            return start_w
    return width


def detect_center(array):
    height, width, _ = array.shape
    center_x = -1
    center_y = -1
    non_zero = -1
    for i in range(height):
        nnz = np.count_nonzero(array[i : i + 1, :, :])
        if nnz > non_zero:
            center_y = i
            non_zero = nnz
    non_zero = -1
    for j in range(width):
        nnz = np.count_nonzero(array[:, j : j + 1, :])
        if nnz > non_zero:
            center_x = j
            non_zero = nnz
    return center_x, center_y


def detect_frame(array, space, threshold):
    reversed_array = array - 255
    height, width, _ = array.shape
    threshold_h = max(int(height * threshold), 1)
    threshold_w = max(int(width * threshold), 1)

    cx, cy = detect_center(reversed_array)
    top = detect_top(reversed_array, cy, space, threshold_h)
    bottom = detect_bottom(reversed_array, cy, space, threshold_h)
    left = detect_left(reversed_array, cx, top, bottom, space, threshold_w)
    right = detect_right(reversed_array, cx, top, bottom, space, threshold_w)
    # print(cx, cy)
    return left / width, top / height, right / width, bottom / height


def rect_str(rect):
    return "(%d, %d), (%d, %d)" % (rect[0], rect[1], rect[2], rect[3])
