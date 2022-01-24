# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains dataloader functions for the package."""
import torch

from torch.utils.data import Sampler, BatchSampler
from torch.utils.data.dataloader import default_collate
from torch.utils.data.distributed import DistributedSampler

from azureml.automl.dnn.vision.common.dataloaders import RobustDataLoader
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException


def _one_hot_encode(label_list, num_classes=None):
    if num_classes is None:
        raise AutoMLVisionValidationException('num_classes needs to be passed', has_pii=False)
    one_hot_label = torch.zeros(num_classes)
    one_hot_label[label_list] = 1

    return one_hot_label


class _CollateFn:
    def __init__(self, f, multilabel=False, num_classes=None):
        """Collate function for the dataloader that performs transformations on dataset input. Since pytorch
        multiprocessing needs to pickle objects, we could not have nested functions.
        Therefore this ends up as a class.

        :param f: function that takes in a pillow image and returns a torch Tensor.
        :type f: function
        :param multilabel: whether this is a multilabel dataset
        :type multilabel: bool
        :param num_classes: number of classes
        :type num_classes: int
        :return: function that can take a batch of tuples of pillow images and labels and returns tensors of
        transformed
        images and the label.
        :rtype: function
        """
        if multilabel and num_classes is None:
            raise AutoMLVisionValidationException('num_classes needs to be set if multilabel is True', has_pii=False)
        self._multilabel = multilabel
        self._num_classes = num_classes
        self._func = f

    def __call__(self, x):
        batch = []
        for im, label in x:
            if self._multilabel:
                label = _one_hot_encode(label, num_classes=self._num_classes)
            batch.append((self._func(im), label))

        return default_collate(batch)


def _get_data_loader(dataset_wrapper, is_train=False, transform_fn=None, batch_size=None, num_workers=None,
                     distributed=False):
    """Get data loader for the torch dataset only loading the selected indices and transforming the input images using
    transform_fn.

    :param dataset_wrapper: dataset wrapper
    :type dataset_wrapper: azureml.automl.dnn.vision.io.read.dataset_wrapper.BaseDatasetWrapper
    :param is_train: is this data for training
    :type is_train: bool
    :param transform_fn: function that takes a pillow image and returns a torch Tensor
    :type transform_fn: function
    :param batch_size: batch size for dataloader
    :type batch_size: int
    :param num_workers: num workers for dataloader
    :type num_workers: int
    :param distributed: Whether to use distributed data loader.
    :type distributed: bool
    :return: dataloader
    :rtype: torch.utils.data.DataLoader
    """
    if transform_fn is None:
        transform_fn = _identity

    collate_fn = _CollateFn(transform_fn, multilabel=dataset_wrapper.multilabel,
                            num_classes=dataset_wrapper.num_classes)

    if distributed:
        sampler: Sampler[int] = DistributedSampler(dataset_wrapper, shuffle=is_train)
        batch_sampler = BatchSampler(sampler, batch_size, drop_last=False)
        # In distributed mode, we launch the distributed workers using torch.multiprocessing.spawn.
        # This sets the multiprocessing context to "spawn" for all multiprocessing operations, including data
        # loader workers launched when num_workers > 1. Using "spawn" is usually slower than the default "fork".
        # This results in the first mini-batch load time in every epoch to be significantly high because
        # workers are created every time a dataloader iterator is created.
        # Set the multiprocessing context as "fork" here to address the high mini-batch load times.
        return RobustDataLoader(dataset_wrapper,
                                batch_sampler=batch_sampler,
                                num_workers=num_workers,
                                multiprocessing_context="fork",
                                collate_fn=collate_fn,
                                distributed_sampler=sampler)
    else:
        return RobustDataLoader(dataset_wrapper, batch_size=batch_size, shuffle=is_train,
                                collate_fn=collate_fn, num_workers=num_workers)


def _identity(x):
    """
    :param x: any input
    :type x: any type
    :return: return the input
    :rtype: any type
    """
    return x
