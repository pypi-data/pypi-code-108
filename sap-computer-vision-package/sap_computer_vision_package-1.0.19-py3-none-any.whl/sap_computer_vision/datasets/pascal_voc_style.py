# -*- coding: utf-8 -*-
"""Functions to register object detection datasets, that are in a pascal voc style
"""
import pathlib
import xml.etree.ElementTree as ET
from typing import List, Tuple, Union, Dict, Iterable, Any
from collections.abc import Iterable as IsIterable

import numpy as np
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.structures import BoxMode
from detectron2.utils.file_io import PathManager


from .utils import split_images, find_files, check_extensions


__all__ = ["register",
           "split_and_register",
           "get_classnames_from_annotation_files",
           "get_classnames_from_filenames_files"]


def find_folders(base_path: Union[str, pathlib.Path],
                 images_names: Union[None, Iterable[str]]=None,
                 annotations_names: Union[None, Iterable[str]]=None) -> Tuple[pathlib.Path, pathlib.Path]:
    """Small helper functions to find subfolders for images and
    annoation in Pascal VOC datasets.

    Parameters
    ----------
    base_path: str or pathlib.Path
        Folder to search in
    images_names: Iterable of str or None, optional, default=None
        List of potential folder names containing the images.
        If None the default list: ['Images', 'images', 'jpegs', 'jpgs']
         is being used.
    images_names: Iterable of str or None, optional, default=None
        List of potential folder names containing the annotation xmls.
        If None the default list: ['Annotations', 'annotations', 'annotation',
        'Annotation', 'xml', 'xmls'] is being used.

    Returns
    -------
    pathlib.Path
        Image folder
    pathlib.Path
        Annotation folder
    """

    if images_names is None:
        images_names = ['Images', 'images', 'jpegs', 'jpgs']
    if annotations_names is None:
        annotations_names = ['Annotations', 'annotations', 'annotation', 'Annotation', 'xml', 'xmls']
    if len(set(images_names).intersection(set(annotations_names))) != 0:
        raise ValueError(f'Names allowed for the image and annotation folder are overlapping! {set(images_names).intersection(set(annotations_names))}')
    base_path = pathlib.Path(base_path)
    for p in images_names:
        image_folder = base_path / p
        if image_folder.exists() and image_folder.is_dir():
            break
    else:
        raise ValueError('No image folder found!')
    for p in annotations_names:
        annotation_folder = base_path / p
        if annotation_folder.exists() and annotation_folder.is_dir():
            break
    else:
        raise ValueError('No annotation folder found!')
    return image_folder, annotation_folder


def get_annotations_from_xml(annotation_file: Union[str, pathlib.Path, 'ET.ElementTree'],
                             class_names: Union[List[str], None] = None,
                             box_mode: 'BoxMode'=BoxMode.XYXY_ABS) -> Dict[str, Any]:
    """Parse annotations from xml in Pascal VOC format.

    Parameters
    ----------
    annotation_file: str/pathlib.Path or ET.ElementTree
        Path of the annotation file or already parsed ET.ElementTree
    class_names: List[str] or None
        List of class names; either explicitly provided or determined from data if None.
    box_mode: detectron2.structures.BoxMode
        Format of the boxes in the annotations.

    Returns
    -------
    dict
        Dict with containing the annotations
    """
    if not isinstance(annotation_file, ET.ElementTree):
        annotation_file = pathlib.Path(annotation_file)
        with annotation_file.open() as f:
            tree = ET.parse(f)
    else:
        tree = annotation_file
    r = {
        "height": int(tree.findall("./size/height")[0].text),
        "width": int(tree.findall("./size/width")[0].text),
    }
    instances = []
    for obj in tree.findall("object"):
        cls = obj.find("name").text
        bbox = obj.find("bndbox")
        if box_mode == BoxMode.XYXY_ABS:
            bbox = [float(bbox.find(x).text) for x in ["xmin", "ymin", "xmax", "ymax"]]
        else:
            NotImplementedError('Currently only `BoxMode.XYXY_ABS` implemented!')
        bbox[0] -= 1.0
        bbox[1] -= 1.0
        try:
            difficult = bool(obj.find("difficult").text)
        except:
            difficult = False
        try:
            truncated = bool(obj.find("truncated").text)
        except:
            truncated = False
        try:
            pose = obj.find("pose").text
        except:
            pose = "Unspecified"

        instances.append({"category_id": class_names.index(cls) if class_names else cls,
                          "bbox": bbox,
                          "bbox_mode": box_mode,
                          "difficult": difficult,
                          "truncated": truncated,
                          "pose": pose})
    r["annotations"] = instances
    return r


def load_voc_like_instances(img_dir: Union[str, pathlib.Path],
                            xml_dir: Union[str, pathlib.Path],
                            filenames: Union[str, pathlib.Path, List[str], Tuple[str]],
                            class_names: Union[List[str], Tuple[str, ...]],
                            img_extensions: Union[str, List[str]]='.jpg',
                            box_mode: Union[str, BoxMode]=BoxMode.XYXY_ABS,
                            filename_with_extension: bool=False,
                            raise_on_missing: bool=True) -> Dict[str, Any]:
    """Function that will be registered in the dataset catalog to return the
    lightweight version of the dataset.

    Normally this function is used only through `register` or `split_and_register`.

    Parameters
    ----------
    img_dir: str or pathlib.Path
        Path to the directory containing the images.
    xml_dir: str or pathlib.Path
        Path to the directory containing the annotation xmls.
    filenames: str or pathlib.Path or Iterable[str, pathlib.Path]
        Names of the files for this dataset.
        If single str or pathlib.Path this has to be the path to a file containing the actual filenames.
        If iterable the iterable has to contain the actual filenames. During creating of the dicts
        the functions is looking for an image with one of the extensions from `img_extensions`.
        So every filename needs to match an image with path `<img_dir>/<filename>.<extension>` and
        an annotation files with path `<xml_dir>/<filename>.xml`. If the filesnames are with the
        image file extension set `filename_with_extension=True` `img_extensions` will be ignored.
        Behavior on missing files can be controlled through `raise_on_missing`.
    class_names: List[str] or Tuple[str], optional, default=None
        List of all names of the classes in the training. The order of the class names is important
        since internally class labels are indices of the classes in this list.
    img_extensions: str or Iterable[str], optional, default='.jpg'
        Valid extensions for images. Only used when `filename_with_extension=False`.
        See `img_extensions` from `load_voc_like_instances` for more details.
    box_mode: detectron2.structures.BoxMode, optional, default=XYXY_ABS
        Format of the boxes in the annotation files.
        Default is (x1, y1, x2, y2) as absolute pixels
        Check detectron2 documentation for formats available.
    filename_with_extension: bool, optional, default=False
        Whether filenames are with or without img extension.
    raise_on_missing: bool, optional, default=True
        Whether an exception should be raised when either image file or annoation file
        can not be found. If `False`missing files will be ignored.

    Returns
    ----------
    List of dicts
       A list of dicts with a dict for each example.

    Raises
    ------
    FileNotFoundError
        If either an xml or image file can not be found.
    """
    img_dir = pathlib.Path(img_dir).resolve()
    annotation_dirname = pathlib.Path(xml_dir).resolve()
    if isinstance(filenames, IsIterable) and not isinstance(filenames, str):
        fileids = np.array(filenames, dtype=str)
    else:
        filenames = pathlib.Path(filenames).resolve()
        with PathManager.open(filenames) as f:
            fileids = np.loadtxt(f, dtype=str)
    # Needs to read many small annotation files. Makes sense at local
    dicts = []
    if isinstance(box_mode, str):
        box_mode = BoxMode[box_mode]

    if isinstance(img_extensions, str):
        img_extensions = [img_extensions]



    def add_img_extension(path):
        if filename_with_extension:
            return path
        elif len(img_extensions) > 1:
            for ext in img_extensions:
                ext = ext.replace('*', '')
                img_path = path.parent / (path.name + ext)
                if img_path.exists():
                    return img_path
            if raise_on_missing:
                raise FileNotFoundError(f'Image `{path}` does not exist for any of the extensions {img_extensions}')
            else:
                return None
        else:
            img_path = path.with_suffix(img_extensions[0])
            if img_path.exists():
                return img_path
            else:
                if raise_on_missing:
                    raise FileNotFoundError(f'Image `{img_path}` does not exist!')
                else:
                    return None

    add_img_extension.with_extension = None


    for fileid in fileids:
        jpeg_file = add_img_extension(img_dir / fileid)
        if not jpeg_file:
            continue
        anno_file = annotation_dirname / jpeg_file.with_suffix('.xml').name
        annotation = get_annotations_from_xml(annotation_file=anno_file, class_names=class_names, box_mode=box_mode)
        annotation["file_name"] = str(jpeg_file)
        annotation["image_id"] = fileid
        dicts.append(annotation)
    return dicts


def split_and_register(basename: Union[str, None],
                       img_dir: Union[str, pathlib.Path],
                       xml_dir: Union[str, pathlib.Path],
                       splits: Dict[str, float],
                       class_names: Union[None, List[str], Tuple[str]]=None,
                       rnd_gen: Union[int, None]=1337,
                       extensions: Union[str, List[str]]=None,
                       box_mode: BoxMode=BoxMode.XYXY_ABS,
                       **additional_dataset_infos):
    """Register a dataset in the detectron2 DatasetCatalog and MetadataCatalog.
    After registration the dataset can be referenced in the cfg by simply providing
    the `name`.

    Parameters
    ----------
    basename: str
        All datasets will be registered as `<basename>_<split>`
    img_dir: str or pathlib.Path
        Path to the directory containing the images.
    xml_dir: str or pathlib.Path
        Path to the directory containing the annotation xmls.
    splits: dict(str, float)
        Dictionary with the names of the splits and their size.
        Check `sap_computer_visison.datasets.utils.split` for more details.
    class_names: None or List[str] or Tuple[str], optional, default=None
        List of all names of the classes in the training. The order of the class names is important
        since internally class labels are indices of the classes in this list.
        If `None` class names will be extracted from the annotation files of the dataset. Beware
        in some cases especially for smaller test datasets not all classes might be part of a
        dataset and this will result in a mixup of labels.
    rnd_gen: int, np.random.Generator or None, optional, default=None
        Random seed or np.random.Generator for the splits. If None no specific seed will be used. This results
        in unreproducible splits!
    extensions: str or Iterable[str], optional, default=['.jpg', '.jpeg']
        Valid extensions for images. Only used when `filename_with_extension=False`.
        See `load_voc_like_instances` for more details.
    box_mode: detectron2.structures.BoxMode, optional, default=XYXY_ABS
        Format of the boxes in the annotation files.
        Default is (x1, y1, x2, y2) as absolute pixels
        Check detectron2 documentation for formats available.
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
                           img_dir=dataset_path / 'images',
                           xml_dir=dataset_path / 'annotations',
                           splits={'train': 0.7, 'val': 0.15, 'test': 0.15})
    >>>
    ({'my_dataset_train': ['img1', 'img3', ...],
      'my_dataset_test': ['img2', 'img6', ...],
      'my_dataset_val': ['img4', 'img9', ...]}, ['cat', 'dog', ...])
    """
    if extensions is None:
        extensions = ['*.jpg', '*.jpeg']
    splits = split_images(img_dir,
                          output_dir=None,
                          extensions=extensions,
                          splits=splits,
                          remove_dir=True,
                          remove_ext=True,
                          rnd_gen=rnd_gen)
    if not class_names:
        class_names = get_classnames_from_annotation_files(
            xml_dir,
            [item for sublist in splits.values() for item in sublist])
    registered_datasets = {}

    def create_loading_f(filenames):
        def _f():
            return load_voc_like_instances(img_dir, xml_dir, filenames, class_names=class_names, img_extensions=extensions, box_mode=box_mode)

        return _f

    for split, fileids in splits.items():
        name = f'{basename}_{split}' if basename and basename != '' else split
        DatasetCatalog.register(name, create_loading_f(fileids))
        MetadataCatalog.get(name).set(thing_classes=list(class_names),
                                      img_dir=str(img_dir),
                                      xml_dir=str(xml_dir),
                                      split=split,
                                      box_mode=box_mode if isinstance(box_mode, BoxMode) else BoxMode[box_mode],
                                      **additional_dataset_infos)
        registered_datasets[name] = fileids
    return registered_datasets, class_names


def register(name:str,
             img_dir: Union[str, pathlib.Path],
             xml_dir: Union[str, pathlib.Path],
             filenames: Union[str, pathlib.Path, Iterable[Union[str, pathlib.Path]]]=None,
             class_names: Union[None, List[str], Tuple[str]]=None,
             extensions: Union[str, Iterable[str]]=None,
             box_mode: BoxMode=BoxMode.XYXY_ABS,
             filename_with_extension: bool=False,
             append_missing_classes: bool=True,
             **additional_dataset_infos):
    """Register a dataset in the detectron2 DatasetCatalog and MetadataCatalog.
    After registration the dataset can be referenced in the cfg by simply providing
    the `name`.

    Parameters
    ----------
    name: str
        Name under which the dataset will be registered. Has to be unique
    img_dir: str or pathlib.Path
        Path to the directory containing the images.
    xml_dir: str or pathlib.Path
        Path to the directory containing the annotation xmls.
    filenames: str or pathlib.Path or Iterable[str, pathlib.Path]
        Names of the files for this dataset.
        If single str or pathlib.Path this has to be the path to a file containing the actual filenames.
        If iterable the iterable has to contain the actual filenames.
        Every filename needs to match an image with path `<img_dir>/<filename>.<extension>` and
        an annotation files with path `<xml_dir>/<filename>.xml`.
        If the filesnames are with the the image file extension set `filename_with_extension=True`.
        Usally the filenames are only the stem.
    class_names: None or List[str] or Tuple[str], optional, default=None
        List of all names of the classes in the training. The order of the class names is important
        since internally class labels are indices of the classes in this list.
        If `None` class names will be extracted from the annotation files of the dataset. Beware
        in some cases especially for smaller test datasets not all classes might be part of a
        dataset and this will result in a mixup of labels.
    extensions: str or Iterable[str], optional, default=['.jpg', '.jpeg']
        Valid extensions for images. Only used when `filename_with_extension=False`.
        See `img_extensions` from `load_voc_like_instances` for more details.
    box_mode: detectron2.structures.BoxMode, optional, default=XYXY_ABS
        Format of the boxes in the annotation files.
        Default is (x1, y1, x2, y2) as absolute pixels
        Check detectron2 documentation for formats available.
    filename_with_extension: bool, optional, default=False
        Whether filenames are with or without img extension.
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

    >>> dataset_path = pathlib.Path('data')
    >>> splits = split_images(dataset_path / 'images',
                              dataset_path,
                              extensions=['*.jpg', '*.jpeg'],
                              {'train': 0.7, 'val': 0.15, 'test': 0.15},
                              remove_dir=True,
                              remove_ext=True)
    >>> register('my_dataset_train',
                 img_dir=dataset_path / 'images',
                 xml_dir=dataset_path / 'annotations',
                 filenames=splits['train'])
    ('my_dataset_train', ['cat', 'dog', ...])
    """
    if extensions is None:
        extensions = ['*.jpg', '*.jpeg']
    extensions = check_extensions(extensions)
    if filenames is None:
        filenames = [f.stem for f in find_files(img_dir, extensions, recursive=False)]
    if class_names is None or len(class_names) == 0 or append_missing_classes:
        class_names = class_names if class_names is not None else []
        if isinstance(filenames, str) or isinstance(filenames, pathlib.Path):
            class_names_set = get_classnames_from_filenames_files(xml_dir, filenames)
        elif isinstance(filenames, IsIterable):
            filenames = [*filenames]  # In case of filenames being an iterator/generator
            class_names_set = get_classnames_from_annotation_files(xml_dir, filenames)
        else:
            raise RuntimeError
        if append_missing_classes:
            new_class_names = set(class_names_set).difference(set(class_names))
            class_names.extend([*new_class_names])
        else:
            class_names = class_names_set


    DatasetCatalog.register(name, lambda: load_voc_like_instances(img_dir, xml_dir, filenames, class_names=class_names, img_extensions=extensions, box_mode=box_mode, filename_with_extension=filename_with_extension))
    MetadataCatalog.get(name).set(thing_classes=list(class_names),
                                  img_dir=str(img_dir),
                                  xml_dir=str(xml_dir),
                                  box_mode=box_mode if isinstance(box_mode, BoxMode) else BoxMode[box_mode],
                                  **additional_dataset_infos)
    return filenames, class_names


def get_classnames_from_filenames_files(xml_dir: Union[str, pathlib.Path],
                                        filenames: Union[str, pathlib.Path, Iterable[Union[str, pathlib.Path]]]):
    """Retrieve classes from annotation files provided via files.
    This functions can be useful if datasets are managed in list of files in files.

    Parameters
    ----------
    xml_dir: str or pathlib.Path
        Path to the directory containing xml annotation files
    filenames: str or pathlib.Path or Iterable[str, pathlib.Path]
        Path or iterable containing path of files containing names of annotation files.
        Annotion filenames with and without extensions are valid.
        If filesnames got an extension it will be overwritten with `.xml`.
        If not `.xml` will be appended.

    Returns
    ----------
    List of str
        Sorted list of class names retrieved from the annotation xmls. Beware internally the
        classes will be handles as ids coming from the order of the list.

    Examples
    --------
    Split data for object detection and retrieve classes from all sets.

    >>> dataset_path = pathlib.Path('data')
    >>> splits = split_images(dataset_path / 'images',
                              dataset_path,
                              extensions=['*.jpg', '*.jpeg'],
                              {'train': 0.7, 'val': 0.15, 'test': 0.15},
                              remove_dir=True,
                              remove_ext=True)
    >>> get_classnames_from_filenames_files(dataset_path / 'annotations',
                                            splits.values())
    ['cat', 'dog', ...]
    """
    xml_dir = pathlib.Path(xml_dir)
    if isinstance(filenames, pathlib.Path) or isinstance(filenames, str):
        filenames = [filenames]
    filenames = [str(pathlib.Path(f).resolve()) for f in filenames]
    class_names = []
    for f in filenames:
        with PathManager.open(str(pathlib.Path(f).resolve())) as f:
            fileids = np.loadtxt(f, dtype=str)
        class_names.extend(get_classnames_from_annotation_files(xml_dir, fileids))
    return sorted([*set(class_names)])


def get_classnames_from_annotation_files(xml_dir: Union[str, pathlib.Path],
                                         files: Iterable[Union[str, pathlib.Path]]):
    """Retrieve classes from annotation files provided as iterable of files.

    Parameters
    ----------
    xml_dir: str or pathlib.Path
        Path to the directory containing xml annotation files
    files: Iterable[str, pathlib.Path]
        List of annotation files. Filenames with and without extensions are valid.
        If filesnames got an extension it will be overwritten with `.xml`.
        If not `.xml` will be appended.

    Returns
    ----------
    List of str
        Sorted list of class names retrieved from the annotation xmls. Beware internally the
        classes will be handles as ids coming from the order of the list.

    Examples
    --------
    Split data for object detection and retrieve classes from all sets.

    >>> dataset_path = pathlib.Path('data')
    >>> splits = split_images(dataset_path / 'images',
                              None,
                              extensions=['*.jpg', '*.jpeg'],
                              {'train': 0.7, 'val': 0.15, 'test': 0.15},
                              remove_dir=True,
                              remove_ext=True)
    >>> get_classnames_from_annotation_files(dataset_path / 'annotations',
                                             [s for s in split_i for split_i in splits])
    ['cat', 'dog', ...]
    """
    class_names = set()
    for fileid in files:
        anno_file = xml_dir / pathlib.Path(fileid).with_suffix('.xml').name
        if not anno_file.exists():
            anno_file = xml_dir / (pathlib.Path(fileid).name + '.xml')
        with anno_file.open() as f:
            tree = ET.parse(f)
        for obj in tree.findall("object"):
            cls = obj.find("name").text
            class_names.add(cls)
    return sorted([*class_names])
