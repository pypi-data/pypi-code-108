#
# DATABRICKS CONFIDENTIAL & PROPRIETARY
# __________________
#
# Copyright 2020-present Databricks, Inc.
# All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains the property of Databricks, Inc.
# and its suppliers, if any.  The intellectual and technical concepts contained herein are
# proprietary to Databricks, Inc. and its suppliers and may be covered by U.S. and foreign Patents,
# patents in process, and are protected by trade secret and/or copyright law. Dissemination, use,
# or reproduction of this information is strictly forbidden unless prior written permission is
# obtained from Databricks, Inc.
#
# If you view or obtain a copy of this information and believe Databricks, Inc. may not have
# intended it to be made available, please promptly report it to Databricks Legal Department
# @ legal@databricks.com.
#
from inspect import getfullargspec

from pyspark import since, SparkContext
from pyspark.sql.types import ArrayType, StringType, StructType, BinaryType, MapType
from pyspark.sql.column import Column, _to_java_column
from pyspark.sql.pandas.functions import _create_pandas_udf
from pyspark.sql.udf import _create_udf
from pyspark.sql.pandas.utils import require_minimum_pandas_version, require_minimum_pyarrow_version


@since('3.0.1')
def unwrap_udt(col):
    """
    Unwrap UDT data type column into its underlying struct type
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.com.databricks.sql.DatabricksFunctions.unwrap_udt(_to_java_column(col))
    return Column(jc)


def _create_edge_udf(f, returnType, evalType):
    # The following table shows most of Pandas data and SQL type conversions in Python UDFs with
    # Arrow enabled, that are not yet visible to the user. Some of behaviors are buggy and
    # might be changed in the near future. The table might have to be eventually documented
    # externally. Please see SC-70036's PR to see the codes in order to generate the table below.
    #
    # +-----------------------------+--------------+------------------+--------------------+------+--------------------+-----------------------------+----------+----------------------+------------------+------------------+----------------------------+--------------------+--------------+  # noqa
    # |SQL Type \ Python Value(Type)|None(NoneType)|        True(bool)|              1(int)|a(str)|    1970-01-01(date)|1970-01-01 00:00:00(datetime)|1.0(float)|array('i', [1])(array)|         [1](list)|       (1,)(tuple)|bytearray(b'ABC')(bytearray)|          1(Decimal)|{'a': 1}(dict)|  # noqa
    # +-----------------------------+--------------+------------------+--------------------+------+--------------------+-----------------------------+----------+----------------------+------------------+------------------+----------------------------+--------------------+--------------+  # noqa
    # |                      boolean|          None|              True|                True|     X|                   X|                            X|      True|                     X|                 X|                 X|                           X|                   X|             X|  # noqa
    # |                      tinyint|          None|                 1|                   1|     X|                   X|                            X|         1|                     X|                 X|                 X|                           X|                   1|             X|  # noqa
    # |                     smallint|          None|                 1|                   1|     X|                   X|                            X|         1|                     X|                 X|                 X|                           X|                   1|             X|  # noqa
    # |                          int|          None|                 1|                   1|     X|                   X|                            X|         1|                     X|                 X|                 X|                           X|                   1|             X|  # noqa
    # |                       bigint|          None|                 1|                   1|     X|                   X|                            0|         1|                     X|                 X|                 X|                           X|                   1|             X|  # noqa
    # |                       string|          None|            'True'|                 '1'|   'a'|        '1970-01-01'|         '1970-01-01 00:00...|     '1.0'|     "array('i', [1])"|             '[1]'|            '(1,)'|         "bytearray(b'ABC')"|                 '1'|    "{'a': 1}"|  # noqa
    # |                         date|          None|                 X|                   X|     X|datetime.date(197...|         datetime.date(197...|         X|                     X|                 X|                 X|                           X|datetime.date(197...|             X|  # noqa
    # |                    timestamp|          None|                 X|datetime.datetime...|     X|                   X|         datetime.datetime...|         X|                     X|                 X|                 X|                           X|datetime.datetime...|             X|  # noqa
    # |                        float|          None|               1.0|                 1.0|     X|                   X|                            X|       1.0|                     X|                 X|                 X|                           X|                   X|             X|  # noqa
    # |                       double|          None|               1.0|                 1.0|     X|                   X|                            X|       1.0|                     X|                 X|                 X|                           X|                   X|             X|  # noqa
    # |                       binary|          None|bytearray(b'\x00')|  bytearray(b'\x00')|     X|                   X|                            X|         X|  bytearray(b'\x01\...|bytearray(b'\x01')|bytearray(b'\x01')|           bytearray(b'ABC')|                   X|             X|  # noqa
    # |                decimal(10,0)|          None|                 X|                   X|     X|                   X|                            X|         X|                     X|                 X|                 X|                           X|        Decimal('1')|             X|  # noqa
    # +-----------------------------+--------------+------------------+--------------------+------+--------------------+-----------------------------+----------+----------------------+------------------+------------------+----------------------------+--------------------+--------------+  # noqa
    #
    # Note: DDL formatted string is used for 'SQL Type' for simplicity. This string can be
    #       used in `returnType`.
    # Note: The values inside of the table are generated by `repr`.
    # Note: Python 3.8.6, Pandas 1.2.1 and PyArrow 2.0.0 are used.
    # Note: Timezone is KST.
    # Note: 'X' means it throws an exception during the conversion.
    from pyspark.sql import SparkSession
    session = SparkSession._instantiatedSession
    is_arrow_enabled = (
        session is not None and
        session.conf.get(
            "spark.databricks.execution.pythonUDF.arrow.enabled") == "true")
    regular_udf = _create_udf(f, returnType, evalType)
    return_type = regular_udf.returnType
    try:
        is_func_with_args = len(getfullargspec(f).args) > 0
    except TypeError:
        is_func_with_args = False
    is_output_atomic_type = (
        not isinstance(return_type, StructType) and
        not isinstance(return_type, MapType) and
        not isinstance(return_type, ArrayType)
    )

    if is_arrow_enabled and is_output_atomic_type and is_func_with_args:
        require_minimum_pandas_version()
        require_minimum_pyarrow_version()

        import pandas as pd

        result_func = lambda pdf: pdf
        if type(return_type) == StringType:
            result_func = lambda r: str(r) if r is not None else r
        elif type(return_type) == BinaryType:
            result_func = lambda r: bytes(r) if r is not None else r

        def vectorized_udf(*args: pd.Series) -> pd.Series:
            if any(map(lambda arg: isinstance(arg, pd.DataFrame), args)):
                raise NotImplementedError(
                    "Struct input type are not supported with Arrow optimization "
                    "enabled in Python UDFs. Disable "
                    "'spark.databricks.execution.pythonUDF.arrow.enabled' to workaround.")
            # Always cast because regular UDF supports more permissive casting
            # compared to pandas UDFs. This is to don't break the user's codes
            # from enabling this edge feature.
            return pd.Series(result_func(f(*a)) for a in zip(*args))

        # Regular UDFs can take callable instances too.
        vectorized_udf.__name__ = f.__name__ if hasattr(f, '__name__') else f.__class__.__name__
        vectorized_udf.__module__ = (
            f.__module__ if hasattr(f, '__module__') else f.__class__.__module__)
        vectorized_udf.__doc__ = f.__doc__
        pudf = _create_pandas_udf(vectorized_udf, returnType, None)
        # Keep the attributes as if this is a regular Python UDF.
        pudf.func = f
        pudf.returnType = return_type
        pudf.evalType = regular_udf.evalType
        return pudf
    else:
        return regular_udf
