# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Dataloaders"""
import torch.utils.data as data

from typing import Any, Callable, Iterable, List, Tuple, TypeVar

from torch.utils.data.dataloader import default_collate
from torch.utils.data.distributed import DistributedSampler

from ..common.exceptions import AutoMLVisionDataException, AutoMLVisionSystemException
from .logging_utils import get_logger

T_co = TypeVar('T_co', covariant=True)

logger = get_logger(__name__)


class _RobustCollateFn:
    """Wraps the collate fn so that we can filter None items. Since pytorch multiprocessing needs to pickle objects,
    we could not have nested functions. Therefore this ends up as a class."""

    EMPTY_BATCH_ERROR_MESSAGE = "No images left in batch after removing None values."

    def __init__(self, collate_fn: Callable[..., Iterable[Any]] = default_collate) -> None:
        self._collate_fn = collate_fn

    def __call__(self, batch_of_tuples: List[Tuple[Any, ...]]) -> Iterable[Any]:
        # check all indices that have None in them and remove them before calling default_collate
        none_indices = []
        for i, items in enumerate(batch_of_tuples):
            if any([x is None for x in items]):
                none_indices.append(i)
        for i in range(len(none_indices) - 1, -1, -1):
            del batch_of_tuples[none_indices[i]]

        if len(batch_of_tuples) == 0:
            raise AutoMLVisionDataException(self.EMPTY_BATCH_ERROR_MESSAGE, has_pii=False)
        return self._collate_fn(batch_of_tuples)


class RobustDataLoader(data.DataLoader[T_co]):
    """A replacement for torch.utils.data.DataLoader that filters None items. Accepts same args
    as torch.utils.data.DataLoader."""
    COLLATE_FN = 'collate_fn'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        :param args: positional arguments
        :type args: List
        :param kwargs: dictionary of keyword arguments and their values
        :type kwargs: Dict[str, type]
        """
        if 'num_workers' not in kwargs or kwargs['num_workers'] is None:
            raise AutoMLVisionSystemException("num_workers not specified or None")

        logger.info("Using {} num_workers.".format(kwargs['num_workers']))
        passed_collate_fn = default_collate
        if RobustDataLoader.COLLATE_FN in kwargs:
            passed_collate_fn = kwargs.pop(RobustDataLoader.COLLATE_FN)
        collate_fn = _RobustCollateFn(passed_collate_fn)

        self._distributed_sampler = kwargs.pop("distributed_sampler", None)

        super().__init__(*args, collate_fn=collate_fn, **kwargs)

    @property
    def distributed_sampler(self) -> DistributedSampler:
        """ Get the distributed sampler used in the loader.

        :return: DistributedSampler if the loader is initiated in distributed mode, None otherwise
        :rtype: torch.utils.data.distributed.DistributedSampler or None
        """
        return self._distributed_sampler
