import pandas as pd
from typing import Union
from typing import List, Iterable, Optional
from typing import Tuple
import numpy as np
import math

from sklearn.decomposition import NMF

from . import pca as pca
from . import utilities as utl
from . import nmfmodel as nmf
from . import ntfmodel as ntf
from . import imputer as imp

# import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from pathlib import Path

NMF_MODEL = Union[nmf.NmfModel, ntf.NtfModel]


def compare_full_sparse_nmf_model(m: pd.DataFrame, ncomp: int, nblocks: int = 1, sparsity: float = 0.0,
                                  nfills: int = 0, drop_unrelevant: bool = False, do_plot: bool = False,
                                  pictures_path: str = "") -> Tuple[NMF_MODEL, NMF_MODEL]:
    """

    :param m:
    :param ncomp:
    :param nblocks:
    :param sparsity:
    :param nfills:
    :param drop_unrelevant:
    :param do_plot:
    :param pictures_path:
    :return:
    """

    if nblocks == 1:
        full_model = nmf.NmfModel(mat=m, ncomp=ncomp, regularization="components", leverage="robust", max_iter=200)
    else:
        m_dup, m_med = utl.separate_along_median_by_cols(m)
        full_model = ntf.NtfModel(
            mat=m_dup,
            ncomp=ncomp,
            baseline=m_med,
            nblocks=nblocks,
            regularization="components",
            leverage="robust",
            max_iter=200,
        )

    full_model.set_sparsity(sparsity)
    full_model.test_model(nfill_iters=nfills)
    # nc0 = sparse_model.ncomp
    # # Heatmap NMF
    full_model.sort_features_by_cluster()
    full_model.sort_observations_by_cluster()
    nh = full_model.get_effective_dimension()
    if do_plot:
        full_model.plot_data_heatmap(pictures_path / "Full_nb{}_nc{}_sp{}_nh{}.pdf".format(nblocks, ncomp,
                                                                                           sparsity, nh))

    restricted_model = None
    if sparsity > 0:
        # recalculer le modèle sans sparsity après élimination des colonnes non retenues
        # dans le modèle précédent avec sparsity
        ht = full_model.get_h().T
        h_dense, null_features = utl.drop_zero_columns(ht)
        m_filled_dense = m.drop(null_features, axis=1) if drop_unrelevant else m
        if nblocks == 1:
            restricted_model = nmf.NmfModel(mat=m_filled_dense, ncomp=ncomp, leverage="robust", max_iter=200)
        else:
            m_dup_dense, m_med_dense = utl.separate_along_median_by_cols(m_filled_dense)
            restricted_model = ntf.NtfModel(
                mat=m_dup_dense, ncomp=ncomp, baseline=m_med_dense, nblocks=2, leverage="robust", max_iter=200
            )

        restricted_model.test_model(nfill_iters=nfills)
        restricted_model.sort_features_by_cluster()
        restricted_model.sort_observations_by_cluster()
        nh = restricted_model.get_effective_dimension()
        if do_plot:
            restricted_model.plot_data_heatmap(pictures_path / "restricted_nb{}_nc{}_sp{}_nh{}.pdf".format(nblocks,
                                                                                                           ncomp,
                                                                                                           sparsity,
                                                                                                           nh))

    return full_model, restricted_model


def test_nmf_sparsity(m, ncomp, name="", priors=None, nblocks=1, sp_step=0.1, sp_min=0, sp_max=1,
                      do_save_by_sp_level=False,
                      outpath="", do_save_result=True):
    """
    :param do_save_result:

    """
    assert sp_step > 0
    nstep = int(1.0 / sp_step)
    df_res = pd.DataFrame(
        index=[round(i * sp_step, 2) for i in range(nstep)],
        columns=[],
    )

    sparsity = sp_min
    isp = 0
    modelstr = "ntf" if nblocks > 1 else "nmf"
    modelstr += "_" + name
    if nblocks == 1:
        model = nmf.NmfModel(mat=m, name=f"{name}_{ncomp}_nmf", ncomp=ncomp, regularization="components",
                             leverage="robust", max_iter=200)
    else:
        m_dup, m_med = utl.separate_along_median_by_cols(m)
        model = ntf.NtfModel(
            mat=m_dup,
            name=f"{name}_{ncomp}_snmf",
            ncomp=ncomp,
            baseline=m_med,
            nblocks=nblocks,
            regularization="components",
            leverage="robust",
            max_iter=200)

    while sparsity <= sp_max:
        model.set_sparsity(sparsity)
        model.test_model()
        ht = model.get_h().T
        _, null_features = utl.drop_zero_columns(ht)
        _, null_components = utl.drop_zero_columns(model.get_h())
        m_reduced = m.drop(null_features, axis=1) if null_features else m
        if null_features is None:
            reduced_model = model.copy()
        else:
            if nblocks == 1:
                reduced_model = nmf.NmfModel(mat=m_reduced, name=name, ncomp=ncomp, regularization="components",
                                             leverage="robust",
                                             max_iter=200)
            else:
                m_red_dup, m_red_med = utl.separate_along_median_by_cols(m_reduced)
                reduced_model = ntf.NtfModel(
                    mat=m_red_dup,
                    ncomp=ncomp,
                    baseline=m_red_med,
                    nblocks=nblocks,
                    regularization="components",
                    leverage="robust",
                    max_iter=200)
        reduced_model.set_sparsity(0.0)
        hcomp, hspars = reduced_model.get_h_compression()
        df_res.loc[sparsity, "NComponents"] = ncomp
        df_res.loc[sparsity, "Error_unreduced"] = model.get_precision()
        df_res.loc[sparsity, "Error"] = err = reduced_model.get_precision()
        df_res.loc[sparsity, "H_compression"] = hcomp
        df_res.loc[sparsity, "Volume"] = vol = reduced_model.get_volume()
        df_res.loc[sparsity, "Err/Vol"] = np.nan if vol == 0.0 else err/vol
        df_res.loc[sparsity, "H_sparsity"] = hspars
        df_res.loc[sparsity, "Null_features"] = len(null_features)
        df_res.loc[sparsity, "Null_components"] = len(null_components)
        if nblocks == 1:
            df_res.loc[sparsity, "Relative_entropy"] = reduced_model.get_avg_diag_entropies(nbins=3).iloc[0, 0]
        df_res.loc[sparsity, "Misclassifieds"], _ = reduced_model.get_nb_misclassified_obs(priors) if priors is not None \
            else np.nan, np.nan

        feat_compo = model.get_features_by_decreasing_loading(min_contribution=0.2)
        if do_save_by_sp_level:
            feat_compo.to_csv(Path(outpath) / f"{modelstr}{ncomp}_sp{sparsity}_feat_compo.csv")
            model.get_h().to_csv(Path(outpath) / f"{modelstr}{ncomp}_sp{sparsity}_H.csv")
        isp += 1
        sparsity = round(sparsity + sp_step, 2)
        if sparsity == 1:
            m_reduced.to_csv(Path(outpath) / f"{modelstr}_c{ncomp}_hhi_reduced_data.csv")

    if do_save_result:
        df_res.to_csv(Path(outpath) / f"{modelstr}_c{ncomp}_test_sparsity.csv")

    return df_res


def test_nmf_ncomp(m, ncomp_min=2, ncomp_max=10, name="", priors=None, nblocks=1, sparsity=1.0,
                   outpath="", do_save_result=True):
    """
    :param do_save_result:

    """
    df_res = pd.DataFrame(
        index=[n for n in range(ncomp_min, ncomp_max)],
        columns=["NComponents", "Error_unreduced", "Error", "Volume", "H_compression", "H_sparsity",
                 "Null_features", "Null_components", "Relative_entropy", "Misclassifieds"],
    )

    isp = 0
    modelstr = "ntf" if nblocks > 1 else "nmf"
    modelstr += "_" + name
    if nblocks == 1:
        model = nmf.NmfModel(mat=m, name=f"{name}_nmf", ncomp=ncomp_min, regularization="components",
                             leverage="robust", max_iter=200)
    else:
        m_dup, m_med = utl.separate_along_median_by_cols(m)
        model = ntf.NtfModel(
            mat=m_dup,
            name=f"{name}_snmf",
            ncomp=ncomp_min,
            baseline=m_med,
            nblocks=nblocks,
            regularization="components",
            leverage="robust",
            max_iter=200)

    ncomp = ncomp_min

    while ncomp <= ncomp_max:
        model.set_ncomp(ncomp)
        # attention, refixer la sparsity après le changement de nombre de composants
        model.set_sparsity(sparsity)
        model.test_model()
        ht = model.get_h().T
        _, null_features = utl.drop_zero_columns(ht)
        _, null_components = utl.drop_zero_columns(model.get_h())
        m_reduced = m.drop(null_features, axis=1) if null_features else m
        if null_features is None:
            reduced_model = model.copy()
        else:
            if nblocks == 1:
                reduced_model = nmf.NmfModel(mat=m_reduced, name=name, ncomp=ncomp, regularization="components",
                                             leverage="robust",
                                             max_iter=200)
            else:
                m_red_dup, m_red_med = utl.separate_along_median_by_cols(m_reduced)
                reduced_model = ntf.NtfModel(
                    mat=m_red_dup,
                    ncomp=ncomp,
                    baseline=m_red_med,
                    nblocks=nblocks,
                    regularization="components",
                    leverage="robust",
                    max_iter=200)
        reduced_model.set_sparsity(0.0)
        # hcomp, hspars = reduced_model.get_h_compression()
        df_res.loc[ncomp, "NComponents"] = ncomp
        df_res.loc[ncomp, "Error_unreduced"] = model.get_precision()
        err = df_res.loc[ncomp, "Error"] = reduced_model.get_precision()
        vol = df_res.loc[ncomp, "Volume"] = reduced_model.get_volume()
        df_res.loc[ncomp, "Err/Vol"] = np.nan if vol == 0.0 else err / vol
        df_res.loc[ncomp, "Null_features"] = len(null_features)
        ncomp += 1

    if len(df_res.index) > 0 and do_save_result:
        df_res.to_csv(Path(outpath) / f"{modelstr}_test_ncomp.csv")

    return df_res


def test_missing_proportion(m, ncomp, name, imp_method="mean", grp_priors=None,
                            p_min=0.0, p_step=0.05, p_max=1.0,
                            n_trials=100, do_save_result=True, outpath=""):

    assert p_step > 0
    nstep = max(1, int((p_max - p_min) / p_step))
    df_res = pd.DataFrame(
        index=[round(i * p_step, 2) for i in range(nstep)],
        columns=["NComponents", "Error", "Volume", "Misclassifieds"],
    )
    imp_mean = imp.Imputer("mean", params={})
    imp_nmf_proxy = imp.Imputer("nmf.proxy", params={"ncomp": ncomp, "nfill_iters": 1})
    imp_nmf_fills = imp.Imputer("nmf.proxy", params={"ncomp": ncomp, "nfill_iters": 5})
    for i in range(nstep):
        p = p_min + round(i * p_step, 2)
        if p <= p_max:
            pstr = f"{round(p * 100, 1)} %"
            n_trials = max(n_trials, 1)
            df_trials = pd.DataFrame(index=range(n_trials),
                                     columns=["Error", "Volume", "Misclassifieds"])
            for itrial in range(n_trials):
                m_cens = utl.censor_data(m, p_min + i * p_step, inplace=False)
                filled_m = imp_mean.apply(m, name)
                # model = nmf.NmfModel(mat=m_cens, name=f"{name}_{pstr}_empty", ncomp=ncomp,
                #                     regularization="components", leverage="robust", max_iter=200)
                # df_trials.loc[itrial, "Error"] = imp_mean.get_precision()
                # df_trials.loc[itrial, "Volume"] = imp_mean.get_volume()
                df_trials.loc[itrial, "Misclassifieds"], _ = imp_mean.get_nb_misclassifieds(grp_priors) \
                    if grp_priors is not None \
                    else np.nan

        df_res.loc[p, "NComponents"] = ncomp
        # df_res.loc[p, "MeanError"] = df_trials["Error"].mean()
        # df_res.loc[p, "MaxError"] = df_trials["Error"].max()
        # df_res.loc[p, "MeanVolume"] = df_trials["Volume"].mean()
        # df_res.loc[p, "MinVolume"] = df_trials["Volume"].min()
        df_res.loc[p, "MeanMisClass"] = df_trials["Misclassifieds"].mean()
        df_res.loc[p, "MaxMisClass"] = df_trials["Misclassifieds"].max()

    if do_save_result:
        df_res.to_csv(Path(outpath) / f"{name}_c{ncomp}_test_missing_values.csv")
    return df_res

    pass

