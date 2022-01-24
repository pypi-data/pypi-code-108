from abc import ABC, abstractmethod

import numpy as np


def getloss(name):
    if name == "Rmse":
        return Rmse()
    if name == "Mae":
        return Mae()
    if name == "TrimmedRmse":
        return TrimmedRmse()
    if name == "AUC":
        return AUC()
    if name == "Accuracy":
        return Accuracy()
    if name == "MeanPrediction":
        return MeanPrediction()
    if name == "MeanActual":
        return MeanActual()
    else:
        raise NotImplementedError


class Loss(ABC):
    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    def greater_is_better(self):
        return False

    @property
    def convert_to_np_arrays_first(self):
        return False

    def metric(self, pred, y):
        if self.convert_to_np_arrays_first:
            return self._metric(
                np.array(pred, dtype=pred.dtype), np.array(y, dtype=y.dtype)
            )
        else:
            return self._metric(pred, y)

    @abstractmethod
    def _metric(self, pred, y):
        raise NotImplementedError


class Rmse(Loss):
    """Implements RMSE loss"""

    name = "Root Mean Squared Error"
    convert_to_np_arrays_first = True

    def _metric(self, pred, y):
        return np.sqrt(np.mean((y - pred) ** 2))


class Mae(Loss):
    name = "Mean Absolute Error"
    convert_to_np_arrays_first = True

    def _metric(self, pred, y):
        return np.mean(np.abs(y - pred))


class TrimmedRmse(Loss):
    name = "Trimmed RMSE"
    convert_to_np_arrays_first = True

    def _metric(self, pred, y):
        index = trim_outliers(y, return_index=True)
        trmse = np.sqrt(np.mean((y[index] - pred[index]) ** 2))
        return trmse


class MeanPrediction(Loss):
    name = "Mean Prediction"

    def _metric(self, pred, y):
        return np.mean(pred)


class MeanActual(Loss):
    name = "Mean Actual"

    def _metric(self, pred, y):
        return np.mean(y)


def count_false(a):
    """Count number of False (zero) occurences in array"""
    return np.size(a) - np.count_nonzero(a)


def count_true(a):
    """Count number of True (non-zero) occurences in array"""
    return np.count_nonzero(a)


class AUC(Loss):
    name = "AUC"
    greater_is_better = True
    convert_to_np_arrays_first = True

    def _metric(self, pred, y):
        if len(np.unique(y)) != 2:
            raise ValueError("y must consist of two classes (True/False)")
        cutoffs = np.unique(np.append(pred, [-np.inf, np.inf]))
        cutoffs = cutoffs[::-1]  # reverse order
        y = np.array(y)
        pred = np.array(pred)
        tpr = [np.sum((pred > x) & y) / count_true(y) for x in cutoffs]
        fpr = [np.sum((pred > x) & ~y) / count_false(y) for x in cutoffs]
        auc = np.trapz(y=tpr, x=fpr)
        return auc


class Accuracy(Loss):
    name = "Accuracy"
    greater_is_better = True
    threshold = 0.5
    convert_to_np_arrays_first = True

    def _metric(self, pred, y):
        tpr = np.mean((pred > self.threshold) & y)  # true positive rate
        tnr = np.mean((pred < self.threshold) & ~y)  # true negative rate
        accuracy = tpr + tnr
        return accuracy


def trim_outliers(a, lb=0.005, ub=0.995, return_index=False):
    """Drop values at the edges of a distribution"""
    a = np.array(a)
    lb = np.quantile(a, q=lb)
    ub = np.quantile(a, q=ub)
    index = (a >= lb) & (a <= ub)
    if return_index:
        return index
    elif not return_index:
        return a[index]
    else:
        raise ValueError("return_index must only accepts True/False")
