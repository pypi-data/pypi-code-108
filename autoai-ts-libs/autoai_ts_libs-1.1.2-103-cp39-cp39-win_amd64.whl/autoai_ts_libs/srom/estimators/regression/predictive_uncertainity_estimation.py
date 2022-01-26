import warnings
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import BaggingRegressor
from autoai_ts_libs.utils.messages.messages import Messages
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

class PredictiveUncertaintyEstimator(BaseEstimator, RegressorMixin):
    """
    A Predictive Uncertainty regressor.
    """
                
    def fit(self, X, y):
        """
        fit the model from the training set (X, y).
        
        Parameters:
            X: Array-like, shape = [m, n] where m is the number of samples \
                and n is the number of features, the training predictors. \
                The X parameter can be a numpy array, a pandas DataFrame, a patsy
                DesignMatrix, or a tuple of patsy DesignMatrix objects as
                output by patsy.dmatrices.
            y: Array-like, shape = [m, p] where m is the number of samples \
                the training responds, p the number of outputs. \
                The y parameter can be a numpy array, a pandas DataFrame, \
                a Patsy DesignMatrix, or can be left as None(default) if X was \
                the output of a call to patsy.dmatrices (in which case, X contains \
                the response).
            
        Returns:
            self : object.
        """
        for item in self.bagging_models:
            item.fit(X,y)
        return self

    def _get_result_summary(self, tmp_result):
        """
        internal method.
        """
        if self.aggr_type == 'mean':
            result = np.mean(tmp_result,axis=0)
        elif self.aggr_type == 'median':
            result = np.median(tmp_result,axis=0)
        else:
            raise Exception(Messages.get_message(self.aggr_type, message_id='AUTOAITSLIBS0054E'))
        return result
    
    def predict(self, X):
        """
        Predict the response based on the input data X.
        
        Parameters:
            X: Array-like, shape = [m, n] where m is the number of samples and n \
                is the number of features, the training predictors. The X parameter \
                can be a numpy array, a pandas DataFrame, or a patsy DesignMatrix.
            
        Returns:
            y: Array of shape = [m] or [m, p] where m is the number of samples \
                and p is the number of outputs.The predicted values.
        """
        _prediction = []
        for item in self.bagging_models:
            for item_estimator in item.estimators_:
                y_pred = item_estimator.predict(X)
                # Fix for shape in case of 1d output (some algorithms do not have consistent output)
                if((len(y_pred.shape)> 1) and (y_pred.shape[1]==1)):
                    y_pred = y_pred.reshape(-1) 
                _prediction.append(y_pred)
        result = np.array(_prediction)
        return self._get_result_summary(result)

    def predict_interval(self, X, percentile=95):
        """
        Calculates prediction interval.
        
        Parameters:
            X: Array-like, shape = [m, n] where m is the number of samples and n \
                is the number of features, the training predictors. The X parameter \
                can be a numpy array, a pandas DataFrame, or a patsy DesignMatrix.
            percentile: int confidence interval.
        
        Return:
            Prediction interval.
        """
        _prediction = []
        for item in self.bagging_models:
            for item_estimator in item.estimators_:
                y_pred = item_estimator.predict(X)
                # Fix for shape in case of 1d output (some algorithms do not have consistent output)
                if((len(y_pred.shape)> 1) and (y_pred.shape[1]==1)):
                    y_pred = y_pred.reshape(-1) 
                _prediction.append(y_pred)
        result = np.array(_prediction)
        lower_bound = np.percentile(result,(100 - percentile) / 2.,axis=0)
        upper_bound = np.percentile(result,100 - (100 - percentile) / 2.,axis=0)
        result = np.array([lower_bound, upper_bound])
        return result.transpose()
    