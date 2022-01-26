import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
# Allows us to split our data into training and testing data
from sklearn.model_selection import train_test_split
# Allows us to test parameters of classification algorithms and find the best one
from sklearn.model_selection import GridSearchCV
# Logistic Regression classification algorithm
from sklearn.linear_model import LogisticRegression
# Support Vector Machine classification algorithm
from sklearn.svm import SVC
# Decision Tree classification algorithm
from sklearn.tree import DecisionTreeClassifier
# K Nearest Neighbors classification algorithm
from sklearn.neighbors import KNeighborsClassifier


def split_data(X, Y):
    """
    This function split the features and the target into training and test set
    Params:
        X- (df containing predictors)
        y- (series conatining Target)
    Returns:
        X_train, y_train, X_test, y_test
    """
    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.2, random_state=2)

    return X_train, X_test, Y_train, Y_test

    
    
def plot_confusion_matrix(Y_test,y_predict, modelname):
    """
    This function plots the confusion matrix of the models.
    
    Params:
        Y_test
        Predictions
    Output:
        Confusion matrix
    
    
    """
    from sklearn.metrics import confusion_matrix

    cm = confusion_matrix(Y_test, y_predict)
    ax= plt.subplot()
    sns.heatmap(cm, annot=True, ax = ax); #annot=True to annotate cells
    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('True labels')
    ax.set_title(f'Confusion Matrix for {modelname}'); 
    ax.xaxis.set_ticklabels(['Em Readmit', 'No Em Readmit']); \
        ax.yaxis.set_ticklabels(['Em Readmit', 'No Em Readmit'])


def reveal_best_classification_model(X_train, Y_train, X_test, Y_test):
    """
    This function build four classifcation models using four different Algorithm,
    -Logistic regression
    -Support Vecter Machines
    -Decision Tree Classifier
    -K Nearest Neighbors
    It runs a grid search cv through the models to determine the best hyper parameter and their best score.
    compares the scores of all the four Algorithms and creates a dictionary of the model with their respective 
    best score and best parameter as per he gridsearch cv hyperparameter tuning during cross validations.
    
    Params:
        X_train
        Y_train
        X_test
        Y_test
    Returns:
        A dataframe containing the four models with their best hyper parameter and best scores.
    
    """
    print("Model training started - this may take several minutes...")
    lr_parameters ={'C':[0.01,0.1,1],
             'penalty':['l2'],
             'solver':['lbfgs']}
    
    tree_parameters =  {'criterion': ['gini', 'entropy'],
     'splitter': ['best', 'random'],
     'max_depth': [2*n for n in range(1,10)],
     'max_features': ['auto', 'sqrt'],
     'min_samples_leaf': [1, 2, 4],
     'min_samples_split': [2, 5, 10]}
    
    knn_parameters = {'n_neighbors': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
              'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
              'p': [1,2]}
    try:
        
        #creating and trainin a logistic model using a grid serach cv
        print("Training logistic regression model...", end = "")
        logreg = LogisticRegression()
        logreg_cv = GridSearchCV(logreg, lr_parameters, cv=5)
        logreg_cv.fit(X_train, Y_train)
        print("Complete")

        #creating and trainin a support vector machine model using a grid serach cv
        # svm = SVC()
        # svm_cv = GridSearchCV(svm, svm_paramters, cv=5, refit=True)
        # svm_cv.fit(X_train, Y_train)

        #creating and trainin a tree based model using a grid serach cv            
        print("Training decision tree classifier...", end = "")
        tree = DecisionTreeClassifier()
        tree_cv = GridSearchCV(tree, tree_parameters, cv=5)
        tree_cv.fit(X_train, Y_train)
        print("Complete")
        
        #creating and trainin Knearest neighbors model using a grid serach cv
        print("Training KNN...", end = "")
        KNN = KNeighborsClassifier()
        knn_cv = GridSearchCV(KNN, knn_parameters, cv=5)
        knn_cv.fit(X_train, Y_train)
        print("Complete")
        
    except Exception as e:
        print(F"Error {e}!")
    models_dict = {
        "models":['logreg_cv', 'tree_cv', 'knn_cv'],
        "BestParams":[logreg_cv.best_params_, tree_cv.best_params_, knn_cv.best_params_],
        "BestTraininScore":[logreg_cv.best_score_, tree_cv.best_score_, knn_cv.best_score_],
        "TestAccuracy": [logreg_cv.score(X_test, Y_test), tree_cv.score(X_test, Y_test), knn_cv.score(X_test, Y_test)]

    }
    performance_df = pd.DataFrame(models_dict)
    lr_pred = logreg_cv.predict(X_test)
    tree_pred = logreg_cv.predict(X_test)
    knn_pred = logreg_cv.predict(X_test)
    print("Performance Metrics:")
    print(performance_df)

    #ploting confusion matrices
    plt.figure
    plot_confusion_matrix(Y_test, lr_pred, 'Logistic Regression')
    plt.figure()
    plot_confusion_matrix(Y_test, tree_pred, 'Decision Tree Classifier')
    plt.figure()
    plot_confusion_matrix(Y_test, knn_pred, 'KNN')

    return performance_df


def visualize_model_performance(model):
    """
    This function creates a bar plot with score of the individual models and their labels.
    Params:
        reveal_best_classification_model type(function)
    Output:
        Barplot
    """
    
    
    return model.plot(kind="bar")



    