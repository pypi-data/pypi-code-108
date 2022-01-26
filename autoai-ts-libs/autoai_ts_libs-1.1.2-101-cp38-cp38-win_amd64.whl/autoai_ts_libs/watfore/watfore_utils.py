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

Utility functions for WatFore
"""


import logging
import math
from sklearn.model_selection import TimeSeriesSplit,train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)
logger.setLevel('WARNING')

class WatForeUtils():
    # try:
    #     import os
    #     os.environ['TS_HOME'] = "../libs/time-series-assembly-1.0.0-jar-with-dependencies.jar"
    # except Exception as e:
    #     logger.error(e)

    debug = False

    """
      Provides Single split
      """

    @classmethod
    def ts_train_test_split(cls, X, y, ts_icol_loc=-1, test_size=0.2, random_state=None):

        # if (y.any()== None):
        y = X

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False,
                                                            random_state=random_state)

        # print(X_train)
        # print(y_train)
        # print(X_test)
        # print(y_test)

        if ts_icol_loc == -1:
            X_test = [[val] for val in range(len(X_train), (len(X_train) + len(X_test)))]
        else:
            ts_loc = ts_icol_loc[0]
            X_test = np.asarray(X_test)  # May be later test if iterate over list of list
            X_test = [[val] for val in X_test[:, ts_loc]]
            # print(ts_loc)
            # print (y_test)
            y_test = np.delete(y_test, ts_loc, axis=1)

        # print(X_train)
        # print(y_train)
        # print(X_test)
        # print(y_test)

        return X_train, X_test, y_train, y_test

    @classmethod
    def mean_absolute_percentage_error(cls, y_true, y_pred):
        try:
            y_true, y_pred = np.array(y_true), np.array(y_pred)
            return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        except Exception as e:
            logger.debug("== Error in computing mean_absolute_percentage_error")
            return None

    @classmethod
    def adjusted_smape(cls, y_true, y_pred):
        '''
        SMAPE
        '''
        y_true, y_pred = np.array(y_true).ravel(), np.array(y_pred).ravel()
        if len(y_true) != len(y_pred):
            logger.error('adjusted_smape computation error')
            logger.error('Size of Ground Truth and Predicted Values do not match!, returning None.')
            # May be raising error will interfere with daub execution if one pipeline fails
            # raise ValueError('Size of Ground Truth and Predicted Values do not match!')
            return None

        pred_diff = 2.0 * np.abs(y_true - y_pred)
        divide = np.abs(y_true) + np.abs(y_pred)
        divide[divide < 1e-12] = 1.0
        scores = (pred_diff / divide)
        scores = np.array(scores, dtype=np.float)
        return np.nanmean(scores) * 100.0

    @classmethod
    def smape(cls, y_true, y_pred):
        try:
            y_true, y_pred = np.array(y_true).ravel(), np.array(y_pred).ravel()
            return np.mean(np.abs(y_true - y_pred) / (np.abs(y_true) + np.abs(y_pred))) * 2 * 100
        except Exception as e:
            logger.debug("== Error in computing smape")
            return None
        # return np.mean(2.0 * np.abs(y_true - y_pred) / (np.abs(y_true) + np.abs(y_pred)))

    """
    Provides multiple splits
    Requires time stamp even if generated otherwise if ts split gives test point towards end missing in between 
    we get wrong indexing 
    """

    @classmethod
    def ts_train_test_splits(cls, X, y=None, ts_icol_loc=-1, n_splits=2):

        if (y == None):
            y = X

        X_train_ary = []
        y_train_ary = []

        X_test_ary = []
        y_test_ary = []

        tscv = TimeSeriesSplit(n_splits=n_splits)

        for train_index, test_index in tscv.split(X):
            if (cls.debug):
                print("TRAIN:", train_index, "TEST:", test_index.ravel())
                logger.debug("TRAIN:", train_index, "TEST:", test_index.ravel())

            X_train, X_test = X[train_index[0]:(train_index[-1]) + 1], X[test_index[0]:(test_index[
                -1]) + 1]  # +1 to include last value
            y_train, y_test = y[train_index[0]:(train_index[-1]) + 1], y[test_index[0]:(test_index[
                -1]) + 1]  # +1 to include last value

            if ts_icol_loc == -1:
                # X_test_ts = list(range(0, len(X)))
                # X_test = np.append(X_test,X_test_ts,axis=0)
                # print (X_test)
                # print (X_test_ts)
                X_test = [[val] for val in test_index]  # np.insert(X_test,0, X_test_ts)
                y_test_ary.append(y_test)
                # print('--1')
                # print (y_test)
                # exit()
                # print(X_test)
                # ts_icol_loc[0] = 0

            else:
                ts_loc = ts_icol_loc[0]
                X_test = np.asarray(X_test)  # May be later test if iterate over list of list
                X_test = [[val] for val in X_test[:, ts_loc]]  # X_test[:, ts_loc]
                # print(X_test)
                # print(ts_loc)
                # print (y_test)
                y_test = np.delete(y_test, ts_loc, axis=1)
                y_test_ary.append(y_test.tolist())
                # print (y_test)

            X_train_ary.append(X_train)
            y_train_ary.append(y_train)
            X_test_ary.append(X_test)

        return X_train_ary, X_test_ary, y_train_ary, y_test_ary

    # @classmethod# gets runtime from 200sec to 68.40858721733093
    # def get_bats_init_samples(cls, num_data_samples,all_seasson_lens):
    #
    #     #num_data_samples = len(X)
    #     base_samples = 1000 # This base could be dynamic, if only 1 season is found this can be higher
    #     up_base_limit = 2200
    #     MAX_CAP = 300000 # 300K rows
    #     #per,ac_seas = cls.get_regular_season_periodicity(X=X, wf_context=wf_context)
    #     if all_seasson_lens is None:
    #         if num_data_samples <= base_samples:
    #             return num_data_samples
    #         else:
    #             return base_samples
    #
    #     ac_seas = all_seasson_lens
    #     ac_seas.sort()  # sort just in case
    #
    #     if len(ac_seas) <= 1:
    #         base_samples = up_base_limit
    #     # else:
    #     #     if (ac_seas[-1] % ac_seas[0]) == 0:# out of mememory for large datasets
    #     #         base_samples = 5000
    #
    #     #print("=================NUM SEASONS========", len(ac_seas))
    #     #print('Seasons', ac_seas)
    #     #return int(2*ac_seas[-1])
    #     if num_data_samples <= base_samples:
    #         return  num_data_samples
    #     #seas_diff = 0
    #     #min_samps = 8
    #     #init_samps = min_samps
    #     #make sure 2xmax_season samples are available
    #
    #     seas = int(2*ac_seas[-1]) if int(2*ac_seas[-1]) < num_data_samples else ac_seas[-1]
    #     #seas = int(2*ac_seas[0]) if int(2*ac_seas[0]) < num_data_samples else ac_seas[0]
    #     # When there are 2 seasons and 2nd= 2*1st_seasons bats running time can be high for 2*seasonal length
    #     # if len(ac_seas) > 1:
    #     #     if (ac_seas[-1] % ac_seas[0]) == 0:
    #     #         seas = seas + 5 #ac_seas[0]
    #     lg_in = base_samples + int(num_data_samples/np.log(num_data_samples))
    #     # check for cases slightly up 3K
    #     log_inc_samples = lg_in if lg_in < num_data_samples else num_data_samples
    #     # if len(ac_seas) <= 1 and seas < base_samples :
    #     #     init_samps = max(seas, log_inc_samples)
    #     #     print('Num seasons is ', len(ac_seas), init_samps)
    #     # else:
    #     init_samps = max(min(seas,log_inc_samples),base_samples)
    #     #init_samps = min(seas,log_inc_samples)
    #     #print(' init size as befor limit===', init_samps,ac_seas)
    #     #check to not cross to 2nd season for init in large ds
    #     if len(ac_seas) > 1 and num_data_samples > up_base_limit and init_samps > up_base_limit:
    #         #if init_samps > ac_seas[-1]  and init_samps > up_base_limit:
    #         init_samps = up_base_limit
    #
    #
    #
    #     # print('Data size', num_data_samples)
    #     # print('log_inc init size as ', log_inc_samples)
    #     # print('np log',np.log(num_data_samples))
    #     # print('actual log_inc', int(num_data_samples/np.log(num_data_samples)))
    #     # print('seasonal init size as ', seas)
    #     #print('returning init size as ===', init_samps)
    #     #print('total rows =====',num_data_samples )
    #     # if len(ac_seas) > 1:
    #     #     #seas_diff = np.abs(ac_seas[-1] - ac_seas[0])
    #     #     #print('season diff', seas_diff,2*ac_seas[0] + seas_diff)
    #     #     return int(2*ac_seas[-1])
    #     #     #return data_samples
    #     # else:
    #     #     # init_samps = max(int(data_samples/2),2*ac_seas[-1])
    #     #     print('Single season',ac_seas[-1],init_samps )
    #     #     # if init_samps < min_samps:
    #     #     init_samps= data_samples
    #
    #     return min(init_samps, MAX_CAP)

    # @classmethod
    # def get_init_samples(cls, X,wf_context = None,init_perc=0.25, upper_limit = 300,
    #                      lower_limit =10):
    #
    #     l = len(X)
    #     per,all_seasons_lens = cls.get_regular_season_periodicity(X=X, wf_context=wf_context)
    #     per_from_fft = per
    #     bats_samps = cls.get_bats_init_samples(l,all_seasons_lens) # samples to init bats model
    #     bats_samps = 8 if bats_samps < 8 else bats_samps # just in case
    #     #print('PERIORIDICTY==================================== ', per)
    #     if per != -1:
    #         #print('number of init samples=', (3*int(per)))
    #         samples = max(math.ceil(2*int(per)),lower_limit) #
    #         per = int(samples / 2)  # in case lower_limit is selected and to ensure atleast 2 seasons
    #         ##init_samps = 0.9999 if samples/l == 1 else samples/l
    #         ############samples for bats##########
    #
    #         ####################################
    #         #print('returning SEASONAL ANALYSIS',samples , per,bats_samps,per_from_fft)
    #         return samples , per,bats_samps,per_from_fft # 2x the periodicity
    #
    #     n_samples = max(int(len(X) * init_perc), lower_limit)
    #     if n_samples > upper_limit:
    #         n_samples = upper_limit
    #     #print('PERIORIDICTY==================================== ', per)
    #     #print('number of init samples=',n_samples)
    #     #init_samps = 0.9999 if n_samples / l == 1 else n_samples / l
    #     #print('SEANSONAL Ananlysis Default',n_samples, int(n_samples/2),bats_samps,per_from_fft)
    #     return n_samples, int(n_samples/2),bats_samps,per_from_fft#per
    #
    #
    # @classmethod
    # def get_regular_season_periodicity(cls, X, wf_context = None, sub_season_percent_delta=0.0,
    #                                    max_num_seasons=2):
    #     per = -1
    #     multi_season_len = None
    #     try:
    #         if wf_context == None:
    #             import tspy
    #             wf_context = tspy #TSContext(die_on_exit=False)
    #
    #         #X = list(np.log1p(100 + np.array(X)))
    #         season_selector = wf_context.forecasters.season_selector(sub_season_percent_delta)
    #         multi_season_len = season_selector.get_multi_season_length(max_num_seasons, X)
    #         #print(multi_season_len)
    #         multi_season_len.sort()
    #         per = multi_season_len[-1]#0 for smallest season, -1 for largest season
    #         #print('Period',per)
    #         #not needed in new tspy Jan2020
    #         #if wf == -1:
    #         #    wf_context.stop()
    #     except BaseException as e:
    #         # not needed in new tspy Jan2020
    #         #if wf == -1:
    #          #   wf_context.stop()
    #         #print(e)
    #         #logger.warning(Exception(str(e)))
    #         logger.warning('Cannot find seasons')
    #     return per,multi_season_len
    #
    # @classmethod
    # def get_arima_init_size(cls,trial_ind, data_len):
    #     #print ('Data Len == ', data_len)
    #     data_len_cap = min(data_len,300000)
    #     if trial_ind == 4:
    #         return -1
    #     else:
    #         return data_len_cap- int(trial_ind*data_len/4)

    @classmethod
    def compute_metrics(cls, y_true, y_pred, verbose=False):
        '''
        :param y_true: a list of real numbers
        :param y_pred: a list of real numbers
        :return: mae, mse, r2, smape
        '''

        if y_pred is None or y_true is None:
            logger.warning('== Error in computing metrics, y_pred or y_true is None')
            return (None, None, None, None)

        y_true,y_pred = np.array(y_true).ravel(),np.array(y_pred).ravel()
        if (y_true.shape !=y_pred.shape):
            logger.warning('== Error in computing metrics, y_pred and y_true are not in the same dimension')
            return (None, None, None, None)

        # exclude nan based on y_true:
        idx = ~np.isnan(y_true)
        y_true,y_pred = y_true[idx], y_pred[idx]
        # exclude nan based on y_pred:
        idx = ~np.isnan(y_pred)
        y_true,y_pred = y_true[idx], y_pred[idx]

        try:
            # No multioutput='raw_values' param, so below functions return scalars
            mae = mean_absolute_error(y_true, y_pred)
            mse = mean_squared_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            # A constant model that always predicts the expected value of y, disregarding the input features,
            # would get a R^2 score of 0.0.
            if max(abs(y_pred - y_true)) < 1e-12:
                r2 = 1.0
            # smape = WatForeUtils.smape(y_true, y_pred)   # moved to adjusted_smape
            smape = WatForeUtils.adjusted_smape(y_true, y_pred)
        except Exception as e:
            print('== Error in computing metrics: ', e)
            return (None, None, None, None)

        if verbose:
            print('\n=== Evaluation metrics:')
            print(' %20s : %10.2f' % ('MAE', mae))
            print(' %20s : %10.2f' % ('MSE', mse))
            print(' %20s : %10.2f' % ('R2', r2))
            print(' %20s : %10.2f' % ('SMAPE', smape))
        return (mae, mse, r2, smape)

    # Periodicity with hw (older version but keeping for backup)
    # @classmethod
    # def get_hw_season_periodicity(cls, X,ts,wf_context = None, samples_per_sea=0.25):
    #     per = -1
    #     wf = 0
    #     try:
    #         if wf_context == None:
    #             import tspy
    #             #print('Context is None.')
    #             wf_context = tspy #TSContext(die_on_exit=False)
    #             wf = -1
    #         l = len(X)
    #         sps = int(l*samples_per_sea)
    #         init_seas = int(l /sps)
    #
    #         fr = wf_context.forecasters.hws(samples_per_season = sps,compute_seasonality=True,
    #                                         initial_training_seasons=init_seas)#,
    #                                         #use_full_error_history=False,error_history_length=int(0.40*l))
    #         X = list(np.log1p(100 + np.array(X)))
    #         ml = fr.update_model(ts,X)
    #         #print(fr)
    #         #print(ml)
    #         str_ml = str(fr)
    #         #assumes str format
    #         # Algorithm: HWSMultiplicative=48 (aLevel=0.801, bSlope=0.001, gSeas=0.001) level=6.838617369801295,
    #         # slope=-4.705137777022272E-4, seasonal(amp,per,avg)=(0.09172675546959308,48,0.9999832490720787)
    #         per = str_ml.split(', ')[-1].split(',')[-2]
    #         #not needed in new tspy Jan2020
    #         #if wf == -1:
    #         #    wf_context.stop()
    #     except BaseException as e:
    #         # not needed in new tspy Jan2020
    #         #if wf == -1:
    #          #   wf_context.stop()
    #         #print(e)
    #         #logger.warning(Exception(str(e)))
    #         logger.warning('Cannot find season, model not trained')
    #
    #     return per

    """
    scoring : str, default= mean_absolute_error
    other options for scroign mean_squared_error, mean_squared_log_error
    """

    # for Future use
    # @classmethod
    # def ts_cross_validation(cls, estimator,X, y,ts_icol_loc=-1, n_splits=2,scoring ='mean_absolute_error'):
    #
    #     scores = []
    #     #ests = []
    #     X_train_ary, X_test_ary, y_train_ary, y_test_ary = WatForeUtils.ts_train_test_splits(X=X,y=y,n_splits=n_splits,
    #                                                                                       ts_icol_loc=ts_icol_loc)
    #
    #     for tr in range(len(X_train_ary)):
    #
    #         estimator.fit(X=X_train_ary[tr],y=y_train_ary)
    #         pred_vals = estimator.predict(X_test_ary[tr])
    #         if cls.debug:
    #             print(X_train_ary[tr])
    #             print (X_test_ary[tr])
    #             print(pred_vals)
    #             print(y_test_ary[tr])
    #         if scoring == "mean_absolute_error": #mean_absolute_error,mean_squared_error, mean_squared_log_error
    #             scores.append(mean_absolute_error(y_test_ary[tr], pred_vals))
    #         if scoring == "mean_squared_error": #mean_squared_error, mean_squared_log_error
    #             scores.append(mean_squared_error(y_test_ary[tr], pred_vals))
    #         if scoring == "mean_squared_log_error": #mean_squared_error, mean_squared_log_error
    #             scores.append(mean_squared_log_error(y_test_ary[tr], pred_vals))
    #
    #
    #     return scores

    @classmethod# gets runtime from 200sec to 68.40858721733093
    def get_bats_init_samples(cls, num_data_samples,all_seasson_lens):

        #num_data_samples = len(X)
        base_samples = 1000 # This base could be dynamic, if only 1 season is found this can be higher
        up_base_limit = 2200
        MAX_CAP = 300000 # 300K rows
        #per,ac_seas = cls.get_regular_season_periodicity(X=X, wf_context=wf_context)
        if all_seasson_lens is None:
            if num_data_samples <= base_samples:
                return num_data_samples
            else:
                return base_samples

        ac_seas = all_seasson_lens
        ac_seas.sort()  # sort just in case

        if len(ac_seas) <= 1:
            base_samples = up_base_limit
        # else:
        #     if (ac_seas[-1] % ac_seas[0]) == 0:# out of mememory for large datasets
        #         base_samples = 5000

        #print("=================NUM SEASONS========", len(ac_seas))
        #print('Seasons', ac_seas)
        #return int(2*ac_seas[-1])
        if num_data_samples <= base_samples:
            return  num_data_samples
        #seas_diff = 0
        #min_samps = 8
        #init_samps = min_samps
        #make sure 2xmax_season samples are available

        seas = int(2*ac_seas[-1]) if int(2*ac_seas[-1]) < num_data_samples else ac_seas[-1]
        #seas = int(2*ac_seas[0]) if int(2*ac_seas[0]) < num_data_samples else ac_seas[0]
        # When there are 2 seasons and 2nd= 2*1st_seasons bats running time can be high for 2*seasonal length
        # if len(ac_seas) > 1:
        #     if (ac_seas[-1] % ac_seas[0]) == 0:
        #         seas = seas + 5 #ac_seas[0]
        lg_in = base_samples + int(num_data_samples/np.log(num_data_samples))
        # check for cases slightly up 3K
        log_inc_samples = lg_in if lg_in < num_data_samples else num_data_samples
        # if len(ac_seas) <= 1 and seas < base_samples :
        #     init_samps = max(seas, log_inc_samples)
        #     print('Num seasons is ', len(ac_seas), init_samps)
        # else:
        init_samps = max(min(seas,log_inc_samples),base_samples)
        #init_samps = min(seas,log_inc_samples)
        #print(' init size as befor limit===', init_samps,ac_seas)
        #check to not cross to 2nd season for init in large ds
        if len(ac_seas) > 1 and num_data_samples > up_base_limit and init_samps > up_base_limit:
            #if init_samps > ac_seas[-1]  and init_samps > up_base_limit:
            init_samps = up_base_limit



        # print('Data size', num_data_samples)
        # print('log_inc init size as ', log_inc_samples)
        # print('np log',np.log(num_data_samples))
        # print('actual log_inc', int(num_data_samples/np.log(num_data_samples)))
        # print('seasonal init size as ', seas)
        #print('returning init size as ===', init_samps)
        #print('total rows =====',num_data_samples )
        # if len(ac_seas) > 1:
        #     #seas_diff = np.abs(ac_seas[-1] - ac_seas[0])
        #     #print('season diff', seas_diff,2*ac_seas[0] + seas_diff)
        #     return int(2*ac_seas[-1])
        #     #return data_samples
        # else:
        #     # init_samps = max(int(data_samples/2),2*ac_seas[-1])
        #     print('Single season',ac_seas[-1],init_samps )
        #     # if init_samps < min_samps:
        #     init_samps= data_samples

        return min(init_samps, MAX_CAP)


    @classmethod
    def get_init_samples(cls, X,wf_context = None,init_perc=0.25, upper_limit = 300,
                         lower_limit =10):

        l = len(X)
        per,all_seasons_lens = cls.get_regular_season_periodicity(X=X, wf_context=wf_context)
        per_from_fft = per
        bats_samps = cls.get_bats_init_samples(l,all_seasons_lens) # samples to init bats model
        bats_samps = 8 if bats_samps < 8 else bats_samps # just in case
        #print('PERIORIDICTY==================================== ', per)
        if per != -1:
            #print('number of init samples=', (3*int(per)))
            samples = max(math.ceil(2*int(per)),lower_limit) #
            per = int(samples / 2)  # in case lower_limit is selected and to ensure atleast 2 seasons
            ##init_samps = 0.9999 if samples/l == 1 else samples/l
            ############samples for bats##########

            ####################################
            #print('returning SEASONAL ANALYSIS',samples , per,bats_samps,per_from_fft)
            return samples , per,bats_samps,per_from_fft # 2x the periodicity

        n_samples = max(int(len(X) * init_perc), lower_limit)
        if n_samples > upper_limit:
            n_samples = upper_limit
        #print('PERIORIDICTY==================================== ', per)
        #print('number of init samples=',n_samples)
        #init_samps = 0.9999 if n_samples / l == 1 else n_samples / l
        #print('SEANSONAL Ananlysis Default',n_samples, int(n_samples/2),bats_samps,per_from_fft)
        return n_samples, int(n_samples/2),bats_samps,per_from_fft#per


    @classmethod
    def get_regular_season_periodicity(cls, X, wf_context = None, sub_season_percent_delta=0.0,
                                       max_num_seasons=2):
        per = -1
        multi_season_len = None
        try:
            if wf_context == None:
                import autoai_ts_libs.deps.tspy
                wf_context = autoai_ts_libs.deps.tspy #TSContext(die_on_exit=False)

            #X = list(np.log1p(100 + np.array(X)))
            season_selector = wf_context.forecasters.season_selector(sub_season_percent_delta)
            multi_season_len = season_selector.get_multi_season_length(max_num_seasons, X)
            #print(multi_season_len)
            multi_season_len.sort()
            per = multi_season_len[-1]#0 for smallest season, -1 for largest season
            #print('Period',per)
            #not needed in new tspy Jan2020
            #if wf == -1:
            #    wf_context.stop()
        except BaseException as e:
            # not needed in new tspy Jan2020
            #if wf == -1:
             #   wf_context.stop()
            #print(e)
            #logger.warning(Exception(str(e)))
            logger.warning('Cannot find seasons')
        return per,multi_season_len

    @classmethod
    def get_arima_init_size(cls,trial_ind, data_len):
        #print ('Data Len == ', data_len)
        data_len_cap = min(data_len,300000)
        if trial_ind == 4:
            return -1
        else:
            return data_len_cap- int(trial_ind*data_len/4)

#class DataSets():

    # Some of datasets adapted from SROM benchmarking

    # @classmethod
    # def load_airline_passengers(cls) :
    #     name = "AirLine_Passengers"
    #     description = "AirLine Passengers"
    #     # trainfile = "https://vincentarelbundock.github.io/Rdatasets/csv/datasets/AirPassengers.csv"
    #     # Not use online data link to avoid build failure because of data download issue
    #     trainfile = "./time_series_fvt/repository/input/data/AirPassengers.csv"
    #     cols = ["ID", "time", "AirPassengers"]
    #     df_train = pd.read_csv(trainfile, names=cols, sep=r',', index_col='ID', engine='python', skiprows=1)
    #     univar_cols = ["AirPassengers"]
    #     return [name, description, df_train, 'time', univar_cols]

    # @classmethod
    # def load_cashflows(cls) :
    #     name = "CashFlows"
    #     description = "CashFlows dataset"
    #     trainfile = "https://raw.githubusercontent.com/antoinecarme/pyaf/master/data/CashFlows.txt"
    #     df_train = pd.read_csv(trainfile, sep=r'\t', engine='python')
    #     df_train['Date'] = df_train['Date'].apply(lambda x : datetime.datetime.strptime(x, "%Y-%m-%d"))
    #     return [name, description, df_train, 'Date', 'Cash']

    # @classmethod
    # def load_ozone(cls) :
    #     name = "Ozone"
    #     description = "https://datamarket.com/data/set/22u8/ozon-concentration-downtown-l-a-1955-1972"
    #     trainfile = "https://raw.githubusercontent.com/antoinecarme/TimeSeriesData/master/ozone-la.csv"
    #     cols = ["Month" , "Ozone"]
    #     df_train = pd.read_csv(trainfile, names = cols, sep=r',', engine='python', skiprows=1)
    #     df_train['Time'] = df_train['Month'].apply(lambda x : datetime.datetime.strptime(x, "%Y-%m"))
    #     lType = 'datetime64[D]'
    #     time_col = "Time"
    #     univar_col = "Ozone"
    #     return [name,description,df_train,time_col, univar_col]

    # @classmethod
    # def load_NN5(cls):
    #     name = "NN5"
    #     description = "NN5 competition final dataset"
    #     # trainfile = "https://raw.githubusercontent.com/antoinecarme/pyaf/master/data/NN5-Final-Dataset.csv"
    #     # Not use online data link to avoid build failure because of data download issue
    #     trainfile = "./time_series_fvt/repository/input/data/NN5-Final-Dataset.csv"
    #     df_train = pd.read_csv(trainfile, sep='\t', header=0, engine='python')
    #     df_train['Day'] = df_train['Day'].apply(lambda x : datetime.datetime.strptime(x, "%d-%b-%y"))
    #     time_col = "Day"
    #     data_cols = ['NN5-101', 'NN5-102', 'NN5-103', 'NN5-104', 'NN5-105', 'NN5-106',
    #                            'NN5-107', 'NN5-108', 'NN5-109', 'NN5-110',
    #                            'NN5-111']
    #     return [name,description,df_train,time_col, data_cols]

    # @classmethod
    # def load_M4(cls, granularity='Yearly'):
    #     name = "M4"
    #     description = "M4 competition final dataset"
    #     fileN= 'Yearly'
    #     if granularity.lower() == 'daily': fileN= 'Daily'
    #     if granularity.lower() == 'montly': fileN= 'Montly'
    #     if granularity.lower() == 'quartely': fileN= 'Quarterly'
    #     if granularity.lower() == 'weekly': fileN= 'Weekly'
    #
    #     trainfile = "https://github.com/M4Competition/M4-methods/blob/master/Dataset/Train/" + fileN +"-train.csv"
    #     testfile = "https://github.com/M4Competition/M4-methods/blob/master/Dataset/Test/" + fileN + "-test.csv"
    #
    #     df_train = pd.read_csv(trainfile, sep='\t', header=0, engine='python')
    #     df_test = pd.read_csv(testfile, sep='\t', header=0, engine='python')
    #     df_train['Day'] = df_train['Day'].apply(lambda x : datetime.datetime.strptime(x, "%d-%b-%y"))
    #     time_col = "V1"
    #     univar_col = "V2"
    #     return [name,description,df_train,df_test,time_col, univar_col]

    # @classmethod
    # #Train: 1~3285 / Test: 3286~3650
    # def load_daily_temp(cls) :
    #     name = "Daily Temperature"
    #     description = "Daily Temperature"
    #     # trainfile = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/daily-min-temperatures.csv"
    #     # Not use online data link to avoid build failure because of data download issue
    #     trainfile = "./time_series_fvt/repository/input/data/daily-min-temperatures.csv"
    #     cols = ["Date", "Temp"]
    #     df_train = pd.read_csv(trainfile, names = cols, sep=r',', engine='python', skiprows=1)
    #     univar_cols = ["Temp"]
    #     return [name, description, df_train, 'Date', univar_cols]


# if __name__ == "__main__":
#
#     #X = [[0, 10], [1, 20], [2, 30], [3, 40], [4, 50], [5, 60], [6, 79], [7, 31], [8, 98], [9, 76]]
#     #y = [[0, 10], [1, 20], [2, 30], [3, 40], [4, 50], [5, 60], [6, 79], [7, 31], [8, 98], [9, 76]]
#     import os
#     print(os.path.dirname(__file__))
#     X = [[0, 3, 10], [1, 3, 20], [2, 3, 30], [3, 3, 40], [4, 3, 50], [5, 3, 60], [6, 3, 76], [7, 3, 31],
#              [8, 3, 65], [9, 3, 77]]
#
#     #X = [[10, 3, 10], [11, 3, 20], [12, 3, 30], [13, 3, 40], [14, 3, 50], [15, 3, 60], [16, 3, 76], [17, 3, 31],
#     #         [18, 3, 65], [19, 3, 77]]
#     y = None#[[0, 3, 10], [1, 3, 20], [2, 3, 30], [3, 3, 40], [4, 3, 50], [5, 3, 60], [6, 3, 76], [7, 3, 31],
#               #[8, 3, 65], [9, 3, 77]]
#
#     #WatForeUtils.debug = True
#     # X_train_ary, X_test_ary, y_train_ary, y_test_ary = WatForeUtils.ts_train_test_splits(X,y,n_splits=2, ts_icol_loc=[0])
#     # print (X_train_ary)
#     # print(y_train_ary)
#     # print(X_test_ary)
#     # print(y_test_ary)
#
#     X_train, X_test, y_train, y_test = WatForeUtils.ts_train_test_split(X,y,ts_icol_loc = [0])
#
#     # print (X_train)
#     # print(y_train)
#     # print(X_test)
#     # print(y_test)
#
#
#     ds1 = DataSets.load_airline_passengers()
#     print(ds1[2].head())
#     print(len(ds1[2]))
#     #print(ds1[2].values[:,1])
#     print('Periodicity=', WatForeUtils.get_regular_season_periodicity(X=ds1[2].values[:, 1]))
#     #exit()
#     ds1 = DataSets.load_ozone()
#     print(ds1[2].head())
#     print(len(ds1[2]))
#     print('Periodicity=', WatForeUtils.get_regular_season_periodicity(X=ds1[2].values[:, 1].astype(float)))
#
#     ds1 = DataSets.load_cashflows()
#     print(ds1[2].head())
#     print(len(ds1[2]))
#     print('Periodicity=', WatForeUtils.get_regular_season_periodicity(X=ds1[2].values[:, 1].astype(float)))
#
#     ds1 = DataSets.load_NN5()
#     print(ds1[2].head())
#     print(len(ds1[2]))
#     print('Periodicity=', WatForeUtils.get_regular_season_periodicity(X=ds1[2].values[:, 1].astype(float)))
