# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class for training Pytorch Models in distributed"""

import logging
import torch
from torch.utils.data import RandomSampler
from torch.utils.data.distributed import DistributedSampler
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import RuntimeModuleDependencyMissing
from azureml.automl.core.shared.exceptions import ClientException, ConfigException
from azureml.automl.dnn.nlp.common.constants import Split
from azureml.automl.dnn.nlp.classification.common.constants import MultiLabelParameters
from azureml.automl.dnn.nlp.classification.multilabel.trainer import PytorchTrainer
from azureml.automl.dnn.nlp.common import _utils

_logger = logging.getLogger(__name__)


try:
    import horovod.torch as hvd
    from horovod.common.util import gpu_available
    has_horovod = True
except Exception:
    _logger.warning("Horovod unavailable in environment. Distributed training will be disabled")
    has_horovod = False


class HorovodDistributedTrainer(PytorchTrainer):
    """This class runs training routine in a distributed mode. It uses horovod to distribute across many gpus/nodes"""

    def __init__(self,
                 model_class,
                 dataset_language,
                 num_label_cols,
                 is_gpu=True):
        """
        Function initializes horovod trainer, and sets up model for training

        :param model_class: Class to use for model initialization
        :param dataset_language: language code of dataset
        :param num_label_cols: Number of unique classes in label column
        :param is_gpu: Setting to allow for gpu training
        """
        if not has_horovod:
            raise ConfigException._with_error(
                AzureMLError.create(RuntimeModuleDependencyMissing, target="horovod", module_name="horovod")
            )
        hvd.init()
        super().__init__(model_class, dataset_language, num_label_cols, is_gpu=(is_gpu and gpu_available('torch')))
        self.optimizer = hvd.DistributedOptimizer(self.optimizer, named_parameters=self.model.named_parameters(),
                                                  compression=hvd.Compression.fp16, op=hvd.Adasum)
        hvd.broadcast_parameters(self.model.state_dict(), root_rank=0)
        hvd.broadcast_optimizer_state(self.optimizer, root_rank=0)

    def _get_learning_rate(self):
        learning_rate = MultiLabelParameters.LEARNING_RATE
        return hvd.local_size() * learning_rate

    def _get_device(self, is_gpu=True):
        """
        Device can differ based on trainer. This function is used to get device based on what the trainer needs
        """
        torch.cuda.set_device(hvd.local_rank())
        return torch.device("cuda", hvd.local_rank())

    def _data_sampler(self, dataset, mode=Split.train):
        """
        Function to choose data sampling type

        :param dataset: Pytorch dataset object to be used to sample
        :param mode: Split enum to use to choose sampling method
        """
        if mode == Split.train:
            return DistributedSampler(dataset, num_replicas=hvd.size(), rank=hvd.rank())
        else:
            return RandomSampler(dataset)

    def validate(self, valid_set):
        """
        Function to start model validation. This method can only be run from main process

        :param valid_set: Pytorch dataset object to use for validation
        """
        if _utils.is_main_process():
            return super().validate(valid_set)
        else:
            raise ClientException('Validation should not be called for non-main processes', has_pii=False)

    def compute_metrics(self, valid_set):
        """
        Function to start computing metrics on validation dataset

        :param valid_set: Pytorch dataset object to use for computing metrics
        """
        if _utils.is_main_process():
            return super().compute_metrics(valid_set)
        else:
            raise ClientException('Metric computation should not be called for non-main processes', has_pii=False)
