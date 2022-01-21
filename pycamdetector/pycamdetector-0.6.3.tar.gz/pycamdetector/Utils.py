"""
A Library concluding the necessary Functions for Computer Vision using OpenCV

Author: Roshaan Mehmood
"""

import cv2
import numpy as np
import copy


def imgFlip(img, horFlip=False):
    """
    function to flip an image vertically or horizontally. It is based on openCV flip function

    :param img: Image to flip in.
    :param horFlip: Flag for flipping the image horizontally.
    :return: Flipped Image.
    """
    if horFlip:
        img = cv2.flip(img, 0)
    else:
        img = cv2.flip(img, 1)

    return img


def imagesStack(imageList, cols, scale):
    """
    Stack Images together to display in a single window.

    :param imageList: list of images to stack
    :param cols: the num of img in a row
    :param scale: bigger~1+ ans smaller~1-
    :return: Stacked Image
    """
    imageList = copy.deepcopy(imageList)

    # make the array full by adding blank img, otherwise the openCV can't work
    totalImages = len(imageList)
    rows = totalImages // cols if totalImages // cols * cols == totalImages else totalImages // cols + 1
    blankImages = cols * rows - totalImages

    width = imageList[0].shape[1]
    height = imageList[0].shape[0]
    imgBlank = np.zeros((height, width, 3), np.uint8)
    imageList.extend([imgBlank] * blankImages)

    # resize the images
    for i in range(cols * rows):
        imageList[i] = cv2.resize(imageList[i], (0, 0), None, scale, scale)
        if len(imageList[i].shape) == 2:
            imageList[i] = cv2.cvtColor(imageList[i], cv2.COLOR_GRAY2BGR)

    # put the images in a board
    hor = [imgBlank] * rows
    for y in range(rows):
        line = []
        for x in range(cols):
            line.append(imageList[y * cols + x])
        hor[y] = np.hstack(line)
    ver = np.vstack(hor)
    return ver


def cornerRect(img, bbox, drawRect=True, corLen=30, corThick=2, rectThick=1,
               rectColor=(255, 255, 255), corColor=(255, 0, 255)):
    """
    Draw the rectangle with corners on image

    :param img: Image to draw rectangle on.
    :param bbox: Bounding box [x, y, w, h]
    :param drawRect: Flag to draw the rectangle
    :param corLen: Length of rectangle corners
    :param corThick: thickness of rectangle corners
    :param rectThick: thickness of the rectangle
    :param rectColor: Color of the Rectangle
    :param corColor: Color of rectangle corners
    :return: Image with rectangle
    """
    x, y, w, h = bbox
    x1, y1 = x + w, y + h
    if rectThick != 0 and drawRect:
        cv2.rectangle(img, bbox, rectColor, rectThick)
    # Top Left  x,y
    cv2.line(img, (x, y), (x + corLen, y), corColor, corThick)
    cv2.line(img, (x, y), (x, y + corLen), corColor, corThick)
    # Top Right  x1,y
    cv2.line(img, (x1, y), (x1 - corLen, y), corColor, corThick)
    cv2.line(img, (x1, y), (x1, y + corLen), corColor, corThick)
    # Bottom Left  x,y1
    cv2.line(img, (x, y1), (x + corLen, y1), corColor, corThick)
    cv2.line(img, (x, y1), (x, y1 - corLen), corColor, corThick)
    # Bottom Right  x1,y1
    cv2.line(img, (x1, y1), (x1 - corLen, y1), corColor, corThick)
    cv2.line(img, (x1, y1), (x1, y1 - corLen), corColor, corThick)

    return img


def findContours(img, imgPre, minArea=1000, sort=True, filter=0, drawContours=True, color=(255, 0, 0)):
    """
    Finds Contours in an image.

    :param img: Image on which we want to draw
    :param imgPre: Image on which we want to find contours
    :param minArea: Minimum Area to detect as valid contour
    :param sort: True will sort the contours by area (biggest first)
    :param filter: Filters based on the corner points e.g. 4 = Rectangle or square
    :param drawContours: draw contours boolean
    :param color: Color of the contours and shapes
    :return: Foudn contours with [contours, Area, BoundingBox, Center]
    """
    conFound = []
    imgContours = img.copy()
    contours, hierarchy = cv2.findContours(imgPre, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > minArea:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # print(len(approx))
            if len(approx) == filter or filter == 0:
                if drawContours: cv2.drawContours(imgContours, cnt, -1, color, 3)
                x, y, w, h = cv2.boundingRect(approx)
                cx, cy = x + (w // 2), y + (h // 2)
                cv2.rectangle(imgContours, (x, y), (x + w, y + h), color, 2)
                cv2.circle(imgContours, (x + (w // 2), y + (h // 2)), 5, color, cv2.FILLED)
                conFound.append({"cnt": cnt, "area": area, "bbox": [x, y, w, h], "center": [cx, cy]})

    if sort:
        conFound = sorted(conFound, key=lambda x: x["area"], reverse=True)

    return imgContours, conFound


def PNGOverlay(imgBack, imgFront, pos=[0, 0]):
    hf, wf, cf = imgFront.shape
    hb, wb, cb = imgBack.shape
    *_, mask = cv2.split(imgFront)
    maskBGRA = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGRA)
    maskBGR = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    imgRGBA = cv2.bitwise_and(imgFront, maskBGRA)
    imgRGB = cv2.cvtColor(imgRGBA, cv2.COLOR_BGRA2BGR)

    imgMaskFull = np.zeros((hb, wb, cb), np.uint8)
    imgMaskFull[pos[1]:hf + pos[1], pos[0]:wf + pos[0], :] = imgRGB
    imgMaskFull2 = np.ones((hb, wb, cb), np.uint8) * 255
    maskBGRInv = cv2.bitwise_not(maskBGR)
    imgMaskFull2[pos[1]:hf + pos[1], pos[0]:wf + pos[0], :] = maskBGRInv

    imgBack = cv2.bitwise_and(imgBack, imgMaskFull2)
    imgBack = cv2.bitwise_or(imgBack, imgMaskFull)

    return imgBack


def imageRotate(img, angle, scale=1):
    h, w = img.shape[:2]
    center = (w / 2, h / 2)
    rotate_matrix = cv2.getRotationMatrix2D(center=center, angle=angle, scale=scale)
    img = cv2.warpAffine(src=img, M=rotate_matrix, dsize=(w, h))
    return img


def putRectText(img, text, pos, scale=3, textThick=3, textColor=(255, 255, 255),
                rectColor=(255, 0, 255), font=cv2.FONT_HERSHEY_PLAIN,
                offset=10, border=None, borderColor=(0, 255, 0)):
    """
    Creates Text with Rectangle Background.

    :param img: Image to put text rect on
    :param text: Text inside the rectangle
    :param pos: Starting position of the rect x1,y1
    :param scale: Scale of the text
    :param textThick: Thickness of the text
    :param textColor: Color of the Text
    :param rectColor: Color of the Rectangle
    :param font: Font used. Must be cv2.FONT....
    :param offset: Clearance around the text
    :param border: Outline around the rect
    :param borderColor: Color of the outline
    :return: image, rect (x1,y1,x2,y2)
    """
    ox, oy = pos
    (w, h), _ = cv2.getTextSize(text, font, scale, textThick)

    x1, y1, x2, y2 = ox - offset, oy + offset, ox + w + offset, oy - h - offset

    cv2.rectangle(img, (x1, y1), (x2, y2), rectColor, cv2.FILLED)
    if border is not None:
        cv2.rectangle(img, (x1, y1), (x2, y2), borderColor, border)
    cv2.putText(img, text, (ox, oy), font, scale, textColor, textThick)

    return img, [x1, y2, x2, y1]


def main():
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        img, bbox = putRectText(img, "pycamdetector", [50, 50], 2, 2, offset=10, border=5)
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imageList = [img, img, imgGray, img, imgGray]
        imgStacked = imagesStack(imageList, 2, 0.5)

        cv2.imshow("Stacked Images", imgStacked)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()