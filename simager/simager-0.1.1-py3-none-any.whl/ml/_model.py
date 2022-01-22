from simager.ml._pipelines import PipelineGenerator
from simager.ml._grid_params import GridParamas
from simager.ml._bayes_params import BayesParamas
from simager.ml._modelops import save_model
from lightgbm import LGBMClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from imblearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
import os
import logging
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import plot_confusion_matrix
from skopt import BayesSearchCV
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class CustomCatBoostClassifier(CatBoostClassifier):

    def fit(self, X, y=None, **fit_params):
        return super().fit(
            X,
            y=y,
            **fit_params
        )


class AutoClassifier(object):
    """ The core model which orchestrates everything

    Args:
        config_data (object, required)

        config_preprocess (object, required)

        config_model (object, required)

    """

    def __init__(self,
                 config_data,
                 config_preprocess,
                 config_model
                 ):
        self.dc = config_data
        self.pc = config_preprocess
        self.mc = config_model
        self.pipe = PipelineGenerator(self.dc, self.pc)
        self.cpu_count = os.cpu_count() - 1
        self.clf = {
            "DecisionTreeClassifier": DecisionTreeClassifier(),
            "KNeighborsClassifier": KNeighborsClassifier(),
            "LogisticRegression": LogisticRegression(),
            "SVC": SVC(),
            "RandomForestClassifier": RandomForestClassifier(),
            "AdaBoostClassifier": AdaBoostClassifier(),
            "XGBClassifier": XGBClassifier(n_jobs=self.cpu_count),
            "LGBMClassifier": LGBMClassifier(n_jobs=self.cpu_count),
            "CatBoostClassifier": CustomCatBoostClassifier(thread_count=self.cpu_count, logging_level="Silent")
        }
        self.name, self.best_model = None, None

    def metrics(self, y_test, y_pred):
        metric = classification_report(y_test, y_pred, output_dict=True)
        sim_metric = {
            "accuracy": metric["accuracy"],
            "precision": metric["macro avg"]["precision"],
            "recall": metric["macro avg"]["recall"],
            "f1": metric["macro avg"]["f1-score"]
        }
        return sim_metric, sim_metric.get(self.mc.metrics, 0)

    def fit(self, data, return_model=False):
        """Fit Classification

        Args:
            data (pandas.DataFrame, required): Tabular data, this data will split into train anda test automatically based on data configuration

            return_model (bool, optional): Return model object. Default to False

        """
        base_pipe = self.pipe.generate_pipe()

        X = data.drop(columns=self.dc.target)
        y = data[self.dc.target]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X,
                                                                                y,
                                                                                test_size=self.dc.test_size,
                                                                                random_state=self.dc.random_state
                                                                                )
        tmp_metric = 0
        logging.info("==================")
        for cl in self.mc.algorithm:
            mypipeline = base_pipe.copy()
            # model = None
            # mypipeline = self.pipe.generate_pipe()
            mypipeline.append(("estimator", self.clf[cl]))
            model = Pipeline(mypipeline)
            # logging.info(pipeline2str(model))
            model = model.fit(self.X_train, self.y_train)
            # logging.info(model.score(X_test, y_test))
            y_pred = model.predict(self.X_test)
            # logging.info(classification_report(y_test, y_pred))
            all_metrics, metric = self.metrics(self.y_test, y_pred)
            logging.info(f"{cl} - {self.mc.metrics}: {metric}")
            if tmp_metric < metric:
                self.name, self.best_model = cl, model
                tmp_metric = metric
                report = classification_report(self.y_test, y_pred)
        logging.info("==================")
        logging.info(f"Best Model {self.name} with {self.mc.metrics}: {tmp_metric}")
        logging.info("==================")
        logging.info("Classification Report")
        print(report)
        if return_model:
            return self.best_model

    def hp_tuning(self, search="bayes", params=None, n_jobs=None, cv=5, return_model=False, verbose=0):
        """Hyperparameters tunning
        Hyperparameters tunning will be use best models from fitting models

        Args:
            search(str, optional): Searching method to run hyperparameters tunning. Default to `bayes`
                `bayes` (BayesSearchCV): Bayesian optimization over hyper parameters.
                `grid` (GridSearchCV): Grid optimization over hyper parameters.

            params (dict, optional): Parameters tunning, default to None
                If None, parameter will be use recommendation from simager

            n_jobs (int, optional): Number of jobs to run in parallel. Default to None
                If None, means that (cpu_count - 1)

            cv (int, optional): Determines the cross-validation splitting strategy. Defaults to 5

            return_model (bool, optional): Return model object. Default to False

            verbose (int, optional): Controls the verbosity: the higher, the more messages. Default to 0
                Values: 0-3

        """
        params_maps = {
            "bayes": BayesParamas.AllParams[self.name],
            "grid": GridParamas.AllParams[self.name]
        }
        estimator = self.best_model
        if params is None:
            params = params_maps[search]
        if n_jobs is None:
            n_jobs = self.cpu_count
        params = self.normalize_params(params)
        logging.info(f"Hyperparameter tuning using: {params}")

        if search == "bayes":
            model = BayesSearchCV(
                estimator=estimator,
                search_spaces=params,
                n_jobs=n_jobs,
                cv=cv,
                scoring=self.mc.metrics,
                verbose=verbose)
        else:
            model = GridSearchCV(
                estimator=estimator,
                param_grid=params,
                n_jobs=n_jobs,
                cv=cv,
                scoring=self.mc.metrics,
                verbose=verbose)
        self.best_model = model.fit(self.X_train, self.y_train)
        logging.info(f"Best Params: {model.best_params_}")
        y_pred = self.best_model.predict(self.X_test)
        report = classification_report(self.y_test, y_pred)
        logging.info("Classification Report")
        print(report)
        if return_model:
            return self.best_model

    def normalize_params(self, params):
        par = params
        if not list(params.keys())[0].startswith("estimator__"):
            par = {}
            for k, v in params.items():
                par[f"estimator__{k}"] = v
        return par

    def features_importance(self):
        """ Calculate features importance from the best model """

        importances = permutation_importance(self.best_model, self.X_train, self.y_train, n_repeats=5, n_jobs=self.cpu_count, random_state=42)
        df = pd.DataFrame({
            "feature": self.X_train.columns,
            "importance": importances["importances_mean"],
            "stdev": importances["importances_std"]
        }).sort_values("importance", ascending=False)
        df[["importance", "stdev"]] = df[["importance", "stdev"]] / df.importance.sum()
        plt.figure(figsize=(15, 5))
        plt.bar(range(len(df)), df.importance, yerr=df.stdev, color="green")
        plt.xticks(range(len(df)), df.feature, rotation=45, horizontalalignment='right')
        plt.ylabel('Features Importance')
        plt.title("Mean Score Decrease", fontsize=15)

    def confusion_matrix(self):
        """ Calculate confusion matrix from the best model """

        plot_confusion_matrix(self.best_model, self.X_test, self.y_test)

    def save(self, model_path="model/best_model.pkl"):
        """ Save model

        Args:
            model_path (str, optional): Path to file model name, default to `model/best_model.pkl`

        """
        save_model(self.best_model, model_path)
