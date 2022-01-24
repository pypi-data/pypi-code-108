import copy
import pytest
import torch

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import DatasetProcessingType, \
    CommonObjectDetectionDatasetWrapper
from azureml.automl.dnn.vision.object_detection.data.tiling_distributed_sampler import TilingDistributedSampler

from ..common.run_mock import ObjectDetectionDatasetMock


class TestTilingDistributedSampler:

    def _create_dataset(self, num_images, num_tiles):
        dataset_items = []
        base_dataset_item = (
            None,
            {"boxes": torch.tensor([[0, 0, 300, 200], [300, 200, 600, 400]], dtype=torch.float32),
             "labels": torch.tensor([0, 0], dtype=torch.int64)},
            {"areas": [60000, 60000], "iscrowd": [0, 0], "filename": "image.jpg",
             "height": 400, "width": 600})
        for idx in range(num_images):
            current_item = copy.deepcopy(base_dataset_item)
            current_item[2]["filename"] = "image_{}.jpg".format(idx)
            dataset_items.append(current_item)
            for tile_idx in range(num_tiles):
                current_tile_item = copy.deepcopy(base_dataset_item)
                current_tile_item[2]["filename"] = "image_{}.jpg".format(idx)
                current_tile_item[2]["tile"] = (tile_idx, tile_idx, 100, 100)
                dataset_items.append(current_tile_item)
        dataset = ObjectDetectionDatasetMock(dataset_items, num_classes=5)
        return dataset

    def test_init(self):
        # Init with dataset wrapper processing only images should fail
        dataset = self._create_dataset(4, 3)
        dataset_wrapper = CommonObjectDetectionDatasetWrapper(
            dataset, dataset_processing_type=DatasetProcessingType.IMAGES)
        with pytest.raises(AutoMLVisionSystemException):
            TilingDistributedSampler(dataset_wrapper, num_replicas=4, rank=0)

        # drop_last=True is not supported
        dataset_wrapper = CommonObjectDetectionDatasetWrapper(
            dataset, dataset_processing_type=DatasetProcessingType.IMAGES_AND_TILES)
        with pytest.raises(AutoMLVisionSystemException):
            TilingDistributedSampler(dataset_wrapper, num_replicas=4, rank=0, drop_last=True)

        # drop_last=False should succeed.
        TilingDistributedSampler(dataset_wrapper, num_replicas=4, rank=0, drop_last=False)

    @pytest.mark.parametrize("shuffle", [True, False])
    def test_dataset_image_and_tiles_processed_on_single_worker(self, shuffle):
        num_images = 8
        num_tiles = 4
        num_workers = 4

        # Create samplers for each worker
        worker_sampler_list = []
        for rank in range(num_workers):
            dataset = self._create_dataset(num_images, num_tiles)
            dataset_wrapper = CommonObjectDetectionDatasetWrapper(
                dataset, dataset_processing_type=DatasetProcessingType.IMAGES_AND_TILES)
            tiling_distributed_sampler = TilingDistributedSampler(dataset_wrapper, num_replicas=num_workers,
                                                                  rank=rank, shuffle=shuffle)
            worker_sampler_list.append(tiling_distributed_sampler)

        # Test that entire image and all tiles from the image are processed on same worker
        # across invocations to iter(). In normal training loop, iter() is invoked once each epoch.
        images_per_worker = {}
        for epoch in range(10):
            for worker_idx, sampler in enumerate(worker_sampler_list):
                sampler.set_epoch(epoch)
                sampled_indices = list(iter(sampler))

                # Each worker should sample 8 (num_images)/ 4 (num_workers) images and its tiles
                assert len(sampled_indices) == 10  # 2 images and 4 tiles for each image
                sampled_images_set = set()
                sampled_tiles = []
                for idx in sampled_indices:
                    dataset_item = dataset_wrapper[idx]
                    sampled_images_set.add(dataset_item[2]["filename"])
                    if "tile" in dataset_item[2]:
                        sampled_tiles.append((dataset_item[2]["filename"], dataset_item[2]["tile"]))
                assert len(sampled_images_set) == 2
                assert len(sampled_tiles) == 8

                # if shuffle is True, the images sampled in current epoch should be different from
                # previous epoch.
                if shuffle and epoch != 0:
                    assert sampled_images_set != images_per_worker[worker_idx]
                images_per_worker[worker_idx] = sampled_images_set

            # The workers in total should process all the images
            total_images_from_all_workers = []
            for entry in images_per_worker.values():
                total_images_from_all_workers.extend(entry)
            assert len(total_images_from_all_workers) == 8
