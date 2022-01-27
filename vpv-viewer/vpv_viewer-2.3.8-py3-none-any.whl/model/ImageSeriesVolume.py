from .volume import Volume

class ImageSeriesVolume(Volume):
    """
    Contains a series of images
    """
    def __init__(self, *args):
        self.images = []
        super(ImageSeriesVolume, self).__init__(*args)
        self.levels = [float(self._arr_data.min()), float(self._arr_data.max())]

    def _load_data(self, paths, memmap=False):
        """
        :param path:
            multiple paths
        :param memmap:
        :return:
        """
        for path in paths:
            array = super(ImageSeriesVolume, self)._load_data(path, memmap)
            self.images.append(array)
        return self.images[0]

    def set_image(self, idx):
        self._arr_data = self.images[idx]

    def num_images(self):
        return len(self.images)
