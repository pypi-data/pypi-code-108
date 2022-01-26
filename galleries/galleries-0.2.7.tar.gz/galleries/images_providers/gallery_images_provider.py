import abc


class GalleryImagesProvider(abc.ABC):

    @abc.abstractmethod
    def get_indices(self):
        pass

    @abc.abstractmethod
    def get_image_by_index(self, img_index):
        pass
