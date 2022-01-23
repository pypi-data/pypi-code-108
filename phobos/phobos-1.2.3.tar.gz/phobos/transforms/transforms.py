import logging
import numpy as np

from albumentations.core.transforms_interface import ImageOnlyTransform


class Normalize(ImageOnlyTransform):
    r"""Performs Normalization on the image
    
    Normalization is applied by the formula: 
    
    .. math:: img = \frac{img - mean}{std}

    Parameters
    ----------
    mean : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        channel mean values
    std : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        channel std values
    max_pixel_value : `float <https://docs.python.org/3/library/functions.html#float>`_
        maximum possible pixel value

    Examples
    --------
    Create a Normalize instance

    >>> params = {
    ...     'mean': [0.2, 0.4, 0.6, 0.8, 1.0],
    ...     'std': [0.1, 0.1, 0.1, 0.1, 0.1]
    ... }
    >>> N = Normalize(**params)

    Apply normalize transform on a mock image

    >>> image = np.ones([64, 64, 5])
    >>> norm = N.apply(image)
    >>> norm[0, 0, :]
    array([8. , 6. , 4. , 2. , 0. ], dtype=float32)

    """    

    def __init__(self, mean=(0.485, 0.456, 0.406),
                 std=(0.229, 0.224, 0.225), always_apply=False, p=1.0):
        super(Normalize, self).__init__(always_apply, p)
        self.mean = np.array(mean, dtype=np.float32)
        self.std = np.array(std, dtype=np.float32)

    def apply(self, image, **params):
        logging.debug("Enter Normalize apply routine")
        denominator = np.reciprocal(self.std, dtype=np.float32)

        img = np.array(image, dtype=np.float32)
        img -= self.mean
        img *= denominator

        return img

    def get_transform_init_args_names(self):
        return ("mean", "std")


class MinMaxNormalize(ImageOnlyTransform):
    r"""Performs MinMax Normalization on the image.

    MinMax Normalization is applied by the formula :  
    
    .. math:: img = \frac{img - min}{max - min}

    Parameters
    ----------
    min : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        band wise minimum values
    max : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        band wise maximum values

    Examples
    --------
    Create a MinMaxNormalize instance

    >>> params = {
    ...     'min': [0.1, 0.3, 0.1],
    ...     'max': [0.9, 1.1, 0.9]
    ... }
    >>> N = MinMaxNormalize(**params)

    Apply minmax normalize transform on a mock image

    >>> image = np.ones([64, 64, 3])
    >>> norm = N.apply(image)
    >>> norm[0, 0, :]
    array([1.125, 0.875, 1.125],dtype=float32) 

    """    

    def __init__(self, min, max, always_apply=False, p=1.0):
        super(MinMaxNormalize, self).__init__(always_apply, p)
        self.min = np.array(min, dtype=np.float32)
        self.max = np.array(max, dtype=np.float32)

    def apply(self, image, **params):
        logging.debug("Enter MinMax Normalize apply routine")
        denominator = np.reciprocal(self.max - self.min, dtype=np.float32)

        img = np.array(image, dtype=np.float32)
        img -= self.min
        img *= denominator

        return img

    def get_transform_init_args_names(self):
        return ("min", "max")
