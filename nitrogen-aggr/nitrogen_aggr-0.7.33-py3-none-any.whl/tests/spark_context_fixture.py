import findspark  # this needs to be the first import

findspark.init()
import os
import logging
import pytest

from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SparkSession

""" pytest fixtures that can be resued across tests. the filename needs to be conftest.py
"""

# make sure env variables are set correctly


def quiet_py4j():
    """ turn down spark logging for the test context """
    logger = logging.getLogger("py4j")
    logger.setLevel(logging.INFO)


@pytest.fixture(scope="session")
def spark_context(request):
    """ fixture for creating a spark context
    Args:
        request: pytest.FixtureRequest object
    """
    conf = SparkConf().setMaster("local[2]").setAppName("pytest-pyspark-local-testing")
    sc = SparkContext(conf=conf)
    request.addfinalizer(lambda: sc.stop())

    quiet_py4j()
    return sc


@pytest.fixture(scope="session")
def spark_session(request):
    """ fixture for creating a spark session
    Args:
        request: pytest.FixtureRequest object
    """
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("pytest-pyspark-local-testing")
        .getOrCreate()
    )
    spark.conf.set("spark.hadoop.fs.s3a.access.key", os.environ["AWS_ACCESS_KEY_ID"])
    spark.conf.set(
        "spark.hadoop.fs.s3a.secret.key", os.environ["AWS_SECRET_ACCESS_KEY"]
    )
    request.addfinalizer(lambda: spark.stop())

    quiet_py4j()
    return spark
