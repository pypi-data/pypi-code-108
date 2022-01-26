"""
Arrow client utilities
"""
import logging
import math
import typing as t

import certifi  # type: ignore
from pyarrow import Table  # type: ignore
from pyarrow.flight import (  # type: ignore
    ActionType,
    FlightClient,
    FlightDescriptor,
    FlightStreamReader,
    FlightStreamWriter,
)

from taktile_client.arrow.serialize import UserType, deserialize, serialize
from taktile_client.config import settings

logger = logging.getLogger(__name__)


def batch_arrow(  # pylint: disable=too-many-locals
    *,
    client: FlightClient,
    action: ActionType,
    payload: UserType,
    nrows: t.Optional[int],
) -> UserType:
    """
    Send a batch via arrow

    Parameters
    ----------
    client : FlightClient
        client to use
    action : ActionType
        action type
    payload : UserType
        payload to send
    nrows: t.Optional[int]
        number of rows to send per batch
    """
    table = serialize(payload)
    batch_size, batch_memory = _get_chunk_size(table, nrows)
    if not (batch_size and batch_memory):
        return None
    descriptor = client.get_flight_info(
        FlightDescriptor.for_command(action.type)
    )
    writer, reader = client.do_exchange(descriptor.descriptor)
    logger.debug(
        "Initiating prediction request with batches of %d records of "
        "~%.2f MB/batch",
        batch_size,
        batch_memory,
    )
    batches = table.to_batches(max_chunksize=batch_size)
    chunks = []
    schema = None
    with writer:
        writer.begin(table.schema)
        for i, batch in enumerate(batches):
            logger.debug("Prediction for batch %d/%d", i + 1, len(batches))
            chunk = _send_batch(
                writer=writer, batch=batch, reader=reader, batch_number=i + 1
            )
            if not chunk:
                continue
            if schema is None and chunk.data.schema is not None:
                schema = chunk.data.schema
            chunks.append(chunk.data)
    deserialized = deserialize(Table.from_batches(chunks, schema))
    return deserialized


def _send_batch(
    writer: FlightStreamWriter,
    batch: t.Any,  # RecordBatch, but there is no python type
    reader: FlightStreamReader,
    batch_number: int,
) -> t.Any:
    try:
        writer.write_batch(batch)
        return reader.read_chunk()
    except Exception as err:  # pylint: disable=broad-except
        logger.error(
            "ERROR: performing prediction for batch %d: %s "
            "The predictions from this batch will be missing from the result",
            batch_number,
            str(err),
        )
        return None


def _get_chunk_size(
    sample_table: Table, batch_size: t.Optional[int]
) -> t.Tuple[t.Optional[int], t.Optional[float]]:

    if sample_table.num_rows == 0:
        logger.error(
            "Empty payload received, "
            "which is currently not supported for arrow endpoints"
        )
        return None, None
    mem_per_record = sample_table.nbytes / sample_table.num_rows
    if batch_size:
        batch_memory_mb = (batch_size * mem_per_record) / 1e6
    else:
        batch_memory_mb = settings.ARROW_BATCH_MB
        batch_size = math.ceil(batch_memory_mb * 1e6 / mem_per_record)
    return batch_size, batch_memory_mb


def load_certs() -> str:
    """Load certificates"""
    with open(certifi.where(), "r", encoding="utf-8") as cert:
        return cert.read()
