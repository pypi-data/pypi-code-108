import matplotlib.pyplot as plt
import ipywidgets as widgets
import numpy as np
import pandas as pd
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from matplotlib.colors import ListedColormap
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score

def feature_selector(df_list):
    df_options = {}
    features_list = {}
    for x in df_list:
        df_options[x.name] = x
        features_list[x.name] = list(x)

    def select_df(df):
        def select_target(target):
            def select_feature_x(feature_x):
                def select_feature_y(feature_y):
                        plt.figure(2, figsize=(8, 6))
                        plt.clf()
                        plt.scatter(df_options[df][feature_x], df_options[df][feature_y], c=df_options[df][target], cmap=plt.cm.Set1, edgecolor="k")
                        plt.xlabel(feature_x)
                        plt.ylabel(feature_y)
                        plt.xticks(())
                        plt.yticks(())
                widgets.interact(select_feature_y, feature_y=features_list[df_options[df].name])
            widgets.interact(select_feature_x, feature_x=features_list[df_options[df].name])
        widgets.interact(select_target, target=features_list[df_options[df].name])
    widgets.interact(select_df, df=df_options.keys())
    
    
def classification_selector(df_list):
    df_options = {}
    features_list = {}
    for x in df_list:
        df_options[x.name] = x
        features_list[x.name] = list(x)
    
    classifier_names = [
        "Nearest Neighbors",
        "Linear SVM",
        "Gaussian Process",
        "Decision Tree",
        "Random Forest",
        "Neural Net",
        "AdaBoost",
        "Naive Bayes",
        "Compare All",
    ]
    
    classifiers = [
        KNeighborsClassifier(3),
        SVC(kernel="linear", C=0.025),
        GaussianProcessClassifier(1.0 * RBF(1.0)),
        DecisionTreeClassifier(max_depth=5),
        RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
        MLPClassifier(alpha=1, max_iter=1000),
        AdaBoostClassifier(),
        GaussianNB(),
    ]
    
    
    def train(df, target, classifier):
        try:
            X = df
            y = target
            X = StandardScaler().fit_transform(X)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)
            for name, clf in zip(classifier_names, classifiers):
                if (name == classifier or classifier == "Compare All"):
                    startTime = time.time()
                    model = clf.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    endTime = time.time()
                    executionTime = endTime - startTime
                    acc = clf.score(X_test, y_test)
                    prec = precision_score(y_test, y_pred, average='weighted')
                    recall = recall_score(y_test, y_pred, average='weighted')
                    f1 = f1_score(y_test, y_pred, average='weighted')
                    data = [["%.2f" % acc, "%.2f" % prec, "%.2f" % recall, "%.2f" % f1, "%.3f" %executionTime]]
                    
                    # Table
                    columns = ('Classification Accuracy', 'Precision Score', 'Recall Score', 'F1 Score', 'Execution Time (s)')
                    plt.figure(linewidth=2,
                       tight_layout={'pad':1},
                       figsize=(18,1)
                      )
                    results_table = plt.table(cellText=data, rowLabels=[name], colLabels=columns, loc='center')
                    results_table.scale(1, 3)
                    ax = plt.gca()
                    ax.axis("off")
                    plt.draw()                    
                    if(classifier != "Compare All"): break
        except:
            print("Please select a valid target feature")

            
    def select_df(df):
        def select_target(target):
            def select_training(classifier):
                # Actually get and send the required params
                train(df_options[df], df_options[df][target], classifier)
                print("")
            widgets.interact(select_training, classifier=classifier_names)
        widgets.interact(select_target, target=features_list[df_options[df].name])
    widgets.interact(select_df, df=df_options.keys())