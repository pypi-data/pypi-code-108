import aicsimageio
import numpy as np
import logging
import typing
import tifffile
from aicsimageio import AICSImage, aics_image
from multipledispatch import dispatch


log = logging.getLogger(__name__)

"""
ImageUtils
------------------
Class that contains some static methods to help handle images
Channel= 'C'
MosaicTile= 'M'
Samples= 'S'
SpatialX= 'X'
SpatialY= 'Y'
SpatialZ= 'Z'
Time= 'T'

Two main functions params are
image - AICSImage ("STCZYX")
image_ndarray - np.ndarray ("CZYX")
"""


class ImageUtils:

    @staticmethod
    def imread(image: typing.Union[np.ndarray, str]) -> AICSImage:
        with AICSImage(image) as img:
            img.size_z
            return img

    @staticmethod
    def imsave(image_ndarray: np.ndarray, path: str):
        tifffile.imsave(path, image_ndarray, image_ndarray.shape)

    @staticmethod
    @dispatch(AICSImage, int)
    def get_channel(image: AICSImage, channel_index: int) -> np.ndarray:
        return image.get_image_data("CZYX")[channel_index:channel_index+1, :, :, :]

    @staticmethod
    @dispatch(np.ndarray, int)
    def get_channel(image_ndarray: np.ndarray, channel_index: int) -> np.ndarray:
        return image_ndarray[channel_index:channel_index+1, :, :, :]

    @staticmethod
    def add_channel(image_ndarray: np.ndarray, channel) -> np.ndarray:
        new_image_ndarray = np.append(image_ndarray, channel, axis=0)
        return new_image_ndarray

    @staticmethod
    def image_to_ndarray(image):
        return image.get_image_data("CZYX")

    @staticmethod
    def get_channel_names(image):
        return image.get_channel_names()

    """
    Normalize all values between 0 to 1
    """
    @staticmethod
    def normalize(image_ndarray) -> np.ndarray:
        return image_ndarray/np.max(image_ndarray)
