"""In this module a methode to visualize the similarity between two images as seen by the model."""
from typing import Union, Iterable

import cv2
import numpy as np
import torch
import detectron2.data.detection_utils as utils


def visualize_similarities(image_a: Union[np.ndarray, torch.Tensor],
                           unpooled_a: Iterable[Union[np.ndarray, torch.Tensor]],
                           pooled_a: Iterable[Union[np.ndarray, torch.Tensor]],
                           image_b: Union[np.ndarray, torch.Tensor],
                           unpooled_b: Iterable[Union[np.ndarray, torch.Tensor]],
                           pooled_b: Iterable[Union[np.ndarray, torch.Tensor]],
                           pooling_type: str='average',
                           image_format: str='BGR',
                           image_channel_first: Union[str, bool]='auto',
                           cmap: str='magma',
                           aggregate: Union[str, None]='mean',
                           alpha: float=0.5):
    """Implementation of `Visualizing Deep Similarity Networks`https://arxiv.org/abs/1901.00536

    It is a function to visualize which part of two similar images contribute the most
    to the similarity. It is applicable to conv based distance metric learners using a pooling layer.

    Parameters
    ----------
    image_a/image_b: np.ndarry or torch.Tensor
        First/Second image as an array the format of the array can be specified with
        `image_format` and `image_channel_first`.
    unpooled_a/unpooled_b: Iterable of np.ndarry or torch.Tensor
        Name under which the dataset will be registered. Has to be unique
    pooled_a/pooled_b: Iterable of np.ndarry or torch.Tensor
        Name under which the dataset will be registered. Has to be unique
    pooling_type: ['average', 'max'], optional, default='average'
        Type of pooling layer used in the model.
    image_format: str, optional, default='BGR'
        One of the supported image modes in PIL, or "BGR" or "YUV-BT.601".
    image_channel_first: bool or 'auto'
        Whether the color channel of the image is in the first axis of the image arrays.
        If 'auto' the color channel axis is determined by np.argmin(image_arr.shape).
    cmap: str or None, optional, default='magma
        Name of the matplotlib cmap used to create a visualization. The similarity heatmap
        is used as an overlay for the input image.
        If `None`the raw similarity values are returned.
    alpha: float, optional, default=0.5
        Alpha of the similarity heat map.


    Returns
    ----------

    """
    image_a = _image_to_rgb_numpy(image_a, image_format, image_channel_first)
    image_b = _image_to_rgb_numpy(image_b, image_format, image_channel_first)
    unpooled_a = [_convert_to_numpy(a) for a in unpooled_a]
    pooled_a = [_convert_to_numpy(a) for a in pooled_a]
    unpooled_b = [_convert_to_numpy(a) for a in unpooled_b]
    pooled_b = [_convert_to_numpy(a) for a in pooled_b]
    sim_ab, sim_ba = _calculate_similarities(image_a=image_a,
                                            unpooled_a=unpooled_a,
                                            pooled_a=pooled_a,
                                            image_b=image_b,
                                            unpooled_b=unpooled_b,
                                            pooled_b=pooled_b,
                                            pooling_type=pooling_type,
                                            aggregate=aggregate)
    if cmap is not None:
        try:
            from matplotlib import pyplot as plt
        except ImportError:
            raise ImportError('To create a visualization from the similarity matplotlib has to be installed')
        cmap = plt.get_cmap(cmap)
        min_ = np.min((np.min(sim_ab), np.min(sim_ba)))
        max_ = np.max((np.max(sim_ab), np.max(sim_ba)))
        sim_ab = (sim_ab - min_) / max_
        sim_ba = (sim_ba - min_) / max_
        if len(sim_ba.shape) == 3:
            for i in range(len(sim_ab)):
                sim_ab[i] = _apply_heatmap(image_a, sim_ab[i], alpha, cmap)
                sim_ba[i] = _apply_heatmap(image_b, sim_ba[i], alpha, cmap)
        else:
            sim_ab = _apply_heatmap(image_a, sim_ab, alpha, cmap)
            sim_ba = _apply_heatmap(image_b, sim_ba, alpha, cmap)

    return sim_ab, sim_ba


def _image_to_rgb_numpy(image, image_format, channel_first='auto'):
    image = _convert_to_numpy(image)
    if channel_first == 'auto':
        channel_first = np.argmin(image.shape) == 0
    if channel_first:
        image = np.moveaxis(image, 0, -1)
    return utils.convert_image_to_rgb(image, image_format)

def _apply_heatmap(image, sim, alpha, cmap):
    sim_c = cmap(sim)[:, :, :3]
    if image.dtype == np.uint8:
        sim_c *= 255
        sim_c = sim_c.astype(np.uint8)
    if alpha < 1:
        sim_c = cv2.addWeighted(image, (1-alpha), sim_c, alpha, 0.0)
    return sim_c


def _calculate_similarities(image_a,
                           unpooled_a,
                           pooled_a,
                           image_b,
                           unpooled_b,
                           pooled_b,
                           pooling_type='average',
                           aggregate='mean'):
    h_a, w_a, _ = image_a.shape
    h_b, w_b, _ = image_b.shape
    joined_sim_ab = _calc_sim(unpooled_a, pooled_a, pooled_b, pooling_type=pooling_type, height=h_a, width=w_a, aggregate=aggregate)
    joined_sim_ba = _calc_sim(unpooled_b, pooled_b, pooled_a, pooling_type=pooling_type, height=h_b, width=w_b, aggregate=aggregate)
    return joined_sim_ab, joined_sim_ba

def _convert_to_numpy(arr):
    if isinstance(arr, torch.Tensor):
        arr = arr.cpu().numpy()
    if not isinstance(arr, np.ndarray):
        raise TypeError(f'Expected np.array or torch.Tensor, but got {type(arr)}.')
    return arr

def _calc_sim(unpooled_a, pooled_a, pooled_b, pooling_type='average', height=None, width=None, aggregate='mean'):
    sim_layers = []
    assert len(unpooled_a) == len(pooled_a) == len(pooled_b)
    for unpooled_a_i, pooled_a_i, pooled_b_i in zip(unpooled_a, pooled_a, pooled_b):
        assert unpooled_a_i.shape[0] == len(pooled_a_i) == len(pooled_b_i)
        if pooling_type.lower() == 'average':
            normalization = unpooled_a_i.shape[1] * unpooled_a_i.shape[2] * np.linalg.norm(pooled_a_i) * np.linalg.norm(pooled_b_i)
            sim_layers.append(np.einsum('ijk,i->jk', unpooled_a_i, pooled_b_i) / normalization)
        elif pooling_type.lower() == 'max':
            surrogate_unpooled = np.zeros_like(unpooled_a_i)
            for c_idx, c_val in enumerate(pooled_a_i):
                try:
                    idx_x, idx_y = np.where(unpooled_a_i[c_idx] == c_val)
                except:
                    raise
                surrogate_unpooled[c_idx, idx_x, idx_y] = c_val / len(idx_x)
            normalization = np.linalg.norm(pooled_a_i) * np.linalg.norm(pooled_b_i)
            sim_layers.append(np.einsum('ijk,i->jk', surrogate_unpooled, pooled_b_i) / normalization)
    stacked = np.array([cv2.resize(s, (width, height), interpolation=cv2.INTER_NEAREST) for s in sim_layers])
    if aggregate == 'mean':
        stacked = np.mean(stacked, axis=0)
    elif aggregate == 'sum':
        stacked = np.sum(stacked, axis=0)
    elif aggregate == 'prod':
        stacked = np.prod(stacked, axis=0)
    return stacked
