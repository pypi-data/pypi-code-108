import os

from galleries.gallery import Gallery
from galleries.igallery import IGallery


class GalleriesManagement:

    _galleries_extension = '.glr'
    _galleries_folder = ''

    @staticmethod
    def get_galleries_folder():
        return GalleriesManagement._galleries_folder

    @staticmethod
    def get_gallery_data_folder(gallery_name: str):
        folder = os.path.join(GalleriesManagement._galleries_folder, f"{gallery_name}_data")
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

    @staticmethod
    def set_galleries_folder(folder: str):
        GalleriesManagement._galleries_folder = folder

    @staticmethod
    def load_galleries(folder: str = None):
        galleries_folder = folder or GalleriesManagement._galleries_folder
        for subdir, dirs, files in os.walk(galleries_folder):
            for filename in files:
                file_path = os.path.join(subdir, filename)
                if GalleriesManagement.is_file_gallery(file_path):
                    gallery_name, _ = os.path.splitext(filename)
                    gallery = IGallery.read_gallery(file_path)
                    yield gallery_name, gallery

    @staticmethod
    def get_gallery_file_path(gallery_name: str) -> str:
        galleries_folder = GalleriesManagement._galleries_folder
        galleries_extension = GalleriesManagement._galleries_extension
        gallery_path = os.path.join(galleries_folder, f'{gallery_name}{galleries_extension}')
        return gallery_path

    @staticmethod
    def save_gallery(gallery_name: str, gallery: Gallery):
        gallery_path = GalleriesManagement.get_gallery_file_path(gallery_name)
        Gallery.write_gallery(gallery, gallery_path)

    @staticmethod
    def remove_gallery_by_name(gallery_name: str):
        gallery_path = GalleriesManagement.get_gallery_file_path(gallery_name)
        if os.path.exists(gallery_path):
            os.remove(gallery_path)

    @staticmethod
    def is_file_gallery(file_path: str) -> bool:
        galleries_extension = GalleriesManagement._galleries_extension
        return file_path.endswith(galleries_extension)
