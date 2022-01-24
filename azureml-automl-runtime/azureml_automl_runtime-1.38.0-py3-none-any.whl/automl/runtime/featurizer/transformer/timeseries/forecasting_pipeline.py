# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""create a pipeline capable of supporting the operations like train, transform and predict."""
import warnings
from enum import Enum
from typing import Iterable

from sklearn.pipeline import Pipeline

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal,
    TimeseriesInvalidValueInPipeline,
    TimeseriesInvalidTypeInPipeline,
    TimeseriesInvalidPipelineExecutionType)
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.core.shared.forecasting_exception import ForecastingConfigException
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.forecasting_verify import Messages
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame


class AzureMLForecastPipelineExecutionType(Enum):
    """Enums representing execution types."""

    transforms = 1
    fit = 2
    fit_predict = 3
    fit_transform = 4
    predict = 5


class AzureMLForecastPipeline:
    """
    Pipeline class for Azure Machine Learning Package For Forecasting.

    Encapsulates the sklearn pipeline and exposes methods to execute
    pipeline steps and retrieve execution metrics.

    sklearn.pipeline.Pipeline: http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html

    :param steps:
        List of (name, transformer/estimator) tuples (implementing
        fit/transform) that are chained, in the order in which they are
        chained.
        Transformers must be a subclass of
        AzureMLForecastTransformerBase
    :type steps: list
    """

    def __init__(self, steps=None, **kwargs):
        """Create an AzureMLForecastPipeline."""
        # Hold a reference to the steps. We might
        # do something with these...
        self._steps = steps

        # Compose the sklearn pipeline.
        self._pipeline = Pipeline(self._steps)

        # Set all **kwargs on sklearn pipeline
        self._pipeline.set_params(**kwargs)

        # Legacy parameter, kept for back compatibility.
        self._logging_on = False

    def add_pipeline_step(self, name, step, prepend=False):
        """
        Add a pipeline step.

        .. py:method:: AzureMLForecastPipeline.add_pipeline_step
        Append a new step at the end of a pipeline or prepend a new step at
        the beginning if prepend is set to ```True```.

        :param name:
            Name of the new step.
        :type name: str

        :param step:
            New step, transformer or estimator, to add to the pipeline. An
            estimator can only be added when the pipeline doesn't contain an
            estimator already.
        :type step:
            azureml.automl.runtime.featurizer.transformer.
            timeseries.forecasting_base_estimator.AzureMLForecastTransformerBase

        :param prepend:
            If True, insert the new step at the beginning of the pipeline.
            Otherwise, append the new step at the end of the pipeline.
        :type prepend: bool
        :return: None
        """
        if next((step for key, step in self._pipeline.steps if key == name),
                None) is None:
            if prepend:
                self._pipeline.steps.insert(0, (name, step))
            else:
                self._pipeline.steps.append((name, step))
            self.validate_pipeline()
        else:
            raise ForecastingConfigException.create_without_pii(
                Messages.PIPELINE_STEP_ADD_INVALID,
                reference_code=ReferenceCodes._FORECASTING_PIPELINE_ADD_STEP)

    def remove_pipeline_step(self, name):
        """
        Remove an existing step from the pipeline.

        .. py:method:: AzureMLForecastPipeline.remove_pipeline_step

        :param name:
            Name of the step to remove.
        :type name: str

        :return: None
        """
        if next((step for key, step in self._pipeline.steps if key == name),
                None) is not None:
            self._pipeline.steps[:] = [(key, step) for key, step in
                                       self._pipeline.steps if not key == name]
            self.validate_pipeline()
        else:
            raise ForecastingConfigException.create_without_pii(
                Messages.PIPELINE_STEP_REMOVE_INVALID,
                reference_code='forecasting_pipeline.AzureMLForecastPipeline.remove_pipeline_step')

    def get_pipeline_params(self, deep=True):
        """
        Get pipeline parameters.

        .. py:method:: AzureMLForecastPipeline.get_pipeline_params

        :param deep:
            If True, will return the parameters for transformers/estimators
            and contained subobjects that are transformers/estimators.
        :type deep: bool

        :return: Parameter names mapped to their values.
        """
        return self._pipeline.get_params(deep)

    def get_params(self, deep=True):
        """
        Get pipeline parameters.

        .. py:method:: AzureMLForecastPipeline.get_params

        sklearn.pipeline.Pipeline.get_params:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline
        .get_params

        :param deep:
            If True, will return the parameters for transformers/estimators
            and contained subobjects that are transformers/estimators.
        :type deep: bool

        :return: Parameter names mapped to their values.
        :rtype: mapping of string to any
        """
        return self.get_pipeline_params(deep=deep)

    def set_pipeline_params(self, **kwargs):
        """
        Set the parameters of transformers and estimators in the pipeline.

        .. py:method:: AzureMLForecastPipeline.set_pipeline_params

        sklearn.pipeline.Pipeline.set_params:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline
        .set_params

        """
        self._pipeline.set_params(**kwargs)

    def validate_pipeline(self):
        """
        Validate pipeline step names.

        .. py:method:: AzureMLForecastPipeline.validate_pipeline

        Check if the transformers and estimators in the pipeline implement
        the required fit and transform methods.
        """
        try:
            if self._steps is None:
                raise ValidationException._with_error(AzureMLError.create(
                    AutoMLInternal, target="self._steps",
                    reference_code=ReferenceCodes._FORECASTING_PIPELINE_EMPTY,
                    error_details='Invalid forecasting pipeline found.')
                )
            self._pipeline._validate_steps()
        except ValueError as val_error:
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    TimeseriesInvalidValueInPipeline, target='self._pipeline',
                    reference_code=ReferenceCodes._FORECASTING_PIPELINE_INVALID_VALUE,
                    steps=str(self._pipeline.steps)
                ), inner_exception=val_error
            ) from val_error
        except TypeError as type_error:
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    TimeseriesInvalidTypeInPipeline, target='self._pipeline',
                    reference_code=ReferenceCodes._FORECASTING_PIPELINE_INVALID_TYPE,
                    steps=str(self._pipeline.steps)
                ), inner_exception=type_error
            ) from type_error

    def get_pipeline_step(self, name):
        """
        Return a pipeline step object by name.

        .. py:method:: AzureMLForecastPipeline.get_pipeline_step

        :param name: Name of the step to return.
        :type name: str

        :return: The step object corresponding the given step name.
        """
        # steps is a list containing a dictionary. The dictionary has a key that is the name and
        # and an object. We are returning an the step object's generator
        return next((step for key, step in self._pipeline.steps if key == name), None)

    def execute_pipeline_op(self, execution_type, X, y=None, **fit_params):
        """
        Execute the pipeline based on the execution type specified.

        1. Calling this method with a {fit*} execution type results in:
            a. Fit method invocation on all but last estimator step
            b. Invocation of a method with the same name as the execution_type
            on the last estimator step

        1. Calling this method with a {predict*} execution type results in:
            a. Transform method invocation on all but last estimator step
            b. Invocation of a method with the same name as the execution_type
            on the last estimator step

        :param execution_type:
            Pipeline operation to execute. Supports most operations of the
            sklearn pipeline.
        :type execution_type: AzureMLForecastPipelineExecutionType

        :param X:
            Input data for training, prediction, or transformation,
            depending on the execution type.
        :type X:
            azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :param y:
            Target values for model training or scoring.
        :type y: Iterable

        :return:
            Fitted pipeline, transformed data, prediction result,
            or scoring result, depending on ```execution_type```
        """
        # Check execution type
        if execution_type is None or not isinstance(execution_type, AzureMLForecastPipelineExecutionType):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesInvalidPipelineExecutionType, target='execution_type',
                                    reference_code=ReferenceCodes._FORECASTING_PIPELINE_INVALID_OP,
                                    exec_type=str(execution_type))
            )

        # Get hold of the last step.
        last_step = self._pipeline._final_estimator
        if last_step is None:
            raise ValidationException._with_error(AzureMLError.create(
                AutoMLInternal, target="last_step",
                reference_code=ReferenceCodes._FORECASTING_PIPELINE_NO_FINAL_STEP,
                error_details='The final estimator in the pipeline is invalid.')
            )

        # A compact if not giant chunck that models all pipeline execution types.
        if execution_type == AzureMLForecastPipelineExecutionType.fit:
            """ """
            Xt, fit_params = self.__execute_pipeline__preprocess_fit(X=X, y=y, **fit_params)
            last_step.fit(Xt, y, **fit_params)

            res = self

        elif execution_type == AzureMLForecastPipelineExecutionType.fit_transform:
            Xt, fit_params = self.__execute_pipeline__preprocess_fit(X=X, y=y, **fit_params)
            if hasattr(last_step, 'fit_transform'):
                res = last_step.fit_transform(Xt, y, **fit_params)
            else:
                res = last_step.fit(Xt, y, **fit_params).transform(Xt)

        elif execution_type == AzureMLForecastPipelineExecutionType.predict:
            Xt = self.__execute_pipeline__preprocess_transforms(X)
            try:
                res = last_step.predict(Xt, **fit_params)
            except TypeError:
                warnings.warn('The estimator does not seem to like kwargs.')
                res = last_step.predict(Xt)

        elif execution_type == AzureMLForecastPipelineExecutionType.fit_predict:
            Xt, fit_params = self.__execute_pipeline__preprocess_fit(X=X, y=y, **fit_params)
            res = last_step.fit_predict(Xt, y, **fit_params)

        elif execution_type == AzureMLForecastPipelineExecutionType.transforms:
            Xt = self.__execute_pipeline__preprocess_transforms(X)
            if hasattr(last_step, 'transform'):
                Xt = last_step.transform(Xt)
            res = Xt

        return res

    def __execute_pipeline__preprocess_transforms(self, X):
        """Private method that runs transform on all but last step in the pipeline."""
        Xt = X
        for name, transform in self._pipeline.steps[:-1]:
            if transform is not None:
                Xt = transform.transform(Xt)
        return Xt

    def __execute_pipeline__preprocess_fit(self, X, y=None, **fit_params):
        """Async method that runs fit on all but last step in the pipeline."""
        return self._pipeline._fit(X, y, **fit_params)

    # Executing pipeline functions by name

    def fit(self, X, y=None, **fit_params):
        """
        Fit the transformers then run fit.

        .. py:method:: AzureMLForecastPipeline.fit
        Fit all the transforms one after another and transform the data,
        then fit the transformed data using the final estimator.
        When y is ```None``` and X is a TimeSeriesDataFrame, the ```ts_vallue_colname```
        column of X is used as the target column.

        sklearn.pipeline.Pipeline.fit:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline.fit

        :param X:
            Training data. Must fulfill input requirements of the
            first step of the pipeline.
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :param y:
            Training target. Must fulfill label requirements for all steps of
            the pipeline.
        :type y: Iterable

        :return: Fitted pipeline.
        :rtype: azureml.automl.runtime.featurizer.transformer.timeseries.forecasting_pipeline.AzureMLForecastPipeline
        """
        if (y is None) and (isinstance(X, TimeSeriesDataFrame)):
            y = X[X.ts_value_colname]

        res = self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.fit,
                                       X, y, **fit_params)

        return res

    def fit_transform(self, X, y=None, **fit_params):
        """
        Fit the transformers then run fit_transform.

        .. py:method:: AzureMLForecastPipeline.fit_transform
        Fits all the transforms one after another and transforms the data,
        then applies the ```fit_transform``` method of the final estimator on
        transformed data.
        When y is ```None``` and X is a TimeSeriesDataFrame, the ```ts_vallue_colname```
        column of X is used as the target column.

        sklearn.pipeline.Pipeline.fit_transform:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline
        .fit_transform

        :param X:
            Training data. Must fulfill input requirements of the
            first step of the pipeline.
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :param y:
            Training target. Must fulfill label requirements for all steps of
            the pipeline.
        :type y: Iterable

        :return: Transformed samples.
        :rtype: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        """
        if (y is None) and (isinstance(X, TimeSeriesDataFrame)):
            y = X.ts_value

        return self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.fit_transform,
                                        X, y, **fit_params)

    def fit_predict(self, X, y=None, **fit_params):
        """
        Fit the transformers then run fit_predict.

        .. py:method:: AzureMLForecastPipeline.fit_predict
        Applies ```fit_transforms``` of a pipeline to the data, followed by the
        ```fit_predict``` method of the final estimator in the pipeline.
        Valid only if the final estimator implements fit_predict.
        When y is ```None``` and X is a TimeSeriesDataFrame, the ```ts_vallue_colname```
        column of X is used as the target column.

        sklearn.pipeline.Pipeline.fit_predict:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline
        .fit_predict

        :param X:
            Training data. Must fulfill input requirements of the
            first step of the pipeline.
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :param y:
            Training target. Must fulfill label requirements for all steps of
            the pipeline. default=None.
        :type y: Iterable

        :return: Prediction result on training data.
        """
        if (y is None) and (isinstance(X, TimeSeriesDataFrame)):
            y = X.ts_value

        return self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.fit_predict,
                                        X, y, **fit_params)

    def predict(self, X, **predict_params):
        """
        Apply transforms to the data, and predict with the final estimator.

        .. py:method:: AzureMLForecastPipeline.predict

        sklearn.pipeline.Pipeline.predict:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline
        .predict

        :param X:
            Data to predict on. Must fulfill input requirements of first
            step of the pipeline.
        :type X:
            TimeSeriesDataFrame

        :return: Prediction results on input data.
        """
        return self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.predict,
                                        X, y=None, **predict_params)

    def transform(self, X):
        """
        Apply transforms of all steps to the input data.

        .. py:method:: AzureMLForecastPipeline.transform

        :param X:
            Data to transform. Must fulfill input requirements of first
            step of the pipeline.
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :return: Transformed data.
        :rtype: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        """
        return self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.transforms,
                                        X, y=None)
