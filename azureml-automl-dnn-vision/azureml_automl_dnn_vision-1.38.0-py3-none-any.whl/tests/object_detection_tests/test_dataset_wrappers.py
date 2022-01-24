import json
import os

import pytest
import torch

from PIL import Image

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException, AutoMLVisionSystemException
from azureml.automl.dnn.vision.object_detection.data.datasets import FileObjectDetectionDataset, \
    AmlDatasetObjectDetection
from azureml.automl.dnn.vision.object_detection.eval.utils import prepare_dataset_for_eval
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import \
    CommonObjectDetectionDatasetWrapper, DatasetProcessingType
from azureml.automl.dnn.vision.object_detection.common.augmentations import transform

from .aml_dataset_mock import AmlDatasetMock
from .test_datasets import TestAmlDatasetObjectDetection


@pytest.mark.usefixtures('new_clean_dir')
class TestCommonObjectDetectionDatasetWrapper:
    def _read_annotations_file(self, annotations_file):
        annotations = []

        with open(annotations_file, "r") as json_file:
            for line in json_file:
                annotations.append(json.loads(line))
        return annotations

    def test_missing_annotations(self):
        missing_annotations_file = 'object_detection_data/annotation_missing_image_dimensions.json'
        image_root = 'object_detection_data/images'
        dataset = FileObjectDetectionDataset(annotations_file=missing_annotations_file, image_folder=image_root)
        dataset_wrapper = CommonObjectDetectionDatasetWrapper(dataset, DatasetProcessingType.IMAGES)

        assert len(dataset_wrapper) == 1
        image, boxes_labels_dict, details = dataset_wrapper[0]

        assert details['width'] > 100
        assert details['height'] > 100

        box = boxes_labels_dict['boxes'][0]
        assert all([box[0].item() > 1 and box[1].item() > 1 and box[2].item() > 1 and box[3].item() > 1])

    def test_all_images_in_annotations_are_ill_formed(self):
        missing_annotations_file = 'object_detection_data/annotation_all_images_ill_formed.json'
        image_root = 'object_detection_data/images'
        with pytest.raises(AutoMLVisionDataException):
            FileObjectDetectionDataset(annotations_file=missing_annotations_file, image_folder=image_root)

    def test_transform_when_training(self):
        annotations_file = 'object_detection_data/annotation_missing_image_dimensions.json'
        image_root = 'object_detection_data/images'

        annotations = self._read_annotations_file(annotations_file)
        image_url = os.path.join(image_root, annotations[0]['imageUrl'])
        image = Image.open(image_url).convert('RGB')
        train_dataset = FileObjectDetectionDataset(annotations_file=annotations_file,
                                                   image_folder=image_root,
                                                   is_train=True)
        train_dataset_wrapper = CommonObjectDetectionDatasetWrapper(train_dataset, DatasetProcessingType.IMAGES)

        transformed_image, boxes_labels_dict, details = train_dataset_wrapper[0]
        assert details['width'] * details['height'] > image.width * image.height * 0.6
        bbox_area = (boxes_labels_dict['boxes'][0][2] - boxes_labels_dict['boxes'][0][0]) * \
                    (boxes_labels_dict['boxes'][0][3] - boxes_labels_dict['boxes'][0][1])
        assert int(details['areas'][0]) == int(bbox_area)

    def test_transform_with_bad_boxes(self):
        annotations_file = 'object_detection_data/annotation_bad_box_coordinates.json'
        image_root = 'object_detection_data/images'

        annotations = self._read_annotations_file(annotations_file)
        image_url = os.path.join(image_root, annotations[0]['imageUrl'])
        image = Image.open(image_url).convert('RGB')

        width, height = image.width, image.height
        bounding_box = [annotations[0]['label']['topX'] * width,
                        annotations[0]['label']['topY'] * height,
                        annotations[0]['label']['bottomX'] * width,
                        annotations[0]['label']['bottomY'] * height]
        boxes = torch.as_tensor(bounding_box, dtype=torch.float32).unsqueeze(0)
        # data augmentations
        transformed_image, transformed_boxes, areas, height, width, _ = transform(
            image=image,
            boxes=boxes,
            is_train=True,
            prob=1.0,
            post_transform=None)

        assert any(coord < 0 for coord in transformed_boxes[0])
        bbox_area = (transformed_boxes[0][2] - transformed_boxes[0][0]) * \
                    (transformed_boxes[0][3] - transformed_boxes[0][1])
        assert int(areas[0]) == int(bbox_area.data)

    def test_common_object_detection_dataset_wrapper(self):

        def _test(bbox_list, tile_grid_size, dataset_processing_type, valid, expected_num_images, expected_num_tiles,
                  expected_indices_for_images):
            mockworkspace, test_dataset_id, test_files_full_path, test_labels \
                = TestAmlDatasetObjectDetection._build_dataset_with_bbox_list(bbox_list)
            try:
                dataset = AmlDatasetObjectDetection(test_dataset_id,
                                                    workspace=mockworkspace,
                                                    datasetclass=AmlDatasetMock,
                                                    tile_grid_size=tile_grid_size,
                                                    tile_overlap_ratio=0.25)
                dataset_wrapper = CommonObjectDetectionDatasetWrapper(dataset, dataset_processing_type)

                # Test init
                assert valid
                assert dataset_wrapper.dataset == dataset
                assert dataset_wrapper.dataset_processing_type == dataset_processing_type

                # Test len()
                assert len(dataset_wrapper) == expected_num_images + expected_num_tiles

                # Test get_item()
                num_images = 0
                num_tiles = 0
                for image, target, image_info in dataset_wrapper:
                    assert image is not None
                    assert target is not None
                    assert image_info is not None
                    if "tile" in image_info:
                        num_tiles += 1
                    else:
                        num_images += 1
                assert num_images == expected_num_images
                assert num_tiles == expected_num_tiles

                # Test get_indices_for_image
                for idx, image_url in enumerate(test_files_full_path):
                    indices_for_image = dataset_wrapper.get_indices_for_image(image_url)
                    assert indices_for_image == expected_indices_for_images[idx]
                    for dataset_wrapper_index in indices_for_image:
                        _, _, image_info = dataset_wrapper[dataset_wrapper_index]
                        assert image_info["filename"] == image_url

            except AutoMLVisionSystemException:
                assert not valid
            finally:
                for test_file in test_files_full_path:
                    os.remove(test_file)

        # Two images with one bbox each
        bbox_list = [[[0.0, 0.0, 0.5, 0.5]], [[0.5, 0.5, 1.0, 1.0]]]
        # Dataset without tiles + DatasetProcessingType.IMAGES
        _test(bbox_list, None, DatasetProcessingType.IMAGES, True, 2, 0, [[0], [1]])

        # Dataset with tiles + DatasetProcessingType.IMAGES
        _test(bbox_list, (3, 2), DatasetProcessingType.IMAGES, True, 2, 0, [[0], [1]])

        # Dataset with tiles + DatasetProcessingType.IMAGES_AND_TILES
        # 4 tiles overlapping ground truth boxes in each image
        _test(bbox_list, (3, 2), DatasetProcessingType.IMAGES_AND_TILES, True, 2, 8,
              [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])

        # Dataset without tiles + DatasetProcessingType.IMAGES_AND_TILES
        _test(bbox_list, None, DatasetProcessingType.IMAGES_AND_TILES, False, None, None, None)

    def test_filter_invalid_crowd_dataset(self):

        def _get_dataset_wrapper(annotation_file):
            data_root = 'object_detection_data'
            annotation_file = os.path.join(data_root, annotation_file)
            image_folder = os.path.join(data_root, 'images')

            dataset = FileObjectDetectionDataset(annotations_file=annotation_file,
                                                 image_folder=image_folder,
                                                 ignore_data_errors=True)
            dataset_wrapper = CommonObjectDetectionDatasetWrapper(dataset,
                                                                  DatasetProcessingType.IMAGES)
            return dataset_wrapper

        # expect AutoMLVisionDataException for invalid dataset wrapper
        invalid_dataset_wrapper = _get_dataset_wrapper('annotation_all_crowd.json')
        with pytest.raises(AutoMLVisionDataException):
            prepare_dataset_for_eval(invalid_dataset_wrapper)

        # validate for at least one non-crowd bounding boxes
        valid_dataset_wrapper = _get_dataset_wrapper('valid_annotations.json')
        assert prepare_dataset_for_eval(valid_dataset_wrapper) is not None
