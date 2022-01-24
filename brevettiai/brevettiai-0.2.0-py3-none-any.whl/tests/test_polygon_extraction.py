import unittest

import numpy as np
import cv2
from brevettiai.utils.polygon_utils import cv2_contour_to_shapely, simplify_polygon


def plot_mask_and_contours(mask, contours):
    import matplotlib.pyplot as plt
    plt.imshow(mask)
    for cnt in contours:
        try:
            plt.plot(*cnt.xy, 'b-x')
        except NotImplementedError:
            try:
                plt.plot(*cnt.boundary.xy, 'r-x')
            except NotImplementedError:
                for b in cnt.boundary:
                    plt.plot(*b.xy, 'g-x')
    plt.xlim(plt.xlim() + np.array([-1, 1]))
    plt.ylim(plt.ylim() + np.array([1, -1]))
    plt.show()


class TestPolygonExtraction(unittest.TestCase):
    def test_polygon_validity(self):
        mask = np.array([
            [0, 1, 0, 0, 0, 0, 1],
            [0, 0, 1, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 1],
            [0, 1, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 0, 1, 1, 1],
            [0, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0],
            [0, 1, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [1, 1, 0, 1, 1, 0, 0],
            [0, 1, 0, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 1, 1, 0],
            [1, 0, 0, 0, 1, 0, 0],
            [1, 0, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 1, 1],
            [1, 0, 0, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ], dtype=np.uint8)

        num_labels, labels = cv2.connectedComponents(mask)
        # https://docs.opencv.org/master/d9/d8b/tutorial_py_contours_hierarchy.html
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        polygons = [cv2_contour_to_shapely(x, resolution=2) for x in contours]

        #plot_mask_and_contours(labels, polygons)
        self.assertTrue(all(p.is_valid for p in polygons), "All polygons must be valid")

    def test_polygon_validity_random_field(self):
        mask = cv2.resize(np.random.randn(10, 10), (500, 500), interpolation=cv2.INTER_LANCZOS4)
        mask += cv2.resize(np.random.randn(51, 51), (500, 500), interpolation=cv2.INTER_LANCZOS4)
        mask += cv2.resize(np.random.randn(167, 167), (500, 500), interpolation=cv2.INTER_LANCZOS4)
        mask += 0.5*np.random.randn(500, 500)
        mask = (mask > 0.9).astype(np.uint8)

        num_labels, labels = cv2.connectedComponents(mask)
        # https://docs.opencv.org/master/d9/d8b/tutorial_py_contours_hierarchy.html
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        parent_info = hierarchy[0][:, 3]
        is_hole = parent_info != -1
        for ix, hole in enumerate(is_hole):
            if hole:
                is_hole[ix] = not is_hole[parent_info[ix]]

        polygons = [simplify_polygon(cv2_contour_to_shapely(cnt, hole=hole, resolution=2))
                    for cnt, hole in zip(contours, is_hole)]

        #plot_mask_and_contours(labels, polygons)
        self.assertTrue(all(p.is_valid for p in polygons), "All polygons must be valid")
