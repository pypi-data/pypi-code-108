# -*- coding: utf-8 -*-
"""
Functions to register datasets for multiclass image classification.
Expects folder structure ./<classname>/[images]
"""
import glob
import pathlib
import logging
from typing import Callable, List, Tuple, Union, Dict, Iterable
from collections.abc import Iterable as IsIterable

import numpy as np
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.utils.file_io import PathManager

from .utils import split_images_dirs, check_extensions, find_files

__all__ = ["register",
           "split_and_register"]
logger = logging.getLogger(__name__)


def build_image_dict(filenames: Union[str, pathlib.Path, List[str], Tuple[str]],
                     class_names: Union[List[str], None] = None,
                     labels: Union[Iterable[str], None] = None,
                     raise_on_missing: bool = True,
                     extract_class_func: Union[Callable, None] = lambda f: pathlib.Path(f).parent.name,
                     append_missing_classes: bool = False):
    """Function that will be registered in the dataset catalog to return the
    lightweight version of the dataset.

    Normally this function is used only through `register` or `split_and_register`.
    Make sure to set remove_dir=False and remove_ext=False when generating the splits to feed into here.

    Parameters
    ----------
    filenames: str or pathlib.Path or Iterable[str, pathlib.Path]
        Names of the files for this dataset.
        If single str or pathlib.Path this has to be the path to a file containing the actual filenames.
        If iterable the iterable has to contain the actual filenames.
        So every filename needs to correspond to an image with the provided path on the filesystem.
        Behavior on missing files can be controlled through `raise_on_missing`.
    class_names: List[str] or None
        List of class names; either explicitly provided or determined from data if None.
    raise_on_missing: bool, optional, default=True
        Whether an exception should be raised when an image file or annoation file can not be found.
        If `False` missing files will be ignored.
    append_missing_classes: bool
        Completes missing classes when explicitly provided.
        This can be useful when you want to create consistent label mapping for multiple different datasets.

    Returns
    ----------
    List of dicts
       A list of dicts with a dict for each example.

    Raises
    ------
    FileNotFoundError
        If either an xml or image file can not be found.
    """
    if isinstance(filenames, IsIterable):
        fileids = np.array(filenames, dtype=str)
    else:
        filenames = pathlib.Path(filenames).resolve()
        with PathManager.open(filenames) as f:
            fileids = np.loadtxt(f, dtype=str)
    if class_names is None:
        class_names = []
    items = []
    for i, fileid in enumerate(fileids):
        path = pathlib.Path(fileid)
        if path.exists():
            if labels is None:
                label = extract_class_func(path)
            else:
                label = labels[i]
            try:
                class_id = class_names.index(label)
            except ValueError:
                if append_missing_classes:
                    class_id = len(class_names)
                    class_names.append(label)
                else:
                    raise ValueError(f'Got example of class `{label}`. Add to `class_names` or set append_missing_classes `True`.')
            item = {
                'file_name': str(path),
                'label': label,
                'class_id': class_id
            }
            items.append(item)
        elif raise_on_missing:
            raise FileNotFoundError(path)
    return items



def _parse_file_names_txt(input_):
    if isinstance(input_, str) or isinstance(input_, pathlib.Path):
        input_ = [input_]
    files_names = []
    for i in input_:
        with pathlib.Path(i).open() as stream:
            files_names.extend([l.strip() for l in stream.readlines()])
    return files_names


def register(name: str,
             base_dir: Union[str, pathlib.Path],
             filenames: Union[List[str], List[pathlib.Path]] = None,
             labels: List[str] = None,
             extensions: Union[str, Iterable[str]] = None,
             class_names: Union[List[str], None] = None,
             extract_class_func: Union[Callable, None] = lambda f: pathlib.Path(f).parent.name,
             append_missing_classes: bool=True,
             **additional_dataset_infos):
    """Register a dataset in the detectron2 DatasetCatalog and MetadataCatalog.
    After registration the dataset can be referenced in the cfg by simply providing
    the `name`.

    Parameters
    ----------
    name: str
        Name under which the dataset will be registered. Has to be unique.
    base_dir: str or pathlib.Path
        Path to the directory containing the dataset. Expects to contain subfolders corresponding to each class and
        each of those subfolders has to contain the relevant images.
    filenames: List[str] or List[pathlib.Path], optional
        If not provided will parse base_dir for image files and use all of them.
        If provided will simply use the provided filenames instead.
    extensions: str or Iterable[str], optional, default=['.jpg', '.jpeg']
        Valid extensions for images. Only used when `filename_with_extension=False`.
        See `img_extensions` from `load_voc_like_instances` for more details.
    class_names: List[str] or None
        List of class names, if provided, otherwise determined automatically from data.
    extract_class_func: Callable or None, optional, default=lambda f: pathlib.Path(f).parent.name
        Function used to label the the image. The callable is called with the path of the image
        and is expected to return a str. Default is to use the name of the parent folder as
        the label.
    append_missing_classes: bool
        Completes missing classes when explicitly provided.
        This can be useful when you want to create consistent label mapping for multiple different datasets.
    **additional_dataset_infos: str
        Every additional keyword arguements are considered to be metadata and
        will be registered in the metadata catalog. For all datasets the
        names of the classes, image directory and xml directory are stored.

    Returns
    ----------
    List of str
        List of images in the dataset
    List of str
        Used class names.

    Examples
    --------
    Split data for object detection and register train dataset.

    >>> dataset_path = pathlib.Path('pets')
    >>> register('my_dataset',
                 base_dir=dataset_path,
                 extensions=['.jpg'])
    ('my_dataset_train', ['cat', 'dog', ...])
    """
    if labels is None and extract_class_func is None:
        raise ValueError('Either `labels` or `extract_class_func` has to be provided.' )
    if filenames is None: # Only base_dir specified, in this case the base_dir is scanned for images
        if extensions is None:
            extensions = ['*.jpg', '*.jpeg']
        extensions = check_extensions(extensions)
        filenames = find_files(base_dir, extensions, recursive=True)
        labels = None
    else:
        # Try to figure out what is provided as filenames.
        # Possiblities are:
        #  - paths of images
        #  - 1 or multiple txt-files contianing image paths
        if isinstance(filenames, str): # Single file -> has to be a file containing image paths
            list_files_as_input = True
        elif isinstance(filenames, IsIterable):
            list_files_as_input = False
            filenames = [*filenames]
            if pathlib.Path(filenames[0]).suffix == '.txt':
                list_files_as_input = True
        if list_files_as_input:
            filenames = _parse_file_names_txt(filenames)
            labels = None
        else:
            # Since the paths of the images are directly provided to the function
            # nothing has to be done for the image paths
            if labels is not None:
                labels = [*labels]
                if not len(labels) != len(filenames):
                    raise ValueError('`labels` and `filenames` have to be of the same length.')

    if class_names is None or len(class_names) == 0:
        if labels is None:
            labels = [extract_class_func(p) for p in filenames]
            class_names = sorted(set(labels))
        else:
            class_names = sorted(set(labels))
    elif append_missing_classes:
        if labels is None:
            labels = [extract_class_func(p) for p in filenames]
        new_class_names = set(labels).difference(set(class_names))
        class_names.extend([*new_class_names])
    DatasetCatalog.register(name, lambda: build_image_dict(filenames, class_names=class_names, labels=labels, extract_class_func=extract_class_func, append_missing_classes=False))
    MetadataCatalog.get(name).set(classes=list(class_names),
                                  base_dir=str(base_dir),
                                  **additional_dataset_infos)
    return filenames, class_names


def split_and_register(basename: Union[str, None],
                       base_dir: Union[str, pathlib.Path],
                       splits: Dict[str, float],
                       rnd_gen: Union[int, None] = 1337,
                       extensions: Union[str, List[str]] = None,
                       class_names: Union[List[str], None] = None,
                       extract_class_func: Union[Callable, None] = lambda f: pathlib.Path(f).parent.name,
                       **additional_dataset_infos):
    """Register a dataset in the detectron2 DatasetCatalog and MetadataCatalog.
    After registration the dataset can be referenced in the cfg by simply providing
    the `name`.

    Parameters
    ----------
    basename: str
        All datasets will be registered as `<basename>_<split>`
    base_dir: str or pathlib.Path
        Path to the directory containing the dataset. Expects to contain subfolders corresponding to each class and
        each of those subfolders has to contain the relevant images.
    splits: dict(str, float)
        Dictionary with the names of the splits and their size.
        Check `sap_computer_visison.datasets.utils.split` for more details.
    rnd_gen: int, np.random.Generator or None, optional, default=None
        Random seed or np.random.Generator for the splits. If None no specific seed will be used. This results
        in unreproducible splits!
    extensions: str or Iterable[str], optional, default=['.jpg', '.jpeg']
        Valid extensions for images. Only used when `filename_with_extension=False`.
        See `load_voc_like_instances` for more details.
    class_names: List[str] or None
        List of class names, if provided, otherwise determined automatically from data.
    **additional_dataset_infos: str
        Every additional keyword arguements are considered to be metadata for all splits and
        will be registered in the metadata catalog for each split. For all datasets the
        names of the classes, image directory, xml directory and name of the
        split are stored.

    Returns
    ----------
    dict(str, List[str])
       Name and list of filenames for each dataset
    List of str
        Used class names.

    Examples
    --------
    Split data for object detection and register train dataset.

    >>> dataset_path = pathlib.Path('data')
    >>> split_and_register('my_dataset'
                           base_dir=dataset_path,
                           splits={'train': 0.7, 'val': 0.15, 'test': 0.15})
    >>>
    ({'my_dataset_train': ['img1', 'img3', ...],
      'my_dataset_test': ['img2', 'img6', ...],
      'my_dataset_val': ['img4', 'img9', ...]}, ['cat', 'dog', ...])
    """
    if extensions is None:
        extensions = ['*.jpg', '*.jpeg']

    base_dir = pathlib.Path(base_dir)
    splits = split_images_dirs(glob.glob(str(base_dir / '*')),
                               output_dir=None,
                               extensions=extensions,
                               splits=splits,
                               remove_dir=False,
                               remove_ext=False,
                               rnd_gen=rnd_gen)
    registered_datasets = {}
    if class_names is None:
        class_names = sorted(set([pathlib.Path(p).parent.name for split in splits.values() for p in split]))
    for split, fileids in splits.items():
        name = f'{basename}_{split}' if basename and basename != '' else split
        register(
            name=name,
            base_dir=base_dir,
            filenames=fileids,
            split=split,
            extract_class_func=extract_class_func,
            class_names=class_names,
            additional_dataset_infos=additional_dataset_infos)
        class_names_class = set([pathlib.Path(p).parent.name for p in fileids])
        if len(set(class_names).difference(class_names_class)) > 0:
             logger.warning(f"Split `{name}` is missing classes: {', '.join(set(class_names).difference(class_names_class))}")
        registered_datasets[name] = fileids
    return registered_datasets, class_names
