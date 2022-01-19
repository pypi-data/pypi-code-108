import pandas as pd
import numpy as np
import os

from sklearn.decomposition import NMF

import adlinear.data_collector
from adlinear import pca as pca
from adlinear import utilities as utl
from adlinear import nmfmodel as nmf
# from adlinear import ntfmodel as ntf
from adlinear import testers as tst

# import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
# from pathlib import Path

import root_path
import dotenv

dotenv.load_dotenv()

# import bokeh
# from bokeh.plotting import figure, output_file, show
sns.set()


def load_sectors():
    df_sect = pd.read_csv(sectors_path / "Sectors.csv", index_col=0)
    df_w_sect = pd.read_csv(sectors_path / "weights_by_sectors.csv", index_col=0)
    return df_sect, df_w_sect


def load_scores(fname):
    if (temp_data_path / fname).is_file():
        mat = pd.read_csv(temp_data_path / fname, index_col=0)
    else:
        mat = adlinear.data_collector.collect_features_mean_values(
            primary_data_path, exclusion_list=["sector_average", "controversy", "Severity", "conflict", "ecofi"]
        )
        mat.to_csv(temp_data_path / fname)
    return mat


def plot_errors_along_fill_iteration(mat, nc, fills):
    nmf_model = nmf.NmfModel(mat=mat, ncomp=nc, regularization="components")
    nmf_model.set_sparsity(0.5)
    nmf_model.set_n_bootstrap(10)
    nmf_model.test_model(nfill_iters=fills)
    errors = pd.Series(nmf_model.errors)

    fig, ax = plt.subplots(figsize=(8, 4))
    # ax.yaxis.set_major_locator(mtick.MultipleLocator(1.00))
    ax.yaxis.set_minor_locator(mtick.MultipleLocator(1))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_ylabel("Error")
    xlabel = "#Trial"

    xa = errors.index
    # noinspection PyTypeChecker
    ax.plot(xa, errors * 100, color="blue", linewidth=4, linestyle="-")

    ax.set_xlabel(xlabel)
    ax.set_title("Error after iterated refills")
    ax.legend()
    plt.show()
    plt.gcf().savefig(pictures_path / "error_along_lines.pdf")


def plot_matrix_fill_rates_by_sector(mat, df_sectors_):
    df_fill_rate = utl.sort_columns_by_fill_rate(mat, df_sectors_).astype(float)
    df_fill_rate["M"] = np.nanmean(df_fill_rate, axis=1)
    df_fill_rate = df_fill_rate.sort_values(by="M", ascending=False, inplace=False)
    df_fill_rate["M"].to_csv(temp_data_path / "fill_rate_by_sector.csv")
    plt.subplots(figsize=(20, 10))
    # plt.xticks(rotation=45)
    ax = sns.heatmap(
        df_fill_rate.drop(columns=["Avg_rate_by_group"]),
        annot=False,
        linewidths=0,
        yticklabels=True,
        xticklabels=True,
        cmap="Blues",
        cbar_kws={"label": "Fill rate"},
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=75)
    plt.gcf().savefig(pictures_path / "fill_rates_by_sector.pdf")
    plt.show()


def plot_decreasing_h_values(nmfmodel):
    fig, ax = plt.subplots(figsize=(8, 4))
    # ax.yaxis.set_major_locator(mtick.MultipleLocator(1.00))
    ax.yaxis.set_minor_locator(mtick.MultipleLocator(1))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_ylabel("H loading")
    xlabel = ""
    s_h = nmfmodel.get_sorted_h()

    xa = s_h.index

    ax.plot(xa, s_h.iloc[:, 0], color="blue", linewidth=4, linestyle="-")
    # noinspection PyProtectedMember
    for i in range(1, nmfmodel._ncomp):
        ax.plot(xa, s_h.iloc[:, i])

    ax.set_xlabel(xlabel)
    ax.set_title("Sorted H loadings")
    ax.legend(s_h.columns, loc="upper right")
    plt.gcf().savefig(pictures_path / "decreasing_h_values.pdf")
    plt.show()


def compare_nmf_ntf_by_entropy(mat, keep_restricted, drop_unr, nbmin, nbmax, ncmin, ncmax, sp):
    df_delta_entropy = pd.DataFrame(index=range(ncmin, ncmax + 1), columns=range(nbmin, nbmax + 1))
    df_avg_diag_nmf_entropies = None
    df_avg_diag_sntf_entropies = None
    for ncomp_ in range(ncmin, ncmax + 1):
        nmf_model0, nmf_model1 = tst.compare_full_sparse_nmf_model(m=mat, ncomp=ncomp_, sparsity=sp,
                                                                   drop_unrelevant=drop_unr)
        ntf_model0, ntf_model1 = tst.compare_full_sparse_nmf_model(m=mat, ncomp=ncomp_, nblocks=2, sparsity=sp,
                                                                   drop_unrelevant=drop_unr)
        nmf_model = nmf_model1 if keep_restricted and drop_unr else nmf_model0
        ntf_model = ntf_model1 if keep_restricted and drop_unr else ntf_model0
        if nmf_model is not None and ntf_model is not None:
            for nb in range(nbmin, nbmax + 1):
                df_nmf_entropies, _ = nmf_model.get_entropies_by_cluster()
                df_avg_diag_nmf_entropies = nmf_model.get_avg_diag_entropies(nb)
                df_sntf_entropies, _ = ntf_model.get_entropies_by_cluster()
                df_avg_diag_sntf_entropies = ntf_model.get_avg_diag_entropies(nb)
                df_delta_entropy.loc[ncomp_, nb] = df_avg_diag_sntf_entropies.iloc[0, 0] - \
                                                    df_avg_diag_nmf_entropies.iloc[0, 0]

    if nbmax == nbmin and ncmax == ncmin:
        return df_delta_entropy, df_avg_diag_nmf_entropies, df_avg_diag_sntf_entropies
    else:
        return df_delta_entropy, None, None


def plot_correspondence(model, df_sectors_, path=None):

    df_obs_clusters = model.get_obs_leverage_clusters()
    common_idx = set(df_sectors_.index).intersection(set(df_obs_clusters.index))
    df_sect_clust = pd.DataFrame(index=common_idx, columns=["Sector", "NMF cluster"])
    df_sect_clust.loc[common_idx, "Sector"] = df_sectors_.loc[common_idx, df_sectors_.columns[0]]
    df_sect_clust.loc[common_idx, "NMF cluster"] = df_obs_clusters.loc[common_idx, df_obs_clusters.columns[0]]
    # df_corr = utl.build_correspondence_map(df_sect_clust)
    utl.plot_correspondence_map(df_sect_clust, path)


if __name__ == "__main__":

    # Data localization
    rootpath = root_path.get_root_path()
    rd_subpath = "research_and_development/" if os.getenv("rd_subpath") is None else os.getenv("rd_subpath")
    rd_path = rootpath / rd_subpath
    esg_subpath = "AdNMF/esg_ntf_paper" if os.getenv("esg_paper_path") is None else os.getenv("esg_paper_path")
    esg_paper_path = rd_path / esg_subpath

    sectors_path = esg_paper_path / "Base/"
    primary_data_path = esg_paper_path / "Base/scors/"
    temp_data_path = esg_paper_path / "temp_data/"
    pictures_path = esg_paper_path / "Pics"
    out_data_path = esg_paper_path / "results/"

    features_file_name = "Raw_features_no28J.csv"
    # Instantiating global variables
    df_sectors, df_w_sectors = load_sectors()

    # test_pca()
    M_unfilled = load_scores(features_file_name)
    M_unfilled.to_csv(temp_data_path / f"unfilled_{features_file_name}")
    M_filled = utl.fill_missing(M_unfilled, method="median")
    M_filled = utl.shorten_features_names(M_filled)
    M_filled.to_csv(temp_data_path / f"trimmed_and_filled_{features_file_name}")

    M_feat_corr = utl.get_features_correlation_matrix(M_filled)
    entropies = [utl.normalized_entropy(M_filled, nbins) for nbins in range(2, 20)]
    ncomp = 6

    do_plot_pca = os.getenv("esg_do_pca", "False").lower() == "true"

    if do_plot_pca:
        pca.test_pca(mat=M_filled, nc_pca=50, pictures_path=pictures_path)

    do_plot_fill_rates = os.getenv("esg_do_plot_fill_rates", "False").lower() == "true"
    if do_plot_fill_rates:
        plot_matrix_fill_rates_by_sector(mat=M_unfilled, df_sectors_=df_sectors)

    do_sk_nmf = os.getenv("esg_do_sklearn_nmf", "False").lower() == "true"
    if do_sk_nmf:
        try:
            sk_model = NMF(n_components=6, init="random", random_state=0)
            sk_W = sk_model.fit_transform(M_unfilled)
            sk_H = sk_model.components_
        except ValueError as e:
            print("SkLearn NMF does not take missing values !")

    do_screeplot = os.getenv("esg_do_screeplot", "False").lower() == "true"
    if do_screeplot:
        ncmin = 3
        ncmax = 12
        df_scree_plot = nmf.generate_scree_plot(M_unfilled, ncmin=ncmin, ncmax=ncmax)
        df_scree_plot.to_csv(out_data_path/"ESG_unfilled_screeplot.csv")

    do_imputation_test = os.getenv("esg_do_imputation_test", "False").lower() == "true"
    if do_imputation_test:
        nmf6_missing, _ = tst.compare_full_sparse_nmf_model(M_unfilled, ncomp=6, sparsity=0.0, nfills=0)
        error_missing = nmf6_missing.get_precision()
        h_missing = nmf6_missing.get_h()
        nmf6_missing_5, _ = tst.compare_full_sparse_nmf_model(M_unfilled, ncomp=6, sparsity=0.0, nfills=5)
        error_missing_5 = nmf6_missing_5.get_precision()
        nmf6_imputed_0, _ = tst.compare_full_sparse_nmf_model(M_filled, ncomp=6, sparsity=0.0, nfills=0)
        error_imputed_0 = nmf6_imputed_0.get_precision()
        h_imputed0 = nmf6_imputed_0.get_h()

    do_stats_on_variables = os.getenv("esg_do_stats_on_variables", "False").lower() == "true"
    if do_stats_on_variables:
        df_avg_sect = pd.DataFrame(index=set(np.unique(df_sectors)),
                                   columns=M_unfilled.columns,
                                   data=0)
        df_max_sect = pd.DataFrame(index=set(np.unique(df_sectors)),
                                   columns=M_unfilled.columns,
                                   data=0)
        df_minvars_by_sectors = pd.DataFrame(index=set(np.unique(df_sectors)),
                                             columns=M_unfilled.columns)
        df_nbstocks_by_sectors = pd.DataFrame(index=set(np.unique(df_sectors)),
                                              columns=M_unfilled.columns,
                                              data=0)
        for col in M_unfilled.columns:
            for isin in M_unfilled.index:
                if isin in df_sectors.index:
                    sector = df_sectors.loc[isin].iloc[0]
                    val = M_unfilled.loc[isin, col]
                    if not pd.isnull(val):
                        df_nbstocks_by_sectors.loc[sector, col] += 1
                        df_avg_sect.loc[sector, col] += val
                        df_max_sect.loc[sector, col] = np.nanmax([df_max_sect.loc[sector, col],
                                                                  val])
                        df_minvars_by_sectors.loc[sector, col] = np.nanmin([df_minvars_by_sectors.loc[sector, col],
                                                                            val])
        df_avg_sect = np.divide(df_avg_sect, df_nbstocks_by_sectors)
        df_avg_sect.loc["BestAvg", :] = np.nanmax(df_avg_sect, axis=0)
        df_avg_sect.loc["WorstAvg", :] = np.nanmin(df_avg_sect, axis=0)
        df_avg_sect.loc["Dispersion", :] = df_avg_sect.loc["BestAvg", :] - df_avg_sect.loc["WorstAvg", :]
        df_avg_sect.loc["WorstSector", :] = df_avg_sect.index[np.apply_over_axes(np.argmin,
                                                                                 df_avg_sect.iloc[0:-3, :],
                                                                                 axes=0)]
        df_avg_sect.loc["BestSector", :] = df_avg_sect.index[np.apply_over_axes(np.argmax,
                                                                                df_avg_sect.iloc[0:-3, :],
                                                                                axes=0)]

        df_avg_sect.loc[:, "BestScore"] = df_avg_sect.columns[np.apply_over_axes(np.argmax,
                                                                                 df_avg_sect.iloc[:, :],
                                                                                 axes=1)]
        df_avg_sect.loc[:, "WorstScore"] = df_avg_sect.index[np.apply_over_axes(np.argmin,
                                                                                df_avg_sect.iloc[:, 0:-1],
                                                                                axes=1)]
        df_avg_sect.to_csv(out_data_path / "df_avg_by_sectors.csv")
        pass

    do_features = False
    if do_features:
        sp_nmf6, _ = tst.compare_full_sparse_nmf_model(M_unfilled, ncomp=6, drop_unrelevant=True, do_plot=True)
        ntf6, dense_ntf6 = tst.compare_full_sparse_nmf_model(M_filled, ncomp=6, nblocks=2, drop_unrelevant=True,
                                                             do_plot=False)
        nmf_feat_compo = sp_nmf6.get_features_by_decreasing_loading(min_contribution=0.2)
        ntf_feat_compo = ntf6.get_features_by_decreasing_loading(min_contribution=0.2)
        dense_nmf_feat_compo = sp_nmf6.get_features_by_decreasing_loading(min_contribution=0.2)
        dense_ntf_feat_compo = ntf6.get_features_by_decreasing_loading(min_contribution=0.2)
        sp_nmf6.get_h().to_csv(temp_data_path / "nmf6_h.csv")
        ntf6.get_h().to_csv(temp_data_path / "ntf6_h.csv")
        nmf_feat_compo.to_csv(temp_data_path / "nmf6_feat_compo.csv")
        ntf_feat_compo.to_csv(temp_data_path / "ntf6_feat_compo.csv")
        dense_nmf_feat_compo.to_csv(temp_data_path / "dense_nmf6_feat_compo.csv")
        dense_ntf_feat_compo.to_csv(temp_data_path / "dense_ntf6_feat_compo.csv")
        plot_correspondence(ntf6, df_sectors, pictures_path / "correspondance.pdf")
    nbins = 3
    ncomp = 6

    do_sparsity = False
    # cette étape pour fixer la vacuité optimale dans les modèles
    if do_sparsity:
        for ncomp in [6]:
            df_sparsity_results_nmf = tst.test_nmf_sparsity(M_unfilled, ncomp_=ncomp)
            df_sparsity_results_nmf.to_csv(temp_data_path / f"nmf{ncomp}_sparsity.csv")
            df_sparsity_results_ntf = tst.test_nmf_sparsity(M_filled, nblocks=2, ncomp_=ncomp)
            df_sparsity_results_ntf.to_csv(temp_data_path / f"ntf{ncomp}_sparsity.csv")

    do_comparison = True
    if do_comparison:
        df_comparison = pd.DataFrame(
            index=["nmf", "sparse_nmf", "restricted_nmf",
                   "snmf", "sparse_snmf", "restricted_snmf"],
            columns=["ncomp", "effective_dim", "sparsity", "error", "Clustering entropy", "Matrix entropy", "Delta"],
        )
        nmf6, _ = tst.compare_full_sparse_nmf_model(M_filled, ncomp=6, sparsity=0.0, drop_unrelevant=False,
                                                    do_plot=True, pictures_path=pictures_path)
        df_comparison.loc["nmf", "ncomp"] = nmf6.ncomp
        df_comparison.loc["nmf", "effective_dim"] = nmf6.get_effective_dimension()
        df_comparison.loc["nmf", "sparsity"] = nmf6.get_target_sparsity()
        df_comparison.loc["nmf", "error"] = nmf6.get_precision()
        ce = df_comparison.loc["nmf", "Clustering entropy"] = nmf6.get_avg_diag_entropies(relative=False).iloc[0, 0]
        me = df_comparison.loc["nmf", "Matrix entropy"] = utl.normalized_entropy(nmf6.origin_mat)
        df_comparison.loc["nmf", "Delta"] = ce / me - 1

        sp_nmf6, restricted_nmf6 = tst.compare_full_sparse_nmf_model(M_filled, ncomp=6, sparsity=0.9,
                                                                     drop_unrelevant=True,
                                                                     do_plot=True, pictures_path=pictures_path)
        df_comparison.loc["sparse_nmf", "ncomp"] = sp_nmf6.ncomp
        df_comparison.loc["sparse_nmf", "effective_dim"] = sp_nmf6.get_effective_dimension()
        df_comparison.loc["sparse_nmf", "sparsity"] = sp_nmf6.get_target_sparsity()
        df_comparison.loc["sparse_nmf", "error"] = sp_nmf6.get_precision()
        ce = df_comparison.loc["sparse_nmf", "Clustering entropy"] = \
            sp_nmf6.get_avg_diag_entropies(relative=False).iloc[0, 0]
        me = df_comparison.loc["sparse_nmf", "Matrix entropy"] = \
            utl.normalized_entropy(sp_nmf6.origin_mat)
        df_comparison.loc["sparse_nmf", "Delta"] = ce / me - 1

        # noinspection PyProtectedMember
        df_comparison.loc["restricted_nmf", "ncomp"] = restricted_nmf6._ncomp
        df_comparison.loc["restricted_nmf", "effective_dim"] = restricted_nmf6.get_effective_dimension()
        df_comparison.loc["restricted_nmf", "sparsity"] = restricted_nmf6.get_target_sparsity()
        df_comparison.loc["restricted_nmf", "error"] = restricted_nmf6.get_precision()
        ce = df_comparison.loc["restricted_nmf", "Clustering entropy"] = \
            restricted_nmf6.get_avg_diag_entropies(relative=False).iloc[0, 0]
        me = df_comparison.loc["restricted_nmf", "Matrix entropy"] = \
            utl.normalized_entropy(restricted_nmf6.origin_mat)
        df_comparison.loc["restricted_nmf", "Delta"] = ce / me - 1

        sp_snmf6, _ = tst.compare_full_sparse_nmf_model(M_filled, ncomp=6, nblocks=2, sparsity=0.0, nfills=5,
                                                        drop_unrelevant=False,
                                                        do_plot=True, pictures_path=pictures_path)
        # noinspection PyProtectedMember
        df_comparison.loc["snmf", "ncomp"] = sp_snmf6._ncomp
        df_comparison.loc["snmf", "effective_dim"] = sp_snmf6.get_effective_dimension()
        df_comparison.loc["snmf", "sparsity"] = sp_snmf6.get_target_sparsity()
        df_comparison.loc["snmf", "error"] = sp_snmf6.get_precision()
        ce = df_comparison.loc["snmf", "Clustering entropy"] = \
            sp_snmf6.get_avg_diag_entropies(relative=False).iloc[0, 0]
        me = df_comparison.loc["snmf", "Matrix entropy"] = utl.normalized_entropy(sp_snmf6.origin_mat)
        df_comparison.loc["snmf", "Delta"] = ce / me - 1

        sp_snmf6, restricted_snmf6 = tst.compare_full_sparse_nmf_model(M_filled, ncomp=6, nblocks=2, sparsity=0.9,
                                                                       nfills=5,
                                                                       drop_unrelevant=True,
                                                                       do_plot=True, pictures_path=pictures_path)
        # noinspection PyProtectedMember
        df_comparison.loc["sparse_snmf", "ncomp"] = sp_snmf6._ncomp
        df_comparison.loc["sparse_snmf", "effective_dim"] = sp_snmf6.get_effective_dimension()
        df_comparison.loc["sparse_snmf", "sparsity"] = sp_snmf6.get_target_sparsity()
        df_comparison.loc["sparse_snmf", "error"] = sp_snmf6.get_precision()
        ce = df_comparison.loc["sparse_snmf", "Clustering entropy"] = \
            sp_snmf6.get_avg_diag_entropies(relative=False).iloc[0, 0]
        me = df_comparison.loc["sparse_snmf", "Matrix entropy"] = \
            utl.normalized_entropy(sp_snmf6.origin_mat)
        df_comparison.loc["sparse_snmf", "Delta"] = ce / me - 1

        # noinspection PyProtectedMember
        df_comparison.loc["restricted_snmf", "ncomp"] = restricted_snmf6._ncomp
        df_comparison.loc["restricted_snmf", "effective_dim"] = \
            restricted_snmf6.get_effective_dimension()
        df_comparison.loc["restricted_snmf", "sparsity"] = \
            restricted_snmf6.get_target_sparsity()
        df_comparison.loc["restricted_snmf", "error"] = \
            restricted_snmf6.get_precision()
        ce = df_comparison.loc["restricted_snmf", "Clustering entropy"] = \
            restricted_snmf6.get_avg_diag_entropies(relative=False).iloc[0, 0]
        me = df_comparison.loc["restricted_snmf", "Matrix entropy"] = \
            utl.normalized_entropy(restricted_snmf6.origin_mat)
        df_comparison.loc["restricted_snmf", "Delta"] = ce / me - 1

        df_comparison.to_csv(temp_data_path / "sparse_vs_restricted_models.csv")

    do_compare_diag_entropies = True
    if do_compare_diag_entropies:
        df_delta, diag_nmf, diag_ntf = compare_nmf_ntf_by_entropy(
            M_filled, keep_restricted=True, drop_unr=True,
            nbmin=nbins, nbmax=nbins, ncmin=ncomp, ncmax=ncomp, sp=0.9
        )
        diag_nmf.to_csv(temp_data_path / f"nmf_diag_entropiesc{ncomp}b{nbins}.csv")
        diag_ntf.to_csv(temp_data_path / f"ntf_diag_entropiesc{ncomp}b{nbins}.csv")
        df_delta.to_csv(temp_data_path / f"avg_delta_entropyc{ncomp}b{nbins}.csv")
