from maaml.functions.preprocessing import (
    dataset_loader,
    sklearn_data_normalizer,
    encoding_label,
)
import numpy as np
import pandas as pd
import time
from sklearn.model_selection import train_test_split, ShuffleSplit
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
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import ExtraTreeClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

# function blocks
# # model selection function
def createMLmodel(model_name="", paramater=100, verbose=0):
    model_name = str(model_name)
    if model_name == "1" or model_name == "DecisionTree":
        model = DecisionTreeClassifier()
        model_name = "DecisionTree"
    elif model_name == "2" or model_name == "RandomForest":
        paramater = int(paramater)
        model = RandomForestClassifier(n_estimators=paramater)
        model_name = "RandomForest"
    elif model_name == "3" or model_name == "ExtraTree":
        model = ExtraTreeClassifier()
        model_name = "ExtraTree"
    elif model_name == "4" or model_name == "ExtraTrees":
        paramater = int(paramater)
        model = ExtraTreesClassifier(n_estimators=paramater)
        model_name = "ExtraTrees"
    elif model_name == "5" or model_name == "KNeighbors":
        paramater = int(paramater)
        model = KNeighborsClassifier(n_neighbors=paramater)
        model_name = "KNeighbors"
    elif model_name == "6" or model_name == "GaussianNB":
        model = GaussianNB()
        model_name = "GaussianNB"
    elif model_name == "7" or model_name == "svm":
        paramater = str(paramater)
        model = svm.SVC(gamma=paramater)
        model_name = "svm"
    elif model_name == "8" or model_name == "LogisticRegression":
        paramater = str(paramater)
        model = LogisticRegression(solver=paramater, multi_class="auto", max_iter=1000)
        model_name = "LogisticRegression"
    elif model_name == "9" or model_name == "MLPClassifier":
        paramater = int(paramater)
        model = MLPClassifier(max_iter=paramater)
        model_name = "MLPClassifier"
    else:
        print(
            'ERROR:wrong entry, "createMLmodel" have 9 diffrent classifiers, you could choose by number or by name'
        )
        model_name = "Empty model"
        model = None
    if verbose == 1:
        print(model_name, "selected")
    return model, model_name


# # cross validation function
def cross_validate_model(
    dataset,
    target_name="target",
    model_name="",
    model_param=100,
    nb_splits=5,
    test_size=0.3,
    verbose=0,
):
    X = dataset.drop(target_name, axis=1)
    Y = dataset[target_name]
    cv = ShuffleSplit(n_splits=nb_splits, test_size=test_size, random_state=10)
    acc_scores, pres_scores, rec_scores, f1, cokap_scores, roc_auc_scores = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    cv_scores = []
    for train, test in cv.split(X, Y):
        classes = Y.unique()
        y_testb = label_binarize(Y[test], classes=classes)
        model, model_name = createMLmodel(model_name=model_name, paramater=model_param)
        model = model.fit(X.loc[train], Y[train]).predict(X.loc[test])
        acc_scores.append(accuracy_score(Y[test], model, normalize=True) * 100)
        pres_scores.append(precision_score(Y[test], model, average="macro") * 100)
        rec_scores.append(recall_score(Y[test], model, average="macro") * 100)
        f1.append(f1_score(Y[test], model, average="macro") * 100)
        cokap_scores.append(cohen_kappa_score(Y[test], model) * 100)
        roc_auc_scores.append(roc_auc_score(y_testb, model.reshape(-1, 1)) * 100)
    cv_scores = [
        model_name,
        "accuracy: %.2f%% (+/- %.2f%%)" % (np.mean(acc_scores), np.std(acc_scores)),
        "precision: %.2f%% (+/- %.2f%%)" % (np.mean(pres_scores), np.std(pres_scores)),
        "recall: %.2f%% (+/- %.2f%%)" % (np.mean(rec_scores), np.std(rec_scores)),
        "F1: %.2f%% (+/- %.2f%%)" % (np.mean(f1), np.std(f1)),
        "cohen_kappa: %.2f%% (+/- %.2f%%)"
        % (np.mean(cokap_scores), np.std(cokap_scores)),
        "roc_auc: %.2f%% (+/- %.2f%%)"
        % (np.mean(roc_auc_scores), np.std(roc_auc_scores)),
    ]
    if verbose == 1:
        print("\033[1m" + "\n" + model_name + ": " + "\033[0m")
        print(
            "accuracy cross validation :",
            "%.4f%% (+/- %.4f%%)" % (np.mean(acc_scores), np.std(acc_scores)),
        )
        print(
            "precision cross validation :",
            "%.4f%% (+/- %.4f%%)" % (np.mean(pres_scores), np.std(pres_scores)),
        )
        print(
            "recall cross validation :",
            "%.4f%% (+/- %.4f%%)" % (np.mean(rec_scores), np.std(rec_scores)),
        )
        print(
            "f1 cross validation :", "%.4f%% (+/- %.4f%%)" % (np.mean(f1), np.std(f1))
        )
        print(
            "cohen_kappa cross validation :",
            "%.4f%% (+/- %.4f%%)" % (np.mean(cokap_scores), np.std(cokap_scores)),
        )
        print(
            "roc_auc_score cross validation :",
            "%.4f%% (+/- %.4f%%)" % (np.mean(roc_auc_scores), np.std(roc_auc_scores)),
        )
        print("\n")
    if verbose == 2:
        print("\n                          Accuracy Detailed splits :\n\n", acc_scores)
        print(
            "\n                          Precision Detailed splits :\n\n", pres_scores
        )
        print("\n                           Detailed splits accuracy:\n\n", rec_scores)
        print("\n                          F1 Detailed splits :\n\n", f1)
        print(
            "\n                          Cohen_kappa Detailed splits :\n\n",
            cokap_scores,
        )
        print(
            "\n                          Roc_Auc_score Detailed splits :\n\n",
            roc_auc_scores,
        )
    return cv_scores


# # feature importance function
def extract_features_importance(
    df, classifier="default", target_name="target", split_size=0.3, verbose=0
):
    x = df.drop(target_name, axis=1)
    y = df[target_name]
    X_train, X_test, y_train, y_test = train_test_split(
        x, y, test_size=split_size, random_state=10
    )
    if classifier == "default":
        model = RandomForestClassifier(n_estimators=100)
        print("Default Classifier is RandomForestClassifier ")
    else:
        model = classifier
    model = model.fit(X_train, y_train)
    pred = model.predict(X_test)

    if verbose == 1:
        print(
            str(classifier),
            "Classifier accuracy : ",
            accuracy_score(y_test, pred, normalize=True),
            "\n",
        )
        print(classification_report(y_test, pred))
    importances = model.feature_importances_
    ranks = pd.DataFrame(importances * 100, index=x.columns, columns=["importance %"])
    ranks = ranks.sort_values("importance %")[::-1]
    return ranks


# # full evaluation pipeline function
def evaluation_pipline(
    path,
    specific,
    droped_colummns=[],
    prediction_column="target",
    model_parameter=100,
    feature_importance=True,
    verbose=0,
):
    if specific == "all":
        data = dataset_loader(path=path, full=True)
    elif specific == "" or specific == "secondary road":
        data = dataset_loader(path=path, full=False, specific=specific, verbose=verbose)
    elif specific == "0" or specific == "motorway road":
        data = dataset_loader(path=path, full=False, specific=specific, verbose=verbose)
    elif int(specific) < 7:
        data = dataset_loader(path=path, full=False, specific=specific, verbose=verbose)
    for column_name in droped_colummns:
        data = data.drop(column_name, axis=1)
        if verbose == 1:
            print("droped colummn :", column_name)
    normalizer_result, importance, results = (
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
    )
    for i in range(0, 9):
        data_numeric = encoding_label(
            encoding_label(data, "target", verbose=verbose), "road", verbose=verbose
        ).drop("Timestamp (seconds)", axis=1)
        df, normalizer_name = sklearn_data_normalizer(
            data_numeric, [prediction_column], i, verbose=verbose
        )
        if verbose == 1:
            print("number of features used: ", df.shape[1] - 1)
        for m in range(1, 10):
            model_param = model_parameter
            if m == 7:
                model_param = "scale"
            elif m == 8:
                model_param = "lbfgs"
            elif m == 9:
                model_param = 2000
            start_time = time.time()
            cross_validation = cross_validate_model(
                df,
                model_name=m,
                model_param=model_param,
                target_name=prediction_column,
                nb_splits=5,
                verbose=verbose,
            )
            end_time = time.time()
            time_recorded = str(format((end_time - start_time) / 5, ".2f")) + " (s)"
            if verbose == 1:
                print(
                    createMLmodel(model_name=m, paramater=model_param)[1],
                    "excution time (single fold): ",
                    time_recorded,
                )
            index, model_results = ["preprocessing", "execution time"], [
                normalizer_name,
                time_recorded,
            ]
            for j in range(1, len(cross_validation)):
                ind, res = cross_validation[j].split(":")
                model_results.append(res)
                index.append(ind)
            normalizer_result["metrics"] = index
            normalizer_result[cross_validation[0]] = model_results
            if m < 5 and feature_importance == True:
                classifier = createMLmodel(model_name=m, paramater=model_param)[0]
                ranks = extract_features_importance(
                    df, classifier, target_name=prediction_column, verbose=0
                )
            if feature_importance == True:
                importance = importance.append(ranks)
        results = results.append(normalizer_result)
    if feature_importance == True:
        return results, importance
    return results
