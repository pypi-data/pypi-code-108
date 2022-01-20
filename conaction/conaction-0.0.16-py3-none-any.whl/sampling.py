import numpy as np

def permute_columns(x):
    '''
    Permutes the columns of a data matrix.

    Parameters
    ----------
    x : array-like
        An m x n data matrix.

    Returns
    -------
    : array-like
        Permuted matrix.
    '''
    ix_i = np.random.sample(x.shape).argsort(axis=0)
    ix_j = np.tile(np.arange(x.shape[1]), (x.shape[0], 1))
    return x[ix_i, ix_j]

def statistic_permute(X, stat_func, iters=100):
    '''
    Performs a permutation Monte Carlo of a statistical
    function applied to a given dataset.

    Parameters
    ----------
    X : array-like
        An m x n data matrix.

    Returns
    -------
    y : list
        Resulting permutation statistics.

    Notes
    -----
    This function wraps around the permute_columns function to
    sample a function of a data matrix multiple times under
    pseudo-randomly sampled permutations within the columns.
    '''
    y = []
    for r in tqdm.tqdm(range(iters), total=iters):
        y.append(stat_func(permute_columns(X)))
    return y
