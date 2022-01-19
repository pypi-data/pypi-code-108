"""
This file contains the default logic to build a dataloader for training or testing.
In contrast to the detectron2/data/build.py this file implements similar functions
but for image classificaion and distance learning use cases.
"""
import logging
from typing import Dict, Iterable, Union, Callable

import numpy as np

import torch.utils.data as torchdata
import detectron2
from detectron2.config import configurable, CfgNode
from detectron2.data.samplers import InferenceSampler
from detectron2.data.build import trivial_batch_collator, _test_loader_from_config, worker_init_reset_seed
from detectron2.data.samplers import (
    RepeatFactorTrainingSampler,
    TrainingSampler
)
from torch.utils.data import DataLoader, Dataset, Sampler
try:
    from detectron2.data.samplers.distributed_sampler import RandomSubsetTrainingSampler
except ImportError:
    RandomSubsetTrainingSampler = None

from detectron2.data import DatasetMapper
from detectron2.data.common import MapDataset, DatasetFromList
from detectron2.data import transforms as T

from detectron2.data.build import build_batch_data_loader

from sap_computer_vision.data.image_classification import DatasetMapperClassification, get_classification_dataset_dicts
from sap_computer_vision.data.samplers import PKTripletSampler, TripletTrainSampler, TripletReservoirSampler, triplet_collator_fn

from .augs import build_augmentations, generate_aug_cfg_node


def _test_loader_from_config_batched(cfg, *args, **kwargs):
    return {**_test_loader_from_config(cfg, *args, **kwargs),
            "batch_size": cfg.SOLVER.get('IMS_PER_BATCH_EVAL', cfg.SOLVER.IMS_PER_BATCH)}


@configurable(from_config=_test_loader_from_config_batched)
def build_detection_test_loader_batched(dataset, *, mapper, sampler=None, num_workers=0, batch_size=1) -> DataLoader:
    """
    Similar to `build_detection_train_loader`, but uses a batch size of 1,
    and :class:`InferenceSampler`. This sampler coordinates all workers to
    produce the exact set of all samples.
    This interface is experimental.
    Parameters
    ----------
    dataset (list or torch.utils.data.Dataset): a list of dataset dicts,
        or a map-style pytorch dataset. They can be obtained by using
        :func:`DatasetCatalog.get` or :func:`get_detection_dataset_dicts`.
    mapper: callable
        a callable which takes a sample (dict) from dataset
        and returns the format to be consumed by the model.
        When using cfg, the default choice is ``DatasetMapper(cfg, is_train=False)``.
    sampler: torch.utils.data.sampler.Sampler or None, optinal, default=None
        A sampler that produces
        indices to be applied on ``dataset``. Default to :class:`InferenceSampler`,
        which splits the dataset across all workers.
    num_workers: int, optional, default=0:
        Number of parallel data loading workers
    batch_size: int, optional, default=1
        Batch_size
    Returns
    ----------
    torch.DataLoader
        A torch DataLoader, that loads the given detection
        dataset, with test-time transformation and batching.

    Examples
    --------
    Examples:
    ::
        data_loader = build_detection_test_loader(
            DatasetRegistry.get("my_test"),
            mapper=DatasetMapper(...))
        # or, instantiate with a CfgNode:
        data_loader = build_detection_test_loader(cfg, "my_test")
    """
    if isinstance(dataset, list):
        dataset = DatasetFromList(dataset, copy=False)
    if mapper is not None:
        dataset = MapDataset(dataset, mapper)
    if sampler is None:
        sampler = InferenceSampler(len(dataset))
    batch_sampler = torchdata.sampler.BatchSampler(sampler, batch_size, drop_last=False)
    data_loader = torchdata.DataLoader(
        dataset,
        num_workers=num_workers,
        batch_sampler=batch_sampler,
        collate_fn=trivial_batch_collator,
    )
    return data_loader


def _classification_train_loader_from_config(cfg: Dict,
                                             mapper: Union[Callable, None]=None,
                                             *,
                                             dataset: Union[Dataset, None]=None,
                                             sampler: Union[Sampler, None]=None,
                                             triplet_excludes: Union[Dict, None]=None,
                                             collate_fn: Union[None, Callable]=None) -> Dict:
    """Function to create classification/distance metric learning dataloader from cfg.

    This functions is not intended to be used directly.
    Check :func:`build_classification_train_loader` for all parameters not documented here.


    Parameters
    ----------
    triplet_excludes: None or dict, optional, default=None
        Triplet exclude dict passed to sampler, if sampler supports it.
        Check sap_computer_vision.data.samplers for more details on the different samplers.
        This parameters is meant for distance metric learning.
    Returns
    ----------
    dict
        kwargs for :func:`build_classification_train_loader`
    """
    if dataset is None:
        dataset = get_classification_dataset_dicts(cfg.DATASETS.TRAIN)

    if mapper is None:
        mapper = DatasetMapperClassification(cfg, True)   # pylint: disable=E1125, E1121

    aspect_ratio_grouping = cfg.DATALOADER.ASPECT_RATIO_GROUPING
    if sampler is None:
        sampler_name = cfg.DATALOADER.SAMPLER_TRAIN
        logger = logging.getLogger(__name__)
        logger.info("Using training sampler {}".format(sampler_name))
        if sampler_name == "TrainingSampler":
            sampler = TrainingSampler(len(dataset))
        elif sampler_name == "RepeatFactorTrainingSampler":
            repeat_factors = RepeatFactorTrainingSampler.repeat_factors_from_category_frequency(
                dataset, cfg.DATALOADER.REPEAT_THRESHOLD
            )
            sampler = RepeatFactorTrainingSampler(repeat_factors)
        elif sampler_name == "RandomSubsetTrainingSampler":
            if RandomSubsetTrainingSampler is None:
                raise ImportError('To use `RandomSubsetTrainingSampler` detectron > 0.5.0 is need.'
                                  f' (installed: {detectron2.__version__}).')
            else:
                sampler = RandomSubsetTrainingSampler(len(dataset), cfg.DATALOADER.RANDOM_SUBSET_RATIO)
        elif sampler_name == "PKSampler":
            class_ids = np.array([d["class_id"] for d in dataset], dtype=int)
            sampler = PKTripletSampler(p=cfg.DATALOADER.PK_SAMPLER.P_CLASSES_PER_BATCH,
                                       k=cfg.DATALOADER.PK_SAMPLER.K_EXAMPLES_PER_CLASS,
                                       class_ids=class_ids,
                                       ignore_class_weights=cfg.DATALOADER.PK_SAMPLER.IGNORE_CLASS_WEIGHTS,
                                       rng=cfg.SEED,
                                       excludes=triplet_excludes,
                                       return_batch=True,
                                       infinite_stream=True)
            aspect_ratio_grouping = False
            collate_fn = trivial_batch_collator if collate_fn is None else collate_fn
        elif sampler_name == "TripletSampler":
            class_ids = np.array([d["class_id"] for d in dataset], dtype=int)
            sampler = TripletTrainSampler(class_ids=class_ids,
                                          n_triplets_per_batch=cfg.SOLVER.IMS_PER_BATCH,
                                          rng=cfg.SEED,
                                          excludes=triplet_excludes,
                                          return_batch=True,
                                          infinite_stream=True)
            aspect_ratio_grouping = False
            collate_fn = triplet_collator_fn if collate_fn is None else collate_fn
        elif sampler_name == "TripletReservoirSampler":
            class_ids = np.array([d["class_id"] for d in dataset], dtype=int)
            sampler = TripletReservoirSampler(class_ids=class_ids,
                                              n_triplets_per_batch=cfg.SOLVER.IMS_PER_BATCH,
                                              k_examples_per_class=cfg.DATALOADER.TRIPLET_RESERVOIR_SAMPLER.K_EXAMPLES_PER_CLASS,
                                              reservoir_of_n_batches=cfg.DATALOADER.TRIPLET_RESERVOIR_SAMPLER.N_BATCHES_PER_RESERVOIR,
                                              refresh_after_n_batches=cfg.DATALOADER.TRIPLET_RESERVOIR_SAMPLER.REFRESH_EVERY_N_STEPS,
                                              n_random_batches_start=cfg.DATALOADER.TRIPLET_RESERVOIR_SAMPLER.NUM_STEPS_RANDOM,
                                              strategy=cfg.DATALOADER.TRIPLET_RESERVOIR_SAMPLER.TRIPLET_STRATEGY,
                                              rng=cfg.SEED,
                                              excludes=triplet_excludes,
                                              return_batch=True,
                                              infinite_stream=True)
            aspect_ratio_grouping = False
            collate_fn = triplet_collator_fn if collate_fn is None else collate_fn
        else:
            raise ValueError("Unknown training sampler: {}".format(sampler_name))
    return {
        "dataset": dataset,
        "sampler": sampler,
        "mapper": mapper,
        "total_batch_size": sampler.batch_size if isinstance(sampler, PKTripletSampler) else cfg.SOLVER.IMS_PER_BATCH,
        "aspect_ratio_grouping": aspect_ratio_grouping,
        "collate_fn": collate_fn,
        "num_workers": cfg.DATALOADER.NUM_WORKERS,
    }


@configurable(from_config=_classification_train_loader_from_config)
def build_classification_train_loader(
    dataset, *, mapper, total_batch_size, sampler=None, aspect_ratio_grouping=True, num_workers=0, collate_fn=None) -> DataLoader:
    """
    Build a dataloader for image classification with some default features.
    This interface is experimental.

    Parameters
    ----------
    dataset: list or torch.utils.data.Dataset
        A list of dataset dicts,
        or a pytorch dataset (either map-style or iterable). It can be obtained
        by using :func:`DatasetCatalog.get` or :func:`get_class_dataset_dicts`.
    mapper: callable
        A callable which takes a sample (dict) from dataset and
        returns the format to be consumed by the model.
        When using cfg, the default choice is ``DatasetMapper(cfg, is_train=True)``.
    total_batch_size: int
        total batch size across all workers. Batching
        simply puts data into a list.
    sampler: torch.utils.data.sampler.Sampler or None):
        A sampler that produces indices to be applied on ``dataset``.
        If ``dataset`` is map-style, the default sampler is a :class:`TrainingSampler`,
        which coordinates an infinite random shuffle sequence across all workers.
        Sampler must be None if ``dataset`` is iterable.
    aspect_ratio_grouping: bool, optinal, default=True
        whether to group images with similar
        aspect ratio for efficiency. When enabled, it requires each
        element in dataset be a dict with keys "width" and "height".
    num_workers: int
        number of parallel data loading workers
    collate_fn: None or callable
        Collate functions passed to the Dataloader. If None a default collate function
        depending on the selected Sampler will be used.

    Returns
    ----------
    torch.utils.data.DataLoader:
        a dataloader. Each output from it is a ``list[mapped_element]`` of length
        ``total_batch_size / num_workers``, where ``mapped_element`` is produced
        by the ``mapper``.
    """
    if isinstance(dataset, list):
        dataset = DatasetFromList(dataset, copy=False)
    if mapper is not None:
        dataset = MapDataset(dataset, mapper)

    if isinstance(dataset, torchdata.IterableDataset):
        assert sampler is None, "sampler must be None if dataset is IterableDataset"
    else:
        if sampler is None:
            sampler = TrainingSampler(len(dataset))
        assert isinstance(sampler, torchdata.Sampler), f"Expect a Sampler but got {type(sampler)}"

    if getattr(sampler, 'return_batch', False):
        #dataset = ToIterableDataset(dataset, sampler)
        return DataLoader(
            dataset,
            batch_sampler=sampler,
            num_workers=num_workers,
            collate_fn=collate_fn,
            worker_init_fn=worker_init_reset_seed
        )
    else:
        return build_batch_data_loader(
            dataset,
            sampler,
            total_batch_size,
            aspect_ratio_grouping=aspect_ratio_grouping,
            num_workers=num_workers,
        )


def _classification_test_loader_from_config_batched(cfg, dataset_name, mapper=None):
    """
    Uses the given `dataset_name` argument (instead of the names in cfg), because the
    standard practice is to evaluate each test set individually (not combining them).
    """
    if isinstance(dataset_name, str):
        dataset_name = [dataset_name]

    dataset = get_classification_dataset_dicts(dataset_name)
    if mapper is None:
        mapper = DatasetMapperClassification(cfg, False)  # pylint: disable=E1125, E1121
    return {"dataset": dataset,
            "mapper": mapper,
            "num_workers": cfg.DATALOADER.NUM_WORKERS,
            "batch_size": cfg.SOLVER.get('IMS_PER_BATCH_EVAL', cfg.SOLVER.IMS_PER_BATCH)}


@configurable(from_config=_classification_test_loader_from_config_batched)
def build_classification_test_loader_batched(dataset, *, mapper, sampler=None, num_workers=0, batch_size=1):
    """
    Similar to `build_classification_train_loader`, but uses a batch size of 1,
    and :class:`InferenceSampler`. This sampler coordinates all workers to
    produce the exact set of all samples.
    This interface is experimental.

    Parameters
    ----------
    dataset: list or torch.utils.data.Dataset
        a list of dataset dicts,
        or a map-style pytorch dataset. They can be obtained by using
        :func:`DatasetCatalog.get` or :func:`get_classification_dataset_dicts`.
    mapper: callable
        a callable which takes a sample (dict) from dataset
       and returns the format to be consumed by the model.
       When using cfg, the default choice is ``DatasetMapper(cfg, is_train=False)``.
    sampler: torch.utils.data.sampler.Sampler or None
        a sampler that produces
        indices to be applied on ``dataset``. Default to :class:`InferenceSampler`,
        which splits the dataset across all workers.
    num_workers: int
        number of parallel data loading workers
    batch_size: int
        Batch_size

    Returns
    ----------
    DataLoader: a torch DataLoader
        That loads the given classification
        dataset, with test-time transformation and batching.
    Examples:
    ::
        data_loader = build_classification_test_loader(
            DatasetRegistry.get("my_test"),
            mapper=DatasetMapper(...))
        # or, instantiate with a CfgNode:
        data_loader = build_classification_test_loader(cfg, "my_test")
    """
    if isinstance(dataset, list):
        dataset = DatasetFromList(dataset, copy=False)
    if mapper is not None:
        dataset = MapDataset(dataset, mapper)
    if sampler is None:
        sampler = InferenceSampler(len(dataset))
    batch_sampler = torchdata.sampler.BatchSampler(sampler, batch_size, drop_last=False)
    data_loader = torchdata.DataLoader(
        dataset,
        num_workers=num_workers,
        batch_sampler=batch_sampler,
        collate_fn=trivial_batch_collator,
    )
    return data_loader


class DatasetMapperWithAdditionalAugmentaions(DatasetMapper):
    """This DatasetMapper extends the default detectron2.data.DatasetMapper
    to accepts a list on additional augmenations and to append a final
    resize transformation to the list if cfg.INPUT.FIXED_IMAGE_SIZE is set.
    """

    @classmethod
    def from_config(cls,
                    cfg: 'CfgNode',
                    is_train: bool = True,
                    additional_augs_orignal_image: Iterable['T.Transform']=None,
                    additional_augs_resized_image: Iterable['T.Transform']=None,
                    ) -> Dict:
        """Classmethod to create an instance based on the config.

        Check detectron configs mechanism.

        Parameters
        ----------
        cfg: CfgNode
            Config
        is_train: bool, optional, default=None
            Indicator if DatasetMapper is used for training.
            This enables random ordering of examples.
        additional_augs_orignal_image: None or Iterable of T.Transform
            Optional list of additional augementations. Those augmentations are applied before
            the image is brought to its original size.
        additional_augs_resized_image: None or Iterable of T.Transform
            Optional list of additional augementations. Those augmentations are applied after
            the image is brought to its original size.

        Returns
        -------
        dict
            Dict with the relevant kwargs. This dict can be consumed by the
            __init__ function.
        """
        ret = super(DatasetMapperWithAdditionalAugmentaions, cls).from_config(cfg, is_train)
        cfg_augs = generate_aug_cfg_node(cfg, cfg.INPUT if is_train else CfgNode({}), is_train)
        ret['augmentations'] = build_augmentations(cfg_augs, cfg.INPUT.FORMAT)
        if additional_augs_orignal_image is not None:
            ret['augmentations'] = [*additional_augs_orignal_image] + ret['augmentations']
        if additional_augs_resized_image is not None:
            ret['augmentations'].extend(additional_augs_resized_image)
        return ret
