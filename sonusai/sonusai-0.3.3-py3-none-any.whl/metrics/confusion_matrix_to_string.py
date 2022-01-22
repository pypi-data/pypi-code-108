import numpy as np


def confusion_matrix_to_string(cm: np.ndarray, normalize: bool = False) -> str:
    # Convert confusion matrix to string
    # If normalize is False (default) then print standard non-normalized confusion matrix,
    # else print normalized confusion matrix
    assert cm.ndim == 2, 'Confusion matrix must be two-dimensional.'
    assert cm.shape[0] == cm.shape[1], 'Confusion matrix must be square.'

    num_classes = np.shape(cm)[0]
    row_count = np.sum(cm, 1)
    total_count = np.sum(row_count)

    result = ''
    if not normalize:
        result += 'Confusion matrix with num_classes, total count: {},{}:\n'.format(num_classes, total_count)
        with np.printoptions(suppress=True):
            result += '{}\n'.format(cm.astype(int))
    else:
        eps = np.finfo(float).eps
        norm_val = (np.tile(np.reshape(row_count, (num_classes, 1)), (1, num_classes)) + eps)
        ncm = cm / norm_val  # element by element
        result += 'Normalized confusion matrix (%) with num_classes, total count: {},{}:\n'.format(num_classes,
                                                                                                   total_count)
        with np.printoptions(precision=2, suppress=True):
            result += '{}\n'.format(np.round(ncm * 100, 0).astype(int))

    return result
