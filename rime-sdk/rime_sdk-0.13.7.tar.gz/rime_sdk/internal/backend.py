"""Library for connecting to RIME backend services."""

from typing import Any, Callable, Generic, Optional, TypeVar

import grpc

from rime_sdk.protos.image_registry.image_registry_pb2_grpc import ImageRegistryStub
from rime_sdk.protos.model_testing.model_testing_pb2_grpc import ModelTestingStub
from rime_sdk.protos.results_upload.results_upload_pb2_grpc import ResultsStoreStub
from rime_sdk.protos.test_run_results.test_run_results_pb2_grpc import ResultsReaderStub
from rime_sdk.protos.test_run_tracker.test_run_tracker_pb2_grpc import (
    TestRunTrackerStub,
)

# Generic type representing a client stub for a gRPC server.
C = TypeVar("C")

# GrpcApiKeyAuth is an AuthMetadataPlugin to add api key in header on all calls
class GrpcApiKeyAuth(grpc.AuthMetadataPlugin):
    """Auth plugin to add 'rime-api-key' header to grpc calls."""

    def __init__(self, api_key: str) -> None:
        """Create an Auth plugin to add 'rime-api-key' header to grpc calls.

        Args:
            api_key: str
                Valid RIME Api Key to add to requests
        """
        self._api_key = api_key

    def __call__(self, context: Any, callback: Callable) -> None:
        """Add rime-api-key to grpc metadata when called."""
        callback((("rime-api-key", self._api_key),), None)


class RIMEConnection(Generic[C]):
    """A connection to a backend client of type C."""

    def __init__(
        self,
        create_backend_fn: Callable[..., C],
        addr: str,
        api_key: str,
        channel_timeout: float = 5.0,
    ) -> None:
        """Create a new connection for a RIME backend.

        Args:
            create_backend_fn: Callable[..., C]
                Function to create a backend of type C from the channel acquired for
                this connection.
            addr: str
                The address of the backend server to create a channel to.
            api_key: str
                Api Key to validate RIME grpc requests with.
            channel_timeout: float
                The timeout in seconds for waiting for the given channel.
        """
        self._create_backend_fn = create_backend_fn
        self._api_key = api_key
        self._addr = addr
        self._channel_timeout = channel_timeout
        self._channel: Optional[grpc.Channel] = None

    def __enter__(self) -> C:
        """Acquires the channel created in the with-context."""
        self._channel = self._build_and_validate_channel(
            self._addr, self._channel_timeout
        )
        return self._create_backend_fn(self._channel)

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        """Frees the channel created in the with-context.

        Args:
            exc_type: Any
                The type of the exception (None if no exception occurred).
            exc_value: Any
                The value of the exception (None if no exception occurred).
            exc_traceback: Any
                The traceback of the exception (None if no exception occurred).
        """
        if self._channel:
            self._channel.close()

    def _build_and_validate_channel(self, addr: str, timeout: float) -> grpc.Channel:
        """Build and validate a secure gRPC channel at `addr`.

        Args:
            addr: str
                The address of the RIME gRPC service.
            timeout: float
                The amount of time in seconds to wait for the channel to become ready.

        Raises:
            ValueError
                If a connection cannot be made to a backend service within `timeout`.
        """
        try:
            # create credentials
            credentials = grpc.composite_channel_credentials(
                self._get_ssl_channel_credentials(),
                grpc.metadata_call_credentials(GrpcApiKeyAuth(self._api_key)),
            )
            channel = grpc.secure_channel(addr, credentials)
            grpc.channel_ready_future(channel).result(timeout=timeout)
            return channel
        except grpc.FutureTimeoutError:
            raise ValueError(f"Could not connect to server at address `{addr}`")

    def _get_ssl_channel_credentials(self) -> grpc.ChannelCredentials:
        """Fetch channel credentials for an SSL channel."""
        return grpc.ssl_channel_credentials()


class RIMEBackend:
    """An abstraction for connecting to RIME's backend services."""

    def __init__(self, domain: str, api_key: str = "", channel_timeout: float = 5.0):
        """Create a new RIME backend.

        Args:
            domain: str
                The base domain/address of the RIME service.+
            api_key: str
                The api key providing authentication to RIME services
            channel_timeout: float
                The amount of time in seconds to wait for channels to become ready
                when opening connections to gRPC servers.
        """
        self._channel_timeout = channel_timeout
        self._api_key = api_key
        domain_split = domain.split(".", 1)
        if domain_split[0][-4:] != "rime":
            raise ValueError("The configuration must be a valid rime webapp url")
        base_domain = domain_split[1]
        self._image_registry_addr = self._get_image_registry_addr(base_domain)
        self._model_testing_addr = self._get_model_testing_addr(base_domain)
        self._results_store_addr = self._get_results_store_addr(base_domain)
        self._test_run_tracker_addr = self._get_test_run_tracker_addr(base_domain)
        self._test_run_results_addr = self._get_test_run_results_addr(base_domain)

    def _get_image_registry_addr(self, domain: str) -> str:
        """Construct an address to the image-registry service from `domain`.

        Args:
            domain: str
                The base domain/address of the RIME service.
        """
        return f"rime-image-registry.{domain}:443"

    def _get_model_testing_addr(self, domain: str) -> str:
        """Construct an address to the model-testing service from `domain`.

        Args:
            domain: str
                The base domain/address of the RIME service.
        """
        return f"rime-modeltesting.{domain}:443"

    def _get_results_store_addr(self, domain: str) -> str:
        """Construct an address to the results store service from `domain`.

        Args:
            domain: str
                The base domain/address of the RIME service.
        """
        return f"rime-results-store.{domain}:443"

    def _get_test_run_tracker_addr(self, domain: str) -> str:
        """Construct an address to the test-run-tracker service from `domain`.

        Args:
            domain: str
                The base domain/address of the RIME service.
        """
        return f"rime-test-run-tracker.{domain}:443"

    def _get_test_run_results_addr(self, domain: str) -> str:
        """Construct an address to the test-run-results service from `domain`.

        Args:
            domain: str
                The base domain/address of the RIME service.
        """
        return f"rime-test-run-results.{domain}:443"

    def get_image_registry_stub(self) -> RIMEConnection[ImageRegistryStub]:
        """Return an image registry client."""
        return RIMEConnection[ImageRegistryStub](
            ImageRegistryStub,
            self._image_registry_addr,
            self._api_key,
            channel_timeout=self._channel_timeout,
        )

    def get_model_testing_stub(self) -> RIMEConnection[ModelTestingStub]:
        """Return a model testing client."""
        return RIMEConnection[ModelTestingStub](
            ModelTestingStub,
            self._model_testing_addr,
            self._api_key,
            channel_timeout=self._channel_timeout,
        )

    def get_result_store_stub(self) -> RIMEConnection[ResultsStoreStub]:
        """Return a result store client."""
        return RIMEConnection[ResultsStoreStub](
            ResultsStoreStub,
            self._results_store_addr,
            self._api_key,
            channel_timeout=self._channel_timeout,
        )

    def get_test_run_tracker_stub(self) -> RIMEConnection[TestRunTrackerStub]:
        """Return a test run tracker client."""
        return RIMEConnection[TestRunTrackerStub](
            TestRunTrackerStub,
            self._test_run_tracker_addr,
            self._api_key,
            channel_timeout=self._channel_timeout,
        )

    def get_test_run_results_stub(self) -> RIMEConnection[ResultsReaderStub]:
        """Return a test run results reader client."""
        return RIMEConnection[ResultsReaderStub](
            ResultsReaderStub,
            self._test_run_results_addr,
            self._api_key,
            channel_timeout=self._channel_timeout,
        )
