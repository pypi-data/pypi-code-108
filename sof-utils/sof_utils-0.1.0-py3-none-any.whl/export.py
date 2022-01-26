from typing import Tuple, Union, List, Set, Dict

import tensorflow as tf


def export_images(dataset: tf.data.Dataset,
                  target_path: str,
                  format: str = 'png',
                  downsample_to: Tuple[Union[int, None], Union[int, None]] = (1, None),
                  split_lr: bool = False,
                  flip_lr: bool = False,
                  visits: List[int] = [],
                  included_ids: Set[int] = set(),
                  excluded_ids: Set[int] = set(),
                  num_groups: Union[None, int] = None,
                  max_group_size: Union[None, int] = None,
                  randomized_groups: bool = False,
                  zip: bool = False):
    """ Export the given dataset to png images
    :param dataset: Dataset to export
    :param target_path: path where the images will be exported to.
    :param format: image format to use: png (default) or jpeg
    :param downsample_to: target (width, height) of exported image (defaults to (None, None)).
        If one entry is None, it is inferred from the other one by keeping the aspect ratio.
        If booth entries are None, the original size is kept.
    :split_lr: if true (default is false), splits the image vertically into a left and a right part, i.e. two instead of
        one image files are written per example.
    :flip_lr: if true (default is false), flips the right part of the image vertically. Does nothing if
        'split_lr == False'.
    :visits: list of visits to include in the export. If visits is empty all visits are exported.
    :included_ids: set of SOF IDs to include. If empty, all IDs are exported.
    :excluded_ids: set of SOF IDs that should be excluded from the export.
    :num_groups: number of groups the exported files should be split into. If both, `max_group_size` and `num_groups` are `None` no grouping will be performed.
    :max_group_size: maximum number of files per group. If both, `max_group_size` and `num_groups` are `None` no grouping will be performed.
    :randomized_groups: If true, file to group assignments will be random.
    :zip: If true, write files into a zip file instead of a directory. If grouping is enabled, create one zip file per group.
    """
    from pathlib import Path
    from tqdm import tqdm
    from math import ceil
    from zipfile import ZipFile

    groups = {}
    group_sizes = []
    if num_groups or max_group_size:
        groups, group_sizes = _group_items(dataset,
                                           num_groups=num_groups,
                                           max_group_size=max_group_size,
                                           randomized=randomized_groups,
                                           split_lr=split_lr,
                                           visits=visits,
                                           included_ids=included_ids,
                                           excluded_ids=excluded_ids)

    target_path = Path(target_path)
    if zip and not groups:
        target_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        target_path.mkdir(parents=True, exist_ok=True)

    if format.lower() == 'png':
        encoding_func = lambda x: tf.io.encode_png(x)
    elif format.lower() == 'jpeg':
        encoding_func = lambda x: tf.io.encode_jpeg(x)
    else:
        raise ValueError(f"Unsupported image format: {format}. supported formats are: png, jpeg")

    image_shape = next(iter(dataset))['image'].shape

    # Compute missing downsample_to entry, if any
    if not downsample_to[0] and not downsample_to[1]:
        downsample_to = (image_shape[1], image_shape[0])
    elif not downsample_to[0]:
        ratio = float(downsample_to[1]) / float(image_shape[0])
        downsample_to = (int(ceil(ratio * float(image_shape[0]))), downsample_to[1])
    elif not downsample_to[1]:
        ratio = float(downsample_to[0]) / float(image_shape[1])
        downsample_to = (downsample_to[0], int(ceil(ratio * float(image_shape[1]))))

    def group_prefix(sof_id, visit, lr):
        if not groups:
            return ''
        group = groups[(sof_id, visit, lr)]
        group_size = group_sizes[group]

        return f"G{group:04d}-N{group_size}-"

    if zip and not groups:
        zip_file = ZipFile(target_path, 'w')
    else:
        zip_files = [ZipFile(target_path.joinpath(f"{group:04d}-N{group_sizes[group]}.zip"), 'w') for group in
                     range(len(group_sizes))]

    def write_file(filename, bytes, group=None):
        if not zip:
            with open(str(filename), 'wb') as f:
                f.write(bytes)
        if not groups:
            zip_file.writestr(filename.name, bytes)
        else:
            zf = zip_files[group]
            zf.writestr(filename.name, bytes)

    for example in tqdm(dataset):
        sof_id = example['id'].numpy()
        visit = example['visit'].numpy()
        if visits and visit not in visits:
            continue
        if included_ids and sof_id not in included_ids or sof_id in excluded_ids:
            continue

        image = tf.cast(tf.image.resize(example['image'], (downsample_to[1], downsample_to[0])), dtype=tf.uint8)

        if split_lr:
            left_img, right_img = split_image_lr(image, flip_lr)
            postfix = f"-{left_img.shape[1]}x{left_img.shape[0]}"
            # write left image, ie.e right hip
            key = (sof_id, visit, 'R')
            group = groups[key] if groups else None
            pref = group_prefix(*key)
            filename = target_path.joinpath(f'{pref}{sof_id}V{visit}R{postfix}.png')
            encoded_image = encoding_func(left_img)
            write_file(filename, encoded_image.numpy(), group)

            # write right image, i.e. left hip
            key = (sof_id, visit, 'L')
            group = groups[key] if groups else None
            pref = group_prefix(*key)
            filename = target_path.joinpath(f'{pref}{sof_id}V{visit}L{postfix}.png')
            encoded_image = encoding_func(right_img)
            write_file(filename, encoded_image.numpy(), group)
        else:
            postfix = f"-{image.shape[1]}x{image.shape[0]}"
            key = (sof_id, visit, '')
            group = groups[key] if groups else None
            pref = group_prefix(*key)
            filename = target_path.joinpath(f'{pref}{sof_id}V{visit}{postfix}.png')
            encoded_image = encoding_func(image)
            write_file(filename, encoded_image.numpy(), group)


def split_image_lr(image: tf.Tensor, flip_lr: bool = False) -> Tuple[tf.Tensor, tf.Tensor]:
    """ Split image vertically into a left and a right image.
    If the image does not have an even width, it is padded by one column at the right.
    :param image: source image to split
    :param flip_lr: If true, flips the right image vertically.
    :return: (left_image, right_image) tuple containing the left and the right half of the image.
    """
    padding = image.shape[1] % 2
    padded_image = tf.image.pad_to_bounding_box(image, 0, 0, image.shape[0], image.shape[1] + padding)

    image_half_width = tf.cast(tf.math.ceil(padded_image.shape[1] / 2), tf.int64)

    left_image = padded_image[..., 0:image_half_width, :]
    right_image = padded_image[..., image_half_width:, :]

    if flip_lr:
        right_image = tf.image.flip_left_right(right_image)

    return left_image, right_image


def _group_items(dataset: tf.data.Dataset,
                 max_group_size: Union[None, int],
                 num_groups: Union[None, int],
                 randomized: bool,
                 split_lr: bool,
                 visits: List[int],
                 included_ids: Set[int],
                 excluded_ids: Set[int]) -> Tuple[Dict[Tuple[int, int, str], int], List[int]]:
    """ Assigns each to be exported items to a group
    :param dataset: Dataset
    :param max_group_size: Maximum group size, only when num_groups is not given
    :param num_groups: Maximum number of groups, only when max_group_size is not given
    :param randomized: If true, assigment will be random
    :param split_lr: Tf example images should be split in left and right images
    :param visits: visits to include, if empty all visits are included
    :param included_ids: list of SOF IDs to include, if empty all IDs will be included
    :param excluded_ids: list of SOF IDs eo exclude
    :return: (group_dict, group_size) tuple containing a group dictionary and a list of group sizes..
    """
    from tqdm import tqdm
    from math import ceil
    from random import sample

    splits = ['L', 'R'] if split_lr else ['']

    # Generate item keys
    keys = []
    for example in tqdm(dataset, desc='Scanning dataset', unit='example'):
        sof_id = example['id'].numpy()
        visit = example['visit'].numpy()

        if included_ids and sof_id not in included_ids or sof_id in excluded_ids:
            continue
        if visits and visit not in visits:
            continue

        for split in splits:
            key = (sof_id, visit, split)
            keys.append(key)

    if (not num_groups and not max_group_size) or (num_groups and max_group_size):
        raise ValueError("Must set either num_groups or max_group_size")

    # group items
    num_items = len(keys)
    num_groups = num_groups if num_groups else int(ceil(num_items / max_group_size))
    max_group_size = max_group_size if max_group_size else int(ceil(num_items / num_groups))

    group_sizes = [0 for i in range(num_groups)]

    group_dict = {}
    for key in keys:
        available_groups = [i for i in range(num_groups) if group_sizes[i] < max_group_size]

        assert available_groups

        group = sample(available_groups, 1)[0] if randomized else available_groups[0]

        group_sizes[group] += 1
        group_dict[key] = group

    return group_dict, group_sizes
