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
Date: Feb-19-2020
"""

import logging
from autoai_ts_libs.watfore.watfore_forecasters import WatForeForecaster
from autoai_ts_libs.watfore.watfore_interpolator import WatForeInterpolator

logger = logging.getLogger()

logger.setLevel('WARNING')
from sklearn.pipeline import Pipeline


class ForecastingPipeline(Pipeline):

    # try:
    #     import os
    #     os.environ['TMP_DIR'] = '../libs/tmp'
    #     os.environ['TS_HOME'] = "../libs/time-series-assembly-1.0.0-jar-with-dependencies.jar"
    # except Exception as e:
    #     logger.error(e)

    def __init__(self, ts_icol_loc=-1,fill_missing_vals=False,
                 interpolator_type='linear',optimize_interpolator=False,prediction_horizon=1,
                 log_transform=True, lookback_win=1,
                 debug=False,**kwargs):


        self.ts_ocol_loc = ts_icol_loc
        self.ts_icol_loc = ts_icol_loc
        self.fill_missing_vals = fill_missing_vals
        self.wf_pipeline = None
        self.optimize_interpolator = optimize_interpolator
        self.wf_pipeline_args = kwargs
        self.interpolator_type = interpolator_type

        self.wf_pipeline_args['interpolator_type'] = self.interpolator_type
        self.wf_pipeline_args['ts_icol_loc'] = self.ts_icol_loc
        self.wf_pipeline_args['ts_ocol_loc'] = self.ts_ocol_loc
        self.wf_pipeline_args['debug'] =debug

        # self.log_transform = log_transform
        # self.lookback_win = lookback_win
        # self.prediction_horizon = prediction_horizon
        # self.wf_pipeline_args['log_transform'] = self.log_transform
        # self.wf_pipeline_args['lookback_win'] = self.lookback_win
        # self.wf_pipeline_args['prediction_horizon'] = self.prediction_horizon
        #self.wf_pipeline_args['fill_missing'] = self.fill_missing
        #self.wf_pipeline_args['optimize_interpolator'] = self.optimize_interpolator
        self._estimator = None
        self.debug = debug

        #self.steps = []

        #print(self.fill_missing_vals)



    def fit(self, X, y=None, **fit_params):

        if self.debug:
            logger.debug('x==',X)

        ########################################################
        #Models need to be created here because hpo calls set_param&fit and which doesn't reflect model change
        #if models initialized in init. Same should be done in forecasters if hpo is needed directly on forecasters
        if self.fill_missing_vals:
            # self._interpolator = WatForeInterpolator(interpolator_type=interpolator_type, append_tranform=False,
            #                                          ts_icol_loc=ts_icol_loc,
            #                                          ts_ocol_loc=ts_ocol_loc, default_value=0, debug=False)
            # print('Here------',self.interpolator_type)
            self._interpolator = WatForeInterpolator(ts_icol_loc=self.ts_icol_loc,debug=self.debug,
                                                     ts_ocol_loc=self.ts_ocol_loc,**self.wf_pipeline_args)
            # self._interpolator = WatForeInterpolator(interpolator_type=self.interpolator_type,
            #                                         ts_icol_loc=self.ts_icol_loc, ts_ocol_loc=self.ts_ocol_loc,
            #                                         debug = self.debug)#, kwargs=self.wf_pipeline_args)
            self._estimator = WatForeForecaster(ts_icol_loc=self.ts_icol_loc,debug=self.debug,
                                                **self.wf_pipeline_args)
            # self._estimator = WatForeForecaster(ts_icol_loc=self.ts_icol_loc,
            #                                    debug = self.debug)#,kwargs=self.wf_pipeline_args)  # , ts_icol_loc=ts_icol_loc
            self.steps = [('interpolator', self._interpolator),('forecaster', self._estimator)]
            self.wf_pipeline = Pipeline(steps=self.steps)
        else:
            # print('Here------2',kwargs)
            # self._estimator  = WatForeForecaster( **self.wf_pipeline_args)  # , ts_icol_loc=ts_icol_loc
            self._estimator = WatForeForecaster(ts_icol_loc=self.ts_icol_loc,debug=self.debug,
                                                **self.wf_pipeline_args)#**wf_pipeline has model params only
            self.steps= [('forecaster', self._estimator)]
            self.wf_pipeline = Pipeline(steps=self.steps)

            #        self.rbfopt = RbfoptSearchCV(self.forecasting_pipeline) #self.forecasting_pipeline#
        #        self.rbfopt = RandomizedSearchCV(estimator=self.forecasting_model,
        #                                         param_distributions=self.forecasting_model.get_param_dist(),
        #                                        cv=TimeSeriesSplit(n_splits=4),
        #                                       n_iter=10, return_train_score=False, verbose=2)  # ,n_jobs=10

        ##########################################################
        #print(('x==',X))
        #print(self.wf_pipeline_args)
        #print('fitting...',self._estimator)
        try:
            self.wf_pipeline.fit(X,y)
        except Exception as e:
            logger.warning('Model not Fitted!!,skipping')

        return self

    # def update_model(self, X, y):
    #     #print('Updating model', X, y)
    #     self._estimator.update_model(X,y)
    #     return self

    def predict(self, X, **predict_params):
        #print('estimator--', self.wf_pipeline.steps[-1][-1])
        #return self.wf_pipeline.steps[-1][-1].predict(X)
        #print('estimator--',self._estimator)
        pred_v = self._estimator.predict(X)
        #self._estimator.stop_context() # Already closing in estimator predict
        return pred_v

    # def predict_sliding_window(self, X, prediction_horizon=1, ts_col_loc=-1, validation_scoring=False):
    #
    #     return  self._estimator.predict_sliding_window(self, X, prediction_horizon=prediction_horizon,
    #                                                    ts_col_loc=ts_col_loc,validation_scoring=validation_scoring)

    def score(self, X, y, sample_weight=None):
        #return self.wf_pipeline.steps[-1][-1].score( X, y, sample_weight)
        return self._estimator.score(X, y, sample_weight)

    #def stop_context(self):

     #   return self._estimator.stop_context()

    def set_params(self, **params):
        # get params for both forecaster& interpolator and set here
        #print('SET PARAM Called--pipeline')
        self.wf_pipeline_args = params
        return self


    def get_param_dist(self, size=None):
        if self.optimize_interpolator:
            all_dist = WatForeForecaster.get_param_dist()
            all_dist.update(WatForeInterpolator.get_param_dist())
            #
            #print('-----------------', all_dist)
            #print(all_dist)
        else:
            all_dist = WatForeForecaster.get_param_dist()
            #print('-----------------',all_dist)

        return all_dist

    # def get_param_ranges(self, size=None):
    #     all_dist = None
    #     if self.optimize_interpolator:
    #         all_dist = WatForeForecaster.get_param_ranges()
    #         all_dist.update(WatForeInterpolator.get_param_ranges())
    #         print('-----------------',all_dist)
    #     else:
    #         all_dist = WatForeForecaster.get_param_ranges()
    #         #print(all_dist)
    #
    #     return all_dist

    def get_model_params(self):
        return self.wf_pipeline_args

    #def export(self):
 #       return self
