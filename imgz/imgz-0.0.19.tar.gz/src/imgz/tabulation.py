import cv2
import numpy as np

from imgz import TOP, BOTTOM, RIGHT, LEFT


def find_table_lines(img_rbg, horizontal_scale=10, vertical_scale=10):
    """
    获得表格图片横竖线

    :param 图片路径
    """
    gray = cv2.cvtColor(img_rbg, cv2.COLOR_BGR2GRAY)

    # 二值化
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)

    height, width = binary.shape

    # 识别横线
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (width // horizontal_scale, 1))
    eroded = cv2.erode(binary, kernel, iterations=1)
    dilated_horizontal = cv2.dilate(eroded, kernel, iterations=1)

    # 识别竖线
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, height // vertical_scale))
    eroded = cv2.erode(binary, kernel, iterations=1)
    dilated_vertical = cv2.dilate(eroded, kernel, iterations=1)

    return dilated_horizontal, dilated_vertical, binary


def find_effective_points(coords=[], step=10):
    """
    通过排序，获取跳变的x和y的值，说明是交点，否则交点会有好多像素值值相近，只取相近值的最后一点
    这个10的跳变不是固定的，根据不同的图片会有微调，基本上为单元格表格的高度（y坐标跳变）和长度（x坐标跳变）

    :param coords: 坐标簇
    :param step: 跳变幅度
    :return: 返回有效坐标点
    """
    coord_list = []
    if len(coords):
        i = 0
        coos = np.sort(coords)
        for i in range(len(coos) - 1):
            if coos[i + 1] - coos[i] > step:
                coord_list.append(coos[i])
            i = i + 1

        # 要将最后一个点加入
        coord_list.append(coos[i])

    return coord_list


def split_image(image, coord_y, coord_x, roi=None, paddle=(0, 1, 1, 1), do_post=None):
    """
    循环y坐标，x坐标分割表格
    """
    for i in range(len(coord_y) - 1):
        for j in range(len(coord_x) - 1):
            # 在分割时，第一个参数为y坐标，第二个参数为x坐标
            image_patch = image[
                          coord_y[i] + paddle[TOP]:coord_y[i + 1] - paddle[BOTTOM],
                          coord_x[j] + paddle[LEFT]:coord_x[j + 1] - paddle[RIGHT]
                          ]

            if do_post:
                do_post(image_patch, image_patch[roi[TOP]:roi[BOTTOM], roi[LEFT]:roi[RIGHT]] if roi else None)

            j += 1
        i += 1
