from collections import namedtuple
import torch
from typing import Union


def confusion_matrix_1D_input(y: torch.LongTensor, yhat: torch.LongTensor, num_classes=None) -> torch.Tensor:
    assert not isinstance(y, (torch.FloatTensor, torch.cuda.FloatTensor)), 'y or yhat cannot have float values'
    assert not isinstance(yhat, (torch.FloatTensor, torch.cuda.FloatTensor)), 'y or yhat cannot have float values'
    if num_classes is None:
        num_classes = y.max()
    return torch.sparse_coo_tensor(
        torch.stack([y, yhat]),
        torch.ones(yhat.numel(), device=y.device),
        size=(num_classes, num_classes)).to_dense()


def confusion_matrix_binary_soft_assignment(
        y: Union[torch.FloatTensor,torch.LongTensor],
        yhat: Union[torch.FloatTensor,torch.LongTensor]):
    """
    Create a binary confusion matrix given 1d inputs, where the inputs are
    assumed to be probabilities of the (positive) class with index value 1.

    Performs a soft assignment of the confusion matrix.  It is useful for
    binary classification with label noise, or less commonly when the predicted
    probabilities are considered as soft assignment.  Here's an example input
    and output:

        >>> y = [.7]
        >>> yhat = [.2]
        >>> confusion_matrix(y, yhat, 2)
            [[(1-.7) * (1-.2) , (1-.7) * .2]
             [(.7    * (1-.2) , .7     * .2]]

    """

    # special case of 1D probability vectors
    assert (y.max() <= 1).all() and (y.min() >= 0).all()
    assert (yhat.max() <= 1).all() and (yhat.min() >= 0).all()

    yhat = torch.stack([1-yhat, yhat]).T.float()
    y = torch.stack([1-y, y]).T.float()
    return confusion_matrix_2D_input(y=y, yhat=yhat)


def confusion_matrix_2D_input(y: torch.Tensor, yhat: torch.Tensor, normalize_y=False) -> torch.Tensor:
    """
    Output a confusion matrix from 2D inputs.

    Inputs are assumed either both LongTensor or both FloatTensor.  In the
    LongTensor setting, the columns of input arrays y and yhat are class index
    and the rows correspond to different (minibatch) samples.  In FloatTensor
    setting, read below to understand better what you're doing.

    How: Compute the outer product `y y_{hat}^T` for
    each of the `n` samples and sum the resulting matrices.  In other words,
    each row is a weighted sum of the yhat row vector with the scalar weight
    y_i, so we have a row of the confusion matrix defined as (yhat * y_i).

    This function generalizes a confusion matrix, because the ground truth `y`
    values are free to be fractions, multi-label and do not need to sum to 1.
    The trade-off of this generalized design is that y and yhat are never
    1-D vectors, like they are in the sklearn method (e.g. for binary
    classification, both y and yhat have two columns).

    :y:  (n,c) matrix of true values (e.g. if multi-class, each row is one-hot).
        In general, it doesn't make sense if y has negative values.
        e.g. for binary classification, set c=2.
    :yhat:  (n,c) matrix of predicted values.  Note: All `c` classes should
        have the same bounds (ie they are all logits).
        e.g. `yhat = softmax(model(x))`
        or a multi-class setting: `yhat = model(x).argmax(1)`
    :normalize_y:  If True, ensure the ground truth labels (each row of `y`) is
        a probability distribution (sums to 1).  If False, y is not normalized.
        False is useful if different samples have different weights (Assumes the
        sum of a row of y never equals zero.)

    :returns: an (c,c) confusion matrix.
    """
    # --> convert each row of y into a probability distribution
    if normalize_y:
        w = y / y.sum(1, keepdims=True)
    else:
        w = y
    # --> compute outer product w yhat^T for each of the n samples.  This gives
    # a confusion matrix for each sample.  Sum the matrices.
    return torch.einsum('nm,no->mo', w, yhat)


def confusion_matrix(y: torch.Tensor, yhat: torch.Tensor, num_classes:int
                     ) -> torch.Tensor:
    """
    A Confusion Matrix enables performance evaluation of a classifier model's
    predictions.  This function works with multi-class or multi-label data, 1D
    input vectors or 2-D inputs.  This class generalizes the confusion matrix,
    so be careful to give inputs of correct type.  To match
    `sklearn.metrics.confusion_matrix`, just ensure that `y` and `yhat` are
    integer type rather than float.  Check your result matches expectation.

    Each row index corresponds to a ground truth class.
    Each column index corresponds to predicted class.

    Standard example: Binary classification, where class "1" is positive, the
    output confusion matrix is:

        | TN | FP |
        | FN | TP |

        where "T" and "F" means true or false, "P" and "N" mean predicted
        positive or predicted negative

    Regarding the inputs:
        :y: ground truth tensor, shape is 1D or 2D.
        :yhat: prediction tensor, shape is 1D or 2D.

        If 1-D input tensor:
            - type must be either
              - LongTensor containing class index (i.e. This is the default
                supported case in sklearn for multi-class setting)
              - FloatTensor with probability of positive class is also allowed,
                but only when num_classes=2.  See "Special Case" section below.

            - The 1-D inputs force multi-class (one-hot) semantics, and is more
            or less the canonical setting.
            - Each value of the 1D vectors identifies a class in the
            confusion matrix by its row index or column index, for `y` and
            `yhat` respectively.

            ** Special Case:  Also support 1D floats when num_classes=2
              - In this case, assume that values are probabilities of
              (positive) class that is identified in the confusion matrix with
              index 1.  Performs a soft assignment of the confusion matrix.  It
              is useful for binary classification with label noise, or less
              commonly when the predicted probabilities are considered as
              soft assignment.  Here's an example input and output:

                >>> y = [.7]
                >>> yhat = [.2]
                >>> confusion_matrix(y, yhat, 2)
                    [[(1-.7) * (1-.2) , (1-.7) * .2]
                     [(.7    * (1-.2) , .7     * .2]]

        If 2-D input tensor:
            - Must be a LongTensor
            - Passing 2-D (n,c) inputs is better suited for multi-label
            data or uncertain ground truth labels or weights over samples.
              - `n` is the number of (minibatch) samples
              - `c` is the number of classes
            - If only one input is 2-D, the other is converted to 2-D.

        - Try to gracefully handle some funky shapes, such as (n,c,1,1) or (n,1)

        :returns: (c,c) tensor, where c is the number of classes.
    """
    # --> convert to 1d input if possible.  e.g. if shape is (n,1,1,1...)
    yhat = yhat.reshape(*yhat.shape[:2])
    y = y.reshape(*y.shape[:2])
    try: y = y.squeeze(1)
    except IndexError: pass
    try: yhat = yhat.squeeze(1)
    except IndexError: pass

    if 1 == yhat.ndim == y.ndim:
        if any(isinstance(x, (torch.FloatTensor, torch.cuda.FloatTensor))
               for x in [y, yhat]):
            assert num_classes == 2
            # special case for 1D probability vectors
            return confusion_matrix_binary_soft_assignment(y=y, yhat=yhat)
        else:
            # dispatch the function with 1D integer inputs
            return confusion_matrix_1D_input(y, yhat, num_classes)
    else:
        # dispatch the 2-D inputs function
        # --> but first, promote a 1D input to 2D if it exists
        if y.ndim == 1:
            y = _confusion_matrix_convert_2d_shape(y, num_classes)
        elif yhat.ndim == 1:
            yhat = _confusion_matrix_convert_2d_shape(yhat, num_classes)
        ret = confusion_matrix_2D_input(y, yhat)
        assert ret.shape == (num_classes, num_classes), "sanity check"
        return ret


def _confusion_matrix_convert_2d_shape(arr, num_classes):
    assert not isinstance(arr, (torch.FloatTensor, torch.cuda.FloatTensor))
    arr = torch.eye(num_classes, dtype=arr.dtype, device=arr.device)[arr]
    assert arr.shape[1] == num_classes, 'sanity check'
    assert arr.ndim == 2, 'sanity check'
    return arr


def accuracy(cm):
    return cm.trace() / cm.sum()


def balanced_accuracy(cm):
    """
    Average of recall:
        balanced_acc = .5 * (recall_pos + recall_neg)
        where
            recall_pos = TP / (TP + FN)
            recall_neg = TN / (TN + FP)

    Args:
        cm: Binary confusion matrix like this:
            | TN | FP |
            | FN | TP |

    Returns:
        scalar precision score
    """
    return recall(cm, 'both').mean()


def matthews_correlation_coeff(cm):
    """
    Implementation of the R_k coefficient applied to a confusion matrix is
    matthew's correlation coefficient.
    Original implementation here:  http://rk.kvl.dk/software/rkorrC
    Section 2.3 of the Gorodkin paper.  https://www.ncbi.nlm.nih.gov/pubmed/15556477?dopt=Abstract
    """
    cm = cm.float()
    N = cm.sum()
    rowcol_sumprod = (cm@cm).sum()
    rowrow_sumprod = (cm@cm.T).sum()
    colcol_sumprod = (cm.T@cm).sum()
    cov_xy = N*cm.trace() - rowcol_sumprod
    cov_xx = N**2 - rowrow_sumprod
    cov_yy = N**2 - colcol_sumprod
    Rk = cov_xy / torch.sqrt(cov_xx)/torch.sqrt(cov_yy)
    return Rk


def precision(cm):
    """
    Precision: of all predicted positive samples, what fraction was correct?

        precision = TP / (TP + FP)

    Args:
        cm: Binary confusion matrix like this:
            | TN | FP |
            | FN | TP |

    Returns:
        scalar precision score
    """
    rv = cm.diag() / cm.sum(0)
    rv[torch.isnan(rv)]=0
    return rv[1]


def recall(cm, mode='pos'):
    """
    Recall:  What fraction of ground truth labels was correct?

    Of all ground truth positive samples, what fraction was predicted positive?
        sensitivity = recall_pos = TP / (TP + FN)

    Similarly, of all ground truth negatives, what fraction was predicted negative?
        specificity = recall_neg = TP / (TP + FN)

    The denominators of above Eqtns are the row sums of the binary confusion matrix.

    Args:
        cm: Binary confusion matrix like this:
            | TN | FP |
            | FN | TP |
        mode:  Either "pos" or "neg" or "both"

    Returns:
        scalar precision score
    """
    rv = cm.diag() / cm.sum(1)
    rv[torch.isnan(rv)]=0
    if mode == 'pos': return rv[1]
    elif mode == 'neg': return rv[1]
    elif mode == 'both': return rv
    else: raise NotImplementedError(f'recall: unrecognized mode: {mode}')


def f1_score(cm, beta=1):
    p = precision(cm)
    r = recall(cm)
    b = beta**2
    return (1+b) * p*r / ( b * (p+r))


def distance_correlation(x:torch.Tensor, y:torch.Tensor=None):
    """
    Distance Correlation measures how independent two samples are, with values
    in [0, 1], and with zero when the two samples are independent.
    Distance variance measures how close to identical a set of observations are.
    Inputs:
        :x: Tensor of shape (..., N, F_x).  N observations, F_x measurements.
        :y: Tensor of shape (..., N, F_y).  N observeations, F_y measurements,
            where F_x and F_y don't have to be equal.
            If not given, compute only the distance variance of x.
    Output:
        :ret: namedtuple of shape (dcor, dcov, dvar_x, dvar_y) where each term is either None or a Tensor of shape (..., N).
          dcor: distance correlation between x and y
          dcov: distance covariance
          dvar_x: distance variance of x
          dvar_y: distance variance of y
    ---
    Original paper:
        Szekely, G.J., Rizzo, M.L., and Bakirov, N.K. (2007) “Measuring and testing dependence by correlation of distances”. Annals of Statistics, Vol. 35 No. 6, pp. 2769-2794.
    Manually tested against this reference implementation for numpy arrays:
        https://www.statsmodels.org/stable/generated/statsmodels.stats.dist_dependence_measures.distance_correlation.html
    """
    N, _ = x.shape[-2:]
    center = lambda arr: (
        arr - arr.mean(-2, keepdim=True)
            - arr.mean(-1, keepdim=True)
            + arr.mean((-1, -2), keepdim=True))
    # get centered pairwise distances
    x = center(torch.cdist(x, x, 2))
    dvar_x = torch.sqrt((x*x).mean((-1, -2), keepdim=True))
    if y is not None:
        assert y.shape[-2] == x.shape[-2]
        y = center(torch.cdist(y, y, 2))
        # compute relevant statistics
        dcov = torch.sqrt((x * y).mean((-1, -2), keepdim=True))
        dvar_y = torch.sqrt((y*y).mean((-1, -2), keepdim=True))
        dcor = dcov / torch.sqrt(dvar_x * dvar_y)
        [x.squeeze_(-1).squeeze_(-1) for x in [dcov, dvar_y, dcor]]
    else:
        dcov, dvar_y, dcor = [None]*3
    dvar_x.squeeze_(-1).squeeze_(-1)
    return namedtuple(
        'DistanceCorrelation', ['dcor', 'dcov', 'dvar_x', 'dvar_y'])(
            dcor, dcov, dvar_x, dvar_y)


def test_distance_correlation():
    x = torch.rand((2, 2, 3, 4))
    y = torch.rand((2, 2, 3, 4))
    actual = distance_correlation(x, y).dcor
    from statsmodels.stats.dist_dependence_measures import distance_correlation as smdc
    xnp, ynp = x.numpy(), y.numpy()
    expected = torch.tensor([
        [smdc(xnp[0,0], ynp[0,0]), smdc(xnp[0,1], ynp[0,1])],
        [smdc(xnp[1,0], ynp[1,0]), smdc(xnp[1,1], ynp[1,1])]], dtype=torch.float)
    assert torch.allclose(actual, expected)


if __name__ == "__main__":
    test_distance_correlation()
