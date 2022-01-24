# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class to make sure each image and its corresponding tiles are processed by the same worker."""
import torch
import math

from torch.utils.data import Sampler
from torch.utils.data.distributed import DistributedSampler

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import DatasetProcessingType, \
    CommonObjectDetectionDatasetWrapper


class TilingDistributedSampler(Sampler):
    """Class to make sure each image and its corresponding tiles are processed by the same worker.

    First, an dataset wrapper is created to process only images.
    To create an iter, a DistributedSampler based on this image dataset wrapper is used to sample images
    to be processed by each worker.
    Then on each worker, the list of indices to be processed is obtained by adding the data points
    (both images and tiles) corresponding to these images.

    Note (Important!!!):
    - The sampler will result in uneven number of data points (and hence uneven batches) across workers. This is
    because different images will have different number of tiles, as only the tiles containing grouth truth boxes
    are processed
    - On a single worker, each iter call can result in different number of data points processed. This is because
    the images sampled by DistributedSampler will be different in each iter call.
    """

    DROP_LAST = "drop_last"

    def __init__(self, dataset_wrapper, **kwargs):
        """
        :param dataset_wrapper: Dataset wrapper
        :type dataset_wrapper: CommonObjectDetectionDatasetWrapper
        :param kwargs: kwargs to specify arguments supported by DistributedSampler
        :type kwargs: dict
        """

        if dataset_wrapper.dataset_processing_type != DatasetProcessingType.IMAGES_AND_TILES:
            raise AutoMLVisionSystemException("only dataset wrapper with processing type images_and_tiles "
                                              "is supported with TilingDistributedSampler", has_pii=False)

        if TilingDistributedSampler.DROP_LAST in kwargs:
            drop_last = kwargs.get(TilingDistributedSampler.DROP_LAST)
            if drop_last:
                raise AutoMLVisionSystemException(
                    "drop_last is not yet supported for TilingDistributedSampler", has_pii=False)

        self._dataset_wrapper = dataset_wrapper
        self._image_dataset_wrapper = CommonObjectDetectionDatasetWrapper(
            dataset=self._dataset_wrapper.dataset, dataset_processing_type=DatasetProcessingType.IMAGES)
        self._image_dataset_dist_sampler = DistributedSampler(dataset=self._image_dataset_wrapper, **kwargs)

        # This value of num_samples is an approximate estimate. This value will change from iter to iter
        # based on the images sampler by _image_dataset_dist_sampler in each iter call. The actual value
        # is updated in the __iter__ function.
        self.num_samples = math.ceil(len(self._dataset_wrapper) / self._image_dataset_dist_sampler.num_replicas)

    def __iter__(self):
        """ Create an iterator.

        :return: Iterator
        :rtype: iterator
        """
        image_dataset_iter = iter(self._image_dataset_dist_sampler)
        # Get the list of indices for dataset elements corresponding to the
        # images selected for this worker by the image_dataset_sampler
        indices = []
        for image_index in image_dataset_iter:
            image_url = self._image_dataset_wrapper.dataset.get_image_url_at_index(image_index)
            image_tile_indices = self._dataset_wrapper.get_indices_for_image(image_url)
            indices.extend(image_tile_indices)

        # Shuffle: The following logic is similar to the shuffle logic in DistributedSampler.
        if self._image_dataset_dist_sampler.shuffle:
            # deterministically shuffle based on epoch and seed
            g = torch.Generator()
            g.manual_seed(self._image_dataset_dist_sampler.seed + self._image_dataset_dist_sampler.epoch)
            indices_tensor = torch.tensor(indices)
            indices = indices_tensor[torch.randperm(len(indices), generator=g)].tolist()

        self.num_samples = len(indices)
        return iter(indices)

    def __len__(self):
        """Get the number of samples. Please note that this value changes for each iter call.

        :return: Number of samples.
        :rtype: int
        """
        return self.num_samples

    def set_epoch(self, epoch):
        """Set epoch.

        :param epoch: Epoch
        :type epoch: int
        """
        self._image_dataset_dist_sampler.set_epoch(epoch)
