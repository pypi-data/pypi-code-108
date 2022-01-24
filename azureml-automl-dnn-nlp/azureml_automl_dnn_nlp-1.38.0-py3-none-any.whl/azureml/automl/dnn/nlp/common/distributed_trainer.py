# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Distributed extention of HF Trainer using Horovod"""

import torch
from transformers import Trainer, TrainingArguments
from torch.utils.data.distributed import DistributedSampler
import logging

from azureml.automl.dnn.nlp.common._utils import is_main_process
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import RuntimeModuleDependencyMissing
from azureml.automl.core.shared.exceptions import ConfigException


_logger = logging.getLogger(__name__)


try:
    import horovod.torch as hvd
    from horovod.common.util import gpu_available
    has_horovod = True
except Exception as e:
    _logger.warning("Horovod unavailable in environment. Distributed training will be disabled")
    has_horovod = False
    _logger.info(str(e))


class DistributedTrainingArguments(TrainingArguments):
    """Class to extend HF Training Arguments to support distributed cuda setup with Horovod"""

    def __init__(self, training_args):
        """
        Function to initialize DistributedTrainingArguments similar to the TrainingArguments
        param training_args: HF training args to be used
        """
        super().__init__(output_dir=training_args.output_dir,
                         per_device_train_batch_size=training_args.per_device_train_batch_size,
                         per_device_eval_batch_size=training_args.per_device_eval_batch_size,
                         num_train_epochs=training_args.num_train_epochs,
                         save_strategy=training_args.save_strategy,
                         gradient_accumulation_steps=training_args.gradient_accumulation_steps,
                         logging_strategy=training_args.logging_strategy,
                         report_to=training_args.report_to)

    @property
    def device(self) -> "torch.device":
        """
        Property returns current cuda device in use
        :return currnt cuda device
        """
        return torch.device("cuda", hvd.local_rank())

    def _setup_devices(self):
        """
        Function sets cuda device using horovod's local rank (same as mpi local rank) and returns current device
        :return current cuda device
        """
        self._n_gpu = 1
        torch.cuda.set_device(hvd.local_rank())
        return torch.device("cuda", hvd.local_rank())

    @property
    def n_gpu(self):
        """
        Function to override n_gpu value for disitrbuted horovod training, which is always 1
        :return n_gpu value, which is 1 for horovod training
        """
        return self._n_gpu


class DistributedTrainer(Trainer):
    """Class to extend HF trainer to distributed mode using Horovod"""

    def __init__(self, model, args, train_dataset, **kwargs):
        """
        Function to initialize DistributedTrainer ready horovod for distributed training

        :param model: text classification model to be trianed
        :param args: HF training args to be used
        :param train_dataset: classification text dataset with labels
        :param tokenizer: HF tokenizer
        :param data_collator: data_collator used for training
        """
        if not has_horovod:
            raise ConfigException._with_error(
                AzureMLError.create(RuntimeModuleDependencyMissing, target="horovod", module_name="horovod")
            )
        if not gpu_available('torch'):
            _logger.warning("Horovod could not find GPUs")

        hvd.init()
        args = DistributedTrainingArguments(args)
        args.learning_rate = hvd.local_size() * args.learning_rate

        super().__init__(model=model,
                         args=args,
                         train_dataset=train_dataset,
                         **kwargs)
        hvd.broadcast_parameters(self.model.state_dict(), root_rank=0)

    def create_optimizer(self):
        """
        Function to override optimizer initializaiton in HF trainer to use distributed optimizer
        This function also broadcasts the initial optimizer state to all nodes to keep it consistent
        """
        super().create_optimizer()
        self.optimizer = hvd.DistributedOptimizer(self.optimizer, named_parameters=self.model.named_parameters(),
                                                  compression=hvd.Compression.fp16, op=hvd.Adasum)
        hvd.broadcast_optimizer_state(self.optimizer, root_rank=0)

    def _get_train_sampler(self):
        """
        Function to update sampler used for distributed training
        :return sampler for the local partition of the dataset
        """
        return DistributedSampler(self.train_dataset, num_replicas=hvd.size(), rank=hvd.rank())

    def evaluate(self, eval_dataset):
        """
        Function to override HF trainer's evaluate to only trigger when the process is main process
        :param eval_dataset: dataset to use for evaluation
        """
        if is_main_process():
            return super().evaluate(eval_dataset=eval_dataset)

    def predict(self, test_dataset):
        """
        Function to override HF trainer's predict to only trigger when the process is main process
        :param test_dataset: dataset to use for prediction
        """
        if is_main_process():
            return super().predict(test_dataset=test_dataset)
