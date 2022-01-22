from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

from sklearn.model_selection import ShuffleSplit, train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    cohen_kappa_score,
    roc_auc_score,
    classification_report,
)
import numpy as np
import time
import os


class Evaluator:
    def __init__(
        self,
        model_name="4",
        paramater=None,
        features=None,
        target=None,
        dataset=None,
        target_name="target",
        nb_splits=5,
        test_size=0.3,
        full_eval=False,
        save_eval=False,
        save_tag=None,
        preprocessing_alias=None,
        verbose=0,
    ):
        if save_tag is None:
            save_tag = ""
        else:
            save_tag = f"_{save_tag}"
        self.model = i = 1
        target_name = [target_name]
        self.evaluation = []
        while True:
            if full_eval is False:
                self.model = self.model_building(
                    model_name=model_name, paramater=paramater, verbose=verbose
                )
            elif full_eval is True:
                try:
                    self.model = self.model_building(
                        model_name=i, paramater=paramater, verbose=verbose
                    )
                    i += 1
                except ValueError:
                    print("full evaluation complete")
                    if save_eval is True:
                        NEW_PATH = f"ML_EVALUATION{save_tag}"
                        if not os.path.exists(NEW_PATH):
                            os.makedirs(NEW_PATH)
                        if preprocessing_alias is not None:
                            np.savetxt(
                                f"{NEW_PATH}/{preprocessing_alias}_full_evaluation{save_tag}.csv",
                                self.evaluation,
                                delimiter=",",
                                fmt="%s",
                            )
                        else:
                            np.savetxt(
                                f"{NEW_PATH}/full_evaluation{save_tag}.csv",
                                self.evaluation,
                                delimiter=",",
                                fmt="%s",
                            )
                        if verbose == 1:
                            print(
                                f"full evaluation saved in:\n{os.getcwd()}/{NEW_PATH}/full_evaluation{save_tag}.csv"
                            )
                    break
            if "SVC" in str(self.model):
                self.model_name = (
                    str(self.model).replace("SVC", "SVMClassifier").replace("()", "")
                )
            else:
                self.model_name = str(self.model).replace("()", "")
            self.target_list = []
            if dataset is not None:
                for column_name in dataset.columns:
                    for keyname in target_name:
                        if keyname in column_name:
                            self.target_list.append(column_name)
            elif dataset is None:
                try:
                    if target.shape[1] > 1:
                        for name in range(0, target.shape[1]):
                            self.target_list.append(f"{target_name[0]} {name}")
                except IndexError:
                    self.target_list = target_name
                except Exception:
                    print("ERROR: Something went wrong in the entry target")
                    return
            else:
                print("ERROR: bad target name or bad target name entry ")
            self.cross_evaluation = self.model_cross_validating(
                features=features,
                target=target,
                dataset=dataset,
                target_names=self.target_list,
                nb_splits=nb_splits,
                test_size=test_size,
                preprocessing_alias=preprocessing_alias,
                verbose=verbose,
            )
            self.evaluation.extend(self.cross_evaluation)
            if save_eval is True and full_eval is False:
                NEW_PATH = f"ML_EVALUATION{save_tag}"
                if not os.path.exists(NEW_PATH):
                    os.makedirs(NEW_PATH)
                if preprocessing_alias is not None:
                    np.savetxt(
                        f"{NEW_PATH}/{preprocessing_alias}_{self.model_name}{save_tag}_evaluation.csv",
                        self.evaluation,
                        delimiter=",",
                        fmt="%s",
                    )
                else:
                    np.savetxt(
                        f"{NEW_PATH}/{self.model_name}{save_tag}_evaluation.csv",
                        self.evaluation,
                        delimiter=",",
                        fmt="%s",
                    )
                if verbose == 1:
                    print(
                        f"evaluation saved in:\n{os.getcwd()}/{NEW_PATH}/{self.model_name}{save_tag}_evaluation.csv"
                    )

            try:
                self.feature_importance_ranks = self.features_importance_ranking(
                    dataset=dataset,
                    classifier=self.model,
                    target_names=self.target_list,
                    features=features,
                    targets=target,
                    test_size=test_size,
                    verbose=verbose,
                )
            except Exception:
                if verbose == 1:
                    print(
                        f"The {str(self.model)} does not allow the extraction of feature importance ranks\nSkipping action"
                    )
            if full_eval is False:
                break

    @staticmethod
    def model_building(model_name="4", paramater=None, verbose=0):
        model_name = str(model_name)
        if model_name == "1" or model_name == "DecisionTree":
            model = DecisionTreeClassifier()
        elif model_name == "2" or model_name == "RandomForest":
            if paramater is not None:
                paramater = int(paramater)
                model = RandomForestClassifier(n_estimators=paramater)
            else:
                model = RandomForestClassifier()
        elif model_name == "3" or model_name == "ExtraTree":
            model = ExtraTreeClassifier()
        elif model_name == "4" or model_name == "ExtraTrees":
            if paramater is not None:
                paramater = int(paramater)
                model = ExtraTreesClassifier(n_estimators=paramater)
            else:
                model = ExtraTreesClassifier()
        elif model_name == "5" or model_name == "KNeighbors":
            if paramater is not None:
                paramater = int(paramater)
                model = KNeighborsClassifier(n_neighbors=paramater)
            else:
                model = KNeighborsClassifier()
        elif model_name == "6" or model_name == "GaussianNB":
            model = GaussianNB()
        elif model_name == "7" or model_name == "SVM":
            if paramater is not None:
                paramater = str(paramater)
                model = svm.SVC(gamma=paramater)
            else:
                model = svm.SVC()
        elif model_name == "8" or model_name == "LogisticRegression":
            if paramater is not None:
                paramater = str(paramater)
                model = LogisticRegression(
                    solver=paramater, multi_class="auto", max_iter=1000
                )
            else:
                model = LogisticRegression(multi_class="auto", max_iter=1000)
        elif model_name == "9" or model_name == "MLPClassifier":
            if paramater is not None:
                paramater = int(paramater)
                model = MLPClassifier(max_iter=paramater)
            else:
                model = MLPClassifier()
        elif int(model_name) > 9:
            raise ValueError(
                f"You entered {model_name}, a number bigger than the number of existant models"
            )
        else:
            print(
                "ERROR:wrong entry, this method have 9 diffrent classifiers, you could choose by number or by name"
            )
            model = "No model"
        if verbose == 1:
            print(f"\nThe {str(model)} is selected")
        return model

    def model_cross_validating(
        self,
        features=None,
        target=None,
        dataset=None,
        target_names=["target"],
        nb_splits=5,
        test_size=0.3,
        preprocessing_alias=None,
        verbose=0,
    ):
        start_time = time.perf_counter()
        if dataset is not None:
            X, Y = dataset.drop(target_names, axis=1), dataset[target_names]
        elif features is not None and target is not None:
            X, Y = features, target
        else:
            print(
                "ERROR: please enter a dataset with a target_name or enter features and target"
            )
            return
        cv = ShuffleSplit(n_splits=nb_splits, test_size=test_size, random_state=10)
        (
            acc_scores,
            pres_scores,
            rec_scores,
            f1,
            cokap_scores,
            roc_auc_scores,
            cv_scores,
        ) = ([], [], [], [], [], [], [])
        for train, test in cv.split(X, Y):
            if len(target_names) <= 1:
                classes = Y.unique()
                y_testb = label_binarize(Y[test], classes=classes)
            else:
                y_testb = Y.loc[test]
            Y_values = Y.values
            model = self.model
            try:
                pred = model.fit(X.loc[train], Y_values[train]).predict(X.loc[test])
            except ValueError:
                Y_values = Y.values.reshape(-1, 1).ravel()
                pred = model.fit(X.loc[train], Y_values[train]).predict(X.loc[test])
            acc_scores.append(
                accuracy_score(Y_values[test], pred, normalize=True) * 100
            )
            pres_scores.append(
                precision_score(Y_values[test], pred, average="macro") * 100
            )
            rec_scores.append(recall_score(Y_values[test], pred, average="macro") * 100)
            f1.append(f1_score(Y_values[test], pred, average="macro") * 100)
            cokap_scores.append(
                cohen_kappa_score(Y_values[test].reshape(-1, 1), pred.reshape(-1, 1))
                * 100
            )
            if len(target_names) <= 1:
                roc_auc_scores.append(roc_auc_score(y_testb, pred.reshape(-1, 1)) * 100)
            else:
                try:
                    roc_auc_scores.append(roc_auc_score(y_testb, pred) * 100)
                except ValueError:
                    roc_auc_scores.append(
                        roc_auc_score(Y_values[test].reshape(-1, 1), pred) * 100
                    )
        end_time = time.perf_counter()
        cv_scores = [
            ["MLclassifier", f"{self.model_name}"],
            ["execution time", f"{((end_time-start_time) / nb_splits): .2f} (s)"],
            ["accuracy", f"{np.mean(acc_scores):.2f}% (+/- {np.std(acc_scores):.2f}%)"],
            [
                "precision",
                f"{np.mean(pres_scores):.2f}% (+/- {np.std(pres_scores):.2f}%)",
            ],
            ["recall", f"{np.mean(rec_scores):.2f}% (+/- {np.std(rec_scores):.2f}%)"],
            ["F1", f"{np.mean(f1):.2f}% (+/- {np.std(f1):.2f}%)"],
            [
                "cohen_kappa",
                f"{np.mean(cokap_scores):.2f}% (+/- {np.std(cokap_scores):.2f}%)",
            ],
            [
                "roc_auc",
                f"{np.mean(roc_auc_scores):.2f}% (+/- {np.std(roc_auc_scores):.2f}%)",
            ],
        ]
        if preprocessing_alias is not None:
            cv_scores.insert(1, ["preprocessing", preprocessing_alias])
        if verbose == 1:
            for i, v in enumerate(cv_scores):
                if i == 0:
                    print(f"\033[1m\n{v[0]}:{v[1]}\033[0m")
                else:
                    print(f"cross validation {v[0]}: {v[1]}")
            print("\n")
        if verbose == 2:
            print(f"\nAccuracy evaluation for the separate splits:\n{acc_scores}")
            print(f"\nPrecision evaluation for the separate splits:\n{pres_scores}")
            print(f"\nRecall evaluation for the separate splits:\n{rec_scores}")
            print(f"\nF1 evaluation for the separate splits:\n{f1}")
            print(f"\nCohen_kappa evaluation for the separate splits:\n{cokap_scores}")
            print(f"\nRoc_Auc evaluation for the separate splits:\n{roc_auc_scores}")
        return cv_scores

    @staticmethod
    def features_importance_ranking(
        dataset=None,
        classifier=None,
        target_names=["target"],
        features=None,
        targets=None,
        test_size=0.3,
        verbose=0,
    ):
        if dataset is not None and target_names is not None:
            x = dataset.drop(target_names, axis=1)
            y = dataset[target_names].values
        elif dataset is None:
            x = features
            y = targets.values
        X_train, X_test, y_train, y_test = train_test_split(
            x, y, test_size=test_size, random_state=10
        )
        if classifier is None:
            model = ExtraTreesClassifier()
            classifier = str(model)
            print(
                f"The default Classifier for feature importance ranking is {classifier}"
            )
        else:
            model = classifier
        model = model.fit(X_train, y_train)
        pred = model.predict(X_test)

        if verbose == 1:
            f1score = f1_score(y_test, pred, average="macro")
            print(
                f"\nTrying to use {str(classifier)} for the feature ranking with an F1 score of : {f1score*100: .2f}%\n"
            )
        importances = model.feature_importances_
        ranks = x.T.drop(x.index, axis=1)
        ranks["importance %"] = importances * 100
        ranks = ranks.sort_values("importance %")[::-1]
        if verbose == 1:
            print(
                f"The {len(ranks)} features importance is ranked successfully using the {str(model)}"
            )
        return ranks

    @staticmethod
    def model_evaluating(
        dataset=None,
        classifier=None,
        target_names=["target"],
        features=None,
        targets=None,
        test_size=0.3,
        verbose=0,
    ):
        if dataset is not None and target_names is not None:
            x = dataset.drop(target_names, axis=1)
            y = dataset[target_names].values
        elif dataset is None:
            x = features
            y = targets.values
        else:
            print("No data is provided for the evaluation")
        X_train, X_test, y_train, y_test = train_test_split(
            x, y, test_size=test_size, random_state=10
        )
        if classifier is None:
            model = ExtraTreesClassifier()
            classifier = str(model)
            print(
                f"You did not provide a classifier, the default Classifier is {classifier}"
            )
        else:
            model = classifier
        model = model.fit(X_train, y_train)
        pred = model.predict(X_test)
        results = classification_report(y_test, pred)
        if verbose == 1:
            print(results)
        return results


def main():
    from maaml.preprocessing import DataPreprocessor as dp

    processed = dp(dataset="UAHdataset", scaler=2)
    uahdataset = processed.preprocessed_dataset
    alias = processed.scaler_name
    features = processed.features
    target_column = processed.target_column
    target = processed.target
    ml_evaluation = Evaluator(
        3,
        dataset=uahdataset,
        verbose=1,
        preprocessing_alias=alias,
        full_eval=True,
        save_eval=True,
    )
    print("\nThe target list is :", ml_evaluation.target_list)
    print("feature importance : \n", ml_evaluation.feature_importance_ranks)


if __name__ == "__main__":
    main()
