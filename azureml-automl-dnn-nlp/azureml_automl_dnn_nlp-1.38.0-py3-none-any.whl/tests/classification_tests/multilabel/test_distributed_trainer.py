import pytest
from unittest.mock import patch
import unittest
import torch
import importlib

from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer import HorovodDistributedTrainer
from azureml.automl.dnn.nlp.common.constants import Split
from torch.utils.data import RandomSampler
from torch.utils.data.distributed import DistributedSampler

horovod_spec = importlib.util.find_spec("horovod")
has_horovod = horovod_spec is not None


class MockPytorchTrainer:

    def __init__(self):
        self.n_valid_called = 0
        self.valod_called_last_with = None
        self.n_compute_called = 0
        self.compute_called_with = None

    def validate(self, valid_dataset):
        self.n_valid_called = self.n_valid_called + 1
        self.valid_called_last_with = valid_dataset
        return "outputs", "targets"

    def compute_metrics(self, valid_dataset):
        self.n_compute_called = self.n_compute_called + 1
        self.compute_called_with = valid_dataset
        return 0.5, 0.6, 0.7


class MockModelClass(torch.nn.Module):

    def __init__(self, download_dir, num_labels):
        super().__init__()
        self.l1 = torch.nn.Linear(10, 2)
        self.download_dir = download_dir
        self.labels = num_labels

    def to(self, device):
        self.device = device


@unittest.skipIf(not has_horovod, "Horovod not installed")
def test_initilization_horovod():
    mock_model_class = MockModelClass
    mocked_trainer = MockPytorchTrainer()
    pytorch_trainer_patch = "azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer.PytorchTrainer"
    with patch(pytorch_trainer_patch, return_value=mocked_trainer):
        with patch("horovod.torch.init", return_value=None):
            with patch("horovod.torch.broadcast_parameters", return_value=None):
                with patch("horovod.torch.broadcast_optimizer_state", return_value=None):
                    with patch("horovod.torch.rank", return_value=0):
                        with patch("horovod.common.util.gpu_available", return_value=False):
                            with patch("horovod.torch.local_rank", return_value=1):
                                with patch("torch.cuda.set_device", return_value=None):
                                    with patch("torch.device", return_value="cpu"):
                                        trainer = HorovodDistributedTrainer(mock_model_class, "some_path", 3)
                                        assert trainer.model.device == "cpu"


@unittest.skipIf(not has_horovod, "Horovod not installed")
@pytest.mark.parametrize('mode',
                         [Split.train,
                          Split.test])
def test_distributed_data_sampler(mode):
    init = "azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer.HorovodDistributedTrainer.__init__"
    with patch(init, return_value=None):
        with patch("horovod.torch.size", return_value=1):
            with patch("horovod.torch.rank", return_value=0):
                trainer = HorovodDistributedTrainer("some_class", "some_path", 3)
                sampler = trainer._data_sampler("some_dataset", mode)
                if mode == Split.train:
                    assert type(sampler) is DistributedSampler
                else:
                    assert type(sampler) is RandomSampler


def test_valid_runs_main_process():
    init = "azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer.HorovodDistributedTrainer.__init__"
    validate_patch = "azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer.PytorchTrainer.validate"
    with patch(validate_patch, return_value="some_validation_scores"):
        with patch(init, return_value=None):
            with patch("azureml.automl.dnn.nlp.common._utils.is_main_process", return_value=True):
                trainer = HorovodDistributedTrainer("some_class", "some_path", 3)
                result = trainer.validate("some_dataset")
    assert result == "some_validation_scores"


def test_valid_worker_process_raises_exception():
    init = "azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer.HorovodDistributedTrainer.__init__"
    validate_patch = "azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer.PytorchTrainer.validate"
    with patch(validate_patch, return_value="some_validation_scores"):
        with patch(init, return_value=None):
            with patch("azureml.automl.dnn.nlp.common._utils.is_main_process", return_value=False):
                with pytest.raises(ClientException):
                    trainer = HorovodDistributedTrainer("some_class", "some_path", 3)
                    trainer.validate("some_dataset")


def test_compute_runs_main_process():
    comp_patch = "azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer.PytorchTrainer.compute_metrics"
    init = "azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer.HorovodDistributedTrainer.__init__"
    with patch(comp_patch, return_value="some_metrics"):
        with patch(init, return_value=None):
            with patch("azureml.automl.dnn.nlp.common._utils.is_main_process", return_value=True):
                trainer = HorovodDistributedTrainer("some_class", "some_path", 3)
                result = trainer.compute_metrics("some_dataset")
    assert result == "some_metrics"


def test_compute_worker_process_raises_exception():
    comp_patch = "azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer.PytorchTrainer.compute_metrics"
    init = "azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer.HorovodDistributedTrainer.__init__"
    with patch(comp_patch, return_value="some_metrics"):
        with patch(init, return_value=None):
            with patch("azureml.automl.dnn.nlp.common._utils.is_main_process", return_value=False):
                with pytest.raises(ClientException):
                    trainer = HorovodDistributedTrainer("some_class", "some_path", 3)
                    trainer.compute_metrics("some_dataset")
