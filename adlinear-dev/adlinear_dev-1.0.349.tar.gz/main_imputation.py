import pandas as pd
import os
import numpy as np
# import math

# from adlinear import pca
from adlinear import utilities as utl
from adlinear import nmfmodel as nmf
# from adlinear import testers as tst
from adlinear import imputer as imp
from adlinear import clusterizer as clu
# from adlinear import ntfmodel as ntf
from randomgenerators import randomgenerators as rng

import root_path
import dotenv
from pathlib import Path
dotenv.load_dotenv()


if __name__ == "__main__":
    # Defining paths
    # ***********************************************************************************

    root_path = root_path.get_root_path()

    rd_path = root_path / os.getenv("rd_subpath")
    imputation_paper_path = rd_path / os.getenv("imputation_paper_subpath")

    data_path = imputation_paper_path / os.getenv("data_subpath")

    temp_data_path = data_path / "temp_data/"
    pictures_path = data_path / "Pics"
    out_data_path = imputation_paper_path / "results/"

    res_path = imputation_paper_path / os.getenv("results_subpath")

    # Experiments on Brunet dataset
    if os.getenv("imp_do_brunet", "False").lower() == "true":
        df_brunet = pd.read_csv(data_path / os.getenv("brunet_filename"))
        df_brunet_groups = pd.read_csv(data_path / os.getenv("brunet_grp_filename"))
        df_brunet.loc[:, "Group"] = df_brunet_groups.loc[:, "Group"]
        ngrps_brunet = 3
        ncomp_brunet = 4
        # la colonne d'attribution des groupes
        # Brunet dataset has 3 groups, the group ALL_B being sometimes divided in two subgroups
        if ngrps_brunet == 4:
            df_brunet_priors = df_brunet.replace({"Group": {"ALL_B_1": 1,
                                                            "ALL_B_2": 2,
                                                            "ALL_T": 3,
                                                            "AML": 4}})["Group"]
        else:
            df_brunet_priors = df_brunet.replace({"Group": {"ALL_B": 1,
                                                            "ALL_T": 2,
                                                            "AML": 3}})["Group"]

        df_brunet = df_brunet[df_brunet.columns[2:]]
        df_log_brunet = df_brunet - np.nanmin(df_brunet, axis=0)
        df_log_brunet = np.log(1.0 + df_log_brunet)

        nmf_brunet = nmf.NmfModel(mat=df_brunet, name="brunet",
                                  ncomp=ncomp_brunet, regularization="components", leverage="robust", max_iter=200)
        nmf_log_brunet = nmf.NmfModel(mat=df_log_brunet, name="log_brunet",
                                      ncomp=ncomp_brunet, regularization="components", leverage="robust", max_iter=200)

        if os.getenv("imp_do_brunet_screeplot", "False").lower() == "true":
            ncmin = 1
            ncmax = 15
            df_scree_plot = nmf.generate_scree_plot(df_log_brunet, ncmin=ncmin, ncmax=ncmax, do_entropies=False)
            df_scree_plot.to_csv(res_path/"logbrunet_screeplot.csv")

        if os.getenv("imp_do_brunet_test_prop", "False").lower() == "true":
            # df_res_brunet = tst.test_missing_proportion(df_log_brunet, ncomp=ncomp_brunet,
            #                                             name="log_brunet", grp_priors=df_brunet_priors,
            #                                             p_min=0.0, p_max=0.4, p_step=0.02, n_trials=50,
            #                                             do_save_result=True, outpath=out_data_path)

            p_step = 0.05
            n_step = int(0.4 / p_step)
            missing_props = [round(i * p_step, 2) for i in range(n_step)]
            # missing_props = [0]

            clusters_brunet_priors = clu.Clusterizer(method="set_groups",
                                                     groups=df_brunet_priors,
                                                     name="Brunet_3_groups",
                                                     nb_groups=ngrps_brunet)
            clusters_nmf4_grp3 = clu.Clusterizer(method="nmf.kmeans", nb_groups=3, ncomp=4)

            imp_kmeans = imp.Imputer(method="kmeans",
                                     params={"ngroups": 3})
            imp_nmf_proxy = imp.Imputer(method="nmf.proxy",
                                        params={"ncomp": ncomp_brunet,
                                                "nfill_iters": 0})
            imp_snmf_proxy = imp.Imputer(method="snmf.proxy",
                                         params={"ncomp": ncomp_brunet,
                                                 "nblocks": 2,
                                                 "nfill_iters": 0})

            imp_mean = imp.Imputer("mean", params={})

            imputers = [imp_mean, imp_kmeans, imp_nmf_proxy, imp_snmf_proxy]
            # imputers = [imp_mean, imp_kmeans]

            # imp_tester = imp.ImputerTester(mat=df_log_brunet, name="Log_Brunet_MisClass", imputer=imp_mean,
            #                                ref_clst=clusters_brunet_priors, clst=clusters_nmf4_grp3,
            #                                err_func="Misclassifieds")
            # # missing_props = [0, 0.05]
            # for imputer in imputers:
            #     imp_tester.set_imputer(imputer)
            #     imp_tester.run(missing_props, 100)

            # imp_tester.output_results(out_data_path)

            imp_tester = imp.ImputerTester(mat=df_log_brunet, name="Log_Brunet_MSE", imputer=imp_mean,
                                           ref_clst=clusters_brunet_priors, clst=clusters_nmf4_grp3, err_func="MSE")
            for imputer in imputers:
                imp_tester.set_imputer(imputer)
                imp_tester.run(missing_props, 100)

            imp_tester.output_results(out_data_path)

    # Experiments on Epithor dataset
    if os.getenv("imp_do_epithor", "False").lower() == "true":
        df_epithor = pd.read_csv(data_path / os.getenv("epithor_filename"))
        df_epithor.drop(["Ref_Sujet", "Centre", "N°INSEE", "Code", "Suivi"], axis='columns', inplace=True)
        ncmin = 1
        ncmax = 15
        df_scree_plot = nmf.generate_scree_plot(df_epithor, ncmin=ncmin, ncmax=ncmax, do_entropies=False)
        df_scree_plot.to_csv(res_path/"df_epithor.csv")

    if os.getenv("imp_do_random", "False").lower() == "true":

        standard_noise = rng.RandomVariable(np.random.normal, 1, 0.05)

        # direct_x_clones, _ = standard_noise.apply_bias(size=[10, 100], min=0.0, max=4.0)
        # biased_x_clones, _ = standard_noise.apply_bias(size=[10, 100], signal_prop=0.1, bias=0.1, min=0.0, max=4.0)

        dict1 = {"Variable": standard_noise,
                 "Signal_prop": 0.10,
                 "Bias": 0.2,
                 "Coeff": 0.01,
                 "Min": -10,
                 "Max": 10
                 }
        dict2 = {"Variable": standard_noise,
                 "Signal_prop": 0.05,
                 "Bias": 0.1,
                 "Coeff": 0.01,
                 "Min": -10,
                 "Max": 10
                 }
        dict3 = {"Variable": standard_noise,
                 "Signal_prop": 0.20,
                 "Bias": -0.2,
                 "Coeff": 0.01,
                 "Min": -10,
                 "Max": 10
                 }
        dict4 = {"Variable": standard_noise,
                 "Signal_prop": 0.40,
                 "Bias": -0.4,
                 "Min": -10,
                 "Max": 10
                 }
        noise = {"Variable": standard_noise,
                 "Signal_prop": 0.0,
                 "Bias": 0.0,
                 "Coeff": 0.01,
                 "Min": 0,
                 "Max": 4
                 }
        var_list = [dict1, dict2, dict3, dict4]
        noise_factor = 0.50
        n_clones = 100
        n_samples = 250
        my_dls = rng.DependentLocalizedSignals(signal_dist=var_list,
                                               non_overlapping_obs=True,
                                               noise_dist=noise,
                                               cloning_mult=n_clones,
                                               n_crossproducts=30,
                                               n_noisecolumns=int(n_clones*noise_factor),
                                               nsamples=250,
                                               lbound=-10,
                                               ubound=10)
        my_dls_name = my_dls.__repr__()
        _ = my_dls()
        df_rnd_samples = my_dls.get_samples()

        rnd_ngroups = len(var_list) + 1
        df_rnd_groups = df_rnd_samples.loc[:, "Group"]
        df_rnd_mat = df_rnd_samples.drop("Group", axis=1)

        p_step = 0.05
        n_step = int(0.4 / p_step)
        missing_props = [round(i * p_step, 2) for i in range(n_step)]
        # missing_props = [0]

        clusters_rnd_priors = clu.Clusterizer(method="set_groups",
                                              groups=df_rnd_groups,
                                              name=f"{my_dls_name}_{rnd_ngroups}_groups",
                                              nb_groups=rnd_ngroups)

        clusters_nmf = clu.Clusterizer(method="nmf.kmeans", nb_groups=rnd_ngroups, ncomp=rnd_ngroups)
        clusters_kmeans = clu.Clusterizer(method="kmeans", nb_groups=rnd_ngroups, ncomp=rnd_ngroups)

        imp_kmeans = imp.Imputer(method="kmeans",
                                 params={"ngroups": rnd_ngroups})
        imp_nmf_proxy = imp.Imputer(method="nmf.proxy",
                                    params={"ncomp": rnd_ngroups,
                                            "nfill_iters": 0})
        imp_nmf_it1_proxy = imp.Imputer(method="nmf.proxy",
                                        params={"ncomp": rnd_ngroups,
                                                "nfill_iters": 1})

        imp_snmf_proxy = imp.Imputer(method="snmf.proxy",
                                     params={"ncomp": rnd_ngroups,
                                             "nblocks": 2,
                                             "nfill_iters": 0})
        imp_snmf_it1_proxy = imp.Imputer(method="snmf.proxy",
                                         params={"ncomp": rnd_ngroups,
                                                 "nblocks": 2,
                                                 "nfill_iters": 1})

        imp_nmf_fills = imp.Imputer(method="nmf.proxy", params={"ncomp": rnd_ngroups, "nfill_iters": 4})
        imp_snmf_proxy_fills = imp.Imputer(method="snmf.proxy",
                                           params={"ncomp": rnd_ngroups, "nblocks": 2, "nfill_iters": 4})
        imp_mean = imp.Imputer("mean", params={})

        imputers = [[imp_mean, clusters_kmeans],
                    [imp_kmeans, clusters_kmeans],
                    [imp_snmf_proxy, clusters_kmeans],
                    [imp_snmf_proxy, clusters_nmf]
                    ]

        # imputers = [[imp_mean, clusters_kmeans]]
        # imputers = [[imp_kmeans, clusters_kmeans]]

        imp_tester = imp.ImputerTester(mat=df_rnd_mat, name=my_dls_name, imputer=imp_mean, ref_clst=clusters_rnd_priors,
                                       clst=clusters_nmf, err_func="MSE")
        for imputer in imputers:
            imp_tester.set_imputer(imputer[0])
            imp_tester.set_clst(imputer[1])
            imp_tester.run(missing_props, 100)

        imp_tester.output_results(out_data_path)

    if os.getenv("imp_do_random_block_matrices", "False").lower() == "true":
        # Expérience pour prouver que l'imputation de valeurs via SNMF
        # donne les meilleurs résultats quand on connait le nombre exact de composants
        # nb_clusters = np.random.randint(low=5, high=40)
        nb_clusters = 5
        min_corr = np.random.uniform(low=0.70, high=0.95)
        # min_corr = 0.70
        max_corr = np.random.uniform(low=0.05, high=0.30)
        # max_corr = 0.30
        h_size = np.random.randint(low=10, high=20)
        # h_size = 200
        w_size = np.random.randint(low=10, high=100)
        # w_size = 200
        rnd_norms = True
        # eps = np.random.uniform(low=0.0, high=0.25)
        eps = 0.10
        # noinspection PyTupleAssignmentBalance
        gen_M, _, _, _ = rng.generate_nmf_reconstruction(n_comp=nb_clusters, n_feat=h_size, n_obs=w_size,
                                                         h_icorr_min=min_corr, h_icorr_max=max_corr,
                                                         random_norms=rnd_norms, epsilon=eps)
        imp_nmf_proxy = imp.Imputer(method="nmf.proxy",
                                    params={"ncomp": 3,
                                            "nblocks": 1,
                                            "nfill_iters": 0})

        imp_mean = imp.Imputer(method="mean")

        imp_nmf_proxy_mean_first = imp.Imputer(method="nmf.proxy",
                                               params={"ncomp": 3,
                                                       "nblocks": 1,
                                                       "nfill_iters": 0,
                                                       "prefill": "mean"})

        imp_nmf_proxy_pgrad = imp.Imputer(method="nmf.proxy",
                                          params={"ncomp": 3,
                                                  "nblocks": 1,
                                                  "use_hals": False,
                                                  "nfill_iters": 0})

        imputers = [[imp_mean, None],
                    [imp_nmf_proxy, None],
                    [imp_nmf_proxy_mean_first, None]]
        imp_name = "RandomBlockMatrices_2"
        wh_name = rng.generate_wh_name(w_size, h_size, nb_clusters, min_corr, max_corr, eps, rnd_norms)
        imp_tester = imp.ImputerTester(mat=gen_M, name=f"{imp_name}_{wh_name}",
                                       imputer=imp_nmf_proxy, ref_clst=None,
                                       clst=None, err_func="MSE")
        for imp in imputers:
            for nc in range(1, 20):
                imputer = imp[0]
                imputer.set_ncomp(nc)
                imp_tester.set_imputer(imputer)
                # imp_tester.run([0.05, 0.10, 0.25, 0.4], ntrials=20)
                imp_tester.run([0.01, 0.05, 0.10, 0.15], ntrials=10)

        imp_tester.output_results(out_data_path)

    if os.getenv("imp_do_nmf_with_missings", "False").lower() == "true":

        nb_clusters = 5
        min_corr = 0.7
        max_corr = 0.40
        h_size = 200
        w_size = 100
        eps = 0.10
        wclust_factor = np.random.uniform(0.25, 1.0)
        random_norms = True
        censor_rate = 0.0
        censor_indices_list = [[],
                               [[0, 0]],
                               [[0, 0], [1, 2]]]
        gen_m, gen_w, gen_h, gen_noise = rng.generate_nmf_reconstruction(n_comp=nb_clusters, n_feat=h_size,
                                                                         n_obs=w_size, h_icorr_min=min_corr,
                                                                         h_icorr_max=max_corr,
                                                                         random_norms=random_norms, epsilon=eps,
                                                                         avg_w_clust=wclust_factor)
        for censor_indices in censor_indices_list:

            utl.censor_data(mat=gen_m, censored_indices=censor_indices, inplace=True)
            rnstr = "RandNorms" if random_norms else "ConstNorms"
            wh_name = rng.generate_wh_name(w_size, h_size, nb_clusters, min_corr, max_corr, eps, random_norms,
                                           censor_indices)
            # wh_name = f"M{w_size}x{h_size}_nc{nb_clusters}_corrmin{round(min_corr,2)}_" \
            #           f"corrmax{round(max_corr,2)}_noise{round(eps,2)}_{rnstr}_mis{censor_indices}.csv"
            gen_m.to_csv(res_path / "random_nmf" / wh_name,
                         float_format="%.4f")
            gen_m_nmf = nmf.NmfModel(mat=gen_m, ncomp=nb_clusters)
            gen_m_nmf.test_model()
            nmf_w = gen_m_nmf.get_w()
            nmf_h = gen_m_nmf.get_h()
            nmf_w.to_csv(res_path / "random_nmf" / f"W_{wh_name}",
                         float_format="%.4f")
            nmf_h.to_csv(res_path / "random_nmf" / f"H_{wh_name}",
                         float_format="%.4f")
            df_scree_plot = nmf.generate_scree_plot(gen_m, ncmin=1, ncmax=15)
            df_scree_plot.to_csv(res_path / f"{wh_name}_screeplot.csv")

    if os.getenv("imp_do_screeplot_tests", "False").lower() == "true":

        nb_clusters = 12
        # nb_clusters = 1
        min_corr = 0.9
        max_corr = 0.10
        h_size = 40
        w_size = 30
        eps = 0
        random_norms = True
        censor_rate = 0.0

        read_wh_mat = (os.getenv("imp_read_whmat", "True").lower() == "true")
        rnstr = "RandNorms" if random_norms else "ConstNorms"

        censor_rates = [0.0, 0.01, 0.05, 0.10]
        for censor_rate in censor_rates:

            if read_wh_mat:
                fixed_mat_name = os.getenv("imp_wh_matname")
                fixed_w_name = os.getenv("imp_w_matname")
                fixed_h_name = os.getenv("imp_h_matname")
                rad_name = fixed_mat_name.split(".csv")[0]
                wh_name = f"{rad_name}_mis{censor_rate}.csv"
                # wh_name = "M_nc10_corrmin0.9_corrmax0.1_noise0_RandNorms_mis0.0.csv"
                gen_M = pd.read_csv(data_path / fixed_mat_name, index_col=0)
                gen_w = pd.read_csv(data_path / fixed_w_name, index_col=0)
                gen_h = pd.read_csv(data_path / fixed_h_name, index_col=0)
                # gen_M = gen_w @ gen_h
            else:
                wh_name = f"M_nc{nb_clusters}_corrmin{round(min_corr, 2)}_" \
                          f"corrmax{round(max_corr, 2)}_noise{round(eps, 2)}_{rnstr}_mis{censor_rate}.csv"
                gen_M, gen_w, gen_h, _ = rng.generate_nmf_reconstruction(n_comp=nb_clusters, n_feat=h_size,
                                                                         n_obs=w_size, h_icorr_min=min_corr,
                                                                         h_icorr_max=max_corr,
                                                                         random_norms=random_norms, epsilon=eps)

            utl.censor_data(mat=gen_M, p=censor_rate, inplace=True)
            gen_M.to_csv(res_path / "random_nmf" / wh_name,
                         float_format="%.4f")
            gen_w.to_csv(res_path / "random_nmf" / f"W_{wh_name}",
                         float_format="%.4f")
            gen_h.to_csv(res_path / "random_nmf" / f"H_{wh_name}",
                         float_format="%.4f")
            df_scree_plot = nmf.generate_scree_plot(gen_M, ncmin=6, ncmax=30)
            df_scree_plot.to_csv(res_path / f"{wh_name}_screeplot.csv")

    if os.getenv("imp_do_ecodata_gans", "False").lower() == "true":
        # expérience où l'on soumet les résultats de l'imputation à un GAN
        # localisation du modèle GAN
        path_models = Path('/media/SERVEUR/production/research_and_development/AdFactory/Models/')
        # model_name = '15_09_21_25000_epochs'
        model_name = '20_09_21_10000_epochs'
        path_output_models = path_models / model_name
        critic_name = 'wgan_critic_model'

        eco_feat_list = ['Balance_of_Trade', 'Central_Bank_Balance_Sheet', 'Corruption_Index', 'Food_Inflation',
                         'Foreign_Direct_Investment', 'GDP', 'GDP_Growth_Rate',
                         'Population', 'Terrorism_Index', 'BONDS_10Y_close']
        nb_eco_feat = len(eco_feat_list)
        nb_obs = 500

        # Données d'entrée
        eco_data_path = Path('/media/SERVEUR/production/research_and_development/AdFactory/Data/test_critic_full')
        eco_df = pd.DataFrame(index=range(nb_obs),
                              columns=eco_feat_list,
                              data=np.random.normal(size=[nb_obs, nb_eco_feat]))

        ncomp_eco = 6
        # p_step = 0.05
        # n_step = int(0.4 / p_step)
        # missing_props = [round(i * p_step, 2) for i in range(n_step)]
        imp_kmeans = imp.Imputer(method="kmeans",
                                 params={"ngroups": ncomp_eco})
        imp_nmf_proxy = imp.Imputer(method="nmf.proxy",
                                    params={"ncomp": ncomp_eco,
                                            "nfill_iters": 0})
        imp_snmf_proxy = imp.Imputer(method="snmf.proxy",
                                     params={"ncomp": ncomp_eco,
                                             "nblocks": 2,
                                             "nfill_iters": 0})
        clusters_kmeans = clu.Clusterizer(method="kmeans", nb_groups=ncomp_eco, ncomp=ncomp_eco)

        imputers = [[imp_kmeans, clusters_kmeans],
                    [imp_snmf_proxy, clusters_kmeans],
                    ]

        imp_tester = imp.ImputerTester(mat=eco_df, name="Trading_eco", imputer=imp_kmeans, ref_clst=None, clst=None,
                                       err_func="GAN_critic", critic_path=path_output_models, critic_name=critic_name)

        p_step = 0.05
        n_step = int(0.4 / p_step)
        missing_props = [round(i * p_step, 2) for i in range(n_step)]

        file_list = [f"df_{str(1000+i)[1:4]}.csv" for i in range(1, 101)]
        i_choice = range(5)
        for i in i_choice:
            mat = pd.read_csv(eco_data_path / file_list[i])
            mat = mat.drop(["Date", "Countries"], axis=1)
            imp_tester.set_mat(mat)
            imp_tester.set_name(file_list[i])
            for imputer in imputers:
                imp_tester.set_imputer(imputer[0])
                clusterizer = imputer[1]
                score_opt, scores = clu.clusterizer_optimize(clusterizer, mat)
                imp_tester.set_clst(clusterizer)

                imp_tester.run(missing_props, 100)

        imp_tester.output_results(out_data_path)

        pass
