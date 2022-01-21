import os
import sys
import unittest
import numpy as np
import cv2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cv_aid.utils import rotate, resize, concatenate, stack


class TestRotate(unittest.TestCase):
    """Test rotate"""

    def setup(self):
        """Setup"""
        self.img = cv2.imread(os.path.join(os.path.dirname(__file__), "test.webp"))

    def test_rotate(self):
        """Test rotate"""

        self.setup()
        rotated_90 = rotate(self.img, 90)
        rotated_90_loc = cv2.imread(
            os.path.join(os.path.dirname(__file__), "test_rotated.webp")
        )
        self.assertTrue(np.array_equal(rotated_90, rotated_90_loc))
        difference = cv2.subtract(rotated_90, rotated_90_loc)
        self.assertTrue(np.sum(difference) == 0)


class TestResize(unittest.TestCase):
    """Test resize"""

    def setup(self):
        """Setup"""
        self.img = cv2.imread(os.path.join(os.path.dirname(__file__), "test.webp"))

    def test_resize(self):
        """Test resize"""

        self.setup()
        resized = resize(self.img, width=None, height=100)
        self.assertTrue(resized.shape[0] == 100)


class TestConcatenate(unittest.TestCase):
    """Test concatenate"""

    def setup(self):
        """Setup"""
        self.img = cv2.imread(os.path.join(os.path.dirname(__file__), "egypt.webp"))
        self.img2 = cv2.imread(os.path.join(os.path.dirname(__file__), "egypt.webp"))

    def test_concatenate(self):
        """Test concatenate"""

        self.setup()
        concatenated = concatenate(self.img, self.img2)
        img_path = os.path.join(os.path.dirname(__file__), "test_concatenated.webp")
        concatenated_loc = cv2.imread(img_path)
        self.assertTrue(np.array_equal(concatenated, concatenated_loc))
        difference = cv2.subtract(concatenated, concatenated_loc)
        self.assertTrue(np.sum(difference) == 0)


class TestStack(unittest.TestCase):
    """Test stack"""

    def setup(self):
        """Setup"""
        self.img = cv2.imread(os.path.join(os.path.dirname(__file__), "egypt.webp"))
        self.img2 = cv2.imread(os.path.join(os.path.dirname(__file__), "egypt.webp"))

    def test_stack(self):
        """Test stack"""

        self.setup()
        stacked = stack([self.img, self.img2], cols=2)
        stacked_loc = cv2.imread(
            os.path.join(os.path.dirname(__file__), "test_stacked.webp")
        )
        self.assertTrue(np.array_equal(stacked, stacked_loc))
        difference = cv2.subtract(stacked, stacked_loc)
        self.assertTrue(np.sum(difference) == 0)


if __name__ == "__main__":
    unittest.main()
