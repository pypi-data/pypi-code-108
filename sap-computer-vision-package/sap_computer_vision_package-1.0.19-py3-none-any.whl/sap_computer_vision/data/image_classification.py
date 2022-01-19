import itertools
import logging
from typing import Iterable, List, NoReturn, Union, Dict
import copy
from detectron2.data.transforms import augmentation

import numpy as np
from tabulate import tabulate
from termcolor import colored
import torch

from detectron2.data.catalog import DatasetCatalog, MetadataCatalog
from detectron2.data import transforms as T
import detectron2.data.detection_utils as utils
from detectron2.utils.logger import log_first_n
from detectron2.config import configurable, CfgNode

from .augs import build_augmentations, generate_aug_cfg_node


logger = logging.getLogger(__name__)


def print_instances_classification_histogram(dataset_dicts, class_names, class_limit=100) -> NoReturn:
    """
    Parameters
    ----------
    dataset_dicts: list[dict]
        list of dataset dicts.
    class_names: list[str]
        list of class names (zero-indexed).
    """
    num_classes = len(class_names)
    hist_bins = np.arange(num_classes + 1)
    classes = np.asarray([x["class_id"] for x in dataset_dicts], dtype=np.int32)
    histogram = np.histogram(classes, bins=hist_bins)[0]

    N_COLS = min(6, len(class_names) * 2)

    def short_name(x):
        # make long class names shorter. useful for lvis
        if len(x) > 13:
            return x[:11] + ".."
        return x

    data = list(
        itertools.chain(*[[short_name(class_names[i]), int(v)] for i, v in enumerate(histogram)])
    )
    total_num_instances = sum(data[1::2])
    data.extend([None] * (N_COLS - (len(data) % N_COLS)))
    msg = "Distribution of instances among all {} categories:\n".format(num_classes)
    if num_classes > 1:
        data.extend(["total", total_num_instances])
    if num_classes <= class_limit:
        data = itertools.zip_longest(*[data[i::N_COLS] for i in range(N_COLS)])
        table = tabulate(
            data,
            headers=["category", "#instances"] * (N_COLS // 2),
            tablefmt="pipe",
            numalign="left",
            stralign="center",
        )
        msg += colored(table, "cyan")
    else:
        msg += colored(f"{total_num_instances} instances in total\n[distribution print limited: {class_limit} classes]", "cyan")
    log_first_n(
        logging.INFO,
        msg,
        key="message",
    )


def get_classification_dataset_dicts(names: Iterable[str]) -> Dict:
    """Convenience function get get the dataset dics for a list of datsets.

    If the datasets are retrieved for the first time a histogram for the class
    distribution is printed.

    Parameters
    ----------
    names: Iterable[str][dict]
        iterable containing the dataset names.

    Returns
    ----------
    list(dict)
        list of the dataset entries
    """
    dataset_dicts = [DatasetCatalog.get(dataset_name) for dataset_name in names]
    dataset_dicts = list(itertools.chain.from_iterable(dataset_dicts))
    has_instances = "class_id" in dataset_dicts[0]
    if has_instances:
        try:
            class_names = MetadataCatalog.get(names[0]).classes
            utils.check_metadata_consistency("classes", names)
            print_instances_classification_histogram(dataset_dicts, class_names)
        except AttributeError:  # class names are not available for this dataset
            pass

    assert len(dataset_dicts), "No valid data found in {}.".format(",".join(names))
    return dataset_dicts


class DatasetMapperClassification:
    """A callable which takes a dataset dict in Detectron2 Dataset format,
    and map it into a format used by the model.
    This is the default callable to be used to map your dataset dict into training data.
    You may need to follow it to implement your own one for customized logic,
    such as a different way to read or transform images.
    This an adaption of the detectron2.data.DatasetMapper class for
    image classification and distance learning.
    See :doc:`/tutorials/data_loading` for details of detectron 2.
    The callable currently does the following:
    1. Read the image from "file_name"
    2. Applies augmentations to the image
    3. Prepare data as Tensors

    Attributes
    ----------
    is_train: bool
        If mapper used for training dataset
    augmentations: detectron2.data.transform.AugmentationList
        List of detectron2.data.transform.Augmentations
    image_format: str
        Image format. Most detectron models expect BGR format.
    """

    @configurable
    def __init__(self,
                 is_train: bool,
                 *,
                 augmentations: List[Union[T.Augmentation, T.Transform]],
                 image_format: str):
        """
        NOTE: this interface is experimental.

        Parameters
        ----------
        is_train: bool
            whether it's used in training or inference
        augmentations: List of detectron2.data.transform.Augmentation
            a list of augmentations or deterministic transforms to apply
        image_format: str
            an image format supported by :func:`detection_utils.read_image`.
        """
        self.is_train = is_train
        self.augmentations = T.AugmentationList(augmentations)
        self.image_format = image_format
        logger = logging.getLogger(__name__)
        mode = "training" if is_train else "inference"
        logger.info(f"[DatasetMapperClassification] Augmentations used in {mode}: {augmentations}")

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
        cfg_augs = generate_aug_cfg_node(cfg, cfg.INPUT if is_train else CfgNode({}), is_train)
        augmentations = build_augmentations(cfg_augs, cfg.INPUT.FORMAT)
        if additional_augs_orignal_image is not None:
            augmentations = [*additional_augs_orignal_image] + augmentations
        if additional_augs_resized_image is not None:
            augmentations.extend(additional_augs_resized_image)
        ret = {
            "is_train": is_train,
            "augmentations": augmentations,
            "image_format": cfg.INPUT.FORMAT
        }
        return ret

    def _load_image(self, img) -> Dict:
        """Function to load image, check size and apply augmentations and add
        loaded image to example dict.

        Parameters
        ----------
        img: dict
            Dict representing an example of the dataset

        Returns
        -------
        dict
            Input dict extended with the loaded image
        """
        image = utils.read_image(img["file_name"], format=self.image_format)
        img['width'], img['height'] = (image.shape[1], image.shape[0])
        utils.check_image_size(img, image)
        aug_input = T.AugInput(image)
        self.augmentations(aug_input)
        image = aug_input.image
        img['image'] = torch.as_tensor(np.ascontiguousarray(image.transpose(2, 0, 1)))
        return img

    def __call__(self, dataset_dict) -> Dict:
        """
        Parameters
        ----------
            dataset_dict (dict): Metadata of one image, in Detectron2 Dataset format.

        Returns
        -------
        dict
            a format that builtin models in detectron2 accept
        """
        dataset_dict = copy.deepcopy(dataset_dict)
        is_triplet = 'anchor' in dataset_dict.keys()
        if is_triplet:
            for k, img in dataset_dict.items():
                dataset_dict[k] = self._load_image(img)
        else:
            dataset_dict = self._load_image(dataset_dict)
        return dataset_dict
