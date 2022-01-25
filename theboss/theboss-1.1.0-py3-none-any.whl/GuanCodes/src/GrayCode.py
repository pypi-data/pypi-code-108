__author__ = "Tomasz Rybotycki"

"""
    The aim of this script is to provide a method returning the update indices for 
    Gray code iteration. The update indices makes sense in Gray code, as the only
    operation here is basically bit-flipping.
"""

from typing import List


def get_gray_code_update_indices(n: int) -> List[int]:
    """
        Computes and returns the update indices for Gray code iteration.
        :param n: The length of the code.
        :return: The list of indices to bit-flip during iteration.
    """
    if n <= 0:
        return []
    if n == 1:
        return [0]  # We index our tables from 0

    subproblem_update_indices = get_gray_code_update_indices(n - 1)
    update_indices = subproblem_update_indices.copy()
    update_indices.append(n - 1)
    update_indices.extend(subproblem_update_indices.__reversed__())
    return update_indices
