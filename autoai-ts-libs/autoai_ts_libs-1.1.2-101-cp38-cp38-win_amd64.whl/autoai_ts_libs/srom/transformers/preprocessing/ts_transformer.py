from math import fabs
from autoai_ts_libs.srom.transformers.feature_engineering.base import DataTransformer, TargetTransformer
from autoai_ts_libs.srom.transformers.feature_engineering.timeseries.function_map import mapper
from sklearn.utils.validation import check_array, check_is_fitted
import numpy as np
import pandas as pd
from multiprocessing import cpu_count, Pool
from joblib import Parallel, delayed
from functools import partial
from sklearn.utils import check_random_state
from autoai_ts_libs.utils.messages.messages import Messages


# Summary Statistics
PD_FUNC_LIST_SS = ['mean', 'max', 'min', 'median', 'sum', 'std', 'var']

#Advanced Summary Statistics
FUNC_LIST_ASS = ['rate_of_change', 'sum_of_change', 'absoluate_sum_of_change', 'trend_slop', \
                'abs_energy', 'mean_abs_change', 'mean_change', 'mean_second_derivate_central', \
                    'count_above_mean', 'count_below_mean', 'last_location_of_maximum', \
                        'first_location_of_maximum', 'corr_coefficient']

# Wavelet Features
FUNC_LIST_WT = ['wavelet_feature_haar']

# FFT Features
FUNC_LIST_FFT = ['fft_coefficient_real']

# Higher Order Features
FUNC_LIST_HOF = ['quantile_25', 'quantile_75', 'quantile_range']
PD_FUNC_LIST_HOF = ['sum', 'skew', 'kurt']

# All Features
FUNC_LIST_UNION = FUNC_LIST_ASS + FUNC_LIST_WT + FUNC_LIST_FFT + FUNC_LIST_HOF
PD_FUNC_LIST_UNION = PD_FUNC_LIST_SS + PD_FUNC_LIST_HOF

class TimeTensorTransformer(DataTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing.
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
            where n_samples is the number of samples and n_features is the \
            number of features.
        num_look_back (int, optional): Look-back window for the model.
        n_steps_ahead (int): Look-ahead window for the model.
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """
    def __init__(self, 
                 feature_col_index, 
                 target_col_index,
                 lookback_win=1, 
                 pred_win=1):
        self.feature_col_index = feature_col_index
        self.target_col_index = target_col_index
        self.lookback_win = lookback_win
        self.pred_win = pred_win

        self._input_data_dim = (None, len(feature_col_index))
        self._output_data_dim = (None, (lookback_win, len(feature_col_index)))

    def _check_meta_data(self, data_shape):
        if self.feature_col_index is None:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0027E'))
        if self.target_col_index is None:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0028E'))
        if (self.lookback_win + self.pred_win) > data_shape[0]:
            raise Exception(Messages.get_message(format(self.lookback_win),
                                                 format(self.pred_win),
                                                 format(data_shape[0]), message_id='AUTOAITSLIBS0029E'))
    
    def _check_window_params(self):
        if self.lookback_win <= self.lookback_win_min:
            raise Exception(Messages.get_message(format(self.lookback_win_min), message_id='AUTOAITSLIBS0030E'))
        if self.pred_win <= self.pred_win_min:
            raise Exception(Messages.get_message(format(self.pred_win_min), message_id='AUTOAITSLIBS0031E'))

    def _apply_custom_transformer_func(self, func_list, values, col_prefix=""):
        temp = []
        cols = []
        for func in func_list:
            t_x = mapper(func)(values)
            if isinstance(t_x, (list, np.ndarray)):
                for i, t_x_i in enumerate(t_x):
                    cols.append(col_prefix + func + "_" + str(i))
                    temp.append(t_x_i)
            else:
                cols.append(col_prefix + func)
                temp.append(t_x)

        temp_df = pd.DataFrame(np.array([temp]), columns=cols)
        return temp_df
    
    def _apply_transformer_func(self, df, func_list=None, pd_func_list=None):
        transformed_df = None
        for col in df.columns:
            col_prefix = "c" + str(col) + "_"
            
            if func_list is not None:
                if not isinstance(transformed_df, pd.DataFrame):
                    transformed_df = self._apply_custom_transformer_func(func_list, df[col], col_prefix)
                else:
                    temp_df = self._apply_custom_transformer_func(func_list, df[col], col_prefix)
                    transformed_df = pd.concat([transformed_df,
                                                temp_df],
                                                axis=1)
            if pd_func_list is not None:
                new_pd_func_list = [col_prefix + x for x in pd_func_list]
                new_ser = df[col].agg(pd_func_list)
                temp_df = pd.DataFrame(new_ser.tolist(), index=new_pd_func_list)
                
                if transformed_df is None:
                    transformed_df = temp_df.T
                else:
                    transformed_df = pd.concat([transformed_df, temp_df.T], axis=1)

        return transformed_df
    
    def fit(self, X, y=None):
        self._check_meta_data(X.shape)
        X = check_array(X, accept_sparse=True)
        self.n_features_ = X.shape[1]
        return self

    def transform(self, X, y=None):
        self._check_meta_data(X.shape)
        if isinstance(X, pd.DataFrame):
            X = X.values

        X = check_array(X, accept_sparse=True)
        check_is_fitted(self, 'n_features_')
        if X.shape[1] != self.n_features_:
            raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0032E'))

        _x, _y = [], []
        if self.lookback_win > 0:
            for i in range(self.lookback_win, X.shape[0] - self.pred_win + 1):
                _x.append(X[i - self.lookback_win:i, self.feature_col_index])
                if self.pred_win > 1:
                    _y.append(X[i:i + self.pred_win, self.target_col_index])
                else:
                    _y.append(X[i + self.pred_win-1, self.target_col_index])
            _x, _y = np.array(_x), np.array(_y)
        elif self.lookback_win <= -1:  # to support univariate arima model
            _x = X[:, self.feature_col_index]
            _x = _x.flatten()
            _y = _x.copy()
        else:
            raise Exception(Messages.get_message(format(self.lookback_win), message_id='AUTOAITSLIBS0033E'))

        return _x, _y

class Flatten(TimeTensorTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing.
    This utility support univariate, multi-variate, single-step and multi-step functionality.
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
        where n_samples is the number of samples and n_features is the number of features.
        num_look_back (int, optional): Look-back window for the model.
        n_steps_ahead (int): Look-ahead window for the model.
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """

    def __init__(self, 
                 feature_col_index, 
                 target_col_index,
                 lookback_win=1, 
                 pred_win=1):

        super(Flatten, self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )
        self._input_data_dim = (None, len(feature_col_index))
        self._output_data_dim = (None, lookback_win*len(feature_col_index))

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        _x, _y = super(Flatten, self).transform(X)

        # Regular flattening of 3D data to 2D data for consumption of IID models
        _x = [list(_x[i].flatten()) for i in range(len(_x))]
        _x = np.array(_x)

        if self.pred_win == 1:
            # Single Step Support
            if len(self.target_col_index) > 1:
                _y = _y.reshape(-1, len(self.target_col_index))
            else:
                _y = np.array(_y.ravel()).reshape(-1, 1)
        else:
            # Multi Step Support
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
            else:
                _y = _y.reshape(-1, self.pred_win*len(self.target_col_index))

        return _x, _y

class WaveletFeatures(TimeTensorTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing 
    using WaveletFeatures Transformer
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
            where n_samples is the number of samples and n_features is the number of features.
        feature_col_index (numpy array): feature indices
        target_col_index (numpy array): target indices
        lookback_win (int, optional): Look-back window for the model.
        pred_win (int): Look-ahead window for the model.
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """
    def __init__(self, 
                 feature_col_index, 
                 target_col_index,
                 lookback_win=1, 
                 pred_win=1,
                 n_jobs=cpu_count()-1):

        super(WaveletFeatures,self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )
        if n_jobs < 1:
            n_jobs = 1
        self.n_jobs = n_jobs
        self.lookback_win_min = 3
        self.pred_win_min = 0
        self._input_data_dim = (None, len(feature_col_index))

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        # self._check_flatten_type(self.flatten_type)
        self._check_window_params()
        _x, _y = super(WaveletFeatures, self).transform(X)

        # @TODO: Need to converge this aggregation with rolling_window_feature_extraction
        
        # finding the aggregate of each tensor using different window agg methods
        # like summary statistics
        _x = [pd.DataFrame(np.array(_x[i])) for i in range(len(_x))]
        func_list = FUNC_LIST_WT
        
        transformed_x = Parallel(n_jobs=self.n_jobs)(delayed(self._apply_transformer_func)
                                                     (item, func_list=func_list) 
                                                     for item in _x)
        '''
        p = Pool(self.n_jobs)
        transformed_x = p.map(partial(self._apply_transformer_func,
                                        func_list=func_list),
                                _x)
        p.close()
        '''
        
        _x = transformed_x
        col_len = len(_x[0].columns)
        self._output_data_dim = (None, col_len*len(self.feature_col_index))
        _x = [_x[i].values for i in range(len(_x))]

        # Regular flattening of 3D data to 2D data for consumption of IID models
        _x = [list(_x[i].flatten()) for i in range(len(_x))]
        _x = np.array(_x)
        if self.pred_win == 1:
            # Single Step Support
            if len(self.target_col_index) > 1:
                _y = _y.reshape(-1, len(self.target_col_index))
            else:
                _y = np.array(_y.ravel()).reshape(-1, 1)
        else:
            # Multi Step Support
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
            else:
                _y = _y.reshape(-1, self.pred_win*len(self.target_col_index))
        return _x, _y

class FFTFeatures(TimeTensorTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing 
    using FFTFeatures Transformer
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
            where n_samples is the number of samples and n_features is the number of features.
        feature_col_index (numpy array): feature indices
        target_col_index (numpy array): target indices
        lookback_win (int, optional): Look-back window for the model.
        pred_win (int): Look-ahead window for the model.
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """
    def __init__(self, 
                 feature_col_index, 
                 target_col_index,
                 lookback_win=1, 
                 pred_win=1,
                 n_jobs=cpu_count()-1):

        super(FFTFeatures,self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )
        if n_jobs < 1:
            n_jobs = 1
        self.n_jobs = n_jobs
        self.lookback_win_min = 3
        self.pred_win_min = 0
        self._input_data_dim = (None, len(feature_col_index))

    

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        # self._check_flatten_type(self.flatten_type)
        self._check_window_params()
        _x, _y = super(FFTFeatures, self).transform(X)

        # @TODO: Need to converge this aggregation with rolling_window_feature_extraction
        
        # finding the aggregate of each tensor using different window agg methods
        # like summary statistics
        _x = [pd.DataFrame(np.array(_x[i])) for i in range(len(_x))]
        
        func_list = FUNC_LIST_FFT
        transformed_x = Parallel(n_jobs=self.n_jobs)(delayed(self._apply_transformer_func)
                                                     (item, func_list=func_list) 
                                                     for item in _x)
                
        '''
        p = Pool(self.n_jobs)
        transformed_x = p.map(partial(self._apply_transformer_func,
                                        func_list=func_list),
                                _x)
        p.close()
        '''
        
        _x = transformed_x
        col_len = len(_x[0].columns)
        self._output_data_dim = (None, col_len*len(self.feature_col_index))
        _x = [_x[i].values for i in range(len(_x))]

        # Regular flattening of 3D data to 2D data for consumption of IID models
        _x = [list(_x[i].flatten()) for i in range(len(_x))]
        _x = np.array(_x)
        if self.pred_win == 1:
            # Single Step Support
            if len(self.target_col_index) > 1:
                _y = _y.reshape(-1, len(self.target_col_index))
            else:
                _y = np.array(_y.ravel()).reshape(-1, 1)
        else:
            # Multi Step Support
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
            else:
                _y = _y.reshape(-1, self.pred_win*len(self.target_col_index))        
        return _x, _y

class SummaryStatistics(TimeTensorTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing 
    using SS(Summary Statistics) Transformer
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
            where n_samples is the number of samples and n_features is the number of features.
        feature_col_index (numpy array): feature indices
        target_col_index (numpy array): target indices
        lookback_win (int, optional): Look-back window for the model.
        pred_win (int): Look-ahead window for the model.
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """
    def __init__(self, 
                 feature_col_index, 
                 target_col_index,
                 lookback_win=1, 
                 pred_win=1,
                 n_jobs=cpu_count()-1):

        super(SummaryStatistics,self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )
        if n_jobs < 1:
            n_jobs = 1
        self.n_jobs = n_jobs
        self.lookback_win_min = 3
        self.pred_win_min = 0
        self._input_data_dim = (None, len(feature_col_index))

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        # self._check_flatten_type(self.flatten_type)
        self._check_window_params()
        _x, _y = super(SummaryStatistics, self).transform(X)

        # @TODO: Need to converge this aggregation with rolling_window_feature_extraction
        
        # finding the aggregate of each tensor using different window agg methods
        # like summary statistics
        _x = [pd.DataFrame(np.array(_x[i])) for i in range(len(_x))]
        
        pd_func_list = PD_FUNC_LIST_SS
        transformed_x = Parallel(n_jobs=self.n_jobs)(delayed(self._apply_transformer_func)
                                                (item, pd_func_list=pd_func_list) 
                                                for item in _x)

        '''
        p = Pool(self.n_jobs)
        transformed_x = p.map(partial(self._apply_transformer_func,
                                        pd_func_list=pd_func_list),
                                _x)
        p.close()
        '''
        
        _x = transformed_x
        col_len = len(_x[0].columns)
        self._output_data_dim = (None, col_len*len(self.feature_col_index))
        _x = [_x[i].values for i in range(len(_x))]

        # Regular flattening of 3D data to 2D data for consumption of IID models
        _x = [list(_x[i].flatten()) for i in range(len(_x))]
        _x = np.array(_x)
        if self.pred_win == 1:
            # Single Step Support
            if len(self.target_col_index) > 1:
                _y = _y.reshape(-1, len(self.target_col_index))
            else:
                _y = np.array(_y.ravel()).reshape(-1, 1)
        else:
            # Multi Step Support
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
            else:
                _y = _y.reshape(-1, self.pred_win*len(self.target_col_index))
        return _x, _y

class AdvancedSummaryStatistics(TimeTensorTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing 
    using ASS(Advanced Summary Statistics) Transformer
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
            where n_samples is the number of samples and n_features is the number of features.
        feature_col_index (numpy array): feature indices
        target_col_index (numpy array): target indices
        lookback_win (int, optional): Look-back window for the model.
        pred_win (int): Look-ahead window for the model.
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """
    def __init__(self, 
                 feature_col_index, 
                 target_col_index,
                 lookback_win=1, 
                 pred_win=1,
                 n_jobs=cpu_count()-1):

        super(AdvancedSummaryStatistics,self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )
        if n_jobs < 1:
            n_jobs = 1
        self.n_jobs = n_jobs
        self.lookback_win_min = 3
        self.pred_win_min = 0
        self._input_data_dim = (None, len(feature_col_index))

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        # self._check_flatten_type(self.flatten_type)
        self._check_window_params()
        _x, _y = super(AdvancedSummaryStatistics, self).transform(X)

        # @TODO: Need to converge this aggregation with rolling_window_feature_extraction
        
        # finding the aggregate of each tensor using different window agg methods
        # like summary statistics
        _x = [pd.DataFrame(np.array(_x[i])) for i in range(len(_x))]
        func_list = FUNC_LIST_ASS
        transformed_x = Parallel(n_jobs=self.n_jobs)(delayed(self._apply_transformer_func)
                                                (item, func_list=func_list) 
                                                for item in _x)

        '''
        p = Pool(self.n_jobs)
        transformed_x = p.map(partial(self._apply_transformer_func,
                                        func_list=func_list),
                                _x)
        p.close()
        '''
        
        _x = transformed_x
        col_len = len(_x[0].columns)
        self._output_data_dim = (None, col_len*len(self.feature_col_index))
        _x = [_x[i].values for i in range(len(_x))]

        # Regular flattening of 3D data to 2D data for consumption of IID models
        _x = [list(_x[i].flatten()) for i in range(len(_x))]
        _x = np.array(_x)
        if self.pred_win == 1:
            # Single Step Support
            if len(self.target_col_index) > 1:
                _y = _y.reshape(-1, len(self.target_col_index))
            else:
                _y = np.array(_y.ravel()).reshape(-1, 1)
        else:
            # Multi Step Support
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
            else:
                _y = _y.reshape(-1, self.pred_win*len(self.target_col_index))        
        return _x, _y

class HigherOrderStatistics(TimeTensorTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing 
    using HOS(Higher Order Statistics) Transformer
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
            where n_samples is the number of samples and n_features is the number of features.
        feature_col_index (numpy array): feature indices
        target_col_index (numpy array): target indices
        lookback_win (int, optional): Look-back window for the model.
        pred_win (int): Look-ahead window for the model.
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """
    def __init__(self, 
                 feature_col_index, 
                 target_col_index,
                 lookback_win=1, 
                 pred_win=1,
                 n_jobs=cpu_count()-1):

        super(HigherOrderStatistics,self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )
        if n_jobs < 1:
            n_jobs = 1
        self.n_jobs = n_jobs
        self.lookback_win_min = 3
        self.pred_win_min = 0
        self._input_data_dim = (None, len(feature_col_index))

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        # self._check_flatten_type(self.flatten_type)
        self._check_window_params()
        _x, _y = super(HigherOrderStatistics, self).transform(X)

        # @TODO: Need to converge this aggregation with rolling_window_feature_extraction
        
        # finding the aggregate of each tensor using different window agg methods
        # like summary statistics
        _x = [pd.DataFrame(np.array(_x[i])) for i in range(len(_x))]
        
        func_list = FUNC_LIST_HOF
        pd_func_list = PD_FUNC_LIST_HOF
        transformed_x = Parallel(n_jobs=self.n_jobs)(delayed(self._apply_transformer_func)
                                                (item, func_list=func_list, pd_func_list=pd_func_list) 
                                                for item in _x)

        '''
        p = Pool(self.n_jobs)        
        transformed_x = p.map(partial(self._apply_transformer_func,
                                        func_list=func_list,
                                        pd_func_list=pd_func_list),
                                _x)
        p.close()
        '''

        _x = transformed_x
        col_len = len(_x[0].columns)
        self._output_data_dim = (None, col_len*len(self.feature_col_index))
        _x = [_x[i].values for i in range(len(_x))]

        # Regular flattening of 3D data to 2D data for consumption of IID models
        _x = [list(_x[i].flatten()) for i in range(len(_x))]
        _x = np.array(_x)
        if self.pred_win == 1:
            # Single Step Support
            if len(self.target_col_index) > 1:
                _y = _y.reshape(-1, len(self.target_col_index))
            else:
                _y = np.array(_y.ravel()).reshape(-1, 1)
        else:
            # Multi Step Support
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
            else:
                _y = _y.reshape(-1, self.pred_win*len(self.target_col_index))
        return _x, _y

class TimeSeriesFeatureUnion(TimeTensorTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing
    using TimeSeriesFeatureUnion Transformer. (includes Summary Statistics, Advanced Summary Statistics,
    Higher Order Statistics, Wavelet and FFT featuers)
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
            where n_samples is the number of samples and n_features is the number of features.
        feature_col_index (numpy array): feature indices
        target_col_index (numpy array): target indices
        lookback_win (int, optional): Look-back window for the model.
        pred_win (int): Look-ahead window for the model.
    """
    def __init__(self, 
                 feature_col_index, 
                 target_col_index,
                 lookback_win=1, 
                 pred_win=1,
                 n_jobs=cpu_count()-1):

        super(TimeSeriesFeatureUnion,self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )
        if n_jobs < 1:
            n_jobs = 1
        self.n_jobs = n_jobs
        self.lookback_win_min = 3
        self.pred_win_min = 0
        self._input_data_dim = (None, len(feature_col_index))

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        # self._check_flatten_type(self.flatten_type)
        self._check_window_params()
        _x, _y = super(TimeSeriesFeatureUnion, self).transform(X)

        # TO DO: Need to converge this aggregation with rolling_window_feature_extraction
        
        # finding the aggregate of each tensor using different window agg methods
        # like summary statistics
        _x = [pd.DataFrame(np.array(_x[i])) for i in range(len(_x))]

        func_list = FUNC_LIST_UNION
        pd_func_list = PD_FUNC_LIST_UNION
        transformed_x = Parallel(n_jobs=self.n_jobs)(delayed(self._apply_transformer_func)
                                                (item, func_list=func_list, pd_func_list=pd_func_list) 
                                                for item in _x)

        '''
        p = Pool(self.n_jobs)
        transformed_x = p.map(partial(self._apply_transformer_func,
                                        func_list=func_list,
                                        pd_func_list=pd_func_list),
                                _x)
        p.close()
        '''
        
        _x = transformed_x
        col_len = len(_x[0].columns)
        self._output_data_dim = (None, col_len*len(self.feature_col_index))
        _x = [_x[i].values for i in range(len(_x))]

        # Regular flattening of 3D data to 2D data for consumption of IID models
        _x = [list(_x[i].flatten()) for i in range(len(_x))]
        _x = np.array(_x)
        if self.pred_win == 1:
            # Single Step Support
            if len(self.target_col_index) > 1:
                _y = _y.reshape(-1, len(self.target_col_index))
            else:
                _y = np.array(_y.ravel()).reshape(-1, 1)
        else:
            # Multi Step Support
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
            else:
                _y = _y.reshape(-1, self.pred_win*len(self.target_col_index))
        return _x, _y

class customTimeSeriesFeatures(TimeTensorTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing
    using TimeSeriesFeatureUnion Transformer. (includes Summary Statistics, Advanced Summary Statistics,
    Higher Order Statistics, Wavelet and FFT featuers)
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
            where n_samples is the number of samples and n_features is the number of features.
        feature_col_index (numpy array): feature indices
        target_col_index (numpy array): target indices
        lookback_win (int, optional): Look-back window for the model.
        pred_win (int): Look-ahead window for the model.
        func_list (list): name of features
        pd_func_list (list): name of features based on pandas
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """
    def __init__(self, 
                 feature_col_index, 
                 target_col_index,
                 func_list,
                 pd_func_list,
                 lookback_win=1, 
                 pred_win=1,
                 n_jobs=cpu_count()-1):

        super(customTimeSeriesFeatures,self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )
        if n_jobs < 1:
            n_jobs = 1
        self.n_jobs = n_jobs
        self.lookback_win_min = 3
        self.pred_win_min = 0
        self._input_data_dim = (None, len(feature_col_index))
        self.func_list = func_list
        self.pd_func_list = pd_func_list

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        # self._check_flatten_type(self.flatten_type)
        self._check_window_params()
        _x, _y = super(customTimeSeriesFeatures, self).transform(X)

        # TO DO: Need to converge this aggregation with rolling_window_feature_extraction
        
        # finding the aggregate of each tensor using different window agg methods
        # like summary statistics
        _x = [pd.DataFrame(np.array(_x[i])) for i in range(len(_x))]
        
        func_list = self.func_list
        pd_func_list = self.pd_func_list
        transformed_x = Parallel(n_jobs=self.n_jobs)(delayed(self._apply_transformer_func)
                                                (item, func_list=func_list, pd_func_list=pd_func_list) 
                                                for item in _x)

        '''
        p = Pool(self.n_jobs)        
        transformed_x = p.map(partial(self._apply_transformer_func,
                                        func_list=func_list,
                                        pd_func_list=pd_func_list),
                                _x)
        p.close()
        '''
        
        _x = transformed_x
        col_len = len(_x[0].columns)
        self._output_data_dim = (None, col_len*len(self.feature_col_index))
        _x = [_x[i].values for i in range(len(_x))]

        # Regular flattening of 3D data to 2D data for consumption of IID models
        _x = [list(_x[i].flatten()) for i in range(len(_x))]
        _x = np.array(_x)
        if self.pred_win == 1:
            # Single Step Support
            if len(self.target_col_index) > 1:
                _y = _y.reshape(-1, len(self.target_col_index))
            else:
                _y = np.array(_y.ravel()).reshape(-1, 1)
        else:
            # Multi Step Support
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
            else:
                _y = _y.reshape(-1, self.pred_win*len(self.target_col_index))
        
        return _x, _y

class RandomTimeTensorTransformer(TimeTensorTransformer):
    """
    Prepare Randomized data to be consumed by the model either for training.
    Random Samples are ordered w.r.t. input data
    
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
            where n_samples is the number of samples and n_features is the \
            number of features.
        num_look_back (int, optional): Look-back window for the model.
        n_steps_ahead (int): Look-ahead window for the model.
        n_intervals (string or float or int): number of intervals to be generated, \
            default : 'sqrt' of total samples, 
            other values: positive number, 
                        log of total samples, 
                        float with <= 1.0 and >= 0 
        random_state (None or int): setting seed of randomness
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """
    def __init__(self, 
                 feature_col_index, 
                 target_col_index,
                 lookback_win=1, 
                 pred_win=1,
                 n_intervals='sqrt', 
                 random_state=None
                 ):
        super(RandomTimeTensorTransformer,self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )

        self.n_intervals = n_intervals
        self.random_state = random_state
    
    def predict_transform(self, X, y=None):
        '''
        '''
        return super(RandomTimeTensorTransformer,self).transform(X,y)
    
    def transform(self, X, y=None):
        self._check_meta_data(X.shape)
        if isinstance(X, pd.DataFrame):
            X = X.values

        X = check_array(X, accept_sparse=True)

        check_is_fitted(self, 'n_features_')
        if X.shape[1] != self.n_features_:
            raise ValueError(Messages.get_message(message_id='AUTOAITSLIBS0032E'))

        len_series = X.shape[0]
        _x, _y = [], []
        if self.lookback_win > 0:
            if self.n_intervals == 'sqrt':
                n_intervals = int(np.sqrt(len_series))
            elif self.n_intervals == 'log':
                n_intervals = int(np.log(len_series))
            elif np.issubdtype(type(self.n_intervals), np.floating) and \
                (self.n_intervals > 0) and (self.n_intervals <= 1):
                n_intervals = int(len_series * self.n_intervals)
            else:
                raise ValueError(Messages.get_message(format(self.n_intervals), message_id='AUTOAITSLIBS0034E'))
            n_intervals = np.maximum(1, n_intervals)
            
            _rng = check_random_state(self.random_state)
            ind_value = _rng.randint(self.lookback_win, 
                                     len_series - self.pred_win + 1, 
                                     size=n_intervals)
            ind_value.sort()
            
            for i in ind_value:
                _x.append(X[i - self.lookback_win:i, self.feature_col_index])
                #_y.append(X[i + self.pred_win-1, self.target_col_index])
                if self.pred_win > 1:
                    _y.append(X[i:i + self.pred_win, self.target_col_index])
                else:
                    _y.append(X[i + self.pred_win-1, self.target_col_index])
            _x, _y = np.array(_x), np.array(_y)
        else:
            raise Exception(Messages.get_message(format(self.lookback_win), message_id='AUTOAITSLIBS0033E'))

        return _x, _y

class RandomTimeSeriesFeatures(RandomTimeTensorTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing
    using RandomTimeSeriesFeatures Transformer.
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
            where n_samples is the number of samples and n_features is the number of features.
        feature_col_index (numpy array): feature indices
        target_col_index (numpy array): target indices
        lookback_win (int, optional): Look-back window for the model.
        pred_win (int): Look-ahead window for the model.
        n_intervals (string or float or int): number of intervals to be generated, \
            default : 'sqrt' of total samples, 
            other values: positive number, 
                        log of total samples, 
                        float with <= 1.0 and >= 0 
        random_state (None or int): setting seed of randomness
        n_random_features (int): number of time series features to be selected
        baseline_feature (string: default 'identity'): features to be used as a baseline
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """
    def __init__(self, 
                 feature_col_index, 
                 target_col_index,
                 lookback_win=1, 
                 pred_win=1,
                 n_intervals='sqrt',
                 random_state=None,
                 n_random_features=3,
                 baseline_feature='identity',
                 n_jobs=cpu_count()-1):

        super(RandomTimeSeriesFeatures,self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win,
            n_intervals=n_intervals, 
            random_state=random_state
        )
        if n_jobs < 1:
            n_jobs = 1
        self.n_jobs = n_jobs
        self.lookback_win_min = 3
        self.pred_win_min = 0
        self._input_data_dim = (None, len(feature_col_index))
        self.n_random_features = n_random_features
        self.baseline_feature = baseline_feature
        
        # function lists
        self.func_list = None
        self.pd_func_list = None
        
    def _init_features_bundle(self):
        if not self.func_list and not self.pd_func_list:
            from autoai_ts_libs.srom.transformers.feature_engineering.timeseries.function_map import get_random_featureset
            self.pd_func_list, self.func_list = get_random_featureset(self.n_random_features)
            if self.baseline_feature:
                if self.func_list: 
                    if self.baseline_feature not in self.func_list: 
                        self.func_list.append(self.baseline_feature)
                else:
                    self.func_list = [self.baseline_feature]
        
    def fit(self, X, y=None):
        self._check_meta_data(X.shape)
        X = check_array(X, accept_sparse=True)
        self.n_features_ = X.shape[1]
        
        # call function to fix the features to be extracted
        self._init_features_bundle()
        
        return self

    def _transform(self, X, y=None, mode='train'):
        # calling the function to first create time tensors
        # self._check_flatten_type(self.flatten_type)
        self._check_window_params()
        if mode == 'train':
            _x, _y = super(RandomTimeSeriesFeatures, self).transform(X)
        elif mode == 'predict':
            _x, _y = super(RandomTimeSeriesFeatures, self).predict_transform(X)
        else:
            Exception('Not Supported...')

        # TO DO: Need to converge this aggregation with rolling_window_feature_extraction
        
        # finding the aggregate of each tensor using different window agg methods
        # like summary statistics
        _x = [pd.DataFrame(np.array(_x[i])) for i in range(len(_x))]
        
        func_list = self.func_list
        pd_func_list = self.pd_func_list
        transformed_x = Parallel(n_jobs=self.n_jobs)(delayed(self._apply_transformer_func)
                                                (item, func_list=func_list, pd_func_list=pd_func_list) 
                                                for item in _x)

        '''
        p = Pool(self.n_jobs)        
        transformed_x = p.map(partial(self._apply_transformer_func,
                                        func_list=func_list,
                                        pd_func_list=pd_func_list),
                                _x)
        p.close()
        '''
        
        _x = transformed_x
        col_len = len(_x[0].columns)
        self._output_data_dim = (None, col_len*len(self.feature_col_index))
        _x = [_x[i].values for i in range(len(_x))]

        # Regular flattening of 3D data to 2D data for consumption of IID models
        _x = [list(_x[i].flatten()) for i in range(len(_x))]
        _x = np.array(_x)
        if self.pred_win == 1:
            # Single Step Support
            if len(self.target_col_index) > 1:
                _y = _y.reshape(-1, len(self.target_col_index))
            else:
                _y = np.array(_y.ravel()).reshape(-1, 1)
        else:
            # Multi Step Support
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
            else:
                _y = _y.reshape(-1, self.pred_win*len(self.target_col_index))
        
        return _x, _y

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        # self._check_flatten_type(self.flatten_type)
        return self._transform(X, y, 'train')

    def predict_transform(self, X, y=None):
        # calling the function to first create time tensors
        # this will make sure that tensor is not dropped
        # self._check_flatten_type(self.flatten_type)
        return self._transform(X, y, 'predict')

class NormalizedFlatten(TimeTensorTransformer, TargetTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing.
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
        where n_samples is the number of samples and n_features is the number of features.
        num_look_back (int, optional): Look-back window for the model.
        n_steps_ahead (int): Look-ahead window for the model.
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """

    def __init__(self,
                 feature_col_index,
                 target_col_index,
                 lookback_win=1,
                 pred_win=1):

        super(NormalizedFlatten, self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )

        def _check_col_index():
            for i in range(len(self.feature_col_index)):
                if self.feature_col_index[i] != self.target_col_index[i]:
                    return True
            return False

        if len(feature_col_index) != len(target_col_index) or \
            set(feature_col_index) != set(target_col_index) or \
            _check_col_index():
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0035E'))

        self._input_data_dim = (None, len(feature_col_index))
        self._output_data_dim = (None, lookback_win*len(feature_col_index))

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        _x, _y = super(NormalizedFlatten, self).transform(X)

        # Regular flattening of 3D data to 2D data for consumption of IID models
        _x = [list(_x[i][:,j].flatten()) for i in range(len(_x)) for j in range(len(self.feature_col_index))]
        _x = np.array(_x)

        self._x_mean = _x.mean(axis=1).reshape(-1,1)
        self._x_std = _x.std(axis=1).reshape(-1,1)
        self._x_std[self._x_std==0] = 1.0
        _x = (_x - self._x_mean)/self._x_std

        if self.pred_win == 1:
            _y = np.array(_y.ravel()).reshape(-1, 1)
            _y = (_y - self._x_mean)/self._x_std
        else:
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
                _y = (_y - self._x_mean)/self._x_std
            else:
                _y = [list(_y[i][:,j].flatten()) for i in range(len(_y)) for j 
                      in range(len(self.target_col_index))]
                _y = np.array(_y)
                _y = (_y - self._x_mean)/self._x_std

        return _x, _y

    def inverse_transform(self, y):
        # make sure we have correct shape of y
        if self.pred_win == 1:
            y = y.reshape(-1,1)
        else:
            y = y.reshape(-1, self.pred_win)
        return (y * self._x_std) + self._x_mean    

class DifferenceFlatten(TimeTensorTransformer, TargetTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing.
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
        where n_samples is the number of samples and n_features is the number of features.
        num_look_back (int, optional): Look-back window for the model.
        n_steps_ahead (int): Look-ahead window for the model.
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """

    def __init__(self,
                 feature_col_index,
                 target_col_index,
                 lookback_win=1,
                 pred_win=1):

        super(DifferenceFlatten, self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )

        def _check_col_index():
            for i in range(len(self.feature_col_index)):
                if self.feature_col_index[i] != self.target_col_index[i]:
                    return True
            return False

        if len(feature_col_index) != len(target_col_index) or \
            set(feature_col_index) != set(target_col_index) or \
            _check_col_index():
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0035E'))

        self._input_data_dim = (None, len(feature_col_index))
        self._output_data_dim = (None, lookback_win*len(feature_col_index))

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        _x, _y = super(DifferenceFlatten, self).transform(X)

        # Regular flattening of 3D data to 2D data for consumption of IID models
        self._x_last = np.array([list(_x[i][:,j])[-1] for i in range(len(_x)) 
                                 for j in range(len(self.feature_col_index))]).reshape(-1,1)
        _x = [list(np.diff(_x[i][:,j])) for i in range(len(_x)) for j in range(len(self.feature_col_index))]
        _x = np.array(_x)

        if self.pred_win == 1:
            _y = np.array(_y.ravel()).reshape(-1, 1)
            _y = (_y - self._x_last)
        else:
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
                _y = _y - self._x_last
            else:
                _y = [list(_y[i][:,j].flatten()) for i in range(len(_y)) for j 
                      in range(len(self.target_col_index))]
                _y = np.array(_y)
                _y = _y - self._x_last

        return _x, _y

    def inverse_transform(self, y):
        if self.pred_win == 1:
            y = y.reshape(-1,1)
        else:
            y = y.reshape(-1, self.pred_win)
        return (y + self._x_last)

class DifferenceNormalizedFlatten(DifferenceFlatten):
    """
    Prepare the data to be consumed by the model either for training or testing.
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
        where n_samples is the number of samples and n_features is the number of features.
        num_look_back (int, optional): Look-back window for the model.
        n_steps_ahead (int): Look-ahead window for the model.
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """

    def __init__(self,
                 feature_col_index,
                 target_col_index,
                 lookback_win=1,
                 pred_win=1):

        super(DifferenceNormalizedFlatten, self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        _x, _y = super(DifferenceNormalizedFlatten, self).transform(X)

        self._x_mean = _x.mean(axis=1).reshape(-1,1)
        self._x_std = _x.std(axis=1).reshape(-1,1)
        self._x_std[self._x_std==0] = 1.0
        _x = (_x - self._x_mean)/self._x_std
        _y = (_y - self._x_mean)/self._x_std

        return _x, _y

    def inverse_transform(self, y):
        if self.pred_win == 1:
            y = y.reshape(-1,1)
        else:
            y = y.reshape(-1, self.pred_win)
        return super(DifferenceNormalizedFlatten, self).\
            inverse_transform((y * self._x_std) + self._x_mean)

class LocalizedFlatten(TimeTensorTransformer, TargetTransformer):
    """
    Prepare the data to be consumed by the model either for training or testing.
    Parameters:
        X (pandas dataframe or numpy array, required): shape = [n_samples, n_features] \
        where n_samples is the number of samples and n_features is the number of features.
        num_look_back (int, optional): Look-back window for the model.
        n_steps_ahead (int): Look-ahead window for the model.
    Returns:
        _x (list of list): Each index in the list has a list of lookback window elements.
        _y (list of list): Each index in the list has a list of look ahead window elements.
    """

    def __init__(self,
                 feature_col_index,
                 target_col_index,
                 lookback_win=1,
                 pred_win=1):

        super(LocalizedFlatten, self).__init__(
            feature_col_index = feature_col_index,
            target_col_index = target_col_index,
            lookback_win = lookback_win,
            pred_win = pred_win
        )

        def _check_col_index():
            for i in range(len(self.feature_col_index)):
                if self.feature_col_index[i] != self.target_col_index[i]:
                    return True
            return False

        if len(feature_col_index) != len(target_col_index) or \
            set(feature_col_index) != set(target_col_index) or \
            _check_col_index():
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0035E'))

        self._input_data_dim = (None, len(feature_col_index))
        self._output_data_dim = (None, lookback_win*len(feature_col_index))

    def transform(self, X, y=None):
        # calling the function to first create time tensors
        _x, _y = super(LocalizedFlatten, self).transform(X)

        # Regular flattening of 3D data to 2D data for consumption of IID models
        _x = [list(_x[i][:,j].flatten()) for i in range(len(_x)) for j in range(len(self.feature_col_index))]
        _x = np.array(_x)

        if self.pred_win == 1:
            _y = np.array(_y.ravel()).reshape(-1,1)
        else:
            if len(self.target_col_index) == 1:
                _y = _y.reshape(-1, self.pred_win)
            else:
                _y = [list(_y[i][:,j].flatten()) for i in range(len(_y)) for j 
                      in range(len(self.target_col_index))]
                _y = np.array(_y)

        return _x, _y
    
    def inverse_transform(self, y):
        # make sure we have correct shape of y
        if self.pred_win == 1:
            y = y.reshape(-1,1)
        else:
            y = y.reshape(-1, self.pred_win)
        return y