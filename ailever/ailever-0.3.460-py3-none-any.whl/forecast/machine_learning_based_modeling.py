from ailever.forecast import __forecast_bs__ as forecast_bs
from ..logging_system import logger

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, KFold, cross_val_score, GridSearchCV
from sklearn import linear_model, tree, neighbors, svm, ensemble
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

model = dict()
# Classification model
model['KNC'] = neighbors.KNeighborsClassifier()
# Regression model
model['LR'] = linear_model.LinearRegression()
model['LASSO'] = linear_model.Lasso()
model['EN'] = linear_model.ElasticNet()
model['KNR'] = neighbors.KNeighborsRegressor()
model['CART'] = tree.DecisionTreeRegressor()
model['SVR'] = svm.SVR()
model['ABR'] = ensemble.AdaBoostRegressor()
model['GBR'] = ensemble.GradientBoostingRegressor()
model['RFR'] = ensemble.RandomForestRegressor()
model['ETR'] = ensemble.ExtraTreesRegressor()

class LightMLOps:
    def __init__(self, dataset, target):
        self.model = model

        # Dataset
        num_instance = dataset[target].unique().shape[0]
        self.problem = 'classification' if num_instance == 2 else 'regression'
            
        self.dataset_X = dataset.drop(target, axis=1).values
        self.dataset_Y = dataset[target].values
        self.X_train, self.X_validation, self.Y_train, self.Y_validation = train_test_split(self.dataset_X, self.dataset_Y, test_size=0.2)
        
        # Models
        self.regressors = ['LR', 'LASSO', 'EN', 'KNR', 'CART', 'SVR', 'ABR', 'GBR', 'RFR', 'ETR']
        self.classifiers = ['KNC'] 
        self.training_models = self.classifiers if self.problem == 'classification' else self.regressors
        
        self.baselines = list()
        self.pipelines1 = list() # Standard
        self.pipelines2 = list() # MinMax
        self.pipelines3 = list() # Robust
        for training_model in self.training_models:
            # Baseline Model
            self.baselines.append((training_model, self.model[training_model]))
            # Standard Scaled Model
            self.pipelines1.append(('StandardScaled'+training_model, Pipeline([('Scaler', StandardScaler()),(training_model, self.model[training_model])])))        
            # MinMax Scaled Model
            self.pipelines2.append(('MinMaxScaled'+training_model, Pipeline([('Scaler', MinMaxScaler()),(training_model, self.model[training_model])])))        
            # Robust Scaled Model
            self.pipelines3.append(('RobustScaled'+training_model, Pipeline([('Scaler', MinMaxScaler()),(training_model, self.model[training_model])])))        
        
    def __getitem__(self, idx):
        return self.model[idx]
    
    def trigger(self, fine_tuning=False):
        logger['forecast'].info('SPOT CHECK')
        self.spot_check_base_block()
        self.scaling_block(scaler='Standard')
        self.scaling_block(scaler='MinMax')
        self.scaling_block(scaler='Robust')

        if fine_tuning:
            self.tunning_block()
        
    def spot_check_base_block(self):
        results = []
        names = []
        for name, model in self.baselines:
            scoring = 'neg_mean_squared_error'
            kfold = KFold(n_splits=10, shuffle=True)
            cv_results = cross_val_score(model, self.X_train, self.Y_train, cv=kfold, scoring=scoring)
            results.append(cv_results)
            names.append(name)
            msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
            print(msg)

        # Compare Algorithms
        fig = plt.figure(figsize=(25,5))
        fig.suptitle('Algorithm Comparison')
        ax = fig.add_subplot(111)
        plt.boxplot(results)
        ax.set_xticklabels(names)
    
    def scaling_block(self, scaler):
        if scaler == 'Standard':
            pipeline = self.pipelines1
        elif scaler == 'MinMax':
            pipeline = self.pipelines2
        elif scaler == 'Robust':
            pipeline = self.pipelines3

        results = []
        names = []
        for name, model in pipeline:
            scoring = 'neg_mean_squared_error'
            kfold = KFold(n_splits=10, shuffle=True)
            cv_results = cross_val_score(model, self.X_train, self.Y_train, cv=kfold, scoring=scoring)
            results.append(cv_results)
            names.append(name)
            msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
            print(msg)

        # Compare Algorithms
        fig = plt.figure(figsize=(25,5))
        fig.suptitle(f'{scaler} Scaled Algorithm Comparison')
        ax = fig.add_subplot(111)
        plt.boxplot(results)
        ax.set_xticklabels(names)
 

    def tunning_block(self):
        param_grids = dict()
        # PARAM_GRID : KNC
        param_grids['KNC'] = dict(
                n_neighbors=np.array([1,3,5,7,9,11,13,15,17,19,21])
                )

        # PARAM_GRID : KNR
        param_grids['KNR'] = dict(
                n_neighbors=np.array([1,3,5,7,9,11,13,15,17,19,21])
                )
        # PARAM_GRID : CART
        param_grids['CART'] = dict(
                max_depth=[None,2,3,4,5,6]
                )
        # PARAM_GRID : SVR
        param_grids['SVR'] = dict(
                C=[0.1, 0.3, 0.5, 0.7, 0.9, 1.0, 1.3, 1.5, 1.7, 2.0],
                kernel=['linear', 'poly', 'rbf', 'sigmoid']
                )
        # PARAM_GRID : ABR
        param_grids['ABR'] = dict(
                n_estimators=np.array([50,100,150,200,250,300,350,400]),
                #max_depth=[80, 90, 100, 110],
                #max_features=[2, 3],
                #min_samples_leaf=[3, 4, 5],
                #min_samples_split=[8, 10, 12],
                )
        # PARAM_GRID : GBR
        param_grids['GBR'] = dict(
                n_estimators=np.array([50,100,150,200,250,300,350,400]),
                #max_depth=[80, 90, 100, 110],
                #max_features=[2, 3],
                #min_samples_leaf=[3, 4, 5],
                #min_samples_split=[8, 10, 12],
                )
        # PARAM_GRID : RFR
        param_grids['RFR'] = dict(
                n_estimators=np.array([50,100,150,200,250,300,350,400]),
                #max_depth=[80, 90, 100, 110],
                #max_features=[2, 3],
                #min_samples_leaf=[3, 4, 5],
                #min_samples_split=[8, 10, 12],
                )
        # PARAM_GRID : ETR
        param_grids['ETR'] = dict(
                n_estimators=np.array([50,100,150,200,250,300,350,400]),
                #max_depth=[80, 90, 100, 110],
                #max_features=[2, 3],
                #min_samples_leaf=[3, 4, 5],
                #min_samples_split=[8, 10, 12],
                )

        scaler = StandardScaler().fit(self.X_train)
        rescaledX = scaler.transform(self.X_train)
        scoring = 'neg_mean_squared_error'
        kfold = KFold(n_splits=10, shuffle=True)
        for name, model in self.baselines:
            if name in param_grids.keys():
                grid = GridSearchCV(estimator=model, param_grid=param_grids[name], scoring=scoring, cv=kfold)
                grid_result = grid.fit(rescaledX, self.Y_train)
                logger['forecast'].info(f"[{name}] Best: {grid_result.best_score_} using {grid_result.best_params_}")
                means = grid_result.cv_results_['mean_test_score']
                stds = grid_result.cv_results_['std_test_score']
                params = grid_result.cv_results_['params']
                for mean, stdev, param in zip(means, stds, params):
                    print("%f (%f) with: %r" % (mean, stdev, param))

    def ensemble_block(self):
        pass
    
    def feature_store(self):
        pass

    def model_registry(self):
        pass

    def analysis_report_repository(self):
        pass
    


