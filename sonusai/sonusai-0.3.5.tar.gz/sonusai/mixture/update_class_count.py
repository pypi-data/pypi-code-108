from typing import List

import numpy as np


def update_class_count(total_class_count: List[int],
                       truth_index: List[int],
                       truth: np.ndarray,
                       class_weights_threshold: List[float]) -> (List[int], int):
    mixture_class_count = [0] * len(truth_index)
    for offset, cl in enumerate(truth_index):
        truth_sum = int(np.sum(truth[cl - 1, :] >= class_weights_threshold[cl - 1]))
        mixture_class_count[offset] = truth_sum
        total_class_count[cl - 1] += truth_sum

    return total_class_count, mixture_class_count
