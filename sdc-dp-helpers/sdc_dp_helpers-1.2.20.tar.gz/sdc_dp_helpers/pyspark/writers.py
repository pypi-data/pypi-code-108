import os
import warnings
from datetime import datetime
from pyspark.sql import functions as F
import pyspark.sql.types as T


def user_defined_timestamp(date_col, date_format: str = '%Y%m%d'):
    """
        (UDF) convert datetime column using python datetime

        args:
            date_col (pyspark.sql.functions.col): datetime column to format
            date_format (str): a datetime valid string format
        return
            (pyspark.sql.functions.col)
    """
    _date = datetime.strptime(date_col, '%Y-%m-%d')
    return _date.strftime(date_format)

def advanced_writer(
    *,
    dataframe,
    output_data_config: dict = None,
    **kwargs
):
    """
        Constructs a write function configuration and returns this.

        note:
            - on return write_function.csv() or write_function.json() or write_function.parquet()
    """
    # pylint: disable=too-many-locals, too-many-branches, too-many-statements

    if not isinstance(output_data_config, dict):
        raise TypeError("output_data_config was not of type dict.")

    output_path =  output_data_config.get('output_path', None)
    if output_path is None:
        raise TypeError("output_path is required but was not found")

    output_type = output_data_config.get('output_type', None)
    if output_type is None:
        raise TypeError("output_type is required but was not found")

    partition_config = kwargs.get('partition_config', {})
    if not isinstance(partition_config, dict):
        raise TypeError("partition_config was not of type dict.")

    partitions =  partition_config.get('partitions', None)
    partition_by =  partition_config.get('partition_by', None)
    partition_type =  partition_config.get('partition_type', None)

    bucket_config = kwargs.get('bucket_config', {})
    if not isinstance(bucket_config, dict):
        raise TypeError("bucket_config was not of type dict.")

    bucket_type =  bucket_config.get('bucket_type', None)
    buckets =  bucket_config.get('buckets', None)

    compression_type = kwargs.get('compression_type', None)
    overwrite = kwargs.get('overwrite', False)
    header = kwargs.get('header', True)

    # output from this step is a dataframe writer
    if partition_type in ['key', 'random']:
        if partition_by is None:
            raise Exception("To perform repartitioning 'partition_by' is required.")

        col_structure = []
        for column in partition_by:
            col_structure.append(F.col(column))

        if partition_type == 'random':
            col_structure.append(F.rand)

        dataframe = dataframe.repartition(partitions, *col_structure)
        if bucket_type == 'size':
            # this will be ignored in the case where partitions are added
            dataframe_writer = dataframe.write.option(
                "maxRecordsPerFile", buckets
            ).partitionBy(*partition_by)
        else:
            dataframe_writer = dataframe.write.partitionBy(*partition_by)

    elif bucket_type == 'size':
        # this will be ignored in the case where partitions are added
        dataframe_writer = dataframe.write.option("maxRecordsPerFile", buckets)
    else:
        warnings.warn((
            'Defaulting to standard writer. '
            'Either set a num_partitions or max_size '
            'to bucket for additional options.'
        ))
        dataframe_writer = dataframe.write

    if overwrite is True:
        dataframe_writer = dataframe_writer.mode('overwrite')

    dataframe_writer = dataframe_writer.option("header", header)

    if compression_type is not None:
        dataframe_writer = dataframe_writer.option("compression", compression_type)

    if output_type == 'csv':
        dataframe_writer.csv(output_path)
    elif output_type == 'json':
        dataframe_writer.json(output_path)
    elif output_type == 'parquet':
        dataframe_writer.parquet(output_path)
    else:
        raise Exception(
            "Output type = {OUTPUT_TYPE} not supported. "
            "Only support csv and json at current.".format(
                OUTPUT_TYPE=output_type
            )
        )

def advanced_writer_w_custom_partition_naming(
    *,
    dataframe,
    output_data_config: dict,
    **kwargs
):
    """
        SDC custom pyspark writer that extends advanced_writer
        to offer special date partitioning which includes a more
        well formatted set of directory names for single level partition.
    """
    # pylint: disable=too-many-locals, too-many-function-args

    if not isinstance(output_data_config, dict):
        raise TypeError("output_data_config was not of type dict.")

    partition_config = kwargs.get('partition_config', {})
    if not isinstance(partition_config, dict):
        raise TypeError("partition_config was not of type dict.")

    partition_by =  partition_config.get('partition_by', None)
    partition_type =  partition_config.get('partition_type', None)
    date_partition_format = partition_config.get('date_partition_format', None)

    bucket_config = kwargs.get('bucket_config', {})
    if not isinstance(bucket_config, dict):
        raise TypeError("bucket_config was not of type dict.")

    if partition_type == 'date':
        output_path = output_data_config.get('output_path', None)
        if output_path is None:
            raise KeyError("output_path is required but was not found")

        output_type = output_data_config.get('output_type', None)
        if output_type is None:
            raise KeyError("output_type is required but was not found")

        if not isinstance(partition_by, str):
            raise TypeError(
                "For partition_type == date, "
                "the 'partition_by' field should be name of date field."
            )

        if date_partition_format is None:
            raise KeyError(
                "For partition_type == date, "
                "'date_partition_format' field is required but missing"
            )

        # pop partition_config from kwargs
        kwargs.pop('partition_config')

        # create udf to format date
        user_defined_timestamp_udf = F.udf(user_defined_timestamp, T.StringType())

        # create tmp_partition_field
        dataframe = dataframe.withColumn(
            'tmp_partition_field', user_defined_timestamp_udf(
                partition_by, F.lit(date_partition_format)
            )
        )

        partition_groups = list(
            dataframe.select(
                'tmp_partition_field'
            ).distinct().rdd.map(
                lambda r: r[0]
            ).collect()
        )

        for partition in partition_groups:
            partioned_dataframe = dataframe.filter(
                F.col("tmp_partition_field") == partition
            ).drop("tmp_partition_field")


            advanced_writer(
                dataframe=partioned_dataframe,
                output_data_config={
                   'output_path': os.path.join(output_path, partition),
                   'output_type': output_type
                },
                **kwargs
            )
    else:
        advanced_writer(
            dataframe,
            output_data_config=output_data_config,
            **kwargs
        )
