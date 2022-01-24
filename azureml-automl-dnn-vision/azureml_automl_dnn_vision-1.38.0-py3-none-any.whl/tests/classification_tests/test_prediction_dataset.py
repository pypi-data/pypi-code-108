import os
import pytest
from shutil import copyfile
import tempfile
import pandas as pd

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException, AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper
from azureml.automl.dnn.vision.common.prediction_dataset import PredictionDataset
from azureml.automl.dnn.vision.common.tiling_utils import get_tiles
from azureml.automl.dnn.vision.common.tiling_dataset_element import TilingDatasetElement

from .aml_dataset_mock import AmlDatasetMock, WorkspaceMock, DataflowMock, DataflowStreamMock


@pytest.mark.usefixtures('new_clean_dir')
class TestPredictionDataset:

    @staticmethod
    def _create_image_list_file(tmp_output_dir, lines, create_each_file=True):
        image_file = 'image_list_file.txt'
        image_list_file = os.path.join(tmp_output_dir, image_file)
        with open(image_list_file, 'w') as f:
            for line in lines:
                f.write(line + '\n')
                # create each file with no content
                if create_each_file and line.strip():
                    # filter out label info if exist
                    filename = line.split('\t')[0]
                    full_path = os.path.join(tmp_output_dir, filename.strip())
                    copyfile(os.path.join(os.path.dirname(__file__),
                                          "../data/classification_data/images/crack_1.jpg"),
                             full_path)
        return image_list_file

    @staticmethod
    def _create_aml_dataset(num_files):
        test_dataset_id = 'e7c014ec-474a-49f4-8ae3-09049c701913'
        test_files = []
        for index in range(num_files):
            test_files.append('e7c014ec-474a-49f4-8ae3-09049c701913-{}.txt'.format(index))
        test_files_full_path = [os.path.join(AmlDatasetHelper.get_data_dir(),
                                             test_file) for test_file in test_files]
        properties = {}
        label_dataset_data = {
            'Path': ['/' + f for f in test_files]
        }
        dataframe = pd.DataFrame(label_dataset_data)

        mockdataflowstream = DataflowStreamMock(test_files_full_path)
        mockdataflow = DataflowMock(dataframe, mockdataflowstream, 'Path')
        mockdataset = AmlDatasetMock(properties, mockdataflow, test_dataset_id)
        mockworkspace = WorkspaceMock(mockdataset)
        return mockworkspace, test_dataset_id, test_files, test_files_full_path

    def test_prediction_dataset(self):
        mockworkspace, test_dataset_id, test_files, test_files_full_path = self._create_aml_dataset(2)

        try:
            datasetwrapper = PredictionDataset(input_dataset_id=test_dataset_id, ws=mockworkspace,
                                               datasetclass=AmlDatasetMock)

            file_names = [element.image_url for element in datasetwrapper._elements]
            file_names.sort()
            assert file_names == test_files, "File Names"
            assert len(datasetwrapper) == len(test_files), "len"

            for test_file in test_files_full_path:
                assert os.path.exists(test_file)

        finally:
            for test_file in test_files_full_path:
                os.remove(test_file)

    def _test_tiling(self, dataset, expected_file_names, expected_tile_grid_size, expected_tile_overlap_ratio,
                     expected_num_images, expected_num_tiles):
        assert dataset._tile_grid_size == expected_tile_grid_size
        assert dataset._tile_overlap_ratio == expected_tile_overlap_ratio

        file_names = set()
        num_images = 0
        num_tiles = 0
        for element in dataset._elements:
            file_names.add(element.image_url)
            if element.tile is not None:
                num_tiles += 1
            else:
                num_images += 1
        file_names = sorted(file_names)
        assert file_names == expected_file_names, "File Names"
        assert len(dataset) == expected_num_images + expected_num_tiles, "len"
        assert num_images == expected_num_images, "Number of images"
        assert num_tiles == expected_num_tiles, "Number of tiles"

        # Test getitem()
        for idx in range(len(dataset)):
            filename, image, info = dataset[idx]
            assert filename is not None
            assert image is not None
            assert info is not None
            assert "original_width" in info
            assert "original_height" in info

            if dataset._elements[idx].tile is not None:
                assert "tile" in info
                assert info["tile"] == dataset._elements[idx].tile
            else:
                assert "tile" not in info

    def test_prediction_dataset_with_tiles(self):

        def _test(tile_grid_size, tile_overlap_ratio, valid, expected_tile_grid_size,
                  expected_tile_overlap_ratio, expected_num_images, expected_num_tiles):
            mockworkspace, test_dataset_id, test_files, test_files_full_path = self._create_aml_dataset(2)

            try:
                datasetwrapper = PredictionDataset(input_dataset_id=test_dataset_id, ws=mockworkspace,
                                                   datasetclass=AmlDatasetMock, tile_grid_size=tile_grid_size,
                                                   tile_overlap_ratio=tile_overlap_ratio)

                assert valid
                self._test_tiling(datasetwrapper, test_files, expected_tile_grid_size, expected_tile_overlap_ratio,
                                  expected_num_images, expected_num_tiles)

                for test_file in test_files_full_path:
                    assert os.path.exists(test_file)

            except AutoMLVisionValidationException:
                assert not valid
            finally:
                for test_file in test_files_full_path:
                    if os.path.exists(test_file):
                        os.remove(test_file)

        _test(None, None, True, None, None, 2, 0)

        _test((3, 2, 3), 0.25, False, None, None, None, None)

        tile_grid_sizes = [(2, 1), (3, 2), (5, 3)]
        for tile_grid_size in tile_grid_sizes:
            _test(tile_grid_size, 0.25, True, tile_grid_size, 0.25, 2, 2 * tile_grid_size[0] * tile_grid_size[1])

    def test_prediction_dataset_with_image_file(self):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            file_content = ['test.txt', 'whitespace.txt ', 'space in a filename.txt']
            image_list_file = self._create_image_list_file(tmp_output_dir, file_content)

            pred_dataset = PredictionDataset(root_dir=tmp_output_dir, image_list_file=image_list_file)

            filenames = [element.image_url for element in pred_dataset._elements]
            filenames.sort()
            assert filenames == ['space in a filename.txt', 'test.txt', 'whitespace.txt']

    def test_prediction_dataset_with_image_file_with_tiles(self):

        def _test(tile_grid_size, tile_overlap_ratio, valid, expected_tile_grid_size,
                  expected_tile_overlap_ratio, expected_num_images, expected_num_tiles):
            with tempfile.TemporaryDirectory() as tmp_output_dir:
                try:
                    file_content = ['test.txt', 'whitespace.txt ', 'space in a filename.txt']
                    image_list_file = self._create_image_list_file(tmp_output_dir, file_content)

                    pred_dataset = PredictionDataset(root_dir=tmp_output_dir, image_list_file=image_list_file,
                                                     tile_grid_size=tile_grid_size,
                                                     tile_overlap_ratio=tile_overlap_ratio)
                    expected_file_names = ['space in a filename.txt', 'test.txt', 'whitespace.txt']
                    self._test_tiling(pred_dataset, expected_file_names, expected_tile_grid_size,
                                      expected_tile_overlap_ratio, expected_num_images, expected_num_tiles)
                except AutoMLVisionValidationException:
                    assert not valid

        _test(None, None, True, None, None, 3, 0)

        _test((3, 2, 3), 0.25, False, None, None, None, None)

        tile_grid_sizes = [(2, 1), (3, 2), (5, 3)]
        for tile_grid_size in tile_grid_sizes:
            _test(tile_grid_size, 0.25, True, tile_grid_size, 0.25, 3, 3 * tile_grid_size[0] * tile_grid_size[1])

    def test_prediction_dataset_with_labeled_image_file(self):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            file_content = ['test.txt\ttestlabel', 'whitespace.txt\ttestlabel ',
                            'space in a filename.txt\ttestlabel']
            image_list_file = self._create_image_list_file(tmp_output_dir, file_content)

            pred_dataset = PredictionDataset(root_dir=tmp_output_dir, image_list_file=image_list_file)

            filenames = [element.image_url for element in pred_dataset._elements]
            filenames.sort()
            assert filenames == ['space in a filename.txt', 'test.txt', 'whitespace.txt']

    def test_prediction_dataset_with_invalid_row(self):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            file_content = ['test.txt', ' ']
            image_list_file = self._create_image_list_file(tmp_output_dir, file_content)

            pred_dataset = PredictionDataset(root_dir=tmp_output_dir, image_list_file=image_list_file)
            files = [element.image_url for element in pred_dataset._elements]
            assert files == ['test.txt']

    def test_prediction_dataset_with_none_root_dir(self):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            file_content = ['test.txt', ' ']
            image_list_file = self._create_image_list_file(tmp_output_dir, file_content)

            pred_dataset = PredictionDataset(image_list_file=image_list_file)
            files = [element.image_url for element in pred_dataset._elements]
            assert files == []

    def test_prediction_dataset_invalid_without_ignore(self):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            file_content = ['test.txt', ' ']
            image_list_file = self._create_image_list_file(tmp_output_dir, file_content)
            with pytest.raises(AutoMLVisionDataException):
                PredictionDataset(root_dir=tmp_output_dir, image_list_file=image_list_file, ignore_data_errors=False)

    def test_prediction_dataset_with_json_file(self):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            file_content = ['{"imageUrl": "test.png", "imageDetails": {}}',
                            '{"imageUrl": "ws.png ", "imageDetails": {}}',
                            '{"imageUrl": "", "imageDetails": {}}',
                            '{"imageUrl": , "imageDetails": {}}']
            image_list_file = self._create_image_list_file(tmp_output_dir, file_content, create_each_file=False)

            pred_dataset = PredictionDataset(image_list_file=image_list_file)
            # since there is no actual file exists, it should return an empty list
            files = [element.image_url for element in pred_dataset._elements]
            assert files == []
