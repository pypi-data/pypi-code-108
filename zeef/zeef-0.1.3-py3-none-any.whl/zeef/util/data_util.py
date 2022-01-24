import numpy as np


def flatten_data(data_x):
    """
    Convert the data to single dimension.
    @param data_x: the input data.
    @return: the flatten data in np.ndarray type.
    """
    data_x = np.array(data_x)
    shape = data_x.shape
    flat_x = data_x
    if len(shape) > 2:
        flat_x = np.reshape(data_x, (shape[0], np.product(shape[1:])))
    return flat_x
