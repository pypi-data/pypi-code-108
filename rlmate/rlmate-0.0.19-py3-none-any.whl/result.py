import os
from datetime import datetime
import sys

import torch
import numpy as np
import matplotlib.pyplot as plt
import logging

from pathlib import Path
import pathlib

# path_to_hermes = pathlib.Path(__file__).parent.resolve().joinpath('..')
# sys.path.append(str(path_to_hermes))
from . import util


class Result(dict):
    """
    A class for storing results, i.e. data that is generated during the execution of some script/experiment.

    This class inherits from :python:`dict` and provides useful methods for
    - storing data in the underlying dictionary
    - saving the dictionary to disk
    - accessing stored data
    - plotting stored data

    Note that these plots are meant for rapid prototyping/debugging and are neither very pretty, nor camera-ready as of yet.
    """

    def __init__(self, name, path=None, dictionary=None):
        if dictionary is not None:
            super().__init__(dictionary)
        else:
            super().__init__()
        self.name = name
        self.path = path

    @property
    def dictionary(self):
        return {key: val for key, val in self.items()}

    @classmethod
    def new(cls, name):
        """
        Create a new result and give it a name

        :param name: the result name
        :type name: str

        :return: the result
        :rtype: Result
        """
        res = cls(name)
        return res

    @classmethod
    def from_namespace(cls, name, namespace):
        """
        Create a new result from an existing namespace

        :param name: the result name
        :type name: str

        :param namespace: the namespace to use
        :type namespace: namespace
        """
        d = vars(namespace)
        cls(name, dictionary=d)

    def save(self, directory=None):
        """
        Save the result to disk. Uses :python:`torch.save` internally.

        :param directory: the directory, where to save the result. Set to :python:`None`, if the result already has a path and you wish to overwrite,
        default to :python:`None`. Note that you will have to specify a path on every first save.
        :type directory: Union[str, os.PathLike]
        """
        if directory:
            save_at = os.path.join(directory, self.name + ".result")
        else:
            save_at = self.path
        if save_at is None:
            raise ValueError(
                "The result has not been assigend a path yet, so you have to specify a directory where to save it"
            )
        torch.save(self.dictionary, save_at)

    @classmethod
    def load(cls, path):
        """
        Load a result from disk

        :param path: the path to a result file
        :type str:

        Some things you should know about this method:
        - stored scalar lists are converted to numpy arrays on load
        - internally it uses :python:`torch.load`

        :return: the result
        """
        path = Path(path)
        assert path.exists() and path.is_file() and path.suffix == ".result"
        dictionary = torch.load(path)
        name = path.stem
        res = cls(name, dictionary=dictionary, path=path)
        for key in res:
            if isinstance(res[key], list) and key != "tags":
                try:
                    res[key] = np.array(res[key])
                except:
                    logging.warning("Unable to convert list %s to numpy" % key)
        return res

    def store_scalar(self, value, key):
        """
        Store a scalar, or list/iterable of scalars associated with some key, i.e. name / string identifier.

        :param value: The value to store
        :type value: Union[bool, int, float, Iterable[Union[bool, int, float]]]

        :param key: The key under which the scalar is stored
        :type key: str

        If the key is new, a list entry in the result dictionary is associated with it,
        otherwise the scalar(s) is (are) appended to the key's list.
        """
        if not hasattr(value, "__iter__"):
            value = [value]
        if key in self.keys():
            self[key].extend(value)
        else:
            self[key] = list(value)

    def store_array(self, value, key):
        """
        Similar to :func:`~Result.store_scalar`, but store lists of values, without flatting them into
        one dimension. After loading this list, it will be a 2d numpy :type:numpy.ndarray.

        :param value: The array to store
        :type value: Union[List[Any], numpy.ndarray]

        :param key: The key under which the array is stored
        :type key: str
        """
        value = np.array(value)
        if key in self.keys():
            self[key].append(value)
        else:
            self[key] = [value]

    def plot_scalar(self, key, smoothing=50, show=True, ax=None):
        """
        Plot the array of scalars stored under a specific key

        :param key: the scalars key
        :type key: str

        :param smoothing: Size of a smoothing window applied to the scalars before plotting, defaults to 50
        :type smoothing: int, optional

        :param show: Whether to immediately show the plot, i.e. call :python:`plt.show`, defaults to True
        :type show: bool, optional

        :param ax: An axis to to plot on, defaults to None
        :type ax: matplotlib.axis, optional
        """
        x = util._moving_average(self[key], smoothing)
        if not ax:
            plt.plot(x, label=key)
            if show:
                plt.legend()
                plt.show()
        else:
            ax.plot(x)
