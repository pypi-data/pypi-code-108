# -*- coding: utf-8 -*-
"""
Functions to register datasets for multiclass image classification.
Expects folder structure ./<classname>/[images]
"""
import pathlib
from typing import List, Union, Dict

import numpy as np
from detectron2.data import DatasetCatalog, MetadataCatalog
from sap_computer_vision.data.triplet_sampling_utils import TripletGenerator


__all__ = ["register",
           "create_triplets"]


def build_triplet_dict(triplets: Dict[str, Union[str, pathlib.Path]],
                       base_dir: Union[str, pathlib.Path, None] = None):
    if base_dir is not None:
        base_dir = pathlib.Path(base_dir)

    items = []
    for triplet in triplets:
        item = {}
        add_item = True
        for k in ['pos', 'neg', 'anchor']:
            img_path = pathlib.Path(triplet[k])
            if base_dir is not None:
                img_path = base_dir / img_path
            if img_path.exists():
                item[k] = {'file_name': str(img_path)}
            else:
                add_item = False
                break
        if add_item:
            items.append(item)
    return items


def register(name: str,
             triplets: List[Dict[str, Union[str, pathlib.Path]]],
             base_dir: Union[str, pathlib.Path, None] = None,
             **additional_dataset_infos):
    DatasetCatalog.register(name, lambda: build_triplet_dict(triplets, base_dir))
    MetadataCatalog.get(name).set(classes=None,
                                  base_dir=str(base_dir),
                                  **additional_dataset_infos)
    return name


def create_triplets(classes, excludes=None, size=1, rng=None, replace=False, example_vectors=None, images=None, return_triplet_dicts=False):
    generator = TripletGenerator(class_ids=classes,
                                 excludes=excludes,
                                 rng=rng,
                                 example_vectors=example_vectors)
    a, p, n = generator.build_random_triplets(size, replace)
    if images:
        images = np.array(images)
        a, p, n = images[a], images[p], images[n]
    if return_triplet_dicts:
        return [{'anchor': a_i, 'pos': p_i, 'neg': n_i} for a_i, p_i, n_i in zip(a, p, n)]
    else:
        return a, p, n
