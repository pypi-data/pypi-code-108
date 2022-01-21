import unittest
import os

from cv_aid import Frame
import numpy as np
import cv2

base_path = os.path.dirname(__file__)


class Test(unittest.TestCase):
    def test_frame_constructor(self):
        frame = Frame.load(f"{base_path}/test.webp")
        self.assertEqual(frame.width, 400)
        self.assertEqual(frame.height, 600)

    def test_frame_save(self):
        frame = Frame.load(f"{base_path}/test.webp")
        frame.save(base_path, "test_save.webp")
        self.assertTrue(os.path.exists(f"{base_path}/test_save.webp"))
        os.remove(f"{base_path}/test_save.webp")

    def test_frame_resize(self):
        frame = Frame.load(f"{base_path}/test.webp")
        frame = frame.resize(width=None, height=100)
        self.assertEqual(frame.width, 400)
        self.assertEqual(frame.height, 100)

    def test_frame_rotate_same_dim(self):
        frame = Frame.load(f"{base_path}/test.webp")
        frame = frame.rotate(90)
        rotated = Frame.load(f"{base_path}/test_rotated.webp")
        self.assertEqual(np.array_equal(frame.frame, rotated.frame), True)

    def test_frame_rotate_different_dim(self):
        frame = Frame.load(f"{base_path}/test.webp")
        frame = frame.rotate(0, same_dim=False)
        self.assertEqual(frame.width, 600)
        self.assertEqual(frame.height, 400)

    def test_frame_crop(self):
        frame = Frame.load(f"{base_path}/test.webp")
        frame = frame.crop(x=0, y=0, width=100, height=100)
        self.assertEqual(frame.width, 100)
        self.assertEqual(frame.height, 100)

    def test_frame_gray(self):
        frame = Frame.load(f"{base_path}/test.webp")
        frame = frame.gray()
        self.assertEqual(frame.frame.shape, (600, 400))

    def test_frame_blur(self):
        frame = Frame.load(f"{base_path}/test.webp")
        frame = frame.blur((5, 5))
        variance = cv2.Laplacian(frame.frame, cv2.CV_64F).var()
        self.assertLess(variance, 100.0)

    def test_frame_canny(self):
        frame = Frame.load(f"{base_path}/test.webp")
        frame = frame.canny(100, 200)
        self.assertEqual(frame.frame.shape, (600, 400))

    def test_frame_line(self):
        frame = Frame.load(f"{base_path}/test.webp")
        frame = frame.line((0, 0), (100, 100), thickness=5)
        lined = Frame.load(f"{base_path}/test_line.webp")
        self.assertEqual(np.array_equal(frame.frame, lined.frame), True)
