# TODO: Consider suggestions at https://stackoverflow.com/questions/35673895/type-hinting-annotation-pep-484-for-numpy-ndarray
# TODO: Ensure code follows style guide: https://numpydoc.readthedocs.io/en/latest/format.html
from numba import jit
import numpy as np
from scipy.stats import rankdata
import tqdm

def grade_entropy(X: np.ndarray) -> np.float64:
    '''
    Computes grade entropy for a strict product order
    on the row space points.

    A strict product order on embeddings of the real
    numbers gives a partial order. On a particular data
    set it may be desirable to quantify the extent to
    which there is a total order vs noorder at all.

    Under such an order, two points :math:`\\vec{x}, \\vec{y} \\in \\mathbb{R}^n`
    hold the relation :math:`\\vec{x} < \\vec{y}` if-and-only-if
    :math:`x_j < y_j\\ \\forall j \\in \\{1, \\cdots, n\\}`.

    This function computes

    .. math::
        H_g = \\frac{-\\sum_{i=1}^{m} p \\circ g(x_i) \\ln (p \\circ g(x_i))}{\\ln{m}}

    where :math:`p` is a probability distribution over the grades :math:`g`
    of the point :math:`x_i` among the indexed set of points :math:`i \\in \\{1, \\cdots, m\\}`
    according to a strict product order relation.

    Parameters
    ----------
    X : array-like
        An m x n data matrix.

    Returns
    -------
    entropy : np.float64
        Grade entropy of product order.

    References
    ----------
    .. [1] "Graded Poset.", https://en.wikipedia.org/wiki/Graded_poset
    .. [2] "Entropy (Information Theory).", https://en.wikipedia.org/wiki/Entropy_(information_theory)
    .. [3] "Partially Ordered Set.", https://en.wikipedia.org/wiki/Partially_ordered_set
    .. [4] "Partially Ordered Set.", https://mathworld.wolfram.com/PartiallyOrderedSet.html
    .. [5] "Product Order.", https://en.wikipedia.org/wiki/Product_order
    .. [6] "Ranked Poset.", https://en.wikipedia.org/wiki/Ranked_poset
    .. [7] "Total Order.", https://en.wikipedia.org/wiki/Total_order

    Examples
    --------
    >>> import numpy as np
    >>> data = np.arange(100).reshape(10,10)
    >>> grade_entropy(data)
    1.0

    .. warning::
        The underlying tqdm tool that achieves parallel processing will also print a progress bar. This printout can be needlessly obscure in certain environments such as IDLE. The progress bar should print normally from a BASH environment.

    '''
    P = np.zeros((X.shape[0], X.shape[0]))
    @jit(nopython=True, fastmath=True) # does fastmath actually improve speed?
    def grade(q):
        v = np.zeros(X.shape[0])
        for j in range(X.shape[0]):
            if np.all(X[j] < X[q]):
                v[j] += 1
        return v
    for i in tqdm.tqdm(range(X.shape[0])):
        P[:, i] = grade(i)
    bins, counts = np.unique(np.sum(P, axis=0), return_counts=True)
    probs = counts / np.sum(counts)
    entropy = np.sum(probs * np.log(probs)) / (np.log(1/np.sum(counts)))
    return entropy

def minkowski_deviation(x: np.ndarray, order=2) -> np.float64:
    '''
    Calculates the Minkowski deviation of order p.
    When the order = 2, it is the same as the standard
    deviation.

    This function estimates

    .. math::
        \\text{Dev}_p \\left[ X \\right] \\triangleq \\sqrt[p]{\\mathbb{E}\\left[ |X - \\mathbb{E}[X]|^p \\right]}

    Parameters
    ----------
    x : array-like.

    Returns
    -------
    result : np.float64

    See Also
    --------
    np.std : Standard deviation.

    References
    ----------
    .. [1] "Standard Deviation.", https://en.wikipedia.org/wiki/Standard_deviation

    Examples
    --------
    >>> import numpy as np
    >>> data = np.arange(10)
    >>> minkowski_deviation(data)
    5.338539126015656
    '''
    result = x - np.mean(x)
    result = np.abs(x)
    result = np.power(result, order)
    result = np.mean(result)
    result = np.power(result, 1 / order)
    return result

def reflective_correlation(X: np.ndarray) -> np.float64:
    '''
    Calculates the multilinear reflective correlation coefficient.
    When given an m x 2 data matrix, it is equivalent to the
    reflective correlation coefficient.

    This function estimates

    .. math::
        R_r \\left[ X_1, \\cdots, X_n \\right] = \\frac{\\mathbb{E} \\left[ \\prod_{j=1}^{n} X_j \\right]}{\\prod_{j=1}^{n} \\sqrt[n]{\\mathbb{E}\\left[ |X_n|^n \\right]}}

    Parameters
    ----------
    X : array-like
        The m x n data matrix.

    Returns
    -------
    r : np.float64
        Reflective correlation coefficient score.

    References
    ----------
    .. [1] "Reflective Correlation Coefficient.", https://en.wikipedia.org/wiki/Pearson_correlation_coefficient#Reflective_correlation_coefficient

    Examples
    ----------
    >>> import numpy as np
    >>> data = np.arange(100).reshape(10,10)
    >>> reflective_correlation(data)
    0.9995245464170066
    '''
    if X.dtype != np.float64:
        X = X.astype(np.float64)
    
    numerator = np.prod(X, axis=1)
    numerator = np.sum(numerator)
    denominator = np.abs(X)
    denominator = np.power(denominator, X.shape[1])
    denominator = np.sum(denominator, axis=0)
    denominator = np.prod(denominator)
    denominator = np.power(denominator, 1 / X.shape[1])
    r = numerator / denominator
    return r

def pearson_correlation(X: np.ndarray) -> np.float64:
    '''
    This function calculates the n-ary Pearson's r correlation
    coefficient. When given an m x 2 data matrix, it is equivalent
    to the Pearson's r correlation coefficient.

    This function estimates

    .. math::
        R_p \\left[ X_1, \\cdots, X_n \\right] = \\frac{\\mathbb{E} \\left[ \\prod_{j=1}^{n} \\left( X_j - \\mathbb{E}[X_j] \\right) \\right]}{\\prod_{j=1}^{n} \\sqrt[n]{\\mathbb{E}\\left[ |X_n- \\mathbb{E}[X_j]|^n \\right]}}

    Parameters
    ----------
    X : array-like
        An m x n data matrix.

    Returns
    -------
    r : np.float64
        The calculated Pearson r correlation coefficient.

    References
    ----------
       https://en.wikipedia.org/wiki/Pearson_correlation_coefficient

    Examples
    ----------
    >>> import numpy as np
    >>> data = np.arange(100).reshape(10,10)
    >>> pearson_correlation(data)
    0.9999999999999978
    '''
    transform = X - np.mean(X, axis=0)
    r = reflective_correlation(transform)
    return r

def circular_correlation(X: np.ndarray) -> np.float64:
    '''
    This function calculates the n-ary circular correlation
    coefficient. When given an m x 2 data matrix, it is equivalent
    to the circular correlation coefficient.

    This function estimates

    .. math::
        R_c \\left[ X_1, \\cdots, X_n \\right] = \\frac{\\mathbb{E} \\left[ \\prod_{j=1}^{n} \\sin \\left( X_j - \\mathbb{E}[X_j] \\right) \\right]}{\\prod_{j=1}^{n} \\sqrt[n]{\\mathbb{E}\\left[ |\\sin \\left( X_j - \\mathbb{E}[X_j] \\right)|^n \\right]}}
    
    Parameters
    ----------
        X (array-like): m x n data matrix

    Returns
    -------
        r : np.float64
            Circular correlation coefficient.

    References
    ----------
    .. [1] "Circular Correlation Coefficient", https://en.wikipedia.org/wiki/Pearson_correlation_coefficient#Circular_correlation_coefficient

    Examples
    ----------
    >>> import numpy as np
    >>> data = np.arange(100).reshape(10,10)
    >>> circular_correlation(data)
    0.9999999999999999
    '''
    transform = X - np.mean(X, axis=0)
    transform = np.sin(transform)
    r = reflective_correlation(transform)
    return r

def spearman_correlation(X: np.ndarray, method='average') -> np.float64:
    '''
    This function calculates the n-ary Spearman correlation
    coefficient. When given an m x 2 data matrix, it is equivalent
    to the Spearman's Rho correlation coefficient.

    This function estimates

    .. math::
        R_c \\left[ X_1, \\cdots, X_n \\right] = \\frac{\\mathbb{E} \\left[ \\prod_{j=1}^{n} \\text{rank} \\left( X_j - \\mathbb{E}[X_j] \\right) \\right]}{\\prod_{j=1}^{n} \\sqrt[n]{\\mathbb{E}\\left[ |\\text{rank} \\left( X_j - \\mathbb{E}[X_j] \\right)|^n \\right]}}
    
    Parameters
    ----------
        X : array-like
            m x n data matrix.
        method : {'average', 'min', 'max', 'dense', 'ordinal'}, optional
            The method used to assign ranks to tied elements.
            The following methods are available (default is 'average'):
          * 'average': The average of the ranks that would have been assigned to
            all the tied values is assigned to each value.
          * 'min': The minimum of the ranks that would have been assigned to all
            the tied values is assigned to each value.  (This is also
            referred to as "competition" ranking.)
          * 'max': The maximum of the ranks that would have been assigned to all
            the tied values is assigned to each value.
          * 'dense': Like 'min', but the rank of the next highest element is
            assigned the rank immediately after those assigned to the tied
            elements.
          * 'ordinal': All values are given a distinct rank, corresponding to
            the order that the values occur in `a`.

    Returns
    -------
        : np.float64
            Spearman's correlation coefficient.

    See Also
    --------
    scipy.stats.rankdata

    Notes
    -----
    The available data ranking options are directly from `scipy.stats.rankdata`.
            
    References
    ----------
    .. [1] "Spearman%27s_rank_correlation_coefficient", https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient
    .. [2] "scipy.stats.rankdata", https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rankdata.html

    Examples
    --------
    >>> import numpy as np
    >>> data = np.arange(100).reshape(10,10)
    >>> estimators.spearman_correlation(data)
    0.9999999999999991
    '''
    transform = rankdata(X, axis=0, method=method)
    transform = transform - np.mean(transform, axis=0)
    return reflective_correlation(transform)

def angular_disimilarity(X: np.ndarray) -> np.float64:
    ''' 
    Computes the multilinear angular disimilarity.
    When given an m x 2 data matrix, it is equivalent
    to the angular distance.

    This function computes

    .. math::
        \\text{angular disimilarity} \\triangleq \\frac{\\theta}{\\pi}

    where :math:`\\theta` is the result of computing the arccosine on
    the reflective correlation coefficient.

    Parameters
    ----------
    X : array-like
        m x n data matrix

    Returns
    -------
    : np.float64
        angular disimilarity

    References
    ----------
    .. [1] "Angular distance", https://en.wikipedia.org/wiki/Cosine_similarity#Angular_distance_and_similarity
    .. [2] "What is the exact and precise definition of an ANGLE?", https://math.stackexchange.com/questions/583066/what-is-the-exact-and-precise-definition-of-an-angle

    Examples
    --------
    >>> import numpy as np
    >>> data = np.arange(100).reshape(10,10)
    >>> angular_disimilarity(data)
    0.00981604173368436
    '''
    return np.arccos(reflective_correlation(X)) / np.pi

# TODO: Implement 
def correlation_ratio(X: np.ndarray, y: np.ndarray) -> np.float64:
    '''
    .. warning::
        Not implemented yet.
        
    This function calculates the multilinear correlation ratio of a
    collection of response variables given their classes. The
    classic Fisher's correlation ratio is a special case.

    Parameters
    ----------
    X: array-like
        m x n data matrix
    y: array-like
        m-dimensional vector of class labels

    Returns
    -------
    : np.float64
        Correlation ratio score.

    Raises
    ------
    NotImplementedError

    References
    ----------
    .. [1] "Correlation Ratio", https://en.wikipedia.org/wiki/Correlation_ratio

    Examples
    --------
    >>> import numpy as np
    >>> data = np.arange(100).reshape(10,10)
    >>> y = np.arange(10)
    >>> correlation_ratio(data, y)
    '''
    raise NotImplementedError
    global_means = np.mean(X, axis=0)
    classes = set(y)
    partitions_X = [X[y == c] for c in classes]
    

def misiak_correlation(x: np.ndarray, y: np.ndarray, X: np.ndarray) -> np.float64:
    '''
    Misiak's n-inner correlation coefficient.

    Parameters
    ----------
        x: array-like
            1-D data vector
        y: array-like
            1-D data vector
        X: array-like
            m x n data matrix

    Returns
    ----------
        : np.float64
            Misiak correlation score.

    Examples
    --------
    >>> import numpy as np
    >>> np.random.seed(0)
    >>> x = np.random.normal(size=10)
    >>> y = np.random.normal(size=10)
    >>> X = np.random.normal(size=100).reshape(10,10)
    >>> misiak_correlation(x,y,X)
    -0.11209570083901074
    '''
    G = np.empty((X.shape[1]+1, X.shape[1]+1))
    G[0, 0] = x @ y
    G[0, 1:] = (x.reshape(-1,1).T @ X).flatten()
    G[1:, 0] = (y.reshape(-1,1).T @ X).flatten()
    G[1:, 1:] = X.T @ X
    numerator = np.linalg.det(G)
    G[0, 0] = x @ x
    G[1:, 0] = (x.reshape(-1,1).T @ X).flatten()
    denominator = np.linalg.det(G)
    G[0, 0] = y @ y
    G[0, 1:] = (y.reshape(-1,1).T @ X).flatten()
    G[1:, 0] = (y.reshape(-1,1).T @ X).flatten()
    denominator = denominator * np.linalg.det(G)
    denominator = np.sqrt(denominator)
    result = numerator / denominator
    return result

def multisemideviation(X: np.ndarray, p=1) -> np.float64:
    '''
    This function calculates the multisemideviation
    which is the multisemimetric between a collection
    of random variables from their expectations. The
    multisemimetric is induced by the multiseminorm,
    which is a generalization of the notion of a
    seminorm.

    Parameters
    ----------
        X: array-like
            m x n data matrix

    Returns
    ----------
        : float
            Multisemideviation score.

    See Also
    --------
    numpy.std : Standard deviation.
    minkowski_deviation : Minkowski deviation of order p.

    References
    ----------
    .. [1] "Seminorm", https://mathworld.wolfram.com/Seminorm.html
    .. [2] "Seminorm", https://en.wikipedia.org/wiki/Seminorm
    '''
    result = X - np.mean(X, axis=0)
    result = np.prod(result, axis=1)
    result = np.power(result, p)
    result = np.mean(result)
    result = np.power(result, 1/p)
    return result

def signum_correlation(X: np.ndarray) -> np.float64:
    '''
    Signum correlation coefficient.

    Parameters
    ----------
        X: array-like
            m x n data matrix

    Returns
    ----------
        : float
            Signum correlation score.
    '''
    transform = X - np.mean(X, axis=0)
    transform = np.sign(transform)
    return reflective_correlation(transform)


def taylor_correlation(X: np.ndarray) -> np.float64:
    '''
    Taylor's multi-way correlation coefficient.

    References
    ----------
    .. [1] Taylor, BM. 2020. "A Multi-Way Correlation Coefficient", https://arxiv.org/abs/2003.02561

    Notes
    -----
    Taylor 2020 defines this function to be

    .. math::

        \\frac{1}{\\sqrt{d}} \\sqrt{\\frac{1}{d-1} \\sum_{i}^{d} ( \\lambda_i -  \\bar{\\lambda})^2 }

    where :math:`d` is the number of variables, :math:`\lambda_1, \cdots, \lambda_d` are the eigenvalues of
    the correlation matrix for a given set of variables, and :math:`\\bar{\\lambda}` is the mean of those eigenvalues.
    Thus Taylor's multi-way correlation coefficient is a rescaling of the Bessel-corrected standard deviation of the
    eigenvalues of the correlation matrix of the set of variables.
    '''
    d = X.shape[1]
    result = np.corrcoef(X)
    result = np.linalg.eigvals(result)
    result = np.std(result)
    result = result / np.sqrt(d)
    return result

def trencevski_malceski_correlation(X: np.ndarray, Y: np.ndarray) -> np.float64:
    '''
    Generalized n-inner product correlation coefficient.

    Computes a correlation coefficient based
    on Trencevski and Melceski 2006.

    Parameters
    ----------
    X: array-like
        m x n data matrix
    Y: array-like
        m x n data matrix

    Returns
    ----------
        : float
            Correlation score.

    References
    ----------
    .. [1] Trencevski, Kostadin. Malceski, Risto. 2006. "On a generalized n-inner product and the corresponding Cauchy-Schwarz inequality", https://www.researchgate.net/publication/268999118_On_a_generalized_n-inner_product_and_the_corresponding_Cauchy-Schwarz_inequality
    '''
    numerator = np.linalg.det(X.T @ Y)
    denominator = np.linalg.det(X.T @ X) *\
                  np.linalg.det(Y.T @ Y)
    denominator = np.sqrt(denominator)
    result = numerator / denominator
    return result

def wang_zheng_correlation(X: np.ndarray) -> np.float64:
    '''
    Correlation coefficient due to Wang & Zheng 2014.

    This correlation coefficient is equivalent to

    .. math::

        R_{wz} \\triangleq 1 - \\det (R_{n \\times n})

    where :math:`R_{n \\times n}` is the correlation
    matrix computed on a collection of n variables. In
    other words, this correlation coefficient is the
    complement of the determinant of the correlation
    matrix.


    Parameters
    ----------
    X : array-like
        m x n data matrix

    Returns
    -------
    result : np.float64
            Unsigned correlation coefficient.

    References
    ----------
    .. [1] Wang, Jianji. Zheng, Nanning. 2014. "Measures of Correlation for Multiple Variables", https://arxiv.org/abs/1401.4827

    Notes
    -----
    The complement of this statistic is the unsigned incorrelation coefficient.
    '''
    result = X.T
    result = np.corrcoef(result)
    result = np.linalg.det(result)
    result = 1 - result
    return result

def weak_inner_correlation():
    '''
    Raises
    ------
    NotImplementedError

    References
    ----------
    .. [1] https://arxiv.org/pdf/1904.09542.pdf
    '''
    raise NotImplementedError
