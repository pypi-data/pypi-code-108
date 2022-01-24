import json
import numpy as np
import pandas as pd
from transformers.trainer_utils import EvalPrediction
from unittest.mock import mock_open, MagicMock

from azureml.core import Dataset as AmlDataset
from azureml.data import FileDataset
from azureml.dataprep.native import StreamInfo
from azureml.automl.dnn.nlp.classification.common.constants import MultiClassInferenceLiterals, MultiClassParameters

try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


class MockExperiment:
    def __init__(self):
        self.workspace = "some_workspace"


class MockRun:
    def __init__(
            self,
            run_source='automl',
            label_column_name=None,
            featurization="auto",
            labeling_dataset_type=None
    ):
        self.metrics = {}
        self.properties = {}
        self.id = 'mock_run_id'
        self.duplicate_metric_logged = False
        self.run_source = run_source
        self.label_column_name = label_column_name
        self.featurization = featurization
        self.labeling_dataset_type = labeling_dataset_type

    @property
    def experiment(self):
        return self

    @property
    def workspace(self):
        workspace_mock = MockWorkspace()
        return workspace_mock

    @property
    def parent(self):
        return MockParentRun(
            self.run_source, self.label_column_name, self.featurization, self.labeling_dataset_type
        )

    def log(self, metric_name, metric_val):
        if metric_name in self.metrics.keys():
            self.duplicate_metric_logged = True
        self.metrics[metric_name] = metric_val

    def add_properties(self, new_properties):
        self.properties.update(new_properties)

    def RaiseError(self):
        raise ValueError()

    def get_environment(self):
        return 'fake environment'

    def download_file(self, name, output_file_path=None, _validate_checksum=False):
        return None


class MockParentRun:
    def __init__(
            self,
            run_source,
            label_column_name,
            featurization,
            labeling_dataset_type
    ):
        self.metrics = {}
        settings_dict = {
            "label_column_name": label_column_name,
            "featurization": featurization
        }
        if labeling_dataset_type is not None:
            settings_dict["labeling_dataset_type"] = labeling_dataset_type
        self.properties = {
            "azureml.runsource": run_source,
            "AMLSettingsJsonString": json.dumps(settings_dict)
        }
        self.id = 'mock_run_id'

    @property
    def parent(self):
        return self


class MockWorkspace:
    def __init__(self):
        self.metrics = {}

    @property
    def datastores(self):
        datastore_mock = MagicMock()
        return {'datastore': datastore_mock, 'ner_data': datastore_mock}


class MockBertClass(torch.nn.Module):
    def __init__(self, num_labels):
        super(MockBertClass, self).__init__()
        self.num_labels = num_labels
        self.l1 = torch.nn.Linear(num_labels, num_labels)
        # number of times forward was called
        self.forward_called = 0
        self.train_called = False
        self.eval_called = False
        return

    def forward(self, ids, attention_mask, token_type_ids):
        self.forward_called = self.forward_called + 1
        return self.l1(torch.randn(ids.shape[0], self.num_labels))

    def train(self, mode=True):
        self.train_called = True
        super().train(mode)

    def eval(self):
        self.eval_called = True
        super().eval()


def file_dataset_mock():
    dataset_mock = MagicMock(FileDataset)
    dataset_mock.download.return_value = MagicMock()
    dataset_mock.to_path.side_effect = [["/train.txt"], ["/dev.txt"]]
    return dataset_mock


def ner_trainer_mock():
    mock_trainer = MagicMock()
    mock_trainer_result = MagicMock()
    mock_trainer_result.metrics.return_value = {"result_key": "result_value"}
    mock_trainer.train.return_value = mock_trainer_result
    mock_trainer.evaluate.return_value = {
        "eval_accuracy": 0.85,
        "eval_f1_score_micro": 0.21, "eval_f1_score_macro": 0.30, "eval_f1_score_weighted": 0.30,
        "eval_precision_score_micro": 0.28, "eval_precision_score_macro": 0.3, "eval_precision_score_weighted": 0.3,
        "eval_recall_score_micro": 0.41, "eval_recall_score_macro": 0.37, "eval_recall_score_weighted": 0.37,
    }
    return mock_trainer


def multiclass_trainer_mock(num_examples, num_cols=4):
    mock_trainer = MagicMock()
    mock_trainer.is_world_process_zero.return_value = True
    mock_trainer_result = MagicMock()
    mock_trainer.train.return_value = mock_trainer_result
    predictions = EvalPrediction(predictions=np.random.rand(num_examples, num_cols),
                                 label_ids=np.random.randint(0, high=num_cols, size=num_examples))
    mock_trainer.validate.return_value = predictions.predictions
    mock_trainer.predict.return_value = predictions
    return mock_trainer


def aml_dataset_mock(input_df):
    dataset_mock = MagicMock(AmlDataset)
    dataset_mock.to_pandas_dataframe.return_value = input_df
    return dataset_mock


def get_np_load_mock(file_to_load, allow_pickle=True):
    if file_to_load == MultiClassInferenceLiterals.LABEL_LIST:
        return np.array(['label_1', 'label_2', 'label_3'])
    else:
        return np.array([MultiClassParameters.MAX_SEQ_LENGTH_128])


def get_ner_labeling_df():
    dataset_df = pd.DataFrame()
    dataset_df['image_url'] = [
        StreamInfo(
            arguments={'datastoreName': 'ner_data'},
            handler='AmlDatastore',
            resource_identifier='sample1.txt'),
        StreamInfo(
            arguments={'datastoreName': 'ner_data'},
            handler='AmlDatastore',
            resource_identifier='sample2.txt')
    ]
    dataset_df['label'] = [
        [
            {'label': 'LOC', 'offsetStart': 20, 'offsetEnd': 25},
            {'label': 'LOC', 'offsetStart': 53, 'offsetEnd': 63},
            {'label': 'PER', 'offsetStart': 85, 'offsetEnd': 94}
        ],
        [
            {'label': 'PER', 'offsetStart': 0, 'offsetEnd': 14}
        ]
    ]
    dataset_df['label_confidence'] = [
        [1.0, 1.0, 1.0],
        [1.0]
    ]

    return dataset_df


def get_multilabel_labeling_df():
    dataset_df = pd.DataFrame()
    dataset_df['image_url'] = [
        StreamInfo(
            arguments={'datastoreName': 'datastore'},
            handler='AmlDatastore',
            resource_identifier='sample1.txt'),
        StreamInfo(
            arguments={'datastoreName': 'datastore'},
            handler='AmlDatastore',
            resource_identifier='sample2.txt'),
        StreamInfo(
            arguments={'datastoreName': 'datastore'},
            handler='AmlDatastore',
            resource_identifier='sample3.txt')
    ]
    dataset_df['label'] = [
        ['label_1', 'label_2'],
        [],
        ['label_1']
    ]
    dataset_df['label_confidence'] = [
        [1.0, 1.0],
        [],
        [1.0]
    ]

    return dataset_df


def get_multiclass_labeling_df():
    dataset_df = pd.DataFrame()
    dataset_df['image_url'] = [
        StreamInfo(
            arguments={'datastoreName': 'datastore'},
            handler='AmlDatastore',
            resource_identifier='sample1.txt'),
        StreamInfo(
            arguments={'datastoreName': 'datastore'},
            handler='AmlDatastore',
            resource_identifier='sample2.txt'),
        StreamInfo(
            arguments={'datastoreName': 'datastore'},
            handler='AmlDatastore',
            resource_identifier='sample3.txt')
    ]
    dataset_df['label'] = [
        'label_1',
        'label_2',
        'label_3'
    ]
    dataset_df['label_confidence'] = [
        1.0,
        1.0,
        1.0
    ]

    return dataset_df


def open_classification_file(filename, mode=None, encoding=None, errors=None):
    if filename.endswith('sample1.txt'):
        content = "Example text content 1. Multiple sentences."
    elif filename.endswith('sample2.txt'):
        content = "Example text content 2."
    elif filename.endswith('sample3.txt'):
        content = "Example text content 3, comma separated."
    elif filename.endswith('predictions.txt'):
        content = ""
    else:
        raise FileNotFoundError(filename)
    file_object = mock_open(read_data=content).return_value
    file_object.__iter__.return_value = content.splitlines(True)
    return file_object
