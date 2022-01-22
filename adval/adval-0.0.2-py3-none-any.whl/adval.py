import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
import xgboost as xgb
from xgboost import cv


class adVal:

    def __init__(self, train, test, target, id):
        self.train = train
        self.test = test
        self.target = target
        self.id =id

    def auc_score(self): 
        train = self.train.drop(columns=[self.target, self.id], errors='ignore')
        test = self.test.drop(columns=[self.target , self.id], errors='ignore')
        X_test  = test.select_dtypes(include=['number']).copy()
        X_train = train.select_dtypes(include=['number']).copy()

        # add the train/test labels
        X_train["AV_label"] = 0
        X_test["AV_label"]  = 1

        # make one big dataset
        all_data = pd.concat([X_train, X_test], axis=0, ignore_index=True)

        # shuffle
        all_data_shuffled = all_data.sample(frac=1)

        # create our DMatrix (the XGBoost data structure)
        X = all_data_shuffled.drop(['AV_label'], axis=1)
        y = all_data_shuffled['AV_label']
        XGBdata = xgb.DMatrix(data=X,label=y)

        # our XGBoost parameters
        params = {"objective":"binary:logistic",
                  "eval_metric":"logloss",
                  'learning_rate': 0.05,
                  'max_depth': 6, }

        # perform cross validation with XGBoost
        cross_val_results = cv(dtrain=XGBdata, params=params, 
                       nfold=5, metrics="auc", 
                       num_boost_round=200,early_stopping_rounds=20,
                       as_pandas=True)

        # print out the final result
        score = (cross_val_results["test-auc-mean"]).iloc[-1]
        if score <= 0.55:
            print("Few data leakage, AUC Score: {:.2}".format(score))
        else: 
            print("More than threshold data leakage, AUC Score: {:.2}".format(score))
