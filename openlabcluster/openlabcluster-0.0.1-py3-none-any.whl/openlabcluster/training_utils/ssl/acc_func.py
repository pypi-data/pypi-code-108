import numpy as np

from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from collections import Counter
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import adjusted_rand_score
from sklearn import svm
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import recall_score
from sklearn.neighbors import KNeighborsClassifier
import torch
def acc(y_true, y_pred):
    """
    Calculate clustering accuracy. Require scikit-learn installed

    # Arguments
        y: true labels, numpy.array with shape `(n_samples,)`
        y_pred: predicted labels, numpy.array with shape `(n_samples,)`

    # Return
        accuracy, in [0,1]
    """
    y_true = y_true.astype(np.int64)
    assert y_pred.size == y_true.size
    D = max(y_pred.max(), y_true.max()) + 1
    w = np.zeros((D, D), dtype=np.int64)
    for i in range(y_pred.size):
        w[y_pred[i], y_true[i]] += 1
    # ind = linear_assignment(w.max() - w)
    ind = linear_sum_assignment(w.max() - w)
    ind = np.asarray(ind)
    ind = np.transpose(ind)
    return sum([w[i, j] for i, j in ind]) * 1.0 / y_pred.size


def topk_accuracy(output, target, topk=(1,)):
    """Computes the precision@k for the specified values of k"""
    maxk = max(topk)
    target = torch.tensor(target)
    batch_size = target.size(0)

    _, pred = output.topk(maxk, 1, True, True)
    pred = pred.t().cpu()
    correct = pred.eq(target.view(1, -1).expand_as(pred)).contiguous()

    res = []
    for k in topk:
        correct_k = correct[:k].view(-1).float().sum(0, keepdim=True)
        res.append(correct_k.mul_(100.0 / batch_size))
    return res

def knn(data_train, data_test, label_train, label_test, nn=1):
    label_train = np.asarray(label_train)
    label_test = np.asarray(label_test)

    Xtr_Norm = preprocessing.normalize(data_train)
    Xte_Norm = preprocessing.normalize(data_test)

    knn = KNeighborsClassifier(n_neighbors=nn,
                               metric='cosine')  # , metric='cosine'#'mahalanobis', metric_params={'V': np.cov(data_train)})
    knn.fit(Xtr_Norm, label_train)
    pred = knn.predict(Xte_Norm)
    acc = accuracy_score(pred, label_test)
    return acc