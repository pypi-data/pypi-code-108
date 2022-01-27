import numpy as np

from sonusai import logger


def calculate_metrics(cmall: np.ndarray, binary_mode: bool = True) -> (np.ndarray, np.ndarray, np.ndarray):
    # Calculates metrics from a confusion matrix of num_classes x num_classes or
    # sets of cm S1 x S2 x ... x num_classes x num_classes where the sum is taken over
    # all the other dimensions and metrics are calculated on this sum.
    #
    # binary_mode sets binary mode where if True and num_classes=2 then only the last (-1)
    # dimension of metrics is returned (the positive metrics), i.e. a 1x10 array.
    #
    # Returns:
    # metrics  num_classes x 12            [ACC, TPR, PPV, TNR, FPR, HITFA, F1, MCC, NT, PT, TP, FP]
    # mcm      num_classes x 2 x 2
    # cmsum    num_classes x num_classes   Sum of all sum counts

    if cmall.shape[-1] != cmall.shape[-2]:
        logger.error('Confusion matrix must be a square matrix.')
        exit()

    num_classes = cmall.shape[-1]
    ndimsum = np.ndim(cmall) - 2
    if ndimsum == 0:
        cmsum = cmall
    else:
        dsi = tuple([i for i in range(0, cmall.ndim - 2)])
        cmsum = np.sum(cmall, dsi)  # sum over all dims except -2,-1

    metrics = np.zeros((num_classes, 12))
    mcm = np.zeros((num_classes, 2, 2))
    total_count = np.sum(np.sum(cmsum))
    eps = np.finfo(float).eps

    for nci in range(num_classes):
        mcm[nci, 1, 1] = cmsum[nci, nci]  # TP True positive
        mcm[nci, 1, 0] = np.sum(cmsum[nci, :]) - mcm[nci, 1, 1]  # FN False negative = true but predicted negative
        mcm[nci, 0, 1] = np.sum(cmsum[:, nci]) - mcm[nci, 1, 1]  # FP False positive
        mcm[nci, 0, 0] = total_count - np.sum(mcm[nci, :, :])  # TN True negative = false and predicted negative
        # True negative
        TN = mcm[nci, 0, 0]
        # False positive
        FP = mcm[nci, 0, 1]
        # False negative
        FN = mcm[nci, 1, 0]
        # True positive
        TP = mcm[nci, 1, 1]
        # Accuracy
        ACC = (TP + TN) / (TP + TN + FP + FN + eps)
        # True positive rate, sensitivity, recall, hit rate (note eps in numerator)
        # When ``true positive + false negative == 0``, recall is undefined, set to 0
        TPR = (TP) / (TP + FN + eps)
        # Precision, positive predictive value
        # When ``true positive + false positive == 0``, precision is undefined, set to 0
        PPV = TP / (TP + FP + eps)
        # Specificity i.e., selectivity, or true negative rate
        TNR = TN / (TN + FP + eps)
        # False positive rate = 1-specificity, roc x-axis
        FPR = FP / (TN + FP + eps)
        # HitFA used by some separation research, close match to MCC
        HITFA = TPR - FPR
        # F1 harmonic mean of precision, recall = 2*PPV*TPR / (PPV + TPR)
        F1 = 2 * TP / (2 * TP + FP + FN + eps)
        # Matthew correlation coefficient
        MCC = (TP * TN - FP * FN) / (np.sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN)) + eps)
        # Num. negatives total (truth), also = TN+FP denom of FPR
        NT = sum(mcm[nci, 0, :])
        # Num. positives total (truth), also = FN+TP denom of TPR, precision
        PT = sum(mcm[nci, 1, :])
        metrics[nci] = [ACC, TPR, PPV, TNR, FPR, HITFA, F1, MCC, NT, PT, TP, FP]

    if num_classes == 2 and binary_mode:
        # If binary, drop dim0 stats which are redundant
        mcm = mcm[1:, :, :]
        metrics = metrics[1:, :]

    return metrics, mcm, cmsum
