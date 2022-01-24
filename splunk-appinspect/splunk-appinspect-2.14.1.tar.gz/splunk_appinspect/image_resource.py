"""Splunk app image file abstraction resource module"""

from PIL import Image

from .file_resource import FileResource


class ImageResource(FileResource):
    """store metadata of an image file in app"""

    def __init__(self, image_path):
        """This only supports PNG/JPEG/GIF image formats, and will thrown NotImplementedError for non supported formats"""
        FileResource.__init__(self, image_path)
        self.image_path = image_path
        self.meta = Image.open(self.image_path)

    def dimensions(self):
        return self.meta.size

    def is_png(self):
        return self.meta.format == "PNG"

    def content_type(self):
        return self.meta.format
