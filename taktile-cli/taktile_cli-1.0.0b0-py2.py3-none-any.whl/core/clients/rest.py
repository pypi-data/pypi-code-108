import os
from http import HTTPStatus
from typing import Optional

import requests
import tenacity  # type: ignore
from openapi_schema_pydantic import OpenAPI  # type: ignore
from requests import ConnectionError, Timeout
from taktile_types.enums.instance import ServiceType

from tktl import __version__ as tktl_version
from tktl.core.clients import Client
from tktl.core.clients.http_client import API, interpret_response
from tktl.core.config import settings
from tktl.core.exceptions import APIClientException, APIClientExceptionRetryable
from tktl.core.loggers import LOG, Logger
from tktl.core.schemas.repository import _format_http_url

# codes for which retry-ing is not necessary, and for which
# precise error information can be retrieved either from
# the request, or deployment logs
DO_NOT_RETRY_STATUS_CODES = [
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.FORBIDDEN,
    HTTPStatus.UNAUTHORIZED,
    HTTPStatus.UNPROCESSABLE_ENTITY,
]


class RestClient(Client):
    def get_schema(self, *args, **kwargs):
        pass

    TRANSPORT = ServiceType.REST

    def __init__(
        self,
        api_key: str,
        repository_name: str,
        branch_name: str,
        endpoint_name: str,
        local: bool = False,
        logger: Logger = LOG,
        verbosity: int = 0,
        skip_auth: bool = False,
    ):
        super().__init__(
            api_key=api_key,
            repository_name=repository_name,
            branch_name=branch_name,
            endpoint_name=endpoint_name,
            local=local,
            logger=logger,
            verbosity=verbosity,
        )
        if not skip_auth:
            self._authenticate()

    def predict(self, inputs, retries=3, timeout=10):
        """predict.
        Use model endpoint

        Parameters
        ----------
        inputs :
            inputs variables
        retries : int
            number of retries
        timeout : float
            timeout in seconds

        Raises
        ------
        requests.Timeout
            If the last attempt resulted in a timeout exception
        requests.ConnectionError
            If the last attempt was not able to connect
        EndpointException
            If the last attempt resulted in a connection error
        """

        def my_after(retry_state):
            self.logger.warning(
                f"Timeout while trying to predict on try #{retry_state.attempt_number}/{retries}: {retry_state.outcome}"
            )

        def my_stop(retry_state):
            if retry_state.attempt_number >= retries:
                self.logger.error(
                    f"Giving up trying to predict after {retry_state.attempt_number} attempts"
                )
                return True
            return False

        @tenacity.retry(
            stop=my_stop,
            retry=tenacity.retry_if_exception_type(
                exception_types=(APIClientExceptionRetryable,)
            ),
            wait=tenacity.wait_random(min=0, max=1),
            after=my_after,
            reraise=True,
        )
        def wrapped():
            try:
                response = self.client.post(
                    url=f"model/{self.endpoint_name}", json=inputs, timeout=timeout,
                )
            except (Timeout, ConnectionError) as e:
                raise APIClientExceptionRetryable(
                    status_code=-1, detail="A connection error has occured"
                ) from e

            if response.status_code in DO_NOT_RETRY_STATUS_CODES:
                if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                    raise APIClientException(
                        status_code=response.status_code,
                        detail="An error occurred with your request. Check the deployment's logs for more information",
                    )
                elif response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
                    json_response = response.json()
                    raise APIClientException(
                        status_code=response.status_code,
                        detail=f"Unprocessable request body: {json_response['detail']})",
                    )
                else:
                    json_response = response.json()
                    raise APIClientException(
                        status_code=response.status_code,
                        detail=f"Authentication Error: {json_response['detail']}",
                    )
            try:
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                try:
                    json_response = response.json()
                    raise APIClientExceptionRetryable(
                        status_code=response.status_code,
                        detail=json_response["detail"],
                    ) from e
                except (ValueError, KeyError) as e:
                    # Note that we use ValueError instead of JSONDecodeError above on purpose,
                    # because depending on runtime configuration `requests` might choose to
                    # use `simplejson` which has a different JSONDecodeError. However both derive
                    # from ValueError.
                    content = response.text
                    raise APIClientExceptionRetryable(
                        status_code=response.status_code,
                        detail=f"An error occurred with your request: {content})",
                    ) from e
            return response.json()

        return wrapped()

    @classmethod
    def for_url(cls, api_key: str, url: str, endpoint_name: str):
        rest_url = cls.format_url(url=url)
        instantiated = cls(
            api_key=api_key,
            repository_name="",
            branch_name="",
            endpoint_name=endpoint_name,
            skip_auth=True,
        )
        client = API(api_url=rest_url)
        client.headers.update({"User-Agent": f"taktile-client:{tktl_version}"})
        instantiated.set_client_and_location(location=rest_url, client=client)
        instantiated.logger.trace(f"Performing authentication request against {url}")
        try:
            instantiated.health()
        except APIClientException as e:
            instantiated.logger.error(f"Could not instantiate client: {e.detail}")
            return
        return instantiated

    @staticmethod
    def format_url(url: Optional[str]) -> str:
        return _format_http_url(url, docs=False)

    def _authenticate(self, health_check: bool = False):
        if health_check:
            location = self.get_deployment_location()
        else:
            location = self.get_endpoint_and_location()
        client = API(api_url=location)
        self.set_client_and_location(location=location, client=client)

    @property
    def local_endpoint(self):
        return settings.LOCAL_REST_ENDPOINT

    def list_deployments(self):
        pass

    def get_sample_data(self):
        if not self.endpoint_has_rest_sample_data:
            self.logger.warning("Sample data not available for this endpoint")
            return None, None
        schema = self.client.get(url="openapi.json")
        openapi = OpenAPI.parse_obj(schema.json())
        request_reference, response_reference = get_endpoint_model_reference(
            openapi, endpoint=self.endpoint_name
        )
        sample_input = openapi.components.schemas[request_reference].example
        if not sample_input:
            self.logger.warning("No sample input found for endpoint")
        sample_output = openapi.components.schemas[response_reference].example
        if not sample_output:
            self.logger.warning("No sample output found for endpoint")
        return sample_input, sample_output

    def health(self):
        response = self.client.get(url="healthz")
        return interpret_response(response, model=None, ping=True)


def get_endpoint_model_reference(openapi: OpenAPI, endpoint: str):
    for k in openapi.paths.keys():
        if f"/model/{endpoint}" == k:
            request_ref = (
                openapi.paths[k]
                .post.requestBody.content["application/json"]
                .media_type_schema.ref
            )
            response_ref = (
                openapi.paths[k]
                .post.responses["200"]
                .content["application/json"]
                .media_type_schema.ref
            )
            return os.path.basename(request_ref), os.path.basename(response_ref)
    return None
