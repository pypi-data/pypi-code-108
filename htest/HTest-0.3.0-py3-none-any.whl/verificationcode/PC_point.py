#!/usr/bin/env python3.7
# encoding: utf-8
# 获取图片上鼠标点击的坐标

import cv2
import numpy as np

# 图片路径
img = cv2.imread('../content/screenshots/01.png')
a = []
b = []


def on_event_button(event, x, y, flags, param):

    if event == cv2.EVENT_LBUTTONDOWN:
        xy = "%d,%d" % (x, y)
        a.append(x)
        b.append(y)
        cv2.circle(img, (x, y), 1, (0, 0, 255), thickness=-1)
        cv2.putText(img, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                    1.0, (0, 0, 0), thickness=1)
        cv2.imshow("image", img)


cv2.namedWindow("image")
cv2.setMouseCallback("image", on_event_button)
cv2.imshow("image", img)
cv2.waitKey(0)
print(a[0], b[0])
