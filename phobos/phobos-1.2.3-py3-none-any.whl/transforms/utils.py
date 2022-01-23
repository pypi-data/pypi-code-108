from albumentations.core.composition import Compose

from .transforms import Normalize, MinMaxNormalize
from phobos.config import get_map, save_map
import logging

transforms_cmap = {
    'normalize': Normalize,
    'minmaxnormalize': MinMaxNormalize
}

transforms_map = get_map('transform')
transforms_map.update(transforms_cmap)

def save_transforms_map(dest):
    """Saves transforms map in location ``dest`` as a json file

    This file can later be used to lookup phobos supported transforms

    Parameters
    ----------
    dest : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ 
        destination path

    Examples
    --------
    Save transforms map in location ``/tmp``

    >>> save_transforms_map('/tmp')
    
    """
    save_map(map=transforms_map, name='transform', dest=dest)

def build_pipeline(dstype, train_aug_dict, val_aug_dict):
    """Create train and val transforms pipelines from args.

    Parameters
    ----------
    train_aug_dict : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        Dictionary of transforms to be applied in training pipeline.
    val_aug_dict : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        Dictionary of transforms to be applied in validation pipeline.

    Returns
    -------
    train _aug_pipeline / val_aug_pipeline : `Compose  <https://albumentations.ai/docs/api_reference/core/composition/#albumentations.core.composition.Compose>`_
        train pipeline / val pipeline based on :attr:`dstype` passed

    Examples
    --------
    Create train and val transforms pipeline using arguments' Namespace instance

    >>> params = {
    ...             'train_augs':
    ...             {
    ...                 'augmentations':{    
    ...                         'normalize': {},
    ...                         'verticalflip': {'p': 0.5},
    ...                         'horizontalflip': {'p': 0.5}
    ...                  }
    ...             },
    ...             'val_augs':
    ...             {
    ...                 'augmentations':{   
    ...                         'horizontalflip': {'p': 0.5}
    ...                  }
    ...             }
    ...         }
    >>> args = Namespace(**params)
    >>> train_pipeline = build_pipeline('train', args.train_augs, args.val_augs)
    >>> val_pipeline = build_pipeline('val', args.train_augs, args.val_augs)
    >>> train_pipeline
    Compose([
        Normalize(always_apply=False, p=1.0, mean=[0.485 0.456 0.406], std=[0.229 0.224 0.225]),
        VerticalFlip(always_apply=False, p=0.5),
        HorizontalFlip(always_apply=False, p=0.5),
    ], p=1.0, bbox_params=None, keypoint_params=None, additional_targets={})
    >>> val_pipeline
    Compose([
        HorizontalFlip(always_apply=False, p=0.5),
    ], p=1.0, bbox_params=None, keypoint_params=None, additional_targets={})

    Use these pipelines to apply transforms to image and masks in dataloaders. We pass patches to pipeline below

    >>> img = full_load[key]['i']
    >>> msk = full_load[key]['m']
    >>>
    >>> img_crop = np.copy(img[:,x:x+w,y:y+w])
    >>> msk_crop = np.copy(msk[x:x+w,y:y+w])
    >>>
    >>> trns_out = train_pipeline(image=img_crop,mask=msk_crop)
    >>>
    >>> tr_img_crop = trns_out['image']
    >>> tr_msk_crop = trns_out['mask']

    Click `here <phobos.transform.map.html>`_ for details of transforms supported by phobos currently

    Custom transforms can also be added to transforms pipelines. Please check `here <phobos.transforms.html#phobos.transforms.utils.set_transform>`_ for more details.
 
    """
    logging.debug("Enter build_pipeline routine")
    if dstype == 'train':
        train_aug_pipeline = process_aug_dict(train_aug_dict)
        return train_aug_pipeline
    elif dstype == 'val':
        val_aug_pipeline = process_aug_dict(val_aug_dict)
        return val_aug_pipeline
    else:
        print("Please enter a valid type(train/val)")


def _check_augs(augs):
    """Check if augmentations are loaded in already or not.

    Parameters
    ----------
    augs : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_ / `Compose  <https://albumentations.ai/docs/api_reference/core/composition/#albumentations.core.composition.Compose>`_
        loaded/unloaded augmentations.

    Returns
    -------
    `Compose  <https://albumentations.ai/docs/api_reference/core/composition/#albumentations.core.composition.Compose>`_
        loaded augmentations.

    """
    logging.debug("Enter _check_augs routine")
    if isinstance(augs, dict):
        return process_aug_dict(augs)
    elif isinstance(augs, Compose):
        return augs


def process_aug_dict(pipeline_dict, meta_augs_list=['oneof', 'oneorother']):
    """Create a Compose object from an augmentation config dict.

    Parameters
    ----------
    pipeline_dict : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        augmentation config dictionary.
    meta_augs_list : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list of meta augmentations.

    Returns
    -------
    compose : `Compose  <https://albumentations.ai/docs/api_reference/core/composition/#albumentations.core.composition.Compose>`_
        Compose object formed from augmentation dictionary.

    """
    logging.debug("Enter process_aug_dict routine")
    if pipeline_dict is None:
        return None
    xforms = pipeline_dict['augmentations']
    composer_list = get_augs(xforms, meta_augs_list)
    logging.debug("composer_list")
    logging.debug(composer_list)
    logging.debug("Exit process_aug_dict routine")
    return Compose(composer_list)


def get_augs(aug_dict, meta_augs_list=['oneof', 'oneorother']):
    """Get the set of augmentations contained in a dict.

    Parameters
    ----------
    aug_dict : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary containing augmentations.
    meta_augs_list : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list of meta augmentations.

    Returns
    -------
    aug_list : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list of augmentations.

    """
    logging.debug("Enter get_augs routine")
    aug_list = []
    if aug_dict is not None:
        for aug, params in aug_dict.items():
            if aug.lower() in meta_augs_list:
                # recurse into sub-dict
                aug_list.append(transforms_map[aug](get_augs(aug_dict[aug])))
            else:
                aug_list.append(_get_aug(aug, params))
    logging.debug("Exit get_augs routine")
    return aug_list


def _get_aug(aug, params):
    """Get augmentations (recursively if needed) from items in the aug_dict.

    Parameters
    ----------
    aug : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        string describing augmentation.
    params : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of augmentation parameters.

    Returns
    -------
    aug_obj : `albumentations.augmentations.transforms <https://albumentations.ai/docs/api_reference/augmentations/transforms/#transforms-augmentationstransforms>`_
        augmentation object.

    """
    aug_obj = transforms_map[aug.lower()]
    if params is None:
        return aug_obj()
    elif isinstance(params, dict):
        return aug_obj(**params)
    else:
        raise ValueError(
            '{} is not a valid aug param (must be dict of args)'.format(params))


def set_transform(key, transform):
    """Allows: 

    * Addition of a new transform to transforms map
    
    * Modification of existing transform definitions in transforms map

    Parameters
    ----------
    key : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        type of scheduler instance
    transform : `albumentations.core.transforms_interface <https://albumentations.ai/docs/api_reference/core/transforms_interface/>`_
        transform class

    Examples
    --------
    Add a dummy transform to transforms map 

    >>> from albumentations.core.transforms_interface import ImageOnlyTransform
    >>> class DummyTransform(ImageOnlyTransform):
    ...     def __init__(self, args):
    ...         super().__init__(**args)
    >>>
    >>> key = 'dummytransform'
    >>> set_transform(key,DummyTransform)

    This transform can then be used in pipelines

    >>> params = {
    ...             'train_augs':
    ...             {
    ...                 'augmentations':{    
    ...                         'normalize': {},
    ...                         'verticalflip': {'p': 0.5},
    ...                         'horizontalflip': {'p': 0.5}
    ...                  }
    ...             },
    ...             'val_augs':
    ...             {
    ...                 'augmentations':{   
    ...                         'horizontalflip': {'p': 0.5},
    ...                         'dummytransform': {}
    ...                  }
    ...             }
    ...         }
    >>> args = Namespace(**params)
    >>> val_pipeline = build_pipeline('val', args.train_augs, args.val_augs)
    >>> val_pipeline
    Compose([
        HorizontalFlip(always_apply=False, p=0.5),
        DummyTransform(),
    ], p=1.0, bbox_params=None, keypoint_params=None, additional_targets={})

    Click `here <phobos.transform.map.html>`_ for details of transforms supported by phobos currently
    
    """
    logging.debug("Enter set_transform routine")
    transforms_map[key] = transform
    logging.debug("Exit set_transform routine")