import copy
import pathlib
import re
from typing import Callable, List, Union, Dict, Iterable

import numpy as np


__all__ = ["split_images_dirs", "split_images", "find_files", "generate_class_ids", "check_extensions"]


def find_files(input_dir: Union[str, pathlib.Path], extensions: Union[str, List[str]] = None, recursive=False):
    """Find files with given extensions

    Parameters
    ----------
    input_dir : str or pathlib.Path
        Directory to be searched in.

    extensions : str or List[str], optional, default=['*.jpg', '*.jpeg']
        List of acceptable extensions.

    recursive : bool, optinal, default = False
        Whether subdirectories should be included.

    Returns
    ----------
    List[pathlib.Path]
        List of files

    Raises
    ----------
    ValueError
        If extension with bad format
    """
    if extensions is None:
        extensions = ['*.jpg', '*.jpeg']
    input_dir = pathlib.Path(input_dir)
    images = []
    extensions = check_extensions(extensions)
    for ext in extensions:
        images.extend([*input_dir.glob(f'**/{ext}' if recursive else ext)])
    return images


def generate_class_ids(images, extract_class_func=lambda p: pathlib.Path(p).parent.name, class_names=None, append_missing_classes=True):
    """Check and normalize the file type extensions.

    Parameters
    ----------
    images : Iterable[str, pathlib.Path]
        Iterable containing list of images.

    extract_class_func : callable, optional
        Callable accepting the entries of `images` and returning the class label as str.

    class_names : list[str], optional, default=[]
        List of class names.

    append_missing_classes : bool, optional, default=True
        Whether unexpected class labels should be added.
        TODO: would propose to remove, either you provide explicit list to be strict or you provide empty list and want to be non-strict

    Returns
    ----------
    List[int]
        List of class_ids same length as images

    List[str]
        Full list of used class_names.

    Raises
    ----------
    ValueError
        If class label is not in `class_names` and `append_missing_classes=False`.
    """
    if class_names is None:
        class_names = []
    class_ids = []
    class_names = [*class_names]
    for i in images:
        label = extract_class_func(i)
        try:
            class_id = class_names.index(label)
        except ValueError:
            if append_missing_classes:
                class_id = len(class_names)
                class_names.append(label)
            else:
                ValueError(f'Class `{label}` not in `class_names` provide complete list '
                            'of class names or set `append_missing_classes` to true.')
        class_ids.append(class_id)
    return class_ids, class_names


def check_extensions(extensions: Iterable[str]):
    """Check and normalize the file type extensions.

    Parameters
    ----------
    extensions : Iterable[str]
        List of extensions. Acceptables formats are '.{file_type}' and '*.{file_type}

    Returns
    ----------
    List[str]
        List of file extensions [*.{file_type}]

    Raises
    ----------
    ValueError
        If extension is not in the expected format.
    """
    r = re.compile('^.*\*\.([a-zA-Z0-9.]*)$')
    checked_extensions = []
    if isinstance(extensions, str):
        extensions = [extensions]
    for ext in extensions:
        if not r.match(ext):
            ext_new = f'*{ext}'
            if r.match(ext_new):
                checked_extensions.append(ext_new)
            else:
                raise ValueError('The extension `{ext}` is not valid. Please add'
                                 ' extension starting with a * and only file types.')
        else:
            checked_extensions.append(ext)
    return checked_extensions


def split_images_dirs(input_dirs: Iterable[Union[str, pathlib.Path]],
                      output_dir: Union[str, pathlib.Path, None],
                      splits: Dict[str, Union[float]],
                      extensions: Union[str, List[str]] = None,
                      remove_ext: bool = False,
                      remove_dir: bool = False,
                      rnd_gen: Union[int, None] = None):
    """Collect and split files with specific extensions for multiple folders.

    Each folder is split individually and the splits are merge at the end. This function can be used
    to do stratified sampling for image classification cases if images of the same class are grouped
    in subfolders.
    Parameters
    ----------
    input_dirs : Iterable[str, pathlib.Path]
        List of directory used to search for files. In this directory a glob for each given extensions is
        executed to select all files.
    output_dir : str or pathlib.Path or None
        Directory in which `<split>.txt` files will be created to with list of files per split.
        If None no files will be created.
    splits: dict(str, float)
        Dict naming the splits and providing split sizes. If sum of sizes <= 1. the numbers are directly used
        as the ratio. If sum of sizes < 1 a single split can have `size=None`. This splits will consists of
        all remaining files.
        If sum of sizes > 1 the ratio of images for each split is `size/sum(sizes)`.
    extensions: str or Iterable[str], optional, default = ['*.jpg', '*.jpeg']
        All file extensions used in the globs.
    remove_ext: bool, optional, default=False
        Remove file extensions from the file lists. This can be useful for spliting files for object detection
        datasets in pascal voc style (.jpg + .xml).
    remove_dir: bool, optional, default=False
        Remove all directories from the file paths.
    rnd_gen: int, np.random.Generator or None, optional, default=None
        Random seed or np.random.Generator for the splits. If None no specific seed will be used. This results
        in unreproducible splits!

    Returns
    ----------
    dict(str, List[pathlib.Path]) or dict(pathlib.Path, List[pathlib.Path])
        Dict containing a list of files for each split.
        If `output_dir` is None the keys of the dict are the keys from `splits`.
        If `output_dir` is not None the key of the dict are: `<output_dir>/<split_name>.txt``
        the name of the txt-files containing the names of the files for each split.


    Examples
    --------
    Split data for image classification. Images for every class are in separate
    subfolders: data/class1, data/class2, ...

    >>> dataset_path = pathlib.Path('data')
    >>> split_images_dirs(glob.glob(DATASET_PATH + '/*/'),
                          None,
                          {'train': 0.7, 'val': 0.15, 'test': 0.15},
                          remove_dir=False,
                          remove_ext=False)
    {'train': ['data/class1/img1.jpg', 'data/class2/img231.jpg', ...],
     'val': ['data/class1/img7.jpg', 'data/class2/img21.jpg', ...],
     'test': ['data/class1/img9.jpg', 'data/class2/img3.jpg', ...]}
    """
    if extensions is None:
        extensions = ['*.jpg', '*.jpeg']
    splits_images = {}
    for input_dir in input_dirs:
        splits_i = split_images(input_dir=input_dir,
                                output_dir=None,
                                splits=splits,
                                extensions=extensions,
                                remove_ext=remove_ext,
                                remove_dir=remove_dir,
                                rnd_gen=rnd_gen)
        for split, images_split_i in splits_i.items():
            images_split = splits_images.setdefault(split, [])
            images_split.extend(images_split_i)
    if output_dir:
        output_dir = pathlib.Path(output_dir).resolve()
        output_files = {}
        for name, images_split in splits_images.items():
            output_i = output_dir / f'{name}.txt'
            with output_i.open('w') as stream:
                stream.write('\n'.join(str(i) for i in images_split))
            output_files[output_i] = images_split
        return output_files
    else:
        return splits_images


def split_images(input_dir: Union[str, pathlib.Path],
                 output_dir: Union[str, pathlib.Path, None],
                 splits: Dict[str, Union[float]],
                 extensions: Union[str, Iterable[str]] = None,
                 remove_ext: bool = False,
                 remove_dir: bool = False,
                 extract_class_func: Union[None, Callable] = None,
                 rnd_gen: Union[int, None, 'np.random.Generator'] = None):
    """Collect and split files with specific extensions.

    This function can be used to split files from a directory into arbitrary splits.

    Parameters
    ----------
    input_dir : str or pathlib.Path
        Directory used to search for files. In this directory a glob for each given extensions is
        executed to select all files.
    output_dir : str or pathlib.Path or None
        Directory in which `<split>.txt` files will be created to with list of files per split.
        If None no files will be created.
    splits: dict(str, float)
        Dict naming the splits and providing split sizes. If sum of sizes <= 1. the numbers are directly used
        as the ratio. If sum of sizes < 1 a single split can have `size=None`. This splits will consists of
        all remaining files.
        If sum of sizes > 1 the ratio of images for each split is `size/sum(sizes)`.
    extensions: str or Iterable[str], optional, default = ['*.jpg', '*.jpeg']
        All file extensions used in the globs.
    remove_ext: bool, optional, default=False
        Remove file extensions from the file lists. This can be useful for spliting files for object detection
        datasets in pascal voc style (.jpg + .xml).
    remove_dir: bool, optional, default=False
        Remove all directories from the file paths.
    extract_class_func: None or callable
        Callable returning the class label. The callable for each file with the path as an argument.
        If a callable is provided the split will be done for each class individually to achieve a
        stratified sampling.
    rnd_gen: int, np.random.Generator or None, optional, default=None
        Random seed or np.random.Generator for the splits. If None no specific seed will be used. This results
        in unreproducible splits!

    Returns
    ----------
    dict(str, List[pathlib.Path]) or dict(pathlib.Path, List[pathlib.Path])
        Dict containing a list of files for each split.
        If `output_dir` is None the keys of the dict are the keys from `splits`.
        If `output_dir` is not None the key of the dict are: `<output_dir>/<split_name>.txt``
        the name of the txt-files containing the names of the files for each split.

    Examples
    --------
    Split data for image classification. Images for every class are in separate
    subfolders: data/class1, data/class2, ...
    To include files from subfolders use extensions like '**/*.jpg' instead of '*.jpg'.

    >>> dataset_path = pathlib.Path('data')
    >>> split_images(dataset_path,
                     None,
                     extensions=['**/*.jpg', '**/*.jpeg'],
                     {'train': 0.7, 'val': 0.15, 'test': 0.15},
                     extract_class_func=lambda f: f.parent.name,
                     remove_dir=False,
                     remove_ext=False)
    {'train': ['data/class1/img1.jpg', 'data/class2/img231.jpg', ...],
     'val': ['data/class1/img7.jpg', 'data/class2/img21.jpg', ...],
     'test': ['data/class1/img9.jpg', 'data/class2/img3.jpg', ...]}
    """
    if extensions is None:
        extensions = ['*.jpg', '*.jpeg']
    splits = copy.deepcopy(splits)
    sum_sizes = sum(v for v in splits.values() if v)
    got_remaining_split = [v is None for v in splits.values()]
    if sum(got_remaining_split) == 0:
        got_remaining_split = False
    elif sum(got_remaining_split) == 1:
        got_remaining_split = True
    else:
        raise ValueError('Only one split can has size=None!')
    if got_remaining_split and sum_sizes > 1:
        raise ValueError('Sum of `size` for all splits > 1, '
                         'therefore it is treated as relative size definitions. '
                         'With relative sizes size=None is not allowed')
    start = 0.
    if sum_sizes > 1:
        quotient = sum_sizes
    else:
        quotient = 1.
    split_name_remaining = None
    for n, v in splits.items():
        if v is not None:
            len_split = v / quotient
            splits[n] = (start, start+len_split)
            start += len_split
        else:
            split_name_remaining = n
    if split_name_remaining:
       splits[split_name_remaining] = (start, 1.0)
    if not isinstance(rnd_gen, np.random.Generator):
        rnd_gen = np.random.default_rng(rnd_gen)
    input_dir = pathlib.Path(input_dir)
    if output_dir:
        output_dir = pathlib.Path(output_dir).resolve()
    images = find_files(input_dir, extensions=extensions)
    if callable(extract_class_func):
        classes = np.array([extract_class_func(img) for img in images])
        images = np.array(images)
        split_files = {}
        for c in np.unique(classes):
            images_c = np.where(classes == c)[0]
            rnd_gen.shuffle(images_c)
            eps = 1/(len(images_c) + 1)
            split_files_i = {}
            prev_limit = None
            for n, (s, e) in splits.items():
                split_files_i[n] = slice(prev_limit, int(np.round(e*len(images_c))) if e + eps < 1 else None)
                prev_limit = split_files_i[n].stop
            for n, s in split_files_i.items():
                images_s = split_files.setdefault(n, [])
                indices = np.sort(images_c[s])
                images_s.extend([images[idx] for idx in indices])
    else:
        rnd_gen.shuffle(images)
        eps = 1/(len(images) + 1)
        split_files = {}
        prev_limit = None
        for n, (s, e) in splits.items():
            split_files[n] = slice(prev_limit, int(np.round(e*len(images))) if e + eps < 1 else None)
            prev_limit = split_files[n].stop
        split_files = {n: images[s] for n, s in split_files.items()}
    output_files = {}
    for n, imgs in split_files.items():
        if remove_ext:
            imgs = [i.with_suffix('') for i in imgs]
        if remove_dir:
            imgs = [i.name for i in imgs]
        if output_dir:
            output_i = output_dir / f'{n}.txt'
            with output_i.open('w') as stream:
                stream.write('\n'.join(str(i) for i in imgs))
        else:
            output_i = n
        output_files[output_i] = imgs
    return output_files
