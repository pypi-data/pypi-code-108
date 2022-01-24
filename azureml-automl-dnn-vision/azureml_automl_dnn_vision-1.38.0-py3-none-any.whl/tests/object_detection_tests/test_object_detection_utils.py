import os
import pytest
import tempfile
import torch
import unittest.mock as mock

from azureml.automl.dnn.vision.common import utils
import azureml.automl.dnn.vision.object_detection.common.object_detection_utils as od_utils
from azureml.automl.dnn.vision.object_detection.data.datasets import AmlDatasetObjectDetection
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import \
    CommonObjectDetectionDatasetWrapper, DatasetProcessingType
from azureml.automl.dnn.vision.object_detection.eval.vocmap import VocMap

from ..common.run_mock import RunMock, ExperimentMock, DatastoreMock, WorkspaceMock
from .aml_dataset_mock import AmlDatasetMock
from .test_datasets import TestAmlDatasetObjectDetection


@pytest.mark.usefixtures('new_clean_dir')
class TestObjectDetectionUtils:

    @staticmethod
    def _setup_wrapper(only_one_file=False):
        ws_mock, test_dataset_id, _, _ = TestAmlDatasetObjectDetection._build_dataset(only_one_file)
        dataset_mock = AmlDatasetObjectDetection(test_dataset_id,
                                                 workspace=ws_mock,
                                                 datasetclass=AmlDatasetMock)
        wrapper_mock = CommonObjectDetectionDatasetWrapper(dataset_mock, DatasetProcessingType.IMAGES)
        return ws_mock, test_dataset_id, wrapper_mock

    @staticmethod
    def _write_output_file(output_file, only_one_file=False):
        with open(output_file, 'w') as f:
            line1 = '{"filename": "a7c014ec-474a-49f4-8ae3-09049c701913-1.txt", ' \
                    '"boxes": [{"box": {"topX": 0.1, "topY": 0.9, "bottomX": 0.2, "bottomY": 0.8}, ' \
                    '"label": "cat", "score": 0.7}]}'
            line2 = '{"filename": "a7c014ec-474a-49f4-8ae3-09049c701913-2", ' \
                    '"boxes": [{"box": {"topX": 0.5, "topY": 0.5, "bottomX": 0.6, "bottomY": 0.4}, '\
                    '"label": "dog", "score": 0.8}]}'
            f.write(line1 + '\n')
            f.write(line2 + '\n')

    @mock.patch(od_utils.__name__ + '.CommonObjectDetectionDatasetWrapper')
    @mock.patch(od_utils.__name__ + '.AmlDatasetObjectDetection')
    @mock.patch(od_utils.__name__ + '.VocMap')
    @mock.patch(od_utils.__name__ + '._parse_bounding_boxes')
    @mock.patch(od_utils.__name__ + '._evaluate_results')
    def test_validate_score_run(self, mock_eval, mock_parse, mock_vocmap, mock_dataset, mock_wrapper):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            # Patch functions
            ws_mock, test_dataset_id, wrapper_mock = self._setup_wrapper()
            vocmap_obj = VocMap(wrapper_mock)

            mock_dataset.return_value = wrapper_mock.dataset
            mock_wrapper.return_value = wrapper_mock
            mock_vocmap.return_value = vocmap_obj
            mock_parse.return_value = 'mock_bounding_boxes'
            mock_eval.return_value = None

            # Setup mock objects
            predictions_file = 'predictions_od.txt'
            output_file = os.path.join(tmp_output_dir, predictions_file)
            experiment_mock = ExperimentMock(ws_mock)
            mock_run = RunMock(experiment_mock)

            od_utils._validate_score_run(input_dataset_id=test_dataset_id,
                                         workspace=ws_mock,
                                         use_bg_label=True,
                                         output_file=output_file,
                                         score_run=mock_run)

            # Assert that expected methods were called
            mock_dataset.assert_called_once_with(dataset_id=test_dataset_id, is_train=False,
                                                 ignore_data_errors=True, workspace=ws_mock,
                                                 download_files=False, use_bg_label=True)
            mock_wrapper.assert_called_once_with(dataset=wrapper_mock.dataset,
                                                 dataset_processing_type=DatasetProcessingType.IMAGES)
            mock_vocmap.assert_called_once_with(wrapper_mock)
            mock_parse.assert_called_once_with(output_file, wrapper_mock.dataset, wrapper_mock.dataset.classes)
            mock_eval.assert_called_once_with(mock_run, vocmap_obj, 'mock_bounding_boxes')

    def test_parse_bounding_boxes(self):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            # Setup output file
            predictions_file = 'predictions_od.txt'
            output_file = os.path.join(tmp_output_dir, predictions_file)
            self._write_output_file(output_file)

            _, _, wrapper_mock = self._setup_wrapper()
            eval_bounding_boxes = od_utils._parse_bounding_boxes(output_file=output_file,
                                                                 validation_dataset=wrapper_mock.dataset,
                                                                 val_index_map=wrapper_mock.dataset.classes)

            assert len(eval_bounding_boxes) == 2

            bbox1 = eval_bounding_boxes[0]
            assert 'a7c014ec-474a-49f4-8ae3-09049c701913-1' in bbox1['image_id']
            assert bbox1['category_id'] == 'cat'
            assert bbox1['score'] == 0.7
            assert len(bbox1['bbox']) == 4

            bbox2 = eval_bounding_boxes[1]
            assert 'a7c014ec-474a-49f4-8ae3-09049c701913-2' in bbox2['image_id']
            assert bbox2['category_id'] == 'dog'
            assert bbox2['score'] == 0.8
            assert len(bbox1['bbox']) == 4

    @mock.patch(utils.__name__ + '._read_image')
    def test_parse_bounding_boxes_invalid_img(self, mock_read_img):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            # Mock behavior for invalid images
            mock_read_img.return_value = None
            predictions_file = 'predictions_od.txt'
            output_file = os.path.join(tmp_output_dir, predictions_file)
            self._write_output_file(output_file, True)

            _, _, wrapper_mock = self._setup_wrapper()
            eval_bounding_boxes = od_utils._parse_bounding_boxes(output_file=output_file,
                                                                 validation_dataset=wrapper_mock.dataset,
                                                                 val_index_map=wrapper_mock.dataset.classes)
            # No boxes are returned for an invalid image
            assert len(eval_bounding_boxes) == 0

    @mock.patch(od_utils.__name__ + '.VocMap.compute')
    def test_evaluate_results(self, mock_compute):
        # Set up mock objects
        per_label_metrics = {
            1: {'precision': torch.tensor(0.1), 'recall': torch.tensor(0.2), 'average_precision': torch.tensor(0.3)},
            2: {'precision': torch.tensor(0.1), 'recall': torch.tensor(0.2), 'average_precision': torch.tensor(0.3)},
            3: {'precision': torch.tensor(0.1), 'recall': torch.tensor(0.2), 'average_precision': torch.tensor(0.3)},
        }
        mock_compute.return_value = {
            VocMap.PER_LABEL_METRICS: per_label_metrics,
            VocMap.PRECISION: 0.7,
            VocMap.RECALL: 0.8,
            VocMap.MAP: 0.9
        }

        mock_record = {
            'image_id': 'test_id',
            'bbox': 'test_value',
            'category_id': 'some_label',
            'score': 1.0
        }
        mock_bboxes = [mock_record]

        ws_mock, _, wrapper_mock = self._setup_wrapper()
        experiment_mock = ExperimentMock(ws_mock)
        mock_run = RunMock(experiment_mock)
        vocmap_obj = VocMap(wrapper_mock)

        od_utils._evaluate_results(score_run=mock_run,
                                   val_vocmap=vocmap_obj,
                                   eval_bounding_boxes=mock_bboxes)

        # Validate that compute was called
        mock_compute.assert_called_once_with(mock_bboxes, "bbox")

        properties = mock_run.properties

        # Validate properties and metrics contain expected values
        assert properties[VocMap.PRECISION] == 0.7
        assert properties[VocMap.RECALL] == 0.8
        assert properties[VocMap.MAP] == 0.9

        metrics = mock_run.metrics
        assert metrics[VocMap.PRECISION] == 0.7
        assert metrics[VocMap.RECALL] == 0.8
        assert metrics[VocMap.MAP] == 0.9


@pytest.mark.usefixtures('new_clean_dir')
def test_score_validation_data(monkeypatch):
    def mock_fetch_model(run_id, device, model_settings):
        assert run_id == 'mock_run_id'
        expected_model_settings = {"dummySetting": "dummyVal"}
        assert model_settings == expected_model_settings
        return 'mock_model'

    def mock_score(model_wrapper, run, target_path, device,
                   output_file, root_dir, image_list_file,
                   batch_size, ignore_data_errors, input_dataset_id,
                   num_workers, validate_score, log_output_file_info):
        assert model_wrapper == 'mock_model'
        assert target_path.startswith('automl/datasets/')
        assert batch_size == 20
        assert input_dataset_id == '123'
        assert num_workers == 8
        assert device == 'cpu'
        assert log_output_file_info

        data_folder = os.path.join(tmp_output_dir, 'dummyFolder')
        expected_root_dir = os.path.join(data_folder, '.')
        assert root_dir == expected_root_dir

        with open(image_list_file, 'w') as f:
            f.write('testcontent')

    with tempfile.TemporaryDirectory() as tmp_output_dir:
        ds_mock = DatastoreMock('datastore_mock')
        ws_mock = WorkspaceMock(ds_mock)
        experiment_mock = ExperimentMock(ws_mock)
        run_mock = RunMock(experiment_mock)
        model_settings = {"dummySetting": "dummyVal"}
        settings = {
            'validation_dataset_id': '123',
            'validation_batch_size': 20,
            'validation_labels_file': 'test.csv',
            'labels_file_root': tmp_output_dir,
            'data_folder': os.path.join(tmp_output_dir, 'dummyFolder'),
            'num_workers': 8,
            'validate_scoring': False,
            'images_folder': '.',
            'log_scoring_file_info': True
        }

        with monkeypatch.context() as m:
            m.setattr(od_utils, '_fetch_model_from_artifacts', mock_fetch_model)
            od_utils.score_validation_data(run=run_mock, model_settings=model_settings,
                                           settings=settings, device='cpu',
                                           score_with_model=mock_score)
            expected_val_labels_file = os.path.join(tmp_output_dir, 'test.csv')
            assert os.path.exists(expected_val_labels_file)
