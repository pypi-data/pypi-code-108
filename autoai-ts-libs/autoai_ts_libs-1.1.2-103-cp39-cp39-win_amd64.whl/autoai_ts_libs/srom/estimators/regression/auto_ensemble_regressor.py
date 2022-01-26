from abc import ABC
from autoai_ts_libs.srom.joint_optimizers.auto.auto_regression import AutoRegression

from sklearn.base import BaseEstimator, RegressorMixin
from autoai_ts_libs.utils.messages.messages import Messages

class SROMEnsemble(ABC):
    pass

class EnsembleRegressor(BaseEstimator, RegressorMixin, SROMEnsemble):
    """
    The class for performing the auto-Regression in SROM using a well tested heuristic "Bottom-Up". \
    The model_stages in this class have already been setup from the benchmark results. \
    """

    def __init__(
        self,
        level="default",
        save_prefix="auto_regression_output_",
        execution_platform="spark_node_random_search",
        cv=5,
        scoring=None,
        stages=None,
        execution_time_per_pipeline=2,
        num_options_per_pipeline_for_random_search=10,
        num_option_per_pipeline_for_intelligent_search=30,
        total_execution_time=10,
        param_grid=None,
        n_estimators_for_pred_interval=30,
        bootstrap_for_pred_interval=True,
        prediction_percentile=95,
        aggr_type_for_pred_interval="median",
        n_leaders_for_ensemble=5,
        max_samples_for_pred_interval=1.0,
        ensemble_type="voting",
        **kwarg
    ):

        self.auto_regression = AutoRegression(
            level=level,
            save_prefix=save_prefix,
            execution_platform=execution_platform,
            cv=cv,
            scoring=scoring,
            stages=stages,
            execution_time_per_pipeline=execution_time_per_pipeline,
            num_options_per_pipeline_for_random_search=num_options_per_pipeline_for_random_search,
            num_option_per_pipeline_for_intelligent_search=num_option_per_pipeline_for_intelligent_search,
            total_execution_time=total_execution_time,
            param_grid=param_grid,
        )
        self.level = level
        self.save_prefix = save_prefix
        self.execution_platform = execution_platform
        self.cv = cv
        self.scoring = scoring
        self.stages = stages
        self.execution_time_per_pipeline = execution_time_per_pipeline
        self.num_options_per_pipeline_for_random_search = num_options_per_pipeline_for_random_search
        self.num_option_per_pipeline_for_intelligent_search = num_option_per_pipeline_for_intelligent_search
        self.total_execution_time = total_execution_time
        self.param_grid = param_grid
        self.n_leaders_for_ensemble = n_leaders_for_ensemble
        self.prediction_percentile = prediction_percentile
        self.aggr_type_for_pred_interval = aggr_type_for_pred_interval
        self.n_estimators_for_pred_interval = n_estimators_for_pred_interval
        self.bootstrap_for_pred_interval = bootstrap_for_pred_interval
        self.max_samples_for_pred_interval = max_samples_for_pred_interval
        self.ensemble_type = ensemble_type
        if len(kwarg) > 0:
            if 'auto_regression' in kwarg.keys():
                self.auto_regression = kwarg['auto_regression']

    def fit(self, X, y):
        """
        Train the best model on the given data.
        Parameters:
            X (pandas dataframe or numpy array): Training dataset. \
                shape = [n_samples, n_features] \
                where n_samples is the number of samples and n_features is the number of features.
            y (pandas dataframe or numpy array, optional): Target vector to be used. \
                If target_column is added in the meta data, it is \
                used from there. shape = [n_samples] or [n_samples, n_output]
        Returns:
            Returns the trained pipeline object. \
            This would be an instance of the original pipeline class \
            i.e. sklearn.pipeline.Pipeline.
        """
        if self.n_leaders_for_ensemble == 1 and self.n_estimators_for_pred_interval == 1:
            self.auto_regression.fit(X, y)
        else:
            # Dealing with wrong samplings for prediction interval            
            tmp_max_samples_for_pred_interval = 1.0
            if isinstance(self.max_samples_for_pred_interval, int) and self.max_samples_for_pred_interval <= X.shape[0]:
                tmp_max_samples_for_pred_interval = self.max_samples_for_pred_interval
            elif isinstance(self.max_samples_for_pred_interval, int):
                tmp_max_samples_for_pred_interval = 1.0
            else:
                tmp_max_samples_for_pred_interval = self.max_samples_for_pred_interval
            
            if self.ensemble_type=="voting":
                self.auto_regression.fit_voting_ensemble(X, y, self.n_leaders_for_ensemble,
                                                    n_estimators=self.n_estimators_for_pred_interval,
                                                    aggr_type=self.aggr_type_for_pred_interval,
                                                    bootstrap=self.bootstrap_for_pred_interval,
                                                    max_samples=tmp_max_samples_for_pred_interval)
            else:
                self.auto_regression.fit_stacked_ensemble(X,y,self.n_leaders_for_ensemble,
                                                    n_estimators=self.n_estimators_for_pred_interval,
                                                    aggr_type=self.aggr_type_for_pred_interval,
                                                    bootstrap=self.bootstrap_for_pred_interval,
                                                    max_samples=tmp_max_samples_for_pred_interval,
                                                    )

        return self

    def predict(self, X):
        """
        Predict the class labels/regression targets/anomaly scores etc. using \
        the trained model pipeline.
        
        Parameters:
            X (pandas dataframe or numpy array): Input samples to be used for prediction.
        Returns:
            Predicted scores in an array of shape = [n_samples] or [n_samples, n_outputs].
        
        """
        if self.n_leaders_for_ensemble == 1 and self.n_estimators_for_pred_interval == 1:
            return self.auto_regression.predict(X)
        else:
            if self.ensemble_type=="voting":
                return self.auto_regression.predict_voting_ensemble(X)
            else:
                return self.auto_regression.predict_stacked_ensemble(X)

    def get_params(self, deep=True):
        ans = super().get_params(deep=deep)
        ans['auto_regression'] = self.auto_regression
        return ans

    def predict_proba(self, X):
        """
        Prediction probability.
        Parameters:
            X (pandas dataframe or numpy array): Input samples to be used for prediction.
        Returns:
            Prediction probability
        """
        if self.n_leaders_for_ensemble == 1 and self.n_estimators_for_pred_interval == 1:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0052E'))
        else:
            if self.ensemble_type=="voting":
                return self.auto_regression.predict_voting_ensemble_interval(X, 
                                                                    prediction_percentile=self.prediction_percentile)
            else:
                return self.auto_regression.predict_stacked_ensemble_interval(X,
                                                                    prediction_percentile=self.prediction_percentile)
