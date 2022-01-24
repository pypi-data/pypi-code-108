import os.path
from typing import List
import numpy as np
from pandas import DataFrame
import urllib.request
import tarfile
from scipy.spatial.distance import euclidean


def distance(bp1: DataFrame, bp2: DataFrame, frame: int):
    """
    calculates the distance between DataFrame points

    """
    p1 = (bp1["x"][frame], bp1["y"][frame])
    p2 = (bp2["x"][frame], bp2["y"][frame])

    d = euclidean(p1, p2)
    return d


def point_array(data_frame: DataFrame, points: List[str]):
    nd_arrays = list()
    for point in points:
        nd_arrays.append(data_frame[point].to_numpy(dtype=np.float64))
    return np.stack(nd_arrays, axis=0)[:, :, 0:2]


def angle_between_lines(m1: float, m2: float) -> float:
    """
    calculates the angle between 2 lines in degrees
    :param m1: slope of line 1
    :param m2: slope of line 2
    :return: angle
    """
    return float(np.degrees(np.arctan(((m2 - m1) / (1 + m1 * m2)))))


def download_model(url: str, dest: str) -> str:
    """
    downloads a tarball model from url to dest/temp extracts it to dest/tar_name and returns the path of the
    model directory
    :param url: the url to download the model from
    :param dest: the destination to put the model
    :return: the path of the model directory
    """
    temp = os.path.join(dest, "temp")
    if not os.path.isdir(temp):
        os.mkdir(temp)
    model_tar = urllib.request.urlretrieve(url, temp)[0]
    if tarfile.is_tarfile(model_tar):
        ext = os.path.splitext(model_tar)[1]
        if ext == "gz" or ext == ".gz":
            tar = tarfile.open(model_tar, "r:gz")
        elif ext == "xz" or ext == ".xz":
            tar = tarfile.open(model_tar, "r:gz")
        else:
            raise ValueError("File must be .tar.gz or tar.xz")
    else:
        raise ValueError("File must be .tar.gz or tar.xz")
    name = os.path.splitext(os.path.split(model_tar)[1])[0]
    if not os.path.isdir(name):
        os.mkdir(name)
    tar.extractall(name)
    return name
