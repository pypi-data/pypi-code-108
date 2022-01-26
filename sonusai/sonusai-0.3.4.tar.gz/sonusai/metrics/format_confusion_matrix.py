from typing import List

import numpy as np


def format_confusion_matrix(cm: np.ndarray, labels: List[str] = None) -> str:
    # print confusion matrix from float variable cm and optional labels list
    result = '{}\n'.format(cm.astype(int))
    return result
