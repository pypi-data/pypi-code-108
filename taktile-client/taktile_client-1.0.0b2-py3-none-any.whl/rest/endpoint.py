"""
Endpoint implementation for the rest client.
"""
import json
import typing as t

from taktile_types.enums.endpoint import ArrowFormatKinds
from taktile_types.schemas.deployment.endpoint import EndpointInfoSchema

from taktile_client.config import arrow_available
from taktile_client.http_client import API
from taktile_client.rest.utils import is_serializable, safe_post

if arrow_available:
    import numpy as np
    import pandas as pd  # type: ignore

    # pylint: disable-next=ungrouped-imports
    from taktile_client.rest.serialize import deserialize, serialize


class ClientRestEndpoint:
    """
    The actual endpoint object.

    This is a Rest endpoint, exposing function calling through `__call__` and
    explainer endpoints through `explain`. This is the object that is
    `client.endpoints.repayment`.

    Parameters
    ----------
    api : API
        the api to use for making the calls
    info : EndpointInfoSchema
        the endpoint info of this endpoint
    """

    def __init__(self, *, api: API, info: EndpointInfoSchema):
        self._api = api
        self._info = info
        self.__name__ = info.name
        self._y: t.Any = None

    def __call__(
        self, payload: t.Any, *, retries: int = 3, timeout: float = 10.0
    ) -> t.Any:
        """
        Call the endpoints

        Parameters
        ----------
        payload : t.Any
            the payload
        retries : int
            how often to retry on recoverable errors
        timeout : float
            timeout of call

        Returns
        -------
        t.Any
            The response of the endpoint
        """
        serializable = is_serializable(payload)
        if serializable:
            data = serialize(payload)
        else:
            data = json.dumps(payload)
        result = safe_post(
            api=self._api,
            url=self._info.path,
            retries=retries,
            timeout=timeout,
            data=data,
        )
        if serializable:
            if self._info.response_kind == ArrowFormatKinds.DATAFRAME:
                return deserialize(pd.DataFrame(), value=result)
            if self._info.response_kind == ArrowFormatKinds.SERIES:
                return deserialize(pd.Series(), value=result)
            if self._info.response_kind == ArrowFormatKinds.ARRAY:
                return deserialize(np.array([]), value=result)
            return result
        return result

    def explain(
        self, payload: t.Any, *, retries: int = 3, timeout: float = 10.0
    ) -> t.Any:
        """
        Call the endpoint's explainer endpoint.

        Parameters
        ----------
        payload : t.Any
            the payload
        retries : int
            how often to retry on recoverable errors
        timeout : float
            timeout of call

        Returns
        -------
        t.Any
            The response of the explainer
        """
        if not self._info.explain_path:
            raise ValueError(
                "The endpoint {self._info.name} is of type {self._info.kind}"
                " and does not have an explain endpoint"
            )
        if is_serializable(payload):
            data = serialize(payload)
        else:
            data = json.dumps(payload)
        return safe_post(
            api=self._api,
            url=self._info.explain_path,
            retries=retries,
            timeout=timeout,
            data=data,
        )

    def X(self) -> t.Any:  # pylint: disable=invalid-name
        """Retrieve sample data

        Returns
        -------
        t.Any
            sample data to call the endpoint
        """
        return self._info.input_example

    def y(self) -> t.Any:  # pylint: disable=invalid-name
        """Retrieve sample response

        Returns
        -------
        t.Any
            sample response from the endpoint
        """
        # Use functools.cache when upgrading to Python 3.8
        if not self._y:
            self._y = safe_post(
                api=self._api,
                url=self._info.path,
                json=self._info.input_example,
            )
        return self._y


class RestEndpoints:  # pylint: disable=too-few-public-methods
    """
    A collection object for Rest endpoints.

    This is the `endpoints` object on Taktile Rest Clients.

    Parameters
    ----------
    api : API
        the api to use for calls
    infos : t.List[EndpointInfoSchema]
        a list of endpoints to instantiate
    """

    def __init__(self, *, api: API, infos: t.List[EndpointInfoSchema]):

        for info in infos:
            setattr(self, info.name, ClientRestEndpoint(api=api, info=info))
