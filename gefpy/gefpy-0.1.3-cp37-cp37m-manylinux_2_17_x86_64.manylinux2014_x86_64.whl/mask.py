import tifffile
import cv2 as cv
import numpy as np

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

inv_small = 0.000000000001


class Polygen(object):
    def __init__(self, points):
        self.border = None
        self.center = None
        self.area = None
        self._init(points)

    def _init(self, points, points_len=16):
        if len(points) > points_len:points = cv.approxPolyDP(points, 0.01 * cv.arcLength(points, True), True)
        self.border = np.squeeze(points)
        if self.border.ndim == 1:
            self.border = self.border.reshape((1, 2))
        mu = cv.moments(points, False)
        m = (inv_small + mu['m00'])
        self.center = (int(mu['m10'] / m), int(mu['m01'] / m))

        if self.border.shape[0] == 1:
            # logger.info("self.border 1: {}".format(self.center))
            self.center = (self.border[0][0], self.border[0][1])
        elif self.border.shape[0] == 2:
            self.center = (int((self.border[0][0] + self.border[1][0])/2.0), int((self.border[0][1] + self.border[1][1])/2.0))

        self.area = cv.contourArea(points)


class Mask(object):
    def __init__(self, file_path):
        self.polygens = None
        self.region = None
        self.count = None
        self.mask_shape = None
        self._init(file_path)

    def _init(self, file_path):
        mask = tifffile.imread(file_path)
        logger.info('Load \'{}\' completed.'.format(file_path))
        mask = np.where(mask != 0, 1, 0).astype(np.uint8)
        self.mask_shape = mask.shape
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        self.polygens = list()
        # rects = list()
        for i, c in enumerate(contours):
            # rect = cv.boundingRect(c)
            # rects.append([rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]])
            self.polygens.append(Polygen(c))
        # self.count = len(rects)
        # rects = np.array(rects)
        # xmin = np.min(rects[:, 0])
        # ymin = np.min(rects[:, 1])
        # xmax = np.max(rects[:, 2])
        # ymax = np.max(rects[:, 3])
        # self.region = (xmin, ymin, xmax, ymax)
        # logger.info(
        #     '[MaskShape, PolygenCount, RegionOfInterest]: {}, {}, {}.'.format(mask.shape[:2], self.count, self.region))

    def get_polygen_by_index(self, ind):
        if ind < self.count:
            return self.polygens[ind]
        else:
            return None


def main():
    gem = Mask(
        '/Users/huangzhibo/workitems/13.github/gefpy/test_data/FP200000617TL_B6_mask.tif')
    # cell = gem.get_polygen_by_index(10000)
    # print(cell.area)


if __name__ == '__main__':
    main()
