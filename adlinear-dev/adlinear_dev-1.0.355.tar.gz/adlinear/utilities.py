import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats

# import typing
from typing import Union, Tuple
from sklearn.cluster import KMeans
from sklearn import metrics
# from . import clusterizer as cls


def hhi_1(tab) -> float:
    tab = [abs(x) for x in tab]
    listsum = sum(tab)
    if listsum == 0:
        return 0
    else:
        rtab = [x / listsum for x in tab]
        tab2 = [x * x for x in rtab]
        return 1.0 / sum(tab2)


def mat_hhi_1(mat, axis=0) -> pd.DataFrame:
    mat = pd.DataFrame(mat)
    if axis == 0:
        res = pd.DataFrame(index=mat.columns, columns=["InvHHI"])
        res.loc[:, "InvHHI"] = [hhi_1(mat.loc[:, col]) for col in mat.columns]
    else:
        res = pd.DataFrame(index=mat.index, columns=["InvHHI"])
        res.loc[:, "InvHHI"] = [hhi_1(mat.loc[row, :]) for row in mat.index]
    return res


def count_not_nans(mat) -> int:
    return np.count_nonzero(~np.isnan(mat.astype(float)))


def count_nans(mat) -> int:
    return np.count_nonzero(np.isnan(mat.astype(float)))


def mean_square(mat) -> float:
    sz = count_not_nans(mat)
    if sz == 0:
        return np.nan
    else:
        mat = np.nan_to_num(mat, nan=0.0)
        return np.sum(mat ** 2) / sz


def norm_n2(vec) -> float:
    vec = np.nan_to_num(vec, nan=0.0)
    return (np.sum(vec**2))**0.5


def relative_squared_error(mat1, mat2, refmat=None) -> float:
    assert mat1.shape == mat2.shape
    if refmat is None:
        meansq1 = mean_square(mat1)
        meansq2 = mean_square(mat2)
        meansq = 0.5 * (meansq1 + meansq2)
    else:
        meansq = mean_square(refmat)
    return mean_square(mat1 - mat2) / meansq if meansq > 0 else 1e9


def freq_bins(mat, nbins=10) -> Union[tuple, np.ndarray, float]:
    """

     freq_bins:

     Parameters
     ----------

     mat: a float array or matrix

     nbins: a positive integer representing a linear binning of the values

     :returns:
     a DataFrame containing the features (attributes) as columns, the observations (e.g stocks) as lines
     """

    values = pd.DataFrame(np.ravel(mat)).dropna()
    return scipy.stats.relfreq(values, nbins)


def normalized_entropy(mat, nbins=3) -> float:
    assert nbins > 0
    if nbins == 1:
        return 0
    else:
        freqs = freq_bins(mat, nbins)
        return scipy.stats.entropy(freqs.frequency) / math.log(nbins)


def relative_entropy_by_cluster(mat, lineclusters, colclusters, nbins=10):
    assert nbins > 0
    nl, nc = mat.shape
    assert nl == len(lineclusters)
    assert nc == len(colclusters)
    l_clust_values = pd.unique(pd.DataFrame(lineclusters).iloc[:, 0].sort_values())
    c_clust_values = pd.unique(pd.DataFrame(colclusters).iloc[:, 0].sort_values())

    clust_values = list(set(l_clust_values).intersection(c_clust_values))
    df_entropies = pd.DataFrame(index=clust_values, columns=clust_values)
    df_sizes = pd.DataFrame(index=clust_values, columns=clust_values)
    for l_val in clust_values:
        for c_val in clust_values:
            val_lines = lineclusters[lineclusters == l_val].dropna().index
            val_cols = colclusters[colclusters == c_val].dropna().index
            submat = mat.loc[val_lines, val_cols]
            df_entropies.loc[l_val, c_val] = normalized_entropy(submat, nbins)
            df_sizes.loc[l_val, c_val] = len(val_lines) * len(val_cols)
    return df_entropies, df_sizes


def clustering_caha_score(mat, clusters):
    return metrics.calinski_harabasz_score(mat, clusters)


def clustering_caha_score_by_ncomp(mat, clustermodel, ncompmin=2, ncompmax=20):
    kmeans_model = clustermodel.fit(mat)
    return metrics.calinski_harabasz_score(mat, clustermodel)


def censor_data(mat, p=0.0, censored_indices=[], inplace=True, randomgen=None):
    """

    """
    assert (0.0 <= p < 1.0)
    if p == 0.0 and len(censored_indices) == 0:
        return mat.copy() if not inplace else None
    else:
        if randomgen is None:
            randomgen = np.random.default_rng()
        nr = len(mat.index)
        matc = mat if inplace else mat.copy()
        if len(censored_indices) > 0:
            for idx in censored_indices:
                matc.iloc[idx[0], idx[1]] = np.nan
        else:
            nans = int(abs(p) * nr)
            for icol, _ in enumerate(matc.columns):
                # censored_idx = np.random.Generator.choice(range(nr), nans, replace=False)
                censored_idx = randomgen.choice(range(nr), nans, replace=False)
                matc.iloc[censored_idx, icol] = np.nan

        return None if inplace else matc


def swap_in_mat(mat, i, j, axis=0, inplace=True):
    """
    swap_in_mat: swaps two lines or two rows of a matrix.
    Can be in place or not.

    :returns
    None if in place, swapped matrix otherwise
    """
    nr, nc = mat.shape
    assert (0 <= i < nr and 0 <= j < nc)
    if i == j:
        return None if inplace else mat
    else:
        matc = mat if inplace else mat.copy()
        chunk_i = mat.iloc[i, :] if axis == 0 else mat.iloc[:, i]
        chunk_j = mat.iloc[j, :] if axis == 0 else mat.iloc[:, j]
        temp = chunk_i.copy()
        if axis == 0:
            matc.iloc[i, :] = chunk_j
            matc.iloc[j, :] = temp
        else:
            matc.iloc[:, i] = chunk_j
            matc.iloc[:, j] = temp

        return None if inplace else matc


def make_diagonal_dominant(mat, inplace=True):
    nr, nc = mat.shape
    assert (nr == nc)
    matc = mat if inplace else mat.copy()
    for ir, _ in enumerate(mat.index):
        cmax = np.argmax(matc.iloc[ir, :])
        swap_in_mat(matc, ir, cmax, axis=1, inplace=True)
    return None if inplace else matc


def get_observations_km_clusters(mat, ngroups=2):

    km = KMeans(n_clusters=ngroups)
    return km.fit_predict(mat)


def get_clustering_incidence_matrix(mat: Union[np.ndarray, pd.DataFrame],
                                    df_clust1: Union[np.ndarray, pd.DataFrame, Tuple[int]],
                                    df_clust2: Union[np.ndarray, pd.DataFrame, Tuple[int]]):

    assert (len(mat) == len(df_clust1) and len(df_clust1) == len(df_clust2))
    df_clust1 -= np.min(df_clust1) - 1
    df_clust2 -= np.min(df_clust2) - 1
    nclust1 = np.max(df_clust1)
    nclust2 = np.max(df_clust2)
    incidence_mat = pd.DataFrame(index=sorted(pd.unique(df_clust1.iloc[:, 0])),
                                 columns=sorted(pd.unique(df_clust2.iloc[:, 0]))).fillna(0.0, inplace=False)
    df_clust1 = pd.DataFrame(df_clust1)
    df_clust2 = pd.DataFrame(df_clust2)
    for iobs, obs in enumerate(mat.index):
        clust1 = int(df_clust1.iloc[iobs])
        clust2 = int(df_clust2.iloc[iobs])
        incidence_mat.loc[clust1, clust2] = incidence_mat.loc[clust1, clust2] + 1

    return incidence_mat


def get_clustering_mismatches(mat: Union[np.ndarray, pd.DataFrame],
                              df_clust1: Union[np.ndarray, pd.DataFrame, Tuple[int]],
                              df_clust2: Union[np.ndarray, pd.DataFrame, Tuple[int]]):
    inc_mat = get_clustering_incidence_matrix(mat, df_clust1, df_clust2)
    make_diagonal_dominant(inc_mat, inplace=True)
    nobj = len(mat.index)
    nmis = nobj - np.trace(inc_mat)
    return nmis, float(nmis) / nobj


def get_nb_misclassifieds_old(mat, grp_priors):
    ngrps = len(set(grp_priors))
    km_grps = get_observations_km_clusters(mat, ngrps)
    return get_clustering_mismatches(mat, km_grps, grp_priors)


def get_nb_misclassifieds(mat: Union[np.ndarray, pd.DataFrame],
                          cltzr,
                          ref_cltzr):
    ngrps = cltzr.get_nbgroups()
    ref_ngrps = ref_cltzr.get_nbgroups()
    assert(ngrps == ref_ngrps)
    grps = cltzr.apply(mat)
    ref_grps = ref_cltzr.apply(mat)
    return get_clustering_mismatches(mat, grps, ref_grps)


def get_avg_features_by_clusters(mat: Union[np.ndarray, pd.DataFrame], cltzr):
    groups = cltzr.apply(mat)
    ngroups = len(set(groups))
    df_mat = pd.DataFrame(mat)
    df_means = pd.DataFrame(index=range(ngroups), columns=df_mat.columns)
    df_mat['cluster'] = groups
    for grp in range(ngroups):
        submat = df_mat[df_mat['cluster'] == grp]
        df_means.loc[grp, :] = np.nanmean(submat.drop(['cluster'], axis=1), axis=0)
    return df_means, groups


def get_avg_features_by_km_clusters(mat: Union[np.ndarray, pd.DataFrame], ngroups=2):
    km = get_observations_km_clusters(mat, ngroups)
    df_mat = pd.DataFrame(mat)
    df_means = pd.DataFrame(index=range(ngroups), columns=df_mat.columns)
    df_mat['cluster'] = km
    for grp in range(ngroups):
        submat = df_mat[df_mat['cluster'] == grp]
        df_means.loc[grp, :] = np.nanmean(submat.drop(['cluster'], axis=1), axis=0)
    return df_means, km


def fill_missing(mat, method="median", axis=0, fill_values=None, ngroups=0):

    if type(mat) is not pd.DataFrame:
        cols = list(["F" + str(x) for x in range(1, mat.shape[1] + 1)])
        filled_mat = pd.DataFrame(data=mat.values, columns=cols)
    else:
        filled_mat = mat.copy().astype(float)

    if method in ["median", "mean"]:
        if method == "median":
            df_estimates = mat.astype(float).apply(np.nanmedian, axis=axis)
        elif method == "mean":
            df_estimates = mat.astype(float).apply(np.nanmean, axis=axis)
        if axis == 0:
            # TODO: do the fill in next step without for loop
            # for col in mat.columns:
            #     filled_mat[col].fillna(value=df_estimates[col], inplace=True)
            filled_mat.fillna(value=df_estimates.to_dict(), inplace=True)
        else:
            for idx in mat.index:
                filled_mat.loc[idx].fillna(value=df_estimates.loc[idx], inplace=True)

    elif method == "kmeans":
        # KMeans ne tolère pas les valeurs manquantes: imputer la moyenne par feature
        km_filled_mat = fill_missing(mat, method="mean", axis=axis)
        df_means, km = get_avg_features_by_km_clusters(km_filled_mat, ngroups)
        # reprendre la matrice incomplète
        filled_mat = mat.copy()
        for idx in filled_mat.index:
            grp = km[idx]
            filled_mat.loc[idx] = mat.loc[idx].fillna(value=df_means.loc[grp, :])

    elif method == "values" and fill_values is not None:
        # update works inplace
        filled_mat.update(other=fill_values, overwrite=False)

    return filled_mat


def shorten_features_names(mat, wished_len=20):
    if hasattr(mat, "columns"):
        cols_dict = dict.fromkeys(list(mat.columns))
        for col in cols_dict:
            cols_dict[col] = col[0:wished_len] if len(col) >= wished_len else col
        mat = mat.rename(columns=cols_dict)
    return mat


def center_by_columns(mat):
    if type(mat) is pd.DataFrame:
        pass
    else:
        cols = list(["F" + str(x) for x in range(1, mat.shape[1] + 1)])
        mat = pd.DataFrame(data=mat.values, columns=cols)
    centered_mat = mat.copy()
    return centered_mat


def normalize_by_columns(mat):
    if type(mat) is not pd.DataFrame:
        cols = list(["F" + str(x) for x in range(1, mat.shape[1] + 1)])
        mat = pd.DataFrame(data=mat.values, columns=cols)
    normalized_mat = mat.copy()
    means = np.nanmean(normalized_mat, axis=0)
    stdevs = np.nanstd(normalized_mat, axis=0)
    normalized_mat -= means
    normalized_mat /= stdevs

    return normalized_mat, means, stdevs


def denormalize_by_columns(mat, means=0, stdevs=1):
    if type(mat) is not pd.DataFrame:
        cols = list(["F" + str(x) for x in range(1, mat.shape[1] + 1)])
        mat = pd.DataFrame(data=mat.values, columns=cols)
    denormalized_mat = mat.copy()
    denormalized_mat *= stdevs
    denormalized_mat += means

    return denormalized_mat


def sort_columns_by_fill_rate(mat, grouping_vect=None):
    """

    - si grouping_vect == [], on calcule le taux de remplissage sur la totalité de la matrice
    - si grouping_vect n'est pas vide, c'est un DF indexé comme mat (par des ids d'objets)
    et le taux de remplissage d'une colonne est calculé séparément sur tous les groupes d'objets
    partageant le même identifiant de regroupement

    """

    if grouping_vect is None:
        grouping_vect = []
    if type(mat) is pd.DataFrame:
        cols = mat.columns
    else:
        cols = list(["F" + str(x) for x in range(1, mat.shape[1] + 1)])
        mat = pd.DataFrame(data=mat.values, columns=cols)
    # cols.append ('Avg_rate_by_group')

    if len(grouping_vect) == 0:
        fill_index = [0, "Avg_rate_by_feature"]
        # attribution du groupe 0 à toutes les observations
        grouping_vect = pd.DataFrame(index=mat.index, columns=["Grp"])
        grouping_vect["Grp"] = 0
        # grp_values = {0}

    elif type(grouping_vect) in [pd.Series, pd.DataFrame]:
        grp_values = list(set(grouping_vect[grouping_vect.columns[0]]))
        fill_index = grp_values
        # noinspection PyTypeChecker
        fill_index.append("Avg_rate_by_feature")

    else:
        return

    df_fill_rate = pd.DataFrame(index=fill_index, columns=cols)
    df_fill_rate["Avg_rate_by_group"] = 0.0
    fill_index.remove("Avg_rate_by_feature")

    for idx in fill_index:
        for col in cols:
            subindex = grouping_vect[grouping_vect[grouping_vect.columns[0]] == idx].index
            subindex = mat.index.intersection(subindex)
            colvalues = mat.loc[subindex, col]
            colvalues = colvalues.dropna(inplace=False)
            if len(subindex) > 0:
                df_fill_rate.loc[idx, col] = float(len(colvalues) / len(subindex))

    df_fill_rate.loc["Avg_rate_by_feature", :] = np.nanmean(df_fill_rate, axis=0)
    df_fill_rate.loc[:, "Avg_rate_by_group"] = np.nanmean(df_fill_rate, axis=1)

    if len(grouping_vect) == 0:
        # pas de groupement des observations: un seul taux de remplissage par feature
        # Tri des colonnes par taux décroissant
        df_fill_rate = df_fill_rate.sort_values(by="Avg_rate_by_feature", axis=1, ascending=False, inplace=False)
    else:
        df_fill_rate = df_fill_rate.sort_values(by="Avg_rate_by_feature", axis=1, ascending=False, inplace=False)
        df_fill_rate = df_fill_rate.sort_values(by="Avg_rate_by_group", axis=0, ascending=False, inplace=False)

    return df_fill_rate.astype(float)


def sort_lines_by_fill_rate(mat):
    if type(mat) is pd.DataFrame:
        lines = mat.index
    else:
        lines = list(["I" + str(x) for x in range(1, mat.shape[0] + 1)])
        mat = pd.DataFrame(data=mat.values, index=lines)
    df_fill_rate = pd.DataFrame(index=[0], columns=lines)
    for line in lines:
        linevalues = mat.loc[line]
        linevalues = linevalues.dropna(inplace=False)
        df_fill_rate[line] = float(len(linevalues) / mat.shape[1])

    df_fill_rate = df_fill_rate.sort_values(by=0, axis=1, ascending=False)
    return df_fill_rate.astype(float)


def drop_sparse_lines(mat, minimum_fill_rate=0.5):
    if type(mat) is pd.DataFrame:
        cols = mat.columns
        lines = mat.index
    else:
        cols = list(["F" + str(x) for x in range(1, mat.shape[1] + 1)])
        lines = list(["I" + str(x) for x in range(1, mat.shape[0] + 1)])
    submat = pd.DataFrame(data=mat.values, columns=cols, index=lines)
    # df_lfill_rate = pd.DataFrame(index=[0],
    #                             columns=lines)
    lines_to_drop = []

    for line in lines:
        linevalues = mat.loc[line]
        linevalues = linevalues.dropna(inplace=False)
        if float(len(linevalues) / submat.shape[1]) < minimum_fill_rate:
            lines_to_drop.append(line)

    submat = submat.drop(lines_to_drop, axis=0)

    return submat


def drop_sparse_columns(mat, minimum_fill_rate=0.5) -> (pd.DataFrame, list):
    """

    drop_sparse_columns:
    Eliminates columns from a matrix for which the proportion of filled (not nan) values
    to the number of entries is less than a given minimum.

    Parameters
    ----------

    mat: a bi-dimensional numeric array: float[,] ndarray or DataFrame
    If mat has no index/columns, a DataFrame with automated index and columns is created.

    minimum_fill_rate: the minimum ratio. All columns with a strictly lower fill rate are dropped.

    returns
    -------

    pd.DataFrame, list: A copy of the original matrix (as DataFrame), without the sparse columns and the list of
    dropped columns
    """

    if type(mat) is pd.DataFrame:
        cols = mat.columns
        lines = mat.index
    else:
        cols = list(["F" + str(x) for x in range(1, mat.shape[1] + 1)])
        lines = list(["I" + str(x) for x in range(1, mat.shape[0] + 1)])

    submat = pd.DataFrame(data=mat.values, columns=cols, index=lines)
    # df_cfill_rate = pd.DataFrame(index=[0],
    #                             columns=cols)
    cols_to_drop = []
    for col in cols:
        colvalues = mat[col]
        colvalues = colvalues.dropna(inplace=False)
        if float(len(colvalues) / mat.shape[0]) < minimum_fill_rate:
            cols_to_drop.append(col)

    submat = submat.drop(cols_to_drop, axis=1)

    return submat, cols_to_drop


def drop_zero_columns(mat):
    """

    drop_null_columns:
    Eliminates from a matrix those columns only populated by 0.

    Parameters
    ----------

    :param mat: a bi-dimensional numeric array: float[,] ndarray or DataFrame
    If mat has no index/columns, a DataFrame with automated index and columns is created.

     :returns
    --------

    A copy of the original matrix (as DataFrame), without the null columns
    The list of dropped columns
    """

    if type(mat) is pd.DataFrame:
        cols = mat.columns
        lines = mat.index
    else:
        cols = list(["F" + str(x) for x in range(1, mat.shape[1] + 1)])
        lines = list(["I" + str(x) for x in range(1, mat.shape[0] + 1)])

    submat = pd.DataFrame(data=mat.values, columns=cols, index=lines)
    # df_cfill_rate = pd.DataFrame(index=[0],
    #                             columns=cols)
    cols_to_drop = []
    for col in cols:
        colvalues = mat[col]
        if all([v == 0 for v in colvalues]):
            cols_to_drop.append(col)

    submat = submat.drop(cols_to_drop, axis=1)

    return submat, cols_to_drop


def drop_lines_and_columns(mat, minimum_fill_rate=0.5, droplines=True, dropcols=True, colsfirst=True):
    if droplines and dropcols:
        if colsfirst:
            submat = drop_sparse_columns(mat, minimum_fill_rate)
            submat = drop_sparse_lines(submat, minimum_fill_rate)
        else:
            submat = drop_sparse_lines(mat, minimum_fill_rate)
            submat = drop_sparse_columns(submat, minimum_fill_rate)
    elif dropcols:
        submat = drop_sparse_columns(mat, minimum_fill_rate)
    else:
        submat = drop_sparse_lines(mat, minimum_fill_rate)

    return submat


def drop_features(mat, features_to_drop):
    submat = mat.copy().drop(features_to_drop, axis=1) if features_to_drop is not None else mat.copy()
    return submat


def separate_along_median_by_cols(mat):
    cols_plus = [str(x) + "_+" for x in mat.columns]
    cols_minus = [str(x) + "_-" for x in mat.columns]
    cols_meds = mat.astype(float).apply(np.nanmedian, axis=0)
    mat_plus = pd.DataFrame(index=mat.index, data=mat.values, columns=cols_plus)

    mat_minus = pd.DataFrame(index=mat.index, data=mat.values, columns=cols_minus)
    m = pd.concat([mat_plus, mat_minus], axis=1)
    for col in mat.columns:
        m[str(col) + "_+"] = np.maximum(0.0, mat[col] - cols_meds[col])
        m[str(col) + "_-"] = np.maximum(0.0, cols_meds[col] - mat[col])
    return m, cols_meds


def rebuild_median_separated_matrix(duplicated_mat, med):

    if med is None:
        pass
    [nf] = med.shape
    _, nmf = duplicated_mat.shape
    assert nmf == 2 * nf
    origin_mat = pd.DataFrame(columns=med.index, index=duplicated_mat.index, data=0)
    origin_mat = origin_mat.add(duplicated_mat.iloc[:, 0:nf].values)
    origin_mat = origin_mat.sub(duplicated_mat.iloc[:, nf: 2 * nf].values)
    origin_mat = origin_mat.T.add(med, axis="index").T
    return origin_mat


def plot_fill_rate(mat, bycols=True, grouping_vect=None, path=None):
    if grouping_vect is None:
        grouping_vect = []
    fill_rate = sort_columns_by_fill_rate(mat, grouping_vect) if bycols else sort_lines_by_fill_rate(mat)

    axis = 1 if bycols else 0

    f, ax = plt.subplots(figsize=(10, 5))
    if len(grouping_vect) == 0:
        mean_rate = np.mean(fill_rate, axis=axis)[0]
        plt.bar(
            list(range(len(fill_rate.columns))),
            fill_rate.loc[0, :], width=2.0, label="Mean {0:.1%}".format(mean_rate)
        )
        ax.set_ylabel("Fill rate")
        xlabel = "Features" if bycols else "Stocks"
        ax.set_xlabel(xlabel)
        ax.set_title(xlabel + " ordered by fill rate")
        ax.legend()
    else:
        fill_rate = fill_rate.astype(float)

        _, _ = plt.subplots(figsize=(20, 10))
        _ = sns.heatmap(
            fill_rate,
            annot=False,
            linewidths=0,
            yticklabels=True,
            xticklabels=True,
            cmap="coolwarm",
            cbar_kws={"label": "Fill rate"},
        )
    if path is not None:
        plt.gcf().savefig(path)
    plt.show()


def get_features_correlation_matrix(mat):
    mat_corr = pd.DataFrame(index=mat.columns, columns=mat.columns)
    for irow, row in enumerate(mat_corr.index):
        for icol, col in enumerate(mat_corr.columns):
            if icol == irow:
                mat_corr.iloc[irow, icol] = 1
            elif icol < irow:
                mat_corr.iloc[irow, icol] = mat_corr.iloc[icol, irow]
            else:
                mat_corr.iloc[irow, icol] = np.corrcoef(mat.iloc[:, irow], mat.iloc[:, icol])[0, 1]

    return mat_corr


def plot_values(mat, xticklabels=False, yticklabels=True, path=None):
    if not type(mat) is pd.DataFrame:
        cols = list(["F" + str(x) for x in range(1, mat.shape[1] + 1)])
        lines = list(["I" + str(x) for x in range(1, mat.shape[0] + 1)])
        mat = pd.DataFrame(index=cols, columns=lines, data=mat)
    plt.subplots(figsize=(40, 20))
    sns.heatmap(mat, annot=False, linewidths=0, xticklabels=xticklabels, yticklabels=yticklabels, cmap="bwr")

    if path is not None:
        plt.gcf().savefig(path)
    else:
        plt.show()
    plt.close("all")


def generate_random_correl_matrix(size: int, corr_max: float) -> pd.DataFrame:
    """

     generate_random_correl_matrix:
     generate a random correlation matrix having an absolute maximum correlation

     Parameters
     ----------

     size: the size of the square matrix

     corr_max: the maximum of absolute value of non-diagonal terms

     :returns:
     the desired correlation matrix as DataFrame
     """

    assert (size > 0)
    mat = np.ndarray([size, size])
    res = pd.DataFrame(mat)
    for col in range(size):
        res.iloc[col, :] = np.random.uniform(-corr_max, corr_max, size)
        res.iloc[col, col] = 1
    return res


def generate_orthogonal_vector(v: object) -> pd.DataFrame:
    """

     generate_orthogonal_vector:
     generate a random vector of the same size as a given non null vector v, orthogonal to v

     Parameters
     ----------

     v: the vector

     :returns:
     the random vector orthogonal to v
     """
    if type(v) is list:
        v = pd.DataFrame(v)
    n, _ = v.shape
    assert (n > 1)
    assert (not all([v.iloc[i, 0] == 0 for i in range(n)]))
    w = pd.DataFrame(np.zeros(n))
    if n == 2:
        w.iloc[0, 0] = v.iloc[1, 0]
        w.iloc[1, 0] = -v.iloc[0, 0]
    else:
        istar = np.argmin([1 if v.iloc[i, 0] != 0 else 0 for i in range(n)])
        w.iloc[:, 0] = np.random.uniform(-1, 1, n)
        vw = np.dot(v.T, w)[0, 0]
        w.iloc[istar, 0] = - vw / v.iloc[istar, 0]
    return w


def generate_vectors_bouquet(vpivot: Union[np.ndarray, Tuple[float], pd.DataFrame],
                             bouquet_size: int,
                             min_corr: float = 0.0,
                             positive: bool = True,
                             col_shift: int = 0,
                             row_shift: int = 0) -> pd.DataFrame:
    """
    generate_vectors_bouquet:
    generates a set of vectors around a given pivot vector, having a minimum prescribed mutual correlation
    Parameters
    ----------
    vpivot: Union[np.ndarray, Tuple[float], pd.DataFrame]
        the pivot vector used to create the bouquet
    bouquet_size: int
        number of vectors in the bouquet
    min_corr: float = 0.0
        minimum correlation between two vectors
    positive: bool = True
        if true, all vectors have positive coordinates
    col_shift: int = 0
        the integer shift applied to the column numbering
    row_shift: int = 0
        the integer shift applied to the line numbering
    Returns
    -------
    A dataframe having one line per space coordinate (common dimension), one column per vector in the bouquet
    """
    vpivot = pd.DataFrame(vpivot)
    nr, _ = vpivot.shape
    df_bouquet = pd.DataFrame(index=range(row_shift, row_shift+nr),
                              columns=range(col_shift, col_shift+bouquet_size))
    df_bouquet.fillna(value=0.0, inplace=True)
    epsilon = (1 - min_corr)**0.5
    n2v = norm_n2(vpivot)
    for icol in range(bouquet_size):
        if nr > 1:
            w = generate_orthogonal_vector(vpivot)
            n2w = norm_n2(w)
            rescaled_w = epsilon * n2v / n2w * pd.DataFrame(w)
            vals = vpivot.values + rescaled_w.values
            df_bouquet.loc[:, col_shift+icol] = vals
        else:
            vals = vpivot.values + epsilon * np.random.uniform(0, 1.0)
            df_bouquet.loc[:, col_shift+icol] = vals
    if positive:
        minval = np.min(np.min(df_bouquet))
        if minval < 0:
            df_bouquet -= minval
    return df_bouquet


def generate_clusters_centroids(ndim: int, max_corr: float, n_centroids: int = 0) -> pd.DataFrame:
    """
    Generates a vector set of fixed dimension having pairwise bounded correlation.
    By default, the set size is the same as the vector space dimension.
    TODO: handle the case where the set size is greater thar the dimension, this may result in a contradiction
    TODO: if the correlation bound is too small or null
    Parameters
    ----------
    ndim: int
        size of vectors
    max_corr: float
        maximum pairwise correlation
    n_centroids
        number of generated vectors

    Returns
    -------
    A ndim x ndim dataframe. The desired vectors are in columns and satsify the correlation condition.
    """
    assert (ndim >= 1)
    assert (0 <= max_corr < 1)
    if n_centroids == 0:
        n_centroids = ndim
    a = ndim / 4.0 * (1 - max_corr / 3)
    b = 1 - max_corr
    c = - max_corr
    delta = b*b - 4*a*c
    epsmax = 0.5 * (- b + delta**0.5) / a
    df_centroids = pd.DataFrame(index=range(ndim), columns=range(ndim))
    df_centroids.fillna(value=0.0, inplace=True)
    for icol in range(ndim):
        df_centroids.iloc[icol, icol] = 1
        df_centroids.iloc[:, icol] += np.random.uniform(0.0, 2*epsmax, ndim)

    return df_centroids


def generate_integer_partition(ntot: int, nbpart: int, nmin: int = 1):

    # assert(ntot >= nbpart*nmin)
    rng = np.random.default_rng()
    cuts = np.sort(rng.choice(ntot, nbpart, replace=False))
    res = []
    zum = 0
    defect = 0
    for i, cut in enumerate(cuts):
        diff = cut if i == 0 else cut - cuts[i-1]
        if diff < nmin:
            defect += nmin - diff
            val = nmin
        elif defect == 0:
            val = diff
        elif diff >= nmin + defect:
            val = diff - defect
            defect = 0
        else:
            val = diff
        res.append(val)
        zum += val
    if zum < ntot:
        res[-1] += ntot-zum
    # partsize = ntot / nbpart
    # res = [partsize] * nbpart
    return res


def generate_clusterized_vectors(vsize: int, nbvect: int, nclusters: int,
                                 clusterminsize: int, max_inter_corr: float,
                                 min_intra_corr: float, random_norms: bool = True) -> pd.DataFrame:
    """
    generate_clusterized_vectors: generates several bouquets or set of vectors grouped by correlation clusters.

    Parameters
    ----------
    vsize: int
        common vector length - the dimension of the surrounding vector space
    nbvect: int
        total number of vector to generate
    nclusters: int
        number of vector clusters to generate. The default case is nclusters == vsize,
        ie as many clusters as the dimension
    clusterminsize: int
        minimum size of a cluster
    max_inter_corr: float
        maximum correlation between the centroids of two distinct clusters
    min_intra_corr: float
        minimum correlation between two vectors belonging to the same cluster
    random_norms: bool
        if true, the norms of generated vectors are log-normally distributed

    Returns
    -------
    A dataframe having 'vsize' lines and 'nbvects' columns. The columns are grouped into the desired 'nclusters' groups.
    """
    clustersizes = generate_integer_partition(ntot=nbvect, nbpart=nclusters, nmin=clusterminsize)
    centroids = generate_clusters_centroids(ndim=vsize, max_corr=max_inter_corr)
    df_res = pd.DataFrame(index=range(vsize))
    # factors = np.random.exponential(size=nclusters) if random_norms else np.zeros(shape=nclusters)
    factors = np.random.lognormal(mean=0, sigma=1, size=nclusters)
    row_shift = 0
    col_shift = 0
    for icluster, csize in enumerate(clustersizes):
        if icluster < len(centroids.columns):
            centroid = centroids.iloc[:, icluster]
            df_bouquet = generate_vectors_bouquet(vpivot=centroid,
                                                  bouquet_size=int(csize),
                                                  min_corr=min_intra_corr,
                                                  col_shift=col_shift
                                                  )
            df_bouquet *= 1 + factors[icluster]

            df_res = pd.concat([df_res, df_bouquet], axis=1)
        col_shift += int(csize)
    return df_res


def build_correspondence_map(df_clusters) -> pd.DataFrame:

    assert len(df_clusters.columns) >= 2
    clusters_1 = [str(x) for x in set(df_clusters.iloc[:, 0])]
    clusters_2 = [str(x) for x in set(df_clusters.iloc[:, 1])]
    df_map = pd.DataFrame(index=clusters_1, columns=clusters_2)
    df_map.fillna(value=0.0, inplace=True)
    for idx in df_clusters.index:
        cl1 = str(df_clusters.loc[idx][0])
        cl2 = str(df_clusters.loc[idx][1])
        df_map.loc[cl1, cl2] += 1

    sum_of_cluster1 = df_map.apply(np.sum, axis=1)
    for idx in df_map.index:
        df_map.loc[idx, :] /= sum_of_cluster1[idx]

    return df_map


def plot_correspondence_map(df_clusters, path=None):

    df_map = build_correspondence_map(df_clusters)
    plot_values(df_map, xticklabels=True, path=path)
    return None


def duplicate_data_wfold(df: pd.DataFrame, window: int) -> pd.DataFrame:
    if window <= 0:
        return pd.DataFrame()
    cols = df.columns
    nidx = len(df.index)
    l_shifted_cols = [[f"{c}_{i}" for i in range(window)] for c in cols]
    shifted_cols = [item for sublist in l_shifted_cols for item in sublist]
    duplicated_df = pd.DataFrame(index=df.index, columns=shifted_cols)
    for irow, idx in enumerate(df.index):
        for icol, col in enumerate(cols):
            for shift in range(window):
                duplicated_df.loc[idx, f"{col}_{shift}"] = df.iloc[irow+shift, icol] if irow+shift < nidx else np.nan
    return duplicated_df

