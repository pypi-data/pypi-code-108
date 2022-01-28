import functools
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pandas  # type: ignore
from cached_property import cached_property  # type: ignore

from tktl.core.exceptions import ValidationException
from tktl.core.t import EndpointKinds
from tktl.core.utils import (
    DelayedLoaderX,
    DelayedLoaderXProfile,
    DelayedLoaderY,
    check_and_get_value,
)
from tktl.registration.schema import EndpointInputSchema, EndpointOutputSchema
from tktl.registration.validation import (
    input_pandas_representation,
    output_pandas_representation,
    validate_binary,
    validate_outputs,
    validate_shapes,
)


class Endpoint(ABC):
    KIND: EndpointKinds
    input_schema: EndpointInputSchema
    output_schema: EndpointOutputSchema
    explain_input_schema: Optional[EndpointInputSchema]
    delayed_loading: bool
    profile_columns: Optional[List[str]]

    def __init__(
        self,
        func: Callable,
        profile_columns: Optional[List] = None,
        disable_rest_validation: bool = True,
    ):
        self._func = func
        self.delayed_loading = False
        self.profile_columns = (
            [str(c) for c in profile_columns] if profile_columns is not None else None
        )
        self.disable_rest_validation = disable_rest_validation

    @cached_property
    def has_arrow_sample_data(self):
        return (
            self.input_schema.supports_arrow_sample_data
            and self.output_schema.supports_arrow_sample_data
        )

    @cached_property
    def has_rest_sample_data(self):
        if self.disable_rest_validation:
            return False
        else:
            return (
                self.input_schema.supports_rest_sample_data
                and self.output_schema.supports_rest_sample_data
            )

    @property
    def func(self):
        return self._func

    @property
    def series_func(self) -> Union[Any, pandas.Series]:
        name = self._func.__name__

        def to_series(x):
            return pandas.Series(self.func(x))

        to_series.__name__ = name
        return to_series

    @cached_property
    @abstractmethod
    def profiling_supported(self):
        return True

    @cached_property
    def input_names(self):
        return []

    @cached_property
    def output_names(self):
        return []


class TabularEndpoint(Endpoint):
    explain_input_schema: Optional[EndpointInputSchema]
    KIND: EndpointKinds = EndpointKinds.TABULAR

    def __init__(self, func, X, y, profile_columns, disable_rest_validation):
        super().__init__(
            func, profile_columns, disable_rest_validation=disable_rest_validation
        )

        if isinstance(X, str) and isinstance(y, str):
            self.delayed_loading = True

            x_value = DelayedLoaderX(path=X, label=y)
            y_value = DelayedLoaderY(path=X, label=y)

        else:
            x_value = X
            y_value = y

        self.input_schema = EndpointInputSchema(
            value=x_value, endpoint_kind=self.KIND, endpoint_name=self.func.__name__
        )
        self.output_schema = EndpointOutputSchema(
            value=y_value, endpoint_kind=self.KIND, endpoint_name=self.func.__name__
        )

        if self.profiling_supported:
            if not profile_columns:
                self.profile_columns = self.input_schema.names

            if self.delayed_loading:
                explain_input_value = DelayedLoaderXProfile(
                    path=X, label=y, columns=self.profile_columns
                )
            else:
                explain_input_value = self.input_schema.pandas_representation[
                    self.profile_columns
                ]

            self.explain_input_schema = EndpointInputSchema(
                value=explain_input_value,
                endpoint_kind=self.KIND,
                endpoint_name=f"explain__{self.func.__name__}",
            )
        else:
            self.explain_input_schema = None

    def _profiling_supported(self) -> Union[bool, pandas.Series]:
        if (
            not self.input_schema.pandas_convertible
            or not self.output_schema.pandas_convertible
        ):

            return False
        try:
            value = check_and_get_value(self.input_schema.value, first_batch=True)
            predictions = self.func(value)
        except Exception as e:
            raise ValidationException(
                f"Function provided is unable to produce predictions from given sample values: {e}"
            )
        return predictions

    @cached_property
    def profiling_supported(self):
        predictions = self._profiling_supported()
        if predictions is False:
            return False
        else:
            try:
                x_frame = input_pandas_representation(value=self.input_schema.value)
                y_series = output_pandas_representation(value=self.output_schema.value)
            except ValueError:
                return False
            return validate_outputs(predictions) and validate_shapes(
                x_frame, y_series, predictions
            )

    @cached_property
    def input_names(self):
        return self.input_schema.names

    @cached_property
    def explain_input_names(self):
        return self.explain_input_schema.names if self.explain_input_schema else []

    @cached_property
    def output_names(self):
        return self.output_schema.names if self.explain_input_schema else []


class BinaryEndpoint(TabularEndpoint):
    KIND = EndpointKinds.BINARY

    def __init__(self, func, X, y, profile_columns, disable_rest_validation=False):
        super().__init__(
            func, X, y, profile_columns, disable_rest_validation=disable_rest_validation
        )

    @cached_property
    def profiling_supported(self):
        predictions = self._profiling_supported()
        if predictions is False:
            return False
        return super().profiling_supported and validate_binary(predictions)


class RegressionEndpoint(TabularEndpoint):
    KIND = EndpointKinds.REGRESSION

    def __init__(self, func, X, y, profile_columns, disable_rest_validation=False):
        super().__init__(
            func, X, y, profile_columns, disable_rest_validation=disable_rest_validation
        )

    @cached_property
    def profiling_supported(self):
        predictions = self._profiling_supported()
        if predictions is False:
            return False
        return super().profiling_supported and validate_outputs(predictions)


class CustomEndpoint(Endpoint):
    def get_input_and_output_for_profiling(
        self, **kwargs
    ) -> Tuple[pandas.DataFrame, pandas.Series]:
        raise ValueError("Custom endpoint does not have profiling enabled")

    KIND = EndpointKinds.CUSTOM

    def __init__(
        self,
        func,
        payload_model=None,
        response_model=None,
        X=None,
        y=None,
        disable_rest_validation=False,
    ):
        try:
            assert isinstance(func, Callable)
        except AssertionError:
            raise ValidationException("Endpoint function is not a callable")

        models_defined = payload_model and response_model
        x_and_y_defined = (X is not None) and (y is not None)
        if not models_defined and not x_and_y_defined:
            disable_rest_validation = True
            payload_model = response_model = Union[Dict, List]

        if models_defined and x_and_y_defined:
            raise ValueError(
                "For custom endpoints, either define sample data or payload models"
            )

        super().__init__(func, disable_rest_validation=disable_rest_validation)

        self.input_schema = EndpointInputSchema(
            value=X,
            endpoint_kind=self.KIND,
            endpoint_name=self.func.__name__,
            user_defined_model=payload_model,
        )
        self.output_schema = EndpointOutputSchema(
            value=y,
            endpoint_kind=self.KIND,
            endpoint_name=self.func.__name__,
            user_defined_model=response_model,
        )

    @cached_property
    def profiling_supported(self):
        return False


class Tktl:
    def __init__(self):
        self.endpoints = []

    # This is the user-facing decorator for function registration
    def endpoint(
        self,
        func: Callable = None,
        kind: str = EndpointKinds.REGRESSION,
        X: Any = None,
        y: Any = None,
        payload_model=None,
        response_model=None,
        disable_rest_validation: bool = False,
        profile_columns: Optional[List] = None,
    ):
        """Register function as a Taktile endpoint

        Parameters
        ----------
        func : Callable, optional
            Function that describes the desired operation, by default None
        kind : str, optional
            Specification of endpoint type ("regression", "binary", "custom"),
            by default "regression"
        X : pd.DataFrame, optional
            Reference input dataset for testing func. Used when argument "kind"
            is set to "regression" or "binary", by default None.
        y : pd.Series, optional
            Reference output for evaluating func. Used when argument "kind"
            is set to "regression" or "binary", by default None.
        payload_model:
            Type hint used for documenting and validating payload. Used in
            custom endpoints only.
        response_model:
            Type hint used for documenting and validating response. Used in
            custom endpoints only.
        disable_rest_validation: bool
            If true, skip Rest schema validation
        profile_columns: List, optional
            List of column names for which to run profiling. Used in binary
            and regression endpoints only.

        Returns
        -------
        Callable
            Wrapped function
        """
        endpoint: Union[
            TabularEndpoint, RegressionEndpoint, BinaryEndpoint, CustomEndpoint
        ]
        if func is None:
            return functools.partial(
                self.endpoint,
                kind=kind,
                X=X,
                y=y,
                payload_model=payload_model,
                response_model=response_model,
                disable_rest_validation=disable_rest_validation,
                profile_columns=profile_columns,
            )
        if kind == "tabular":
            endpoint = TabularEndpoint(
                func=func,
                X=X,
                y=y,
                profile_columns=profile_columns,
                disable_rest_validation=disable_rest_validation,
            )
        elif kind == "regression":
            endpoint = RegressionEndpoint(
                func=func,
                X=X,
                y=y,
                profile_columns=profile_columns,
                disable_rest_validation=disable_rest_validation,
            )
        elif kind == "binary":
            endpoint = BinaryEndpoint(
                func=func,
                X=X,
                y=y,
                profile_columns=profile_columns,
                disable_rest_validation=disable_rest_validation,
            )
        elif kind == "custom":
            endpoint = CustomEndpoint(
                func=func,
                payload_model=payload_model,
                response_model=response_model,
                X=X,
                y=y,
                disable_rest_validation=disable_rest_validation,
            )
        else:
            raise ValidationException(f"Unknown endpoint kind: '{kind}'")

        self.endpoints.append(endpoint)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            pred = func(*args, **kwargs)
            return pred

        return wrapper
