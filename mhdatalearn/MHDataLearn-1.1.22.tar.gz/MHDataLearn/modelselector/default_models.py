# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 10:00:12 2022

@author: krisj
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from MHDataLearn.modelselector.model_selector import split_data,\
                                            plot_confusion_matrix,\
                                            reveal_best_classification_model,\
                                            visualize_model_performance

def train_default_models(df, imd_include=False):
    """
    Creates a list of default features and outcome variable (Emergency
    Readmission within 30 days of discharge).
    Scales feature set using Standard Scaler
    Splits data in to training and test sets (80/20)
    Trains classification models (Logistic Regression, Decision Tree and
    KNN models) and outputs confusion matrices plots and performance metrics 
    in a dataframe.

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    imd_include : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    models.info : Performance metrics for each model
    models_plots : Plot of model performance metrics

    """
    #Define X, Y for models
    Y = df['EmergencyReadmit']
    feature_list = ['age_admit', 'Gender', 'MaritalStatus', 'EmployStatus', 
                'SettledAccommodationInd', 'MHCareClusterSuperClass', 
                'HospitalBedTypeMH']
    if imd_include:
        feature_list.append('imd_dec')
        X = df[feature_list]
    else:
        X = df[feature_list]
    #Scale features
    st_scaler = StandardScaler()
    X = pd.DataFrame(st_scaler.fit_transform(X))
    #Split in to test and train sets
    X_train, X_test, Y_train, Y_test = split_data(X, Y)
    #Train models and output metrics / confusion matrices
    models = reveal_best_classification_model(X_train, Y_train, X_test, Y_test)
    #Visualise model performance
    models_plots = visualize_model_performance(models)
    
    return models.info, models_plots