import math
import typing as t

import pandas as pd  # type: ignore
from pyarrow import Table  # type: ignore
from pyarrow.flight import FlightClient  # type: ignore
from pyarrow.flight import ActionType, FlightDescriptor

from tktl.core.config import settings
from tktl.core.loggers import LOG
from tktl.core.serializers import deserialize_arrow, serialize_arrow


def batch_arrow(
    *, client: FlightClient, action: ActionType, X: t.Any, use_input_index: bool = False
):
    table = serialize_arrow(X)
    batch_size, batch_memory = _get_chunk_size(table)
    if not (batch_size and batch_memory):
        return
    descriptor = client.get_flight_info(FlightDescriptor.for_command(action.type))
    writer, reader = client.do_exchange(descriptor.descriptor)  # type: ignore
    LOG.trace(
        f"Initiating prediction request with batches of {batch_size} records of "
        f"~{batch_memory:.2f} MB/batch"
    )
    batches = table.to_batches(max_chunksize=batch_size)
    chunks = []
    schema = None
    with writer:
        writer.begin(table.schema)
        for i, batch in enumerate(batches):
            LOG.trace(f"Prediction for batch {i + 1}/{len(batches)}")
            chunk = _send_batch(
                writer=writer, batch=batch, reader=reader, batch_number=i + 1
            )
            if not chunk:
                continue
            if not schema and chunk.data.schema is not None:
                schema = chunk.data.schema
            chunks.append(chunk.data)
    deserialized = deserialize_arrow(Table.from_batches(chunks, schema))
    if use_input_index:
        input_has_index = isinstance(X, pd.Series) or isinstance(X, pd.DataFrame)
        output_has_index = isinstance(deserialized, pd.Series) or isinstance(
            deserialized, pd.DataFrame
        )
        if not input_has_index or not output_has_index:
            LOG.warning(
                "Inputs or Outputs are not of type series or dataframe, use_input_index has no effect"
            )
        else:
            try:
                deserialized.index = X.index
            except Exception as e:
                LOG.warning(f"Unable to set indexes of output frame: {repr(e)}")
    return deserialized


def _send_batch(writer, batch, reader, batch_number):
    try:
        writer.write_batch(batch)
        return reader.read_chunk()
    except Exception as e:
        LOG.error(
            f"ERROR: performing prediction for batch {batch_number}: {e} "
            f"The predictions from this batch will be missing from the result"
        )
        return None


def _get_chunk_size(sample_table: Table) -> t.Tuple[t.Optional[int], t.Optional[float]]:
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
