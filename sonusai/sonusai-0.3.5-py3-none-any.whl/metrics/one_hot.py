import numpy as np
from sklearn.metrics import confusion_matrix

from sonusai import logger
from sonusai.metrics import calculate_metrics


def one_hot(truth: np.ndarray,
            predict: np.ndarray,
            pthrmode: int = 0,
            num_classes: int = -1) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    # Calculates metrics from one-hot prediction and truth data where input
    # is one-hot probabilities for each class with size frames x num_classes or
    # frames x timesteps x num_classes.
    #
    # num_classes is inferred from truth dims by default (num_classes = -1).
    # Only set in case of binary 2-dimensional input frames x timesteps with timestep,
    # then must set num_classes = 1.
    #
    # returns metrics over all frames + timesteps:
    # mcm      num_classes x 2 x 2         multiclass confusion matrix count ove
    # metrics  num_classes x 10            [ACC, TPR, PPV, TNR, FPR, HITFA, F1, MCC, NT, PT, TP, FP]
    # cm, cmn: num_classes x num_classes   confusion matrix, normalized confusion matrix
    # rmse:    num_classes x 1             RMS error over all frames + timesteps

    if truth.shape != predict.shape:
        logger.error('Shape of truth and predict are not equal')
        exit()

    # truth, predict can be either frames x num_classes, or frames x timesteps x num_classes
    # in binary case, num_classes == 1 and dim may not exist
    if truth.ndim == 3 or (truth.ndim == 2 and num_classes == 1):  # flatten
        # frames = truth.shape[0]
        # timesteps = truth.shape[1]
        if truth.ndim == 2:
            num_classes = 1
        else:
            num_classes = truth.shape[2]

        truth = np.reshape(truth, (truth.shape[0] * truth.shape[1], truth.shape[2]))
        predict = np.reshape(predict, (predict.shape[0] * predict.shape[1], predict.shape[2]))
    else:
        # frames = truth.shape[0]
        # timesteps = 0
        if truth.ndim == 1:
            num_classes = 1
        else:
            num_classes = truth.shape[1]

    rmse = np.sqrt(np.mean(np.square(truth - predict), axis=0))

    if pthrmode == 0 and num_classes > 1:
        pthr = 0.5  # multiclass, single-label (argmax) or multilabel case default
    else:
        if num_classes == 1 and pthrmode == 0:
            pthr = 0.5  # binary case default >= 0.5 which is equiv to argmax()
        else:
            pthr = pthrmode  # any case using specified threshold

    # Convert continuous probabilities to binary via argmax() or threshold comparison
    # and create labels of int encoded (0:num_classes-1), and then equivalent one-hot
    if num_classes == 1:  # If binary
        binary_mode = True
        labels = ([i for i in range(0, 2)])  # int encoded 0,1
        plabel = np.int8(predict >= pthr)  # frames x 1, default 0.5 is equiv. to argmax()
        tlabel = np.int8(truth >= pthr)  # frames x 1
        predb = plabel
        truthb = tlabel
    else:
        binary_mode = False
        labels = ([i for i in range(0, num_classes)])  # int encoded 0,...,num_classes-1
        if pthrmode == 0:  # multiclass, use argmax (i.e. single label mutex)
            plabel = np.argmax(predict, axis=-1)  # frames x 1 labels
            tlabel = np.argmax(truth, axis=-1)  # frames x 1 labels
            predb = np.zeros(predict.shape, dtype=np.int8)  # frames x num_classes one-hot binary
            truthb = np.zeros(truth.shape, dtype=np.int8)  # frames x num_classes one-hot binary
            predb[np.arange(predb.shape[0]), plabel] = 1
            truthb[np.arange(truthb.shape[0]), tlabel] = 1
        else:  # multiclass prob threshold comparison (i.e. multi-label)
            plabel = np.int8(predict >= pthr)  # frames x num_classes multilabel one-hot decision
            tlabel = np.int8(truth >= pthr)  # frames x num_classes multilabel one-hot decision

    # Create num_classes x num_classes normalized confusion matrix
    cmn = confusion_matrix(tlabel, plabel, labels=labels, normalize='true')

    # Create num_classes x num_classes confusion matrix
    cm = confusion_matrix(tlabel, plabel, labels=labels)

    (metrics, mcm, _) = calculate_metrics(cm, binary_mode)

    return mcm, metrics, cm, cmn, rmse
