import os, json, inspect
import phobos
import torch
import torchmetrics
import albumentations

def get_map(type):
    """dynamically generates and returns a map of third party components
    
    supported by phobos by traversing through third party libraries

    Parameters
    ----------
    type : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ 
        component type

    Returns
    -------
    `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map of third party components

    Examples
    --------
    retrieve a map of third party schedulers supported by phobos

    >>> smap = get_map('scheduler')

    """
    mlistmap = {
        'metric': [ 
            torchmetrics.image,
            torchmetrics.retrieval,
            torchmetrics.regression,
            torchmetrics.classification
        ],
        'loss': [
            torch.nn
        ],
        'optimizer': [
            torch.optim
        ],
        'scheduler': [
            torch.optim.lr_scheduler
        ],
        'transform': [
            albumentations.augmentations,
            albumentations.core.composition,
            albumentations.augmentations.crops,
            albumentations.augmentations.geometric
        ]   
    }

    modlist = mlistmap[type]

    mtuples = [entry for mod in modlist for entry in inspect.getmembers(mod) if isinstance(entry, tuple)]
    map = { key.lower(): val for key, val in mtuples if inspect.isclass(val)}
    if type == 'loss':
        map = {key: map[key] for key in map if 'loss' in key}

    return map

def save_map(map, name, dest):
    """Saves component map in location ``dest`` as ``name.json``

    Parameters
    ----------
    map : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        component map
    name : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ 
        name of json to save
    dest : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ 
        destination path for json

    Examples
    --------
    Retrieve a map of third party schedulers supported by phobos

    >>> smap = get_map('scheduler')

    Save schedulers map in location : ``/tmp`` by name ``loss.json``

    >>> save_map(map=smap, name=name, dest=dst)

    """
    map = { key: str(map[key]) for key in map}

    dfile = os.path.join(dest, '{}.json'.format(name))

    with open(dfile, 'w') as fp:
        json.dump(map, fp, indent=4)     
