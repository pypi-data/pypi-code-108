import os
import shutil

import pandas as pd
import pytest
import torch

from pytest import approx

from azureml.automl.dnn.vision.common.dataloaders import RobustDataLoader
from azureml.automl.dnn.vision.common.utils import _save_image_df
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException, AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper
from azureml.automl.dnn.vision.common.tiling_utils import get_tiles
from azureml.automl.dnn.vision.common.tiling_dataset_element import TilingDatasetElement
from azureml.automl.dnn.vision.object_detection.data.datasets import FileObjectDetectionDataset, \
    AmlDatasetObjectDetection, CommonObjectDetectionDataset
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import \
    CommonObjectDetectionDatasetWrapper, DatasetProcessingType

from .aml_dataset_mock import AmlDatasetMock, WorkspaceMock, DataflowMock, DataflowStreamMock


@pytest.mark.usefixtures('new_clean_dir')
class TestCommonObjectDetectionDataset:
    def test_missing_images(self):
        data_root = 'object_detection_data'
        image_root = os.path.join(data_root, 'images')
        annotation_file = os.path.join(data_root, 'missing_image_annotations.json')
        with pytest.raises(AutoMLVisionDataException):
            FileObjectDetectionDataset(annotations_file=annotation_file,
                                       image_folder=image_root,
                                       ignore_data_errors=False)

        dataset = FileObjectDetectionDataset(annotations_file=annotation_file,
                                             image_folder=image_root,
                                             ignore_data_errors=True)

        assert len(dataset) == 1

        # create missing image
        new_path = os.path.join(image_root, 'missing_image.jpg')
        shutil.copy(os.path.join(image_root, "000001517.png"), new_path)
        dataset = FileObjectDetectionDataset(annotations_file=annotation_file, image_folder=image_root,
                                             ignore_data_errors=True)
        dataset_wrapper = CommonObjectDetectionDatasetWrapper(dataset, DatasetProcessingType.IMAGES)
        os.remove(new_path)

        total_size = 0
        for images, _, _ in RobustDataLoader(dataset_wrapper, batch_size=100, num_workers=0):
            total_size += images.shape[0]

        assert total_size == 1

    def test_bad_annotations(self):
        data_root = 'object_detection_data'
        annotation_file = os.path.join(data_root, 'annotation_bad_line.json')
        image_folder = os.path.join(data_root, 'images')
        with pytest.raises(AutoMLVisionDataException):
            FileObjectDetectionDataset(annotations_file=annotation_file,
                                       image_folder=image_folder,
                                       ignore_data_errors=False)

        dataset = FileObjectDetectionDataset(annotations_file=annotation_file,
                                             image_folder=image_folder,
                                             ignore_data_errors=True)

        assert len(dataset) == 1

    def test_filter_invalid_bounding_boxes(self):
        num_valid_boxes = 5
        num_total_boxes = 10
        boxes = torch.rand(num_total_boxes, 4, dtype=torch.float32)
        labels = torch.randint(5, (num_total_boxes,), dtype=torch.int64)
        iscrowd = torch.randint(2, (num_total_boxes,), dtype=torch.int8).tolist()

        # Make first few boxes valid
        new_boxes = boxes.clone().detach()
        new_boxes[:num_valid_boxes, 0] = torch.min(boxes[:num_valid_boxes, 0], boxes[:num_valid_boxes, 2])
        new_boxes[:num_valid_boxes, 1] = torch.min(boxes[:num_valid_boxes, 1], boxes[:num_valid_boxes, 3])
        new_boxes[:num_valid_boxes, 2] = torch.max(boxes[:num_valid_boxes, 0], boxes[:num_valid_boxes, 2]) + 1
        new_boxes[:num_valid_boxes, 3] = torch.max(boxes[:num_valid_boxes, 1], boxes[:num_valid_boxes, 3]) + 1
        # rest invalid
        new_boxes[num_valid_boxes:, 0] = torch.max(boxes[num_valid_boxes:, 0], boxes[num_valid_boxes:, 2])
        new_boxes[num_valid_boxes:, 1] = torch.max(boxes[num_valid_boxes:, 1], boxes[num_valid_boxes:, 3])
        new_boxes[num_valid_boxes:, 2] = torch.min(boxes[num_valid_boxes:, 0], boxes[num_valid_boxes:, 2])
        new_boxes[num_valid_boxes:, 3] = torch.min(boxes[num_valid_boxes:, 1], boxes[num_valid_boxes:, 3])

        areas = ((new_boxes[:, 2] - new_boxes[:, 0]) * (new_boxes[:, 3] - new_boxes[:, 1])).tolist()

        def _validate_results(valid_boxes, valid_labels, valid_iscrowd, valid_areas):
            assert torch.equal(new_boxes[:num_valid_boxes], valid_boxes)
            assert torch.equal(labels[:num_valid_boxes:], valid_labels)
            assert len(valid_iscrowd) == num_valid_boxes
            assert len(valid_areas) == num_valid_boxes
            for idx in range(num_valid_boxes):
                assert iscrowd[idx] == valid_iscrowd[idx]
                assert areas[idx] == approx(valid_areas[idx], abs=1e-5)

        valid_boxes, valid_labels, valid_iscrowd, valid_areas, _ = \
            CommonObjectDetectionDataset._filter_invalid_bounding_boxes(new_boxes, labels, iscrowd, areas)
        _validate_results(valid_boxes, valid_labels, valid_iscrowd, valid_areas)


def _get_mockworkspace(test_files, test_labels, test_files_full_path, test_dataset_id):
    label_dataset_data = {
        'image_url': test_files,
        'label': test_labels
    }
    dataframe = pd.DataFrame(label_dataset_data)
    mockdataflowstream = DataflowStreamMock(test_files_full_path)
    mockdataflow = DataflowMock(dataframe, mockdataflowstream, 'image_url')
    mockdataset = AmlDatasetMock({}, mockdataflow, test_dataset_id)
    mockworkspace = WorkspaceMock(mockdataset)
    return mockworkspace


@pytest.mark.usefixtures('new_clean_dir')
class TestAmlDatasetObjectDetection:

    @staticmethod
    def _build_dataset(only_one_file=False):
        test_dataset_id = 'a7c014ec-474a-49f4-8ae3-09049c701913'
        test_file0 = 'a7c014ec-474a-49f4-8ae3-09049c701913-1.txt'
        if not only_one_file:
            test_file1 = 'a7c014ec-474a-49f4-8ae3-09049c701913-2.txt'
            test_files = [test_file0, test_file1]
        else:
            test_files = [test_file0]

        test_files_full_path = [os.path.join(AmlDatasetHelper.get_data_dir(),
                                             test_file) for test_file in test_files]
        test_label0 = [{'label': 'cat', 'topX': 0.1, 'topY': 0.9, 'bottomX': 0.2, 'bottomY': 1.0},
                       {'label': 'dog', 'topX': 0.5, 'topY': 0.5, 'bottomX': 0.6, 'bottomY': 0.6}]
        if not only_one_file:
            test_label1 = [{"label": "pepsi_symbol", "topX": 0.55078125, "topY": 0.53125,
                            "bottomX": 0.703125, "bottomY": 0.6611328125}]
            test_labels = [test_label0, test_label1]
        else:
            test_labels = [test_label0]

        mockworkspace = _get_mockworkspace(test_files, test_labels, test_files_full_path, test_dataset_id)
        return mockworkspace, test_dataset_id, test_files_full_path, test_labels

    @staticmethod
    def _build_dataset_missing_topX(only_one_file=False):
        test_dataset_id = 'a7c014ec-474a-49f4-8ae3-09049c701913'
        test_file0 = 'a7c014ec-474a-49f4-8ae3-09049c701913-1.txt'
        if not only_one_file:
            test_file1 = 'a7c014ec-474a-49f4-8ae3-09049c701913-2.txt'
            test_files = [test_file0, test_file1]
        else:
            test_files = [test_file0]

        test_files_full_path = [os.path.join(AmlDatasetHelper.get_data_dir(),
                                             test_file) for test_file in test_files]
        test_label0 = [{'label': 'cat', 'topY': 0.9, 'bottomX': 0.2, 'bottomY': 0.8},
                       {'label': 'dog', 'topY': 0.5, 'bottomX': 0.6, 'bottomY': 0.4}]
        if not only_one_file:
            test_label1 = [{"label": "pepsi_symbol", "topY": 0.53125, "bottomX": 0.703125, "bottomY": 0.6611328125}]
            test_labels = [test_label0, test_label1]
        else:
            test_labels = [test_label0]

        mockworkspace = _get_mockworkspace(test_files, test_labels, test_files_full_path, test_dataset_id)
        return mockworkspace, test_dataset_id, test_files_full_path, test_labels

    def test_aml_dataset_object_detection_default(self):
        mockworkspace, test_dataset_id, test_files_full_path, test_labels = self._build_dataset()

        try:
            dataset = AmlDatasetObjectDetection(test_dataset_id,
                                                workspace=mockworkspace,
                                                datasetclass=AmlDatasetMock)

            for a, t in zip(dataset._annotations.values(), test_labels):
                for a_label, t_label in zip(a, t):
                    assert a_label._label == t_label['label'], "Test _label"
                    assert a_label._x0_percentage == t_label['topX'], "Test _x0_percentage"
                    assert a_label._y0_percentage == t_label['topY'], "Test _y0_percentage"
                    assert a_label._x1_percentage == t_label['bottomX'], "Test _x1_percentage"
                    assert a_label._y1_percentage == t_label['bottomY'], "Test _y1_percentage"

            for test_file in test_files_full_path:
                assert os.path.exists(test_file)

        finally:
            for test_file in test_files_full_path:
                os.remove(test_file)

    def test_aml_dataset_object_detection_with_missing_topX(self):
        mockworkspace, test_dataset_id, _, _ = self._build_dataset_missing_topX()

        with pytest.raises(AutoMLVisionDataException):
            AmlDatasetObjectDetection(test_dataset_id,
                                      workspace=mockworkspace,
                                      datasetclass=AmlDatasetMock,
                                      ignore_data_errors=True)

    @pytest.mark.parametrize('single_file_dataset', [True, False])
    def test_aml_dataset_object_detection_train_test_split(self, single_file_dataset):

        def _test(tile_grid_size, tile_overlap_ratio):
            mockworkspace, test_dataset_id, test_files_full_path, test_labels = \
                self._build_dataset(single_file_dataset)

            try:
                dataset = AmlDatasetObjectDetection(test_dataset_id, is_train=True,
                                                    workspace=mockworkspace,
                                                    datasetclass=AmlDatasetMock,
                                                    tile_grid_size=tile_grid_size,
                                                    tile_overlap_ratio=tile_overlap_ratio)
                train_dataset, valid_dataset = dataset.train_val_split()
                _save_image_df(train_df=dataset.get_images_df(),
                               train_index=train_dataset._indices,
                               val_index=valid_dataset._indices, output_dir='.')

                assert train_dataset._is_train
                assert not valid_dataset._is_train
                assert train_dataset.classes == valid_dataset.classes

                num_train_images = len(train_dataset._indices)
                num_valid_images = len(valid_dataset._indices)
                if single_file_dataset:
                    assert num_train_images + num_valid_images == 2
                else:
                    assert num_train_images + num_valid_images == len(dataset._image_urls)

                image_urls_from_splits = []
                for index in range(len(train_dataset)):
                    image_urls_from_splits.append(train_dataset.get_image_url_at_index(index))
                for index in range(len(valid_dataset)):
                    image_urls_from_splits.append(valid_dataset.get_image_url_at_index(index))

                image_urls = []
                for index in range(len(dataset)):
                    image_urls.append(dataset.get_image_url_at_index(index))
                if single_file_dataset:
                    # The same file is duplicated in train and validation splits
                    assert set(image_urls) == set(image_urls_from_splits)
                else:
                    assert sorted(image_urls) == sorted(image_urls_from_splits)

                for test_file in test_files_full_path:
                    assert os.path.exists(test_file)
                # it's train_df.csv and val_df.csv files created from _save_image_df function
                assert os.path.exists('train_df.csv')
                assert os.path.exists('val_df.csv')

            finally:
                for test_file in test_files_full_path:
                    assert os.path.exists(test_file)
                os.remove('train_df.csv')
                os.remove('val_df.csv')

        # test train_val_split with no tiles
        _test(None, None)

        # test train_val_split with tiles.
        # train_val_split should split images and not tiles.
        _test((3, 2), 0.25)

    @staticmethod
    def _build_dataset_with_bbox_list(bbox_list):
        test_dataset_id = 'a7c014ec-474a-49f4-8ae3-09049c701913'
        test_files = []
        for idx in range(len(bbox_list)):
            test_files.append('a7c014ec-474a-49f4-8ae3-09049c701913-{}.txt'.format(idx))

        test_files_full_path = [os.path.join(AmlDatasetHelper.get_data_dir(),
                                             test_file) for test_file in test_files]
        test_labels = []
        for file_bbox_list in bbox_list:
            file_labels = []
            for bbox in file_bbox_list:
                file_labels.append({'label': '1', 'topX': bbox[0], 'topY': bbox[1],
                                    'bottomX': bbox[2], 'bottomY': bbox[3]})
            test_labels.append(file_labels)
        mockworkspace = _get_mockworkspace(test_files, test_labels, test_files_full_path, test_dataset_id)
        return mockworkspace, test_dataset_id, test_files_full_path, test_labels

    def test_aml_dataset_object_detection_invalid_bboxes(self):

        def _test_loop(bbox_list, valid, num_valid_boxes):
            mockworkspace, test_dataset_id, test_files_full_path, test_labels \
                = self._build_dataset_with_bbox_list(bbox_list)
            try:
                dataset = AmlDatasetObjectDetection(test_dataset_id,
                                                    workspace=mockworkspace,
                                                    datasetclass=AmlDatasetMock)
                dataset_wrapper = CommonObjectDetectionDatasetWrapper(dataset, DatasetProcessingType.IMAGES)
                assert valid
                assert len(dataset) == 1
                for test_file in test_files_full_path:
                    single_image_annotations = dataset._annotations[test_file]
                    len(single_image_annotations) == num_valid_boxes

                for image, target, info in dataset_wrapper:
                    assert image is not None
                    assert target is not None
                    assert info is not None

                for test_file in test_files_full_path:
                    assert os.path.exists(test_file)
            except AutoMLVisionDataException:
                assert not valid
            finally:
                for test_file in test_files_full_path:
                    os.remove(test_file)

        valid_bbox = [0.0, 0.0, 0.5, 0.5]

        # Single invalid bbox in an image. Values < 0.0
        bbox_list = [[[-0.1, 0.0, 0.5, 0.5]]]
        _test_loop(bbox_list, False, 0)
        # One invalid bbox and one valid bbox in an image.
        bbox_list = [[[-0.1, 0.0, 0.5, 0.5], valid_bbox]]
        _test_loop(bbox_list, True, 1)

        # Single invalid bbox in an image. Values > 1.0
        bbox_list = [[[0.0, 0.0, 0.5, 1.1]]]
        _test_loop(bbox_list, False, 0)
        # One invalid bbox and one valid bbox in an image.
        bbox_list = [[[0.0, 0.0, 0.5, 1.1], valid_bbox]]
        _test_loop(bbox_list, True, 1)

        # Single invalid bbox in an image. x0 > x1
        bbox_list = [[[0.8, 0.0, 0.5, 0.5]]]
        _test_loop(bbox_list, False, 0)
        # One invalid bbox and one valid bbox in an image.
        bbox_list = [[[0.8, 0.0, 0.5, 0.5], valid_bbox]]
        _test_loop(bbox_list, True, 1)

        # Single invalid bbox in an image. x0 = x1
        bbox_list = [[[0.5, 0.0, 0.5, 0.5]]]
        _test_loop(bbox_list, False, 0)
        # One invalid bbox and one valid bbox in an image.
        bbox_list = [[[0.5, 0.0, 0.5, 0.5], valid_bbox]]
        _test_loop(bbox_list, True, 1)

        # Single invalid bbox in an image. y0 > y1
        bbox_list = [[[0.0, 0.8, 0.5, 0.5]]]
        _test_loop(bbox_list, False, 0)
        # One invalid bbox and one valid bbox in an image.
        bbox_list = [[[0.0, 0.8, 0.5, 0.5], valid_bbox]]
        _test_loop(bbox_list, True, 1)

        # Single invalid bbox in an image. y0 = y1
        bbox_list = [[[0.0, 0.5, 0.5, 0.5]]]
        _test_loop(bbox_list, False, 0)
        # One invalid bbox and one valid bbox in an image.
        bbox_list = [[[0.0, 0.5, 0.5, 0.5], valid_bbox]]
        _test_loop(bbox_list, True, 1)

    def test_aml_dataset_object_detection_tiling_functions(self):

        def _test(bbox_list, tile_grid_size, tile_overlap_ratio, valid,
                  expected_tile_grid_size, expected_tile_overlap_ratio, expected_num_tiles_for_image):
            mockworkspace, test_dataset_id, test_files_full_path, test_labels \
                = self._build_dataset_with_bbox_list(bbox_list)
            try:
                dataset = AmlDatasetObjectDetection(test_dataset_id,
                                                    workspace=mockworkspace,
                                                    datasetclass=AmlDatasetMock,
                                                    tile_grid_size=tile_grid_size,
                                                    tile_overlap_ratio=tile_overlap_ratio)

                # Test supports_tiling()
                if tile_grid_size is not None:
                    assert dataset.supports_tiling()

                # Test tiling related parameters
                assert dataset._tile_grid_size == expected_tile_grid_size
                assert dataset._tile_overlap_ratio == expected_tile_overlap_ratio

                # Test that length of dataset only considers images. Not tiles
                assert len(dataset) == len(test_files_full_path)

                for index, image_url in enumerate(test_files_full_path):
                    image_tiles = dataset.get_image_tiles(image_url)
                    # Test get_image_tiles
                    assert len(image_tiles) == expected_num_tiles_for_image[index]

                    # Test that each tile has non-empty annotations
                    for image_tile in image_tiles:
                        assert isinstance(image_tile, TilingDatasetElement)
                        assert len(dataset._tile_annotations[image_tile]) != 0

                for test_file in test_files_full_path:
                    assert os.path.exists(test_file)
            except AutoMLVisionValidationException:
                assert not valid
            finally:
                for test_file in test_files_full_path:
                    if os.path.exists(test_file):
                        os.remove(test_file)

        # Two images with one ground truth box each
        bbox_list = [[[0.0, 0.0, 0.5, 0.5]], [[0.0, 0.0, 0.1, 0.1]]]

        # Dataset init without tiles
        _test(bbox_list, None, None, True, None, None, [0, 0])

        # Datset init with invalid tile settings
        _test(bbox_list, (3, 2, 3), None, False, None, None, None)

        # Dataset with both tile_grid_size and tile_overlap_ratio passed
        # with tile_grid_size: (3, 2) and overlap_ratio: 0.25
        #   - first image has 4 tiles overlapping the ground truth box
        #   - second image has one tile overlapping the ground truth box
        _test(bbox_list, (3, 2), 0.25, True, (3, 2), 0.25, [4, 1])

    def test_aml_dataset_object_detection_generate_tile_elements(self):

        def _test(bbox_list, tile_grid_size, tile_overlap_ratio, valid, expected_tiles, expected_tile_bbox_list):
            mockworkspace, test_dataset_id, test_files_full_path, test_labels \
                = self._build_dataset_with_bbox_list(bbox_list)
            try:
                dataset = AmlDatasetObjectDetection(test_dataset_id,
                                                    workspace=mockworkspace,
                                                    datasetclass=AmlDatasetMock,
                                                    tile_grid_size=tile_grid_size,
                                                    tile_overlap_ratio=tile_overlap_ratio)

                for image_index, image_url in enumerate(test_files_full_path):
                    image_tiles = dataset.get_image_tiles(image_url)

                    assert len(image_tiles) == len(expected_tiles[image_index])
                    assert len(image_tiles) == len(expected_tile_bbox_list[image_index])
                    for tile_index, image_tile in enumerate(image_tiles):
                        # Test tile co-ordinates
                        assert isinstance(image_tile, TilingDatasetElement)
                        assert image_tile.tile == expected_tiles[image_index][tile_index]

                        # Test tile bounding boxes
                        tile_annotations = dataset._tile_annotations[image_tile]
                        expected_tile_bboxes = expected_tile_bbox_list[image_index][tile_index]
                        assert len(tile_annotations) == len(expected_tile_bboxes)
                        for tile_annotation_index, tile_annotation in enumerate(tile_annotations):
                            tile_bbox = [tile_annotation._x0_percentage, tile_annotation._y0_percentage,
                                         tile_annotation._x1_percentage, tile_annotation._y1_percentage]
                            assert tile_bbox == expected_tile_bboxes[tile_annotation_index]
                            assert tile_annotation.label == "1"
                            assert tile_annotation.iscrowd == 0

                for test_file in test_files_full_path:
                    assert os.path.exists(test_file)
            except AutoMLVisionValidationException:
                assert not valid
            finally:
                for test_file in test_files_full_path:
                    os.remove(test_file)

        image_size = (768, 1024)
        tile_grid_size = (2, 2)
        tile_overlap_ratio = 0.0  # Using overlap_ratio of 0 for easier test case construction
        tiles = get_tiles(tile_grid_size, tile_overlap_ratio, image_size)

        bbox_list = [[[0.0, 0.0, 0.25, 0.25],  # box in tile 0
                      [0.0, 0.25, 0.25, 0.75],  # box in tile 0 and tile 1
                      [0.0, 0.75, 0.25, 1.0],  # box in tile 1
                      [0.75, 0.0, 1.0, 0.25],  # box in tile 2
                      [0.25, 0.0, 0.75, 0.25]  # box in tile 0 and tile 2
                      ]]
        # Expected bounding boxes in each tile with co-ordinates relative to tile dimensions
        # the comment against each line indicates what box in bbox_list it corresponds to.
        expected_tile_bbox_list = [[] for _ in tiles]
        expected_tile_bbox_list[0] = [[0.0, 0.0, 0.5, 0.5],  # bbox_list[0]
                                      [0.0, 0.5, 0.5, 1.0],  # bbox_list[1]
                                      [0.5, 0.0, 1.0, 0.5]  # bbox_list[4]
                                      ]
        expected_tile_bbox_list[1] = [[0.0, 0.0, 0.5, 0.5],  # bbox_list[1]
                                      [0.0, 0.5, 0.5, 1.0]  # bbox_list[2]
                                      ]
        expected_tile_bbox_list[2] = [[0.5, 0.0, 1.0, 0.5],  # bbox_list[3]
                                      [0.0, 0.0, 0.5, 0.5]  # bbox_list[4]
                                      ]
        _test(bbox_list, tile_grid_size, tile_overlap_ratio, True, [tiles[:3]], [expected_tile_bbox_list[:3]])

    def test_aml_dataset_object_detection_get_image(self):

        def _test(bbox_list, tile_grid_size, tile_overlap_ratio, valid, expected_num_boxes):
            mockworkspace, test_dataset_id, test_files_full_path, test_labels \
                = self._build_dataset_with_bbox_list(bbox_list)
            try:
                dataset = AmlDatasetObjectDetection(test_dataset_id,
                                                    workspace=mockworkspace,
                                                    datasetclass=AmlDatasetMock,
                                                    tile_grid_size=tile_grid_size,
                                                    tile_overlap_ratio=tile_overlap_ratio)
                assert valid
                assert len(dataset) == len(test_files_full_path)

                for index in range(len(dataset)):
                    image_url = dataset.get_image_url_at_index(index)
                    image_url_tile_list = [(image_url, None)]
                    image_tiles = dataset.get_image_tiles(image_url)
                    image_url_tile_list.extend([(image_url, image_tile.tile) for image_tile in image_tiles])

                    for item_index, item in enumerate(image_url_tile_list):
                        # Check get_image with entire image
                        image, target, info = dataset.get_image(item[0], item[1], index)
                        assert image is not None
                        assert target is not None
                        assert info is not None
                        assert "boxes" in target
                        assert target["boxes"].shape[0] == expected_num_boxes[index][item_index]
                        assert "original_width" in info
                        assert "original_height" in info
                        if item[1] is None:
                            assert "tile" not in info
                        else:
                            assert "tile" in info
                            assert info["tile"] == item[1]

                for test_file in test_files_full_path:
                    assert os.path.exists(test_file)
            except AutoMLVisionDataException:
                assert not valid
            finally:
                for test_file in test_files_full_path:
                    os.remove(test_file)

        # One image with 2 boxes
        bbox_list = [[[0.0, 0.0, 0.1, 0.1], [0.0, 0.0, 0.5, 0.5]]]
        _test(bbox_list, None, None, True, [[2]])

        _test(bbox_list, (3, 2), 0.25, True, [[2, 2, 1, 1, 1]])


@pytest.mark.usefixtures('new_clean_dir')
class TestAmlDatasetObjectDetection_with_polygon:

    @staticmethod
    def _build_dataset(only_one_file=False):
        test_dataset_id = 'a7c014ec-474a-49f4-8ae3-09049c701914'
        test_file0 = 'a7c014ec-474a-49f4-8ae3-09049c701914-1.txt'
        if not only_one_file:
            test_file1 = 'a7c014ec-474a-49f4-8ae3-09049c701914-2.txt'
            test_files = [test_file0, test_file1]
        else:
            test_files = [test_file0]

        test_files_full_path = [os.path.join(AmlDatasetHelper.get_data_dir(),
                                             test_file) for test_file in test_files]
        test_label0 = [{'label': "1", "bbox": None, "polygon": [[0.47227191413237923, 0.8031716417910447,
                                                                 0.3470483005366726, 0.7882462686567164,
                                                                 0.37298747763864043, 0.5652985074626866,
                                                                 0.40608228980322003, 0.33675373134328357]]},
                       {'label': "2", "bbox": None, "polygon": [[0.15579710144927536, 0.6282051282051282,
                                                                 0.08333333333333333, 0.4408284023668639,
                                                                 0.18206521739130435, 0.4970414201183432,
                                                                 0.15579710144927536, 0.6282051282051282],
                                                                [0.1431159420289855, 0.7642998027613412,
                                                                 0.11141304347826086, 0.6568047337278107,
                                                                 0.12047101449275362, 0.6351084812623274,
                                                                 0.14402173913043478, 0.7258382642998028,
                                                                 0.151268115942029, 0.7416173570019724]]}]
        if not only_one_file:
            test_label1 = [{'label': "2", "bbox": None, "polygon": [[0.47227191413237923, 0.8031716417910447,
                                                                     0.3470483005366726, 0.7882462686567164,
                                                                     0.37298747763864043, 0.5652985074626866,
                                                                     0.40608228980322003, 0.33675373134328357,
                                                                     0.47227191413237923, 0.8031716417910447]]}]
            test_labels = [test_label0, test_label1]
        else:
            test_labels = [test_label0]

        mockworkspace = _get_mockworkspace(test_files, test_labels, test_files_full_path, test_dataset_id)
        return mockworkspace, test_dataset_id, test_files_full_path, test_labels

    @staticmethod
    def _calulate_bbox(t_polygon):
        x_min_percent, x_max_percent, y_min_percent, y_max_percent = 101., -1., 101., -1.
        for segment in t_polygon:
            xs = segment[::2]
            ys = segment[1::2]
            x_min_percent = min(x_min_percent, min(xs))
            x_max_percent = max(x_max_percent, max(xs))
            y_min_percent = min(y_min_percent, min(ys))
            y_max_percent = max(y_max_percent, max(ys))
        return [x_min_percent, y_min_percent, x_max_percent, y_max_percent]

    @staticmethod
    def _build_dataset_with_empty_polygon(only_one_file=False):
        test_dataset_id = 'a7c014ec-474a-49f4-8ae3-09049c701915'
        test_file0 = 'a7c014ec-474a-49f4-8ae3-09049c701915-1.txt'
        if not only_one_file:
            test_file1 = 'a7c014ec-474a-49f4-8ae3-09049c701915-2.txt'
            test_file2 = 'a7c014ec-474a-49f4-8ae3-09049c701915-3.txt'
            test_files = [test_file0, test_file1, test_file2]
        else:
            test_files = [test_file0]

        test_files_full_path = [AmlDatasetHelper.get_data_dir() + '/' + test_file for test_file in test_files]
        test_label0 = [{'label': "1", "bbox": None, "polygon": [[]]}]
        if not only_one_file:
            test_label1 = [{'label': "2", "bbox": None, "polygon": []}]
            test_label2 = [{'label': "3", "bbox": None, "polygon": None}]
            test_labels = [test_label0, test_label1, test_label2]
        else:
            test_labels = [test_label0]

        mockworkspace = _get_mockworkspace(test_files, test_labels, test_files_full_path, test_dataset_id)
        return mockworkspace, test_dataset_id, test_files_full_path, test_labels

    @staticmethod
    def _build_dataset_with_odd_element_polygon(only_one_file=False):
        test_dataset_id = 'a7c014ec-474a-49f4-8ae3-09049c701916'
        test_file0 = 'a7c014ec-474a-49f4-8ae3-09049c701916-1.txt'
        if not only_one_file:
            test_file1 = 'a7c014ec-474a-49f4-8ae3-09049c701916-2.txt'
            test_files = [test_file0, test_file1]
        else:
            test_files = [test_file0]

        test_files_full_path = [AmlDatasetHelper.get_data_dir() + '/' + test_file for test_file in test_files]
        test_label0 = [{'label': "1", "bbox": None, "polygon": [[0.15579710144927536, 0.6282051282051282,
                                                                 0.08333333333333333, 0.4408284023668639,
                                                                 0.18206521739130435],
                                                                [0.1431159420289855, 0.7642998027613412,
                                                                 0.11141304347826086, 0.6568047337278107,
                                                                 0.12047101449275362, 0.6351084812623274,
                                                                 0.151268115942029, 0.7416173570019724]]}]
        if not only_one_file:
            test_label1 = [{'label': "2", "bbox": None, "polygon": [[0.47227191413237923, 0.8031716417910447,
                                                                     0.3470483005366726, 0.7882462686567164,
                                                                     0.37298747763864043, 0.5652985074626866,
                                                                     0.40608228980322003]]}]
            test_labels = [test_label0, test_label1]
        else:
            test_labels = [test_label0]

        mockworkspace = _get_mockworkspace(test_files, test_labels, test_files_full_path, test_dataset_id)
        return mockworkspace, test_dataset_id, test_files_full_path, test_labels

    @pytest.mark.parametrize('single_file_dataset', [True, False])
    def test_aml_dataset_object_detection_default_with_polygon(self, single_file_dataset):
        mockworkspace, test_dataset_id, test_files_full_path, test_labels = self._build_dataset(single_file_dataset)

        try:
            dataset = AmlDatasetObjectDetection(test_dataset_id,
                                                workspace=mockworkspace,
                                                datasetclass=AmlDatasetMock)

            for a, t in zip(dataset._annotations.values(), test_labels):
                for a_label, t_label in zip(a, t):
                    assert a_label._label == t_label['label'], "Test _label"
                    assert a_label._normalized_mask_poly == t_label['polygon'], "Test _normalized_mask_poly"
                    target_bbox = self._calulate_bbox(t_label['polygon'])
                    assert a_label._x0_percentage == target_bbox[0], "Test _x0_percentage"
                    assert a_label._y0_percentage == target_bbox[1], "Test _y0_percentage"
                    assert a_label._x1_percentage == target_bbox[2], "Test _x1_percentage"
                    assert a_label._y1_percentage == target_bbox[3], "Test _y1_percentage"

            for test_file in test_files_full_path:
                assert os.path.exists(test_file)

        finally:
            for test_file in test_files_full_path:
                os.remove(test_file)

    def test_aml_dataset_object_detection_with_empty_polygon(self):
        mockworkspace, test_dataset_id, test_files_full_path, test_labels = self._build_dataset_with_empty_polygon()

        try:
            # Basically, if there is "polygon" attribute in the label, we have to handle those corner cases gracefully
            # Raises AutoMLVisionDataException as all images in this dataset have invalid annotations
            with pytest.raises(AutoMLVisionDataException):
                AmlDatasetObjectDetection(test_dataset_id,
                                          workspace=mockworkspace,
                                          datasetclass=AmlDatasetMock,
                                          ignore_data_errors=True)
            for test_file in test_files_full_path:
                assert os.path.exists(test_file)

        finally:
            for test_file in test_files_full_path:
                os.remove(test_file)

    def test_aml_dataset_object_detection_with_odd_element_polygon(self):
        mockworkspace, test_dataset_id, test_files_full_path, test_labels \
            = self._build_dataset_with_odd_element_polygon(only_one_file=True)

        with pytest.raises(AutoMLVisionDataException):
            AmlDatasetObjectDetection(test_dataset_id,
                                      workspace=mockworkspace,
                                      datasetclass=AmlDatasetMock,
                                      ignore_data_errors=True)

    @staticmethod
    def _build_dataset_with_polygon_list_single_image(polygon_list):
        test_dataset_id = 'a7c014ec-474a-49f4-8ae3-09049c701916'
        test_files = ['a7c014ec-474a-49f4-8ae3-09049c701916-0.txt']

        test_files_full_path = [AmlDatasetHelper.get_data_dir() + '/' + test_file for test_file in test_files]
        test_labels = [[]]
        for polygon in polygon_list:
            test_labels[0].append({'label': "1", "bbox": None, "polygon": polygon})
        mockworkspace = _get_mockworkspace(test_files, test_labels, test_files_full_path, test_dataset_id)
        return mockworkspace, test_dataset_id, test_files_full_path, test_labels

    def test_aml_dataset_object_detection_with_invalid_polygon_segments(self):

        def _test_loop(polygon_list, valid, num_valid_polygons):
            mockworkspace, test_dataset_id, test_files_full_path, test_labels \
                = self._build_dataset_with_polygon_list_single_image(polygon_list)
            try:
                dataset = AmlDatasetObjectDetection(test_dataset_id,
                                                    workspace=mockworkspace,
                                                    datasetclass=AmlDatasetMock)
                assert valid
                assert len(dataset) == 1
                for test_file in test_files_full_path:
                    single_image_annotations = dataset._annotations[test_file]
                    len(single_image_annotations) == num_valid_polygons

                datasetwrapper = CommonObjectDetectionDatasetWrapper(dataset, DatasetProcessingType.IMAGES)
                for image, target, info in datasetwrapper:
                    assert image is not None
                    assert target is not None
                    assert info is not None

                for test_file in test_files_full_path:
                    assert os.path.exists(test_file)
            except AutoMLVisionDataException:
                assert not valid
            finally:
                for test_file in test_files_full_path:
                    os.remove(test_file)

        valid_segment = [0.1, 0.2, 0.3, 0.5, 1.0, 1.0]

        # Single polygon segment with len < 5
        polygon_list = [[[0.17, 0.29, 0.19, 0.29]]]
        _test_loop(polygon_list, False, 0)
        # One valid segment and one invalid segment
        polygon_list = [[[0.17, 0.29, 0.19, 0.29], valid_segment]]
        _test_loop(polygon_list, True, 1)
        # One invalid polygon and one valid polygon
        polygon_list = [[[0.17, 0.29, 0.19, 0.29]], [valid_segment]]
        _test_loop(polygon_list, True, 1)

        # Single polygon segment with values < 0.0
        polygon_list = [[[-0.1, 0.2, 0.3, 0.5, 1.0, 1.0]]]
        _test_loop(polygon_list, False, 0)
        # One valid segment and one invalid segment
        polygon_list = [[[-0.1, 0.2, 0.3, 0.5, 1.0, 1.0], valid_segment]]
        _test_loop(polygon_list, True, 1)
        # One invalid polygon and one valid polygon
        polygon_list = [[[-0.1, 0.2, 0.3, 0.5, 1.0, 1.0]], [valid_segment]]
        _test_loop(polygon_list, True, 1)

        # Single polygon segment with values > 1.0
        polygon_list = [[[0.1, 0.2, 0.3, 0.5, 1.0, 1.1]]]
        _test_loop(polygon_list, False, 0)
        # One valid segment and one invalid segment
        polygon_list = [[[0.1, 0.2, 0.3, 0.5, 1.0, 1.1], valid_segment]]
        _test_loop(polygon_list, True, 1)
        # One invalid polygon and one valid polygon
        polygon_list = [[[0.1, 0.2, 0.3, 0.5, 1.0, 1.1]], [valid_segment]]
        _test_loop(polygon_list, True, 1)

        # Multiple invalid segments
        polygon_list = [[[0.17, 0.29, 0.19, 0.29],  # len < 5
                         [-0.1, 0.2, 0.3, 0.5, 1.0, 1.0],  # has values < 0.0
                         [0.1, 0.2, 0.3, 0.5, 1.0, 1.1],  # has values > 1.0
                         ]]
        _test_loop(polygon_list, False, 0)

        # Single polygon segment such that min and max values of the bbox are the same
        polygon_list = [[[0.5, 0.6, 0.5, 0.7, 0.5, 0.8]]]
        _test_loop(polygon_list, False, 0)
