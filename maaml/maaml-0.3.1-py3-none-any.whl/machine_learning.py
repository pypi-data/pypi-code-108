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
from maaml.utils import save_csv, dict_transpose


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
        save_tag = "" if save_tag is None or save_tag == "" else f"_{save_tag}"
        PATH = f"ML_EVALUATION{save_tag}"
        if preprocessing_alias is not None:
            save_tag = f"_{preprocessing_alias}" + save_tag
        self.model = i = 1
        self.evaluation = {}
        while True:
            if full_eval is False:
                self.model = self.model_building(model_name, paramater, verbose)
            elif full_eval is True:
                try:
                    self.model = self.model_building(i, paramater, verbose)
                    i += 1
                except ValueError:
                    print("full evaluation complete")
                    self.evaluation = dict_transpose(self.evaluation)
                    if save_eval is True:
                        self.tag = f"full_evaluation{save_tag}"
                        save_csv(self.evaluation, PATH, self.tag, verbose)
                    break

            if "SVC" in str(self.model):
                self.model_name = str(self.model).replace("SVC", "SVMClassifier")
            self.model_name = str(self.model).replace("()", "")

            self.cross_evaluation = self.model_cross_validating(
                features,
                target,
                dataset,
                target_name,
                nb_splits,
                test_size,
                preprocessing_alias,
                verbose,
            )

            if not self.evaluation:
                self.evaluation = self.cross_evaluation
            else:
                for key in self.cross_evaluation:
                    self.evaluation[key].append(*self.cross_evaluation[key])
            if full_eval is False:
                self.evaluation = dict_transpose(self.evaluation)
                if save_eval is True:
                    self.tag = f"{self.model_name}{save_tag}_evaluation"
                    save_csv(self.evaluation, PATH, self.tag, verbose)

            try:
                self.feature_importance_ranks = self.features_importance_ranking(
                    dataset,
                    self.model,
                    target_name,
                    features,
                    target,
                    test_size,
                    verbose,
                )
            except AttributeError:
                self.feature_importance_ranks = None
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
            error_message = "ERROR:wrong entry,you have 9 different classifiers, you could choose by number or by name"
            print(error_message)
            model = "No model"
        if verbose == 1:
            print(f"\nThe {str(model)} is selected")
        return model

    def model_cross_validating(
        self,
        features=None,
        target=None,
        dataset=None,
        target_name="target",
        nb_splits=5,
        test_size=0.3,
        preprocessing_alias=None,
        verbose=0,
    ):
        start_time = time.perf_counter()
        if dataset is not None:
            X, Y = dataset.drop(target_name, axis=1), dataset[target_name]
        elif features is not None and target is not None:
            X, Y = features, target
        else:
            error_message = "ERROR: please enter a dataset with a target_name or you can enter features and target"
            print(error_message)
            return
        cv = ShuffleSplit(n_splits=nb_splits, test_size=test_size, random_state=10)
        acc_scores, pres_scores, rec_scores, f1, cokap_scores, roc_auc_scores = (
            [],
            [],
            [],
            [],
            [],
            [],
        )
        cv_scores = {
            "MLclassifier": [],
            "preprocessing": [],
            "execution time": [],
            "accuracy": [],
            "precision": [],
            "recall": [],
            "F1": [],
            "cohen_kappa": [],
            "roc_auc": [],
        }
        for train, test in cv.split(X, Y):
            classes = Y.unique()
            y_testb = label_binarize(Y[test], classes=classes)
            Y_values = Y.values
            Y_reshaped = Y_values.reshape(-1, 1)
            model = self.model
            pred = model.fit(X.loc[train], Y_values[train]).predict(X.loc[test])
            pred_reshaped = pred.reshape(-1, 1)
            acc_scores.append(accuracy_score(Y_values[test], pred, normalize=True))
            pres_scores.append(precision_score(Y_values[test], pred, average="macro"))
            rec_scores.append(recall_score(Y_values[test], pred, average="macro"))
            f1.append(f1_score(Y_values[test], pred, average="macro"))
            cokap_scores.append(cohen_kappa_score(Y_reshaped[test], pred_reshaped))
            roc_auc_scores.append(roc_auc_score(y_testb, pred_reshaped))
        end_time = time.perf_counter()
        cv_scores["MLclassifier"].append(self.model_name)
        if preprocessing_alias is not None:
            cv_scores["preprocessing"].append(preprocessing_alias)
        cv_scores["execution time"].append(
            f"{((end_time-start_time) / nb_splits): .2f} (s)"
        )
        cv_scores["accuracy"].append(
            f"{np.mean(acc_scores):.4%} (+/- {np.std(acc_scores):.4%})"
        )
        cv_scores["precision"].append(
            f"{np.mean(pres_scores):.4%} (+/- {np.std(pres_scores):.4%})"
        )
        cv_scores["recall"].append(
            f"{np.mean(rec_scores):.4%} (+/- {np.std(rec_scores):.4%})"
        )
        cv_scores["F1"].append(f"{np.mean(f1):.4%} (+/- {np.std(f1):.4%})")
        cv_scores["cohen_kappa"].append(
            f"{np.mean(cokap_scores):.4%} (+/- {np.std(cokap_scores):.4%})"
        )
        cv_scores["roc_auc"].append(
            f"{np.mean(roc_auc_scores):.4%} (+/- {np.std(roc_auc_scores):.4%})"
        )
        if verbose == 1:
            print("\n\033[1mCross validation results: \033[0m")
            for i, v in cv_scores.items():
                print(f"{i}: {v[0]}")
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
        target_name="target",
        features=None,
        targets=None,
        test_size=0.3,
        verbose=0,
    ):
        if dataset is not None and target_name is not None:
            x = dataset.drop(target_name, axis=1)
            y = dataset[target_name].values
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
        target_name="target",
        features=None,
        targets=None,
        test_size=0.3,
        verbose=0,
    ):
        if dataset is not None and target_name is not None:
            x = dataset.drop(target_name, axis=1)
            y = dataset[target_name].values
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
    uahdataset = processed.ml_dataset
    alias = processed.scaler_name
    ml_evaluation = Evaluator(
        3,
        dataset=uahdataset,
        verbose=1,
        preprocessing_alias=alias,
        full_eval=False,
        save_eval=True,
    )
    print(f"feature importance :\n{ml_evaluation.feature_importance_ranks}")


if __name__ == "__main__":
    main()
