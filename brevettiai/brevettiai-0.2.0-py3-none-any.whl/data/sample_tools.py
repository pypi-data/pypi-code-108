import logging
import concurrent.futures

import pandas as pd

from brevettiai.utils import tag_utils
import brevettiai.interfaces.vue_schema_utils as vue
import numpy as np

log = logging.getLogger(__name__)


class BrevettiDatasetSamples(vue.VueSettingsModule):
    def __init__(self, classes: list = None, class_mapping: dict = None, annotations: dict = None,
                 calculate_md5: bool = False, walk: bool = True, samples_file_name: str = None,
                 contains_column: str = None, contains_regex: str = None):
        """
        :param class_mapping: dict of mapping from path to (category) class. See example for description
        :param classes: Force samples to be of the categories in this list
        """
        self.classes = classes or []
        self.class_mapping = class_mapping or {}
        self.annotations = annotations or {}
        self.calculate_md5 = calculate_md5
        self.walk = walk
        self.samples_file_name = samples_file_name or ""
        self.contains_column = contains_column or ""
        self.contains_regex = contains_regex or ""

    def get_image_samples(self, datasets, *args, **kwargs):
        """
        :param sample_filter: Filter samples by regex
        :param annotations: boolean, or dict Load annotation paths
        :param kwargs:
        :return: Dataframe of samples

        Mapping from path to category:
        Start from the leaf folder, and work towards the dataset root folder. If folder in class_mapping then apply
        its key as the category. If no match is found, apply leaf folder name
        Example:
        class_mapping={
        "A": ["Tilted"],
        "B": ["Tilted"],
        "1": ["Crimp"]
        }
        If classes is True or a list/set of categories. The filter is applied after the mapping.
        """

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(ds.get_image_samples, *args, **{**self.__dict__, **kwargs})
                       for ds in sorted(datasets, key=lambda x: x.id)]
        return pd.concat([f.result() for f in futures]).reset_index(drop=True)

    def get_samples(self, datasets, walk=None, *args, **kwargs):
        """
        Utility function for getting samples across multiple datasets by sample files
        :param datasets:
        :param target:
        :param args:
        :param kwargs:
        :return:
        """
        walk = walk if walk is not None else self.walk

        if walk:
            df = self.get_image_samples(datasets, *args, **kwargs)
        else:
            df = get_samples(datasets, self.samples_file_name)
        if self.contains_column:
            df = df[df[self.contains_column].str.contains(self.contains_regex, regex= True, na=False)]
        return df


def get_samples(datasets, target, *args, **kwargs):
    """
    Utility function for getting samples across multiple datasets by sample files
    :param datasets:
    :param target:
    :param args:
    :param kwargs:
    :return:
    """
    samples = (d.get_samples(target) for d in sorted(datasets, key=lambda x: x.id))
    return pd.concat(samples).reset_index(drop=True)


def save_samples(datasets, target, df):
    for d in datasets:
        d.save_samples(target, df)


def dataset_meta(datasets, tags):
    """
    Build dataset meta dataframe from datasets and tags tree
    :param datasets:
    :param tags:
    :return:
    """
    # Collect all tags
    meta = []
    for dataset in datasets:
        for tag in dataset.tags:
            for path in tag_utils.find_path(tags, "id", tag["id"]):
                name = path[0]["name"]
                key = "tag_" + path[0]["id"].replace(" ", "").replace('-', '_')
                value = path[1]["name"] if len(path) > 1 else path[0]["name"]
                meta.append({"dataset_id": dataset.id, "name":name, "key": key, "value": value})
    meta = pd.DataFrame.from_records(meta)
    # Pivot keys into columns and multivalues to tuples
    if len(meta):
        meta = meta.pivot_table(index="dataset_id", columns=["key", "name"], values="value", aggfunc=pd.unique)
    meta = meta.applymap(lambda x: tuple(x) if pd.api.types.is_list_like(x) else x)
    return meta


def join_dataset_meta(df, datasets, tags):
    """
    join dataset meta
    :param df: sample dataframe with dataset_id to join on
    :param datasets: Dataset objects with metadata
    :param tags: tag root tree, to find parent tags
    :return: df, name/column_id dictionary
    """
    assert "dataset_id" in df.columns, "df must contain dataset_id to join dataset metadata"

    meta = dataset_meta(datasets, tags)

    if len(meta):
        df = df.join(meta.droplevel(1, axis=1), on="dataset_id", how="left")
    return df, dict(meta.columns)


def get_grid_bboxes(bbox, size, tile_size=(1024, 1024), overlap=128, num_tile_steps: int = 1, max_steps: int = -1):
    """
    Get tiled bounding boxes with overlaps, the last row/column will have a larger overlap to fit the image
    :param bbox:
    :param size:
    :param tile_size:
    :param overlap:
    :param num_tile_steps:
    :param max_steps:
    :return:
    """
    assert num_tile_steps >= 1

    # Adjust input parameters for shorter square brackets
    if not hasattr(overlap, "__len__"):
        overlap = (overlap, overlap)

    if not hasattr(tile_size, "__len__"):
        tile_size = (tile_size, tile_size)
    tile_size = np.array(tile_size)

    # Ensure the used "bbox" is valid
    bbox = bbox.clip(min=(0, 0, 0, 0), max=(size[0], size[1], size[0], size[1]))

    w_offset = np.floor(tile_size[0] - overlap[0]).astype(np.int)
    h_offset = np.floor(tile_size[1] - overlap[1]).astype(np.int)

    img_width = bbox[2] - bbox[0]
    img_height = bbox[3] - bbox[1]
    assert img_width > 0
    assert img_height > 0

    # Extract width indexes
    if img_width > tile_size[0]:
        # Indexes should cover at least width - padding
        width = np.arange(0, img_width - overlap[0], w_offset)
        width = np.clip(width, 0, img_width - tile_size[0])
        lr_offset = np.pad((tile_size[0] - np.diff(width)) / 2, 1)
    else:
        width = np.array((0,))
        lr_offset = np.array((0, tile_size[0] - img_width))

    # Extract height indexes
    if img_height > tile_size[1]:
        height = np.arange(0, img_height - overlap[1], h_offset)
        height = np.clip(height, 0, img_height - tile_size[1])
        ud_offset = np.pad((tile_size[1] - np.diff(height)) / 2, 1)
    else:
        height = np.array((0,))
        ud_offset = np.array((0, tile_size[1] - img_height))

    # Find start coordinates of tiles, and move to bbox offset
    start_ix = np.stack([x.flatten() for x in np.meshgrid(width, height)], -1)
    start_ix = start_ix + bbox[:2]
    bboxes = np.concatenate((start_ix, start_ix + tile_size), 1)

    l_offset = np.ceil(lr_offset[:-1]).astype(np.int)
    u_offset = np.ceil(ud_offset[:-1]).astype(np.int)
    left_offsets = np.stack([x.flatten() for x in np.meshgrid(l_offset, u_offset)], -1)

    r_offset = tile_size[0] - np.floor(lr_offset[1:]).astype(np.int)
    d_offset = tile_size[1] - np.floor(ud_offset[1:]).astype(np.int)
    right_offsets = np.stack([x.flatten() for x in np.meshgrid(r_offset, d_offset)], -1)

    #
    # tile_fractional_step = tile_size // num_tile_steps
    # step_size = tile_size - 2 * overlap
    # if max_steps > 0:
    #     bbox[2] = min(bbox[2], bbox[0] - 2 * overlap + max_steps * step_size[0] - 1)
    #     bbox[3] = min(bbox[3], bbox[1] - 2 * overlap + max_steps * step_size[1] - 1)
    #
    # init_tile = np.array(bbox[:2]).clip(min=overlap)
    # end_tile = np.array([(vv + 1).clip(max=sz-overlap) for sz, vv in zip(size, bbox[2:])])
    #
    # tile_area = (end_tile - init_tile)
    #
    # full_tiles = (tile_area // step_size).clip(min=0)
    # fractional_tile = (tile_area - full_tiles * step_size).clip(min=0)
    # fractional_tile_apply = ((fractional_tile > 0) | (full_tiles == 0)).astype(np.int)
    # fractional_size = np.ceil((fractional_tile + 2 * overlap) / tile_fractional_step).astype(np.int) * tile_fractional_step
    #
    # # Build grid
    # grid_steps_full = [np.arange(ft + 1) * ss + iv for iv, ft, ss in zip(init_tile, full_tiles, step_size)]
    # grid_steps_fractional = [np.arange(frt) + fiv[-1] for fiv, frt in zip(grid_steps_full, fractional_tile_apply)]
    #
    # tiles_full = [np.array((gsf[:-1] - overlap, gsf[:-1] - overlap + ts)).T for gsf, ts in zip(grid_steps_full, tile_size)]
    # tiles_fractional = [np.hstack((gsf - overlap, gsf - overlap + fsize)).reshape(-1, 2)
    #                     for gsf, fsize in zip(grid_steps_fractional, fractional_size)]
    #
    # tiles_vectors = [np.vstack((v_fu, v_fr)) for v_fu, v_fr in zip(tiles_full, tiles_fractional)]
    # left_offsets = [np.ones(len(vv), dtype=int) * overlap for vv in tiles_vectors]
    # right_offsets = [vv[:, 1] - vv[:, 0] - overlap for vv in tiles_vectors]
    # for ii in range(2):
    #     left_offsets[ii][0] = bbox[ii] - tiles_vectors[ii][0, 0]
    #     right_offsets[ii][-1] = (tiles_vectors[ii][-1, 1] - tiles_vectors[ii][-1, 0]) - \
    #                             (tiles_vectors[ii][-1, 1] - (bbox[2+ii]+1)).clip(min=0)
    # bboxes = np.array([(v0[0], v1[0], v0[1], v1[1]) for v1 in tiles_vectors[1] for v0 in tiles_vectors[0]])
    # left_offsets = np.array([(lo0, lo1) for lo1 in left_offsets[1] for lo0 in left_offsets[0]])
    # right_offsets = np.array([(ro0, ro1) for ro1 in right_offsets[1] for ro0 in right_offsets[0]])

    return pd.Series([(len(height), len(width)), bboxes, left_offsets, right_offsets])
