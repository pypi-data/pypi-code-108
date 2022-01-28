# -*- coding: utf-8 -*-
# @Author: Zhai Menghua
# @Date:   2020-07-16 10:10:48
# @Last Modified by:   Zhai Menghua
# @Last Modified time: 2020-07-16 10:13:00

# -*-coding:utf-8-*-
#
# Compress and Decompress the shape object
#
import numpy as np
import copy


def encode_labelme_shape(point_list):
    """
    Encode the labelme shape (usually a list of points)
    Return a serializable object (usually a string) for json dumping
    """
    code = list()
    for point in point_list:
        assert len(point) == 2
        code.append('{:.6f}+{:.6f}'.format(point[0], point[1]))
    code = ','.join(code)
    return code


def decode_labelme_shape(encoded_shape):
    """
    Decode the cnn json shape (usually encoded from labelme format)
    Return a list of points that are used in labelme
    """
    assert isinstance(encoded_shape, str)
    points = encoded_shape.split(',')
    shape = list()
    for point in points:
        x, y = point.split('+')
        shape.append([float(x), float(y)])
    return shape


def encode_distribution(distribution):
    """
    Encode the distribution (usually a list of float)
    Return a serializable object (usually a string) for json dumping
    """
    code = list()
    for data in distribution:
        if None:
            pass
        elif isinstance(data, float) or isinstance(data, np.float32):
            code.append('{:0.6e}'.format(data))
        elif isinstance(data, int):
            code.append(str(data))
        else:
            raise RuntimeError
    code = ','.join(code)
    return code


def decode_distribution(encoded_distribution):
    """
    Decode the cnn json distribution (usually encoded data)
    Return a list of float
    """
    if isinstance(encoded_distribution, list):
        return encoded_distribution
    assert isinstance(encoded_distribution, str)
    distribution_str_list = encoded_distribution.split(',')
    distribution = list()
    for data_str in distribution_str_list:
        data = float(data_str)
        distribution.append(data)
    return distribution
