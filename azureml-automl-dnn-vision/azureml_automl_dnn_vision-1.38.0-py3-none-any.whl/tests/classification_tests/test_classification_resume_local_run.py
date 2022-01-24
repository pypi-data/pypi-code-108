import os
import tempfile
from unittest import mock

import pytest
import sys
import time

import azureml
import azureml.automl.core.shared.constants as shared_constants
import azureml.automl.dnn.vision.classification.runner as runner
import azureml.automl.dnn.vision.common.artifacts_utils as artifacts_utils

from azureml.train.automl import constants
from tests.common.utils import mock_prepare_model_export


data_folder = 'classification_data/images'
labels_root = 'classification_data/'


def _get_settings(csv_file):
    return {
        # Only run 1 epoch to make the test faster
        'deterministic': True,
        'epochs': 1,
        'images_folder': '.',
        'labels_file': csv_file,
        'log_verbose_metrics': True,
        'num_workers': 0,
        'output_scoring': True,
        'print_local_package_versions': True,
        'seed': 47,
    }


@pytest.mark.usefixtures('new_clean_dir')
@mock.patch.object(azureml._restclient.JasmineClient, '__init__', lambda x, y, z, t, **kwargs: None)
@mock.patch.object(azureml._restclient.experiment_client.ExperimentClient, '__init__', lambda x, y, z, **kwargs: None)
@mock.patch('azureml._restclient.JasmineClient', autospec=True)
@mock.patch('azureml._restclient.experiment_client.ExperimentClient', autospec=True)
@mock.patch('azureml._restclient.run_client.RunClient', autospec=True)
@mock.patch('azureml._restclient.metrics_client.MetricsClient', autospec=True)
def test_multiclassification_local_run(mock_metrics_client, mock_run_client,
                                       mock_experiment_client, mock_jasmine_client,
                                       monkeypatch):

    settings = _get_settings('multiclass.csv')

    def mock_score_validation_data(azureml_run, model_settings, ignore_data_errors,
                                   val_dataset_id, image_folder, device, settings, score_with_model):
        # Ensures score_validation_data is called
        test_output_dir = settings['output_dir']
        predictions_file = os.path.join(test_output_dir, 'predictions.txt')
        with open(predictions_file, 'w') as f:
            f.write('test content')

    with monkeypatch.context() as m:
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            m.setattr(sys, 'argv', ['runner.py', '--data-folder', data_folder, '--labels-file-root', labels_root])
            # Due to a weird monkeypatch behavior where we need to patch from the file where the method is called
            # (even if it's imported from a different file)
            m.setattr(runner, 'score_validation_data', mock_score_validation_data)
            m.setattr(artifacts_utils, 'prepare_model_export', mock_prepare_model_export)

            settings['output_dir'] = tmp_output_dir
            settings['task_type'] = constants.Tasks.IMAGE_CLASSIFICATION
            settings['device'] = 'cpu'
            runner.run(settings)
            expected_output = os.path.join(tmp_output_dir, shared_constants.PT_MODEL_FILENAME)
            expected_validation_output = os.path.join(tmp_output_dir, 'predictions.txt')
            assert os.path.exists(expected_output)
            assert os.path.exists(expected_validation_output)

            time.sleep(2)
            # support resume
            # resume_pkl_file = expected_output
            # with open(resume_pkl_file, 'rb') as fp:
            #     resume_pkl_model = pickle.load(fp)
            #     optimizer = resume_pkl_model.model_wrapper.optimizer.state_dict()
            #     assert optimizer is not None
            #     lr_scheduler = resume_pkl_model.model_wrapper.lr_scheduler.lr_scheduler.state_dict()
            #     assert lr_scheduler is not None
            #     assert len(optimizer['param_groups']) == len(lr_scheduler['base_lrs'])
            #
            # # bad path + resume flag should fail
            # mock_run = MagicMock(spec=Run)
            # mock_workspace = MagicMock()
            # mock_run.experiment = MagicMock(return_value=Experiment(mock_workspace, "test", _create_in_cloud=False))
            #
            # with patch.object(Run, 'get_context', return_value=mock_run):
            #     settings['resume'] = expected_output + "_random"
            #     try:
            #         runner.run(settings)
            #     except Exception:
            #         pass
            #     mock_run.fail.assert_called_once()
            #     assert mock_run.fail.call_args[1]["error_details"].error_type == 'SystemError'
            #
            # settings['resume'] = expected_output
            # m.setattr(ArtifactLiterals, 'MODEL_WRAPPER_PKL', ArtifactLiterals.MODEL_WRAPPER_PKL + "_after_resume")
            # expected_output_resume = os.path.join(tmp_output_dir,
            #                                       ArtifactLiterals.MODEL_WRAPPER_PKL)
            # expected_validation_output_resume = os.path.join(tmp_output_dir, 'predictions.txt')
            # runner.run(settings)
            # assert os.path.exists(expected_output_resume)
            # assert os.path.exists(expected_validation_output_resume)
