"""Utilities for creating batch transforms."""

from typing import List, MutableMapping, Sequence, Union

import torch


BatchType = MutableMapping[str, torch.Tensor]


def make_int_list(nums: Union[int, Sequence[int]]) -> List[int]:
    """Convert an int or sequence of ints to a list of ints.

    Parameters
    ----------
    nums: Union[int, Sequence[int]]
        An int or sequence of ints

    Returns
    -------
    List[int]
    """
    if isinstance(nums, int):
        return [nums]
    else:
        return list(nums)


def within_range(x: Sequence[int], lb: float, ub: float = float("inf")) -> bool:
    """Do all values of x lie within [lb, ub].

    Parameters
    ----------
    x: Sequence[int]
        The list of ints to be checked
    lb: float
        A lower bound (inclusive)
    ub: float, optional
        An upper bound, inclusive (defaults to inf)

    Returns
    -------
    bool
    """
    return all(lb <= x_ <= ub for x_ in x)
