import numpy as np
import logging
import typing
import matplotlib.pyplot as plt




log = logging.getLogger(__name__)

"""
PlotsUtils
------------------
Class that contains some static methods to help handle and output plots
"""


class PlotsUtils:

    @staticmethod
    def plot_image_heatmap(image: np.ndarray,title: str, xlabel: str, ylabel: str, save: typing.Union[str, None]=None) -> None:
        plt.figure()
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        # plt.colorbar()
        plt.imshow(image, cmap='seismic', interpolation='nearest')
        # cb = np.linspace(0.0,1.0,20)
        # cax = plt.axes(cb)
        plt.colorbar()
        if (save != None):
            plt.savefig(save)
        plt.show()

