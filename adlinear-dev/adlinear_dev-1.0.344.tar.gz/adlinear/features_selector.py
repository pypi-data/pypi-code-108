import numpy as np
import pandas as pd
from . import utilities as utl
from . import nmfmodel as nmf
from . import ntfmodel as ntf
from datetime import datetime

from pathlib import Path
from sklearn import metrics

class FeatureSelector:
    def __init__(self,
                 name="FS",
                 method: str = "random",
                 **kwargs):
        method = method.lower()
        assert(method in ["random", "nmf", "snmf",
                          "elastic_net",
                          "saved_features",
                          "score_based",
                          "none"])
        self._name = name
        self._method = method
        self._kwargs = kwargs
        self._mat = None
        self._submat = None
        self._dropped_features = None

    def get_name(self):
        return self._name

    def get_fuzzy_rank(self):
        return self._kwargs.get("fuzzy_rank", 0)

    def get_what_to_drop(self):
        what_to_drop = self._kwargs.get("what_to_drop", "null")
        assert what_to_drop in ["null", "fuzzy", "both"]
        return what_to_drop

    def get_prop_select(self):
        return self._kwargs.get("prop_select", 0.5)

    def get_nfeat_select(self):
        return self._kwargs.get("nfeat_select", 0)

    def get_ncomp(self):
        return self._kwargs.get("ncomp", 2)

    def get_nblocks(self):
        return self._kwargs.get("nblocks", 1)

    def get_sparsity(self):
        return self._kwargs.get("sparsity", 1.0)

    def get_alpha(self):
        return self._kwargs.get("alpha", 1.0)

    def get_l1_ratio(self):
        return self._kwargs.get("l1_ratio", 0.5)

    def get_submat(self):
        return self._submat

    def get_dropped_features(self):
        return self._dropped_features

    def get_base_nb_features(self):
        return len(self._mat.columns)

    def get_reduced_nb_features(self):
        return len(self._submat.columns)

    def apply(self, mat, **kwargs):
        self._mat = pd.DataFrame(mat)
        name = self._kwargs.get("name", "dataset")

        if self._method == "random":
            nfeat_select = self.get_nfeat_select()
            nfeat = len(self._mat.columns)
            if nfeat_select == 0:
                prop = self.get_prop_select()
                nfeat_select = int(prop * nfeat)
            rng = np.random.default_rng()
            kept_cols = rng.choice(range(nfeat), nfeat_select, replace=False)
            self._submat = self._mat.copy().iloc[:, kept_cols]
            dropped_cols = set(self._mat.columns).difference(self._mat.columns[kept_cols])
            self._dropped_features = dropped_cols

        elif self._method in ["nmf", "snmf"]:
            nbl = self.get_nblocks()
            is_separative = nbl > 1
            what = self.get_what_to_drop()
            rank = self.get_fuzzy_rank()
            ncomp = self.get_ncomp()
            drop_null = what in ["null"]
            drop_fuzzy = what in ["fuzzy"]

            if not is_separative:
                nmf_model = nmf.NmfModel(mat=self._mat, ncomp=self.get_ncomp(),
                                         name=name, regularization="components")
            else:
                nmf_model = ntf.NtfModel(mat=self._mat, ncomp=self.get_ncomp(), unfolded=False,
                                         nblocks=2,
                                         name=name, regularization="components")
            nmf_model.set_sparsity(self.get_sparsity())
            to_drop_features = []
            if drop_null:
                to_drop_features = nmf_model.get_null_features()
            elif drop_fuzzy:
                to_drop_features = nmf_model.get_fuzzy_features(rank)

            self._dropped_features = to_drop_features
            self._submat = self._mat.copy().drop(to_drop_features, axis=1) \
                if to_drop_features and len(to_drop_features) > 0 \
                else self._mat.copy()

        elif self._method == "none":
            self._submat = self._mat.copy()
            self._dropped_features = None

        return self._submat, self._dropped_features

    def __repr__(self):
        return f"{self._name}:{self._method}_{self._kwargs.__repr__()}"

    def output_features(self, outpath):
        df_features = pd.DataFrame(data=self._submat.columns)
        df_features.to_csv(outpath / f"_{self.__repr__()}.csv")


class FeatureSelectorTester:

    def __init__(self, name="FST", predictive_template=None, fselectors=[], dataset_name="Data", training_set=None,
                 validation_set=None, test_set=None, training_labels=None, validation_labels=None, test_labels=None,
                 classifying_y=False, **kwargs):

        def safe_copy(dataset):
            return dataset.copy() if dataset is not None else None

        self._name = name
        self._predictive_template = predictive_template
        self._full_model = None
        self._reduced_model = None
        self._fselectors = fselectors
        self._dataset_name = dataset_name
        self._full_training_set = safe_copy(training_set)
        self._reduced_training_set = safe_copy(training_set)
        self._training_labels = safe_copy(training_labels)

        self._full_validation_set = safe_copy(validation_set)
        self._reduced_validation_set = safe_copy(validation_set)
        self._validation_labels = safe_copy(validation_labels)

        self._full_test_set = safe_copy(test_set)
        self._reduced_test_set = safe_copy(test_set)
        self._test_labels = safe_copy(test_labels)
        self._has_binary_y = classifying_y

        self._kwargs = kwargs
        self._run = 0
        self._df_results = pd.DataFrame(columns=["Dataset", "Model", "Feature Selection", "Nb Features",
                                                 "Base Train Score",
                                                 "Base Test Score", "Reduced Nb Features", "Reduced Train Score",
                                                 "Reduced Test Score"])
        pass

    def set_predictive_model(self, predictive_template, **kwargs):
        self._predictive_template = predictive_template
        self._kwargs = kwargs

    def get_feature_selectors(self):
        return self._fselectors

    def set_feature_selectors(self, fselectors):
        self._fselectors = fselectors

    def get_feature_selector(self, fselector, i=0):
        return self._fselectors[i]

    def set_feature_selector(self, fselector, i=0):
        self._fselectors[i] = fselector

    def get_nb_selectors(self):
        return len(self._fselectors)

    def run(self, random_tests=0):
        # instantiation du modèle
        mdl = self._predictive_template(**self._kwargs) if len(self._kwargs) > 0 else self._predictive_template()
        if mdl is None:
            return
        self._full_model = mdl
        # apprentissage sur les données d'apprentissage complètes
        mdl.fit(self._full_training_set.values, self._training_labels.values)
        y_full_train = mdl.predict(self._full_training_set.values)
        if self._has_binary_y:
            y_full_train = np.round(y_full_train, 0)
        # calcul des scores d'apprentissage
        score_function = metrics.accuracy_score if self._has_binary_y else metrics.mean_absolute_error
        score_train_full = score_function(y_true=self._training_labels.values,
                                          y_pred=y_full_train)
        # score de validation pour lequel les y sont connus
        y_full_val = mdl.predict(self._full_validation_set.values)
        if self._has_binary_y:
            y_full_val = np.round(y_full_val, 0)
        score_val_full = score_function(y_true=self._training_labels.values,
                                        y_pred=y_full_val)
        self._df_results.loc[self._run, "Dataset"] = self._dataset_name
        self._df_results.loc[self._run, "Model"] = mdl.__repr__()
        self._df_results.loc[self._run, "Feature Selection"] = self._fselectors[0].__repr__() \
            if self.get_nb_selectors() == 1 else [fsel.get_name() for fsel in self._fselectors].__repr__()
        self._df_results.loc[self._run, "Nb Features"] = len(self._full_training_set.columns)
        self._df_results.loc[self._run, "Base Train Score"] = score_train_full
        self._df_results.loc[self._run, "Base Validation Score"] = score_val_full

        # création d'un modèle réduit
        reduced_mdl = self._predictive_template(**self._kwargs) if len(self._kwargs) > 0 \
            else self._predictive_template()
        self._reduced_model = reduced_mdl
        # parcours des stratégies d'élimination de features

        self._reduced_training_set = self._full_training_set.copy()
        self._reduced_validation_set = self._full_validation_set.copy()
        self._reduced_test_set = self._full_test_set.copy()
        not_empty = True
        for selector in self._fselectors:
            # calcul des features à éliminer
            reduced_training_set, dropped_features = selector.apply(self._reduced_training_set)
            not_empty = len(reduced_training_set.columns) > 0
            if not_empty:
                self._reduced_training_set = utl.drop_features(self._reduced_training_set, dropped_features)

                self._reduced_validation_set = utl.drop_features(self._reduced_validation_set, dropped_features)

                self._reduced_test_set = utl.drop_features(self._reduced_test_set, dropped_features)
            else:
                break

        if not_empty:
            # prédiction sur les ensembles réduits
            reduced_mdl.fit(self._reduced_training_set.values, self._training_labels.values)
        # calcul des scores sur les ensembles d'apprentissage et de validation
        # le test n'est pas en général disponible
        y_reduced_train = reduced_mdl.predict(self._reduced_training_set.values)
        if self._has_binary_y:
            y_reduced_train = np.round(y_reduced_train, 0)
        score_tr_red = score_function(y_true=self._training_labels,
                                      y_pred=y_reduced_train) if not_empty else 0
        y_reduced_val = reduced_mdl.predict(self._reduced_validation_set.values)
        if self._has_binary_y:
            y_reduced_val = np.round(y_reduced_val, 0)
        score_val_red = score_function(y_true=self._training_labels,
                                       y_pred=y_reduced_val) if not_empty else 0

        self._df_results.loc[self._run, "Reduced Nb Features"] = len(self._reduced_training_set.columns)
        self._df_results.loc[self._run, "Reduced Train Score"] = score_tr_red
        self._df_results.loc[self._run, "Reduced Validation Score"] = score_val_red

        self._run += 1

    def run_random_selections(self, nb_rand_trials=0):
        red_nbf = self.get_reduced_nb_features()
        for _ in range(nb_rand_trials):
            rand_fsel = FeatureSelector(method="random", nfeat_select=red_nbf)
            self.set_feature_selectors([rand_fsel])
            self.run()

    def get_reduced_nb_features(self):
        return 0 if self._reduced_training_set is None else len(self._reduced_training_set.columns)

    def output_all_results(self, outpath):
        self._df_results.to_csv(outpath / f"{self._name}_{datetime.today().strftime('%Y-%m-%d')}.csv")

    def output_current_model(self, dataset_name, outpath):
        if self._full_model is None:
            return
        y_pred_full = self._full_model.predict(self._full_test_set.values)
        np.savetxt(Path(outpath) / f"{dataset_name}_full_test.predict", y_pred_full, fmt="%.0f")
        np.savetxt(Path(outpath) / f"{dataset_name}_full.feat", self._full_test_set.columns, fmt="%s")
        y_pred_reduced = self._reduced_model.predict(self._reduced_test_set.values)
        np.savetxt(Path(outpath) / f"{dataset_name}_{self._fselectors}_reduced_test.predict",
                   y_pred_reduced, fmt="%.0f")
        np.savetxt(Path(outpath) / f"{dataset_name}_{self._fselectors}_reduced.feat",
                   self._reduced_test_set.columns, fmt="%s")


if __name__ == "__main__":

    fs = FeatureSelector("random", prop=2)
