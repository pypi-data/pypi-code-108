from .utils import get_tag_pixels


class Tag2Numpy:

    def __init__(self, tag_file_path, shape=None):
        self.tag_file_path = tag_file_path
        self.npy_array = None
        self.shape = shape

    def execute(self):
        self.npy_array = get_tag_pixels(self.tag_file_path)
        if self.shape is not None:
            self.npy_array = self.npy_array.reshape(self.shape)
        return self.npy_array
