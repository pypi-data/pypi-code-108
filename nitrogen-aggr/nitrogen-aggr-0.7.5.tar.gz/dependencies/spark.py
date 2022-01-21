"""
spark.py
~~~~~~~~
Module containing helper function for use with Apache Spark
source: https://github.com/AlexIoannides/pyspark-example-project/blob/master/dependencies/spark.py
The original source for this file is above. It is heavily  modified for Cadmium use
"""

import __main__
from os import environ
from pyspark.sql import SparkSession


def start_spark(
    app_name="my_spark_app", master="local[*]", jar_packages=[], spark_config={}
):
    """Start Spark session, get Spark logger and load config files.
    Start a Spark session on the worker node and register the Spark
    application with the cluster. Note, that only the app_name argument
    will apply when this is called from a script sent to spark-submit.
    All other arguments exist solely for testing the script from within
    an interactive Python console.

    The function checks the enclosing environment to see if it is being
    run from inside an interactive console session or from an
    environment which has a `DEBUG` environment variable set (e.g.
    setting `DEBUG=1` as an environment variable as part of a debug
    configuration within an IDE such as Visual Studio Code or PyCharm.
    In this scenario, the function uses all available function arguments
    to start a PySpark driver from the local PySpark package as opposed
    to using the spark-submit and Spark cluster defaults. This will also
    use local module imports, as opposed to those in the zip archive
    sent to spark via the --py-files flag in spark-submit.

    :param app_name: Name of Spark app.
    :param master: Cluster connection details (defaults to local[*]).
    :param jar_packages: List of Spark JAR package names.
    :param files: List of files to send to Spark cluster (master and
        workers).
    :param spark_config: Dictionary of config key-value pairs.
    :return: A tuple of references to the Spark session, logger and
        config dict (only if available).
    """

    # detect execution environment
    flag_repl = not (hasattr(__main__, "__file__"))
    flag_debug = "DEBUG" in environ.keys()
    flag_repl = flag_debug = True

    if not (flag_repl or flag_debug):
        # get Spark session factory
        spark_builder = SparkSession.builder.appName(app_name)
    else:
        # get Spark session factory
        # spark_builder = SparkSession.builder.master(master).appName(app_name)
        spark_builder = SparkSession.builder.appName(app_name)

        # create Spark JAR packages string
        spark_jars_packages = ",".join(list(jar_packages))
        spark_builder.config("spark.jars.packages", spark_jars_packages)
        spark_builder.config("spark.sql.parquet.fs.optimized.committer.optimization-enabled", True)
        # add other config params
        for key, val in spark_config.items():
            spark_builder.config(key, val)

    # create session and retrieve Spark logger object
    spark_sess = spark_builder.getOrCreate()

    return spark_sess
