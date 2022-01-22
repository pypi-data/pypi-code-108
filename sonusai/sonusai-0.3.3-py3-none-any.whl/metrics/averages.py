import numpy as np


def averages(metrics: np.ndarray) -> np.ndarray:
    # Compute averages for several averaging methods over classes.
    # For binary these have no meaning macro-avg == statistics of pos. class
    # mavg[0,:]  macro-avg  [PPV, TPR, F1, FPR, ACC, TPSUM]
    # mavg[1,:]  micro-avg  [PPV, TPR, F1, FPR, ACC, TPSUM]  # Note, PPV=TPR=F1=ACC
    # mavg[2,:]  weight-avg [PPV, TPR, F1, FPR, ACC, TPSUM]
    assert metrics.ndim == 2, 'Metrics must be two-dimensional.'
    assert metrics.shape[1] == 12, 'Metrics must have 12 indices.'

    eps = np.finfo(float).eps
    num_classes = np.shape(metrics)[0]
    s = np.sum(metrics[:, 9].astype(int))  # support = sum (true pos total = FN+TP ) over classes

    mavg = np.zeros((3, 6), dtype=np.single)

    # macro average
    mavg[0, :] = [np.mean(metrics[:, 2]), np.mean(metrics[:, 1]), np.mean(metrics[:, 6]),
                  np.mean(metrics[:, 4]), np.mean(metrics[:, 0]), s]

    # micro average, micro-F1 = micro-precision = micro-recall = accuracy
    if num_classes > 1:
        tp_sum = np.sum(metrics[:, 10])  # TP all classes
        rm = tp_sum / (np.sum(metrics[:, 9]) + eps)  # micro mean PPV = TP / (PT=FN+TP)
        fp_sum = np.sum(metrics[:, 11])  # FP all classes
        fpm = fp_sum / (np.sum(metrics[:, 8]) + eps)  # micro mean FPR = FP / (NT=TN+FP)
        # pm  = tp_sum / (tp_sum + fp_sum + eps)      # micro mean TPR = TP / (TP+FP) (note: same as rm for micro-avg)
        mavg[1, :] = [rm, rm, rm, fpm, rm, s]  # specific format, last 3 are unique
        # weighted average TBD
        # mavg[2,:] =
    else:  # binary case, all are same
        mavg[1, :] = mavg[0, :]
        mavg[2, :] = mavg[0, :]

    return mavg
