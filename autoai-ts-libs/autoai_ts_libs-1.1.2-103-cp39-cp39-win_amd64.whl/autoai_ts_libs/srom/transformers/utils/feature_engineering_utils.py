import numpy as np
import pandas as pd
from autoai_ts_libs.utils.messages.messages import Messages

def check_single_dimensional_array(x):
    """
    Check if input is single dimensional array.
    Parameters:
        x (numpy array, required): array of numbers.
    Return:
        return array or exception.
    """
    if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
        x = x.to_numpy()
    if not isinstance(x, np.ndarray):
        raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0019E'))
    if x.ndim > 1:
        raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0020E'))
    return x


def remove_nan_single_dimensional_array(x):
    """
    remove nan from single dimensional array.
    Parameters:
        x (numpy array, required): array of numbers.
    Return:
        return array.
    """
    return x[~np.isnan(x)]


def remove_zero_single_dimensional_array(x):
    """
    remove zero from single dimensional array.
    Parameters:
        x (numpy array, required): array of numbers.
    Return:
        return array.
    """
    return x[x != 0]