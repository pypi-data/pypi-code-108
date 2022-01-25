import numpy as np
from media_processing_lib.image import image_resize_batch
from .deterministic_augmentation import DeterministicAugmentation
from ...logger import logger

class RandomZoom(DeterministicAugmentation):
    def __init__(self, percent_usage: float, max_percent_cut: float, seed: int=None, num_precomputted: int=100):
        super().__init__(seed, num_precomputted)
        self.max_percent_cut = max_percent_cut
        self.percent_usage = percent_usage

    def __call__(self, data):
        super().__call__()
        if np.random.random() > self.percent_usage / 100:
            logger.debug2("Skipping RandomZoom")
            return data

        # Generate the percentage tuples of top left and bottom right
        top_left_percent = np.random.random(size=(2, )) * self.max_percent_cut / 100
        bottom_right_percent = 1 - (np.random.random(size=(2, )) * self.max_percent_cut / 100)

        # Convert the data into a single concatenated array and remember where the initial indexes where
        split_ix = np.cumsum([y.shape[-1] for y in data[0: -1]])
        # MB x H x W x sum(ND)
        data = np.concatenate(data, axis=-1)
        h, w = data.shape[1 : 3]

        # Converting percentagers to pixel positions
        top_left = (top_left_percent * [h, w]).astype(int)
        bottom_right = (bottom_right_percent * [h, w]).astype(int)
        # Getting the zoomed data via slicing at the desired positions and resize back to original shape
        zoomed_data = data[:, top_left[0] : bottom_right[0], top_left[1] : bottom_right[1]]
        resized_data = image_resize_batch(zoomed_data, height=h, width=w, interpolation="nearest", only_uint8=False)

        # Split data back
        split_back = np.split(resized_data, split_ix, axis=-1)
        return split_back
