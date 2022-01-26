from autoai_ts_libs.srom.joint_optimizers.auto.base_auto import SROMAutoPipeline
from autoai_ts_libs.srom.estimators.regression.predictive_uncertainity_estimation import (
    PredictiveUncertaintyEstimator,
)
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.exceptions import NotFittedError
from autoai_ts_libs.utils.messages.messages import Messages
from autoai_ts_libs.srom.estimators.regression.stack_regression import StackRegressor as StackingRegressor 
class AutoRegression(SROMAutoPipeline):
    """
    The class for performing the auto-Regression in SROM using a well tested heuristic "Bottom-Up". \
    The model_stages in this class have already been setup from the benchmark results. \
    (link from the results of experimentation can be put here.)
    """

    def __init__(
        self,
        level="Early",
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
        execution_round=1,
        **kwarg
    ):
    
        super(AutoRegression, self).__init__(
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
        bayesian_paramgrid=None,
        rbopt_paramgrid=None,
        param_grid=param_grid,
        execution_round=execution_round,
        **kwarg
    )
        self.stacked_ensemble_estimator = None
    
    def _initialize_default_stages(self):
        """
        Set stages for the pipeline in a pre-defined manner.
        """
        return self.stages

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
        super(AutoRegression, self).fit(X, y)
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
        return super(AutoRegression, self).predict(X)

    def fit_stacked_ensemble(
        self,
        X,
        y,
        num_leader=5,
        n_estimators=30,
        aggr_type="median",
        bootstrap=True,
        max_samples=1.0,
        meta_regressor_for_stack=LinearRegression()
    ):
        """
        Train an ensemble model on the given data using Stacking strategy.
        Parameters:
            X (pandas dataframe or numpy array): Training dataset. \
                shape = [n_samples, n_features] \
                where n_samples is the number of samples and n_features is the number of features.
            y (pandas dataframe or numpy array, optional): Target vector to be used. \
                If target_column is added in the meta data, it is \
                used from there. shape = [n_samples] or [n_samples, n_output]
            num_leader (int): Number of model for creating stacked ensemble model.
            n_estimators (int): The number of base estimators in the ensemble,
            aggr_type (str): aggreate results either median or mean,
            bootstrap (boolean) : Whether samples are drawn with replacement. If False, sampling without replacement is performed.,
            max_samples (float) : The number of samples to draw from X to train each base estimator,
            meta_regressor_for_stack (object) : meta regressor to be used for stacking.
        Returns:
            Returns the trained pipeline object. \
            This would be an instance of the original pipeline class \
            i.e. sklearn.pipeline.Pipeline or pyspark.ml.Pipeline, not SROMPipeline.
        """
        mSet = self.get_leaders(num_leader)
        

        stacked_ensemble_estimator = StackingRegressor(
            base_models=mSet, meta_model=meta_regressor_for_stack
        )
        pipeline = make_pipeline(stacked_ensemble_estimator)
        self.stacked_ensemble_estimator = PredictiveUncertaintyEstimator(
            base_model=[pipeline],
            n_estimators=n_estimators,
            aggr_type=aggr_type,
            bootstrap=bootstrap,
            max_samples=max_samples
        )

        try:
            self.stacked_ensemble_estimator.fit(X, y)
        except Exception as ex:
            raise ex
        return self

    def predict_stacked_ensemble(self, X):
        """
        Predict the class labels/regression targets/anomaly scores etc. using \
        the trained ensemble stacking model.
        
        Parameters:
            X (pandas dataframe or numpy array): Input samples to be used for prediction.
        Returns:
            Predicted scores in an array of shape = [n_samples] or [n_samples, n_outputs].
        """
        if self.stacked_ensemble_estimator:
            return self.stacked_ensemble_estimator.predict(X)
        else:
            raise NotFittedError(Messages.get_message(message_id='AUTOAITSLIBS0014E'))

    def fit_voting_ensemble(
        self,
        X,
        y,
        num_leader=5,
        n_estimators=30,
        aggr_type="median",
        bootstrap=True,
        max_samples=1.0,
    ):
        """
        Train an ensemble model on the given data using Voting strategy.
        
        Parameters:
            X (pandas dataframe or numpy array): Training dataset. \
                shape = [n_samples, n_features] \
                where n_samples is the number of samples and n_features is the number of features.
            y (pandas dataframe or numpy array, optional): Target vector to be used. \
                If target_column is added in the meta data, it is \
                used from there. shape = [n_samples] or [n_samples, n_output]
            num_leader (int): Number of model for creating ensemble model.
            n_estimators (int): The number of base estimators in the ensemble,
            aggr_type (str): aggreate results either median or mean,
            bootstrap (boolean) : Whether samples are drawn with replacement. If False, sampling without replacement is performed.,
            max_samples (float) : The number of samples to draw from X to train each base estimator,
        Returns:
            Returns the trained pipeline object. \
            This would be an instance of the original pipeline class \
            i.e. sklearn.pipeline.Pipeline or pyspark.ml.Pipeline, not SROMPipeline.
        """
        mSet = self.get_leaders(num_leader)

        self.voting_ensemble_estimator = PredictiveUncertaintyEstimator(
            base_model=mSet,
            n_estimators=n_estimators,
            aggr_type=aggr_type,
            bootstrap=bootstrap,
            max_samples=max_samples,
        )
        try:
            self.voting_ensemble_estimator.fit(X, y)
        except Exception as ex:
            raise ex
        return self

    def predict_voting_ensemble(self, X):
        """
        Predict the class labels/regression targets/anomaly scores etc. using \
        the trained ensemble voting model.
        Parameters:
            X (pandas dataframe or numpy array): Input samples to be used for prediction.
        Returns:
            Predicted scores in an array of shape = [n_samples] or [n_samples, n_outputs].
        """
        if self.voting_ensemble_estimator:
            return self.voting_ensemble_estimator.predict(X)
        else:
            raise NotFittedError(Messages.get_message(message_id='AUTOAITSLIBS0015E'))

    def predict_stacked_ensemble_interval(self, X, prediction_percentile=95):
        """
        Predict the interval (lower bound and upper bound) using \
        the trained ensemble stacked model.
        Parameters:
            X (pandas dataframe or numpy array): Input samples to be used for prediction.
            prediction_percentile (integer): between 0 to 100.
        Returns:
            Predicted scores in an array of shape = [n_samples] or [n_samples, n_outputs].
        """
        if self.stacked_ensemble_estimator:
            return self.stacked_ensemble_estimator.predict_interval(
                X, prediction_percentile
            )
        else:
            raise NotFittedError(Messages.get_message(message_id='AUTOAITSLIBS0014E'))

    def predict_voting_ensemble_interval(self, X, prediction_percentile=95):
        """
        Predict the interval (lower bound and upper bound) using \
        the trained ensemble voting model.
        Parameters:
            X (pandas dataframe or numpy array): Input samples to be used for prediction.
            prediction_percentile (integer): between 0 to 100.
        Returns:
            Predicted scores in an array of shape = [n_samples] or [n_samples, n_outputs].
        """
        if self.voting_ensemble_estimator:
            return self.voting_ensemble_estimator.predict_interval(
                X, prediction_percentile
            )
        else:
            raise NotFittedError(Messages.get_message(message_id='AUTOAITSLIBS0015E'))