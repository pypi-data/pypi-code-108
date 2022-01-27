# define parameters for the random search 

import pprint
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier
from scipy.stats import randint as rint
from imblearn.over_sampling import RandomOverSampler
from lmz import *
import numpy as np

from scipy.stats import randint,uniform





class OS_MLPClassifier(MLPClassifier):
    def fit(self, X, y):
        os = RandomOverSampler(random_state=42)
        X_re, y_re = os.fit_sample(X, y)
        MLPClassifier.fit(self, X_re, y_re)

class OS_ExtraTreesClassifier(ExtraTreesClassifier):
    def fit(self, X, y):
        os = RandomOverSampler(random_state=42)
        X_re, y_re = os.fit_sample(X, y)
        ExtraTreesClassifier.fit(self, X_re, y_re)

class OS_GradientBoostingClassifier(GradientBoostingClassifier):
    def fit(self, X, y):
        os = RandomOverSampler(random_state=42)
        X_re, y_re = os.fit_sample(X, y)
        GradientBoostingClassifier.fit(self, X_re, y_re)



KNeighborsClassifierparam = {'algorithm': ['auto'],
 'leaf_size': [30],
 'metric': ['minkowski'],
 'metric_params': [None],
 'n_jobs': [None],
 'n_neighbors': [5],
 'p': [2],
 'weights': ['uniform']}
SVCparam = {'C': np.arange(0.001,10,0.001),
 'break_ties': [False],
 'cache_size': [200],
 'class_weight': [None],
 'coef0': [0.0],
 'decision_function_shape': ['ovr'],
 'degree': [3],
 'gamma': ['scale'],
 'kernel': ['rbf'],
 'max_iter': [-1],
 'probability': [False],
 'random_state': [None],
 'shrinking': [True],
 'tol': [0.001],
 'verbose': [False]}
DecisionTreeClassifierparam = {'ccp_alpha': [0.0],
 'class_weight': [None],
 'criterion': ['gini'],
 'max_depth': [None],
 'max_features': [None],
 'max_leaf_nodes': [None],
 'min_impurity_decrease': [0.0],
 'min_impurity_split': [None],
 'min_samples_leaf': [1],
 'min_samples_split': [2],
 'min_weight_fraction_leaf': [0.0],
 'random_state': [None],
 'splitter': ['best']}
MLPClassifierparam = {'activation': ['relu'],
 'alpha': [0.0001],
 'batch_size': ['auto'],
 'beta_1': [0.9],
 'beta_2': [0.999],
 'early_stopping': [False],
 'epsilon': [1e-08],
 'hidden_layer_sizes': [(100,)],
 'learning_rate': ['constant'],
 'learning_rate_init': [0.001],
 'max_fun': [15000],
 'max_iter': [200],
 'momentum': [0.9],
 'n_iter_no_change': [10],
 'nesterovs_momentum': [True],
 'power_t': [0.5],
 'random_state': [None],
 'shuffle': [True],
 'solver': ['adam'],
 'tol': [0.0001],
 'validation_fraction': [0.1],
 'verbose': [False],
 'warm_start': [False]}
AdaBoostClassifierparam = {'algorithm': ['SAMME.R'],
 'base_estimator': [None],
 'learning_rate': [1.0],
 'n_estimators': [50],
 'random_state': [None]}
GaussianNBparam = {'priors': [None], 'var_smoothing': [1e-09]}
QuadraticDiscriminantAnalysisparam = {'priors': [None],
 'reg_param': [0.0],
 'store_covariance': [False],
 'tol': [0.0001]}
RandomForestClassifierparam = {'bootstrap': [True],
 'ccp_alpha': [0.0],
 'class_weight': [None],
 'criterion': ['gini'],
 'max_depth': [None],
 'max_features': ['auto'],
 'max_leaf_nodes': [None],
 'max_samples': [None],
 'min_impurity_decrease': [0.0],
 'min_impurity_split': [None],
 'min_samples_leaf': [1],
 'min_samples_split': [2],
 'min_weight_fraction_leaf': [0.0],
 'n_estimators': [100],
 'n_jobs': [None],
 'oob_score': [False],
 'random_state': [None],
 'verbose': [0],
 'warm_start': [False]}


ExtraTreesClassifierparam = {'bootstrap': [False, True],
 'ccp_alpha': [0.0],
 'class_weight': [None, 'balanced'],
 'criterion': ['gini','entropy'],
 'max_depth': randint(2,30),
 'max_features': ['auto'],
 'max_leaf_nodes': [None],
 'max_samples': [None],
 #'min_impurity_decrease': uniform(0,0.1),
 'min_impurity_decrease': [0],
 'min_impurity_split': [None],
 'min_samples_leaf': randint(1,10),
 'min_samples_split': randint(2,10),
 'min_weight_fraction_leaf': [0.0],
 'n_estimators': randint(6,200),
 'n_jobs': [None],
 'oob_score': [False],
 'random_state': [None],
 'verbose': [0],
 'warm_start': [False]}



ExtraTreesClassifierparam_skopt = {'bootstrap': [False, True],
 'ccp_alpha': [0.0],
 'class_weight': [None, 'balanced'],
 'criterion': ['gini','entropy'],
 'max_depth': Range(5,30),
 'max_features': ['auto'],
 'max_leaf_nodes': [None],
 'max_samples': [None],
 'min_impurity_decrease': np.arange(0,0.1,0.001),
 'min_impurity_split': [None],
 'min_samples_leaf': Range(1,10),
 'min_samples_split': Range(2,10),
 'min_weight_fraction_leaf': [0.0],
 'n_estimators': Range(10,300),
 'n_jobs': [None],
 'oob_score': [False],
 'random_state': [None],
 'verbose': [0],
 'warm_start': [False]}


GradientBoostingClassifierparam = {'ccp_alpha': [0.0],
 'criterion': ['friedman_mse'],
 'init': [None],
 'learning_rate': [0.1],
 'loss': ['deviance'],
 'max_depth': [3],
 'max_features': [None],
 'max_leaf_nodes': [None],
 'min_impurity_decrease': [0.0],
 'min_impurity_split': [None],
 'min_samples_leaf': [1],
 'min_samples_split': [2],
 'min_weight_fraction_leaf': [0.0],
 'n_estimators': [100],
 'n_iter_no_change': [None],
 'random_state': [None],
 'subsample': [1.0],
 'tol': [0.0001],
 'validation_fraction': [0.1],
 'verbose': [0],
 'warm_start': [False]}






if __name__=="__main__":
    # THIS GENERATES THE CLASSIFIER LIST 
    classifiers = [
    KNeighborsClassifier(),
    SVC(), 
    DecisionTreeClassifier(),
    MLPClassifier(),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis(),
    RandomForestClassifier(),
    ExtraTreesClassifier(),
    GradientBoostingClassifier() ]

    valtolist = lambda x: { k:[v] for k,v in x.items()}
    param_list = [ valtolist(clf.get_params()) for clf in classifiers]
    for  cl, pa in zip(map(str,classifiers), param_list):
        print (f"{cl[:-2]}param = ", end ='')
        pprint.pprint(pa)
    
    print("classifiers = {")
    for cl in map(str,classifiers):
        print (f"'{cl.replace('Classifier','')[:-2]}' : ({cl},{cl[:-2]}param),")
    print ("}")

classifiers = {
        'KNeighbors' : (KNeighborsClassifier(),KNeighborsClassifierparam),
        'SVC' : (SVC(),SVCparam),
        'DecisionTree' : (DecisionTreeClassifier(),DecisionTreeClassifierparam),
        'MLP' : (MLPClassifier(),MLPClassifierparam),
        'AdaBoost' : (AdaBoostClassifier(),AdaBoostClassifierparam),
        'GaussianNB' : (GaussianNB(),GaussianNBparam),
        'QuadraticDiscriminantAnalysis' : (QuadraticDiscriminantAnalysis(),QuadraticDiscriminantAnalysisparam),
        'RandomForest' : (RandomForestClassifier(),RandomForestClassifierparam),
        'ExtraTrees' : (ExtraTreesClassifier(),ExtraTreesClassifierparam),
        'ExtraTreesSKO' : (ExtraTreesClassifier(),ExtraTreesClassifierparam_skopt),
        'GradientBoosting' : (GradientBoostingClassifier(),GradientBoostingClassifierparam),
        }



