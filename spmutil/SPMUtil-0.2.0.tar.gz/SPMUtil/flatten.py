from enum import Enum

import numpy as np


class FlattenMode(Enum):
    Average = 1
    LinearFit = 2
    PolyFit = 3
    Off = 4




def get_flatten_param(map2d: np.ndarray, flatten=FlattenMode.LinearFit, poly_fit_order=2):
    size = map2d.shape
    array_x = np.linspace(0, size[0], size[0])
    array_y = np.linspace(0, size[1], size[1])


    if flatten == FlattenMode.Average:
        raise ValueError("please use fitting_map function for FlattenMode.Average")
    if flatten == FlattenMode.LinearFit:
        coef_x, coef_y = 0, 0
        for i in range(0, size[1]):
            coef = np.polyfit(array_x, map2d[:, i], 1)
            coef_x += coef[0]
        for i in range(0, size[0]):
            coef = np.polyfit(array_y, map2d[i], 1)
            coef_y += coef[0]
        return coef_x/size[1], coef_y/size[0]

    if flatten == FlattenMode.PolyFit:
        coef_x = np.polyfit(array_x, map2d[:, 0], poly_fit_order)
        coef_y = np.polyfit(array_y, map2d[0], poly_fit_order)
        for i in range(1, size[1]):
            coef_x += np.polyfit(array_x, map2d[:, 0], poly_fit_order)
        for i in range(1, size[0]):
            coef_y += np.polyfit(array_y, map2d[0], poly_fit_order)
        return np.array(coef_x)/size[1], np.array(coef_y)/size[0]

    else:
        raise ValueError("incorrect flatten mode param")



def apply_flatten_plane(map: np.ndarray, coef_x, coef_y, poly_fit_order=2):
    size = map.shape
    if poly_fit_order == 1 or type(coef_x) is np.float64:
        map -= np.tile(np.linspace(0, size[1], size[1]), (size[0], 1)) * coef_y \
               + np.tile(np.array([np.linspace(0, size[0], size[0])]).transpose(), (1, size[1])) * coef_x
    elif poly_fit_order > 1:
        map -= np.tile(np.poly1d(coef_y)(np.linspace(0, size[1], size[1])), (size[0], 1)) \
               + np.tile(np.array([np.poly1d(coef_x)(np.linspace(0, size[0], size[0]))]).transpose(), (1, size[1]))
    return map - np.min(map)


def flatten_map(map2d: np.ndarray, flatten=FlattenMode.Average, poly_fit_order=2):
    size = map2d.shape
    if flatten == FlattenMode.Average:
        map2d -= np.nanmean(map2d)
        col_ave = np.nanmean(map2d, axis=0)
        row_ave = np.nanmean(map2d, axis=1)
        map2d -= np.tile(col_ave, (size[0], 1)) + np.tile(np.array([row_ave]).transpose(), (1, size[1]))

    elif flatten == FlattenMode.LinearFit or flatten == FlattenMode.PolyFit:
        coef1, coef2 = get_flatten_param(map2d, flatten=flatten, poly_fit_order=poly_fit_order)
        map2d = apply_flatten_plane(map2d, coef1, coef2, poly_fit_order)

    return map2d

