from typing import Callable, List, Union

import detectron2.data.transforms as T_
from detectron2.config import CfgNode
from fvcore.transforms.transform import Transform
from timm.data.auto_augment import rand_augment_transform
from timm.data.random_erasing import RandomErasing

from detectron2.data import detection_utils as utils
from PIL import Image
import numpy as np


ALL_AUGS_KEYS = [
    'RANDOM_FLIP',
    'CROP',
    'RANDOM_LIGHTING',
    'RANDOM_BRIGHTNESS',
    'RANDOM_SATURATION',
    'RANDOM_CONTRAST',
    'RAND_AUG',
    'CUT_OUT'
    ]


class RandAugWrapper(Transform):
    def __init__(self, config_str, image_format='BGR', probs=0.5, ):
        super().__init__()
        self.image_format = image_format
        self.augs = rand_augment_transform(config_str, {})
        for op in self.augs.ops:
            op.prob = probs

    def apply_image(self, img: np.ndarray):
        img = utils.convert_image_to_rgb(img, self.image_format)
        return utils.convert_PIL_to_numpy(self.augs(Image.fromarray(img)), format=self.image_format)

    def apply_coords(self, *args, **kwargs):
        raise NotImplementedError


class RandAug(T_.Augmentation):
    def __init__(self, cfg_str: str, image_format='BGR', probs: float=0.5):
        self.aug = RandAugWrapper(cfg_str, image_format, probs=probs)

    def get_transform(self, *args) -> Transform:
        return self.aug

class RandomCutOutTransform(Transform):

    def __init__(self, pos_rel_x, pos_rel_y, rel_area, aspect_ratio, random_color=True, per_pixel=True, contain=False, const_color=(127.5 , 127.2, 127.5)):
        super().__init__()
        self.pos_rel_x = np.atleast_1d(pos_rel_x)
        self.pos_rel_y = np.atleast_1d(pos_rel_y)
        self.rel_area = np.atleast_1d(rel_area)
        self.aspect_ratio = np.atleast_1d(aspect_ratio)
        self.orientation = np.random.choice(['vertical', 'horizontal'], size=len(self.pos_rel_x), replace=True)
        self.aspect_ratio = np.clip(aspect_ratio, 0., 1.)
        self.random_color = random_color
        self.const_color = const_color
        self.per_pixel = per_pixel
        self.contain = contain

    def add_box(self, img: 'np.ndarray', pos_rel_x, pos_rel_y, rel_area, aspect_ratio, orientation):
        h, w = img.shape[0], img.shape[1]
        abs_area = rel_area * h * w
        factor_h, factor_w = (1., aspect_ratio) if orientation == 'vertical' else (aspect_ratio, 1.)
        len_longer_side = np.sqrt(abs_area / (factor_w * factor_h))
        box_h, box_w = len_longer_side * factor_h, len_longer_side * factor_w
        if self.contain:
            if w - box_w < 0:
                pos_abs_x = w * 0.5
            else:
                pos_abs_x = box_w / 2. + (w - box_w) * pos_rel_x
            if h - box_h < 0:
                pos_abs_y = h * 0.5
            else:
                pos_abs_y = box_h / 2. + (h - box_h) * pos_rel_y
        else:
            pos_abs_x, pos_abs_y = pos_rel_x * w, pos_rel_y * h
        x_0, x_1 = np.clip([pos_abs_x - (box_w / 2.), pos_abs_x + (box_w / 2.)], 0., w).astype(int)
        y_0, y_1 = np.clip([pos_abs_y - (box_h / 2.), pos_abs_y + (box_h / 2.)], 0., h).astype(int)
        box = self.get_random_color(img, y_1-y_0, x_1-x_0, self.random_color, self.per_pixel)
        img[slice(y_0, y_1), slice(x_0, x_1), :] = box
        return img

    def get_random_color(self, img, h, w, random_color=True, per_pixel=True):
        dtype = img.dtype
        col = np.zeros((h, w, 3), dtype=dtype)
        if not random_color and not per_pixel:
            if self.const_color == 'median':
                const_color = np.median(img, axis=(0,1))
            else:
                const_color = self.const_color
            col += np.array(const_color).astype(col.dtype)
        elif random_color and not per_pixel:
            col += (np.random.uniform(size=3) * 255.).astype(col.dtype)
        else:
            col += (np.random.uniform(size=col.shape) * 255.).astype(col.dtype)
        return col

    def apply_image(self, img: np.ndarray):
        for x, y, a, r, o in zip(self.pos_rel_x,
                                 self.pos_rel_y,
                                 self.rel_area,
                                 self.aspect_ratio,
                                 self.orientation):
            img = self.add_box(img, x, y, a, r, o)
        return img

    def apply_coords(self, *args, **kwargs):
        raise NotImplementedError


class RandomCutOut(T_.Augmentation):
    def __init__(self, min_area, max_area, min_aspect_ratio, max_aspect_ratio=None, random_color=True, per_pixel=True, max_holes=1, contain=False, const_color=(127.5 , 127.3, 127.5)):
        self.min_area = min_area
        self.max_area = max_area
        self.min_aspect_ratio = min(min_aspect_ratio, 1.)
        self.max_aspect_ratio = max(min(max_aspect_ratio if max_aspect_ratio else 1., 1.), self.min_aspect_ratio)
        self.random_color = random_color
        self.const_color = const_color
        self.per_pixel = per_pixel
        self.contain = contain
        self.max_holes = max_holes

    def get_transform(self, *args) -> Transform:
        n_holes = np.random.randint(1, self.max_holes+1)
        pos_rel_x = np.random.uniform(size=n_holes)
        pos_rel_y = np.random.uniform(size=n_holes)
        rel_area = self.min_area + np.random.uniform(size=n_holes) * (self.max_area - self.min_area)
        aspect_ratio = self.min_aspect_ratio + np.random.uniform(size=n_holes) * (self.max_aspect_ratio - self.min_aspect_ratio)
        return RandomCutOutTransform(
            pos_rel_x=pos_rel_x,
            pos_rel_y=pos_rel_y,
            rel_area=rel_area,
            aspect_ratio=aspect_ratio,
            random_color=self.random_color,
            const_color=self.const_color,
            per_pixel=self.per_pixel,
            contain=self.contain)


def build_augmentations(cfg: CfgNode, img_format: str) -> List['T_.Transform']:
    """Build additional augmentations.
    Parameters
    ----------
    cfg: CfgNode
        Config
    Returns
    -------
    list of T_.Transform
        List of augmentation
    """
    augmentations = []
    if cfg.get('CROP', {}).get('ENABLED', False):
        augmentations.append(T_.RandomCrop(cfg.CROP.TYPE, cfg.CROP.SIZE))
    if cfg.get('RESIZE', {}).get('MODE', None):
        if cfg.RESIZE.MODE is not None and cfg.RESIZE.MODE.upper() == 'FIXED':
            if isinstance(cfg.RESIZE.FIXED_SIZE, tuple):
                h, w = cfg.RESIZE.FIXED_SIZE
            else:
                h, w = cfg.RESIZE.FIXED_SIZE, cfg.RESIZE.FIXED_SIZE
            if not (isinstance(h, int) and isinstance(w, int)):
                raise TypeError('`cfg.RESIZE.FIXED_SIZE` hast to be None, int or (int, int).')
            augmentations.append(T_.Resize((h, w)))
        elif cfg.RESIZE.MODE is not None and cfg.RESIZE.MODE.upper() == 'SHORTEST_EDGE':
            augmentations.append(T_.ResizeShortestEdge(
                cfg.RESIZE.MIN_SIZE,
                cfg.RESIZE.MAX_SIZE,
                cfg.RESIZE.SAMPLE_STYLE))
    if cfg.get('RANDOM_FLIP', None) is not None:
        augmentations.append(T_.RandomFlip(horizontal=cfg.RANDOM_FLIP == "horizontal",
                                           vertical=cfg.RANDOM_FLIP == "vertical"))
    if cfg.get('RANDOM_LIGHTING', {}).get('ENABLED', False):
        augmentations.append(T_.RandomLighting(cfg.RANDOM_LIGHTING.STRENGTH))
    if cfg.get('RANDOM_BRIGHTNESS', {}).get('ENABLED', False):
        augmentations.append(T_.RandomBrightness(*cfg.RANDOM_BRIGHTNESS.STRENGTH))
    if cfg.get('RANDOM_SATURATION', {}).get('ENABLED', False):
        augmentations.append(T_.RandomSaturation(*cfg.RANDOM_BRIGHTNESS.STRENGTH))
    if cfg.get('RANDOM_CONTRAST', {}).get('ENABLED', False):
        augmentations.append(T_.RandomContrast(*cfg.RANDOM_CONTRAST.STRENGTH))
    if cfg.get('RAND_AUG', {}).get('ENABLED', False):
        augmentations.append(RandAug(cfg.RAND_AUG.CONFIG_STR, img_format, cfg.RAND_AUG.PROB))
    if cfg.get('CUT_OUT', {}).get('ENABLED', False):
        aug =RandomCutOut(*sorted(cfg.CUT_OUT.get('AREA_RANGE', (0.05, 0.1))),
                          *sorted(cfg.CUT_OUT.get('ASPRECT_RATIO_RANGE', (0.5, 1.))),
                          random_color=cfg.CUT_OUT.get('RANDOM_COLOR', True),
                          const_color=cfg.CUT_OUT.get('CONST_COLOR', (127.5 , 127.4, 127.5)),
                          per_pixel=cfg.CUT_OUT.get('PER_PIXEL', False),
                          contain=cfg.CUT_OUT.get('CONTAIN', True),
                          max_holes=cfg.CUT_OUT.get('MAX_HOLES', 1),)
        if cfg.CUT_OUT.get('BEFORE_RESIZE', False):
            augmentations = [aug] + augmentations
        else:
            augmentations.append(aug)
    return augmentations


def generate_aug_cfg_node(cfg, target_cfg_node, is_train=True):
    target_cfg_node = target_cfg_node.clone()
    target_cfg_node.defrost()
    if cfg.INPUT.get('FIXED_IMAGE_SIZE', None):
        kwargs = {'MODE': 'FIXED',
                  'FIXED_SIZE': cfg.INPUT.FIXED_IMAGE_SIZE}
    else:
        mode = 'SHORTEST_EDGE'
        if is_train:
            min_size = cfg.INPUT.MIN_SIZE_TRAIN
            max_size = cfg.INPUT.MAX_SIZE_TRAIN
            sample_style = cfg.INPUT.MIN_SIZE_TRAIN_SAMPLING
        else:
            min_size = cfg.INPUT.MIN_SIZE_TEST
            max_size = cfg.INPUT.MAX_SIZE_TEST
            sample_style = "choice"
        kwargs = {'MODE': mode,
                  'MIN_SIZE': min_size,
                  'MAX_SIZE': max_size,
                  'SAMPLE_STYLE': sample_style}
    target_cfg_node.RESIZE = CfgNode(kwargs)
    return target_cfg_node
