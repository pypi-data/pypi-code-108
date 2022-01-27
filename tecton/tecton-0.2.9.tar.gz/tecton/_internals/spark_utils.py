import os
import sys

from pyspark.sql import SparkSession

from tecton import conf
from tecton_spark.logger import get_logger
from tecton_spark.udf_jar import get_udf_jar_path


# Environment variables to propagate to the executor
EXECUTOR_ENV_VARIABLES = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "HIVE_METASTORE_HOST",
    "HIVE_METASTORE_PORT",
    "HIVE_METASTORE_USERNAME",
    "HIVE_METASTORE_DATABASE",
    "HIVE_METASTORE_PASSWORD",
]


logger = get_logger("SparkUtils")


def _get_basic_spark_session_builder():
    builder = SparkSession.builder

    if conf.get_or_none("AWS_ACCESS_KEY_ID") is not None:
        builder = builder.config("spark.hadoop.fs.s3a.access.key", conf.get_or_none("AWS_ACCESS_KEY_ID"))
        builder = builder.config("spark.hadoop.fs.s3a.secret.key", conf.get_or_none("AWS_SECRET_ACCESS_KEY"))
    if conf.get_or_none("HIVE_METASTORE_HOST") is not None:
        builder = (
            builder.enableHiveSupport()
            .config(
                "spark.hadoop.javax.jdo.option.ConnectionURL",
                f"jdbc:mysql://{conf.get_or_none('HIVE_METASTORE_HOST')}:{conf.get_or_none('HIVE_METASTORE_PORT')}/{conf.get_or_none('HIVE_METASTORE_DATABASE')}",
            )
            .config("spark.hadoop.javax.jdo.option.ConnectionDriverName", "com.mysql.cj.jdbc.Driver")
            .config("spark.hadoop.javax.jdo.option.ConnectionUserName", conf.get_or_none("HIVE_METASTORE_USERNAME"))
            .config("spark.hadoop.javax.jdo.option.ConnectionPassword", conf.get_or_none("HIVE_METASTORE_PASSWORD"))
        )
    for v in EXECUTOR_ENV_VARIABLES:
        if conf.get_or_none(v) is not None:
            builder = builder.config(f"spark.executorEnv.{v}", conf.get_or_none(v))
    return builder


def get_or_create_spark_session(custom_spark_options=None):
    logger.debug("Creating Apache Spark Context")
    builder = _get_basic_spark_session_builder()

    if conf.get_or_none("SPARK_DRIVER_LOCAL_IP"):
        # Sadly, Spark will always attempt to retrieve the driver's local IP
        # even if the "spark.driver.host" conf is set. This will
        # result in an error if Spark's code is unable to retrieve the local IP
        # (which happens in the case of SageMaker notebooks). The only way to override Spark's
        # behavior is by setting the SPARK_LOCAL_IP env variable
        os.environ["SPARK_LOCAL_IP"] = conf.get_or_none("SPARK_DRIVER_LOCAL_IP")

    builder = builder.master("local")

    builder = builder.config("spark.jars", get_udf_jar_path())

    # For some reason using the property spark.pyspark.python does not
    # work for this like it should
    os.environ["PYSPARK_PYTHON"] = sys.executable

    if custom_spark_options:
        for k, v in custom_spark_options.items():
            builder.config(k, v)

    return builder.getOrCreate()
