import pandas as pd
import os
import numpy as np
# import math

# from sklearn.decomposition import NMF

# from adlinear import pca
from adlinear import utilities as utl
from adlinear import nmfmodel as nmf
from adlinear import testers as tst
from adlinear import features_selector as fs
from randomgenerators import randomgenerators as rng
# from adlinear import ntfmodel as ntf
from sklearn.svm import SVC, SVR
from sklearn.linear_model import ElasticNet

# import matplotlib
# import matplotlib.pyplot as plt
# import matplotlib.ticker as mtick
# import seaborn as sns
from pathlib import Path

import rulefit
import CoveringAlgorithm.CA as CA
from sklearn.ensemble import RandomForestRegressor

import root_path
import dotenv
dotenv.load_dotenv()


if __name__ == "__main__":

    root_path = root_path.get_root_path()

    rd_path = root_path / os.getenv("rd_subpath")
    sparsity_paper_path = rd_path / os.getenv("sparsity_paper_subpath")

    data_path = sparsity_paper_path / os.getenv("data_subpath")

    temp_data_path = data_path / "temp_data/"
    pictures_path = data_path / "Pics"
    out_data_path = sparsity_paper_path / "results/"
    codalab_data_path = sparsity_paper_path / "codalab"

    if os.getenv("sp_do_brunet", "False").lower() == "true":
        # Récupérer le jeu de données
        df_brunet = pd.read_csv(data_path / os.getenv("brunet_filename"))
        # récupérer le fichier des groupes
        df_brunet_groups = pd.read_csv(data_path / os.getenv("brunet_grp_filename"))
        df_brunet.loc[:, "Group"] = df_brunet_groups.loc[:, "Group"]
        # la colonne d'attribution des groupes
        df_brunet_priors = df_brunet.replace({"Group": {"ALL_B_1": 1,
                                                        "ALL_B_2": 2,
                                                        "ALL_T": 3,
                                                        "AML": 4}})["Group"]
        # Enlever la première colonne d'étiquettes
        df_brunet = df_brunet[df_brunet.columns[2:]]
        # Appliquer la transformation log par rapport au minimum
        df_log_brunet = df_brunet - np.nanmin(df_brunet, axis=0)
        df_log_brunet = np.log(1.0 + df_brunet)

        # Fixer le nombre de composants nmf
        ncomp_brunet = 4
        nmf_brunet = nmf.NmfModel(mat=df_brunet, name="brunet",
                                  ncomp=ncomp_brunet, regularization="components", leverage="robust", max_iter=200)
        nmf_log_brunet = nmf.NmfModel(mat=df_log_brunet, name="log_brunet",
                                      ncomp=ncomp_brunet, regularization="components", leverage="robust", max_iter=200)

#        sparse_res = tst.test_nmf_sparsity(df_brunet, priors=df_brunet_priors, ncomp=ncomp_brunet, nblocks=1,
#                                               sp_step=0.1, sp_min=0, sp_max=1,
#                                               outpath=out_data_path, do_save_result=True, name="brunet")
        sparse_res2 = tst.test_nmf_sparsity(df_log_brunet, priors=df_brunet_priors, ncomp=ncomp_brunet, nblocks=2,
                                                sp_step=0.1, sp_min=0, sp_max=1,
                                                outpath=out_data_path, do_save_result=True, name="log_brunet")
        brunet_sparsity = 0.0
    # Dataprep Arcene
    if os.getenv("sp_do_arcene", "True").lower() == "true":
        # data_path = Path('/home/cgeissler/local_data/Article_sparsity/data/')
        dataset_name = os.getenv("arcene_name")
        df_arcene_X_tr = pd.read_csv(data_path / os.getenv("arcene_train_filename"),
                                     sep=" ",
                                     header=None)
        # récupérer les en-tête de colonnes comme chaines
        df_arcene_X_tr.columns = [str(x) for x in df_arcene_X_tr.columns]
        nf = len(df_arcene_X_tr.columns)
        # remove last column full on nan's
        df_arcene_X_tr = df_arcene_X_tr.iloc[:, 0:nf - 2]

        # lecture des étiquettes d'apprentissage
        df_arcene_y_tr = pd.read_csv(data_path / os.getenv("arcene_train_labels"),
                                     sep=" ",
                                     header=None)
        # lecture des variables de test
        df_arcene_X_te = pd.read_csv(data_path / os.getenv("arcene_test_filename"),
                                     sep=" ",
                                     header=None)
        df_arcene_X_te.columns = [str(x) for x in df_arcene_X_te.columns]
        nf = len(df_arcene_X_te.columns)
        # remove last column full on nan's
        df_arcene_X_te = df_arcene_X_te.iloc[:, 0:nf - 2]

        # lecture des variables de validation
        df_arcene_X_va = pd.read_csv(data_path / os.getenv("arcene_valid_filename"),
                                     sep=" ",
                                     header=None)
        df_arcene_X_va.columns = [str(x) for x in df_arcene_X_va.columns]
        nf = len(df_arcene_X_va.columns)
        # remove last column full on nan's
        df_arcene_X_va = df_arcene_X_va.iloc[:, 0:nf - 2]
        # étiquettes de validation
        df_arcene_y_va = pd.read_csv(data_path / os.getenv("arcene_valid_labels"),
                                     sep=" ",
                                     header=None)

        # Screeplot = dépendance au nombre de composants NMF sur arcene training
        if os.getenv("sp_do_arcene_screeplot", "True").lower() == "true":
            # Tests nmf en parcimonie adaptative et pour différents nombres de composants
            screeplot_res_snmf = tst.test_nmf_ncomp(df_arcene_X_tr, priors=None, ncomp_min=21, ncomp_max=20, nblocks=2,
                                                    sparsity=1.0,
                                                    outpath=out_data_path, do_save_result=True, name=dataset_name)
            screeplot_res_nmf = tst.test_nmf_ncomp(df_arcene_X_tr, priors=None, ncomp_min=2, ncomp_max=17, nblocks=1,
                                                   sparsity=1.0,
                                                   outpath=out_data_path, do_save_result=True, name=dataset_name)
        # Etude d'influence de la parcimonie sur arcene
        if os.getenv("sp_do_arcene_sparsity", "True").lower() == "true":
            # Tests nmf avec 8 composants et différents niveaux de parcimonie
            sparse_res_nmf = tst.test_nmf_sparsity(df_arcene_X_tr, priors=None, ncomp=8, nblocks=1,
                                                   sp_step=0.20, sp_min=0, sp_max=1,
                                                   outpath=out_data_path, do_save_result=True, name=dataset_name)

            sparse_res_ntf = tst.test_nmf_sparsity(df_arcene_X_tr, priors=None, ncomp=9, nblocks=2,
                                                   sp_step=0.20, sp_min=0, sp_max=1,
                                                   outpath=out_data_path, do_save_result=True, name=dataset_name)
        # Influence de la sélection de variables sur le modèle prédictif arcene / svm
        if os.getenv("sp_do_arcene_svm", "True").lower() == "true":
            # Tester la performance d'un modèle
            models_params = [[SVC, ]]
            x_train = df_arcene_X_tr
            x_valid = df_arcene_X_va
            y_train = df_arcene_y_tr
            y_valid = df_arcene_y_va
            x_test = df_arcene_X_te

            for model_params in models_params:
                model = models_params[0]
                params = models_params[1]
                full_model = model.__init__(params)
                full_model.fit(x_train, y_train)
                score_tr_full = full_model.score(x_train, y_train)
                score_va_full = full_model.score(x_valid, y_valid)
                predict_test_full = full_model.predict(x_test)

                arcene_nmf = nmf.NmfModel(mat=x_train, ncomp=8, name=dataset_name, regularization="components")
                arcene_nmf.set_sparsity(1.0)

                ht = arcene_nmf.get_h().T
                _, null_arcene_features = utl.drop_zero_columns(ht)

                df_arcene_X_tr_red = df_arcene_X_tr.drop(null_arcene_features, axis=1) \
                    if null_arcene_features \
                    else df_arcene_X_tr
                df_arcene_X_va_red = df_arcene_X_va.drop(null_arcene_features, axis=1) \
                    if null_arcene_features \
                    else df_arcene_X_va
                df_arcene_X_te_red = df_arcene_X_te.drop(null_arcene_features, axis=1) \
                    if null_arcene_features \
                    else df_arcene_X_te

                arcene_nmf_red = nmf.NmfModel(mat=df_arcene_X_tr_red, ncomp=8, name=dataset_name,
                                              regularization="components")
                fuzzy_features = arcene_nmf_red.get_fuzzy_features(1)
                df_arcene_X_tr_red = df_arcene_X_tr_red.drop(fuzzy_features, axis=1) \
                    if fuzzy_features \
                    else df_arcene_X_tr
                df_arcene_X_va_red = df_arcene_X_va_red.drop(fuzzy_features, axis=1) \
                    if fuzzy_features \
                    else df_arcene_X_va
                df_arcene_X_te_red = df_arcene_X_te_red.drop(fuzzy_features, axis=1) \
                    if fuzzy_features \
                    else df_arcene_X_te

                svc_model_red = SVC()
                svc_model_red.fit(df_arcene_X_tr_red, df_arcene_y_tr)
                score_tr_red = svc_model_red.score(df_arcene_X_tr_red, df_arcene_y_tr)
                score_va_red = svc_model_red.score(df_arcene_X_va_red, df_arcene_y_va)
                predict_test_red = svc_model_red.predict(df_arcene_X_te_red)
                predict_test_red = np.maximum(predict_test_red, 0.0)
                np.savetxt(Path(out_data_path) / f"arcene_test.predict", predict_test_red, fmt="%.0f")
                np.savetxt(Path(out_data_path) / f"arcene_test.feat", df_arcene_X_tr_red.columns, fmt="%s")

                df_svm_scores = pd.DataFrame(index=['Full', 'Reduced'],
                                             columns=['Training', 'Validation'])

                df_svm_scores.loc['Full', 'Training'] = score_tr_full
                df_svm_scores.loc['Reduced', 'Training'] = score_tr_red
                df_svm_scores.loc['Full', 'Validation'] = score_va_full
                df_svm_scores.loc['Reduced', 'Validation'] = score_va_red
                df_svm_scores.to_csv(Path(out_data_path) / f"arcene_svm_scores.csv")

        # Comparaison de méthodes de sélection de variables sur arcene
        if os.getenv("sp_do_arcene_fs", "True").lower() == "true":

            f_sel = fs.FeatureSelector(method="random")
            # Testeur de sélection sur
            selection_tester = fs.FeatureSelectorTester("Arcene_SVC_tester_w_random", predictive_template=None,
                                                        fselectors=[f_sel], dataset_name=dataset_name,
                                                        training_set=df_arcene_X_tr, validation_set=df_arcene_X_va,
                                                        test_set=df_arcene_X_te, training_labels=df_arcene_y_tr,
                                                        validation_labels=df_arcene_y_va, classifying_y=True)
            nb_rand_trials = 100
            selection_tester.set_predictive_model(SVC)
            # Test de RuleFit
            selection_tester.set_predictive_model(rulefit.RuleFit,
                                                  tree_size=4,
                                                  max_rules=500,
                                                  random_state=140,
                                                  rfmode="regress")
            # selection_tester.set_predictive_model(CA.CA)

            for ncomp in range(3, 8):
                non_null_snmf_fsel = fs.FeatureSelector(method="snmf", ncomp=ncomp, sparsity=1.0, nblocks=2)

                non_fuzzy_snmf_fsel = fs.FeatureSelector(name=f"OptimalNonFuzzy_{ncomp}", method="snmf", nblocks=2,
                                                         ncomp=ncomp, sparsity=1.0,
                                                         what_to_drop="fuzzy",
                                                         fuzzy_rank=-1)
                non_null_snmf_fsel = fs.FeatureSelector(name=f"NonNull_{ncomp}", method="snmf", nblocks=2,
                                                        ncomp=ncomp, sparsity=1.0,
                                                        what_to_drop="null")
                # Elimination par sparsity
                selection_tester.set_feature_selectors([non_null_snmf_fsel])
                selection_tester.run()
                selection_tester.run_random_selections(nb_rand_trials)

                # Elimination des features nulles, puis des floues
                # selection_tester.set_feature_selectors([non_null_snmf_fsel, non_fuzzy_snmf_fsel])
                # selection_tester.run()
                # selection_tester.output_current_model(dataset_name=dataset_name, outpath=Path(out_data_path))
                # selection_tester.run_random_selections(nb_rand_trials)

                # Eliminer d'abord les features floues puis les nulles
                # selection_tester.set_feature_selectors([non_fuzzy_snmf_fsel, non_null_snmf_fsel])
                # selection_tester.run()
                # non_fuzzy_nmf_fsel.output_features(outpath=Path(out_data_path))
                # selection_tester.output_current_model(dataset_name=dataset_name, outpath=Path(out_data_path))
                # selection_tester.run_random_selections(nb_rand_trials)

            selection_tester.output_all_results(outpath=Path(out_data_path))
            selection_tester.output_current_model(dataset_name=dataset_name, outpath=Path(out_data_path))

    if os.getenv("sp_do_random_fs", "True").lower() == "true":

        standard_noise = rng.RandomVariable(np.random.normal, 1, 0.05)
        signal_prop = 0.50

        dict1 = {"Variable": standard_noise,
                 "Signal_prop": signal_prop,
                 "Coeff": 0.001,
                 "Bias": 0.2,
                 "Min": -10,
                 "Max": 10
                 }
        dict2 = {"Variable": standard_noise,
                 "Signal_prop": signal_prop,
                 "Coeff": 0.001,
                 "Bias": 0.1,
                 "Min": -10,
                 "Max": 10
                 }
        dict3 = {"Variable": standard_noise,
                 "Signal_prop": signal_prop,
                 "Coeff": 0.001,
                 "Bias": -0.2,
                 "Min": -10,
                 "Max": 10
                 }
        dict4 = {"Variable": standard_noise,
                 "Signal_prop": signal_prop,
                 "Coeff": 0.001,
                 "Bias": -0.4,
                 "Min": -10,
                 "Max": 10
                 }
        noise = {"Variable": standard_noise,
                 "Signal_prop": 0.0,
                 "Bias": 0.0,
                 "Min": -10,
                 "Max": 10
                 }

        var_list = [dict1, dict2, dict3, dict4]
        n_clones = 100
        n_samples = 500
        noise_factor = 1
        my_dls = rng.DependentLocalizedSignals(signal_dist=var_list,
                                               non_overlapping_obs=False,
                                               # random_columns=False,
                                               noise_dist=noise,
                                               cloning_mult=n_clones,
                                               n_crossproducts=0,
                                               n_noisecolumns=n_clones*noise_factor,
                                               nsamples=n_samples,
                                               lbound=0.0,
                                               ubound=100.0)
        my_dls_name = my_dls.__repr__()
        _ = my_dls()
        df_rand_samples = my_dls.get_samples()

        # prendre la somme des variables à signal
        y_rand = df_rand_samples.iloc[:, [i * n_clones for i in range(len(var_list))]].sum(axis=1)

        # rnd_ngroups = len(var_list) + 1
        rand_ngroups = len(var_list)
        df_rand_groups = df_rand_samples.loc[:, "Group"]
        df_rand_mat = df_rand_samples.drop("Group", axis=1)

        x_rand_tr = df_rand_mat.iloc[0: int(n_samples / 2), :]
        y_rand_tr = y_rand.iloc[0: int(n_samples / 2)]
        x_rand_val = df_rand_mat.iloc[int(n_samples / 2):, :]
        y_rand_val = y_rand.iloc[int(n_samples / 2):]
        x_rand_test = df_rand_mat.iloc[int(n_samples / 2):, :]
        y_rand_test = y_rand.iloc[int(n_samples / 2):]

        f_sel = fs.FeatureSelector()
        # Testeur de sélection
        # Comm
        selection_tester = fs.FeatureSelectorTester("Random_Regression_tester", predictive_template=None,
                                                    fselectors=[f_sel], training_set=x_rand_tr,
                                                    validation_set=x_rand_val, test_set=x_rand_test,
                                                    training_labels=y_rand_tr, validation_labels=y_rand_val)

        nb_rand_trials = 100
        # Test de RuleFit
        selection_tester.set_predictive_model(rulefit.RuleFit,
                                              tree_size=4,
                                              max_rules=500,
                                              random_state=140,
                                              model_type="regress")
        # selection_tester.set_predictive_model(rulefit.RuleFit, tree_size=4)

        non_null_nmf_fsel = fs.FeatureSelector(name=f"RandomSet_{rand_ngroups}",
                                               method="snmf", nblocks=2,
                                               ncomp=rand_ngroups, sparsity=1.0,
                                               what_to_drop="null")

        selection_tester.set_feature_selectors([non_null_nmf_fsel])
        selection_tester.run()
        selection_tester.run_random_selections(nb_rand_trials)

        # non_fuzzy_nmf_fsel = fs.FeatureSelector(name=f"RandomSet_{rand_ngroups}",
        #                                         method="snmf", nblocks=2,
        #                                         ncomp=rand_ngroups, sparsity=1.0,
        #                                         what_to_drop="fuzzy",
        #                                         fuzzy_rank=-1)
        #
        # selection_tester.set_feature_selectors([non_fuzzy_nmf_fsel])
        # selection_tester.run()
        # selection_tester.run_random_selections(nb_rand_trials)

        selection_tester.output_all_results(outpath=Path(out_data_path))
        pass

    pass
