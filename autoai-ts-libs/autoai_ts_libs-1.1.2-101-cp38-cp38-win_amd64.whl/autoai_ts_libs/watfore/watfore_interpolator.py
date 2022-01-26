# ************* Begin Copyright - Do not add comments here **************
#   Licensed Materials - Property of IBM
#
#   (C) Copyright IBM Corp. 2019, 2020, All Rights Reserved
#
# The source code for this program is not published or other-
# wise divested of its trade secrets, irrespective of what has
# been deposited with the U.S. Copyright Office.
# **************************** End Copyright ***************************

"""
@author: Syed Yousaf Shah (syshah@us.ibm.com)

This is a wrapper for watfore to access functionalities in autoai api
"""
import logging

import pandas as pd
import numpy as np
# from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin
# from autoai_api.autoai import AutoAIEstimator,AutoAITransformer
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.utils.validation import check_array

#from ai4ml_ts.utils.messages.messages import Messages
from autoai_ts_libs.utils.messages.messages import Messages
logger = logging.getLogger(__name__)
logger.setLevel('WARNING')

try:
    #from tspy import TSContext
    # import tspy
    import autoai_ts_libs.deps.tspy as tspy
    from autoai_ts_libs.deps.tspy.functions import interpolators as tspy_interpolators

except Exception as e:
    logger.warning ("Exception importing tspy")
    logger.warning (e)


class WatForeInterpolator(TransformerMixin, BaseEstimator):

    """ Forecaster using WatFore library. This class is custom transformer providing interface to interpolators in watfore
    library.

      Parameters
      ----------
      interpolator_type : str, default='nearest',
        For ease of use algorithm can be chosen from watfore.Interpolators.*
        Interpoloator that is used to applied to fill missing values.Currently available(and growing) transforms are,
        linear, params:none, linear interpolation over past values
        cubic, params:none
        prev, params: default_value , Uses previous value to interpolate and uses default_value if it doesn't exist.
        next, params:default_value, Uses next value to interpolate and and uses default_value if it doesn't exist.
        nearest, params: none
        fill, params: default_value, interpolates with default_value

        nearest - interpolate the given timestamp,value so the value is that of the nearest timestamp
        next - interpolate the given timestamp,value so the value is that of the next timestamp
        prev - interpolate the given timestamp,value so the value is that of the previous timestamp

      default_value: float, default = 0
      This is the default value that will be used by interpolator in cases where it is needed, e.g., in case of fill
      interpolator it is filled with default_value.

    append_tranform: bool, default=True.
        When set to True applies transformation on the last column and appends all
        original columns to the right of the transformed column. So output will have columns in order,
        input:
        timestamp, col_a
        output
        timestamp, transformed_col_a, col_a
        input:
        timestamp, col_a, col_b
        output
        timestamp, transformed_col_b, col_a, col_b

        If append_tranform is set to False, on transformed column along with timestamp will be returned and original columns
        will be dropped.
        input:
        timestamp, col_a
        output
        timestamp, transformed_col_a

    ts_icol_loc : array [int], default= -1
        This parameter tells the forecasting modeling the absolute location of the timestamp column. For specifying
        time stamp location put value in array e.g., [0] if 0th column is time stamp. The array is to support
        multiple timestamps in future. If ts_icol_loc = -1 that means no timestamp is provided and all data is
        time series. With ts_icol_loc=-1, the model will assume all the data is ordered and equally sampled.

    ts_ocol_loc: int, default = -1
        This parameter tells the interpolator the absolute location of the timestamp column location in the output of the
        interpolator, if set to -1 then timestamp will not be includeded otherwise it will be included on specified column
        number. if ts_ocol_loc is specified outside range i.e., < 0 or > 'total number of columns' then timestamp is
        appended at 0 i.e., the first column in the output of the interpolator.

      """
    # try:
    #     import os
    #     os.environ['TMP_DIR'] = '../libs/tmp'
    #     os.environ['TS_HOME'] = "../libs/time-series-assembly-1.0.0-jar-with-dependencies.jar"
    # except Exception as e:
    #     logger.error(e)

    def __init__(self, interpolator_type ='nearest',append_tranform=False, ts_icol_loc=-1,ts_ocol_loc=-1
                 ,debug = False,missing_val_identifier= np.nan, default_value = 0.0,**kwargs):

        #_set_env(self) #assuming they are set.
        # This will be not be needed once new version of tspy is release
        # try:
        #      import os
        #      os.environ['TS_HOME'] = os.path.abspath(os.path.join(os.path.join(os.path.join(os.path.dirname(__file__)
        #                                                                                     , '../utils'),
        #                                                                        'watfore_javalibs'),
        #                                                           'time-series-assembly-1.0.0-jar-with-dependencies.jar'))
        # except Exception as e:
        #      logger.warning('Unable to set TS_HOME ENV')
        #      logger.error(e)


        self.interpolator_type = interpolator_type
        #self.wfts_context = None #wfts_context #context if already open.
        self.append_tranform = append_tranform
        self.debug = False
        self.ts_icol_loc = ts_icol_loc
        self.ts_ocol_loc = ts_ocol_loc
        self.missing_val_identifier = np.nan
        self.input_missing_val_identifier = missing_val_identifier
        self.tspy_interpolators = tspy_interpolators
        self.debug = debug

        if 'imputer_fill_type' in kwargs.keys() and self.interpolator_type=='fill':
            self.imputer_fill_type=kwargs['imputer_fill_type']
            if self.imputer_fill_type not in ['mean','median','value']:
                raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0062E'))
            elif self.imputer_fill_type == 'value':
                if 'imputer_fill_value' in kwargs.keys():
                    self.imputer_fill_value=kwargs['imputer_fill_value']
                    if not isinstance(self.imputer_fill_value, (int, float)):
                        raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0066E'))
                elif 'imputer_fill_value' not in kwargs.keys():
                    self.imputer_fill_value = 0.0
        elif ('imputer_fill_type' in kwargs.keys() or 'imputer_fill_value' in kwargs.keys() ) and self.interpolator_type!='fill':
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0064E'))
        else:
            self.imputer_fill_type='value'
            self.imputer_fill_value=0.0

        self.default_value = default_value
        if self.default_value == None or self.default_value in [self.input_missing_val_identifier]:
            self.default_value = 0.0

        self.all_args = kwargs
        self.all_args['interpolator_type'] = self.interpolator_type
        self.all_args['append_transform'] = self.append_tranform
        #self.all_args['algorithm'] = self.algorithm
        self._timeseries = None
        self._timestamps = None

        #print('Interpolator called with ', self.all_args)
        if self.debug:
            logger.debug('Interpolator called with ', self.all_args)



    @classmethod
    def get_param_dist(cls, size=None):

        param_dist = {}
        param_dist['interpolator_type'] = ['linear', 'cubic', 'prev', 'next', 'nearest', 'fill']


        return param_dist

    @classmethod
    def get_param_ranges(cls):

        param_ranges = {}
        param_categorical_indices = {}

        param_ranges['transform_name'] = ['linear', 'cubic', 'prev', 'next', 'nearest', 'fill']
        param_categorical_indices['transform_name'] = (int(0), int(5), int(0))

        return param_ranges, param_categorical_indices


    def get_model_params(self):

       return  self.all_args


    """
    Returns model for respective algorithm. 
    """
    def _getTransform(self,kwargs):
        #print(kwargs)

        interpolator_type = kwargs['interpolator_type']
        #alg_args = {}
        #required params
        #alg_params = ['default_value']
        interp = None
        if interpolator_type.lower() == 'linear':
            interp = self.tspy_interpolators.linear()
        if interpolator_type.lower() == 'cubic':
            interp = self.tspy_interpolators.cubic(fill_value=float(self.default_value))
        if interpolator_type.lower()== 'nearest':
            interp = self.tspy_interpolators.nearest()
        if interpolator_type.lower() == 'next':
            #if 'default_value' not in kwargs:
             #   logger.warning("Default Value missing for next interpolator!!!,setting to 0")
              #  kwargs['default_value'] = float(0)
            interp = self.tspy_interpolators.next(default_value=self.default_value)

        if interpolator_type.lower() == 'prev':
            #print ('prev')
            #if 'default_value' not in kwargs:
                #logger.warning("Default Value missing for prev interpolator!!!,setting to 0")
                #kwargs['default_value'] = float(0)
            interp = self.tspy_interpolators.prev(default_value=self.default_value)
        if interpolator_type.lower() == 'fill':
            #if 'default_value' not in kwargs:
             #   logger.warning("Default Value missing for fill interpolator!!!,setting to 0")
              #  kwargs['default_value'] = float(0)
            #if kwargs['default_value'] == np.nan:
            #kwargs['default_value'] = float(0)
            interp = self.tspy_interpolators.fill(self.imputer_fill_value)

        return interp #



    def fit(self, X, y=None):

        """Nothing in fit as interpolator needs to work on whatever ts it gets in transforms

        Returns
        -------
        self : object
            Returns self.
        """

        #X = check_array(X, accept_sparse=True,force_all_finite=False)

        #print (X[:, 1:]) #vals
        #print(X[:, :1])  # Ts
        #print (X.shape[0])
        #self._timestamps =X[:, :1].flatten() #[X.flatten().tolist()]
        #self.n_features_ = X.shape[0];

        return self

    def __getstate__(self):
        #print('Getstate=====================Interpolator')
        state = self.__dict__.copy()
        state["_timeseries"] = None
        state["model"] = None
        state["tspy_interpolators"] = None
        # print('After copy')
        #state['model'] = None
        #print(state['tspy_interpolators'])
        #state['tspy_interpolators'] = None
        #print(state['tspy_interpolators'])
        # #print()
        #return self
        return state

    def __setstate__(self, state):
         #print('SetState=====================Interpolator')
         self.__dict__.update(state)
         self.tspy_interpolators = tspy_interpolators


    def transform(self, X):
        """ A reference implementation of a transform function.
        Parameters
        ----------
        X : {array-like, sparse-matrix}, shape (n_samples, n_features)
            The input samples.
        Returns
        -------
        X_transformed : array, shape (n_samples, n_features)
            The array containing the element-wise square roots of the values
            in ``X``.
        """

        # try:
        #     self.wfts_context = tspy#TSContext(die_on_exit=False)#TSContext()
        # except Exception as e:
        #     print(e)
        #     logger.exception(e)
        #     raise e
        if X is None: # This is case where we have predict(None)
            return X
        #self.model = self._getTransform(self.all_args)

        # Input validation
        X = check_array(X, accept_sparse=True,force_all_finite=False) # because X can contain NaN
        # Check that the input is of the same shape as the one passed
        #print('-----------')
        if self.debug:
            print(str(self.__class__) +' transform \n X=='+str(X))
            logger.debug(str(self.__class__) +' transform \n X=='+str(X))

        # Replace missing self.missing_val_identifier by np.nan
        #X[X == self.input_missing_val_identifier] = self.missing_val_identifier # doesn't work for now
        X = np.where(X == self.input_missing_val_identifier, self.missing_val_identifier, X)
        #print('After Replacement', X)
        if not (np.any(X == self.input_missing_val_identifier) or np.isnan(X).any()):#not :
            #print('Nan or ', self.missing_val_identifier,np.isnan(X).any() , 'Doesnot exist=============================')
            return X

        self._timestamps = []
        ts_col = -1

        #############################
        #ts = X[:, :1].flatten()
        #self._timestamps =[]
        #for t in ts:
        #    self._timestamps.append(int(t))
             #[X.flatten().tolist()]
        ########################
        #if (self.ts_icol_loc < 0):
        #    raise AssertionError('Missing time stamp or specify absolute location of time stamp')
            #autogenerate ts
            #len_ts= X.shape[0]
            #for t in range(0,len_ts):
            #    self._timestamps.append(int(t))
        #else:
        #print(self.ts_icol_loc)
        if (self.ts_icol_loc == -1):
            #autogenerate ts
            len_ts= X.shape[0]
            for t in range(0,len_ts):
                self._timestamps.append(int(t))
        else:
            ts_col = self.ts_icol_loc[0] # Assuming for now only one timestamp

            if ts_col < 0 or ts_col >= X.shape[1]:
                # not needed in new tspy Jan2020
                #self.stop_context()
                raise AssertionError(Messages.get_message(str(ts_col), message_id='AUTOAITS0029E'))
                #print(X[:,ts_col])
            ts = X[:,ts_col] #X[:, :ts_col+1].flatten()
            for t in ts:
                self._timestamps.append(int(t))


        self.n_features_ = X.shape[1]#X.shape[0]
        #print(ts_col)
        all_passthrough_cols = None
        all_transformed_cols = None
        if self.append_tranform:
            all_passthrough_cols = pd.DataFrame(X)
            if ts_col != -1:
                # print(ts_col)
                # Remove ts col, ts_ocol_loc is used to specify location of ts in output
                all_passthrough_cols.drop(columns=[ts_col], inplace=True)

        #vals_df_array = []
        append_ind = 0
        if self.append_tranform:
            total_df_cols = all_passthrough_cols.shape[1]
        for val_ind in range(0, self.n_features_):
            if val_ind != ts_col:
                data_dic = {'timestamp': self._timestamps, 'value': X[:, val_ind]}
                #print (data_dic)
                dataframe = pd.DataFrame(data_dic, columns=['timestamp', 'value'])
                dataframe = dataframe.astype(dtype={"timestamp": "int64", "value": "float64"})

                if self.all_args['interpolator_type']=='fill':
                    if self.imputer_fill_type=='mean':
                        self.imputer_fill_value=np.nanmean(X[:, val_ind])
                    elif self.imputer_fill_type=='median':
                        self.imputer_fill_value=np.nanmedian(X[:, val_ind])
                self.model = self._getTransform(self.all_args)
               # vals_df_array.append(dataframe)
                #print(data_dic['value'])
                #TODO: renable this once tspy is fixed
                #self._timeseries = tspy.time_series(dataframe, ts_column="timestamp", value_column="value")
                self._timeseries = tspy.time_series(list(dataframe['value'])) #fix for tspy 2.0.x error
                #print('Time series',self._timeseries)
                #print(self.model)
                trans_x = self._timeseries.fillna(self.model, self.missing_val_identifier).to_df()
                #trans_x = self._timeseries.fillna(tspy_interpolators.cubic(fill_value=0.0),np.nan).to_df()
                #print('Trans X',trans_x)

                if (all_transformed_cols is None and self.append_tranform == False):
                        all_transformed_cols = pd.DataFrame()
                        all_transformed_cols.insert(append_ind, 'tran_' + str(val_ind),
                                                    trans_x['value'].ravel())
                        append_ind += 1
                else:

                    if self.append_tranform:
                        all_passthrough_cols.insert(total_df_cols + append_ind,
                                                    'tran_' + str(val_ind), trans_x['value'].ravel())
                    else:

                        all_transformed_cols.insert(append_ind, 'tran_' + str(val_ind), trans_x['value'].ravel())
                    append_ind += 1


        if self.append_tranform:
            #print(all_passthrough_cols.shape[1])
            #trans_x.insert(1, 'original_value', X)
            #all_passthrough_cols.insert(1, 'transformation', trans_x['value'].ravel())  # insert after time stamp column

            # not needed in new tspy Jan2020
            #self.stop_context()

            if (self.ts_ocol_loc == -1):
                return all_passthrough_cols.to_numpy()
            else:
                ts_ocol = self.ts_ocol_loc[0]# Assumes one
                if (ts_ocol < 0) or (ts_ocol > all_passthrough_cols.shape[1]):
                    print('Timestamp output location is outside range ts_ocol_loc='+ str(ts_ocol)) # TODO put it in some warning
                    all_passthrough_cols.insert(0, 'timestamp', self._timestamps)
                    #raise
                else:
                    all_passthrough_cols.insert(ts_ocol, 'timestamp', self._timestamps)
            return all_passthrough_cols.to_numpy()
        else:

            #print(all_transformed_cols.shape[1])
            # not needed in new tspy Jan2020
            #self.stop_context()
            # Here processes the ts_ocol_loc before returning
            if (self.ts_ocol_loc == -1):
                return all_transformed_cols.to_numpy()
            else:
                ts_ocol = self.ts_ocol_loc[0]
                if ts_ocol < 0 or ts_ocol > all_transformed_cols.shape[1]:
                    print('Timestamp output location is outside range ts_ocol_loc='+ str(ts_ocol))
                    all_transformed_cols.insert(0, 'timestamp', self._timestamps)
                    #raise
                else:
                    all_transformed_cols.insert(ts_ocol, 'timestamp', self._timestamps)
        # if self.debug:
        #     logger.debug('Transform Received', X)
        #     logger.debug('Transform type',self.all_args['interpolator_type'])
        #     logger.debug('Transform Returning',all_transformed_cols.to_numpy())
            return all_transformed_cols.to_numpy()#trans_x.to_df()['value'].tolist()

    def set_params(self, **params):
            self.all_args = params
            return self

    # not needed in new tspy Jan2020
    #def stop_context(self):
    #    if None != self.wfts_context:
    #        self.wfts_context.stop()



#if __name__ == "__main__":#

    #main_test()
    #pipeline_test()
