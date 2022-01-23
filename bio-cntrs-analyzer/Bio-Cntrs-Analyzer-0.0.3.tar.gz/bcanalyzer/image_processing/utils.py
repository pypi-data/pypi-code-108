
import cv2
import numpy as np

from bisect import bisect_left


def approximateContours(threshold):

    contours, _ = cv2.findContours(
        threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        print('not contours')
        return np.zeros(threshold.shape, dtype=np.uint8)

    contours.sort(key=cv2.contourArea)

    epsilon = 0.001*cv2.arcLength(contours[-1], True)
    approx_contours = []

    for cnt in contours:
        approx_contours.append(
            cv2.approxPolyDP(cnt, epsilon, True)
        )

    blank_mask = np.zeros(threshold.shape, dtype=np.uint8)
    cv2.fillPoly(blank_mask, approx_contours, (255, 255, 255))

    return blank_mask


def getLargestContour(thresh):
    # RETURNS: largest contour and its area

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:
        cnt = max(contours, key=cv2.contourArea)
        return cnt, cv2.contourArea(cnt)

    else:
        return 0, 0


def getLargestContourThresh(thresh):
    '''
    RETURNS: removes all contours except the largest
    '''

    blank_mask = np.zeros(thresh.shape, dtype=np.uint8)
    largest_cnt, area = getLargestContour(thresh)

    if area:
        cv2.fillPoly(blank_mask, [largest_cnt], (255, 255, 255))

    return blank_mask


def invertByMask(img, mask):
    # RETURNS: image with mask filtered inverted color areas

    if mask.max() == 1:
        mask = 255*mask
    inverted = cv2.bitwise_not(img)
    foreground = cv2.bitwise_or(inverted, inverted, mask=mask)

    mask = cv2.bitwise_not(mask)
    background = cv2.bitwise_or(img, img, mask=mask)

    final = cv2.bitwise_or(foreground, background)

    return final


def showDifference(img, reference_mask, compared_mask):
    # RETURNS: markes by invertion difference between two masks on image

    new_mask = cv2.bitwise_xor(reference_mask, compared_mask)
    new_mask = cv2.bitwise_not(new_mask)

    return invertByMask(img, new_mask)


# ---------------------{ utilites }---------------------

def getMaxValueIndex(arr):
    'use only on 1D numpy arrays'
    if not arr.size:
        print('in function \'getMaxValueIndexes\': wrong input ')
        raise ValueError

    max_value = max(arr)
    result = np.where(arr == max_value)

    return result[0][0]  # will return left largest index


def find_ge(arr, x):
    'Find leftmost item greater than or equal to x'
    i = bisect_left(arr, x)
    if i != len(arr):
        return arr[i]
    raise ValueError
