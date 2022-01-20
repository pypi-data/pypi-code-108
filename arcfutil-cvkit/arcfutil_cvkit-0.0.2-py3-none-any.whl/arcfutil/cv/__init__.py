from math import pi
import cv2
import numpy as np

from arcfutil.aff import Arc, NoteGroup


def image_to_arc(path: str, time: int, size=[1, 1.5, -0.2, -0.5], max_gap: float = 10) -> NoteGroup:
    image = cv2.imread(path)
    height, width, color = image.shape
    actual_height, actual_width = size[0] - size[2], size[1] - size[3]
    coef_h, coef_w = actual_height / height, actual_width / width
    canny = cv2.Canny(image, 100, 200)
    lines = cv2.HoughLinesP(canny, 1, pi / 180, 10, max_gap)
    dst = np.zeros((height, width, color), np.uint8)
    arcs = NoteGroup([])

    for each in lines:
        coords = each[0]
        cv2.line(
            dst, (coords[0], coords[1]), (coords[2], coords[3]), (255, 0, 0)
        )
        fromx = round(coords[0] * coef_w + size[3], 2)
        tox = round(coords[2] * coef_w + size[3], 2)
        fromy = round(coords[1] * (-coef_h) + size[0], 2)
        toy = round(coords[3] * (-coef_h) + size[0], 2)
        if not (fromx == tox and fromy == toy):
            arcs.append(Arc(
                time, time, fromx, tox, 's', fromy, toy, 0, True
            ))

    return arcs
