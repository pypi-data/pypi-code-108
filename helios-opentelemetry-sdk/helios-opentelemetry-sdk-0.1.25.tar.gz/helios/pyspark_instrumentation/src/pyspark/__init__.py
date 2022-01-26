"""
Instrument `pyspark-python` to report PySpark save actions

Usage
-----

.code:: python

    from hs_sdk.src.instrumentation.pyspark import PySparkInstrumentor
    from pyspark.sql import SparkSession

    # Instrument PySpark
    PySparkInstrumentor().instrument()


    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()

    data = [('James','','Smith','1991-04-01','M',3000),
       ('Michael','Rose','','2000-05-19','M',4000),
       ('Robert','','Williams','1978-09-05','M',4000),
       ('Maria','Anne','Jones','1967-12-01','F',4000),
       ('Jen','Mary','Brown','1980-02-17','F',-1)
     ]

    columns = ["firstname", "middlename", "lastname", "dob", "gender", "salary"]

    df = spark.createDataFrame(data=data, schema=columns)

    # This will report a span of saving a data frame in a specific path
    df.write.save('employeesPath', 'csv', 'overwrite', ['firstname', 'middlename'])

    # This will report a span of saving a data frame as a table
    df.write.saveAsTable('employeesTable', 'csv', 'overwrite', ['firstname', 'middlename'])


API
___
"""

from typing import Collection

from wrapt import wrap_function_wrapper
import pyspark.sql

from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.trace import Tracer

from helios.pyspark_instrumentation.src.pyspark.package import _instruments

__version__ = "0.1.0"

SAVE_SPAN_NAME = 'DataFrameWriter.save'
SAVE_AS_TABLE_SPAN_NAME = 'DataFrameWriter.saveAsTable'

SPAN_ATTRIBUTES_SPARK_PATH = 'spark.path'
SPAN_ATTRIBUTES_SPARK_FORMAT = 'spark.format'
SPAN_ATTRIBUTES_SPARK_NAME = 'spark.name'
SPAN_ATTRIBUTES_SPARK_MODE = 'spark.mode'
SPAN_ATTRIBUTES_SPARK_PARTITION_BY = 'spark.partitionBy'


def _get_argument(key, position, default_value, args, kwargs):
    if len(args) > position:
        return args[position]
    return kwargs.get(key, default_value)


def _get_path(args, kwargs):
    """ extract path from `save` method arguments in DataFrameWriter class """
    return _get_argument("path", 0, None, args, kwargs)


def _get_name(args, kwargs):
    """ extract name from `saveToTable` method arguments in DataFrameWriter class """
    if len(args) > 0:
        return args[0]
    return "unknown"


def _get_format(args, kwargs):
    """ extract format from `save` and `saveToTable` method arguments in DataFrameWriter class """
    return _get_argument("format", 1, None, args, kwargs)


def _get_mode(args, kwargs):
    """ extract mode from `save` and `saveToTable` method arguments in DataFrameWriter class """
    return _get_argument("mode", 2, None, args, kwargs)


def _get_partition_by(args, kwargs):
    """ extract partitionBy from `save` and `saveToTable` method arguments in DataFrameWriter class """
    return _get_argument("partitionBy", 3, None, args, kwargs)


def _get_save_attributes(args, kwargs):
    format_name = _get_format(args, kwargs)
    mode = _get_mode(args, kwargs)
    partition_by = _get_partition_by(args, kwargs)  # List!
    partition_by_str = None
    if partition_by:
        partition_by_str = ','.join(partition_by) if isinstance(partition_by, list) else partition_by
    return format_name, mode, partition_by_str


def _set_save_attributes(span, format_name, mode, partition_by):
    if span.is_recording():
        span.set_attribute(SPAN_ATTRIBUTES_SPARK_FORMAT, format_name) if format_name else None
        span.set_attribute(SPAN_ATTRIBUTES_SPARK_MODE, mode) if mode else None
        span.set_attribute(SPAN_ATTRIBUTES_SPARK_PARTITION_BY, partition_by) if partition_by else None


def _instrument(tracer: Tracer):

    def _traced_save(func, instance, args, kwargs):
        span_name = SAVE_SPAN_NAME
        path = _get_path(args, kwargs)
        format_name, mode, partition_by_str = _get_save_attributes(args, kwargs)
        with tracer.start_as_current_span(span_name, kind=trace.SpanKind.CLIENT) as span:
            if span.is_recording():
                span.set_attribute(SPAN_ATTRIBUTES_SPARK_PATH, path) if path else None
                _set_save_attributes(span, format_name, mode, partition_by_str)
            return func(*args, **kwargs)

    def _traced_save_as_table(func, instance, args, kwargs):
        span_name = SAVE_AS_TABLE_SPAN_NAME
        name = _get_name(args, kwargs)
        format_name, mode, partition_by_str = _get_save_attributes(args, kwargs)
        with tracer.start_as_current_span(span_name, kind=trace.SpanKind.CLIENT) as span:
            if span.is_recording():
                span.set_attribute(SPAN_ATTRIBUTES_SPARK_NAME, name)
                _set_save_attributes(span, format_name, mode, partition_by_str)
            return func(*args, **kwargs)

    wrap_function_wrapper("pyspark.sql", "DataFrameWriter.save", _traced_save)
    wrap_function_wrapper("pyspark.sql", "DataFrameWriter.saveAsTable", _traced_save_as_table)


class PySparkInstrumentor(BaseInstrumentor):
    """An instrumentor for PySpark module
    See `BaseInstrumentor`
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        """Instruments the pyspark module

        Args:
            **kwargs: Optional arguments
                ``tracer_provider``: a TracerProvider, defaults to global.
        """
        tracer_provider = kwargs.get("tracer_provider")
        tracer = trace.get_tracer(
            'opentelemetry.instrumentation.pyspark', __version__, tracer_provider=tracer_provider
        )
        _instrument(tracer)

    def _uninstrument(self, **kwargs):
        unwrap(pyspark.sql.DataFrameWriter, "save")
        unwrap(pyspark.sql.DataFrameWriter, "saveAsTable")
