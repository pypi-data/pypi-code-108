import os
import sys
import unittest
from pathlib import Path
from typing import Generator

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cv_aid.utils import find_fonts, find_images, find_videos


class TestFonts(unittest.TestCase):
    """Test font"""

    def test_find_fonts(self):
        """Test find_fonts"""
        fonts = find_fonts(Path(os.path.dirname(__file__)))
        self.assertTrue(isinstance(fonts, Generator))
        self.assertTrue(len(list(fonts)) == 0)


class TestImages(unittest.TestCase):
    """Test image"""

    def test_find_images(self):
        """Test find_images"""
        images = find_images(Path(os.path.dirname(__file__)))
        self.assertTrue(isinstance(images, Generator))
        self.assertTrue(len(list(images)) == 7)


class TestVideo(unittest.TestCase):
    """Test video"""

    def test_find_videos(self):
        """Test find_videos"""
        videos = find_videos(Path(os.path.dirname(__file__)))
        self.assertTrue(isinstance(videos, Generator))
        self.assertTrue(len(list(videos)) == 0)
