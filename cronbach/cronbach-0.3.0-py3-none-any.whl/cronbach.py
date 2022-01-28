"""See top level package docstring for documentation"""

import numpy as np
import pandas as pd
from scipy.stats import f

def alpha(data=None, items=None, scores=None, subject=None,
                   nan_policy='pairwise', ci=.95):
    """Cronbach's alpha reliability measure.

    Parameters
    ----------

    data : :py:class:`pandas.DataFrame`
        Wide or long-format dataframe.
    items : str
        Column in ``data`` with the items names (long-format only).
    scores : str
        Column in ``data`` with the scores (long-format only).
    subject : str
        Column in ``data`` with the subject identifier (long-format only).
    nan_policy : bool
        If `'listwise'`, remove the entire rows that contain missing values
        (= listwise deletion). If `'pairwise'` (default), only pairwise
        missing values are removed when computing the covariance matrix.
        For more details, please refer to the :py:meth:`pandas.DataFrame.cov`
        method.
    ci : float
        Confidence interval (.95 = 95%)

    Returns
    -------

    alpha : float
        Cronbach's alpha

    Notes
    -----

    This function works with both wide and long format dataframe. If you pass a
    long-format dataframe, you must also pass the ``items``, ``scores`` and
    ``subj`` columns (in which case the data will be converted into wide
    format using the :py:meth:`pandas.DataFrame.pivot` method).
    Internal consistency is usually measured with Cronbach's alpha [1]_,
    a statistic calculated from the pairwise correlations between items.
    Internal consistency ranges between negative infinity and one.
    Coefficient alpha will be negative whenever there is greater
    within-subject variability than between-subject variability.
    Cronbach's :math:`\\alpha` is defined as

    .. math::

        \\alpha ={k \\over k-1}\\left(1-{\\sum_{{i=1}}^{k}\\sigma_{{y_{i}}}^{2}
        \\over\\sigma_{x}^{2}}\\right)

    where :math:`k` refers to the number of items, :math:`\\sigma_{x}^{2}`
    is the variance of the observed total scores, and
    :math:`\\sigma_{{y_{i}}}^{2}` the variance of component :math:`i` for
    the current sample of subjects.
    Another formula for Cronbach's :math:`\\alpha` is

    .. math::

        \\alpha = \\frac{k \\times \\bar c}{\\bar v + (k - 1) \\times \\bar c}

    where :math:`\\bar c` refers to the average of all covariances between
    items and :math:`\\bar v` to the average variance of each item.
    95% confidence intervals are calculated using Feldt's method [2]_:

    .. math::

        c_L = 1 - (1 - \\alpha) \\cdot F_{(0.025, n-1, (n-1)(k-1))}
        c_U = 1 - (1 - \\alpha) \\cdot F_{(0.975, n-1, (n-1)(k-1))}

    where :math:`n` is the number of subjects and :math:`k` the number of
    items.

    Results have been tested against the `psych
    <https://cran.r-project.org/web/packages/psych/psych.pdf>`_ R package.

    References
    ----------

    .. [1] http://www.real-statistics.com/reliability/cronbachs-alpha/
    .. [2] Feldt, Leonard S., Woodruff, David J., & Salih, Fathi A. (1987).
           Statistical inference for coefficient alpha. Applied Psychological
           Measurement, 11(1):93-103.

    Examples
    --------

    Binary wide-format dataframe (with missing values)

    >>> import cronbach
    >>> # In R: psych:alpha(data, use="pairwise")
    >>> cronbach.alpha(data=data)
    (0.732660835214447, array([0.435, 0.909]))

    After listwise deletion of missing values (remove the entire rows)

    >>> # In R: psych:alpha(data, use="complete.obs")
    >>> cronbach.alpha(data=data, nan_policy='listwise')
    (0.8016949152542373, array([0.581, 0.933]))

    After imputing the missing values with the median of each column

    >>> cronbach.alpha(data=data.fillna(data.median()))
    (0.7380191693290734, array([0.447, 0.911]))

    Likert-type long-format dataframe

    >>> cronbach.alpha(data=data, items='Items', scores='Scores',
    ...                   subject='Subj')
    (0.5917188485995826, array([0.195, 0.84 ]))
    """
    # Safety check
    assert isinstance(data, pd.DataFrame), 'data must be a dataframe.'
    assert nan_policy in ['pairwise', 'listwise']

    if all([v is not None for v in [items, scores, subject]]):
        # Data in long-format: we first convert to a wide format
        data = data.pivot(index=subject, values=scores, columns=items)

    # From now we assume that data is in wide format
    n, k = data.shape
    assert k >= 2, 'At least two items are required.'
    assert n >= 2, 'At least two raters/subjects are required.'
    err = 'All columns must be numeric.'
    assert all([data[c].dtype.kind in 'bfiu' for c in data.columns]), err
    if data.isna().any().any() and nan_policy == 'listwise':
        # In R = psych:alpha(data, use="complete.obs")
        data = data.dropna(axis=0, how='any')

    # Compute covariance matrix and Cronbach's alpha
    C = data.cov()
    cronbach = (k / (k - 1)) * (1 - np.trace(C) / C.sum().sum())
    # which is equivalent to
    # v = np.diag(C).mean()
    # c = C.to_numpy()[np.tril_indices_from(C, k=-1)].mean()
    # cronbach = (k * c) / (v + (k - 1) * c)

    # Confidence intervals
    alpha = 1 - ci
    df1 = n - 1
    df2 = df1 * (k - 1)
    lower = 1 - (1 - cronbach) * f.isf(alpha / 2, df1, df2)
    upper = 1 - (1 - cronbach) * f.isf(1 - alpha / 2, df1, df2)
    return cronbach, np.round([lower, upper], 3)
