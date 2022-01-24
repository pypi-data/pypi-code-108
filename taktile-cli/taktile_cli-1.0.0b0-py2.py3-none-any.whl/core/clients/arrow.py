import math
from typing import Any, Optional, Tuple

import pandas  # type: ignore
from pyarrow import Table  # type: ignore
from pyarrow.flight import ClientAuthHandler  # type: ignore
from pyarrow.flight import (
    FlightCancelledError,
    FlightClient,
    FlightDescriptor,
    FlightInfo,
    FlightUnauthenticatedError,
    FlightUnavailableError,
    Ticket,
)
from pyarrow.lib import ArrowException  # type: ignore
from taktile_types.enums.instance import ServiceType

from tktl.core.clients import Client
from tktl.core.config import settings
from tktl.core.exceptions import APIClientException, AuthenticationError
from tktl.core.loggers import LOG, Logger
from tktl.core.schemas.repository import _format_grpc_url, load_certs
from tktl.core.serializers import deserialize_arrow, serialize_arrow


class ApiKeyClientAuthHandler(ClientAuthHandler):
    """An example implementation of authentication via ApiKey."""

    def __init__(self, api_key: Optional[str]):
        super(ApiKeyClientAuthHandler, self).__init__()
        self.api_key = api_key

    def authenticate(self, outgoing, incoming):
        outgoing.write(self.api_key)
        self.api_key = incoming.read()

    def get_token(self):
        return self.api_key


class ArrowFlightClient(Client):
    TRANSPORT = ServiceType.GRPC

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
            try:
                self._authenticate()
            except ArrowException as AE:
                self.logger.error(
                    f"Unable to authenticate against Arrow endpoint: {AE}"
                )
                exit(1)

    @classmethod
    def for_url(cls, api_key: str, url: str, endpoint_name: str):
        grpc_url = cls.format_url(url=url)
        instantiated = cls(
            api_key=api_key,
            repository_name="",
            branch_name="",
            endpoint_name=endpoint_name,
            skip_auth=True,
        )
        if settings.LOCAL_STACK:
            certs = None
        else:
            certs = load_certs()
        client = FlightClient(tls_root_certs=certs, location=grpc_url)
        instantiated.logger.trace(
            f"Performing authentication request against {grpc_url}"
        )
        client.authenticate(
            ApiKeyClientAuthHandler(api_key=instantiated.taktile_client.api_key)
        )
        instantiated.set_client_and_location(location=grpc_url, client=client)
        return instantiated

    @staticmethod
    def format_url(url: Optional[str]) -> str:
        return _format_grpc_url(url)

    @property
    def local_endpoint(self):
        return settings.LOCAL_ARROW_ENDPOINT

    def list_deployments(self):
        pass

    def list_commands(self):
        return self.client.list_actions()

    def _authenticate(self, health_check: bool = False):
        if health_check:
            location = self.get_deployment_location()
        else:
            try:
                location = self.get_endpoint_and_location()
            except APIClientException as e:
                self.logger.error(f"Unable to authenticate: {e.detail}")
                exit(1)
                return

        certs = None if settings.LOCAL_STACK else load_certs()
        client = FlightClient(location=location, tls_root_certs=certs)
        self.logger.trace(f"Performing authentication request against {location}")
        client.authenticate(
            ApiKeyClientAuthHandler(api_key=self.taktile_client.api_key)
        )

        self.set_client_and_location(location=location, client=client)

    def _send_batch(self, writer, batch, reader, batch_number):
        try:
            writer.write_batch(batch)
            return reader.read_chunk()
        except Exception as e:
            self.logger.error(
                f"ERROR: performing prediction for batch {batch_number}: {e} "
                f"The predictions from this batch will be missing from the result"
            )
            return None

    def predict(self, inputs: Any, use_input_index: bool = False) -> Any:
        table = serialize_arrow(inputs)
        batch_size, batch_memory = get_chunk_size(table)
        if not (batch_size and batch_memory):
            return
        descriptor = self.get_flight_info(command_name=str.encode(self.endpoint_name))
        writer, reader = self.client.do_exchange(descriptor.descriptor)  # type: ignore
        self.logger.trace(
            f"Initiating prediction request with batches of {batch_size} records of "
            f"~{batch_memory:.2f} MB/batch"
        )
        batches = table.to_batches(max_chunksize=batch_size)
        chunks = []
        schema = None
        with writer:
            writer.begin(table.schema)
            for i, batch in enumerate(batches):
                self.logger.trace(f"Prediction for batch {i + 1}/{len(batches)}")
                chunk = self._send_batch(
                    writer=writer, batch=batch, reader=reader, batch_number=i + 1
                )
                if not chunk:
                    continue
                if not schema and chunk.data.schema is not None:
                    schema = chunk.data.schema
                chunks.append(chunk.data)
        deserialized = deserialize_arrow(Table.from_batches(chunks, schema))
        if use_input_index:
            input_has_index = isinstance(inputs, pandas.Series) or isinstance(
                inputs, pandas.DataFrame
            )
            output_has_index = isinstance(deserialized, pandas.Series) or isinstance(
                deserialized, pandas.DataFrame
            )
            if not input_has_index or not output_has_index:
                LOG.warning(
                    "Inputs or Outputs are not of type series or dataframe, use_input_index has no effect"
                )
            else:
                try:
                    deserialized.index = inputs.index
                except Exception as e:
                    LOG.warning(f"Unable to set indexes of output frame: {repr(e)}")
        return deserialized

    def get_sample_data(self):
        if not self.endpoint_name:
            raise AuthenticationError(
                "Please authenticate against a specific endpoint first"
            )
        if not self.endpoint_has_arrow_sample_data:
            self.logger.warning("Sample data not available for this endpoint")
            return None, None
        schema = self.get_schema()
        if schema.metadata is None:
            self.logger.error(
                "Sample data does not exist or is not supported for this endpoint"
            )
            return None, None
        x_ticket, y_ticket = (
            str.encode(f"{self.endpoint_name}__X"),
            str.encode(f"{self.endpoint_name}__y"),
        )
        return self._get_data(ticket=x_ticket), self._get_data(ticket=y_ticket)

    def _get_data(self, ticket):
        if not self.endpoint_name:
            raise AuthenticationError(
                "Please authenticate against a specific endpoint first"
            )
        self.logger.trace("Fetching sample data from server")
        reader = self.client.do_get(Ticket(ticket=ticket))
        return deserialize_arrow(reader.read_all())

    def get_schema(self):
        if not self.endpoint_name:
            raise AuthenticationError(
                "Please authenticate against a specific endpoint first"
            )
        info = self.get_flight_info(str.encode(self.endpoint_name))
        return info.schema

    def get_flight_info(self, command_name: bytes) -> FlightInfo:
        descriptor = FlightDescriptor.for_command(command_name)
        return self.client.get_flight_info(descriptor)  # type: ignore

    def health(self):
        try:
            self.logger.trace("Connecting to server...")
            self.client.wait_for_available(timeout=1)
        except FlightUnauthenticatedError:
            self.logger.trace("Connection successful")
            return True
        except (FlightCancelledError, FlightUnavailableError):
            raise APIClientException(
                detail="Arrow flight is unavailable", status_code=502
            )
        return True


def get_chunk_size(sample_table: Table) -> Tuple[Optional[int], Optional[float]]:
    try:
        mem_per_record = sample_table.nbytes / sample_table.num_rows
    except ZeroDivisionError:
        LOG.error(
            "Empty payload received, which is currently not supported for arrow endpoints"
        )
        return None, None
    batch_size = math.ceil(settings.ARROW_BATCH_MB * 1e6 / mem_per_record)
    batch_memory_mb = (batch_size * mem_per_record) / 1e6
    return batch_size, batch_memory_mb
