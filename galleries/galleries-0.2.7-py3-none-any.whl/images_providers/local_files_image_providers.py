import cv2 as cv
from propsettings.configurable import register_as_setting
from propsettings.setting_types.path_setting_type import Path

from galleries import files_utils
from galleries.images_providers.gallery_images_provider import GalleryImagesProvider


class LocalFilesImageProvider(GalleryImagesProvider):

    def __init__(self,  directory="", recursive=False):
        self._directory = directory
        self._recursive = recursive

    @property
    def directory(self):
        return self._directory

    @directory.setter
    def directory(self, value):
        self._directory = value

    @property
    def recursive(self):
        return self._recursive

    @recursive.setter
    def recursive(self, value):
        self._recursive = value

    def get_indices(self):
        return files_utils.list_images(self._directory, recursive=self._recursive)

    def get_image_by_index(self, img_index):
        img_path: str = img_index
        return cv.imread(img_path)


register_as_setting(LocalFilesImageProvider, "_directory", setting_type=Path(True, []))
register_as_setting(LocalFilesImageProvider, "_recursive")
