import numpy as np
import pandas as pd
from . import utilities as utl
from . import nmfmodel as nmf
from . import ntfmodel as ntf
from . import clusterizer as cls
from typing import Union, Tuple
from datetime import datetime

try:
    from adganinference import AdCritic
except ImportError:
    print("Warning: adganinference package was not imported.")


class Imputer:

    def __init__(self,
                 method: str = "median",
                 fill_values: Tuple[float] = None,
                 params: dict = None):

        assert method in {"median", "mean", "values", "kmeans",
                          "nmf.kmeans", "nmf.proxy", "snmf.kmeans", "snmf.proxy"}
        self._method = method
        self._fill_values = fill_values
        self._params = params
        pass

    def __repr__(self):
        return f"Imp_{self._method}_{self._params}"

    def set_ncomp(self, nc: int):
        if self._method in {"nmf.kmeans", "nmf.proxy", "snmf.kmeans", "snmf.proxy"}:
            assert (nc >= 1)
            self._params["ncomp"] = nc

    def apply(self,
              mat: Union[np.ndarray, pd.DataFrame],
              mat_name: str = ""):

        if self._method in {"median", "mean", "values", "kmeans"}:
            ngroups = 1
            if self._method == "kmeans":
                ngroups = self._params.get("ngroups", 2)
            filled_mat = utl.fill_missing(mat, self._method, axis=0, ngroups=ngroups)
        elif self._method in {"nmf.kmeans", "nmf.proxy", "snmf.kmeans", "snmf.proxy"}:
            model = None
            ncomp = self._params.get("ncomp", 2)
            nblocks = self._params.get("nblocks", 1)
            nfill_iters = self._params.get("nfill_iters", 1)
            sparsity = self._params.get("sparsity", 0.0)
            use_hals = self._params.get("use_hals", True)
            nmf_type = self._method.split(".")[0]
            fill_type = self._method.split(".")[1]
            prefill_type = self._params.get("prefill", None)
            if nblocks == 1:
                assert(nmf_type == "nmf")
                if prefill_type is not None and prefill_type in {"median", "mean", "kmeans"}:
                    fmat = utl.fill_missing(mat, prefill_type, axis=0, ngroups=ncomp)
                else:
                    fmat = mat
                model = nmf.NmfModel(mat=fmat, name=mat_name, ncomp=ncomp,
                                     regularization="components", leverage="robust",
                                     use_hals=use_hals, max_iter=200)
                model.set_sparsity(sparsity)
            elif nblocks == 2:
                assert (nmf_type == "snmf")
                mat_dup, mat_med = utl.separate_along_median_by_cols(mat)
                if prefill_type is not None and prefill_type in {"median", "mean", "kmeans"}:
                    fmat_dup = utl.fill_missing(mat_dup, prefill_type, axis=0, ngroups=ncomp)
                else:
                    fmat_dup = mat_dup
                model = ntf.NtfModel(
                    mat=fmat_dup,
                    name=f"{mat_name}_{ncomp}_snmf",
                    ncomp=ncomp,
                    baseline=mat_med,
                    nblocks=nblocks,
                    regularization="components",
                    leverage="robust",
                    use_hals=use_hals,
                    max_iter=200)
            if model is not None:
                model.test_model(nfill_iters=nfill_iters)
                if fill_type == "proxy":
                    m_proxy = model.get_m_proxy()
                    filled_mat = utl.fill_missing(mat, method="values", fill_values=m_proxy)
                elif fill_type == "kmeans":
                    filled_mat = utl.fill_missing(model.filled_mat, "kmeans", ngroups=ncomp)
            else:
                filled_mat = None

        return filled_mat


class ImputerTester:

    def __init__(self,
                 mat: Union[np.ndarray, pd.DataFrame],
                 name: str,
                 imputer: Imputer,
                 ref_clst: cls.Clusterizer = None,
                 clst: cls.Clusterizer = None,
                 err_func: str = "MSE",
                 **kwargs):

        """

           ImputerTester.__init__:

           Parameters
           ----------
           mat: Union[np.ndarray, pd.DataFrame]: the data to test
           name: test name
           imputer: an Imputer object representing the choosen imputation method
           ref_clst: a Clusterizer object representing a benchmark classification
           clst: a Clusterizer object used to classify the imputed data and give a score
           err_func: a string coding an error function
           # todo: replace the last three parameters by a DataComparator object

           :returns:
           self
           """

        self._mat = mat
        self._name = name
        # self._grps = grps
        self._imputer = imputer
        assert(err_func in ["MSE", "Misclassifieds", "GAN_critic"])
        self._err_func = err_func
        self._ref_clusterizer = ref_clst
        self._clusterizer = clst
        if ref_clst is not None:
            assert (ref_clst.get_nbgroups() == clst.get_nbgroups())
        self._kwargs = kwargs
        self._critic_path = kwargs.get("critic_path", "")
        self._critic_name = kwargs.get("critic_name", "wgan_critic_model")
        self._critic = AdCritic(model_path=self._critic_path,
                                model_name=self._critic_name) if self._err_func.lower() == "gan_critic" else None
        self._run = 0
        self._df_results = pd.DataFrame(columns=["Dataset", "Nb Features", "Nb Obs", "Nb Groups",
                                                 "Imputation strategy",
                                                 "Clustering",
                                                 "Ref Clustering",
                                                 "Missing proportion",
                                                 "Nb Trials",
                                                 "Error Type",
                                                 "Error Min", "Error First decile",
                                                 "Error Median",
                                                 "Error Last decile", "Error Max",
                                                 "Error Stdev",
                                                 "Avg Loss"])
        pass

    def set_imputer(self, imp: Imputer):
        self._imputer = imp

    def set_mat(self, mat):
        self._mat = mat

    def set_name(self, name):
        self._name = name

    def set_clst(self, clst: cls.Clusterizer):
        self._clusterizer = clst

    def set_ref_clst(self, clst: cls.Clusterizer):
        self._ref_clusterizer = clst

    def get_nbgroups(self):
        return self._ref_clusterizer.get_nbgroups() if self._ref_clusterizer is not None else 0

    def run(self,
            missing_props: Tuple[float],
            ntrials: int):

        # imp_mean = Imputer("mean", params={})

        missing_props = sorted(set(missing_props).union({0.0}))
        n_props = len(missing_props)
        run_0 = self._run
        baseline_misclass = 0
        real_scores = []
        if self._err_func.lower() == "gan_critic":
            normed_mat, _, _ = utl.normalize_by_columns(self._mat)
            real_scores = self._critic.predict(normed_mat.values)

        for prop in missing_props:

            self._df_results.loc[self._run, "Dataset"] = self._name
            self._df_results.loc[self._run, "Nb Features"] = len(self._mat.columns)
            self._df_results.loc[self._run, "Nb Obs"] = len(self._mat.index)
            self._df_results.loc[self._run, "Nb Groups"] = self.get_nbgroups()
            self._df_results.loc[self._run, "Imputation strategy"] = self._imputer.__repr__()
            self._df_results.loc[self._run, "Clustering"] = self._clusterizer.__repr__()
            self._df_results.loc[self._run, "Ref Clustering"] = self._ref_clusterizer.__repr__()
            self._df_results.loc[self._run, "Error Type"] = self._err_func
            self._df_results.loc[self._run, "Missing proportion"] = prop
            self._df_results.loc[self._run, "Nb Trials"] = ntrials if prop > 0 else 1
            df_trials = pd.DataFrame(index=range(ntrials),
                                     columns=["Error"])
            trials = range(ntrials) if prop > 0.0 else range(1)
            rndg = np.random.default_rng(seed=42)
            # Générer les matrices remplies après censure aléatoire
            for itrial in trials:
                if prop > 0:
                    m_cens = utl.censor_data(self._mat, prop, inplace=False, randomgen=rndg)
                else:
                    m_cens = self._mat.copy()
                filled_m = self._imputer.apply(m_cens, self._name).astype(float)
                holes = m_cens.apply(lambda x: pd.isnull(x)).astype(int)
                if self._err_func.lower() != "misclassifieds":
                    if "cluster" in filled_m.columns:
                        filled_m = filled_m.drop("cluster", axis=1)
                if self._err_func.lower() == "mse":
                    df_trials.loc[itrial, "ErrorOnMissings"] = utl.relative_squared_error(np.multiply(self._mat, holes),
                                                                                          np.multiply(filled_m, holes),
                                                                                          self._mat)
                    df_trials.loc[itrial, "Error"] = utl.relative_squared_error(self._mat, filled_m)
                elif self._err_func.lower() == "misclassifieds":
                    _, df_trials.loc[itrial, "Error"] = utl.get_nb_misclassifieds(filled_m,
                                                                                  self._clusterizer,
                                                                                  self._ref_clusterizer) \
                                                        if self._clusterizer is not None \
                                                        else np.nan
                elif self._err_func.lower() == "gan_critic":
                    normed_filled_mat, _, _ = utl.normalize_by_columns(filled_m)
                    scores = self._critic.predict(normed_filled_mat)
                    # todo: compute a loss between the scores obtained on real data and the scores on imputed data
                    df_trials.loc[itrial, "Error"] = np.mean(real_scores - scores)

            errors = df_trials["Error"].astype(float)
            missings_errs = df_trials["ErrorOnMissings"].astype(float)
            self._df_results.loc[self._run, "Error Min"] = np.nanmin(errors)
            self._df_results.loc[self._run, "Error First decile"] = np.nanpercentile(errors, q=10)
            self._df_results.loc[self._run, "Error Median"] = np.nanmedian(errors)
            self._df_results.loc[self._run, "ErrorMissings Median"] = np.nanmedian(missings_errs)
            self._df_results.loc[self._run, "Error Last decile"] = np.nanpercentile(errors, q=90)
            self._df_results.loc[self._run, "Error Max"] = np.nanmax(errors)
            self._df_results.loc[self._run, "Error Stdev"] = np.nanstd(errors)
            self._df_results.loc[self._run, "Error Avg"] = np.nanmean(errors)
            baseline_misclass = self._df_results.loc[run_0, "Error Median"]
            self._run += 1

            print(f"Done {self._imputer}_({prop}) on {self._name}")

        for iprop in range(n_props):
            self._df_results.loc[run_0 + iprop, "Avg Loss"] = self._df_results.loc[run_0 + iprop, "Error Avg"] - \
                baseline_misclass

        return

    def output_results(self, outpath):

        self._df_results.to_csv(outpath / f"Imputer _{self._name}_{datetime.today().strftime('%Y-%m-%d-%H:%M')}.csv")

    pass






