from __future__ import annotations

import time
from typing import Any, Optional
from terality._terality.data_transmitter import DataTransmitter, DataTransmitterS3

from terality.exceptions import TeralityError
from terality._terality.errorreporting import ErrorReporter

from common_client_scheduler.config import (
    SessionInfo,
    SessionInfoLocal,
    SessionInfoType,
    TransferConfig,
    TransferConfigLocal,
)
from common_client_scheduler.requests import FollowUpRequest
from common_client_scheduler import (
    PendingComputationResponse,
    CreateSessionResponse,
    AwsCredentials,
    DataTransferResponse,
)

from .utils.config import TeralityConfig, TeralityCredentials
from .httptransport import AuthCredentials, HttpTransport
from .utils import logger


class UnconfiguredTeralityClientError(TeralityError):
    pass


class SessionStateError(TeralityError):
    pass


class TeralityClient:  # pylint: disable=too-many-instance-attributes
    """Implement the connectivity with the Terality API.

    This is a stateful class managing authentication and session management. Currently, a single client
    may only have one session active at any given time.

    This client is not thread-safe.

    The client can be in an "unconfigured state" (no HttpTransport associated to it). In this state,
    it will raise an exception on each request.
    The first time such an unconfigured client is called, it will log a detailed error message.

    Args:
        http_transport: the underlying HttpTransport used to perform requests. If None, then this
            client will raise a user-friendly exception on each request, explaining how to configure Terality.
        auto_session: if True, when no session is currently opened, the TeralityClient will start a new session
            before performing a request.
    """

    # Note: the session management could be split to a separate class, but for now this class
    # is small enough to keep it inline.

    def __init__(self, http_transport: Optional[HttpTransport], auto_session: bool = False) -> None:
        self._http_transport = http_transport
        self._has_printed_error_message = False
        self._session: Optional[SessionInfoType] = None
        self._auto_session = auto_session
        self._credentials_fetcher = _AwsCredentialsFetcher(self)
        self._error_reporter: Optional[ErrorReporter] = None
        if self._http_transport is not None:
            self._error_reporter = ErrorReporter(self._http_transport)
        self._data_transfer: DataTransmitter = DataTransmitterS3()
        self._cache_disabled: bool = False

    def set_data_transfer(self, data_transfer: DataTransmitter) -> None:
        """Switch to data transfer implementation (during tests for instance).

        In production use of this class, the default data transfer implementation created by the constructor is enough and there is no need to call this method.
        """
        self._data_transfer = data_transfer

    def cache_disabled(self) -> bool:
        return self._cache_disabled

    def disable_cache(self) -> None:
        self._cache_disabled = True

    def enable_cache(self) -> None:
        self._cache_disabled = False

    def send_request(self, route: str, payload: Optional[Any], method="POST") -> Any:
        """Send a request to the Terality API, injecting credentials and a session ID when relevant.

        The arguments are the same as the `request` method on the underlying HttpTransport.
        """
        self._raise_if_unconfigured()
        assert self._http_transport is not None

        if self._auto_session and self._session is None:
            self.start_session()

        session_id = self._session.id if self._session is not None else None

        try:
            return self._http_transport.request(
                route,
                payload,
                session_id=session_id,
                method=method,
            )
        except Exception as e:
            if self._error_reporter is not None:
                self._error_reporter.report_exception_noexcept(e)
            raise

    def poll_for_answer(self, route: str, payload: Any, method="POST"):
        """Same as `send_request`, except that it polls the API on a PendingComputationResponse.

        On long running jobs, the API may answer with a PendingComputationResponse. This methods keeps
        polling the API until the answer is a real result.
        """
        response = self.send_request(route, payload, method=method)
        while isinstance(response, PendingComputationResponse):
            function_id = response.pending_computation_id
            response = self.send_request("follow_up", FollowUpRequest(function_id=function_id))
        return response

    def start_session(self):
        """Start a session.

        Before processing data, the client must start a session. The data created during the session is bound
        to the session: when the session is closed, the data is garbage collected. Most API calls that deal
        with data processing require an open session.

        Raise:
            SessionStateError: if a session is already in progress
        """
        if self._session is not None:
            raise SessionStateError("A session is already opened on this client.")

        self._raise_if_unconfigured()
        assert self._http_transport is not None

        session = self._http_transport.request("create_session", payload=None)
        if not isinstance(session, CreateSessionResponse):
            raise RuntimeError(
                f"Unexpected server response type, got {type(session)}, expected SessionInfo."
            )

        if isinstance(session.upload_config, TransferConfigLocal) and isinstance(
            session.download_config, TransferConfigLocal
        ):
            self._session = SessionInfoLocal(
                id=session.id,
                upload_config=session.upload_config,
                download_config=session.download_config,
            )
        elif isinstance(session.upload_config, TransferConfig) and isinstance(
            session.download_config, TransferConfig
        ):
            self._session = SessionInfo(
                id=session.id,
                upload_config=session.upload_config,
                download_config=session.download_config,
            )
        else:
            raise ValueError(
                "Can't create a session with the following transfer config types: upload={type(session.upload_config)} and download={type(session.download_config)}"
            )

    def data_transfer(self) -> DataTransmitter:
        self._data_transfer.set_current_session(self._session)
        return self._data_transfer

    def get_aws_credentials(self) -> AwsCredentials:
        """Return AWS credentials that can be used to upload files to the AWS API.

        Don't cache these credentials anywhere as they have a short lifetime. This method already perfoms
        the necessary caching.
        """
        return self._credentials_fetcher.get_credentials()

    def close_session(self):
        """Close the current session, if any.

        If no session is in progress, this method is a no-op.
        """
        self._raise_if_unconfigured()
        if self._session is None:
            return

        assert self._http_transport is not None

        self._http_transport.request("delete_session", None, session_id=self._session.id)
        self._session = None

    def _raise_if_unconfigured(self):
        if self._http_transport is not None:
            return
        if not self._has_printed_error_message:
            self._has_printed_error_message = True
            # TODO: better error message
            logger.warning("Could not read the Terality configuration files.")
        raise UnconfiguredTeralityClientError(
            "The Terality client is not configured (more info at https://docs.terality.com/)"
        )


class UnreadableTeralityConfigError(TeralityError):
    pass


def client_from_config() -> TeralityClient:
    """Try to read the Terality configuration files, and return a configured TeralityClient from them.

    Raise:
        UnreadableTeralityConfigError: if the Terality configuration files are not accessible.

    See:
        unconfigured_client
    """
    try:
        config = TeralityConfig.load()
        credentials = TeralityCredentials.load()
        auth_credentials = AuthCredentials(
            user=credentials.user_id, password=credentials.user_password
        )
        http_transport = HttpTransport(
            base_url=config.full_url(),
            request_timeout=config.timeout,
            auth_credentials=auth_credentials,
        )
        return TeralityClient(http_transport, auto_session=True)
    except Exception as e:
        raise UnreadableTeralityConfigError("could not read Terality configuration files") from e


def unconfigured_client() -> TeralityClient:
    """
    Return an unconfigured TeralityClient. This client will raise an exception on each request.

    Useful when the caller tried to call `client_from_config`, but no config was available. This unconfigured
    client can be used to signal to the user that it needs to configure Terality.
    """
    return TeralityClient(http_transport=None, auto_session=False)


def anonymous_client(api_url: Optional[str] = None) -> TeralityClient:
    """Return an anonymous Terality client (e.g a client that does not authenticate its requests).

    Args:
        api_url: if not provided, try to get the base URL from a configuration file. If the configuration
            file is missing or unreadable, then silently use the default settings embedded in this package.
            This function can thus be safely called even on systems where Terality is not configured yet.
    """
    timeout = (1, 1)
    if api_url is None:
        config = TeralityConfig.load(fallback_to_defaults=True)
        api_url = config.full_url()
        timeout = config.timeout

    http_transport = HttpTransport(base_url=api_url, request_timeout=timeout, auth_credentials=None)
    return TeralityClient(http_transport, auto_session=False)


class _AwsCredentialsFetcher:
    """Small utility to lazily fetch temporary AWS credentials from the Terality API.

    `get_credentials` will fetch credentials on the first call, and cache the result.

    Those credentials are used to upload files to Terality-owned S3 buckets.
    """

    def __init__(self, client: TeralityClient) -> None:
        self._credentials: Optional[AwsCredentials] = None
        self._credentials_fetched_at = time.monotonic()
        self._client = client

    def get_credentials(self) -> AwsCredentials:
        if self._credentials is None or time.monotonic() > self._credentials_fetched_at + 30 * 60:
            self._fetch_credentials()
        assert self._credentials is not None
        return self._credentials

    def _fetch_credentials(self) -> None:
        res: DataTransferResponse = self._client.send_request("transfers", {})
        self._credentials = res.temporary_upload_aws_credentials
        self._credentials_fetched_at = time.monotonic()
