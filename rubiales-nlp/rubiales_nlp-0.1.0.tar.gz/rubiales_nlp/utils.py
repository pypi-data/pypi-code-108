'''
Author: Alberto Rubiales Borrego
Mail: al.rubiales.b@gmail.com
Github: arubiales
Created Date: 24-Jan-2022
-----
Last Modified: 24-Jan-2022
Modified By: Alberto Rubiales Borrego
-----
'''
from typing import Iterable, Callable
from tqdm import tqdm

def tqdm_manager(iterator: Iterable, func: Callable, verbose: bool):
    """
    Manage if it will be a tqdm or not

    Arguments
    ----------
    iterator: Iterator
        An iterator to iterate

    func: Callable
        A function to apply to every item in the `iterator`

    verbose: Bool
        If tqdm is going to be applyed (True) or not (False)

    Returns
    ---------
        The results of apply the function to every item with the verbose selected
    """
    if verbose:
        return [func(item) for item in tqdm(iterator)]
    return [func(item) for item in iterator]
