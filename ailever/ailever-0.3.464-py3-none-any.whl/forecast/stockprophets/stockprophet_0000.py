from ...logging_system import logger

import re
from datetime import datetime

# preprocessing
import FinanceDataReader as fdr
from scipy import stats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import FeatureUnion

# modeling
import statsmodels.api as sm
import statsmodels.tsa.api as smt
from sklearn.linear_model import LogisticRegression, Perceptron, RidgeClassifier, SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, AdaBoostClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

# evaluation
from sklearn.model_selection import train_test_split, cross_validate
from sklearn import metrics

class FeatureSelection(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
    
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        import pandas as pd
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        from sklearn.preprocessing import Normalizer # MinMaxScaler, StandardScaler, RobustScaler, Normalizer

        # Scaling
        X = pd.DataFrame(data=Normalizer().fit_transform(X), index=X.index, columns=X.columns)
        
        # VIF Feature Selection
        features_by_vif = pd.Series(
            data = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])], 
            index = range(X.shape[1])).sort_values(ascending=True).iloc[:X.shape[1] - 5].index.tolist()
        return X.iloc[:, features_by_vif].copy()

def predictor():
    def decorator(func):
        def wrapper(model, X, y, model_name='model', domain_kind='train'):
            if model_name == 'Logit':
                y_ = model.predict(sm.add_constant(X))
            elif model_name == 'CatBoostClassifier':
                y_ = model.predict(X).squeeze()  
            else:
                y_ = model.predict(X)
                
            if not isinstance(y_, pd.Series):
                y_ = pd.Series(y_, index=y.index)
            return y_
        return wrapper
    return decorator

@predictor()
def prediction(model, X:pd.Series, y:pd.Series, model_name='model', domain_kind='train'):
    return

def evaluation(y_true, y_pred, date_range, model_name='model', code=None, lag_shift=None, domain_kind='train', comment=None):
    summary = dict()
    summary['datetime'] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    summary['code'] = [code]
    summary['model'] = [model_name]
    summary['domain'] = [domain_kind]
    summary['start'] = [date_range[0].to_pydatetime().strftime('%Y-%m-%d %H:%M:%S')]
    summary['end'] = [date_range[-1].to_pydatetime().strftime('%Y-%m-%d %H:%M:%S')]
    summary['LAG'] = [lag_shift]    
    summary['EndDateFluctuation'] = 'Increase' if y_pred[-1] == 1 else 'Decrease'
    summary['ObjectiveDate'] = [date_range[-2:-1].shift(lag_shift)[0]]
    summary['ACC'] = [metrics.accuracy_score(y_true, y_pred)]
    summary['BA'] = [metrics.balanced_accuracy_score(y_true, y_pred)]
    summary['F1'] = [metrics.f1_score(y_true, y_pred, average='micro')]
    summary['Fbeta'] = [metrics.fbeta_score(y_true, y_pred, beta=2, average='micro')]
    fpr, tpr1, thresholds1 = metrics.roc_curve(y_true, y_pred)
    ppv, tpr2, thresholds2 = metrics.precision_recall_curve(y_true, y_pred)
    summary['ROCAUC'] = [metrics.auc(fpr, tpr1)]
    summary['PRAUC'] = [metrics.auc(tpr2, ppv)]
    summary['HL'] = [metrics.hamming_loss(y_true, y_pred)]
    summary['JS'] = [metrics.jaccard_score(y_true, y_pred, average='micro')]
    summary['MCC'] = [metrics.matthews_corrcoef(y_true, y_pred)]
    summary['PPV'] = [metrics.precision_score(y_true, y_pred, average='micro')]
    summary['TPR'] = [metrics.recall_score(y_true, y_pred, average='micro')]
    summary['ZOL'] = [metrics.zero_one_loss(y_true, y_pred)]
    summary['Comment'] = [comment]
    eval_matrix = pd.DataFrame(summary)
    return eval_matrix    


class StockForecaster:
    def __init__(self, code, lag_shift, sequence_length=5):
        self.code = code
        self.lag_shift = lag_shift
        self.preprocessing(code, lag_shift, sequence_length, download=True, return_Xy=False)
        self.modeling(code, lag_shift)

    def preprocessing(self, code, lag_shift, sequence_length, download=True, return_Xy=False):
        logger['forecast'].info(f"[{code}|{lag_shift}] PREPROCESSING...")
        if download:
            df1 = fdr.DataReader(code)
            df2 = fdr.DataReader('VIX')
            df3 = fdr.DataReader('US1YT=X')
            df = pd.concat([df1[['Open', 'High', 'Low', 'Close', 'Volume']].rename(columns={'Close':'target'}), df2['Close'].rename('VIX'), df3['Close'].rename('BOND')], join='inner', axis=1)
            df = df.asfreq('B').fillna(method='ffill').fillna(method='bfill')
            self.origin_df = df.copy()
        else:
            df = self.origin_df.copy()

        # [time series core feature] previous time series(1)
        df[f'target_lag_shift{(lag_shift - 1) + 1}'] = df['target'].shift((lag_shift - 1) + 1).fillna(method='bfill')
        df[f'target_lag_shift{(lag_shift - 1) + 2}'] = df['target'].shift((lag_shift - 1) + 2).fillna(method='bfill')
        df[f'target_lag_shift{(lag_shift - 1) + 3}'] = df['target'].shift((lag_shift - 1) + 3).fillna(method='bfill')
        df[f'target_lag_shift{(lag_shift - 1) + 4}'] = df['target'].shift((lag_shift - 1) + 4).fillna(method='bfill')
        df[f'target_lag_shift{(lag_shift - 1) + 5}'] = df['target'].shift((lag_shift - 1) + 5).fillna(method='bfill')

        # [time series core feature] previous time series(2)
        df[f'target_diff1_lag_shift{(lag_shift - 1) + 1}'] = df['target'].diff(1).shift((lag_shift - 1) + 1).fillna(method='bfill')
        df[f'target_diff2_lag_shift{(lag_shift - 1) + 1}'] = df['target'].diff(2).shift((lag_shift - 1) + 1).fillna(method='bfill')
        df[f'target_diff3_lag_shift{(lag_shift - 1) + 1}'] = df['target'].diff(3).shift((lag_shift - 1) + 1).fillna(method='bfill')
        df[f'target_diff4_lag_shift{(lag_shift - 1) + 1}'] = df['target'].diff(4).shift((lag_shift - 1) + 1).fillna(method='bfill')
        df[f'target_diff5_lag_shift{(lag_shift - 1) + 1}'] = df['target'].diff(5).shift((lag_shift - 1) + 1).fillna(method='bfill')

        # [time series core feature] sequence through decomposition, rolling
        decomposition = smt.seasonal_decompose(df['target'].shift((lag_shift - 1) + 1).fillna(method='bfill'), model=['additive', 'multiplicative'][0], two_sided=False)
        df['target_trend'] = decomposition.trend.fillna(method='ffill').fillna(method='bfill')
        df['target_seasonal'] = decomposition.seasonal
        df['target_by_week'] = decomposition.observed.rolling(7).mean().fillna(method='ffill').fillna(method='bfill')
        df['target_by_month'] = decomposition.observed.rolling(7*4).mean().fillna(method='ffill').fillna(method='bfill')
        df['target_by_quarter'] = decomposition.observed.rolling(int(365/4)).mean().fillna(method='ffill').fillna(method='bfill')
        df['target_trend_by_week'] = decomposition.trend.rolling(7).mean().fillna(method='ffill').fillna(method='bfill')
        df['target_trend_by_month'] = decomposition.trend.rolling(7*4).mean().fillna(method='ffill').fillna(method='bfill')
        df['target_trend_by_quarter'] = decomposition.trend.rolling(int(365/4)).mean().fillna(method='ffill').fillna(method='bfill')
        df['target_seasonal_by_week'] = decomposition.seasonal.rolling(7).mean().fillna(method='ffill').fillna(method='bfill')
        df['target_seasonal_by_month'] = decomposition.seasonal.rolling(7*4).mean().fillna(method='ffill').fillna(method='bfill')
        df['target_seasonal_by_quarter'] = decomposition.seasonal.rolling(int(365/4)).mean().fillna(method='ffill').fillna(method='bfill')

        # [time series core feature] current time series properties
        df['datetime_year'] = df.index.year.astype(int)
        df['datetime_quarterofyear'] = df.index.quarter.astype(int)
        df['datetime_monthofyear'] = df.index.month.astype(int)
        df['datetime_weekofyear'] = df.index.isocalendar().week # week of year
        df['datetime_dayofyear'] = df.index.dayofyear
        df['datetime_dayofmonth'] = df.index.day.astype(int)
        df['datetime_dayofweek'] = df.index.dayofweek.astype(int)

        # [time series feature] additinal informations
        df['Open'] = df['Open'].shift((lag_shift - 1) + 1).fillna(method='bfill')
        df['High'] = df['High'].shift((lag_shift - 1) + 1).fillna(method='bfill')
        df['Low'] = df['Low'].shift((lag_shift - 1) + 1).fillna(method='bfill')
        df['Volume'] = df['Volume'].shift((lag_shift - 1) + 1).fillna(method='bfill')
        df['VIX'] = df['VIX'].shift((lag_shift - 1) + 1).fillna(method='bfill')
        df['BOND'] = df['BOND'].shift((lag_shift - 1) + 1).fillna(method='bfill')
        df = df.rename(columns=
                {'Open':f'open_lag_shift{(lag_shift - 1) + 1}', 
                 'High':f'high_lag_shift{(lag_shift - 1) + 1}', 
                 'Low':f'low_lag_shift{(lag_shift - 1) + 1}', 
                 'Volume':f'volume_lag_shift{(lag_shift - 1) + 1}',
                 'VIX':f'vix_lag_shift{(lag_shift - 1) + 1}',
                 'BOND':f'bond_lag_shift{(lag_shift - 1) + 1}',
                 })

        # [Data Analysis] variable grouping, binning
        num_bin = 5
        for column in df.drop(['target'], axis=1).columns:
            _, threshold = pd.qcut(df[column], q=num_bin, precision=6, duplicates='drop', retbins=True)
            df[column+f'_efbin{num_bin}'] = pd.qcut(df[column], q=num_bin, labels=threshold[1:], precision=6, duplicates='drop', retbins=False).astype(float)
            _, threshold = pd.cut(df[column], bins=num_bin, precision=6, retbins=True)
            df[column+f'_ewbin{num_bin}'] = pd.cut(df[column], bins=num_bin, labels=threshold[1:], precision=6, retbins=False).astype(float)  

        # [exogenous feature engineering] Feature Selection by MultiCollinearity after scaling
        df[f'Change_lag_shift{lag_shift}'] = df['target'].diff(lag_shift).fillna(method='bfill')
        train_df = df.drop(['target'], axis=1).copy()
        X = train_df.loc[:, train_df.columns != f'Change_lag_shift{lag_shift}']
        y = train_df.loc[:, train_df.columns == f'Change_lag_shift{lag_shift}'][f'Change_lag_shift{lag_shift}'].apply(lambda x: 1 if x > 0 else 0).to_frame()

        fs = FeatureSelection()
        X = fs.fit_transform(X)

        # [dataset split] Valiation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)
        
        # Store
        df = df.rename(columns={'target':'Close'})
        self.dataset = df.copy()
        self.price = df[['Close']].copy()
        self.X = X.copy()
        self.y = y.copy()
        self.X_train = X_train.copy()
        self.X_test = X_test.copy()
        self.y_train = y_train.copy()
        self.y_test = y_test.copy()

    def ModelLogit(self, X, y):
        self.model = sm.Logit(y, sm.add_constant(X)).fit() #display(models['Logit'].summay())
        return self.model

    def ModelLogisticRegression(self, X, y):
        self.model = LogisticRegression().fit(X, y)
        return self.model

    def ModelPerceptron(self, X, y):
        self.model = Perceptron().fit(X, y)
        return self.model

    def ModelRidgeClassifier(self, X, y):
        self.model = RidgeClassifier().fit(X, y)
        return self.model

    def ModelSGDClassifier(self, X, y):
        self.model = SGDClassifier().fit(X, y)
        return self.model

    def ModelDecisionTreeClassifier(self, X, y):
        self.model = DecisionTreeClassifier().fit(X, y)
        return self.model

    def ModelRandomForestClassifier(self, X, y):
        self.model = RandomForestClassifier(n_estimators=100, random_state=2022).fit(X, y)
        return self.model

    def ModelBaggingClassifier(self, X, y):
        self.model = BaggingClassifier(n_estimators=100, random_state=2022).fit(X, y)
        return self.model

    def ModelAdaBoostClassifier(self, X, y):
        self.model = AdaBoostClassifier(n_estimators=100, random_state=2022).fit(X, y)
        return self.model

    def ModelGradientBoostingClassifier(self, X, y):
        self.model = GradientBoostingClassifier(subsample=0.3, max_features='sqrt', learning_rate=0.05, n_estimators=1000, random_state=2022).fit(X, y)
        return self.model

    def ModelXGBClassifier(self, X, y):
        self.model = XGBClassifier(subsample=0.3, colsample_bylevel=0.3, colsample_bynode=0.3, colsample_bytree=0.3, learning_rate=0.05, n_estimators=1000, random_state=2022).fit(X, y)
        return self.model

    def ModelLGBMClassifier(self, X, y):
        self.model = LGBMClassifier(subsample=0.3, colsample_bynode=0.3, colsample_bytree=0.3, learning_rate=0.05, n_estimators=1000, random_state=2022).fit(X, y)
        return self.model

    def ModelCatBoostClassifier(self, X, y):
        self.model = CatBoostClassifier(subsample=0.3, colsample_bylevel=0.3, reg_lambda=0, learning_rate=0.05, n_estimators=1000, random_state=2022).fit(X, y, silent=True)
        return self.model

    def modeling(self, code, lag_shift):
        logger['forecast'].info(f"MODELING...")

        # [modeling]
        models = dict()
        #models['Logit'] = self.ModelLogit(self.y_train, self.X_train)
        models['LogisticRegression'] = self.ModelLogisticRegression(self.X_train.values, self.y_train.values.ravel())
        models['Perceptron'] = self.ModelPerceptron(self.X_train.values, self.y_train.values.ravel())
        models['RidgeClassifier'] = self.ModelRidgeClassifier(self.X_train.values, self.y_train.values.ravel())
        models['SGDClassifier'] = self.ModelSGDClassifier(self.X_train.values, self.y_train.values.ravel())
        models['DecisionTreeClassifier'] = self.ModelDecisionTreeClassifier(self.X_train.values, self.y_train.values.ravel())
        models['RandomForestClassifier'] = self.ModelRandomForestClassifier(self.X_train.values, self.y_train.values.ravel())
        models['BaggingClassifier'] = self.ModelBaggingClassifier(self.X_train.values, self.y_train.values.ravel())
        models['AdaBoostClassifier'] = self.ModelAdaBoostClassifier(self.X_train.values, self.y_train.values.ravel())
        models['GradientBoostingClassifier'] = self.ModelGradientBoostingClassifier(self.X_train.values, self.y_train.values.ravel())
        models['XGBClassifier'] = self.ModelXGBClassifier(self.X_train.values, self.y_train.values.ravel())
        models['LGBMClassifier'] = self.ModelLGBMClassifier(self.X_train.values, self.y_train.values.ravel())
        models['CatBoostClassifier'] = self.ModelCatBoostClassifier(self.X_train.values, self.y_train.values.ravel())
        self.models = models
        self.model = list(models.values())[-1]

        order = lag_shift
        y_train_true = self.y_train[order:]  # pd.Sereis
        y_test_true = self.y_test[order:]    # pd.Sereis
        X_train_true = self.X_train[order:]  # pd.Sereis
        X_test_true = self.X_test[order:]    # pd.Sereis

        self.y.plot(lw=0, marker='o', c='black', grid=True, figsize=(25,7))
        logger['forecast'].info(f"EVALUATING...")
        for idx, (name, model) in enumerate(models.items()):
            y_train_pred = prediction(model, self.X_train, self.y_train, model_name=name, domain_kind='train')[order:] # pd.Series
            y_test_pred = prediction(model, self.X_test, self.y_test, model_name=name, domain_kind='test')[order:]     # pd.Series
            
            # Visualization Process
            pd.Series(data=y_train_pred.values.squeeze(), index=self.y_train.index[order:], name=name+'|train').plot(legend=True, grid=True, lw=0, marker='x', figsize=(25,7))
            pd.Series(data=y_test_pred.values.squeeze(), index=self.y_test.index[order:], name=name+'|test').plot(legend=True, grid=True, lw=0, marker='x', figsize=(25,7))


            # Evaluation Process
            eval_matrix = evaluation(y_train_true.values.squeeze(), y_train_pred.values.squeeze(), date_range=self.y_train.index[order:], model_name=name, code=code, lag_shift=lag_shift, domain_kind='train', comment=None)
            if idx == 0:
                if not hasattr(self, 'eval_table'):
                    eval_table = eval_matrix.copy() 
                else:
                    eval_table = eval_table.append(eval_matrix.copy()) 
            else:
                eval_table = eval_table.append(eval_matrix.copy()) 
                
            eval_matrix = evaluation(y_test_true.values.squeeze(), y_test_pred.values.squeeze(), date_range=self.y_test.index[order:], model_name=name, code=code, lag_shift=lag_shift, domain_kind='test', comment=None)
            eval_table = eval_table.append(eval_matrix.copy())
            judgement = eval_table['EndDateFluctuation'].iloc[-1]
            target_date = eval_table['end'].iloc[-1]
            logger['forecast'].info(f"[{target_date}] {name}: {judgement}")
        plt.show()
        self.eval_table = eval_table

    def validate(self, model_name, trainstartdate, teststartdate, code, lag_shift, sequence_length, comment, visual_on):
        if code is not None:
            if self.code != code:
                self.code = code
            else:
                code = None
            
            # when the code is not changed comparing with the previous thing
            if code is None:
                code = self.code
                if lag_shift is not None:
                    if self.lag_shift != lag_shift:
                        self.lag_shift = lag_shift
                    else:
                        lag_shift = None
                    
                    if lag_shift is None:
                        lag_shift = self.lag_shift
                    # when lag_shift is changed
                    else:
                        self.preprocessing(self.code, lag_shift=lag_shift, sequence_length=sequence_length, download=False, return_Xy=False)
                else:
                    pass
            # when code is changed
            else:
                if lag_shift is not None:
                    self.lag_shift = lag_shift
                    self.preprocessing(code, lag_shift=lag_shift, sequence_length=sequence_length, download=True, return_Xy=False)
                else:
                    self.preprocessing(code, lag_shift=self.lag_shift, sequence_length=sequence_length, download=True, return_Xy=False)
        # when the code is not changed comparing with the previous thing
        else:
            if lag_shift is not None:
                if self.lag_shift != lag_shift:
                    self.lag_shift = lag_shift
                else:
                    lag_shift = None
                
                if lag_shift is None:
                    lag_shift = self.lag_shift
                # when lag_shift is changed
                else:
                    self.preprocessing(self.code, lag_shift=lag_shift, sequence_length=sequence_length, download=False, return_Xy=False)
            else:
                pass

        code = self.code
        lag_shift = self.lag_shift

        # [Inference]
        train_start_date = trainstartdate
        test_start_date = teststartdate

        X_ = self.X.loc[train_start_date:]
        y_ = self.y.loc[train_start_date:]

        X_train_true = X_.loc[train_start_date:test_start_date]
        y_train_true = y_.loc[train_start_date:test_start_date]
        X_test_true = X_.loc[test_start_date:]
        y_test_true = y_.loc[test_start_date:]

        self.models[model_name] = getattr(self, 'Model'+model_name)(X_train_true.values, y_train_true.values.ravel())
        y_train_pred = prediction(self.models[model_name], X_train_true, y_train_true, model_name=model_name, domain_kind='train') # pd.Series
        y_test_pred = prediction(self.models[model_name], X_test_true, y_test_true, model_name=model_name, domain_kind='test')     # pd.Series

        eval_matrix = evaluation(y_train_true.values.squeeze(), y_train_pred.values.squeeze(), date_range=y_train_true.index, model_name=model_name, code=code, lag_shift=lag_shift, domain_kind='train', comment=comment)
        eval_table = self.eval_table.append(eval_matrix.copy()) 
        eval_matrix = evaluation(y_test_true.values.squeeze(), y_test_pred.values.squeeze(), date_range=y_test_true.index, model_name=model_name, code=code, lag_shift=lag_shift, domain_kind='test', comment=comment)
        eval_table = eval_table.append(eval_matrix.copy())

        if visual_on:
            fig = plt.figure(figsize=(25,7))
            ax = plt.subplot2grid((1,1), (0,0))
            fig.add_axes(y_.loc[train_start_date:].plot(lw=0, marker='o', c='black', ax=ax))
            fig.add_axes(prediction(self.models[model_name], X_train_true, y_train_true, model_name=model_name, domain_kind='train').plot(grid=True, lw=0, marker='x', c='r', label='Train', ax=ax))
            fig.add_axes(prediction(self.models[model_name], X_test_true, y_test_true, model_name=model_name, domain_kind='test').plot(grid=True, lw=0, marker='x', c='b', label='Test', ax=ax))
            ax.legend()
            plt.show()
        
        self.eval_table = eval_table.copy()
        return eval_table.iloc[::-1].copy()

    def inference(self, model_name, trainstartdate, teststartdate, code, lag_shift, sequence_length, comment, visual_on):
        if code is not None:
            if self.code != code:
                self.code = code
            else:
                code = None
            
            # when the code is not changed comparing with the previous thing
            if code is None:
                code = self.code
                if lag_shift is not None:
                    if self.lag_shift != lag_shift:
                        self.lag_shift = lag_shift
                    else:
                        lag_shift = None
                    
                    if lag_shift is None:
                        lag_shift = self.lag_shift
                    # when lag_shift is changed
                    else:
                        self.preprocessing(self.code, lag_shift=lag_shift, sequence_length=sequence_length, download=False, return_Xy=False)
                else:
                    pass
            # when code is changed
            else:
                if lag_shift is not None:
                    self.lag_shift = lag_shift
                    self.preprocessing(code, lag_shift=lag_shift, sequence_length=sequence_length, download=True, return_Xy=False)
                else:
                    self.preprocessing(code, lag_shift=self.lag_shift, sequence_length=sequence_length, download=True, return_Xy=False)
        # when the code is not changed comparing with the previous thing
        else:
            if lag_shift is not None:
                if self.lag_shift != lag_shift:
                    self.lag_shift = lag_shift
                else:
                    lag_shift = None
                
                if lag_shift is None:
                    lag_shift = self.lag_shift
                # when lag_shift is changed
                else:
                    self.preprocessing(self.code, lag_shift=lag_shift, sequence_length=sequence_length, download=False, return_Xy=False)
            else:
                pass

        code = self.code
        lag_shift = self.lag_shift

        # [Inference]
        train_start_date = trainstartdate
        test_start_date = teststartdate

        X_ = self.X.loc[train_start_date:]
        y_ = self.y.loc[train_start_date:]

        X_train_true = X_.loc[train_start_date:test_start_date]
        y_train_true = y_.loc[train_start_date:test_start_date]
        X_test_true = X_.loc[test_start_date:]
        y_test_true = y_.loc[test_start_date:]

        self.models[model_name] = getattr(self, 'Model'+model_name)(X_train_true.values, y_train_true.values.ravel())
        y_train_pred = prediction(self.models[model_name], X_train_true, y_train_true, model_name=model_name, domain_kind='train') # pd.Series
        y_test_pred = prediction(self.models[model_name], X_test_true, y_test_true, model_name=model_name, domain_kind='test')     # pd.Series

        eval_matrix = evaluation(y_train_true.values.squeeze(), y_train_pred.values.squeeze(), date_range=y_train_true.index, model_name=model_name, code=code, lag_shift=lag_shift, domain_kind='train', comment=comment)
        eval_table = self.eval_table.append(eval_matrix.copy()) 
        eval_matrix = evaluation(y_test_true.values.squeeze(), y_test_pred.values.squeeze(), date_range=y_test_true.index, model_name=model_name, code=code, lag_shift=lag_shift, domain_kind='test', comment=comment)
        eval_table = eval_table.append(eval_matrix.copy())

        if visual_on:
            fig = plt.figure(figsize=(25,7))
            ax = plt.subplot2grid((1,1), (0,0))
            fig.add_axes(y_.loc[train_start_date:].plot(lw=0, marker='o', c='black', ax=ax))
            fig.add_axes(prediction(self.models[model_name], X_train_true, y_train_true, model_name=model_name, domain_kind='train').plot(grid=True, lw=0, marker='x', c='r', label='Train', ax=ax))
            fig.add_axes(prediction(self.models[model_name], X_test_true, y_test_true, model_name=model_name, domain_kind='test').plot(grid=True, lw=0, marker='x', c='b', label='Test', ax=ax))
            ax.legend()
            plt.show()
        
        self.eval_table = eval_table.copy()
        return eval_table.iloc[::-1].copy()

